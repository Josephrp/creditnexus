"""
Policy configuration loader for CreditNexus.

Loads policy rules from YAML files in a configured directory and provides
a unified interface for policy engine initialization.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import yaml

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

from app.core.config import Settings

logger = logging.getLogger(__name__)


class PolicyConfigLoader:
    """
    Loads and manages policy rule configurations from YAML files.
    
    Supports:
    - Loading multiple YAML files from a directory
    - Merging rules from multiple files
    - Hot-reloading on file changes (optional, requires watchdog)
    - Validation of rule structure
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize policy configuration loader.
        
        Args:
            settings: Application settings containing policy configuration
        """
        self.settings = settings
        self.rules_dir = Path(settings.POLICY_RULES_DIR)
        self.pattern = settings.POLICY_RULES_PATTERN
        self._rules_cache: Optional[str] = None
        self._observer: Optional[Any] = None
        
    def load_all_rules(self) -> str:
        """
        Load all policy rules from YAML files in the configured directory.
        
        Rules are loaded in alphabetical order by filename and merged into
        a single YAML string. Files can contain:
        - Single rule definitions
        - Multiple rules in a list
        - Rule imports/references
        
        Returns:
            Combined YAML string containing all rules from all files
            
        Raises:
            ValueError: If no policy files found or invalid YAML structure
        """
        rule_files = self.settings.get_policy_rules_files()
        
        if not rule_files:
            logger.warning(f"No policy rule files found in {self.rules_dir}")
            return ""
        
        logger.info(f"Loading policy rules from {len(rule_files)} file(s)")
        
        all_rules: List[Dict[str, Any]] = []
        
        for rule_file in rule_files:
            try:
                rules = self._load_rules_from_file(rule_file)
                all_rules.extend(rules)
                logger.debug(f"Loaded {len(rules)} rule(s) from {rule_file.name}")
            except Exception as e:
                logger.error(f"Failed to load rules from {rule_file}: {e}")
                raise ValueError(f"Error loading policy rules from {rule_file}: {e}")
        
        # Convert merged rules back to YAML
        combined_yaml = yaml.dump(all_rules, default_flow_style=False, sort_keys=False)
        
        # Cache the result
        self._rules_cache = combined_yaml
        
        logger.info(f"Successfully loaded {len(all_rules)} total policy rule(s)")
        return combined_yaml
    
    def _load_rules_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load rules from a single YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            List of rule dictionaries
            
        Raises:
            yaml.YAMLError: If file contains invalid YAML
            ValueError: If file structure is invalid
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
        
        if content is None:
            return []
        
        # Handle both single rule and list of rules
        if isinstance(content, dict):
            # Single rule
            return [content]
        elif isinstance(content, list):
            # List of rules
            return content
        else:
            raise ValueError(f"Invalid rule file structure in {file_path}: expected dict or list")
    
    def validate_rules(self, rules_yaml: str) -> bool:
        """
        Validate policy rules YAML structure.
        
        Args:
            rules_yaml: YAML string containing policy rules
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        try:
            rules = yaml.safe_load(rules_yaml)
            if rules is None:
                return True  # Empty rules are valid
            
            if not isinstance(rules, list):
                raise ValueError("Policy rules must be a list")
            
            for i, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    raise ValueError(f"Rule {i} must be a dictionary")
                
                # Validate required fields
                if "name" not in rule:
                    raise ValueError(f"Rule {i} missing required field: name")
                if "action" not in rule:
                    raise ValueError(f"Rule {i} missing required field: action")
                if "priority" not in rule:
                    raise ValueError(f"Rule {i} missing required field: priority")
                
                # Validate action values
                if rule["action"] not in ["allow", "block", "flag"]:
                    raise ValueError(f"Rule {i} has invalid action: {rule['action']}")
            
            return True
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in policy rules: {e}") from e
    
    def start_file_watcher(self, callback: Callable[[], None]) -> None:
        """
        Start watching policy files for changes (hot-reload).
        
        Only enabled if POLICY_AUTO_RELOAD is True (development mode).
        Requires watchdog package to be installed.
        
        Args:
            callback: Function to call when files change
        """
        if not self.settings.POLICY_AUTO_RELOAD:
            return
        
        if not WATCHDOG_AVAILABLE:
            logger.warning(
                "Policy auto-reload requested but watchdog package not available. "
                "Install with: pip install watchdog"
            )
            return
        
        if not self.rules_dir.exists():
            logger.warning(f"Policy rules directory does not exist: {self.rules_dir}")
            return
        
        class PolicyFileHandler(FileSystemEventHandler):
            def __init__(self, loader: PolicyConfigLoader, callback: Callable[[], None]):
                self.loader = loader
                self.callback = callback
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                if event.src_path.endswith(('.yaml', '.yml')):
                    logger.info(f"Policy file changed: {event.src_path}")
                    try:
                        self.callback()
                    except Exception as e:
                        logger.error(f"Error reloading policies: {e}")
        
        self._observer = Observer()
        self._observer.schedule(
            PolicyFileHandler(self, callback),
            str(self.rules_dir),
            recursive=False
        )
        self._observer.start()
        logger.info(f"Started file watcher for policy rules in {self.rules_dir}")
    
    def stop_file_watcher(self) -> None:
        """Stop watching policy files for changes."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            logger.info("Stopped policy file watcher")
    
    def get_rules_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about loaded policy rules.
        
        Returns:
            Dictionary with rule counts, file information, etc.
        """
        rule_files = self.settings.get_policy_rules_files()
        
        metadata = {
            "rules_dir": str(self.rules_dir),
            "pattern": self.pattern,
            "files_count": len(rule_files),
            "files": [str(f.name) for f in rule_files],
            "cached": self._rules_cache is not None
        }
        
        if self._rules_cache:
            try:
                rules = yaml.safe_load(self._rules_cache)
                if isinstance(rules, list):
                    metadata["rules_count"] = len(rules)
                    metadata["rule_names"] = [r.get("name", "unnamed") for r in rules]
            except Exception:
                pass
        
        return metadata





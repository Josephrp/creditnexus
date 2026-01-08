"""
Policy Engine Interface for CreditNexus.

This module defines the vendor-agnostic interface for policy engine implementations.
All policy engines must implement this interface to ensure compatibility with
CreditNexus's policy evaluation system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class PolicyEngineInterface(ABC):
    """
    Abstract interface for policy engine implementations.
    
    This allows CreditNexus to work with any policy engine vendor
    that implements this interface. The interface ensures:
    - Consistent evaluation API across vendors
    - Standardized decision format
    - Rule loading from YAML
    - Statistics tracking
    """
    
    @abstractmethod
    def evaluate(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a transaction against policy rules.
        
        The transaction dictionary should contain all relevant information
        for policy evaluation, including:
        - transaction_id, transaction_type, timestamp
        - originator/beneficiary information (id, name, lei, jurisdiction, kyc_status)
        - financial terms (amount, currency, interest_rate)
        - facility-specific data (facility_name, facility_type)
        - ESG/sustainability data (sustainability_linked, esg_kpi_targets, spt_threshold, ndvi_score)
        - regulatory context (governing_law, regulatory_framework)
        - loan asset data (collateral_address, geo_lat, geo_lon, risk_status)
        
        Args:
            transaction: Policy transaction dictionary with all relevant fields
            
        Returns:
            Dictionary containing:
            {
                "decision": "ALLOW" | "BLOCK" | "FLAG",
                "rule": Optional[str],  # Name of rule that triggered decision (if any)
                "matched_rules": List[str],  # All matching rules (for audit)
                "trace": List[Dict[str, Any]]  # Evaluation trace (for debugging)
            }
            
        Raises:
            ValueError: If transaction structure is invalid
            RuntimeError: If policy engine is not properly initialized
        """
        pass
    
    @abstractmethod
    def load_rules(self, rules_yaml: str) -> None:
        """
        Load policy rules from YAML string.
        
        The YAML should contain a list of policy rules, each with:
        - name: Rule identifier
        - when: Condition tree (any/all with field/op/value)
        - action: "allow", "block", or "flag"
        - priority: Numeric priority (higher = more important)
        - description: Human-readable description
        
        Args:
            rules_yaml: YAML-formatted policy rules string
            
        Raises:
            ValueError: If YAML structure is invalid
            RuntimeError: If rule compilation fails
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get engine statistics for monitoring and analytics.
        
        Returns:
            Dictionary containing:
            {
                "total_processed": int,  # Total transactions evaluated
                "decisions": {
                    "ALLOW": int,  # Count of ALLOW decisions
                    "BLOCK": int,  # Count of BLOCK decisions
                    "FLAG": int    # Count of FLAG decisions
                },
                "rules_loaded": int,  # Number of rules currently loaded
                "last_evaluation_time_ms": Optional[float]  # Last evaluation latency
            }
        """
        pass


class MockPolicyEngine(PolicyEngineInterface):
    """
    Mock policy engine implementation for testing and development.
    
    This is a simple implementation that:
    - Always returns ALLOW for testing
    - Tracks basic statistics
    - Validates rule YAML structure
    - Can be extended for more sophisticated mock behavior
    """
    
    def __init__(self):
        """Initialize mock policy engine."""
        self._rules: List[Dict[str, Any]] = []
        self._stats = {
            "total_processed": 0,
            "decisions": {
                "ALLOW": 0,
                "BLOCK": 0,
                "FLAG": 0
            },
            "rules_loaded": 0,
            "last_evaluation_time_ms": None
        }
    
    def evaluate(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock evaluation - always returns ALLOW for testing.
        
        In a real implementation, this would:
        1. Match transaction against all rules
        2. Determine highest priority action
        3. Return decision with trace
        """
        import time
        start_time = time.time()
        
        # Basic validation
        if not isinstance(transaction, dict):
            raise ValueError("Transaction must be a dictionary")
        
        if "transaction_id" not in transaction:
            raise ValueError("Transaction must have 'transaction_id' field")
        
        # Mock evaluation logic (always ALLOW for now)
        decision = "ALLOW"
        matched_rules = []
        trace = [
            {
                "step": "validation",
                "status": "passed",
                "message": "Transaction structure valid"
            },
            {
                "step": "rule_matching",
                "rules_checked": len(self._rules),
                "matched": 0
            },
            {
                "step": "decision",
                "result": decision,
                "reason": "No blocking rules matched (mock engine)"
            }
        ]
        
        # Update statistics
        self._stats["total_processed"] += 1
        self._stats["decisions"][decision] += 1
        self._stats["last_evaluation_time_ms"] = (time.time() - start_time) * 1000
        
        return {
            "decision": decision,
            "rule": None,
            "matched_rules": matched_rules,
            "trace": trace
        }
    
    def load_rules(self, rules_yaml: str) -> None:
        """
        Load rules from YAML string (mock implementation).
        
        Validates YAML structure but doesn't actually compile rules.
        """
        import yaml
        
        if not rules_yaml or not rules_yaml.strip():
            self._rules = []
            self._stats["rules_loaded"] = 0
            return
        
        try:
            rules = yaml.safe_load(rules_yaml)
            
            if rules is None:
                self._rules = []
                self._stats["rules_loaded"] = 0
                return
            
            if not isinstance(rules, list):
                raise ValueError("Policy rules must be a list")
            
            # Validate each rule structure
            for i, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    raise ValueError(f"Rule {i} must be a dictionary")
                
                required_fields = ["name", "action", "priority"]
                for field in required_fields:
                    if field not in rule:
                        raise ValueError(f"Rule {i} missing required field: {field}")
                
                if rule["action"] not in ["allow", "block", "flag"]:
                    raise ValueError(f"Rule {i} has invalid action: {rule['action']}")
            
            self._rules = rules
            self._stats["rules_loaded"] = len(rules)
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in policy rules: {e}") from e
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return self._stats.copy()


















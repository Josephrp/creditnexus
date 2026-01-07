"""
Prompt loader for LMA template prompts.

Dynamically loads prompt templates based on template category.
"""

import logging
from typing import Dict, Optional
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class PromptLoader:
    """
    Loads prompt templates for different LMA template categories.
    
    Maps template categories to prompt modules and provides
    access to section-specific prompts.
    """
    
    # Mapping of template categories to prompt modules
    PROMPT_MODULE_MAP = {
        "Facility Agreement": "app.prompts.templates.facility_agreement",
        "Term Sheet": "app.prompts.templates.term_sheet",
        "Confidentiality Agreement": "app.prompts.templates.confidentiality",
        # Add more mappings as needed
    }
    
    # Mapping of section names to prompt variable names
    SECTION_PROMPT_MAP = {
        "Facility Agreement": {
            "representations_and_warranties": "REPRESENTATIONS_PROMPT",
            "conditions_precedent": "CONDITIONS_PRECEDENT_PROMPT",
            "covenants": "COVENANTS_PROMPT",
            "esg_spt": "ESG_SPT_PROMPT",
            "events_of_default": "EVENTS_OF_DEFAULT_PROMPT",
        },
        "Term Sheet": {
            "purpose": "PURPOSE_PROMPT",
            "conditions_precedent": "CONDITIONS_PRECEDENT_PROMPT",
            "representations": "REPRESENTATIONS_PROMPT",
            "fees": "FEES_PROMPT",
        },
    }
    
    @classmethod
    def load_prompts_for_template(cls, template_category: str) -> Dict[str, ChatPromptTemplate]:
        """
        Load all prompts for a template category.
        
        Args:
            template_category: Template category (e.g., "Facility Agreement", "Term Sheet")
            
        Returns:
            Dictionary mapping section names to ChatPromptTemplate instances
            
        Raises:
            ImportError: If prompt module cannot be imported
            KeyError: If template category is not supported
        """
        if template_category not in cls.PROMPT_MODULE_MAP:
            raise KeyError(f"Template category '{template_category}' not supported. Available: {list(cls.PROMPT_MODULE_MAP.keys())}")
        
        module_path = cls.PROMPT_MODULE_MAP[template_category]
        
        try:
            # Dynamic import
            module = __import__(module_path, fromlist=[""])
            
            # Get prompts dictionary from module
            # Most modules export a PROMPTS dict or similar
            if hasattr(module, f"{template_category.upper().replace(' ', '_')}_PROMPTS"):
                prompts_dict = getattr(module, f"{template_category.upper().replace(' ', '_')}_PROMPTS")
            elif hasattr(module, "PROMPTS"):
                prompts_dict = getattr(module, "PROMPTS")
            elif hasattr(module, "FACILITY_AGREEMENT_PROMPTS"):
                prompts_dict = getattr(module, "FACILITY_AGREEMENT_PROMPTS")
            elif hasattr(module, "TERM_SHEET_PROMPTS"):
                prompts_dict = getattr(module, "TERM_SHEET_PROMPTS")
            else:
                # Try to find all ChatPromptTemplate instances
                prompts_dict = {
                    name: value
                    for name, value in vars(module).items()
                    if isinstance(value, ChatPromptTemplate) and name.endswith("_PROMPT")
                }
                # Convert to lowercase keys
                prompts_dict = {
                    name.lower().replace("_prompt", ""): value
                    for name, value in prompts_dict.items()
                }
            
            logger.debug(f"Loaded {len(prompts_dict)} prompt(s) for category '{template_category}'")
            return prompts_dict
            
        except ImportError as e:
            logger.error(f"Failed to import prompt module '{module_path}': {e}")
            raise ImportError(f"Could not import prompt module for category '{template_category}': {e}") from e
    
    @classmethod
    def get_prompt_for_section(
        cls, 
        template_category: str, 
        section_name: str
    ) -> Optional[ChatPromptTemplate]:
        """
        Get a specific prompt for a section.
        
        Args:
            template_category: Template category
            section_name: Section name (e.g., "representations_and_warranties")
            
        Returns:
            ChatPromptTemplate instance or None if not found
        """
        try:
            prompts = cls.load_prompts_for_template(template_category)
            
            # Try direct lookup
            if section_name in prompts:
                return prompts[section_name]
            
            # Try normalized lookup
            normalized_name = section_name.lower().replace(" ", "_").replace("-", "_")
            if normalized_name in prompts:
                return prompts[normalized_name]
            
            # Try section mapping
            if template_category in cls.SECTION_PROMPT_MAP:
                section_map = cls.SECTION_PROMPT_MAP[template_category]
                if section_name in section_map:
                    prompt_var = section_map[section_name]
                    prompts = cls.load_prompts_for_template(template_category)
                    # The prompts dict should have the section name as key
                    if section_name in prompts:
                        return prompts[section_name]
            
            logger.warning(f"Prompt not found for section '{section_name}' in category '{template_category}'")
            return None
            
        except (KeyError, ImportError) as e:
            logger.error(f"Error loading prompt for section '{section_name}': {e}")
            return None
    
    @classmethod
    def list_available_sections(cls, template_category: str) -> list:
        """
        List available sections for a template category.
        
        Args:
            template_category: Template category
            
        Returns:
            List of available section names
        """
        try:
            prompts = cls.load_prompts_for_template(template_category)
            return list(prompts.keys())
        except (KeyError, ImportError):
            return []













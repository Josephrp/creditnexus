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
        "Secondary Trading": "app.prompts.templates.secondary_trading",
        "Security & Intercreditor": "app.prompts.templates.security_intercreditor",
        "Origination Documents": "app.prompts.templates.origination",
        "Sustainable Finance": "app.prompts.templates.sustainable_finance",
        "Regional Documents": "app.prompts.templates.regional",
        "Regulatory": "app.prompts.templates.regulatory",
        "Restructuring": "app.prompts.templates.restructuring",
        "Supporting Documents": "app.prompts.templates.supporting",
    }
    
    
    # Mapping of section names to prompt variable names
    SECTION_PROMPT_MAP = {
        "Facility Agreement": {
            "representations_and_warranties": "REPRESENTATIONS_PROMPT",
            "conditions_precedent": "CONDITIONS_PRECEDENT_PROMPT",
            "covenants": "COVENANTS_PROMPT",
            "esg_spt": "ESG_SPT_PROMPT",
            "events_of_default": "EVENTS_OF_DEFAULT_PROMPT",
            "governing_law_clause": "GOVERNING_LAW_PROMPT",
            # REF (Real Estate Finance) prompts
            "property_description": "PROPERTY_DESCRIPTION_PROMPT",
            "security_package": "SECURITY_PACKAGE_PROMPT",
            "valuation_requirements": "VALUATION_REQUIREMENTS_PROMPT",
            # SLL (Sustainability-Linked Loan) prompts
            "spt_measurement_methodology": "SPT_MEASUREMENT_METHODOLOGY_PROMPT",
            "margin_adjustment_mechanism": "MARGIN_ADJUSTMENT_MECHANISM_PROMPT",
            "reporting_requirements": "REPORTING_REQUIREMENTS_PROMPT",
            "verification_process": "VERIFICATION_PROCESS_PROMPT",
        },
        "Term Sheet": {
            "purpose": "PURPOSE_PROMPT",
            "conditions_precedent": "CONDITIONS_PRECEDENT_PROMPT",
            "representations": "REPRESENTATIONS_PROMPT",
            "fees": "FEES_PROMPT",
        },
        "Confidentiality Agreement": {
            "confidentiality_obligations": "CONFIDENTIALITY_OBLIGATIONS_PROMPT",
            "no_front_running_undertaking": "NO_FRONT_RUNNING_UNDERTAKING_PROMPT",
            "permitted_disclosures": "PERMITTED_DISCLOSURES_PROMPT",
        },
        "Secondary Trading": {
            "assignment_clause": "ASSIGNMENT_CLAUSE_PROMPT",
            "transfer_restrictions": "TRANSFER_RESTRICTIONS_PROMPT",
            "participation_agreement": "PARTICIPATION_AGREEMENT_PROMPT",
        },
        "Security & Intercreditor": {
            "security_package_description": "SECURITY_PACKAGE_DESCRIPTION_PROMPT",
            "intercreditor_arrangements": "INTERCREDITOR_ARRANGEMENTS_PROMPT",
            "subordination_provisions": "SUBORDINATION_PROVISIONS_PROMPT",
            "enforcement_rights": "ENFORCEMENT_RIGHTS_PROMPT",
        },
        "Origination Documents": {
            "commitment_letter": "COMMITMENT_LETTER_PROMPT",
            "underwriting_terms": "UNDERWRITING_TERMS_PROMPT",
            "syndication_terms": "SYNDICATION_TERMS_PROMPT",
        },
        "Sustainable Finance": {
            "green_loan_framework": "GREEN_LOAN_FRAMEWORK_PROMPT",
            "esg_reporting_framework": "ESG_REPORTING_FRAMEWORK_PROMPT",
            "sustainability_certification": "SUSTAINABILITY_CERTIFICATION_PROMPT",
        },
        "Regional Documents": {
            "regional_compliance": "REGIONAL_COMPLIANCE_PROMPT",
            "jurisdiction_specific_provisions": "JURISDICTION_SPECIFIC_PROVISIONS_PROMPT",
        },
        "Regulatory": {
            "regulatory_compliance": "REGULATORY_COMPLIANCE_PROMPT",
            "mica_compliance": "MICA_COMPLIANCE_PROMPT",
            "basel_iii_compliance": "BASEL_III_COMPLIANCE_PROMPT",
            "fatf_compliance": "FATF_COMPLIANCE_PROMPT",
        },
        "Restructuring": {
            "restructuring_terms": "RESTRUCTURING_TERMS_PROMPT",
            "workout_agreement": "WORKOUT_AGREEMENT_PROMPT",
            "forbearance_provisions": "FORBEARANCE_PROVISIONS_PROMPT",
            "debt_compromise": "DEBT_COMPROMISE_PROMPT",
        },
        "Supporting Documents": {
            "legal_opinion": "LEGAL_OPINION_PROMPT",
            "compliance_certificate": "COMPLIANCE_CERTIFICATE_PROMPT",
            "authorization_resolution": "AUTHORIZATION_RESOLUTION_PROMPT",
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
            # Try category-specific dictionary names
            category_prompts_name = template_category.upper().replace(' ', '_').replace('&', '').replace('-', '_') + "_PROMPTS"
            if hasattr(module, category_prompts_name):
                prompts_dict = getattr(module, category_prompts_name)
            elif hasattr(module, "FACILITY_AGREEMENT_PROMPTS"):
                prompts_dict = getattr(module, "FACILITY_AGREEMENT_PROMPTS")
            elif hasattr(module, "TERM_SHEET_PROMPTS"):
                prompts_dict = getattr(module, "TERM_SHEET_PROMPT")
            elif hasattr(module, "CONFIDENTIALITY_AGREEMENT_PROMPTS"):
                prompts_dict = getattr(module, "CONFIDENTIALITY_AGREEMENT_PROMPTS")
            elif hasattr(module, "SECONDARY_TRADING_PROMPTS"):
                prompts_dict = getattr(module, "SECONDARY_TRADING_PROMPTS")
            elif hasattr(module, "SECURITY_INTERCREDITOR_PROMPTS"):
                prompts_dict = getattr(module, "SECURITY_INTERCREDITOR_PROMPTS")
            elif hasattr(module, "ORIGINATION_PROMPTS"):
                prompts_dict = getattr(module, "ORIGINATION_PROMPTS")
            elif hasattr(module, "SUSTAINABLE_FINANCE_PROMPTS"):
                prompts_dict = getattr(module, "SUSTAINABLE_FINANCE_PROMPTS")
            elif hasattr(module, "REGIONAL_PROMPTS"):
                prompts_dict = getattr(module, "REGIONAL_PROMPTS")
            elif hasattr(module, "REGULATORY_PROMPTS"):
                prompts_dict = getattr(module, "REGULATORY_PROMPTS")
            elif hasattr(module, "RESTRUCTURING_PROMPTS"):
                prompts_dict = getattr(module, "RESTRUCTURING_PROMPTS")
            elif hasattr(module, "SUPPORTING_PROMPTS"):
                prompts_dict = getattr(module, "SUPPORTING_PROMPTS")
            elif hasattr(module, "PROMPTS"):
                prompts_dict = getattr(module, "PROMPTS")
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

















"""
AI field population engine for LMA template generation.

Uses LLM to generate AI-populated sections like representations, covenants,
conditions precedent, events of default, and ESG clauses.
"""

import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal

from app.models.cdm import CreditAgreement
from app.db.models import LMATemplate
from app.core.llm_client import get_chat_model
from app.prompts.templates.loader import PromptLoader

logger = logging.getLogger(__name__)


class AIFieldPopulator:
    """
    Populates AI-generated fields in LMA templates using LLM.
    
    Generates legal clauses based on CDM CreditAgreement data and
    template-specific prompts.
    """
    
    def __init__(self):
        """Initialize AI field populator with LLM."""
        self.llm = get_chat_model()
        self.prompt_loader = PromptLoader()
        logger.info("AIFieldPopulator initialized")
    
    def populate_ai_fields(
        self,
        cdm_data: CreditAgreement,
        template: LMATemplate,
        mapped_fields: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Populate all AI-generated fields for a template.
        
        Args:
            cdm_data: CreditAgreement instance with CDM data
            template: LMATemplate instance
            mapped_fields: Already mapped direct/computed fields (for context)
            
        Returns:
            Dictionary mapping template field names to generated content
            Example: {"[REPRESENTATIONS_AND_WARRANTIES]": "1. The Borrower represents...", ...}
        """
        ai_fields = {}
        
        # Get list of AI-generated sections from template
        ai_sections = template.ai_generated_sections or []
        if isinstance(ai_sections, dict):
            ai_sections = ai_sections.get("sections", [])
        
        if not ai_sections:
            logger.debug(f"No AI-generated sections specified for template {template.template_code}")
            return ai_fields
        
        # Generate each section
        for section_name in ai_sections:
            try:
                generated_content = self._generate_section(
                    section_name=section_name,
                    cdm_data=cdm_data,
                    template=template,
                    mapped_fields=mapped_fields
                )
                
                if generated_content:
                    # Map section name to template field placeholder
                    # Section names like "representations_and_warranties" map to "[REPRESENTATIONS_AND_WARRANTIES]"
                    template_field = f"[{section_name.upper().replace('_', '_')}]"
                    ai_fields[template_field] = generated_content
                    logger.debug(f"Generated {section_name} ({len(generated_content)} chars)")
                else:
                    logger.warning(f"Failed to generate content for section {section_name}")
                    
            except Exception as e:
                logger.error(f"Error generating section {section_name}: {e}", exc_info=True)
                continue
        
        logger.info(f"Generated {len(ai_fields)} AI field(s) for template {template.template_code}")
        return ai_fields
    
    def _generate_section(
        self,
        section_name: str,
        cdm_data: CreditAgreement,
        template: LMATemplate,
        mapped_fields: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Generate a specific section using LLM.
        
        Args:
            section_name: Section name (e.g., "representations_and_warranties")
            cdm_data: CreditAgreement instance
            template: LMATemplate instance
            mapped_fields: Optional already-mapped fields for context
            
        Returns:
            Generated text content or None if generation fails
        """
        # Load section-specific prompt
        prompt_template = self.prompt_loader.get_prompt_for_section(
            template_category=template.category,
            section_name=section_name
        )
        
        if not prompt_template:
            logger.warning(f"No prompt template found for section '{section_name}' in category '{template.category}'")
            return None
        
        # Prepare prompt variables from CDM data
        prompt_vars = self._prepare_prompt_variables(cdm_data, template, mapped_fields)
        
        try:
            # Format prompt with variables
            messages = prompt_template.format_messages(**prompt_vars)
            
            # Invoke LLM
            response = self.llm.invoke(messages)
            
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error invoking LLM for section {section_name}: {e}", exc_info=True)
            return None
    
    def _prepare_prompt_variables(
        self,
        cdm_data: CreditAgreement,
        template: LMATemplate,
        mapped_fields: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare variables for prompt templates from CDM data.
        
        Args:
            cdm_data: CreditAgreement instance
            template: LMATemplate instance
            mapped_fields: Optional already-mapped fields
            
        Returns:
            Dictionary of prompt variables
        """
        # Extract borrower information
        borrower = next(
            (p for p in (cdm_data.parties or []) if "borrower" in p.role.lower()),
            None
        )
        borrower_name = borrower.name if borrower else "Unknown Borrower"
        borrower_lei = borrower.lei if borrower else None
        
        # Extract facility information
        facility = cdm_data.facilities[0] if cdm_data.facilities else None
        facility_name = facility.facility_name if facility else "Unknown Facility"
        commitment_amount = facility.commitment_amount.amount if facility and facility.commitment_amount else Decimal("0")
        currency = facility.commitment_amount.currency.value if facility and facility.commitment_amount else "USD"
        maturity_date = facility.maturity_date.strftime("%d %B %Y") if facility and facility.maturity_date else None
        
        # Extract interest rate information
        interest_rate = None
        if facility and facility.interest_terms and facility.interest_terms.rate_option:
            benchmark = facility.interest_terms.rate_option.benchmark
            spread_bps = facility.interest_terms.rate_option.spread_bps
            spread_pct = spread_bps / 100.0
            interest_rate = f"{benchmark} + {spread_pct:.2f}%"
        
        # Extract ESG KPI targets
        esg_kpi_targets = None
        if cdm_data.esg_kpi_targets:
            esg_kpi_targets = "\n".join([
                f"- {kpi.kpi_type.value}: {kpi.target_value} {kpi.unit} "
                f"(margin adjustment: {kpi.margin_adjustment_bps} bps)"
                for kpi in cdm_data.esg_kpi_targets
            ])
        
        # Calculate total commitment
        total_commitment = Decimal("0")
        if cdm_data.facilities:
            for fac in cdm_data.facilities:
                if fac.commitment_amount:
                    total_commitment += fac.commitment_amount.amount
        
        # Format agreement date
        agreement_date = cdm_data.agreement_date.strftime("%d %B %Y") if cdm_data.agreement_date else None
        
        # Additional context from mapped fields
        additional_context = ""
        if mapped_fields:
            context_items = [
                f"{key}: {value}" for key, value in mapped_fields.items()
                if value and not key.startswith("[")  # Exclude template placeholders
            ]
            if context_items:
                additional_context = "\n".join(context_items)
        
        return {
            "borrower_name": borrower_name,
            "borrower_lei": borrower_lei or "Not provided",
            "facility_name": facility_name,
            "total_commitment": f"{total_commitment:,.2f}",
            "commitment_amount": f"{commitment_amount:,.2f}",
            "currency": currency,
            "maturity_date": maturity_date or "Not specified",
            "interest_rate": interest_rate or "Not specified",
            "governing_law": template.governing_law or cdm_data.governing_law or "English",
            "agreement_date": agreement_date or "Not specified",
            "esg_kpi_targets": esg_kpi_targets or "Not applicable",
            "sustainability_linked": "Yes" if cdm_data.sustainability_linked else "No",
            "additional_context": additional_context,
        }
    
    def _generate_representations(
        self,
        cdm_data: CreditAgreement,
        template: LMATemplate,
        governing_law: str
    ) -> str:
        """
        Generate Representations and Warranties section.
        
        Args:
            cdm_data: CreditAgreement instance
            template: LMATemplate instance
            governing_law: Governing law jurisdiction
            
        Returns:
            Generated representations text
        """
        return self._generate_section(
            section_name="representations_and_warranties",
            cdm_data=cdm_data,
            template=template,
            mapped_fields=None
        ) or ""
    
    def _generate_conditions_precedent(
        self,
        cdm_data: CreditAgreement,
        template: LMATemplate,
        governing_law: str
    ) -> str:
        """
        Generate Conditions Precedent section.
        
        Args:
            cdm_data: CreditAgreement instance
            template: LMATemplate instance
            governing_law: Governing law jurisdiction
            
        Returns:
            Generated conditions precedent text
        """
        return self._generate_section(
            section_name="conditions_precedent",
            cdm_data=cdm_data,
            template=template,
            mapped_fields=None
        ) or ""
    
    def _generate_covenants(
        self,
        cdm_data: CreditAgreement,
        template: LMATemplate
    ) -> str:
        """
        Generate Covenants section.
        
        Args:
            cdm_data: CreditAgreement instance
            template: LMATemplate instance
            
        Returns:
            Generated covenants text
        """
        return self._generate_section(
            section_name="covenants",
            cdm_data=cdm_data,
            template=template,
            mapped_fields=None
        ) or ""
    
    def _generate_esg_clauses(
        self,
        cdm_data: CreditAgreement,
        template: LMATemplate
    ) -> str:
        """
        Generate ESG/SPT clauses for sustainability-linked loans.
        
        Args:
            cdm_data: CreditAgreement instance
            template: LMATemplate instance
            
        Returns:
            Generated ESG clauses text
        """
        if not cdm_data.sustainability_linked:
            return ""
        
        return self._generate_section(
            section_name="esg_spt",
            cdm_data=cdm_data,
            template=template,
            mapped_fields=None
        ) or ""
    
    def _generate_events_of_default(
        self,
        cdm_data: CreditAgreement,
        template: LMATemplate,
        governing_law: str
    ) -> str:
        """
        Generate Events of Default section.
        
        Args:
            cdm_data: CreditAgreement instance
            template: LMATemplate instance
            governing_law: Governing law jurisdiction
            
        Returns:
            Generated events of default text
        """
        return self._generate_section(
            section_name="events_of_default",
            cdm_data=cdm_data,
            template=template,
            mapped_fields=None
        ) or ""


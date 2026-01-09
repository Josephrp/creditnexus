"""
Template-aware extraction system for CDM data extraction.

This module provides extraction capabilities that are aware of template requirements,
allowing for prioritized field extraction based on the target template's needs.
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

from app.core.llm_client import get_chat_model
from app.models.cdm import CreditAgreement, ExtractionResult
from app.templates.registry import TemplateRegistry
from app.db.models import LMATemplate
from app.chains.extraction_chain import extract_data, extract_data_smart, MAP_REDUCE_THRESHOLD
from app.chains.map_reduce_chain import extract_data_map_reduce

logger = logging.getLogger(__name__)


class TemplateAwareExtractor:
    """
    Extracts CDM data with awareness of template requirements.
    
    Prioritizes extraction of fields required by the target template,
    ensuring better completeness for document generation.
    """
    
    def __init__(self, db: Session, template_id: Optional[int] = None):
        """
        Initialize template-aware extractor.
        
        Args:
            db: Database session
            template_id: Optional template ID to use for field prioritization
        """
        self.db = db
        self.template_id = template_id
        self.template: Optional[LMATemplate] = None
        
        if template_id:
            try:
                self.template = TemplateRegistry.get_template(db, template_id)
                logger.info(f"Initialized TemplateAwareExtractor for template {self.template.template_code}")
            except Exception as e:
                logger.warning(f"Could not load template {template_id}: {e}. Proceeding without template awareness.")
                self.template = None
    
    def create_template_aware_prompt(self) -> ChatPromptTemplate:
        """
        Create extraction prompt that prioritizes template-required fields.
        
        Returns:
            ChatPromptTemplate with template-aware instructions
        """
        # Base system prompt
        system_prompt = """You are an expert Credit Analyst. Your task is to extract structured data from the provided Credit Agreement text.

Your responsibilities:
1. Extract the exact legal names of parties and their roles (Borrower, Lender, Administrative Agent, etc.)
2. Extract LEI (Legal Entity Identifier) for parties when available
3. Normalize all financial amounts to the Money structure (amount as Decimal, currency as code)
4. Convert percentage spreads to basis points (e.g., 3.5% -> 350.0, 2.75% -> 275.0)
5. Extract dates in ISO 8601 format (YYYY-MM-DD)
6. Identify all loan facilities and their terms including:
   - Facility name
   - Commitment amount and currency
   - Maturity date
   - Interest rate terms (benchmark, spread in basis points, payment frequency)
7. Extract payment frequency with both period (Day/Week/Month/Year) and period_multiplier (e.g., 3 for quarterly)
8. Extract the governing law/jurisdiction
9. Extract sustainability-linked loan provisions if present (ESG KPI targets, margin adjustments)
10. Set extraction_status:
   - success: valid credit agreement extracted
   - partial_data_missing: some fields missing/uncertain
   - irrelevant_document: not a credit agreement or insufficient info"""

        # Add template-specific field priorities if template is available
        if self.template:
            required_fields = self.template.required_fields or []
            optional_fields = self.template.optional_fields or []
            
            # Normalize field lists (handle both list and dict formats)
            if isinstance(required_fields, dict):
                required_fields = required_fields.get("fields", [])
            if isinstance(optional_fields, dict):
                optional_fields = optional_fields.get("fields", [])
            
            if required_fields:
                system_prompt += f"""

TEMPLATE-SPECIFIC REQUIREMENTS:
This extraction is for template: {self.template.name} ({self.template.template_code})
Category: {self.template.category}

CRITICAL PRIORITY FIELDS (must extract if present in document):
{self._format_field_list(required_fields)}

OPTIONAL BUT RECOMMENDED FIELDS:
{self._format_field_list(optional_fields) if optional_fields else "None specified"}

IMPORTANT: Pay special attention to extracting the CRITICAL PRIORITY FIELDS listed above.
These fields are required for document generation. If any of these fields are mentioned
in the document (even partially), make every effort to extract them accurately.
"""
            
            # Add category-specific guidance
            category_guidance = self._get_category_guidance(self.template.category)
            if category_guidance:
                system_prompt += f"\n\nCATEGORY-SPECIFIC GUIDANCE:\n{category_guidance}"
        
        system_prompt += """

CRITICAL RULES:
- If a field is not explicitly stated in the text, return None/Null. Do not guess or infer values.
- Do not use market standards or assumptions unless explicitly mentioned in the document.
- Convert written numbers (e.g., "five million") to numeric values.
- Ensure all dates are valid and in the correct format.
- For interest rates, always extract the spread in basis points (multiply percentages by 100).
- For payment frequency, extract both period (e.g., "Month") and period_multiplier (e.g., 3 for "every 3 months").
- Always extract spread_bps (spread in basis points) and period_multiplier for payment frequency.
"""

        user_prompt = "Contract Text: {text}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        
        return prompt
    
    def _format_field_list(self, fields: List[str]) -> str:
        """Format field list for prompt display."""
        if not fields:
            return "None"
        
        formatted = []
        for i, field in enumerate(fields[:20], 1):  # Limit to 20 fields for prompt size
            # Format field path for readability
            display_name = field.replace("_", " ").replace(".", " → ")
            formatted.append(f"{i}. {display_name} ({field})")
        
        if len(fields) > 20:
            formatted.append(f"... and {len(fields) - 20} more fields")
        
        return "\n".join(formatted)
    
    def _get_category_guidance(self, category: str) -> Optional[str]:
        """Get category-specific extraction guidance."""
        guidance_map = {
            "Sustainable Finance": """
- Pay special attention to sustainability-linked provisions
- Extract ESG KPI targets, performance metrics, and margin adjustment mechanisms
- Look for green loan framework certifications or sustainability certifications
- Extract reporting obligations related to sustainability performance
""",
            "Regulatory": """
- Extract regulatory compliance statements (FATF, Basel III, MiCA)
- Look for customer due diligence (CDD) obligations
- Extract suspicious transaction reporting requirements
- Identify sanctions compliance provisions
- Extract capital adequacy certifications and risk weighting disclosures
""",
            "Security & Intercreditor": """
- Extract priority provisions and subordination arrangements
- Identify voting mechanisms and decision-making processes
- Extract standstill provisions and enforcement restrictions
- Look for intercreditor agreement terms
""",
            "Origination Documents": """
- Extract AML (Anti-Money Laundering) certifications
- Identify source of funds declarations
- Extract ongoing compliance obligations
- Look for KYC (Know Your Customer) requirements
""",
            "Secondary Trading": """
- Extract collateral obligations and security arrangements
- Identify margin calculation methodologies
- Extract transfer provisions and assignment restrictions
- Look for dispute resolution mechanisms
""",
        }
        return guidance_map.get(category)
    
    def extract_with_template_awareness(
        self,
        text: str,
        force_map_reduce: bool = False,
        max_retries: int = 3
    ) -> ExtractionResult:
        """
        Extract CDM data with template-aware prioritization.
        
        Args:
            text: Document text to extract from
            force_map_reduce: Force map-reduce strategy
            max_retries: Maximum retry attempts
            
        Returns:
            ExtractionResult with extracted CDM data
        """
        # Use map-reduce for long documents
        text_length = len(text)
        if force_map_reduce or text_length > MAP_REDUCE_THRESHOLD:
            logger.info(f"Using map-reduce strategy for template-aware extraction (length: {text_length})")
            # For map-reduce, we'll use the standard prompt but could enhance it
            return extract_data_map_reduce(text)
        
        # Use template-aware prompt for simple extraction
        prompt = self.create_template_aware_prompt()
        llm = get_chat_model(temperature=0)
        structured_llm = llm.with_structured_output(ExtractionResult)
        extraction_chain = prompt | structured_llm
        
        logger.info(f"Extracting with template awareness (template_id: {self.template_id}, length: {text_length})")
        
        last_error: Optional[Exception] = None
        
        for attempt in range(max_retries):
            try:
                result = extraction_chain.invoke({"text": text})
                
                # Validate against template requirements if template is available
                if self.template and result.agreement:
                    validation_result = self.validate_extraction_for_template(result.agreement)
                    if validation_result["missing_critical"]:
                        logger.warning(
                            f"Extraction missing {len(validation_result['missing_critical'])} critical fields: "
                            f"{validation_result['missing_critical'][:5]}"
                        )
                
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Extraction attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Add error context to prompt for retry
                    error_context = f"\n\nPrevious extraction attempt failed with error: {str(e)}. Please correct the extraction."
                    # Could enhance prompt with error context, but for now just retry
                    continue
                else:
                    raise ValueError(f"Template-aware extraction failed after {max_retries} attempts: {e}") from last_error
        
        raise ValueError(f"Template-aware extraction failed: {last_error}") from last_error
    
    def validate_extraction_for_template(self, cdm_data: CreditAgreement) -> Dict[str, Any]:
        """
        Validate extracted CDM data against template requirements.
        
        Args:
            cdm_data: Extracted CreditAgreement instance
            
        Returns:
            Dictionary with validation results:
            - missing_critical: List of missing required fields
            - missing_optional: List of missing optional fields
            - completeness_score: Percentage (0-100)
            - is_valid: Boolean indicating if all critical fields are present
        """
        if not self.template:
            return {
                "missing_critical": [],
                "missing_optional": [],
                "completeness_score": 100.0,
                "is_valid": True,
                "message": "No template specified for validation"
            }
        
        from app.generation.field_parser import FieldPathParser
        
        required_fields = self.template.required_fields or []
        optional_fields = self.template.optional_fields or []
        
        # Normalize field lists
        if isinstance(required_fields, dict):
            required_fields = required_fields.get("fields", [])
        if isinstance(optional_fields, dict):
            optional_fields = optional_fields.get("fields", [])
        
        parser = FieldPathParser()
        
        # Check required fields
        missing_critical = []
        for field_path in required_fields:
            value = parser.get_nested_value(cdm_data, field_path)
            if value is None or value == "":
                missing_critical.append(field_path)
        
        # Check optional fields
        missing_optional = []
        for field_path in optional_fields:
            value = parser.get_nested_value(cdm_data, field_path)
            if value is None or value == "":
                missing_optional.append(field_path)
        
        # Calculate completeness score
        total_required = len(required_fields)
        if total_required > 0:
            completeness_score = ((total_required - len(missing_critical)) / total_required) * 100
        else:
            completeness_score = 100.0
        
        is_valid = len(missing_critical) == 0
        
        return {
            "missing_critical": missing_critical,
            "missing_optional": missing_optional,
            "completeness_score": round(completeness_score, 1),
            "is_valid": is_valid,
            "total_required": total_required,
            "total_optional": len(optional_fields),
            "present_required": total_required - len(missing_critical),
            "present_optional": len(optional_fields) - len(missing_optional)
        }


def extract_with_template(
    db: Session,
    text: str,
    template_id: Optional[int] = None,
    force_map_reduce: bool = False,
    max_retries: int = 3
) -> ExtractionResult:
    """
    Convenience function for template-aware extraction.
    
    Args:
        db: Database session
        text: Document text to extract from
        template_id: Optional template ID for field prioritization
        force_map_reduce: Force map-reduce strategy
        max_retries: Maximum retry attempts
        
    Returns:
        ExtractionResult with extracted CDM data
    """
    extractor = TemplateAwareExtractor(db=db, template_id=template_id)
    return extractor.extract_with_template_awareness(
        text=text,
        force_map_reduce=force_map_reduce,
        max_retries=max_retries
    )

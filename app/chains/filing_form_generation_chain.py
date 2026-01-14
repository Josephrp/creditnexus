"""LangChain chain for generating pre-filled form data for manual filings."""

import logging
from typing import Optional, Dict, Any
from pydantic import ValidationError

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_client import get_chat_model
from app.models.filing_forms import FilingFormData
from app.models.cdm import CreditAgreement
from app.models.filing_requirements import FilingRequirement

logger = logging.getLogger(__name__)


def create_filing_form_chain() -> BaseChatModel:
    """Create and configure the LangChain filing form generation chain.
    
    Returns:
        A BaseChatModel instance configured with structured output
        bound to the FilingFormData Pydantic model.
    """
    llm = get_chat_model(temperature=0)
    structured_llm = llm.with_structured_output(FilingFormData)
    return structured_llm


def create_filing_form_prompt() -> ChatPromptTemplate:
    """Create the prompt template for filing form data generation.
    
    Returns:
        A ChatPromptTemplate with system and user message templates.
    """
    system_prompt = """You are an expert Regulatory Filing Specialist. Your task is to generate pre-filled form data for manual regulatory filings based on credit agreement (CDM) data and filing requirements.

Your responsibilities:
1. Extract relevant data from the credit agreement (CDM format)
2. Map CDM fields to jurisdiction-specific form fields
3. Format data according to form field requirements (dates, numbers, text)
4. Identify required vs optional fields
5. Provide helpful instructions for manual submission
6. Generate submission URLs when available

JURISDICTION-SPECIFIC FORM MAPPINGS:

**US SEC 8-K Form**:
- Company Name → "Company Name" (text)
- CIK (if available) → "CIK" (text)
- Agreement Date → "Agreement Date" (date: YYYY-MM-DD)
- Total Commitment → "Total Commitment" (number with currency)
- Borrower Name → "Borrower" (text)
- Lender Names → "Lenders" (text, comma-separated)
- Governing Law → "Governing Law" (text)
- Form Type: "8-K"
- Submission URL: "https://www.sec.gov/edgar/searchedgar/companysearch.html"

**France AMF Declaration**:
- Company Name → "Nom de la société" (text, French)
- SIREN (if available) → "Numéro SIREN" (text)
- Agreement Date → "Date de l'accord" (date: DD/MM/YYYY)
- Total Commitment → "Montant total" (number with currency: EUR)
- Borrower Name → "Emprunteur" (text, French)
- Lender Names → "Prêteurs" (text, comma-separated, French)
- Form Type: "Declaration de prêt"
- Language: "fr"
- Submission URL: "https://www.amf-france.org/..."

**Germany BaFin Registration**:
- Company Name → "Firmenname" (text, German)
- HRB Number (if available) → "HRB-Nummer" (text)
- Agreement Date → "Vertragsdatum" (date: DD.MM.YYYY)
- Total Commitment → "Gesamtbetrag" (number with currency: EUR)
- Borrower Name → "Kreditnehmer" (text, German)
- Lender Names → "Kreditgeber" (text, comma-separated, German)
- Form Type: "Kreditvertrag Anmeldung"
- Language: "de"
- Submission URL: "https://www.bafin.de/..."

CRITICAL RULES:
- Map CDM fields accurately to form fields
- Format dates according to jurisdiction conventions
- Use appropriate language (English for US/UK, French for FR, German for DE)
- Include all required fields from FilingRequirement
- Mark optional fields appropriately
- Provide clear field names and help text
- Include document references for attachments
- Generate accurate submission URLs
- Handle missing data gracefully (use None/null for missing fields)"""

    user_prompt = """Credit Agreement (CDM Format):
{cdm_data}

Filing Requirement:
- Authority: {authority}
- Jurisdiction: {jurisdiction}
- Form Type: {form_type}
- Required Fields: {required_fields}
- Deadline: {deadline}

Additional Context:
- Document ID: {document_id}
- Deal ID: {deal_id}

Generate pre-filled form data for this filing requirement. Map CDM data to form fields accurately."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    return prompt


def _get_language_for_jurisdiction(jurisdiction: str) -> str:
    """Get language code for a jurisdiction.
    
    Args:
        jurisdiction: Jurisdiction code (US, UK, FR, DE, etc.)
        
    Returns:
        Language code (en, fr, de, etc.)
    """
    language_map = {
        "FR": "fr",
        "DE": "de",
        "US": "en",
        "UK": "en",
        "GB": "en"
    }
    return language_map.get(jurisdiction.upper(), "en")


def _get_language_prompt(language: str) -> str:
    """Get language-specific prompt instructions.
    
    Args:
        language: Language code (en, fr, de)
        
    Returns:
        Language-specific prompt text
    """
    if language == "fr":
        return """INSTRUCTIONS EN FRANÇAIS:
- Tous les champs de formulaire doivent être en français
- Les noms de champs doivent être traduits en français
- Les dates doivent être au format français (DD/MM/YYYY)
- Les montants doivent être formatés selon les conventions françaises
- Les instructions doivent être en français
- Utilisez les termes réglementaires français appropriés"""
    
    elif language == "de":
        return """ANWEISUNGEN AUF DEUTSCH:
- Alle Formularfelder müssen auf Deutsch sein
- Feldnamen müssen ins Deutsche übersetzt werden
- Daten müssen im deutschen Format sein (DD.MM.YYYY)
- Beträge müssen nach deutschen Konventionen formatiert werden
- Anweisungen müssen auf Deutsch sein
- Verwenden Sie die entsprechenden deutschen Regulierungsbegriffe"""
    
    else:
        return """INSTRUCTIONS IN ENGLISH:
- All form fields should be in English
- Field names should be in English
- Dates should be in ISO format (YYYY-MM-DD) or jurisdiction-specific format
- Amounts should be formatted according to jurisdiction conventions
- Instructions should be in English
- Use appropriate regulatory terminology"""


def generate_filing_form_data(
    credit_agreement: CreditAgreement,
    filing_requirement: FilingRequirement,
    document_id: Optional[int] = None,
    deal_id: Optional[int] = None,
    language: Optional[str] = None,
    max_retries: int = 3
) -> FilingFormData:
    """Generate pre-filled form data for a filing requirement.
    
    Args:
        credit_agreement: CreditAgreement CDM model instance
        filing_requirement: FilingRequirement instance
        document_id: Optional document ID
        deal_id: Optional deal ID
        language: Optional language code (en, fr, de). If not provided, auto-detected from jurisdiction
        max_retries: Maximum retry attempts
        
    Returns:
        FilingFormData instance
        
    Raises:
        ValueError: If generation fails after retries
    """
    # Determine language
    if not language:
        language = filing_requirement.language_requirement or _get_language_for_jurisdiction(filing_requirement.jurisdiction)
    
    logger.info(f"Generating filing form data in language: {language} for jurisdiction: {filing_requirement.jurisdiction}")
    
    # Create language-specific prompt
    base_prompt = create_filing_form_prompt()
    language_instructions = _get_language_prompt(language)
    
    # Enhance system prompt with language instructions
    enhanced_system_prompt = base_prompt.messages[0].content + f"\n\n{language_instructions}"
    
    # Create enhanced prompt
    from langchain_core.prompts import ChatPromptTemplate
    enhanced_prompt = ChatPromptTemplate.from_messages([
        ("system", enhanced_system_prompt),
        ("user", base_prompt.messages[1].content)
    ])
    
    structured_llm = create_filing_form_chain()
    generation_chain = enhanced_prompt | structured_llm
    
    cdm_data = credit_agreement.model_dump_json(indent=2)
    
    last_error: Exception | None = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Filing form generation attempt {attempt + 1}/{max_retries} (language: {language})...")
            
            result = generation_chain.invoke({
                "cdm_data": cdm_data,
                "authority": filing_requirement.authority,
                "jurisdiction": filing_requirement.jurisdiction,
                "form_type": filing_requirement.form_type or "N/A",
                "required_fields": ", ".join(filing_requirement.required_fields),
                "deadline": filing_requirement.deadline.isoformat(),
                "document_id": str(document_id) if document_id else "N/A",
                "deal_id": str(deal_id) if deal_id else "N/A",
                "language": language
            })
            
            logger.info(f"Filing form generation completed successfully in {language}")
            return result
            
        except ValidationError as e:
            last_error = e
            logger.warning(f"Validation error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                logger.info("Retrying with validation feedback...")
                continue
            raise ValueError(f"Filing form generation failed validation after {max_retries} attempts: {e}") from e
            
        except Exception as e:
            logger.error(f"Unexpected error during filing form generation: {e}")
            raise ValueError(f"Filing form generation failed: {e}") from e

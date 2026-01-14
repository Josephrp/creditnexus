"""Chain for editing CDM fields using AI and multimodal context.

This module implements AI-assisted editing of specific CDM fields in a
CreditAgreement, using multimodal context to determine the most accurate value.
"""

import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_client import get_chat_model
from app.models.cdm import CreditAgreement

logger = logging.getLogger(__name__)


def create_cdm_edit_chain() -> BaseChatModel:
    """Create chain for AI-assisted CDM field editing.
    
    Returns:
        A BaseChatModel instance configured with structured output
        bound to the CreditAgreement Pydantic model.
    """
    llm = get_chat_model(temperature=0)
    structured_llm = llm.with_structured_output(CreditAgreement)
    return structured_llm


def create_cdm_edit_prompt() -> ChatPromptTemplate:
    """Create prompt for editing CDM fields with AI assistance.
    
    Returns:
        A ChatPromptTemplate with system and user message templates.
    """
    system_prompt = """You are an expert Credit Analyst tasked with EDITING a specific field in a CreditAgreement using multimodal context.

You will receive:
1. The complete CreditAgreement object
2. The field_path to edit (e.g., "parties[0].name", "facilities[0].commitment_amount.amount")
3. The current value of the field
4. A suggested new value (from user input or multimodal extraction)
5. Multimodal context (audio, image, document, text) that may contain the correct value

Your task:
1. Analyze the multimodal context to find the most accurate value
2. Validate the new value against CDM rules:
   - Dates must be ISO 8601 format (YYYY-MM-DD)
   - Amounts must be Decimal with currency
   - Spreads must be in basis points (multiply percentages by 100)
   - LEIs must be 20 characters
3. Edit ONLY the specified field, preserving all other data
4. Return the complete CreditAgreement with the edited field

CRITICAL RULES:
- Only modify the field specified by field_path
- Preserve all other fields exactly as they are
- Validate the new value format and type
- If multimodal context conflicts, prefer: text > document > image > audio
- If new value is invalid, use the most accurate value from multimodal context
- Ensure the result is a valid CreditAgreement
"""
    
    user_prompt = """CreditAgreement:
{cdm_data}

Field to Edit: {field_path}
Current Value: {current_value}
Suggested New Value: {new_value}

Multimodal Context:
- Audio transcription: {audio_text}
- Image OCR: {image_text}
- Document text: {document_text}
- Direct text: {text_input}

Edit the specified field using the most accurate value from multimodal context.
Return the complete CreditAgreement with the edited field."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    return prompt

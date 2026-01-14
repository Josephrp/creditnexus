"""Chain for safely removing CDM fields using AI decision support.

This module evaluates whether a CDM field can be safely removed from a
CreditAgreement without breaking validation rules or creating inconsistencies.
"""

import logging
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.llm_client import get_chat_model

logger = logging.getLogger(__name__)


class RemovalDecision(BaseModel):
    """Decision about whether a field can be safely removed."""
    safe: bool
    reason: str
    alternative_action: Optional[str] = None


def create_cdm_remove_chain() -> BaseChatModel:
    """Create chain for evaluating field removal safety.
    
    Returns:
        A BaseChatModel instance configured with structured output
        bound to the RemovalDecision Pydantic model.
    """
    llm = get_chat_model(temperature=0)
    structured_llm = llm.with_structured_output(RemovalDecision)
    return structured_llm


def create_cdm_remove_prompt() -> ChatPromptTemplate:
    """Create prompt for evaluating CDM field removal safety.
    
    Returns:
        A ChatPromptTemplate with system and user message templates.
    """
    system_prompt = """You are an expert Credit Analyst tasked with evaluating whether a CDM field can be safely removed from a CreditAgreement.

You will receive:
1. The complete CreditAgreement object
2. The field_path to be removed (e.g., "parties[0].lei", "facilities[1].interest_terms")
3. Multimodal context that may indicate why removal is requested

Your task:
1. Evaluate if removing this field would:
   - Break CDM validation rules (required fields)
   - Create inconsistencies (e.g., facility without interest terms)
   - Remove critical data (e.g., borrower name, facility amount)
2. Determine if removal is SAFE:
   - safe=True: Field is optional and removal won't break agreement
   - safe=False: Field is required or removal would cause issues
3. Provide reasoning and alternative actions if removal is unsafe

CRITICAL RULES:
- Required fields (parties, facilities, agreement_date) CANNOT be removed
- Fields referenced by other fields (e.g., facility.commitment_amount) should not be removed
- Optional metadata fields (e.g., party.lei, facility.description) can usually be removed
- If removal is unsafe, suggest alternative (e.g., set to None, modify instead)
- Consider multimodal context to understand user intent
"""
    
    user_prompt = """CreditAgreement:
{cdm_data}

Field to Remove: {field_path}

Multimodal Context:
- Audio: {audio_text}
- Image: {image_text}
- Document: {document_text}
- Text: {text_input}

Evaluate if this field can be safely removed. Return RemovalDecision."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    return prompt

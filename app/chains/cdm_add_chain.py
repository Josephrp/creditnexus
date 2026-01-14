"""Chain for adding CDM data to existing CreditAgreement using multimodal fusion.

This module implements intelligent addition of new CDM fields to an existing
CreditAgreement without modifying existing data.
"""

import logging
import json
from typing import Optional, Dict, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_client import get_chat_model
from app.models.cdm import CreditAgreement, ExtractionResult
from app.chains.multimodal_fusion_chain import fuse_multimodal_inputs

logger = logging.getLogger(__name__)


def create_cdm_add_chain() -> BaseChatModel:
    """Create chain for adding CDM data to existing agreement.
    
    Returns:
        A BaseChatModel instance configured with structured output
        bound to the ExtractionResult Pydantic model.
    """
    llm = get_chat_model(temperature=0)
    structured_llm = llm.with_structured_output(ExtractionResult)
    return structured_llm


def create_cdm_add_prompt() -> ChatPromptTemplate:
    """Create prompt for adding CDM data to existing CreditAgreement.
    
    Returns:
        A ChatPromptTemplate with system and user message templates.
    """
    system_prompt = """You are an expert Credit Analyst tasked with ADDING new CDM data to an existing CreditAgreement.

You will receive:
1. An existing CreditAgreement object (complete and validated)
2. New CDM data extracted from multimodal sources (audio, image, document, text)

Your task:
1. Identify NEW fields/entities not present in existing agreement:
   - New parties (by name, LEI, or role)
   - New facilities (by facility_name)
   - New ESG KPIs (by kpi_type)
   - Missing dates, amounts, or terms
2. ADD new data without modifying existing data:
   - Append new parties to parties list
   - Append new facilities to facilities list
   - Add new ESG KPIs to esg_kpi_targets list
   - Fill in missing fields (None values) with new data
3. Preserve all existing data:
   - Do not modify existing parties, facilities, or terms
   - Do not overwrite existing field values
   - Only add what is genuinely new or missing

CRITICAL RULES:
- If a party with the same name/LEI exists, DO NOT add it again (it's a duplicate)
- If a facility with the same name exists, DO NOT add it again (it's a duplicate)
- Only add fields that are None/missing in existing agreement
- Preserve all existing field values exactly as they are
- Ensure the result is a valid, complete CreditAgreement
- All required fields must remain present
"""
    
    user_prompt = """Existing CreditAgreement:
{existing_cdm}

New CDM Data from Multimodal Sources:
{new_cdm_data}

Multimodal Context:
- Audio transcription: {audio_text}
- Image OCR: {image_text}
- Document text: {document_text}
- Direct text: {text_input}

Add new data to the existing agreement without modifying existing fields.
Return the enhanced CreditAgreement with new data added."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    return prompt

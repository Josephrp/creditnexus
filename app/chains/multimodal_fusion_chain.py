"""Multimodal fusion chain for combining CDM data from multiple sources.

This module implements intelligent fusion of CDM data extracted from:
- Audio transcription (optional)
- Image OCR (optional)
- Document retrieval (optional)
- Text extraction (required)

The fusion process:
1. Prepends optional inputs (audio, image) to required inputs (document, text)
2. Tracks source for each field
3. Detects conflicts between sources
4. Uses deterministic fallbacks for simple cases
5. Uses LLM for complex merging when conflicts exist
"""

import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import date
from decimal import Decimal
from pydantic import ValidationError

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_client import get_chat_model
from app.models.cdm import CreditAgreement, ExtractionResult, ExtractionStatus
from app.chains.extraction_chain import extract_data_smart

logger = logging.getLogger(__name__)


class SourceMetadata:
    """Metadata about a CDM data source."""
    
    def __init__(
        self,
        source_type: str,  # "audio", "image", "document", "text"
        source_id: Optional[str] = None,
        confidence: float = 1.0,
        raw_text: Optional[str] = None,
    ):
        self.source_type = source_type
        self.source_id = source_id
        self.confidence = confidence
        self.raw_text = raw_text
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "confidence": self.confidence,
            "raw_text_length": len(self.raw_text) if self.raw_text else None,
        }


class FieldSource:
    """Tracks which source provided a field value."""
    
    def __init__(
        self,
        source_type: str,
        source_id: Optional[str] = None,
        confidence: float = 1.0,
    ):
        self.source_type = source_type
        self.source_id = source_id
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "confidence": self.confidence,
        }


class ConflictInfo:
    """Information about a conflict between sources."""
    
    def __init__(
        self,
        field_path: str,
        values: List[Tuple[Any, FieldSource]],
        resolution: Optional[str] = None,
        resolved_value: Optional[Any] = None,
    ):
        self.field_path = field_path
        self.values = values  # List of (value, source) tuples
        self.resolution = resolution  # "deterministic", "llm", "user_review"
        self.resolved_value = resolved_value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field_path": self.field_path,
            "values": [
                {
                    "value": str(val),
                    "source": src.to_dict(),
                }
                for val, src in self.values
            ],
            "resolution": self.resolution,
            "resolved_value": str(self.resolved_value) if self.resolved_value else None,
        }


class FusionResult:
    """Result of multimodal fusion."""
    
    def __init__(
        self,
        agreement: CreditAgreement,
        source_tracking: Dict[str, FieldSource],
        conflicts: List[ConflictInfo],
        fusion_method: str,  # "deterministic", "llm", "hybrid"
    ):
        self.agreement = agreement
        self.source_tracking = source_tracking
        self.conflicts = conflicts
        self.fusion_method = fusion_method
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agreement": self.agreement.model_dump(),
            "source_tracking": {
                field: src.to_dict()
                for field, src in self.source_tracking.items()
            },
            "conflicts": [c.to_dict() for c in self.conflicts],
            "fusion_method": self.fusion_method,
        }


def create_fusion_chain() -> BaseChatModel:
    """Create a chain for LLM-based fusion of multiple CDM sources.
    
    Uses the LLM client abstraction to support multiple providers.
    
    Returns:
        A BaseChatModel instance configured with structured output
        bound to the ExtractionResult model.
    """
    llm = get_chat_model(temperature=0)
    structured_llm = llm.with_structured_output(ExtractionResult)
    return structured_llm


def create_multimodal_fusion_chain() -> Any:
    """Create a complete multimodal fusion chain (prompt + LLM).
    
    Convenience function that combines the fusion prompt and LLM chain.
    
    Returns:
        A LangChain chain ready for invocation with {"cdm_extractions": "..."}
    """
    return create_fusion_prompt() | create_fusion_chain()


def create_fusion_prompt() -> ChatPromptTemplate:
    """Create prompt for LLM-based fusion of multiple CDM sources.
    
    Returns:
        A ChatPromptTemplate for merging multiple CDM extractions.
    """
    system_prompt = """You are an expert Credit Analyst tasked with MERGING multiple CDM extractions from different sources into a single, complete CreditAgreement.

You will receive multiple CreditAgreement objects extracted from different sources:
- Audio transcription (optional, may have transcription errors)
- Image OCR (optional, may have OCR errors)
- Document retrieval (optional, from similar documents)
- Text extraction (required, from direct text input)

Your task:
1. Merge all parties, removing duplicates (match by name, LEI, or role)
2. Combine all facilities into a single list (merge duplicates by facility_name)
3. Select the most authoritative agreement_date (prefer text > document > image > audio)
4. Select the most authoritative governing_law (prefer text > document > image > audio)
5. Merge ESG KPI targets (combine unique KPIs, prefer most complete data)
6. Resolve conflicts intelligently:
   - For dates: prefer most recent or most authoritative source
   - For amounts: prefer highest confidence source or most complete
   - For parties: merge attributes, prefer most complete version
   - For facilities: merge attributes, prefer most complete version

CRITICAL RULES:
- If the same party appears multiple times, keep only one instance (prefer the most complete)
- If the same facility appears multiple times, merge them (prefer the most complete version)
- If dates conflict, prefer the one from text or document sources
- All required fields must be present in the final CreditAgreement
- Ensure all validations pass (dates not in future, at least one party, at least one facility)
- Handle missing fields gracefully (use None if not available from any source)
- Prefer data from text/document sources over audio/image sources for accuracy
"""

    user_prompt = """Multiple CDM Extractions from Different Sources:

{cdm_extractions}

Source Priority (highest to lowest):
1. Text extraction (most reliable)
2. Document retrieval (from similar documents)
3. Image OCR (may have OCR errors)
4. Audio transcription (may have transcription errors)

Merge these extractions into a single, complete CreditAgreement.
Ensure all required fields are present and valid.
Resolve conflicts by preferring higher-priority sources."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    return prompt


def _deterministic_merge_parties(
    parties_lists: List[Tuple[List[Dict[str, Any]], FieldSource]]
) -> Tuple[List[Dict[str, Any]], Dict[str, FieldSource]]:
    """Deterministically merge parties from multiple sources.
    
    Args:
        parties_lists: List of (parties_list, source) tuples
        
    Returns:
        Tuple of (merged_parties, source_tracking)
    """
    merged_parties = []
    source_tracking = {}
    seen_parties = {}  # name -> index in merged_parties
    
    for parties, source in parties_lists:
        if not parties:
            continue
            
        for party in parties:
            if not isinstance(party, dict):
                continue
                
            name = party.get("name", "").strip().lower()
            if not name:
                continue
            
            # Check if we've seen this party
            if name in seen_parties:
                idx = seen_parties[name]
                existing = merged_parties[idx]
                
                # Merge attributes, prefer most complete
                for key, value in party.items():
                    if key not in existing or not existing[key]:
                        existing[key] = value
                    elif value and not existing[key]:
                        existing[key] = value
                    # If both have values, prefer existing (first seen wins)
                
                # Track that this field was merged
                field_key = f"parties.{idx}.{name}"
                if field_key not in source_tracking:
                    source_tracking[field_key] = source
            else:
                # New party
                idx = len(merged_parties)
                merged_parties.append(party.copy())
                seen_parties[name] = idx
                source_tracking[f"parties.{idx}.{name}"] = source
    
    return merged_parties, source_tracking


def _deterministic_merge_facilities(
    facilities_lists: List[Tuple[List[Dict[str, Any]], FieldSource]]
) -> Tuple[List[Dict[str, Any]], Dict[str, FieldSource]]:
    """Deterministically merge facilities from multiple sources.
    
    Args:
        facilities_lists: List of (facilities_list, source) tuples
        
    Returns:
        Tuple of (merged_facilities, source_tracking)
    """
    merged_facilities = []
    source_tracking = {}
    seen_facilities = {}  # facility_name -> index in merged_facilities
    
    for facilities, source in facilities_lists:
        if not facilities:
            continue
            
        for facility in facilities:
            if not isinstance(facility, dict):
                continue
                
            facility_name = facility.get("facility_name", "").strip().lower()
            if not facility_name:
                continue
            
            # Check if we've seen this facility
            if facility_name in seen_facilities:
                idx = seen_facilities[facility_name]
                existing = merged_facilities[idx]
                
                # Merge attributes, prefer most complete
                for key, value in facility.items():
                    if key not in existing or not existing[key]:
                        existing[key] = value
                    elif value and not existing[key]:
                        existing[key] = value
                
                field_key = f"facilities.{idx}.{facility_name}"
                if field_key not in source_tracking:
                    source_tracking[field_key] = source
            else:
                # New facility
                idx = len(merged_facilities)
                merged_facilities.append(facility.copy())
                seen_facilities[facility_name] = idx
                source_tracking[f"facilities.{idx}.{facility_name}"] = source
    
    return merged_facilities, source_tracking


def _detect_conflicts(
    field_values: List[Tuple[Any, FieldSource]],
    field_name: str,
) -> Optional[ConflictInfo]:
    """Detect conflicts in field values from different sources.
    
    Args:
        field_values: List of (value, source) tuples
        field_name: Name of the field
        
    Returns:
        ConflictInfo if conflict detected, None otherwise
    """
    if len(field_values) <= 1:
        return None
    
    # Filter out None values
    non_none_values = [(v, s) for v, s in field_values if v is not None]
    if len(non_none_values) <= 1:
        return None
    
    # Check if all values are the same
    first_value = non_none_values[0][0]
    all_same = all(
        _values_equal(v, first_value)
        for v, _ in non_none_values[1:]
    )
    
    if all_same:
        return None
    
    # Conflict detected
    return ConflictInfo(
        field_path=field_name,
        values=non_none_values,
    )


def _values_equal(val1: Any, val2: Any) -> bool:
    """Check if two values are equal (handles dates, decimals, etc.)."""
    if val1 == val2:
        return True
    
    # Handle date objects
    if isinstance(val1, date) and isinstance(val2, date):
        return val1 == val2
    
    # Handle Decimal
    if isinstance(val1, Decimal) and isinstance(val2, Decimal):
        return val1 == val2
    
    # Handle dicts (for Money, etc.)
    if isinstance(val1, dict) and isinstance(val2, dict):
        return val1 == val2
    
    return False


def _deterministic_resolve_conflict(
    conflict: ConflictInfo,
    source_priority: List[str] = ["text", "document", "image", "audio"],
) -> Tuple[Any, str]:
    """Deterministically resolve a conflict using source priority.
    
    Args:
        conflict: ConflictInfo object
        source_priority: Priority order of sources (highest to lowest)
        
    Returns:
        Tuple of (resolved_value, resolution_method)
    """
    # Sort values by source priority
    def get_priority(value_source: Tuple[Any, FieldSource]) -> int:
        _, source = value_source
        try:
            return source_priority.index(source.source_type)
        except ValueError:
            return len(source_priority)  # Unknown sources have lowest priority
    
    sorted_values = sorted(conflict.values, key=get_priority)
    
    # For dates, prefer most recent
    if "date" in conflict.field_path.lower():
        dates = [(v, s) for v, s in sorted_values if isinstance(v, date)]
        if dates:
            # Return most recent date
            resolved = max(dates, key=lambda x: x[0])[0]
            return resolved, "deterministic_most_recent"
    
    # For amounts, prefer highest confidence or first in priority
    if "amount" in conflict.field_path.lower() or "money" in conflict.field_path.lower():
        # Prefer highest confidence
        resolved = max(sorted_values, key=lambda x: x[1].confidence)[0]
        return resolved, "deterministic_highest_confidence"
    
    # Default: use highest priority source
    resolved = sorted_values[0][0]
    return resolved, "deterministic_source_priority"


def fuse_multimodal_inputs(
    audio_cdm: Optional[Dict[str, Any]] = None,
    image_cdm: Optional[Dict[str, Any]] = None,
    document_cdm: Optional[Dict[str, Any]] = None,
    text_cdm: Optional[Dict[str, Any]] = None,
    audio_text: Optional[str] = None,
    image_text: Optional[str] = None,
    document_text: Optional[str] = None,
    text_input: Optional[str] = None,
    use_llm_fusion: bool = True,
) -> FusionResult:
    """Fuse CDM data from multiple sources with source tracking and conflict detection.
    
    This function:
    1. Prepends optional inputs (audio, image) to required inputs (document, text)
    2. Tracks source for each field
    3. Detects conflicts between sources
    4. Uses deterministic fallbacks for simple cases
    5. Uses LLM for complex merging when conflicts exist
    
    Args:
        audio_cdm: Optional CDM data from audio transcription
        image_cdm: Optional CDM data from image OCR
        document_cdm: Optional CDM data from document retrieval
        text_cdm: Optional CDM data from text extraction
        audio_text: Optional raw transcription text
        image_text: Optional raw OCR text
        document_text: Optional raw document text
        text_input: Required text input (if no text_cdm provided)
        use_llm_fusion: Whether to use LLM for complex merging (default: True)
        
    Returns:
        FusionResult with merged CDM data, source tracking, and conflicts
        
    Raises:
        ValueError: If fusion fails or no valid sources provided
    """
    logger.info("Starting multimodal fusion...")
    
    # Collect all sources with metadata
    sources = []
    source_metadata = []
    
    # Priority order: text > document > image > audio
    if text_cdm:
        sources.append((text_cdm, FieldSource("text", confidence=1.0)))
        source_metadata.append(SourceMetadata("text", raw_text=text_input))
    
    if document_cdm:
        sources.append((document_cdm, FieldSource("document", confidence=0.9)))
        source_metadata.append(SourceMetadata("document", raw_text=document_text))
    
    if image_cdm:
        sources.append((image_cdm, FieldSource("image", confidence=0.8)))
        source_metadata.append(SourceMetadata("image", raw_text=image_text))
    
    if audio_cdm:
        sources.append((audio_cdm, FieldSource("audio", confidence=0.7)))
        source_metadata.append(SourceMetadata("audio", raw_text=audio_text))
    
    if not sources:
        # No CDM data provided, try to extract from combined text
        combined_text_parts = []
        if audio_text:
            combined_text_parts.append(f"[Audio Transcription]\n{audio_text}")
        if image_text:
            combined_text_parts.append(f"[Image OCR]\n{image_text}")
        if document_text:
            combined_text_parts.append(f"[Document]\n{document_text}")
        if text_input:
            combined_text_parts.append(f"[Text Input]\n{text_input}")
        
        if not combined_text_parts:
            raise ValueError("No CDM data or text input provided for fusion")
        
        # Combine all text inputs (prepend optional to required)
        combined_text = "\n\n---\n\n".join(combined_text_parts)
        logger.info(f"Extracting CDM from combined text ({len(combined_text)} chars)...")
        
        result = extract_data_smart(text=combined_text, force_map_reduce=False)
        if not result or not result.agreement:
            raise ValueError("Failed to extract CDM data from combined text")
        
        return FusionResult(
            agreement=result.agreement,
            source_tracking={},
            conflicts=[],
            fusion_method="text_extraction",
        )
    
    # If we have text input but no text_cdm, extract from text
    if text_input and not text_cdm:
        logger.info("Extracting CDM from text input...")
        result = extract_data_smart(text=text_input, force_map_reduce=False)
        if result and result.agreement:
            sources.insert(0, (result.agreement.model_dump(), FieldSource("text", confidence=1.0)))
            source_metadata.insert(0, SourceMetadata("text", raw_text=text_input))
    
    # Prepend optional inputs (audio, image) to text if we have raw text
    if (audio_text or image_text) and text_input:
        # Combine: audio + image + text
        combined_parts = []
        if audio_text:
            combined_parts.append(f"[Audio Transcription]\n{audio_text}")
        if image_text:
            combined_parts.append(f"[Image OCR]\n{image_text}")
        combined_parts.append(f"[Text Input]\n{text_input}")
        
        combined_text = "\n\n---\n\n".join(combined_parts)
        logger.info(f"Extracting CDM from combined text with prepended optional inputs ({len(combined_text)} chars)...")
        
        result = extract_data_smart(text=combined_text, force_map_reduce=False)
        if result and result.agreement:
            # Use this as the primary source
            sources.insert(0, (result.agreement.model_dump(), FieldSource("text", confidence=1.0)))
            source_metadata.insert(0, SourceMetadata("text", raw_text=combined_text))
    
    if len(sources) == 1:
        # Single source, no fusion needed
        logger.info("Single source, no fusion needed")
        agreement_dict, source = sources[0]
        try:
            agreement = CreditAgreement(**agreement_dict)
            return FusionResult(
                agreement=agreement,
                source_tracking={},
                conflicts=[],
                fusion_method="single_source",
            )
        except ValidationError as e:
            raise ValueError(f"Invalid CDM data from single source: {e}") from e
    
    # Multiple sources - detect conflicts and merge
    logger.info(f"Merging {len(sources)} CDM sources...")
    
    # Try deterministic merging first
    conflicts = []
    source_tracking = {}
    merged_data = {}
    
    # Extract field values from all sources
    field_values_map = {}  # field_name -> [(value, source), ...]
    
    for agreement_dict, source in sources:
        if not isinstance(agreement_dict, dict):
            continue
        
        # Track all fields
        for key, value in agreement_dict.items():
            if key not in field_values_map:
                field_values_map[key] = []
            field_values_map[key].append((value, source))
    
    # Merge simple fields (deterministic)
    simple_fields = ["agreement_date", "governing_law", "deal_id", "loan_identification_number", "sustainability_linked"]
    for field in simple_fields:
        if field not in field_values_map:
            continue
        
        values = field_values_map[field]
        conflict = _detect_conflicts(values, field)
        
        if conflict:
            conflicts.append(conflict)
            resolved_value, resolution_method = _deterministic_resolve_conflict(conflict)
            merged_data[field] = resolved_value
            conflict.resolution = resolution_method
            conflict.resolved_value = resolved_value
            source_tracking[field] = conflict.values[0][1]  # Track first source
        else:
            # No conflict, use first non-None value
            non_none = [v for v, _ in values if v is not None]
            if non_none:
                merged_data[field] = non_none[0]
                source_tracking[field] = values[0][1]
    
    # Merge parties (deterministic)
    parties_lists = [
        (agreement_dict.get("parties", []), source)
        for agreement_dict, source in sources
        if isinstance(agreement_dict, dict) and agreement_dict.get("parties")
    ]
    if parties_lists:
        merged_parties, parties_tracking = _deterministic_merge_parties(parties_lists)
        merged_data["parties"] = merged_parties
        source_tracking.update(parties_tracking)
    
    # Merge facilities (deterministic)
    facilities_lists = [
        (agreement_dict.get("facilities", []), source)
        for agreement_dict, source in sources
        if isinstance(agreement_dict, dict) and agreement_dict.get("facilities")
    ]
    if facilities_lists:
        merged_facilities, facilities_tracking = _deterministic_merge_facilities(facilities_lists)
        merged_data["facilities"] = merged_facilities
        source_tracking.update(facilities_tracking)
    
    # Merge ESG KPIs (deterministic)
    esg_lists = [
        (agreement_dict.get("esg_kpi_targets", []), source)
        for agreement_dict, source in sources
        if isinstance(agreement_dict, dict) and agreement_dict.get("esg_kpi_targets")
    ]
    if esg_lists:
        # Combine unique KPIs
        seen_kpis = {}
        merged_esg = []
        for esg_list, source in esg_lists:
            for kpi in esg_list:
                if not isinstance(kpi, dict):
                    continue
                kpi_type = kpi.get("kpi_type")
                if kpi_type and kpi_type not in seen_kpis:
                    seen_kpis[kpi_type] = len(merged_esg)
                    merged_esg.append(kpi.copy())
                    source_tracking[f"esg_kpi_targets.{len(merged_esg)-1}"] = source
        merged_data["esg_kpi_targets"] = merged_esg if merged_esg else None
    
    # Set extraction_status
    merged_data["extraction_status"] = ExtractionStatus.SUCCESS.value
    
    # Try to create CreditAgreement from merged data
    try:
        agreement = CreditAgreement(**merged_data)
        fusion_method = "deterministic"
        
        # If we have conflicts and LLM fusion is enabled, try LLM refinement
        if conflicts and use_llm_fusion:
            logger.info(f"Using LLM to refine fusion with {len(conflicts)} conflicts...")
            try:
                # Format CDM extractions for LLM
                cdm_extractions = "\n\n---\n\n".join([
                    f"Source: {src.source_type}\n{json.dumps(agr, default=str, indent=2)}"
                    for agr, src in sources
                ])
                
                fusion_chain = create_fusion_prompt() | create_fusion_chain()
                result = fusion_chain.invoke({"cdm_extractions": cdm_extractions})
                
                if result and result.agreement:
                    agreement = result.agreement
                    fusion_method = "llm"
                    logger.info("LLM fusion successful")
            except Exception as e:
                logger.warning(f"LLM fusion failed, using deterministic result: {e}")
                # Fall back to deterministic result
        
        return FusionResult(
            agreement=agreement,
            source_tracking=source_tracking,
            conflicts=conflicts,
            fusion_method=fusion_method,
        )
        
    except ValidationError as e:
        logger.error(f"Validation error during fusion: {e}")
        # Try LLM fusion as fallback
        if use_llm_fusion:
            try:
                logger.info("Trying LLM fusion due to validation error...")
                cdm_extractions = "\n\n---\n\n".join([
                    f"Source: {src.source_type}\n{json.dumps(agr, default=str, indent=2)}"
                    for agr, src in sources
                ])
                
                fusion_chain = create_fusion_prompt() | create_fusion_chain()
                result = fusion_chain.invoke({"cdm_extractions": cdm_extractions})
                
                if result and result.agreement:
                    return FusionResult(
                        agreement=result.agreement,
                        source_tracking={},
                        conflicts=conflicts,
                        fusion_method="llm_fallback",
                    )
            except Exception as llm_error:
                logger.error(f"LLM fusion also failed: {llm_error}")
        
        raise ValueError(f"Fusion failed validation: {e}") from e


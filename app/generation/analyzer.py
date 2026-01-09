"""
Pre-generation analysis for document generation.

Analyzes CDM data completeness, clause cache predictions, and template compatibility
before document generation to provide users with statistics and recommendations.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from decimal import Decimal

from app.models.cdm import CreditAgreement
from app.db.models import LMATemplate, ClauseCache
from app.generation.field_parser import FieldPathParser
from app.generation.mapper import FieldMapper
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class PreGenerationAnalyzer:
    """
    Analyzes CDM data and template requirements before document generation.
    
    Provides:
    - Field completeness analysis
    - Clause cache predictions
    - Template compatibility assessment
    """
    
    def __init__(self, db: Session):
        """Initialize analyzer with database session."""
        self.db = db
        self.parser = FieldPathParser()
        logger.debug("PreGenerationAnalyzer initialized")
    
    def analyze(
        self,
        template: LMATemplate,
        cdm_data: CreditAgreement,
        field_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive pre-generation analysis.
        
        Args:
            template: LMATemplate instance
            cdm_data: CreditAgreement instance
            field_overrides: Optional field overrides to apply
            
        Returns:
            Dictionary with analysis results:
            - field_completeness: Field completeness analysis
            - clause_cache_predictions: Predictions for clause cache hits
            - template_compatibility: Template compatibility assessment
            - recommendations: List of recommendations
        """
        # Apply field overrides if provided
        if field_overrides:
            from app.models.cdm import CreditAgreement
            # Create a copy and apply overrides
            cdm_data_dict = cdm_data.model_dump(mode='json')
            for field_path, value in field_overrides.items():
                try:
                    FieldPathParser.set_nested_value(cdm_data_dict, field_path, value)
                except Exception as e:
                    logger.warning(f"Failed to apply override for field '{field_path}': {e}")
            # Reconstruct CreditAgreement from dict (simplified - in production, use proper reconstruction)
            # For now, we'll work with the dict for analysis
        
        # Analyze field completeness
        field_completeness = self._analyze_field_completeness(template, cdm_data)
        
        # Predict clause cache hits
        clause_cache_predictions = self._predict_clause_cache_hits(template, cdm_data)
        
        # Assess template compatibility
        template_compatibility = self._assess_template_compatibility(template, cdm_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            field_completeness,
            clause_cache_predictions,
            template_compatibility
        )
        
        return {
            "field_completeness": field_completeness,
            "clause_cache_predictions": clause_cache_predictions,
            "template_compatibility": template_compatibility,
            "recommendations": recommendations
        }
    
    def _analyze_field_completeness(
        self,
        template: LMATemplate,
        cdm_data: CreditAgreement
    ) -> Dict[str, Any]:
        """
        Analyze field completeness for the template.
        
        Returns:
            Dictionary with:
            - required_fields: List of required field paths
            - present_fields: List of present required fields
            - missing_fields: List of missing required fields
            - optional_fields: List of optional fields
            - present_optional_fields: List of present optional fields
            - completeness_score: Percentage (0-100)
        """
        # Get required and optional fields from template
        required_fields = template.required_fields or []
        optional_fields = template.optional_fields or []
        
        # Normalize field lists (handle both list and dict formats)
        if isinstance(required_fields, dict):
            required_fields = required_fields.get("fields", [])
        if isinstance(optional_fields, dict):
            optional_fields = optional_fields.get("fields", [])
        
        # Check which fields are present
        present_required = []
        missing_required = []
        
        for field_path in required_fields:
            value = self.parser.get_nested_value(cdm_data, field_path)
            if value is not None:
                present_required.append(field_path)
            else:
                missing_required.append(field_path)
        
        # Check optional fields
        present_optional = []
        for field_path in optional_fields:
            value = self.parser.get_nested_value(cdm_data, field_path)
            if value is not None:
                present_optional.append(field_path)
        
        # Calculate completeness score
        total_required = len(required_fields)
        if total_required > 0:
            completeness_score = (len(present_required) / total_required) * 100
        else:
            completeness_score = 100.0  # No required fields = 100% complete
        
        return {
            "required_fields": required_fields,
            "present_fields": present_required,
            "missing_fields": missing_required,
            "optional_fields": optional_fields,
            "present_optional_fields": present_optional,
            "completeness_score": round(completeness_score, 1),
            "total_required": total_required,
            "total_present": len(present_required),
            "total_missing": len(missing_required)
        }
    
    def _predict_clause_cache_hits(
        self,
        template: LMATemplate,
        cdm_data: CreditAgreement
    ) -> Dict[str, Any]:
        """
        Predict which AI-generated sections will use cached clauses.
        
        Returns:
            Dictionary with:
            - ai_sections: List of AI-generated section names
            - cached_sections: List of sections predicted to use cache
            - generated_sections: List of sections predicted to generate new
            - cache_hit_rate: Percentage (0-100)
        """
        ai_sections = template.ai_generated_sections or []
        if isinstance(ai_sections, dict):
            ai_sections = ai_sections.get("sections", [])
        
        cached_sections = []
        generated_sections = []
        
        # Check clause cache for each AI section
        for section_name in ai_sections:
            # Generate cache key based on section, template, and CDM data
            cache_key = self._generate_cache_key(template, cdm_data, section_name)
            
            # Check if cached clause exists
            # Note: ClauseCache uses 'field_name' instead of 'section_name', and 'context_hash' instead of 'cache_key'
            cached_clause = self.db.query(ClauseCache).filter(
                ClauseCache.template_id == template.id,
                ClauseCache.field_name == section_name,
                ClauseCache.context_hash == cache_key
            ).first()
            
            if cached_clause:
                cached_sections.append(section_name)
            else:
                generated_sections.append(section_name)
        
        # Calculate cache hit rate
        total_sections = len(ai_sections)
        if total_sections > 0:
            cache_hit_rate = (len(cached_sections) / total_sections) * 100
        else:
            cache_hit_rate = 0.0
        
        return {
            "ai_sections": ai_sections,
            "cached_sections": cached_sections,
            "generated_sections": generated_sections,
            "cache_hit_rate": round(cache_hit_rate, 1),
            "total_sections": total_sections,
            "cached_count": len(cached_sections),
            "generated_count": len(generated_sections)
        }
    
    def _generate_cache_key(
        self,
        template: LMATemplate,
        cdm_data: CreditAgreement,
        section_name: str
    ) -> str:
        """
        Generate cache key for a clause based on template, CDM data, and section.
        
        Args:
            template: LMATemplate instance
            cdm_data: CreditAgreement instance
            section_name: Name of AI-generated section
            
        Returns:
            Cache key string
        """
        import hashlib
        import json
        
        # Extract key CDM fields that affect clause generation
        key_fields = {
            "template_id": template.id,
            "template_code": template.template_code,
            "section": section_name,
            "governing_law": getattr(cdm_data, "governing_law", None),
            "borrower_name": None,
            "facility_name": None,
        }
        
        # Extract borrower name
        borrower = self.parser.get_nested_value(cdm_data, "parties[role='Borrower']")
        if borrower:
            key_fields["borrower_name"] = getattr(borrower, "name", None)
        
        # Extract facility name
        facility = self.parser.get_nested_value(cdm_data, "facilities[0]")
        if facility:
            key_fields["facility_name"] = getattr(facility, "facility_name", None)
        
        # Create hash of key fields
        key_str = json.dumps(key_fields, sort_keys=True, default=str)
        cache_key = hashlib.md5(key_str.encode()).hexdigest()
        
        return cache_key
    
    def _assess_template_compatibility(
        self,
        template: LMATemplate,
        cdm_data: CreditAgreement
    ) -> Dict[str, Any]:
        """
        Assess compatibility between CDM data and template requirements.
        
        Returns:
            Dictionary with:
            - is_compatible: Boolean
            - compatibility_score: Percentage (0-100)
            - issues: List of compatibility issues
            - warnings: List of warnings
        """
        issues = []
        warnings = []
        
        # Check governing law compatibility
        template_law = template.governing_law
        cdm_law = getattr(cdm_data, "governing_law", None)
        
        if template_law and cdm_law:
            if template_law.lower() != cdm_law.lower():
                warnings.append(
                    f"Governing law mismatch: Template expects '{template_law}', "
                    f"CDM data has '{cdm_law}'"
                )
        
        # Check category compatibility
        # Some templates may require specific CDM fields based on category
        if template.category == "Sustainable Finance":
            sustainability_linked = getattr(cdm_data, "sustainability_linked", False)
            if not sustainability_linked:
                warnings.append(
                    "Template is for sustainable finance, but CDM data does not "
                    "indicate sustainability-linked loan"
                )
        
        # Check for required parties
        parties = getattr(cdm_data, "parties", [])
        if not parties:
            issues.append("No parties found in CDM data")
        
        # Check for required facilities
        facilities = getattr(cdm_data, "facilities", [])
        if not facilities:
            issues.append("No facilities found in CDM data")
        
        # Calculate compatibility score
        if issues:
            compatibility_score = 50.0  # Has issues
        elif warnings:
            compatibility_score = 75.0  # Has warnings but no issues
        else:
            compatibility_score = 100.0  # Fully compatible
        
        return {
            "is_compatible": len(issues) == 0,
            "compatibility_score": round(compatibility_score, 1),
            "issues": issues,
            "warnings": warnings
        }
    
    def _generate_recommendations(
        self,
        field_completeness: Dict[str, Any],
        clause_cache_predictions: Dict[str, Any],
        template_compatibility: Dict[str, Any]
    ) -> List[str]:
        """
        Generate recommendations based on analysis results.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Field completeness recommendations
        missing_count = field_completeness.get("total_missing", 0)
        if missing_count > 0:
            recommendations.append(
                f"Fill {missing_count} missing required field(s) before generation. "
                f"Use the field editor to add missing data."
            )
        
        completeness_score = field_completeness.get("completeness_score", 100.0)
        if completeness_score < 50.0:
            recommendations.append(
                "Field completeness is low. Consider adding more CDM data or "
                "using multimodal input to extract additional information."
            )
        
        # Clause cache recommendations
        cache_hit_rate = clause_cache_predictions.get("cache_hit_rate", 0.0)
        if cache_hit_rate < 50.0:
            recommendations.append(
                "Most clauses will be newly generated. This may take longer and "
                "incur higher LLM costs."
            )
        elif cache_hit_rate > 80.0:
            recommendations.append(
                "High clause cache hit rate. Generation will be faster and more cost-effective."
            )
        
        # Compatibility recommendations
        if not template_compatibility.get("is_compatible", True):
            recommendations.append(
                "Template compatibility issues detected. Review warnings before proceeding."
            )
        
        if not recommendations:
            recommendations.append(
                "CDM data looks good! Ready for document generation."
            )
        
        return recommendations


def analyze_pre_generation(
    db: Session,
    template_id: int,
    cdm_data: CreditAgreement,
    field_overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to perform pre-generation analysis.
    
    Args:
        db: Database session
        template_id: Template ID
        cdm_data: CreditAgreement instance
        field_overrides: Optional field overrides
        
    Returns:
        Analysis results dictionary
    """
    from app.templates.registry import TemplateRegistry
    
    # Get template
    template = TemplateRegistry.get_template(db, template_id)
    if not template:
        raise ValueError(f"Template with ID {template_id} not found")
    
    # Perform analysis
    analyzer = PreGenerationAnalyzer(db)
    return analyzer.analyze(template, cdm_data, field_overrides)

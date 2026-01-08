"""
Template registry for LMA template discovery and metadata management.

Provides database-backed template registry for querying and managing templates.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from app.db.models import LMATemplate, TemplateFieldMapping

logger = logging.getLogger(__name__)


class TemplateRegistry:
    """
    Manages LMA template registry in database.
    
    Provides methods for:
    - Template lookup and retrieval
    - Template registration
    - Field mapping management
    """
    
    @staticmethod
    def get_template(db: Session, template_id: int) -> LMATemplate:
        """
        Get template by ID.
        
        Args:
            db: Database session
            template_id: Template ID
            
        Returns:
            LMATemplate instance
            
        Raises:
            NoResultFound: If template not found
        """
        template = db.query(LMATemplate).filter(LMATemplate.id == template_id).first()
        if not template:
            raise NoResultFound(f"Template with ID {template_id} not found")
        return template
    
    @staticmethod
    def list_templates(db: Session, category: Optional[str] = None, subcategory: Optional[str] = None) -> List[LMATemplate]:
        """
        List templates with optional filters.
        
        Args:
            db: Database session
            category: Optional category filter
            subcategory: Optional subcategory filter
            
        Returns:
            List of LMATemplate instances
        """
        query = db.query(LMATemplate)
        
        if category:
            query = query.filter(LMATemplate.category == category)
        
        if subcategory:
            query = query.filter(LMATemplate.subcategory == subcategory)
        
        templates = query.order_by(LMATemplate.category, LMATemplate.name).all()
        logger.debug(f"Found {len(templates)} template(s) with category={category}, subcategory={subcategory}")
        return templates
    
    @staticmethod
    def get_template_by_code(db: Session, code: str) -> Optional[LMATemplate]:
        """
        Get template by template code.
        
        Args:
            db: Database session
            code: Template code (e.g., "LMA-CL-FA-2024-EN")
            
        Returns:
            LMATemplate instance or None if not found
        """
        template = db.query(LMATemplate).filter(LMATemplate.template_code == code).first()
        return template
    
    @staticmethod
    def register_template(db: Session, template_data: Dict[str, Any]) -> LMATemplate:
        """
        Register a new template in the database.
        
        Args:
            db: Database session
            template_data: Dictionary containing template metadata:
                - template_code: str (required)
                - name: str (required)
                - category: str (required)
                - subcategory: str (optional)
                - governing_law: str (optional)
                - version: str (required)
                - file_path: str (required)
                - metadata: dict (optional)
                - required_fields: list (optional)
                - optional_fields: list (optional)
                - ai_generated_sections: list (optional)
                
        Returns:
            Created LMATemplate instance
            
        Raises:
            ValueError: If required fields are missing or template_code already exists
        """
        # Check if template already exists
        existing = TemplateRegistry.get_template_by_code(db, template_data.get("template_code"))
        if existing:
            raise ValueError(f"Template with code {template_data['template_code']} already exists")
        
        # Validate required fields
        required = ["template_code", "name", "category", "version", "file_path"]
        missing = [field for field in required if field not in template_data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        
        # Create template instance
        template = LMATemplate(
            template_code=template_data["template_code"],
            name=template_data["name"],
            category=template_data["category"],
            subcategory=template_data.get("subcategory"),
            governing_law=template_data.get("governing_law"),
            version=template_data["version"],
            file_path=template_data["file_path"],
            additional_metadata=template_data.get("metadata"),  # Use additional_metadata to match model
            required_fields=template_data.get("required_fields"),
            optional_fields=template_data.get("optional_fields"),
            ai_generated_sections=template_data.get("ai_generated_sections"),
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        logger.info(f"Registered template: {template.template_code} (ID: {template.id})")
        return template
    
    @staticmethod
    def get_required_fields(template: LMATemplate) -> List[str]:
        """
        Get list of required CDM field paths for a template.
        
        Args:
            template: LMATemplate instance
            
        Returns:
            List of CDM field paths (e.g., ["parties[role='Borrower'].name", "facilities[0].commitment_amount.amount"])
        """
        if not template.required_fields:
            return []
        
        # required_fields is stored as JSONB, should be a list
        if isinstance(template.required_fields, list):
            return template.required_fields
        
        # If it's a dict, extract the list
        if isinstance(template.required_fields, dict):
            return template.required_fields.get("fields", [])
        
        return []
    
    @staticmethod
    def get_field_mappings(db: Session, template_id: int) -> List[TemplateFieldMapping]:
        """
        Get all field mappings for a template.
        
        Args:
            db: Database session
            template_id: Template ID
            
        Returns:
            List of TemplateFieldMapping instances
        """
        mappings = db.query(TemplateFieldMapping).filter(
            TemplateFieldMapping.template_id == template_id
        ).order_by(TemplateFieldMapping.template_field).all()
        return mappings
    
    @staticmethod
    def create_field_mapping(
        db: Session,
        template_id: int,
        template_field: str,
        cdm_field: str,
        mapping_type: str = "direct",
        transformation_rule: Optional[str] = None,
        is_required: bool = False
    ) -> TemplateFieldMapping:
        """
        Create a field mapping for a template.
        
        Args:
            db: Database session
            template_id: Template ID
            template_field: Template field name (e.g., "[BORROWER_NAME]")
            cdm_field: CDM field path (e.g., "parties[role='Borrower'].name")
            mapping_type: Mapping type ("direct", "computed", "ai_generated")
            transformation_rule: Optional transformation rule for computed fields
            is_required: Whether this field is required
            
        Returns:
            Created TemplateFieldMapping instance
        """
        mapping = TemplateFieldMapping(
            template_id=template_id,
            template_field=template_field,
            cdm_field=cdm_field,
            mapping_type=mapping_type,
            transformation_rule=transformation_rule,
            is_required=is_required,
        )
        
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        
        logger.debug(f"Created field mapping: {template_field} -> {cdm_field} (type: {mapping_type})")
        return mapping


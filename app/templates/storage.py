"""
Template storage system for LMA templates.

Provides file system-based storage for LMA template files and generated documents.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Base paths for template storage
TEMPLATE_BASE_PATH = Path("storage/templates")
GENERATED_BASE_PATH = Path("storage/generated")


class TemplateStorage:
    """
    Manages template file storage and retrieval.
    
    Handles:
    - Template file loading
    - Generated document saving
    - Template directory scanning
    """
    
    def __init__(self, template_base_path: Optional[Path] = None, generated_base_path: Optional[Path] = None):
        """
        Initialize template storage.
        
        Args:
            template_base_path: Base path for template files (default: storage/templates)
            generated_base_path: Base path for generated documents (default: storage/generated)
        """
        self.template_base_path = Path(template_base_path) if template_base_path else TEMPLATE_BASE_PATH
        self.generated_base_path = Path(generated_base_path) if generated_base_path else GENERATED_BASE_PATH
        
        # Create directories if they don't exist
        self.template_base_path.mkdir(parents=True, exist_ok=True)
        self.generated_base_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"TemplateStorage initialized: templates={self.template_base_path}, generated={self.generated_base_path}")
    
    def get_template_path(self, template_code: str, version: str) -> str:
        """
        Get absolute path to template file.
        
        Args:
            template_code: Template code (e.g., "LMA-CL-FA-2024-EN")
            version: Template version (e.g., "2024.1")
            
        Returns:
            Absolute path to template file
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Construct path: storage/templates/{category}/{template_code}/{version}.docx
        # For now, use simpler structure: storage/templates/{template_code}-{version}.docx
        filename = f"{template_code}-{version}.docx"
        template_path = self.template_base_path / filename
        
        if not template_path.exists():
            # Try alternative structure: storage/templates/{category}/{filename}
            # Search in subdirectories
            for subdir in self.template_base_path.iterdir():
                if subdir.is_dir():
                    alt_path = subdir / filename
                    if alt_path.exists():
                        return str(alt_path.absolute())
            
            raise FileNotFoundError(f"Template file not found: {template_code} version {version}")
        
        return str(template_path.absolute())
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available templates in storage.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of template metadata dictionaries
        """
        templates = []
        
        # Scan template directory
        if not self.template_base_path.exists():
            logger.warning(f"Template directory does not exist: {self.template_base_path}")
            return templates
        
        # Look for .docx files
        for template_file in self.template_base_path.rglob("*.docx"):
            try:
                # Extract metadata from filename: {template_code}-{version}.docx
                stem = template_file.stem
                if "-" in stem:
                    parts = stem.rsplit("-", 1)
                    template_code = parts[0]
                    version = parts[1] if len(parts) > 1 else "1.0"
                else:
                    template_code = stem
                    version = "1.0"
                
                # Get category from subdirectory if available
                relative_path = template_file.relative_to(self.template_base_path)
                file_category = str(relative_path.parent) if relative_path.parent != Path(".") else None
                
                # Apply category filter if provided
                if category and file_category and category.lower() not in file_category.lower():
                    continue
                
                templates.append({
                    "template_code": template_code,
                    "version": version,
                    "file_path": str(template_file.absolute()),
                    "category": file_category,
                    "filename": template_file.name,
                    "size": template_file.stat().st_size,
                })
            except Exception as e:
                logger.warning(f"Error processing template file {template_file}: {e}")
                continue
        
        logger.info(f"Found {len(templates)} template(s) in storage")
        return templates
    
    def load_template(self, template_code: str, version: str) -> bytes:
        """
        Load template file as binary data.
        
        Args:
            template_code: Template code
            version: Template version
            
        Returns:
            Template file content as bytes
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If file cannot be read
        """
        template_path = Path(self.get_template_path(template_code, version))
        
        try:
            with open(template_path, "rb") as f:
                content = f.read()
            logger.info(f"Loaded template {template_code} version {version} ({len(content)} bytes)")
            return content
        except FileNotFoundError:
            raise
        except Exception as e:
            raise IOError(f"Failed to read template file {template_path}: {e}") from e
    
    def save_generated_document(self, content: bytes, filename: str) -> str:
        """
        Save generated document to storage.
        
        Args:
            content: Document content as bytes
            filename: Filename for the document
            
        Returns:
            Absolute path to saved file
        """
        # Ensure filename has .docx extension if not present
        if not filename.endswith((".docx", ".pdf")):
            filename = f"{filename}.docx"
        
        output_path = self.generated_base_path / filename
        
        # Create parent directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(output_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Saved generated document: {output_path} ({len(content)} bytes)")
        return str(output_path.absolute())
    
    def get_generated_document_path(self, document_id: int) -> str:
        """
        Get path to generated document by ID.
        
        Args:
            document_id: Generated document ID
            
        Returns:
            Absolute path to document file
            
        Raises:
            FileNotFoundError: If document file doesn't exist
        """
        # Construct path: storage/generated/{document_id}.docx
        # Or use pattern: storage/generated/{document_id}/{filename}
        filename = f"generated_{document_id}.docx"
        doc_path = self.generated_base_path / filename
        
        if not doc_path.exists():
            # Try alternative: look in subdirectories
            for subdir in self.generated_base_path.iterdir():
                if subdir.is_dir() and subdir.name == str(document_id):
                    for file in subdir.glob("*.docx"):
                        return str(file.absolute())
                    for file in subdir.glob("*.pdf"):
                        return str(file.absolute())
            
            raise FileNotFoundError(f"Generated document file not found for ID {document_id}")
        
        return str(doc_path.absolute())

















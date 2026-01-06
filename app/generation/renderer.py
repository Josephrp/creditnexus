"""
Word document renderer for LMA template generation.

Handles placeholder replacement in Word documents including paragraphs,
tables, headers, and footers.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional, Any
from io import BytesIO

from docx import Document
from docx.document import Document as DocumentType
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import Table
from docx.text.paragraph import Paragraph

logger = logging.getLogger(__name__)


class DocumentRenderer:
    """
    Renders Word documents by replacing placeholders with field values.
    
    Supports placeholder replacement in:
    - Paragraphs
    - Tables
    - Headers and footers
    """
    
    # Pattern to match placeholders like [BORROWER_NAME] or [COMMITMENT_AMOUNT]
    PLACEHOLDER_PATTERN = re.compile(r'\[([A-Z_][A-Z0-9_]*)\]')
    
    def __init__(self):
        """Initialize document renderer."""
        logger.debug("DocumentRenderer initialized")
    
    def render_template(
        self,
        template_path: str,
        field_values: Dict[str, str]
    ) -> DocumentType:
        """
        Render template by replacing placeholders with field values.
        
        Args:
            template_path: Path to template Word document
            field_values: Dictionary mapping placeholder names to values
                Example: {"[BORROWER_NAME]": "ACME Corp", "[COMMITMENT_AMOUNT]": "$10,000,000.00 USD"}
            
        Returns:
            Rendered Document instance
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If template cannot be read
        """
        template_file = Path(template_path)
        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        try:
            # Load template document
            doc = Document(str(template_file))
            
            # Replace placeholders in all document elements
            self._replace_placeholders(doc, field_values)
            self._replace_in_tables(doc, field_values)
            self._replace_in_headers_footers(doc, field_values)
            
            logger.info(f"Rendered template {template_path} with {len(field_values)} field(s)")
            return doc
            
        except Exception as e:
            raise IOError(f"Failed to render template {template_path}: {e}") from e
    
    def _replace_placeholders(
        self,
        doc: DocumentType,
        field_values: Dict[str, str]
    ) -> None:
        """
        Replace placeholders in document paragraphs.
        
        Args:
            doc: Document instance
            field_values: Dictionary of placeholder to value mappings
        """
        for paragraph in doc.paragraphs:
            self._replace_in_paragraph(paragraph, field_values)
    
    def _replace_in_paragraph(
        self,
        paragraph: Paragraph,
        field_values: Dict[str, str]
    ) -> None:
        """
        Replace placeholders in a single paragraph.
        
        Args:
            paragraph: Paragraph instance
            field_values: Dictionary of placeholder to value mappings
        """
        if not paragraph.text:
            return
        
        # Find all placeholders in the paragraph
        placeholders = self.PLACEHOLDER_PATTERN.findall(paragraph.text)
        if not placeholders:
            return
        
        # Build replacement text
        text = paragraph.text
        for placeholder_name in placeholders:
            placeholder = f"[{placeholder_name}]"
            if placeholder in field_values:
                value = str(field_values[placeholder])
                text = text.replace(placeholder, value)
            else:
                logger.debug(f"Placeholder {placeholder} not found in field_values, leaving as-is")
        
        # Replace paragraph text
        # Clear existing runs and add new text
        paragraph.clear()
        paragraph.add_run(text)
    
    def _replace_in_tables(
        self,
        doc: DocumentType,
        field_values: Dict[str, str]
    ) -> None:
        """
        Replace placeholders in document tables.
        
        Args:
            doc: Document instance
            field_values: Dictionary of placeholder to value mappings
        """
        # Iterate through all tables in the document
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    # Replace in each cell's paragraphs
                    for paragraph in cell.paragraphs:
                        self._replace_in_paragraph(paragraph, field_values)
    
    def _replace_in_headers_footers(
        self,
        doc: DocumentType,
        field_values: Dict[str, str]
    ) -> None:
        """
        Replace placeholders in document headers and footers.
        
        Args:
            doc: Document instance
            field_values: Dictionary of placeholder to value mappings
        """
        # Process each section's headers and footers
        for section in doc.sections:
            # Header
            if section.header:
                for paragraph in section.header.paragraphs:
                    self._replace_in_paragraph(paragraph, field_values)
            
            # Footer
            if section.footer:
                for paragraph in section.footer.paragraphs:
                    self._replace_in_paragraph(paragraph, field_values)
            
            # First page header (if different)
            if section.first_page_header:
                for paragraph in section.first_page_header.paragraphs:
                    self._replace_in_paragraph(paragraph, field_values)
            
            # First page footer (if different)
            if section.first_page_footer:
                for paragraph in section.first_page_footer.paragraphs:
                    self._replace_in_paragraph(paragraph, field_values)
    
    def save_document(
        self,
        doc: DocumentType,
        output_path: str
    ) -> str:
        """
        Save rendered document to file.
        
        Args:
            doc: Document instance
            output_path: Path to save the document
            
        Returns:
            Absolute path to saved file
        """
        output_file = Path(output_path)
        
        # Create parent directory if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save document
        doc.save(str(output_file))
        
        logger.info(f"Saved rendered document: {output_file} ({output_file.stat().st_size} bytes)")
        return str(output_file.absolute())
    
    def export_to_pdf(
        self,
        doc: DocumentType,
        output_path: str
    ) -> str:
        """
        Export document to PDF format.
        
        Note: This requires docx2pdf or similar library. For now, this is a placeholder.
        In production, you would use:
        - docx2pdf (Windows only, requires Microsoft Word)
        - LibreOffice headless (cross-platform)
        - Cloud conversion service
        
        Args:
            doc: Document instance
            output_path: Path to save the PDF
            
        Returns:
            Absolute path to saved PDF file
            
        Raises:
            NotImplementedError: PDF export not yet implemented
        """
        # For now, raise NotImplementedError
        # In production, implement using one of:
        # 1. docx2pdf (Windows only)
        # 2. LibreOffice headless conversion
        # 3. Cloud service (e.g., CloudConvert API)
        
        raise NotImplementedError(
            "PDF export not yet implemented. "
            "Options: 1) Install docx2pdf (Windows only), "
            "2) Use LibreOffice headless, "
            "3) Use cloud conversion service"
        )
        
        # Example implementation with docx2pdf (if available):
        # try:
        #     from docx2pdf import convert
        #     pdf_path = output_path.replace('.docx', '.pdf')
        #     convert(str(doc_path), pdf_path)
        #     return pdf_path
        # except ImportError:
        #     raise NotImplementedError("docx2pdf not installed")
    
    def render_template_to_bytes(
        self,
        template_path: str,
        field_values: Dict[str, str]
    ) -> bytes:
        """
        Render template and return as bytes.
        
        Args:
            template_path: Path to template Word document
            field_values: Dictionary of placeholder to value mappings
            
        Returns:
            Document content as bytes
        """
        doc = self.render_template(template_path, field_values)
        
        # Save to BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()








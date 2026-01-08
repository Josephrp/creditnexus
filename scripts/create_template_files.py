"""
Script to create template Word files for LMA templates.

Creates placeholder Word documents matching the template codes and versions
stored in the database.
"""

import sys
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import SessionLocal, init_db
from app.templates.registry import TemplateRegistry


def create_template_file(template_code: str, version: str, output_path: Path):
    """
    Create a placeholder Word template file.
    
    Args:
        template_code: Template code (e.g., "LMA-CL-FA-2024-EN")
        version: Template version (e.g., "2024.1")
        output_path: Path to save the template file
    """
    doc = Document()
    
    # Title
    title = doc.add_heading('FACILITY AGREEMENT', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Template Info
    doc.add_paragraph(f'Template: {template_code}')
    doc.add_paragraph(f'Version: {version}')
    doc.add_paragraph('')
    
    # Parties Section
    doc.add_heading('PARTIES', 1)
    doc.add_paragraph('Borrower: {{parties[role="Borrower"].name}}')
    doc.add_paragraph('LEI: {{parties[role="Borrower"].lei}}')
    doc.add_paragraph('Lenders: {{parties[role="Lender"].name}}')
    doc.add_paragraph('Administrative Agent: {{parties[role="AdministrativeAgent"].name}}')
    doc.add_paragraph('')
    
    # Facility Details
    doc.add_heading('FACILITY DETAILS', 1)
    doc.add_paragraph(f'Facility Name: {{facilities[0].facility_name}}')
    doc.add_paragraph(f'Total Commitment: {{facilities[0].total_commitment.amount}} {{facilities[0].total_commitment.currency}}')
    doc.add_paragraph(f'Maturity Date: {{facilities[0].maturity_date}}')
    doc.add_paragraph(f'Agreement Date: {{agreement_date}}')
    doc.add_paragraph('')
    
    # Interest Terms
    doc.add_heading('INTEREST TERMS', 1)
    doc.add_paragraph(f'Benchmark: {{facilities[0].interest_rate.benchmark}}')
    doc.add_paragraph(f'Spread: {{facilities[0].interest_rate.spread}} basis points')
    doc.add_paragraph(f'Payment Frequency: {{facilities[0].payment_frequency}}')
    doc.add_paragraph('')
    
    # Governing Law
    doc.add_heading('GOVERNING LAW', 1)
    doc.add_paragraph(f'This Agreement is governed by {{governing_law}} law.')
    doc.add_paragraph('')
    
    # AI-Generated Sections (placeholders)
    doc.add_heading('REPRESENTATIONS AND WARRANTIES', 1)
    doc.add_paragraph('{{representations_and_warranties}}')
    doc.add_paragraph('')
    
    doc.add_heading('CONDITIONS PRECEDENT', 1)
    doc.add_paragraph('{{conditions_precedent}}')
    doc.add_paragraph('')
    
    doc.add_heading('COVENANTS', 1)
    doc.add_paragraph('{{covenants}}')
    doc.add_paragraph('')
    
    doc.add_heading('EVENTS OF DEFAULT', 1)
    doc.add_paragraph('{{events_of_default}}')
    doc.add_paragraph('')
    
    # ESG Section (if applicable)
    doc.add_heading('SUSTAINABILITY-LINKED LOAN PROVISIONS', 1)
    doc.add_paragraph('Sustainability-Linked: {{sustainability_linked}}')
    doc.add_paragraph('ESG KPI Targets: {{esg_kpi_targets}}')
    doc.add_paragraph('SPT Definitions: {{spt_definitions}}')
    doc.add_paragraph('Margin Adjustment: {{margin_adjustment}}')
    doc.add_paragraph('')
    
    # Save document
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"Created template file: {output_path}")


def main():
    """Create template files for all templates in the database."""
    # Initialize database
    init_db()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get all templates from database
        templates = TemplateRegistry.list_templates(db)
        
        if not templates:
            print("No templates found in database. Please seed templates first.")
            return
        
        print(f"Found {len(templates)} template(s) in database")
        
        # Base path for templates
        base_path = Path("storage/templates")
        base_path.mkdir(parents=True, exist_ok=True)
        
        created_count = 0
        
        for template in templates:
            template_code = template.template_code
            version = template.version
            
            # Try simple naming first: {template_code}-{version}.docx
            filename = f"{template_code}-{version}.docx"
            output_path = base_path / filename
            
            # Check if file already exists
            if output_path.exists():
                print(f"Template file already exists: {output_path}")
                continue
            
            # Create template file
            try:
                create_template_file(template_code, version, output_path)
                created_count += 1
                
                # Update template file_path if it doesn't match
                if template.file_path != str(output_path.absolute()):
                    template.file_path = str(output_path.absolute())
                    db.commit()
                    print(f"Updated template file_path to: {output_path.absolute()}")
                    
            except Exception as e:
                print(f"Error creating template file for {template_code}: {e}")
                continue
        
        print(f"\nSuccessfully created {created_count} template file(s)")
        
        if created_count < len(templates):
            print(f"Note: {len(templates) - created_count} template file(s) already existed")
            
    except Exception as e:
        print(f"Error: {e}", exc_info=True)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()





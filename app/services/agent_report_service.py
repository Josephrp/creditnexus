"""Agent Report Service for CreditNexus.

Provides centralized service for creating, formatting, and attaching agent reports
to deals, documents, and other entities.

Follows repository patterns:
- Service layer with dependency injection
- Document attachment via DealService
- File storage via FileStorageService
- CDM event generation
- Audit logging
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.services.deal_service import DealService
from app.services.file_storage_service import FileStorageService
from app.services.report_formatter import ReportFormatter
from app.db.models import Document, Deal, DealNote
from app.utils.audit import log_audit_action
from app.db.models import AuditAction

logger = logging.getLogger(__name__)


class AgentReportService:
    """
    Service for creating and managing agent reports.
    
    Provides:
    - Report generation from agent results
    - Report formatting (Markdown, PDF, JSON)
    - Document attachment to deals
    - Note creation for agent interactions
    - CDM event generation
    """
    
    def __init__(self, db: Session):
        """
        Initialize agent report service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.deal_service = DealService(db)
        self.file_storage_service = FileStorageService()
        self.report_formatter = ReportFormatter()
    
    async def create_agent_report(
        self,
        agent_type: str,  # 'deepresearch', 'langalpha', 'peoplehub'
        agent_result: Dict[str, Any],
        deal_id: Optional[int] = None,
        document_id: Optional[int] = None,
        user_id: Optional[int] = None,
        format: str = 'markdown',  # 'markdown', 'pdf', 'json'
        attach_as_document: bool = True,
        create_note: bool = True
    ) -> Dict[str, Any]:
        """
        Create an agent report and optionally attach it to a deal/document.
        
        Args:
            agent_type: Type of agent ('deepresearch', 'langalpha', 'peoplehub')
            agent_result: Agent result data
            deal_id: Optional deal ID to attach report to
            document_id: Optional document ID to attach report to
            user_id: User ID for audit logging
            format: Report format ('markdown', 'pdf', 'json')
            attach_as_document: Whether to attach as a document (default: True)
            create_note: Whether to create a note (default: True)
            
        Returns:
            Dictionary with report_id, document_id (if attached), note_id (if created), and file_path
        """
        logger.info(f"Creating {agent_type} report for deal={deal_id}, document={document_id}")
        
        # Format report based on agent type
        formatted_report = await self._format_agent_report(agent_type, agent_result, format)
        
        report_metadata = {
            "agent_type": agent_type,
            "format": format,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "agent_result": agent_result
        }
        
        document_id_result = None
        note_id_result = None
        file_path = None
        
        # Attach as document if requested
        if attach_as_document and deal_id:
            try:
                # Generate filename
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                filename = f"{agent_type}_report_{timestamp}.{format}"
                
                        # Store file
                if deal_id:
                    deal = self.deal_service.get_deal(deal_id)
                    if deal:
                        # Create document record first to get document_id
                        document = Document(
                            deal_id=deal_id,
                            filename=filename,
                            file_path="",  # Will be set after file storage
                            document_type=f"{agent_type}_report",
                            uploaded_by=user_id,
                            extraction_status="completed",
                            cdm_data=agent_result
                        )
                        self.db.add(document)
                        self.db.flush()
                        document_id_result = document.id
                        
                        # Convert content to bytes if string
                        content_bytes = formatted_report["content"].encode('utf-8') if isinstance(formatted_report["content"], str) else formatted_report["content"]
                        
                        # Store file with document_id
                        file_path = self.file_storage_service.store_deal_document(
                            user_id=deal.applicant_id,
                            deal_id=deal.deal_id,
                            document_id=document.id,
                            filename=filename,
                            content=content_bytes,
                            subdirectory="generated"  # Store reports in generated subdirectory
                        )
                        
                        # Update document with file path
                        document.file_path = file_path
                        self.db.add(document)
                        self.db.flush()
                        
                        # Attach to deal
                        self.deal_service.attach_document_to_deal(
                            deal_id=deal_id,
                            document_id=document.id,
                            user_id=user_id or deal.applicant_id
                        )
                        
                        logger.info(f"Attached {agent_type} report as document {document.id} to deal {deal_id}")
            except Exception as e:
                logger.error(f"Failed to attach report as document: {e}", exc_info=True)
                # Continue even if document attachment fails
        
        # Create note if requested
        if create_note and deal_id:
            try:
                from app.services.agent_note_service import AgentNoteService
                note_service = AgentNoteService(db)
                
                note_content = self._generate_note_content(agent_type, agent_result, formatted_report)
                
                note = note_service.create_agent_interaction_note(
                    agent_type=agent_type,
                    interaction_data=agent_result,
                    deal_id=deal_id,
                    document_id=document_id,
                    user_id=user_id,
                    note_content=note_content
                )
                
                note_id_result = note.id
                logger.info(f"Created note {note.id} for {agent_type} report")
            except Exception as e:
                logger.error(f"Failed to create note: {e}", exc_info=True)
                # Continue even if note creation fails
        
        # Audit logging
        if user_id:
            log_audit_action(
                db=self.db,
                action=AuditAction.CREATE,
                target_type="agent_report",
                target_id=document_id_result,
                user_id=user_id,
                metadata={
                    "agent_type": agent_type,
                    "format": format,
                    "deal_id": deal_id,
                    "document_id": document_id,
                    "attached_as_document": attach_as_document,
                    "note_created": create_note
                }
            )
        
        self.db.commit()
        
        return {
            "status": "success",
            "agent_type": agent_type,
            "format": format,
            "document_id": document_id_result,
            "note_id": note_id_result,
            "file_path": file_path,
            "report_metadata": report_metadata
        }
    
    async def _format_agent_report(
        self,
        agent_type: str,
        agent_result: Dict[str, Any],
        format: str
    ) -> Dict[str, str]:
        """
        Format agent report based on type and format.
        
        Args:
            agent_type: Type of agent
            agent_result: Agent result data
            format: Desired format ('markdown', 'pdf', 'json')
            
        Returns:
            Dictionary with 'content' and 'content_type'
        """
        if format == 'json':
            import json
            return {
                "content": json.dumps(agent_result, indent=2),
                "content_type": "application/json"
            }
        elif format == 'markdown':
            content = self.report_formatter.format_agent_report_markdown(agent_type, agent_result)
            return {
                "content": content,
                "content_type": "text/markdown"
            }
        elif format == 'pdf':
            # PDF generation would require additional libraries (e.g., reportlab, weasyprint)
            # For now, generate markdown and note that PDF conversion is not yet implemented
            logger.warning("PDF format not yet implemented, generating markdown instead")
            content = self.report_formatter.format_agent_report_markdown(agent_type, agent_result)
            return {
                "content": content,
                "content_type": "text/markdown"
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_note_content(
        self,
        agent_type: str,
        agent_result: Dict[str, Any],
        formatted_report: Dict[str, str]
    ) -> str:
        """
        Generate note content from agent result.
        
        Args:
            agent_type: Type of agent
            agent_result: Agent result data
            formatted_report: Formatted report dictionary
            
        Returns:
            Note content string
        """
        agent_labels = {
            'deepresearch': 'DeepResearch',
            'langalpha': 'LangAlpha Quantitative Analysis',
            'peoplehub': 'PeopleHub Research'
        }
        
        agent_label = agent_labels.get(agent_type, agent_type)
        
        # Extract summary from result
        summary = ""
        if agent_type == 'deepresearch':
            summary = agent_result.get('answer', '')[:500] if isinstance(agent_result.get('answer'), str) else ''
        elif agent_type == 'langalpha':
            report = agent_result.get('report', {})
            structured = report.get('structured_report', {}) if isinstance(report, dict) else {}
            summary = structured.get('executive_summary', '')[:500] if isinstance(structured, dict) else ''
        elif agent_type == 'peoplehub':
            profile_data = agent_result.get('profile_data', {})
            research = profile_data.get('research_report', '')[:500] if isinstance(profile_data, dict) else ''
            summary = research if research else ''
        
        note_content = f"{agent_label} Report Generated\n\n"
        if summary:
            note_content += f"Summary: {summary}\n\n"
        note_content += f"Full report available as attached document."
        
        return note_content
    
    def get_agent_reports(
        self,
        deal_id: Optional[int] = None,
        agent_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get agent reports for a deal or all deals.
        
        Args:
            deal_id: Optional deal ID to filter by
            agent_type: Optional agent type to filter by
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of report dictionaries
        """
        query = self.db.query(Document).filter(
            Document.document_type.like('%_report')
        )
        
        if deal_id:
            query = query.filter(Document.deal_id == deal_id)
        
        if agent_type:
            query = query.filter(Document.document_type == f"{agent_type}_report")
        
        documents = query.order_by(Document.created_at.desc()).limit(limit).offset(offset).all()
        
        reports = []
        for doc in documents:
            reports.append({
                "id": doc.id,
                "document_id": doc.id,
                "agent_type": doc.document_type.replace("_report", ""),
                "deal_id": doc.deal_id,
                "filename": doc.filename,
                "file_path": doc.file_path,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "cdm_data": doc.cdm_data
            })
        
        return reports

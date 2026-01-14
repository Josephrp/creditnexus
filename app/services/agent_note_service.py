"""Agent Note Service for CreditNexus.

Provides service for creating notes from agent interactions (LangAlpha, DeepResearch, PeopleHub).
Follows repository patterns:
- Service layer with dependency injection
- Automatic note creation from agent results
- File system storage and ChromaDB indexing
- Audit logging
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.models import DealNote, Deal
from app.services.file_storage_service import FileStorageService
from app.chains.document_retrieval_chain import DocumentRetrievalService
from app.utils.audit import log_audit_action
from app.db.models import AuditAction

logger = logging.getLogger(__name__)


class AgentNoteService:
    """
    Service for creating notes from agent interactions.
    
    Provides:
    - Automatic note creation from agent results
    - Note formatting and metadata extraction
    - File system storage and ChromaDB indexing
    - Audit logging
    """
    
    def __init__(self, db: Session):
        """
        Initialize agent note service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.file_storage = FileStorageService()
    
    def create_agent_interaction_note(
        self,
        agent_type: str,  # deepresearch, langalpha, peoplehub
        interaction_data: Dict[str, Any],
        deal_id: Optional[int] = None,
        document_id: Optional[int] = None,
        user_id: Optional[int] = None,
        person_id: Optional[int] = None,
        business_id: Optional[int] = None
    ) -> DealNote:
        """
        Create a note from agent interaction.
        
        Args:
            agent_type: Type of agent (deepresearch, langalpha, peoplehub)
            interaction_data: Dictionary containing agent interaction data
            deal_id: Optional deal ID to attach note to
            document_id: Optional document ID (for future document notes)
            user_id: Optional user ID
            person_id: Optional person profile ID (for future person notes)
            business_id: Optional business profile ID (for future business notes)
            
        Returns:
            Created DealNote instance
            
        Raises:
            ValueError: If deal_id is required but not provided or deal not found
        """
        # Validate deal_id if provided
        if deal_id:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")
        elif not deal_id:
            # For now, require deal_id (future: support document/user/person/business notes)
            raise ValueError("deal_id is required for agent interaction notes")
        
        # Extract note content
        note_content = self._format_note_content(agent_type, interaction_data)
        
        # Determine note_type based on agent_type
        note_type = self._get_note_type(agent_type)
        
        # Create DealNote record
        note = DealNote(
            deal_id=deal_id,
            user_id=user_id or 1,  # Default to system user if not provided
            content=note_content,
            note_type=note_type,
            note_metadata={
                "agent_type": agent_type,
                "interaction_data": interaction_data,
                "document_id": document_id,
                "person_id": person_id,
                "business_id": business_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )
        self.db.add(note)
        self.db.flush()
        
        # Store note in file system
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if deal:
                self.file_storage.store_deal_note(
                    user_id=deal.applicant_id,
                    deal_id=deal.deal_id,
                    note_id=note.id,
                    content=note_content,
                    metadata=note.note_metadata
                )
        except Exception as e:
            logger.warning(f"Failed to store note in file system: {e}")
        
        # Index note in ChromaDB
        try:
            retrieval_service = DocumentRetrievalService(collection_name="creditnexus_deal_notes")
            retrieval_service.add_document(
                document_id=note.id,
                cdm_data={"content": note_content, "note_type": note_type},
                metadata={
                    "deal_id": str(deal_id),
                    "deal_deal_id": deal.deal_id if deal else None,
                    "user_id": str(user_id) if user_id else None,
                    "note_type": note_type,
                    "agent_type": agent_type,
                    "created_at": note.created_at.isoformat() if note.created_at else None,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to index note in ChromaDB: {e}")
        
        # Audit logging
        log_audit_action(
            db=self.db,
            action=AuditAction.CREATE,
            target_type="agent_interaction_note",
            target_id=note.id,
            user_id=user_id,
            metadata={
                "agent_type": agent_type,
                "note_type": note_type,
                "deal_id": deal_id,
                "document_id": document_id
            }
        )
        
        self.db.commit()
        self.db.refresh(note)
        
        logger.info(f"Created agent interaction note {note.id} for {agent_type} agent")
        
        return note
    
    def _format_note_content(
        self,
        agent_type: str,
        interaction_data: Dict[str, Any]
    ) -> str:
        """
        Format note content from interaction data.
        
        Args:
            agent_type: Type of agent
            interaction_data: Agent interaction data
            
        Returns:
            Formatted note content string
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Extract summary
        summary = self._extract_summary(interaction_data)
        
        # Build note content
        content_parts = [
            f"Agent Interaction: {agent_type.upper()}",
            f"Timestamp: {timestamp}",
            ""
        ]
        
        # Add query if available
        if "query" in interaction_data:
            content_parts.append(f"Query: {interaction_data['query']}")
            content_parts.append("")
        
        # Add summary
        if summary:
            content_parts.append("Summary:")
            content_parts.append(summary)
            content_parts.append("")
        
        # Add key findings if available
        if "key_findings" in interaction_data and interaction_data["key_findings"]:
            content_parts.append("Key Findings:")
            findings = interaction_data["key_findings"]
            if isinstance(findings, list):
                for i, finding in enumerate(findings, 1):
                    content_parts.append(f"{i}. {finding}")
            else:
                content_parts.append(str(findings))
            content_parts.append("")
        
        # Add analysis type if available (for LangAlpha)
        if "analysis_type" in interaction_data:
            content_parts.append(f"Analysis Type: {interaction_data['analysis_type']}")
            content_parts.append("")
        
        # Add person name if available (for PeopleHub)
        if "person_name" in interaction_data:
            content_parts.append(f"Person: {interaction_data['person_name']}")
            content_parts.append("")
        
        # Add answer if available (for DeepResearch)
        if "answer" in interaction_data and interaction_data["answer"]:
            answer = interaction_data["answer"]
            # Truncate if too long
            if len(answer) > 500:
                answer = answer[:500] + "..."
            content_parts.append("Answer:")
            content_parts.append(answer)
            content_parts.append("")
        
        # Add report summary if available
        if "report_summary" in interaction_data and interaction_data["report_summary"]:
            content_parts.append("Report Summary:")
            content_parts.append(interaction_data["report_summary"])
            content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _get_note_type(self, agent_type: str) -> str:
        """
        Map agent_type to note_type.
        
        Args:
            agent_type: Type of agent (deepresearch, langalpha, peoplehub)
            
        Returns:
            Note type string
        """
        mapping = {
            "langalpha": "analysis_result",
            "deepresearch": "research_result",
            "peoplehub": "research_result"
        }
        return mapping.get(agent_type.lower(), "agent_interaction")
    
    def _extract_summary(self, interaction_data: Dict[str, Any]) -> str:
        """
        Extract summary from interaction data.
        
        Args:
            interaction_data: Agent interaction data
            
        Returns:
            Summary string
        """
        # Try different summary fields
        summary_fields = [
            "executive_summary",
            "summary",
            "report_summary",
            "final_report",
            "research_summary"
        ]
        
        for field in summary_fields:
            if field in interaction_data and interaction_data[field]:
                summary = interaction_data[field]
                if isinstance(summary, str):
                    # Truncate if too long
                    if len(summary) > 1000:
                        return summary[:1000] + "..."
                    return summary
                elif isinstance(summary, dict):
                    # Extract text from dict
                    if "overview" in summary:
                        return summary["overview"]
                    elif "summary" in summary:
                        return summary["summary"]
        
        # Fallback: use answer or query
        if "answer" in interaction_data and interaction_data["answer"]:
            answer = interaction_data["answer"]
            if len(answer) > 500:
                return answer[:500] + "..."
            return answer
        
        if "query" in interaction_data:
            return f"Query: {interaction_data['query']}"
        
        return "Agent interaction completed."

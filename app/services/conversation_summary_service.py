"""Conversation Summary Service for CreditNexus.

Provides conversation summarization for chatbot sessions using AuditReportChain pattern.
Follows repository patterns:
- Service layer with dependency injection
- LLM-powered summarization
- Conversation history management
- CDM event integration
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.llm_client import get_chat_model
from app.chains.audit_report_chain import AuditReportChain
from app.db.models import ChatbotSession, ChatbotMessage
from app.utils.audit import log_audit_action
from app.db.models import AuditAction

logger = logging.getLogger(__name__)


class ConversationSummaryService:
    """
    Service for summarizing chatbot conversations.
    
    Uses AuditReportChain pattern for generating executive summaries
    of conversations to enable memory sharing across middleware.
    """
    
    def __init__(self, db: Session):
        """
        Initialize conversation summary service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.llm = get_chat_model(temperature=0.3)  # Lower temperature for more consistent summaries
        self.audit_report_chain = AuditReportChain()
    
    async def summarize_conversation(
        self,
        session_id: str,
        user_id: Optional[int] = None,
        max_messages: int = 50,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a summary of a conversation session.
        
        Args:
            session_id: Chatbot session ID
            user_id: Optional user ID for audit logging
            max_messages: Maximum number of messages to include in summary (default: 50)
            force_refresh: Force regeneration even if summary exists (default: False)
            
        Returns:
            Dictionary with summary, key_points, and metadata
        """
        # Load session
        session = self.db.query(ChatbotSession).filter(
            ChatbotSession.session_id == session_id
        ).first()
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Check if summary already exists and is recent (unless force_refresh)
        if not force_refresh and session.conversation_summary:
            # Check if summary is still valid (e.g., less than 1 hour old)
            if session.summary_updated_at:
                age_hours = (datetime.now(timezone.utc) - session.summary_updated_at).total_seconds() / 3600
                if age_hours < 1.0:
                    logger.info(f"Returning existing summary for session {session_id}")
                    return {
                        "summary": session.conversation_summary,
                        "key_points": session.summary_key_points or [],
                        "metadata": {
                            "session_id": session_id,
                            "summary_updated_at": session.summary_updated_at.isoformat() if session.summary_updated_at else None,
                            "message_count": session.message_count or 0
                        }
                    }
        
        # Load messages
        messages = self.db.query(ChatbotMessage).filter(
            ChatbotMessage.session_id == session.id
        ).order_by(ChatbotMessage.created_at.asc()).limit(max_messages).all()
        
        if not messages:
            return {
                "summary": "No messages in this conversation.",
                "key_points": [],
                "metadata": {
                    "session_id": session_id,
                    "message_count": 0
                }
            }
        
        # Build conversation text
        conversation_text = self._build_conversation_text(messages)
        
        # Generate summary using LLM (inspired by AuditReportChain pattern)
        try:
            summary = await self._generate_summary_with_llm(conversation_text, {
                "session_id": session_id,
                "deal_id": session.deal_id,
                "document_id": session.document_id,
                "message_count": len(messages)
            })
            key_points = self._extract_key_points(summary)
        except Exception as e:
            logger.warning(f"Failed to generate summary: {e}, falling back to simple summary")
            # Fallback: simple summary
            summary = self._generate_simple_summary(conversation_text)
            key_points = self._extract_key_points(summary)
        
        # Update session with summary
        session.conversation_summary = summary
        session.summary_key_points = key_points
        session.summary_updated_at = datetime.now(timezone.utc)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Audit logging
        if user_id:
            log_audit_action(
                db=self.db,
                action=AuditAction.UPDATE,
                target_type="conversation_summary",
                target_id=session.id,
                user_id=user_id,
                metadata={
                    "session_id": session_id,
                    "message_count": len(messages),
                    "summary_length": len(summary)
                }
            )
        
        logger.info(f"Generated conversation summary for session {session_id}")
        
        return {
            "summary": summary,
            "key_points": key_points,
            "metadata": {
                "session_id": session_id,
                "summary_updated_at": session.summary_updated_at.isoformat() if session.summary_updated_at else None,
                "message_count": len(messages)
            }
        }
    
    def _build_conversation_text(self, messages: List[ChatbotMessage]) -> str:
        """
        Build conversation text from messages.
        
        Args:
            messages: List of ChatbotMessage objects
            
        Returns:
            Formatted conversation text
        """
        lines = []
        for msg in messages:
            role = "User" if msg.role == "user" else "Assistant"
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if msg.created_at else ""
            lines.append(f"[{timestamp}] {role}: {msg.content}")
        
        return "\n".join(lines)
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """
        Extract key points from summary text.
        
        Args:
            summary: Summary text
            
        Returns:
            List of key point strings
        """
        # Simple extraction: look for numbered or bulleted points
        key_points = []
        lines = summary.split("\n")
        
        for line in lines:
            line = line.strip()
            # Match numbered lists (1., 2., etc.) or bullet points (-, •, etc.)
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•") or line.startswith("*")):
                # Remove numbering/bullets and clean
                cleaned = line.lstrip("0123456789.-•* ").strip()
                if cleaned and len(cleaned) > 10:  # Only include substantial points
                    key_points.append(cleaned)
        
        # If no structured points found, split by sentences and take first few
        if not key_points:
            sentences = summary.split(". ")
            key_points = [s.strip() + "." for s in sentences[:3] if s.strip()]
        
        return key_points[:5]  # Limit to 5 key points
    
    async def _generate_summary_with_llm(
        self,
        conversation_text: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate summary using LLM with structured output.
        
        Args:
            conversation_text: Full conversation text
            context: Additional context (session_id, deal_id, etc.)
            
        Returns:
            Summary string
        """
        from langchain_core.messages import HumanMessage, SystemMessage
        from pydantic import BaseModel, Field
        
        class ConversationSummary(BaseModel):
            """Structured conversation summary."""
            summary: str = Field(description="2-3 sentence summary of the conversation")
            key_points: List[str] = Field(description="3-5 key points discussed")
        
        system_prompt = """You are an expert at summarizing conversations. Generate a concise summary that captures:
- Main topics discussed
- Key decisions or actions taken
- Important information shared
- Workflows or processes launched

Be concise, professional, and focus on actionable insights."""
        
        user_prompt = f"""Summarize the following conversation:

Session Context:
- Session ID: {context.get('session_id', 'N/A')}
- Deal ID: {context.get('deal_id', 'N/A')}
- Document ID: {context.get('document_id', 'N/A')}
- Message Count: {context.get('message_count', 0)}

Conversation:
{conversation_text}

Provide a summary and key points."""
        
        try:
            structured_llm = self.llm.with_structured_output(ConversationSummary)
            result = await structured_llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Combine summary and key points
            summary_parts = [result.summary]
            if result.key_points:
                summary_parts.append("\n\nKey Points:")
                for i, point in enumerate(result.key_points, 1):
                    summary_parts.append(f"{i}. {point}")
            
            return "\n".join(summary_parts)
        except Exception as e:
            logger.error(f"Failed to generate structured summary: {e}")
            raise
    
    def _generate_simple_summary(self, conversation_text: str) -> str:
        """
        Generate a simple summary using LLM.
        
        Args:
            conversation_text: Full conversation text
            
        Returns:
            Summary string
        """
        prompt = f"""Summarize the following conversation in 2-3 sentences, focusing on:
- Main topics discussed
- Key decisions or actions taken
- Important information shared

Conversation:
{conversation_text}

Summary:"""
        
        try:
            from langchain_core.messages import HumanMessage
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Failed to generate simple summary: {e}")
            # Ultimate fallback: truncate conversation
            return conversation_text[:500] + "..." if len(conversation_text) > 500 else conversation_text
    
    def get_conversation_summary(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve existing conversation summary.
        
        Args:
            session_id: Chatbot session ID
            
        Returns:
            Summary dictionary or None if not found
        """
        session = self.db.query(ChatbotSession).filter(
            ChatbotSession.session_id == session_id
        ).first()
        
        if not session or not session.conversation_summary:
            return None
        
        return {
            "summary": session.conversation_summary,
            "key_points": session.summary_key_points or [],
            "metadata": {
                "session_id": session_id,
                "summary_updated_at": session.summary_updated_at.isoformat() if session.summary_updated_at else None,
                "message_count": session.message_count or 0
            }
        }

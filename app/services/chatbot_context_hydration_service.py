"""Chatbot Context Hydration Service.

This service loads comprehensive context from multiple sources to hydrate chatbots
with available information including deals, documents, CDM data, agent results,
and related entities.
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from app.db.models import (
    Deal, Document, DocumentVersion, StagedExtraction,
    DealNote, PolicyDecision, AccountingDocument,
    DeepResearchResult, QuantitativeAnalysisResult,
    IndividualProfile, BusinessProfile,
    ChatbotSession, ChatbotMessage
)

logger = logging.getLogger(__name__)


class ChatbotContextHydrationService:
    """
    Service for hydrating chatbot context with comprehensive information.
    
    Loads context from:
    - Deal information and metadata
    - Document extraction results (CDM data, accounting documents)
    - Parties and credit agreement data
    - Previous agent results (DeepResearch, LangAlpha, PeopleHub)
    - Deal notes and timeline events
    - Policy decisions
    - User profiles and business intelligence
    """
    
    def __init__(self, db: Session):
        """
        Initialize context hydration service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def hydrate_context(
        self,
        deal_id: Optional[int] = None,
        document_id: Optional[int] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        include_agent_results: bool = True,
        include_accounting_docs: bool = True,
        include_policy_decisions: bool = True,
        include_profiles: bool = True,
        max_items_per_category: int = 10
    ) -> Dict[str, Any]:
        """
        Hydrate comprehensive context for chatbot.
        
        Args:
            deal_id: Optional deal ID to load context for
            document_id: Optional document ID to load context for
            user_id: Optional user ID for user profile context
            session_id: Optional chatbot session ID for conversation history
            include_agent_results: Whether to include agent results (DeepResearch, LangAlpha, PeopleHub)
            include_accounting_docs: Whether to include accounting documents
            include_policy_decisions: Whether to include policy decisions
            include_profiles: Whether to include business intelligence profiles
            max_items_per_category: Maximum items to load per category
            
        Returns:
            Dictionary with comprehensive context organized by category
        """
        context = {
            "deal": None,
            "document": None,
            "cdm_data": None,
            "accounting_documents": [],
            "agent_results": {
                "deep_research": [],
                "langalpha": [],
                "peoplehub": []
            },
            "deal_notes": [],
            "policy_decisions": [],
            "profiles": {
                "individual": [],
                "business": []
            },
            "conversation_summary": None,
            "user_profile": None,
            "metadata": {
                "loaded_at": datetime.utcnow().isoformat(),
                "sources": []
            }
        }
        
        try:
            # Load deal context
            if deal_id:
                deal_context = self._load_deal_context(deal_id, max_items_per_category)
                context["deal"] = deal_context.get("deal")
                context["deal_notes"] = deal_context.get("notes", [])
                context["metadata"]["sources"].append("deal")
                
                # Load documents associated with deal
                if not document_id:
                    deal_docs = deal_context.get("documents", [])
                    if deal_docs:
                        # Use the most recent document if no specific document_id
                        context["document"] = deal_docs[0] if deal_docs else None
                        if context["document"]:
                            doc_id = context["document"].get("id")
                            if doc_id:
                                document_id = doc_id
            
            # Load document context
            if document_id:
                doc_context = self._load_document_context(
                    document_id,
                    include_cdm=True,
                    include_accounting=include_accounting_docs,
                    max_items=max_items_per_category
                )
                context["document"] = doc_context.get("document")
                context["cdm_data"] = doc_context.get("cdm_data")
                context["accounting_documents"] = doc_context.get("accounting_documents", [])
                context["metadata"]["sources"].append("document")
                
                # If document has deal_id, ensure deal context is loaded
                if context["document"] and context["document"].get("deal_id") and not context["deal"]:
                    deal_id = context["document"]["deal_id"]
                    deal_context = self._load_deal_context(deal_id, max_items_per_category)
                    context["deal"] = deal_context.get("deal")
                    context["deal_notes"] = deal_context.get("notes", [])
            
            # Load agent results if requested
            if include_agent_results:
                if deal_id:
                    agent_results = self._load_agent_results(deal_id, max_items_per_category)
                    context["agent_results"] = agent_results
                    if any(agent_results.values()):
                        context["metadata"]["sources"].append("agent_results")
            
            # Load policy decisions if requested
            if include_policy_decisions:
                if deal_id:
                    policy_decisions = self._load_policy_decisions(deal_id, max_items_per_category)
                    context["policy_decisions"] = policy_decisions
                    if policy_decisions:
                        context["metadata"]["sources"].append("policy_decisions")
            
            # Load profiles if requested
            if include_profiles:
                if deal_id:
                    profiles = self._load_profiles(deal_id, max_items_per_category)
                    context["profiles"] = profiles
                    if any(profiles.values()):
                        context["metadata"]["sources"].append("profiles")
            
            # Load conversation summary if session_id provided
            if session_id:
                summary = self._load_conversation_summary(session_id)
                context["conversation_summary"] = summary
                if summary:
                    context["metadata"]["sources"].append("conversation_summary")
            
            # Load user profile if user_id provided
            if user_id:
                user_profile = self._load_user_profile(user_id)
                context["user_profile"] = user_profile
                if user_profile:
                    context["metadata"]["sources"].append("user_profile")
        
        except Exception as e:
            logger.error(f"Error hydrating chatbot context: {e}", exc_info=True)
            context["error"] = str(e)
        
        return context
    
    def _load_deal_context(self, deal_id: int, max_items: int = 10) -> Dict[str, Any]:
        """Load deal context including deal data, documents, and notes."""
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                return {}
            
            # Load deal documents
            documents = self.db.query(Document).filter(
                Document.deal_id == deal_id
            ).order_by(desc(Document.created_at)).limit(max_items).all()
            
            doc_list = []
            for doc in documents:
                doc_dict = {
                    "id": doc.id,
                    "title": doc.title,
                    "borrower_name": doc.borrower_name,
                    "borrower_lei": doc.borrower_lei,
                    "total_commitment": float(doc.total_commitment) if doc.total_commitment else None,
                    "currency": doc.currency,
                    "agreement_date": doc.agreement_date.isoformat() if doc.agreement_date else None,
                    "sustainability_linked": doc.sustainability_linked,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                }
                
                # Load latest extraction result if available
                latest_version = self.db.query(DocumentVersion).filter(
                    DocumentVersion.document_id == doc.id
                ).order_by(desc(DocumentVersion.version_number)).first()
                
                if latest_version:
                    staged_extraction = self.db.query(StagedExtraction).filter(
                        StagedExtraction.document_version_id == latest_version.id
                    ).first()
                    
                    if staged_extraction and staged_extraction.extraction_result:
                        doc_dict["extraction_status"] = staged_extraction.status.value if staged_extraction.status else None
                        doc_dict["has_cdm_data"] = True
                
                doc_list.append(doc_dict)
            
            # Load deal notes
            notes = self.db.query(DealNote).filter(
                DealNote.deal_id == deal_id
            ).order_by(desc(DealNote.created_at)).limit(max_items).all()
            
            notes_list = [
                {
                    "id": note.id,
                    "content": note.content,
                    "note_type": note.note_type,
                    "created_at": note.created_at.isoformat() if note.created_at else None,
                    "created_by": note.created_by,
                }
                for note in notes
            ]
            
            return {
                "deal": {
                    "id": deal.id,
                    "deal_id": deal.deal_id,
                    "status": deal.status,
                    "deal_type": deal.deal_type,
                    "deal_data": deal.deal_data,
                    "applicant_id": deal.applicant_id,
                    "created_at": deal.created_at.isoformat() if deal.created_at else None,
                    "updated_at": deal.updated_at.isoformat() if deal.updated_at else None,
                },
                "documents": doc_list,
                "notes": notes_list
            }
        except Exception as e:
            logger.warning(f"Failed to load deal context: {e}")
            return {}
    
    def _load_document_context(
        self,
        document_id: int,
        include_cdm: bool = True,
        include_accounting: bool = True,
        max_items: int = 10
    ) -> Dict[str, Any]:
        """Load document context including extraction results and CDM data."""
        try:
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return {}
            
            doc_dict = {
                "id": document.id,
                "title": document.title,
                "borrower_name": document.borrower_name,
                "borrower_lei": document.borrower_lei,
                "total_commitment": float(document.total_commitment) if document.total_commitment else None,
                "currency": document.currency,
                "agreement_date": document.agreement_date.isoformat() if document.agreement_date else None,
                "sustainability_linked": document.sustainability_linked,
                "esg_metadata": document.esg_metadata,
                "deal_id": document.deal_id,
                "created_at": document.created_at.isoformat() if document.created_at else None,
            }
            
            cdm_data = None
            accounting_docs = []
            
            # Load latest extraction result
            latest_version = self.db.query(DocumentVersion).filter(
                DocumentVersion.document_id == document_id
            ).order_by(desc(DocumentVersion.version_number)).first()
            
            if latest_version:
                staged_extraction = self.db.query(StagedExtraction).filter(
                    StagedExtraction.document_version_id == latest_version.id
                ).first()
                
                if staged_extraction:
                    doc_dict["extraction_status"] = staged_extraction.status.value if staged_extraction.status else None
                    
                    # Load CDM data from extraction result
                    if include_cdm and staged_extraction.extraction_result:
                        try:
                            extraction_result = staged_extraction.extraction_result
                            if isinstance(extraction_result, dict):
                                # Extract CreditAgreement if present
                                if "agreement" in extraction_result:
                                    cdm_data = extraction_result["agreement"]
                                elif "credit_agreement" in extraction_result:
                                    cdm_data = extraction_result["credit_agreement"]
                                else:
                                    cdm_data = extraction_result
                        except Exception as e:
                            logger.warning(f"Failed to parse CDM data: {e}")
            
            # Load accounting documents if requested
            if include_accounting:
                accounting_docs = self._load_accounting_documents(document_id, max_items)
            
            return {
                "document": doc_dict,
                "cdm_data": cdm_data,
                "accounting_documents": accounting_docs
            }
        except Exception as e:
            logger.warning(f"Failed to load document context: {e}")
            return {}
    
    def _load_accounting_documents(self, document_id: int, max_items: int = 10) -> List[Dict[str, Any]]:
        """Load accounting documents associated with a document."""
        try:
            accounting_docs = self.db.query(AccountingDocument).filter(
                AccountingDocument.document_id == document_id
            ).order_by(desc(AccountingDocument.created_at)).limit(max_items).all()
            
            return [
                {
                    "id": doc.id,
                    "document_type": doc.document_type,
                    "reporting_period_start": doc.reporting_period_start.isoformat() if doc.reporting_period_start else None,
                    "reporting_period_end": doc.reporting_period_end.isoformat() if doc.reporting_period_end else None,
                    "currency": doc.currency,
                    "extraction_data": doc.extraction_data,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                }
                for doc in accounting_docs
            ]
        except Exception as e:
            logger.warning(f"Failed to load accounting documents: {e}")
            return []
    
    def _load_agent_results(self, deal_id: int, max_items: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Load agent results (DeepResearch, LangAlpha, PeopleHub) for a deal."""
        results = {
            "deep_research": [],
            "langalpha": [],
            "peoplehub": []
        }
        
        try:
            # Load DeepResearch results
            deep_research = self.db.query(DeepResearchResult).filter(
                DeepResearchResult.deal_id == deal_id
            ).order_by(desc(DeepResearchResult.created_at)).limit(max_items).all()
            
            results["deep_research"] = [
                {
                    "id": result.id,
                    "research_id": result.research_id,
                    "query": result.query,
                    "answer": result.answer[:500] if result.answer else None,  # Truncate for context
                    "status": result.status,
                    "created_at": result.created_at.isoformat() if result.created_at else None,
                    "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                }
                for result in deep_research
            ]
            
            # Load LangAlpha (QuantitativeAnalysis) results
            quantitative_analysis = self.db.query(QuantitativeAnalysisResult).filter(
                QuantitativeAnalysisResult.deal_id == deal_id
            ).order_by(desc(QuantitativeAnalysisResult.created_at)).limit(max_items).all()
            
            results["langalpha"] = [
                {
                    "id": result.id,
                    "analysis_id": result.analysis_id,
                    "analysis_type": result.analysis_type,
                    "query": result.query,
                    "report": result.report,  # Full report data
                    "summary": str(result.report.get("summary", ""))[:500] if result.report and isinstance(result.report, dict) else None,  # Extract summary from report
                    "status": result.status,
                    "created_at": result.created_at.isoformat() if result.created_at else None,
                    "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                }
                for result in quantitative_analysis
            ]
            
            # Load PeopleHub (IndividualProfile) results
            individual_profiles = self.db.query(IndividualProfile).filter(
                IndividualProfile.deal_id == deal_id
            ).order_by(desc(IndividualProfile.created_at)).limit(max_items).all()
            
            results["peoplehub"] = [
                {
                    "id": profile.id,
                    "person_name": profile.person_name,
                    "person_lei": profile.person_lei,
                    "profile_data": profile.profile_data,
                    "created_at": profile.created_at.isoformat() if profile.created_at else None,
                }
                for profile in individual_profiles
            ]
        except Exception as e:
            logger.warning(f"Failed to load agent results: {e}")
        
        return results
    
    def _load_policy_decisions(self, deal_id: int, max_items: int = 10) -> List[Dict[str, Any]]:
        """Load policy decisions for a deal."""
        try:
            # Policy decisions are linked via transaction_id which may be deal_id
            decisions = self.db.query(PolicyDecision).filter(
                PolicyDecision.transaction_id == str(deal_id)
            ).order_by(desc(PolicyDecision.created_at)).limit(max_items).all()
            
            return [
                {
                    "id": decision.id,
                    "transaction_id": decision.transaction_id,
                    "decision": decision.decision,
                    "rule_applied": decision.rule_applied,
                    "trace_id": decision.trace_id,
                    "created_at": decision.created_at.isoformat() if decision.created_at else None,
                }
                for decision in decisions
            ]
        except Exception as e:
            logger.warning(f"Failed to load policy decisions: {e}")
            return []
    
    def _load_profiles(self, deal_id: int, max_items: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Load business intelligence profiles for a deal."""
        profiles = {
            "individual": [],
            "business": []
        }
        
        try:
            # Load individual profiles
            individual_profiles = self.db.query(IndividualProfile).filter(
                IndividualProfile.deal_id == deal_id
            ).order_by(desc(IndividualProfile.created_at)).limit(max_items).all()
            
            profiles["individual"] = [
                {
                    "id": profile.id,
                    "person_name": profile.person_name,
                    "person_lei": profile.person_lei,
                    "profile_data": profile.profile_data,
                    "created_at": profile.created_at.isoformat() if profile.created_at else None,
                }
                for profile in individual_profiles
            ]
            
            # Load business profiles
            business_profiles = self.db.query(BusinessProfile).filter(
                BusinessProfile.deal_id == deal_id
            ).order_by(desc(BusinessProfile.created_at)).limit(max_items).all()
            
            profiles["business"] = [
                {
                    "id": profile.id,
                    "business_name": profile.business_name,
                    "business_lei": profile.business_lei,
                    "business_type": profile.business_type,
                    "industry": profile.industry,
                    "profile_data": profile.profile_data,
                    "created_at": profile.created_at.isoformat() if profile.created_at else None,
                }
                for profile in business_profiles
            ]
        except Exception as e:
            logger.warning(f"Failed to load profiles: {e}")
        
        return profiles
    
    def _load_conversation_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation summary for a chatbot session."""
        try:
            session = self.db.query(ChatbotSession).filter(
                ChatbotSession.session_id == session_id
            ).first()
            
            if session and session.conversation_summary:
                return {
                    "summary": session.conversation_summary,
                    "key_points": session.summary_key_points,
                    "message_count": session.message_count,
                    "summary_updated_at": session.summary_updated_at.isoformat() if session.summary_updated_at else None,
                }
        except Exception as e:
            logger.warning(f"Failed to load conversation summary: {e}")
        
        return None
    
    def _load_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Load user profile information."""
        try:
            from app.db.models import User
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "display_name": user.display_name,
                    "role": user.role,
                    "profile_data": user.profile_data,
                }
        except Exception as e:
            logger.warning(f"Failed to load user profile: {e}")
        
        return None
    
    def format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """
        Format hydrated context into a structured string for LLM consumption.
        
        Args:
            context: Hydrated context dictionary
            
        Returns:
            Formatted string with context information
        """
        parts = []
        
        # Deal context
        if context.get("deal"):
            deal = context["deal"]
            parts.append("=== DEAL CONTEXT ===")
            parts.append(f"Deal ID: {deal.get('deal_id')}")
            parts.append(f"Status: {deal.get('status')}")
            parts.append(f"Type: {deal.get('deal_type')}")
            if deal.get("deal_data"):
                parts.append(f"Deal Data: {json.dumps(deal['deal_data'], indent=2, default=str)}")
            parts.append("")
        
        # Document context
        if context.get("document"):
            doc = context["document"]
            parts.append("=== DOCUMENT CONTEXT ===")
            parts.append(f"Document: {doc.get('title')}")
            parts.append(f"Borrower: {doc.get('borrower_name')}")
            if doc.get("borrower_lei"):
                parts.append(f"LEI: {doc.get('borrower_lei')}")
            if doc.get("total_commitment"):
                parts.append(f"Total Commitment: {doc.get('total_commitment')} {doc.get('currency', '')}")
            if doc.get("agreement_date"):
                parts.append(f"Agreement Date: {doc.get('agreement_date')}")
            parts.append("")
        
        # CDM data
        if context.get("cdm_data"):
            parts.append("=== CDM DATA ===")
            parts.append(json.dumps(context["cdm_data"], indent=2, default=str))
            parts.append("")
        
        # Accounting documents
        if context.get("accounting_documents"):
            parts.append("=== ACCOUNTING DOCUMENTS ===")
            for acc_doc in context["accounting_documents"][:3]:  # Limit to 3
                parts.append(f"- {acc_doc.get('document_type')}: {acc_doc.get('reporting_period_start')} to {acc_doc.get('reporting_period_end')}")
            parts.append("")
        
        # Agent results
        agent_results = context.get("agent_results", {})
        if any(agent_results.values()):
            parts.append("=== PREVIOUS AGENT RESULTS ===")
            
            if agent_results.get("deep_research"):
                parts.append(f"DeepResearch Results ({len(agent_results['deep_research'])}):")
                for result in agent_results["deep_research"][:2]:  # Limit to 2
                    parts.append(f"  - Query: {result.get('query')}")
                    if result.get("answer"):
                        parts.append(f"    Answer: {result.get('answer')[:200]}...")
            
            if agent_results.get("langalpha"):
                parts.append(f"LangAlpha Results ({len(agent_results['langalpha'])}):")
                for result in agent_results["langalpha"][:2]:  # Limit to 2
                    parts.append(f"  - Type: {result.get('analysis_type')}, Query: {result.get('query')}")
                    if result.get("summary"):
                        parts.append(f"    Summary: {result.get('summary')[:200]}...")
            
            if agent_results.get("peoplehub"):
                parts.append(f"PeopleHub Results ({len(agent_results['peoplehub'])}):")
                for result in agent_results["peoplehub"][:2]:  # Limit to 2
                    parts.append(f"  - Person: {result.get('person_name')}")
            
            parts.append("")
        
        # Deal notes
        if context.get("deal_notes"):
            parts.append("=== DEAL NOTES ===")
            for note in context["deal_notes"][:3]:  # Limit to 3
                parts.append(f"- [{note.get('note_type')}] {note.get('content')[:200]}")
            parts.append("")
        
        # Policy decisions
        if context.get("policy_decisions"):
            parts.append("=== POLICY DECISIONS ===")
            for decision in context["policy_decisions"][:3]:  # Limit to 3
                parts.append(f"- Decision: {decision.get('decision')}, Rule: {decision.get('rule_applied')}")
            parts.append("")
        
        # Conversation summary
        if context.get("conversation_summary"):
            summary = context["conversation_summary"]
            parts.append("=== CONVERSATION SUMMARY ===")
            parts.append(summary.get("summary", ""))
            if summary.get("key_points"):
                parts.append("Key Points:")
                for point in summary["key_points"][:5]:
                    parts.append(f"  - {point}")
            parts.append("")
        
        return "\n".join(parts)

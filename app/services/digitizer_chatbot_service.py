"""Digitizer Chatbot Service for Document Digitizer UI.

Provides chat interface with workflow launching capabilities (PeopleHub, LangAlpha, DeepResearch).
"""

import logging
import uuid
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.llm_client import get_chat_model
from app.models.cdm_events import generate_cdm_observation
from app.services.deal_service import DealService
from app.workflows.peoplehub_research_graph import execute_peoplehub_research
from app.services.deep_research_service import DeepResearchService
from app.services.agent_note_service import AgentNoteService
from app.services.conversation_summary_service import ConversationSummaryService
from app.services.chatbot_context_hydration_service import ChatbotContextHydrationService

logger = logging.getLogger(__name__)


class DigitizerChatbotService:
    """
    Chatbot service for document digitizer UI.
    
    Provides:
    - Chat interface with document context
    - Workflow launching (PeopleHub, LangAlpha, DeepResearch)
    - Deal context integration
    - CDM event generation
    - Conversation history management
    """
    
    def __init__(self, db: Session):
        """
        Initialize digitizer chatbot service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.llm = get_chat_model(temperature=0.7)
        self.deal_service = DealService(db)
        self.summary_service = ConversationSummaryService(db)
        self.context_hydration = ChatbotContextHydrationService(db)
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        user_id: Optional[int] = None,
        deal_id: Optional[int] = None,
        document_id: Optional[int] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        document_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            message: User message
            session_id: Chat session ID
            user_id: User ID
            deal_id: Optional deal ID for context
            document_id: Optional document ID for context
            conversation_history: Previous conversation messages
            document_context: Document context (extracted CDM data, etc.)
            
        Returns:
            Dictionary with response, workflow_launched, and metadata
        """
        logger.info(f"Processing chatbot message: session={session_id}, user={user_id}, deal={deal_id}")
        
        # Check if message is a workflow launch command
        workflow_launched = await self._check_workflow_launch(message, deal_id, user_id)
        if workflow_launched:
            return {
                "response": workflow_launched.get("message", "Workflow launched successfully."),
                "workflow_launched": workflow_launched.get("workflow_type"),
                "workflow_result": workflow_launched.get("result"),
                "cdm_events": workflow_launched.get("cdm_events", [])
            }
        
        # Hydrate comprehensive context from multiple sources
        hydrated_context = self.context_hydration.hydrate_context(
            deal_id=deal_id,
            document_id=document_id,
            user_id=user_id,
            session_id=session_id,
            include_agent_results=True,
            include_accounting_docs=True,
            include_policy_decisions=True,
            include_profiles=True,
            max_items_per_category=10
        )
        
        # Format context for LLM
        formatted_context = self.context_hydration.format_context_for_llm(hydrated_context)
        
        # Also include raw document_context if provided (for backward compatibility)
        context_parts = []
        if formatted_context:
            context_parts.append(formatted_context)
        
        if document_context:
            context_parts.append(f"\nAdditional Document Context:\n{json.dumps(document_context, indent=2, default=str)}")
        
        # Build conversation history for context
        history_text = ""
        if conversation_history:
            history_text = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
        
        # Create prompt with enhanced context awareness
        system_prompt = """You are an AI assistant for the CreditNexus Document Digitizer. You help users:
1. Understand extracted document data and CDM (Common Domain Model) information
2. Answer questions about credit agreements, accounting documents, and deal context
3. Launch research workflows (PeopleHub, LangAlpha, DeepResearch)
4. Navigate deal context, document history, agent results, and policy decisions

You have access to comprehensive context including:
- Deal information (status, type, metadata)
- Document extraction results (CDM data, accounting documents)
- Previous agent results (DeepResearch, LangAlpha, PeopleHub analyses)
- Deal notes and timeline events
- Policy decisions and compliance information
- Business intelligence profiles

You can launch workflows by recognizing commands like:
- "Research person [name]" or "Launch PeopleHub for [name]" → Launches PeopleHub research
- "Deep research [query]" or "Launch DeepResearch for [query]" → Launches DeepResearch
- "Analyze financials" or "Launch LangAlpha" → Launches LangAlpha quantitative analysis

Use the provided context to give informed, accurate responses. Reference specific information from the context when relevant.
Be helpful, concise, and professional. If you don't know something, say so."""
        
        user_prompt = f"""User Message: {message}

{history_text if history_text else ""}

{chr(10).join(context_parts) if context_parts else ""}

Provide a helpful response. If the user wants to launch a workflow, acknowledge it and explain what will happen."""
        
        try:
            # Generate response
            response = await self.llm.ainvoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Generate CDM event for chatbot interaction
            cdm_event = generate_cdm_observation(
                trade_id=str(deal_id) if deal_id else session_id,
                satellite_hash="",
                ndvi_score=0.0,
                status="CHATBOT_INTERACTION"
            )
            cdm_event["eventType"] = "ChatbotInteraction"
            cdm_event["chatbotInteraction"] = {
                "session_id": session_id,
                "message": message,
                "response": response_text,
                "deal_id": deal_id,
                "document_id": document_id
            }
            
            # Check if conversation summarization is needed
            # Trigger summarization if conversation has 10+ messages or every 20 messages
            try:
                from app.db.models import ChatbotSession, ChatbotMessage
                session = self.db.query(ChatbotSession).filter(
                    ChatbotSession.session_id == session_id
                ).first()
                
                if session:
                    message_count = self.db.query(ChatbotMessage).filter(
                        ChatbotMessage.session_id == session.id
                    ).count()
                    
                    # Update message count
                    session.message_count = message_count
                    self.db.add(session)
                    self.db.commit()
                    
                    # Trigger summarization if needed (async, non-blocking)
                    if message_count >= 10 and (message_count % 20 == 0 or not session.conversation_summary):
                        # Run summarization in background (fire and forget)
                        import asyncio
                        try:
                            asyncio.create_task(
                                self.summary_service.summarize_conversation(
                                    session_id=session_id,
                                    user_id=user_id,
                                    max_messages=50,
                                    force_refresh=(message_count % 20 == 0)
                                )
                            )
                        except Exception as e:
                            logger.warning(f"Failed to trigger conversation summarization: {e}")
            except Exception as e:
                logger.warning(f"Failed to check/update conversation summary: {e}")
            
            return {
                "response": response_text,
                "workflow_launched": None,
                "cdm_events": [cdm_event]
            }
            
        except Exception as e:
            logger.error(f"Error processing chatbot message: {e}", exc_info=True)
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "workflow_launched": None,
                "cdm_events": []
            }
    
    async def _check_workflow_launch(
        self,
        message: str,
        deal_id: Optional[int],
        user_id: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if message is a workflow launch command and execute it.
        
        Returns:
            Dictionary with workflow result if launched, None otherwise
        """
        message_lower = message.lower()
        
        # Check for PeopleHub launch
        if any(keyword in message_lower for keyword in ["research person", "peoplehub", "launch peoplehub"]):
            # Extract person name from message
            person_name = self._extract_person_name(message)
            if person_name:
                return await self._launch_peoplehub(person_name, deal_id, user_id)
        
        # Check for DeepResearch launch
        if any(keyword in message_lower for keyword in ["deep research", "deepresearch", "launch deepresearch"]):
            # Extract query from message
            query = self._extract_query(message, ["deep research", "deepresearch", "launch deepresearch"])
            if query:
                return await self._launch_deep_research(query, deal_id, user_id)
        
        # Check for LangAlpha launch
        if any(keyword in message_lower for keyword in ["analyze financials", "langalpha", "launch langalpha", "analyze company", "analyze market"]):
            # Extract query from message
            query = self._extract_query(message, ["analyze financials", "langalpha", "launch langalpha", "analyze company", "analyze market"])
            if query:
                return await self._launch_langalpha(query, deal_id, user_id)
            else:
                # Use the full message as query if no specific query extracted
                return await self._launch_langalpha(message, deal_id, user_id)
        
        return None
    
    def _extract_person_name(self, message: str) -> Optional[str]:
        """Extract person name from message."""
        # Simple extraction - look for text after keywords
        keywords = ["research person", "peoplehub for", "launch peoplehub for"]
        for keyword in keywords:
            if keyword.lower() in message.lower():
                parts = message.lower().split(keyword.lower(), 1)
                if len(parts) > 1:
                    name = parts[1].strip()
                    # Remove common trailing words
                    for word in ["please", "now", "thanks", "thank you"]:
                        if name.endswith(word):
                            name = name[:-len(word)].strip()
                    if name:
                        return name
        return None
    
    def _extract_query(self, message: str, keywords: List[str]) -> Optional[str]:
        """Extract query from message."""
        message_lower = message.lower()
        for keyword in keywords:
            if keyword in message_lower:
                parts = message_lower.split(keyword, 1)
                if len(parts) > 1:
                    query = parts[1].strip()
                    # Remove common trailing words
                    for word in ["please", "now", "thanks", "thank you"]:
                        if query.endswith(word):
                            query = query[:-len(word)].strip()
                    if query:
                        return query
        return None
    
    async def _launch_peoplehub(
        self,
        person_name: str,
        deal_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Launch PeopleHub research workflow."""
        logger.info(f"Launching PeopleHub research for: {person_name}")
        
        try:
            result = await execute_peoplehub_research(
                person_name=person_name,
                linkedin_url=None
            )
            
            # Generate CDM event
            cdm_event = generate_cdm_observation(
                trade_id=str(deal_id) if deal_id else "unknown",
                satellite_hash="",
                ndvi_score=0.0,
                status="PEOPLEHUB_LAUNCHED"
            )
            cdm_event["eventType"] = "WorkflowLaunch"
            cdm_event["workflowLaunch"] = {
                "workflow_type": "peoplehub",
                "person_name": person_name,
                "result": result.get("final_report", "Research completed"),
                "deal_id": deal_id
            }
            
            # Update deal timeline if deal_id provided
            if deal_id:
                try:
                    self.deal_service.add_timeline_event(
                        deal_id=deal_id,
                        event_type="peoplehub_research_launched",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        data={
                            "person_name": person_name,
                            "research_report": result.get("final_report", "")[:500]  # First 500 chars
                        },
                        user_id=user_id
                    )
                except Exception as e:
                    logger.warning(f"Failed to update deal timeline: {e}")
            
            # Create agent interaction note if deal_id provided
            if deal_id:
                try:
                    note_service = AgentNoteService(self.db)
                    note = note_service.create_agent_interaction_note(
                        agent_type="peoplehub",
                        interaction_data={
                            "person_name": person_name,
                            "final_report": result.get("final_report", ""),
                            "profile_data": result.get("profile_data", {}),
                            "research_summary": result.get("research_summary", "")
                        },
                        deal_id=deal_id,
                        user_id=user_id
                    )
                    logger.info(f"Created agent interaction note {note.id} for PeopleHub research")
                except Exception as e:
                    logger.warning(f"Failed to create agent interaction note: {e}")
            
            return {
                "workflow_type": "peoplehub",
                "message": f"PeopleHub research launched for {person_name}. Research report generated.",
                "result": result,
                "cdm_events": [cdm_event]
            }
            
        except Exception as e:
            logger.error(f"Error launching PeopleHub: {e}", exc_info=True)
            return {
                "workflow_type": "peoplehub",
                "message": f"Failed to launch PeopleHub research: {str(e)}",
                "result": None,
                "cdm_events": []
            }
    
    async def _launch_deep_research(
        self,
        query: str,
        deal_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Launch DeepResearch workflow."""
        logger.info(f"Launching DeepResearch for query: {query}")
        
        try:
            research_service = DeepResearchService(self.db)
            
            # Create research result record
            from app.db.models import DeepResearchResult
            research_result = DeepResearchResult(
                query=query,
                status="pending",
                user_id=user_id,
                deal_id=deal_id
            )
            self.db.add(research_result)
            self.db.commit()
            self.db.refresh(research_result)
            
            # Execute research asynchronously
            research_id = research_result.id
            await research_service.research_query(
                research_id=research_id,
                query=query,
                user_id=user_id,
                deal_id=deal_id
            )
            
            # Generate CDM event
            cdm_event = generate_cdm_observation(
                trade_id=str(deal_id) if deal_id else "unknown",
                satellite_hash="",
                ndvi_score=0.0,
                status="DEEPRESEARCH_LAUNCHED"
            )
            cdm_event["eventType"] = "WorkflowLaunch"
            cdm_event["workflowLaunch"] = {
                "workflow_type": "deepresearch",
                "query": query,
                "research_id": research_id,
                "deal_id": deal_id
            }
            
            return {
                "workflow_type": "deepresearch",
                "message": f"DeepResearch launched for query: {query}. Research ID: {research_id}",
                "result": {
                    "research_id": research_id,
                    "status": "completed"
                },
                "cdm_events": [cdm_event]
            }
            
        except Exception as e:
            logger.error(f"Error launching DeepResearch: {e}", exc_info=True)
            return {
                "workflow_type": "deepresearch",
                "message": f"Failed to launch DeepResearch: {str(e)}",
                "result": None,
                "cdm_events": []
            }
    
    async def _launch_langalpha(
        self,
        query: str,
        deal_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Launch LangAlpha quantitative analysis workflow."""
        logger.info(f"Launching LangAlpha analysis for query: {query}")
        
        try:
            from app.services.quantitative_analysis_service import QuantitativeAnalysisService
            
            service = QuantitativeAnalysisService(self.db)
            
            # Determine analysis type from query
            query_lower = query.lower()
            if "company" in query_lower or "ticker" in query_lower or any(ticker in query_lower for ticker in ["aapl", "msft", "googl", "tsla"]):
                # Company analysis
                # Extract ticker if present
                ticker = None
                for common_ticker in ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META", "NVDA"]:
                    if common_ticker.lower() in query_lower:
                        ticker = common_ticker
                        break
                
                result = await service.analyze_company(
                    query=query,
                    ticker=ticker,
                    deal_id=deal_id,
                    user_id=user_id
                )
            elif "market" in query_lower or "sector" in query_lower or "industry" in query_lower:
                # Market analysis
                result = await service.analyze_market(
                    query=query,
                    deal_id=deal_id,
                    user_id=user_id
                )
            elif deal_id:
                # Loan application analysis (if deal_id provided)
                result = await service.analyze_loan_application(
                    query=query,
                    deal_id=deal_id,
                    user_id=user_id
                )
            else:
                # Default to company analysis
                result = await service.analyze_company(
                    query=query,
                    deal_id=deal_id,
                    user_id=user_id
                )
            
            # Generate CDM event
            cdm_event = result.get("cdm_event", generate_cdm_observation(
                trade_id=str(deal_id) if deal_id else "unknown",
                satellite_hash="",
                ndvi_score=0.0,
                status="LANGALPHA_LAUNCHED"
            ))
            cdm_event["eventType"] = "WorkflowLaunch"
            cdm_event["workflowLaunch"] = {
                "workflow_type": "langalpha",
                "query": query,
                "analysis_id": result.get("analysis_id"),
                "analysis_type": result.get("analysis_type", "company"),
                "deal_id": deal_id
            }
            
            # Update deal timeline if deal_id provided
            if deal_id:
                try:
                    self.deal_service.add_timeline_event(
                        deal_id=deal_id,
                        event_type="langalpha_analysis_launched",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        data={
                            "query": query,
                            "analysis_id": result.get("analysis_id"),
                            "analysis_type": result.get("analysis_type", "company")
                        },
                        user_id=user_id
                    )
                except Exception as e:
                    logger.warning(f"Failed to update deal timeline: {e}")
            
            return {
                "workflow_type": "langalpha",
                "message": f"LangAlpha quantitative analysis launched. Analysis ID: {result.get('analysis_id')}",
                "result": result,
                "cdm_events": [cdm_event]
            }
            
        except Exception as e:
            logger.error(f"Error launching LangAlpha: {e}", exc_info=True)
            return {
                "workflow_type": "langalpha",
                "message": f"Error launching LangAlpha: {str(e)}",
                "result": None,
                "cdm_events": []
            }

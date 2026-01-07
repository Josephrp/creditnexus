"""Decision support chatbot chain for LMA template generation.

This module implements an AI chatbot that provides decision support for:
- Template selection based on CDM data
- Interactive field filling
- General questions about LMA templates and CDM schema
- Uses RAG (Retrieval Augmented Generation) with ChromaDB knowledge base
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Install with: pip install chromadb")

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.llm_client import get_chat_model, get_embeddings_model
from app.core.config import settings

logger = logging.getLogger(__name__)


class DecisionSupportChatbot:
    """AI chatbot for decision support in LMA template generation.
    
    Provides:
    - Chat interface with CDM context
    - Template suggestions based on CDM data
    - Interactive field filling assistance
    - Knowledge base retrieval for templates and CDM schema
    """
    
    def __init__(
        self,
        kb_collection_name: str = "chatbot_knowledge_base",
        persist_directory: Optional[str] = None,
    ):
        """Initialize decision support chatbot.
        
        Args:
            kb_collection_name: Name of ChromaDB collection for knowledge base
            persist_directory: Directory to persist ChromaDB data
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is not installed. Install with: pip install chromadb"
            )
        
        # Set default persist directory
        if persist_directory is None:
            persist_directory = getattr(settings, "CHROMADB_PERSIST_DIR", "./chroma_db")
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.kb_collection_name = kb_collection_name
        self.client = None
        self.collection = None
        self.embeddings_model = None
        self.llm = None
        
        # Initialize ChromaDB and models
        self._initialize_client()
        self._initialize_models()
    
    def _initialize_client(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.kb_collection_name,
                metadata={"description": "Chatbot knowledge base for LMA templates and CDM schema"}
            )
            
            logger.info(
                f"Initialized ChromaDB collection '{self.kb_collection_name}' "
                f"with {self.collection.count()} documents"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def _initialize_models(self) -> None:
        """Initialize LLM and embeddings models."""
        try:
            self.embeddings_model = get_embeddings_model()
            self.llm = get_chat_model(temperature=0.7)  # Higher temperature for conversational responses
            logger.info("Initialized LLM and embeddings models for chatbot")
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise
    
    def _retrieve_relevant_context(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context from knowledge base.
        
        Args:
            query: User query
            top_k: Number of relevant documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            if self.collection.count() == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embeddings_model.embed_query(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            contexts = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for idx in range(len(results["ids"][0])):
                    contexts.append({
                        "content": results["documents"][0][idx],
                        "metadata": results["metadatas"][0][idx] if results["metadatas"] else {},
                        "distance": results["distances"][0][idx] if results["distances"] else None,
                    })
            
            return contexts
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        cdm_context: Optional[Dict[str, Any]] = None,
        use_kb: bool = True,
    ) -> Dict[str, Any]:
        """Chat with the decision support chatbot.
        
        Args:
            message: User message
            conversation_history: Previous conversation messages [{"role": "user"|"assistant", "content": "..."}]
            cdm_context: Current CDM data context
            use_kb: Whether to use knowledge base retrieval
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Retrieve relevant context from knowledge base
            context_docs = []
            if use_kb:
                context_docs = self._retrieve_relevant_context(message, top_k=5)
            
            # Build system prompt
            system_prompt = """You are an expert AI assistant for LMA (Loan Market Association) document generation.
Your role is to help users:
1. Select appropriate LMA templates based on their credit agreement data (CDM)
2. Fill missing CDM fields interactively
3. Answer questions about LMA templates, CDM schema, and document generation
4. Provide guidance on best practices for credit agreement documentation

You have access to a knowledge base of LMA template metadata and CDM schema documentation.
Use this knowledge to provide accurate, helpful responses.

Be conversational, helpful, and precise. When suggesting templates, explain why they match the user's needs.
When helping fill fields, ask clarifying questions if needed."""
            
            # Build context from knowledge base
            kb_context = ""
            if context_docs:
                kb_context = "\n\nRelevant Knowledge Base Information:\n"
                for doc in context_docs:
                    kb_context += f"- {doc['content']}\n"
                    if doc.get('metadata', {}).get('source'):
                        kb_context += f"  (Source: {doc['metadata']['source']})\n"
            
            # Build CDM context
            cdm_context_str = ""
            if cdm_context:
                cdm_context_str = f"\n\nCurrent CDM Data Context:\n{json.dumps(cdm_context, indent=2, default=str)}"
            
            # Build conversation history
            messages = [SystemMessage(content=system_prompt + kb_context + cdm_context_str)]
            
            if conversation_history:
                for msg in conversation_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # Add current user message
            messages.append(HumanMessage(content=message))
            
            # Generate response
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "response": response_text,
                "sources": [doc.get('metadata', {}).get('source', 'knowledge_base') for doc in context_docs],
                "context_used": len(context_docs) > 0,
            }
        except Exception as e:
            logger.error(f"Chat failed: {e}", exc_info=True)
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "sources": [],
                "context_used": False,
                "error": str(e),
            }
    
    def suggest_template(
        self,
        cdm_data: Dict[str, Any],
        available_templates: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Suggest appropriate LMA templates based on CDM data.
        
        Args:
            cdm_data: CDM data dictionary
            available_templates: Optional list of available templates with metadata
            
        Returns:
            Dictionary with template suggestions and reasoning
        """
        try:
            # Convert CDM data to text for context
            cdm_text = self._cdm_to_text(cdm_data)
            
            # Retrieve relevant template information from knowledge base
            template_context = self._retrieve_relevant_context(
                f"LMA template for {cdm_text}",
                top_k=10
            )
            
            # Build prompt
            system_prompt = """You are an expert LMA template selection advisor.
Analyze the provided CDM data and suggest the most appropriate LMA template(s).

Consider:
- Agreement type (facility agreement, term sheet, confidentiality agreement, etc.)
- Governing law requirements
- Sustainability-linked loan indicators
- Complexity and specific clauses needed

Provide:
1. Primary template recommendation with reasoning
2. Alternative templates if applicable
3. Explanation of why each template fits the CDM data"""
            
            user_prompt = f"""CDM Data:
{cdm_text}

Available Templates:
{json.dumps(available_templates, indent=2, default=str) if available_templates else 'All templates available'}

Template Knowledge Base Context:
{chr(10).join([doc['content'] for doc in template_context[:5]]) if template_context else 'No specific template context available'}

Suggest the most appropriate template(s) and explain your reasoning."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to extract structured suggestions
            suggestions = self._parse_template_suggestions(response_text, available_templates)
            
            return {
                "suggestions": suggestions,
                "reasoning": response_text,
                "cdm_analysis": {
                    "has_parties": bool(cdm_data.get("parties")),
                    "has_facilities": bool(cdm_data.get("facilities")),
                    "is_sustainability_linked": cdm_data.get("sustainability_linked", False),
                    "governing_law": cdm_data.get("governing_law"),
                },
            }
        except Exception as e:
            logger.error(f"Template suggestion failed: {e}", exc_info=True)
            return {
                "suggestions": [],
                "reasoning": f"Error generating suggestions: {str(e)}",
                "error": str(e),
            }
    
    def fill_missing_fields(
        self,
        cdm_data: Dict[str, Any],
        required_fields: List[str],
        conversation_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Help fill missing CDM fields interactively.
        
        Args:
            cdm_data: Current CDM data (may be incomplete)
            required_fields: List of required field paths (e.g., ["parties", "facilities[0].facility_name"])
            conversation_context: Optional conversation context about what user is trying to do
            
        Returns:
            Dictionary with field suggestions, questions, and filled data
        """
        try:
            # Identify missing fields
            missing_fields = self._identify_missing_fields(cdm_data, required_fields)
            
            if not missing_fields:
                return {
                    "all_fields_present": True,
                    "filled_data": cdm_data,
                    "suggestions": {},
                    "questions": [],
                }
            
            # Retrieve relevant CDM schema information
            schema_context = self._retrieve_relevant_context(
                f"CDM schema for fields: {', '.join(missing_fields)}",
                top_k=5
            )
            
            # Build prompt
            system_prompt = """You are an expert CDM field filling assistant.
Help users fill missing required fields in their CDM data.

For each missing field:
1. Explain what the field represents
2. Ask clarifying questions if needed
3. Provide example values
4. Suggest values based on existing CDM data when possible

Be helpful and guide users through the process step by step."""
            
            user_prompt = f"""Current CDM Data:
{json.dumps(cdm_data, indent=2, default=str)}

Missing Required Fields:
{json.dumps(missing_fields, indent=2)}

Conversation Context:
{conversation_context or 'No specific context provided'}

CDM Schema Context:
{chr(10).join([doc['content'] for doc in schema_context]) if schema_context else 'No schema context available'}

Help fill the missing fields. Provide:
1. Questions to ask the user for each missing field
2. Suggested values based on existing data
3. Example values for reference"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to extract structured suggestions
            suggestions = self._parse_field_suggestions(response_text, missing_fields, cdm_data)
            
            return {
                "all_fields_present": False,
                "missing_fields": missing_fields,
                "suggestions": suggestions,
                "guidance": response_text,
                "questions": self._extract_questions(response_text),
            }
        except Exception as e:
            logger.error(f"Field filling failed: {e}", exc_info=True)
            return {
                "all_fields_present": False,
                "missing_fields": missing_fields if 'missing_fields' in locals() else [],
                "error": str(e),
            }
    
    def _cdm_to_text(self, cdm_data: Dict[str, Any]) -> str:
        """Convert CDM data to text representation."""
        text_parts = []
        
        if "parties" in cdm_data and isinstance(cdm_data["parties"], list):
            for party in cdm_data["parties"]:
                if isinstance(party, dict):
                    name = party.get("name", "")
                    role = party.get("role", "")
                    if name:
                        text_parts.append(f"Party: {name} ({role})")
        
        if "facilities" in cdm_data and isinstance(cdm_data["facilities"], list):
            for facility in cdm_data["facilities"]:
                if isinstance(facility, dict):
                    facility_name = facility.get("facility_name", "")
                    if facility_name:
                        text_parts.append(f"Facility: {facility_name}")
        
        if "governing_law" in cdm_data:
            text_parts.append(f"Governing Law: {cdm_data['governing_law']}")
        
        if "sustainability_linked" in cdm_data and cdm_data["sustainability_linked"]:
            text_parts.append("Sustainability-Linked Loan")
        
        return " | ".join(text_parts) if text_parts else json.dumps(cdm_data, default=str)
    
    def _identify_missing_fields(
        self,
        cdm_data: Dict[str, Any],
        required_fields: List[str],
    ) -> List[str]:
        """Identify which required fields are missing from CDM data."""
        missing = []
        
        for field_path in required_fields:
            if not self._field_exists(cdm_data, field_path):
                missing.append(field_path)
        
        return missing
    
    def _field_exists(self, data: Dict[str, Any], field_path: str) -> bool:
        """Check if a field path exists in the data structure."""
        try:
            parts = field_path.split('.')
            current = data
            
            for part in parts:
                if '[' in part:
                    # Handle array access like "facilities[0].facility_name"
                    key, index = part.split('[')
                    index = int(index.rstrip(']'))
                    if key:
                        current = current.get(key, [])
                    if not isinstance(current, list) or index >= len(current):
                        return False
                    current = current[index]
                else:
                    if not isinstance(current, dict) or part not in current:
                        return False
                    current = current[part]
            
            return current is not None
        except (KeyError, IndexError, TypeError, ValueError):
            return False
    
    def _parse_template_suggestions(
        self,
        response_text: str,
        available_templates: Optional[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """Parse template suggestions from LLM response."""
        suggestions = []
        
        # Try to extract template names/codes from response
        if available_templates:
            for template in available_templates:
                template_name = template.get("name", "").lower()
                template_code = template.get("template_code", "").lower()
                
                if template_name in response_text.lower() or template_code in response_text.lower():
                    suggestions.append({
                        "template_id": template.get("id"),
                        "template_code": template.get("template_code"),
                        "name": template.get("name"),
                        "category": template.get("category"),
                        "confidence": "high" if template_name in response_text.lower() else "medium",
                    })
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _parse_field_suggestions(
        self,
        response_text: str,
        missing_fields: List[str],
        cdm_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Parse field suggestions from LLM response."""
        suggestions = {}
        
        # Try to extract field suggestions from response
        for field in missing_fields:
            # Look for field mentions in response
            if field in response_text:
                suggestions[field] = {
                    "mentioned": True,
                    "guidance": response_text,
                }
        
        return suggestions
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from response text."""
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.endswith('?') and ('?' in line):
                questions.append(line)
        
        return questions
    
    def add_to_knowledge_base(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> None:
        """Add content to the knowledge base.
        
        Args:
            content: Text content to add
            metadata: Optional metadata (source, type, etc.)
            doc_id: Optional document ID (auto-generated if not provided)
        """
        try:
            if doc_id is None:
                import uuid
                doc_id = str(uuid.uuid4())
            
            # Generate embedding
            embedding = self.embeddings_model.embed_query(content)
            
            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata["content_type"] = doc_metadata.get("content_type", "general")
            
            # Add to collection
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[doc_metadata],
            )
            
            logger.info(f"Added document to knowledge base: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to add to knowledge base: {e}")
            raise
    
    def get_kb_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "collection_name": self.kb_collection_name,
            }
        except Exception as e:
            logger.error(f"Failed to get KB stats: {e}")
            return {"error": str(e)}













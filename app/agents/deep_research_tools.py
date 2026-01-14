"""DeepResearch tools for web search, URL reading, and query processing.

Tools are separated from the main agent for better organization and reusability.
"""

import logging
from typing import List, Dict, Any
from langchain_core.tools import Tool

from app.core.llm_client import get_chat_model
from app.services.web_search_service import get_web_search_service

logger = logging.getLogger(__name__)


def create_search_tool() -> Tool:
    """Create search tool using WebSearchService."""
    service = get_web_search_service()
    
    async def search_web(query: str) -> str:
        """Search the web for information."""
        try:
            result = await service.search_web(
                query=query,
                search_type="search",
                num_results=4,
                rerank=True
            )
            
            # Format results for agent
            formatted = []
            for chunk in result.get("extracted_content", []):
                formatted.append(
                    f"## {chunk.get('title', 'Untitled')}\n"
                    f"**URL:** {chunk.get('url', '')}\n\n"
                    f"{chunk.get('content', '')}\n"
                )
            
            return "\n---\n".join(formatted) if formatted else "No results found."
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"Search error: {str(e)}"
    
    return Tool(
        name="web_search",
        description="Search the web for information. Use this when you need to find information about a topic.",
        func=search_web
    )


def create_read_url_tool() -> Tool:
    """Create URL reading tool."""
    async def read_url(url: str) -> str:
        """Read content from a URL."""
        # TODO: Implement URL reading using Jina Reader or similar
        # For now, use web search service to fetch content
        service = get_web_search_service()
        try:
            # Use search to find the URL content
            result = await service.search_web(
                query=f"site:{url}",
                search_type="search",
                num_results=1,
                rerank=False
            )
            if result.get("extracted_content"):
                return result["extracted_content"][0].get("content", f"Content from: {url}")
            return f"Could not fetch content from: {url}"
        except Exception as e:
            logger.warning(f"URL reading failed: {e}")
            return f"Error reading URL: {str(e)}"
    
    return Tool(
        name="read_url",
        description="Read content from a URL. Use this to get detailed information from a webpage.",
        func=read_url
    )


def create_answer_evaluator_tool() -> Tool:
    """Create answer evaluation tool."""
    async def evaluate_answer(question: str, answer: str) -> str:
        """Evaluate if an answer is complete and accurate."""
        llm = get_chat_model(temperature=0.3)
        prompt = f"""Evaluate if the following answer is complete and accurate for the question:

Question: {question}

Answer: {answer}

Respond with: "COMPLETE" if the answer fully addresses the question, or "INCOMPLETE" with specific missing information.
"""
        response = await llm.ainvoke(prompt)
        return response.content
    
    return Tool(
        name="evaluate_answer",
        description="Evaluate if an answer is complete and accurate. Use this to check answer quality.",
        func=evaluate_answer
    )


def create_query_rewriter_tool() -> Tool:
    """Create query rewriter tool."""
    async def rewrite_query(original_query: str, context: str = "") -> str:
        """Rewrite a search query based on context."""
        llm = get_chat_model(temperature=0.7)
        prompt = f"""Rewrite the following search query to improve search results based on the context:

Original Query: {original_query}

Context: {context if context else 'No additional context'}

Return only the improved search query, nothing else.
"""
        response = await llm.ainvoke(prompt)
        return response.content.strip()
    
    return Tool(
        name="rewrite_query",
        description="Rewrite a search query to improve search results. Use this to refine queries.",
        func=rewrite_query
    )


def get_all_research_tools() -> List[Tool]:
    """Get all research tools for DeepResearch agent."""
    return [
        create_search_tool(),
        create_read_url_tool(),
        create_answer_evaluator_tool(),
        create_query_rewriter_tool()
    ]

"""DeepResearch orchestrator agent using LangChain.

Ports node-DeepResearch iterative research pattern to Python using LangChain.
Follows existing agent patterns from app/agents/analyzer.py
"""

import logging
import uuid
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder

from app.core.llm_client import get_chat_model
from app.agents.deep_research_tools import get_all_research_tools

logger = logging.getLogger(__name__)


class ResearchAction(str, Enum):
    """Research actions following DeepResearch pattern."""
    SEARCH = "search"
    READ = "read"
    ANSWER = "answer"
    REFLECT = "reflect"
    CODING = "coding"


@dataclass
class KnowledgeItem:
    """Knowledge item accumulated during research."""
    question: str
    answer: str
    references: List[str]
    type: str  # 'url', 'qa', 'side-info', 'coding'
    updated: Optional[str] = None


@dataclass
class ResearchContext:
    """Research context tracking."""
    token_budget: int = 1000000
    visited_urls: List[str] = field(default_factory=list)
    knowledge_items: List[KnowledgeItem] = field(default_factory=list)
    searched_queries: List[str] = field(default_factory=list)
    all_urls: Dict[str, Any] = field(default_factory=dict)


def create_deep_research_agent() -> AgentExecutor:
    """
    Create DeepResearch agent using LangChain ReAct pattern.
    
    Follows existing agent patterns:
    - Uses get_chat_model() for LLM
    - Creates ReAct agent with tools
    - Returns AgentExecutor for execution
    """
    llm = get_chat_model(temperature=0.7)  # Slightly higher for reasoning
    
    # Create tools for research actions
    tools = get_all_research_tools()
    
    # Create ReAct agent prompt
    from langchain import hub
    try:
        prompt = hub.pull("hwchase17/react")
    except Exception:
        # Fallback prompt if hub is unavailable
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate.from_template("""You are a helpful assistant that can use tools to answer questions.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}""")
    
    # Create ReAct agent
    agent = create_react_agent(llm, tools, prompt=prompt)
    
    # Create executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=20,  # Limit iterations to prevent infinite loops
        handle_parsing_errors=True
    )
    
    return executor


async def research_query(
    question: str,
    context: Optional[ResearchContext] = None,
    deal_id: Optional[int] = None,
    workflow_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Execute DeepResearch query with CDM event integration.
    
    Args:
        question: Research question
        context: Optional research context
        deal_id: Optional deal ID for CDM event linking
        workflow_id: Optional workflow ID for CDM event linking
        
    Returns:
        Research result with answer, knowledge items, and CDM events
    """
    if context is None:
        context = ResearchContext()
    
    # Create agent
    agent = create_deep_research_agent()
    
    # Execute research
    result = await agent.ainvoke({
        "input": question,
        "context": str(context)  # Convert context to string for agent
    })
    
    # Generate CDM event for research completion
    research_event = {
        "eventType": "ResearchQuery",
        "eventDate": datetime.now().isoformat(),
        "researchQuery": {
            "query": question,
            "answer": result.get("output", ""),
            "knowledgeItems": [item.__dict__ for item in context.knowledge_items],
            "visitedUrls": context.visited_urls,
            "searchedQueries": context.searched_queries
        },
        "meta": {
            "globalKey": str(uuid.uuid4()),
            "sourceSystem": "CreditNexus_DeepResearch_v1",
            "version": 1
        }
    }
    
    # Link to deal/workflow if provided
    if deal_id:
        research_event["relatedEventIdentifier"] = [{
            "eventIdentifier": {
                "issuer": "CreditNexus",
                "assignedIdentifier": [{"identifier": {"value": f"DEAL_{deal_id}"}}]
            }
        }]
    
    return {
        "answer": result.get("output", ""),
        "knowledge_items": [item.__dict__ for item in context.knowledge_items],
        "visited_urls": context.visited_urls,
        "cdm_event": research_event
    }

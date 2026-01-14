"""Psychometric analysis service using LangChain.

Analyzes individuals for psychometric traits, buying behaviors, and savings behaviors.
"""

import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_client import get_chat_model
from app.models.business_intelligence import (
    PsychometricProfile,
    BuyingBehaviorProfile,
    SavingsBehaviorProfile
)

logger = logging.getLogger(__name__)


def create_psychometric_analysis_chain() -> BaseChatModel:
    """
    Create LangChain chain for psychometric analysis.
    
    Follows existing chain pattern:
    - Uses get_chat_model()
    - Binds Pydantic model as structured output
    """
    llm = get_chat_model(temperature=0.3)  # Lower temperature for more consistent analysis
    structured_llm = llm.with_structured_output(PsychometricProfile)
    return structured_llm


def create_psychometric_analysis_prompt() -> ChatPromptTemplate:
    """Create prompt for psychometric analysis."""
    system_prompt = """You are an expert Psychometric Analyst specializing in financial behavior analysis. Your task is to analyze an individual's psychometric profile, buying behaviors, and savings behaviors based on their professional data, LinkedIn profile, and web research.

PSYCHOMETRIC ANALYSIS RESPONSIBILITIES:

1. BIG FIVE PERSONALITY TRAITS:
   - Openness to Experience (0.0-1.0): Creativity, curiosity, willingness to try new things
   - Conscientiousness (0.0-1.0): Organization, dependability, self-discipline
   - Extraversion (0.0-1.0): Sociability, assertiveness, emotional expressiveness
   - Agreeableness (0.0-1.0): Trust, altruism, kindness, affection
   - Neuroticism (0.0-1.0): Emotional stability, anxiety, moodiness

2. RISK TOLERANCE ASSESSMENT:
   - Conservative: Prefers low-risk, stable investments
   - Moderate: Balanced approach to risk
   - Aggressive: Willing to take high risks for high returns
   - Assess based on: Career choices, investment history, financial decisions

3. DECISION-MAKING STYLE:
   - Analytical: Data-driven, methodical
   - Intuitive: Gut-feel, quick decisions
   - Collaborative: Seeks input from others
   - Independent: Makes decisions alone

4. BUYING BEHAVIOR ANALYSIS:
   - Purchase Frequency: How often they make significant purchases
   - Average Transaction Value: Typical spending amount
   - Preferred Categories: Types of products/services they buy
   - Decision Factors: Price, quality, brand, convenience, etc.
   - Impulse Buying Tendency: Low, Moderate, High

5. SAVINGS BEHAVIOR ANALYSIS:
   - Savings Rate: Percentage of income saved (if inferable)
   - Investment Preferences: Stocks, bonds, real estate, crypto, etc.
   - Financial Goals: Short-term, medium-term, long-term
   - Emergency Fund: Likely presence and adequacy
   - Retirement Planning: Engagement level

6. CREDIT CHECK DATA POINTS:
   - Payment History Indicators: Based on professional reliability
   - Credit Utilization Patterns: Inferred from spending behavior
   - Debt Management: Likely approach to debt
   - Financial Stability: Job stability, income growth trajectory

CRITICAL RULES:
- Base analysis ONLY on available data (LinkedIn, web research, professional history)
- Use 0.0-1.0 scale for personality traits (0.5 = average)
- If data is insufficient, mark fields as None rather than guessing
- Provide confidence scores (0.0-1.0) for each assessment
- Focus on financial behavior indicators relevant to credit assessment
- Consider cultural and professional context in analysis
"""

    user_prompt = """Analyze the psychometric profile, buying behaviors, and savings behaviors for the following individual:

Person Name: {person_name}

LinkedIn Data:
{linkedin_data}

Web Research Summaries:
{web_summaries}

Professional History:
{professional_history}

Provide a comprehensive psychometric analysis with confidence scores.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    return prompt


async def analyze_individual(
    person_name: str,
    linkedin_data: Optional[Dict[str, Any]] = None,
    web_summaries: Optional[List[Dict[str, Any]]] = None,
    professional_history: Optional[Dict[str, Any]] = None
) -> PsychometricProfile:
    """
    Analyze individual for psychometric traits and behaviors.
    
    Args:
        person_name: Name of the individual
        linkedin_data: LinkedIn profile data
        web_summaries: Web research summaries
        professional_history: Professional history data
        
    Returns:
        PsychometricProfile with analysis results
    """
    chain = create_psychometric_analysis_chain()
    prompt = create_psychometric_analysis_prompt()
    
    extraction_chain = prompt | chain
    
    result = await extraction_chain.ainvoke({
        "person_name": person_name,
        "linkedin_data": linkedin_data or {},
        "web_summaries": web_summaries or [],
        "professional_history": professional_history or {}
    })
    
    return result

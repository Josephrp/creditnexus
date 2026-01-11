"""
Deal Generation Chain for Demo Data.

This module provides LangChain chains for generating realistic credit agreement
scenarios using LLMs with structured output validation.
"""

import logging
import random
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, date
from decimal import Decimal

from langchain_core.language_models import BaseChatModel
from pydantic import ValidationError

from app.core.llm_client import get_chat_model
from app.models.cdm import CreditAgreement, Party, LoanFacility, Money, Currency, FloatingRateOption, InterestRatePayout, Frequency, PeriodEnum, ESGKPITarget, ESGKPIType
from app.prompts.demo.deal_generation import (
    create_deal_generation_prompt,
    get_scenario_config,
    get_industry_weights,
    REQUIRED_FIELDS,
    OPTIONAL_FIELDS
)

logger = logging.getLogger(__name__)


def create_deal_generation_chain() -> BaseChatModel:
    """
    Create and configure the LangChain deal generation chain.
    
    Uses the LLM client abstraction to support multiple providers.
    The provider and model are configured via environment variables.
    
    Returns:
        A BaseChatModel instance configured with structured output
        bound to the CreditAgreement Pydantic model.
    """
    # Use global LLM configuration
    # Temperature set to 0.7 for more creative but still realistic generation
    llm = get_chat_model(temperature=0.7)
    
    # Bind the Pydantic model as a structured output
    structured_llm = llm.with_structured_output(CreditAgreement)
    
    return structured_llm


def generate_cdm_for_deal(
    deal_type: str = "loan_application",
    scenario: Optional[str] = None,
    seed: Optional[int] = None,
    industry: Optional[str] = None
) -> CreditAgreement:
    """
    Generate a CDM-compliant CreditAgreement for demo purposes.
    
    Args:
        deal_type: Type of deal (loan_application, refinancing, restructuring)
        scenario: Scenario template (corporate_lending, sustainability_linked, refinancing, restructuring)
                  If None, randomly selects based on deal_type
        seed: Random seed for reproducibility
        industry: Industry sector (if None, randomly selects)
        
    Returns:
        CreditAgreement instance with all required fields
        
    Raises:
        ValidationError: If generated data doesn't pass CDM validation
        RuntimeError: If LLM generation fails after retries
    """
    if seed is not None:
        random.seed(seed)
    
    # Select scenario if not provided
    if scenario is None:
        scenarios = ["corporate_lending", "sustainability_linked", "refinancing", "restructuring"]
        weights = [0.40, 0.30, 0.20, 0.10]  # Match distribution from plan
        scenario = random.choices(scenarios, weights=weights)[0]
    
    # Get scenario configuration
    scenario_config = get_scenario_config(scenario)
    
    # Select industry if not provided
    if industry is None:
        industry_weights = get_industry_weights()
        industries = list(industry_weights.keys())
        weights = list(industry_weights.values())
        industry = random.choices(industries, weights=weights)[0]
    
    # Create scenario-specific and industry-specific prompt
    prompt = create_deal_generation_prompt(deal_type, scenario, industry)
    
    # Format prompt with scenario details
    sustainability_note = ""
    if scenario == "sustainability_linked":
        sustainability_note = "Sustainability-Linked: YES - Must include ESG KPI targets with NDVI vegetation index"
    else:
        sustainability_note = "Sustainability-Linked: NO"
    
    prompt_vars = {
        "deal_type": deal_type,
        "scenario": scenario,
        "industry": industry,
        "loan_size_range": scenario_config["loan_size_range"],
        "term_range": scenario_config["term_range"],
        "interest_range": scenario_config["interest_range"],
        "sustainability_note": sustainability_note
    }
    
    # Create chain
    chain = create_deal_generation_chain()
    
    # Generate with retry logic
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Invoke chain
            formatted_prompt = prompt.format(**prompt_vars)
            result = chain.invoke(formatted_prompt)
            
            # Validate result
            if isinstance(result, CreditAgreement):
                # Additional validation
                _validate_generated_cdm(result)
                return result
            else:
                # Convert dict to CreditAgreement if needed
                result = CreditAgreement(**result)
                _validate_generated_cdm(result)
                return result
                
        except ValidationError as e:
            last_error = e
            logger.warning(f"Validation error on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                # Retry with different seed
                if seed is not None:
                    random.seed(seed + attempt + 1)
                continue
        except Exception as e:
            last_error = e
            logger.error(f"Error generating deal on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                continue
    
    # If all retries failed, raise error
    raise RuntimeError(
        f"Failed to generate valid CreditAgreement after {max_retries} attempts. "
        f"Last error: {last_error}"
    )


def _validate_generated_cdm(cdm: CreditAgreement) -> None:
    """
    Validate that generated CDM has all required fields.
    
    Args:
        cdm: CreditAgreement to validate
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    errors = []
    
    # Check required fields
    if not cdm.parties:
        errors.append("Missing parties")
    else:
        borrower = next((p for p in cdm.parties if p.role == "Borrower"), None)
        if not borrower:
            errors.append("Missing Borrower party")
        elif not borrower.name:
            errors.append("Borrower missing name")
        elif not borrower.lei:
            errors.append("Borrower missing LEI")
        elif len(borrower.lei) != 20:
            errors.append(f"Borrower LEI must be 20 characters, got {len(borrower.lei)}")
    
    if not cdm.facilities:
        errors.append("Missing facilities")
    else:
        facility = cdm.facilities[0]
        if not facility.facility_name:
            errors.append("Facility missing name")
        if not facility.commitment_amount:
            errors.append("Facility missing commitment_amount")
        elif facility.commitment_amount.amount <= 0:
            errors.append("Facility commitment_amount must be positive")
        if not facility.maturity_date:
            errors.append("Facility missing maturity_date")
        if not facility.interest_terms:
            errors.append("Facility missing interest_terms")
        elif not facility.interest_terms.rate_option:
            errors.append("Facility missing rate_option")
        elif not facility.interest_terms.rate_option.benchmark:
            errors.append("Facility missing benchmark")
    
    if not cdm.agreement_date:
        errors.append("Missing agreement_date")
    elif cdm.agreement_date > date.today():
        errors.append("agreement_date must be in the past")
    
    if not cdm.governing_law:
        errors.append("Missing governing_law")
    
    # Validate date relationships
    if cdm.agreement_date and cdm.facilities:
        for facility in cdm.facilities:
            if facility.maturity_date and facility.maturity_date <= cdm.agreement_date:
                errors.append(f"Facility {facility.facility_name} maturity_date must be after agreement_date")
    
    if errors:
        raise ValueError(f"CDM validation failed: {', '.join(errors)}")


def generate_lei() -> str:
    """
    Generate a realistic LEI (Legal Entity Identifier).
    
    Format: 20 alphanumeric characters, uppercase
    
    Returns:
        20-character alphanumeric LEI string
    """
    import string
    chars = string.ascii_uppercase + string.digits
    # Start with common LEI prefix pattern (4 digits, 2 letters)
    prefix = ''.join(random.choices(string.digits, k=4)) + ''.join(random.choices(string.ascii_uppercase, k=2))
    # Rest is random alphanumeric
    suffix = ''.join(random.choices(chars, k=14))
    return prefix + suffix


def generate_company_name(industry: str) -> str:
    """
    Generate a realistic company name for the given industry.
    
    Args:
        industry: Industry sector
        
    Returns:
        Company name string
    """
    suffixes = ["Corp", "Corporation", "LLC", "Inc", "Ltd", "Group", "Holdings", "Partners"]
    industry_words = {
        "Technology": ["Tech", "Digital", "Software", "Systems", "Solutions", "Innovations"],
        "Manufacturing": ["Manufacturing", "Industries", "Production", "Works", "Fabrication"],
        "Energy": ["Energy", "Power", "Utilities", "Resources", "Renewables"],
        "Healthcare": ["Health", "Medical", "Care", "Wellness", "Pharmaceuticals"],
        "Agriculture": ["Farms", "Agriculture", "Crops", "Harvest", "Agri"],
        "Real Estate": ["Properties", "Realty", "Developments", "Estates", "Homes"],
        "Retail": ["Retail", "Stores", "Commerce", "Merchants", "Trading"]
    }
    
    words = industry_words.get(industry, ["Business", "Enterprises", "Ventures"])
    word = random.choice(words)
    suffix = random.choice(suffixes)
    
    # Add location or descriptive prefix
    locations = ["Pacific", "Global", "National", "United", "American", "International", "Continental"]
    prefix = random.choice(locations)
    
    return f"{prefix} {word} {suffix}"

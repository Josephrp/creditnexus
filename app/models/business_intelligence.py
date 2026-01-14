"""Business Intelligence models for PeopleHub research and psychometric analysis.

These models define the schema for individual and business profiling,
psychometric analysis, and audit reports, ensuring CDM compliance.
"""

from decimal import Decimal
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator


class RiskTolerance(str, Enum):
    """Risk tolerance levels."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class DecisionMakingStyle(str, Enum):
    """Decision-making styles."""
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    COLLABORATIVE = "collaborative"
    INDEPENDENT = "independent"


class ImpulseBuyingTendency(str, Enum):
    """Impulse buying tendency levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class BigFiveTraits(BaseModel):
    """Big Five personality traits (0.0-1.0 scale)."""
    openness: float = Field(..., ge=0.0, le=1.0, description="Openness to Experience")
    conscientiousness: float = Field(..., ge=0.0, le=1.0, description="Conscientiousness")
    extraversion: float = Field(..., ge=0.0, le=1.0, description="Extraversion")
    agreeableness: float = Field(..., ge=0.0, le=1.0, description="Agreeableness")
    neuroticism: float = Field(..., ge=0.0, le=1.0, description="Neuroticism")


class BuyingBehaviorProfile(BaseModel):
    """Buying behavior profile."""
    purchase_frequency: Optional[str] = Field(None, description="How often they make significant purchases")
    average_transaction_value: Optional[Decimal] = Field(None, description="Typical spending amount")
    preferred_categories: Optional[List[str]] = Field(None, description="Types of products/services they buy")
    decision_factors: Optional[List[str]] = Field(None, description="Price, quality, brand, convenience, etc.")
    impulse_buying_tendency: Optional[ImpulseBuyingTendency] = Field(None, description="Impulse buying tendency")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in this assessment")


class SavingsBehaviorProfile(BaseModel):
    """Savings behavior profile."""
    savings_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Percentage of income saved (0.0-1.0)")
    investment_preferences: Optional[List[str]] = Field(None, description="Stocks, bonds, real estate, crypto, etc.")
    financial_goals: Optional[List[str]] = Field(None, description="Short-term, medium-term, long-term goals")
    emergency_fund: Optional[str] = Field(None, description="Likely presence and adequacy")
    retirement_planning: Optional[str] = Field(None, description="Engagement level")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in this assessment")


class PsychometricProfile(BaseModel):
    """Psychometric profile with Big Five traits and behaviors."""
    big_five_traits: Optional[BigFiveTraits] = Field(None, description="Big Five personality traits")
    risk_tolerance: Optional[RiskTolerance] = Field(None, description="Risk tolerance level")
    decision_making_style: Optional[DecisionMakingStyle] = Field(None, description="Decision-making style")
    buying_behavior: Optional[BuyingBehaviorProfile] = Field(None, description="Buying behavior profile")
    savings_behavior: Optional[SavingsBehaviorProfile] = Field(None, description="Savings behavior profile")
    overall_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence in analysis")
    
    # Convenience properties for backward compatibility
    @property
    def conscientiousness(self) -> Optional[float]:
        """Get conscientiousness score for convenience."""
        if self.big_five_traits:
            return self.big_five_traits.conscientiousness
        return None


class CreditCheckData(BaseModel):
    """Credit check relevant data extracted from profiles."""
    payment_history_indicators: Optional[str] = Field(None, description="Based on professional reliability")
    credit_utilization_patterns: Optional[str] = Field(None, description="Inferred from spending behavior")
    debt_management: Optional[str] = Field(None, description="Likely approach to debt")
    financial_stability: Optional[str] = Field(None, description="Job stability, income growth trajectory")
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall risk score (0.0 = low risk, 1.0 = high risk)")


class IndividualProfile(BaseModel):
    """Individual profile for business intelligence."""
    person_name: str = Field(..., description="Full name of the individual")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    profile_data: Optional[Dict[str, Any]] = Field(None, description="LinkedIn data, web summaries, research report")
    deal_id: Optional[int] = Field(None, description="Associated deal ID")
    created_at: Optional[datetime] = Field(None, description="Profile creation timestamp")
    
    @model_validator(mode='after')
    def validate_profile_data(self) -> 'IndividualProfile':
        """Validate that profile has meaningful data."""
        if not self.profile_data and not self.linkedin_url:
            raise ValueError("Profile must have either profile_data or linkedin_url")
        return self


class BusinessProfile(BaseModel):
    """Business profile for business intelligence."""
    business_name: str = Field(..., description="Legal name of the business")
    business_lei: Optional[str] = Field(None, description="Legal Entity Identifier")
    business_type: Optional[str] = Field(None, description="Type of business (corporation, LLC, etc.)")
    industry: Optional[str] = Field(None, description="Industry sector")
    profile_data: Optional[Dict[str, Any]] = Field(None, description="Business research data")
    deal_id: Optional[int] = Field(None, description="Associated deal ID")
    created_at: Optional[datetime] = Field(None, description="Profile creation timestamp")


class AuditReport(BaseModel):
    """Audit report for business intelligence."""
    report_type: str = Field(..., description="Type of report (individual, business)")
    profile_id: Optional[int] = Field(None, description="Associated profile ID")
    report_data: Optional[Dict[str, Any]] = Field(None, description="Report content including research, psychometric data, credit check")
    deal_id: Optional[int] = Field(None, description="Associated deal ID")
    created_at: Optional[datetime] = Field(None, description="Report creation timestamp")
    
    @model_validator(mode='after')
    def validate_report_type(self) -> 'AuditReport':
        """Validate report type."""
        if self.report_type not in ["individual", "business"]:
            raise ValueError("report_type must be 'individual' or 'business'")
        return self

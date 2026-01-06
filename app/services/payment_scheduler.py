"""
Payment Scheduler for Periodic Interest Payments.

Schedules and processes interest payments using x402.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import logging

from app.models.cdm import CreditAgreement, Frequency, PeriodEnum
from app.services.x402_payment_service import X402PaymentService

logger = logging.getLogger(__name__)


class PaymentScheduler:
    """Schedules periodic payments for loans."""
    
    def __init__(self, payment_service: X402PaymentService):
        """
        Initialize payment scheduler.
        
        Args:
            payment_service: x402 payment service instance
        """
        self.payment_service = payment_service
    
    async def schedule_interest_payment(
        self,
        credit_agreement: CreditAgreement,
        loan_asset_id: str
    ) -> Dict[str, Any]:
        """
        Schedule interest payment based on payment frequency.
        
        Args:
            credit_agreement: CDM CreditAgreement
            loan_asset_id: Loan asset identifier
            
        Returns:
            Payment schedule information
        """
        if not credit_agreement.facilities:
            logger.warning(f"No facilities found in credit agreement for loan {loan_asset_id}")
            return {"status": "error", "message": "No facilities found"}
        
        facility = credit_agreement.facilities[0]
        
        # Get payment frequency from facility
        payment_frequency = None
        if facility.interest_terms and facility.interest_terms.payment_frequency:
            payment_frequency = facility.interest_terms.payment_frequency
        else:
            # Default to monthly payments
            payment_frequency = Frequency(period=PeriodEnum.Month, period_multiplier=1)
        
        # Calculate next payment date
        next_payment_date = self._calculate_next_payment_date(payment_frequency)
        
        # Calculate interest amount
        interest_amount = self._calculate_interest_amount(
            credit_agreement,
            facility
        )
        
        # Schedule payment
        schedule_info = await self._create_payment_schedule(
            loan_asset_id=loan_asset_id,
            credit_agreement=credit_agreement,
            amount=interest_amount,
            payment_date=next_payment_date,
            payment_type="interest"
        )
        
        return {
            "status": "scheduled",
            "loan_asset_id": loan_asset_id,
            "amount": str(interest_amount),
            "currency": facility.commitment_amount.currency.value if facility.commitment_amount else "USD",
            "payment_date": next_payment_date.isoformat(),
            "payment_frequency": {
                "period": payment_frequency.period.value,
                "period_multiplier": payment_frequency.period_multiplier
            },
            "schedule_id": schedule_info.get("schedule_id")
        }
    
    def _calculate_next_payment_date(self, frequency: Frequency) -> datetime:
        """
        Calculate next payment date based on frequency.
        
        Args:
            frequency: Payment frequency from CDM
            
        Returns:
            Next payment date
        """
        period_days = {
            PeriodEnum.Day: 1,
            PeriodEnum.Week: 7,
            PeriodEnum.Month: 30,
            PeriodEnum.Year: 365
        }
        
        days = period_days.get(frequency.period, 30) * frequency.period_multiplier
        return datetime.utcnow() + timedelta(days=days)
    
    def _calculate_interest_amount(
        self,
        credit_agreement: CreditAgreement,
        facility
    ) -> Decimal:
        """
        Calculate interest amount based on current rate.
        
        Args:
            credit_agreement: CDM CreditAgreement
            facility: Loan facility
            
        Returns:
            Interest amount as Decimal
        """
        # Get current interest rate
        # In production, this would query the loan asset for current_interest_rate
        # For now, use base rate from facility
        if facility.interest_terms and facility.interest_terms.rate_option:
            spread_bps = facility.interest_terms.rate_option.spread_bps or 0
            base_rate = spread_bps / 10000  # Convert basis points to decimal
        else:
            base_rate = 0.05  # Default 5%
        
        # Get principal from commitment amount
        if facility.commitment_amount:
            principal = float(facility.commitment_amount.amount)
        else:
            principal = 0.0
        
        # Simple interest calculation (would be more complex in production)
        # For periodic payments, calculate interest for one period
        if facility.interest_terms and facility.interest_terms.payment_frequency:
            freq = facility.interest_terms.payment_frequency
            period_days = {
                PeriodEnum.Day: 1,
                PeriodEnum.Week: 7,
                PeriodEnum.Month: 30,
                PeriodEnum.Year: 365
            }
            days = period_days.get(freq.period, 30) * freq.period_multiplier
            # Calculate interest for the period: principal * rate * (days/365)
            interest = Decimal(str(principal * base_rate * (days / 365)))
        else:
            # Default monthly calculation
            interest = Decimal(str(principal * base_rate * (30 / 365)))
        
        return interest
    
    async def _create_payment_schedule(
        self,
        loan_asset_id: str,
        credit_agreement: CreditAgreement,
        amount: Decimal,
        payment_date: datetime,
        payment_type: str
    ) -> Dict[str, Any]:
        """
        Create payment schedule record in database.
        
        Args:
            loan_asset_id: Loan asset identifier
            credit_agreement: CDM CreditAgreement
            amount: Payment amount
            payment_date: Scheduled payment date
            payment_type: Type of payment (interest, principal, etc.)
            
        Returns:
            Schedule information
        """
        # In production, this would create a PaymentSchedule record in the database
        # For now, return schedule information
        schedule_id = f"schedule_{loan_asset_id}_{payment_date.isoformat()}"
        
        logger.info(
            f"Scheduled {payment_type} payment: "
            f"loan_asset_id={loan_asset_id}, "
            f"amount={amount}, "
            f"date={payment_date.isoformat()}"
        )
        
        return {
            "schedule_id": schedule_id,
            "loan_asset_id": loan_asset_id,
            "amount": str(amount),
            "payment_date": payment_date.isoformat(),
            "payment_type": payment_type,
            "status": "pending"
        }








"""
Companies House API client for UK regulatory filings.

This service handles authentication, request formatting, and response parsing
for the UK Companies House API (charge filings).
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import requests

from app.models.cdm import CreditAgreement
from app.services.policy_service import FilingRequirement as PolicyFilingRequirement
from app.services.filing_service import FilingAPIError
from app.core.config import settings
from app.utils.rate_limiter import COMPANIES_HOUSE_LIMITER

logger = logging.getLogger(__name__)


class CompaniesHouseAPIClient:
    """Client for Companies House API integration."""
    
    BASE_URL = "https://api.company-information.service.gov.uk"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Companies House API client.
        
        Args:
            api_key: API key (defaults to settings.COMPANIES_HOUSE_API_KEY)
        """
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            raise ValueError("Companies House API key not configured")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from settings.
        
        Returns:
            API key string or None if not configured
        """
        try:
            api_key = getattr(settings, 'COMPANIES_HOUSE_API_KEY', None)
            if api_key and hasattr(api_key, 'get_secret_value'):
                return api_key.get_secret_value()
            return api_key
        except Exception as e:
            logger.warning(f"Could not get Companies House API key: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication.
        
        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _extract_company_number(self, credit_agreement: CreditAgreement) -> str:
        """Extract UK company number from credit agreement.
        
        Args:
            credit_agreement: CreditAgreement instance
            
        Returns:
            Company number string
            
        Raises:
            FilingAPIError: If company number cannot be extracted
        """
        # Try to find borrower party with company number
        for party in credit_agreement.parties:
            if party.role == "Borrower":
                # Company number might be in party metadata or name
                # This is a simplified extraction - in production, would check
                # party.company_number field or extract from party metadata
                if hasattr(party, 'company_number') and party.company_number:
                    return party.company_number
                # Fallback to LEI or ID (not ideal, but works for testing)
                return party.lei or party.id
        
        raise FilingAPIError("Could not extract UK company number from credit agreement")
    
    def _format_charge_payload(
        self,
        credit_agreement: CreditAgreement,
        company_number: str
    ) -> Dict[str, Any]:
        """Format charge filing payload for Companies House API.
        
        Args:
            credit_agreement: CreditAgreement instance
            company_number: UK company number
            
        Returns:
            Formatted payload dictionary
        """
        # Extract lenders
        persons_entitled = [
            p.name for p in credit_agreement.parties 
            if p.role == "Lender"
        ]
        
        # Extract amount and currency
        amount_secured = None
        currency = "GBP"
        if credit_agreement.total_commitment:
            amount_secured = str(credit_agreement.total_commitment.amount)
            currency = credit_agreement.total_commitment.currency.value
        
        # Format payload according to Companies House MR01 form
        payload = {
            "charge_code": "MR01",
            "company_number": company_number,
            "charge_creation_date": (
                credit_agreement.agreement_date.isoformat() 
                if credit_agreement.agreement_date else None
            ),
            "persons_entitled": persons_entitled,
            "amount_secured": amount_secured,
            "currency": currency,
            "charge_description": (
                f"Credit facility agreement dated {credit_agreement.agreement_date.isoformat()}"
                if credit_agreement.agreement_date else "Credit facility agreement"
            )
        }
        
        return payload
    
    def submit_charge(
        self,
        credit_agreement: CreditAgreement,
        filing_requirement: Optional[PolicyFilingRequirement] = None
    ) -> Dict[str, Any]:
        """Submit a charge filing to Companies House.
        
        Args:
            credit_agreement: CreditAgreement instance
            filing_requirement: Optional filing requirement (for context)
            
        Returns:
            Dictionary with filing results:
            - filing_reference: External filing reference
            - filing_url: URL to view filing
            - confirmation_url: Confirmation/receipt URL
            - status: Submission status
            - submitted_at: ISO timestamp
            
        Raises:
            FilingAPIError: If API submission fails
        """
        try:
            # Extract company number
            company_number = self._extract_company_number(credit_agreement)
            
            # Format payload
            payload = self._format_charge_payload(credit_agreement, company_number)
            
            # Build API URL
            api_url = f"{self.BASE_URL}/company/{company_number}/charges"
            
            # Apply rate limiting
            COMPANIES_HOUSE_LIMITER.wait_if_needed()
            
            # Make API request
            logger.info(f"Submitting charge filing to Companies House for company {company_number}")
            response = requests.post(
                api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Format return value
            return {
                "filing_reference": (
                    result.get("filing_reference") or 
                    result.get("transaction_id") or
                    result.get("id")
                ),
                "filing_url": result.get("filing_url") or result.get("links", {}).get("self"),
                "confirmation_url": result.get("confirmation_url") or result.get("links", {}).get("filing"),
                "status": "submitted",
                "submitted_at": datetime.utcnow().isoformat(),
                "raw_response": result
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Companies House API error: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - Status: {e.response.status_code}"
            
            logger.error(error_msg)
            raise FilingAPIError(error_msg) from e
        except Exception as e:
            logger.error(f"Unexpected error submitting to Companies House: {e}")
            raise FilingAPIError(f"Failed to submit to Companies House: {e}") from e
    
    def get_filing_status(
        self,
        company_number: str,
        filing_reference: str
    ) -> Dict[str, Any]:
        """Get status of a previously submitted filing.
        
        Args:
            company_number: UK company number
            filing_reference: Filing reference from submission
            
        Returns:
            Dictionary with filing status information
            
        Raises:
            FilingAPIError: If API request fails
        """
        try:
            api_url = f"{self.BASE_URL}/company/{company_number}/charges/{filing_reference}"
            
            # Apply rate limiting
            COMPANIES_HOUSE_LIMITER.wait_if_needed()
            
            response = requests.get(
                api_url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Companies House API error getting filing status: {e}"
            logger.error(error_msg)
            raise FilingAPIError(error_msg) from e

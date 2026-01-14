"""
Background service for polling filing status from regulatory APIs.

This service periodically checks the status of API-enabled filings (e.g., Companies House)
and updates their status in the database when they are accepted or rejected.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.db.models import DocumentFiling
from app.services.companies_house_client import CompaniesHouseAPIClient
from app.services.filing_service import FilingError
from app.models.cdm import CreditAgreement

logger = logging.getLogger(__name__)


class FilingPollingService:
    """Service for polling filing status from regulatory APIs."""
    
    def __init__(self, db: Session):
        """Initialize filing polling service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def poll_filing_status(
        self,
        filing_id: int
    ) -> Dict[str, Any]:
        """Poll status for a single filing.
        
        Args:
            filing_id: Filing ID to poll
            
        Returns:
            Dictionary with polling results:
            - status_updated: bool - Whether status was updated
            - new_status: str - New status if updated
            - error: str - Error message if polling failed
        """
        filing = self.db.query(DocumentFiling).filter(DocumentFiling.id == filing_id).first()
        if not filing:
            return {
                "status_updated": False,
                "error": f"Filing {filing_id} not found"
            }
        
        # Only poll API-enabled filings that are submitted but not yet accepted/rejected
        if filing.filing_system not in ["companies_house_api"]:
            return {
                "status_updated": False,
                "error": f"Filing system {filing.filing_system} does not support status polling"
            }
        
        if filing.filing_status not in ["submitted", "pending"]:
            return {
                "status_updated": False,
                "error": f"Filing status {filing.filing_status} does not require polling"
            }
        
        if not filing.filing_reference:
            return {
                "status_updated": False,
                "error": "Filing reference not available for polling"
            }
        
        try:
            # Poll based on filing system
            if filing.filing_system == "companies_house_api":
                return self._poll_companies_house_status(filing)
            else:
                return {
                    "status_updated": False,
                    "error": f"Polling not implemented for {filing.filing_system}"
                }
        except Exception as e:
            logger.error(f"Error polling filing {filing_id}: {e}", exc_info=True)
            return {
                "status_updated": False,
                "error": str(e)
            }
    
    def _poll_companies_house_status(
        self,
        filing: DocumentFiling
    ) -> Dict[str, Any]:
        """Poll Companies House filing status.
        
        Args:
            filing: DocumentFiling instance
            
        Returns:
            Dictionary with polling results
        """
        try:
            # Get company number from filing or document
            # For Companies House, we need the company number
            company_number = None
            
            # Try to extract from filing_payload or filing_response
            if filing.filing_response:
                company_number = filing.filing_response.get("company_number")
            
            if not company_number:
                # Try to get from document's CDM data
                from app.services.filing_service import FilingService
                filing_service = FilingService(self.db)
                try:
                    credit_agreement = filing_service._get_credit_agreement_from_document(filing.document_id)
                    if credit_agreement:
                        # Extract company number using the client's method
                        client = CompaniesHouseAPIClient()
                        company_number = client._extract_company_number(credit_agreement)
                except Exception as e:
                    logger.warning(f"Could not extract company number: {e}")
            
            if not company_number:
                return {
                    "status_updated": False,
                    "error": "Company number not available for polling"
                }
            
            # Poll Companies House API
            client = CompaniesHouseAPIClient()
            status_data = client.get_filing_status(
                company_number=company_number,
                filing_reference=filing.filing_reference
            )
            
            # Parse status from response
            # Companies House API response structure may vary
            new_status = None
            if status_data.get("status") == "accepted" or status_data.get("accepted"):
                new_status = "accepted"
            elif status_data.get("status") == "rejected" or status_data.get("rejected"):
                new_status = "rejected"
            elif status_data.get("status") == "pending":
                new_status = "submitted"  # Keep as submitted if still pending
            
            if new_status and new_status != filing.filing_status:
                # Update filing status
                old_status = filing.filing_status
                filing.filing_status = new_status
                filing.filing_response = status_data
                filing.updated_at = datetime.utcnow()
                
                # Set filed_at if accepted
                if new_status == "accepted":
                    filing.filed_at = datetime.utcnow()
                
                self.db.commit()
                
                logger.info(
                    f"Updated filing {filing.id} status from {old_status} to {new_status}"
                )
                
                return {
                    "status_updated": True,
                    "new_status": new_status,
                    "old_status": old_status,
                    "filing_id": filing.id
                }
            else:
                return {
                    "status_updated": False,
                    "current_status": filing.filing_status,
                    "message": "Status unchanged"
                }
                
        except Exception as e:
            logger.error(f"Error polling Companies House status: {e}", exc_info=True)
            raise
    
    def poll_all_pending_filings(
        self,
        max_age_hours: int = 24,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Poll all pending API-enabled filings.
        
        Args:
            max_age_hours: Only poll filings submitted within this many hours (default: 24)
            limit: Maximum number of filings to poll (None for all)
            
        Returns:
            Dictionary with polling results:
            - polled: int - Number of filings polled
            - updated: int - Number of filings with status updates
            - failed: int - Number of polling failures
            - results: List[Dict] - Detailed results for each filing
        """
        # Query for pending API-enabled filings
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        query = self.db.query(DocumentFiling).filter(
            DocumentFiling.filing_system.in_(["companies_house_api"]),
            DocumentFiling.filing_status.in_(["submitted", "pending"]),
            DocumentFiling.filed_at >= cutoff_time,
            DocumentFiling.filing_reference.isnot(None)
        )
        
        if limit:
            query = query.limit(limit)
        
        filings = query.all()
        
        if not filings:
            return {
                "polled": 0,
                "updated": 0,
                "failed": 0,
                "results": []
            }
        
        polled = 0
        updated = 0
        failed = 0
        results = []
        
        for filing in filings:
            try:
                result = self.poll_filing_status(filing.id)
                polled += 1
                
                if result.get("status_updated"):
                    updated += 1
                elif result.get("error"):
                    failed += 1
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error polling filing {filing.id}: {e}")
                failed += 1
                results.append({
                    "filing_id": filing.id,
                    "status_updated": False,
                    "error": str(e)
                })
        
        logger.info(
            f"Polled {polled} filings: {updated} updated, {failed} failed"
        )
        
        return {
            "polled": polled,
            "updated": updated,
            "failed": failed,
            "results": results
        }
    
    def poll_filings_by_deal(
        self,
        deal_id: int
    ) -> Dict[str, Any]:
        """Poll all pending filings for a specific deal.
        
        Args:
            deal_id: Deal ID
            
        Returns:
            Dictionary with polling results
        """
        filings = self.db.query(DocumentFiling).filter(
            DocumentFiling.deal_id == deal_id,
            DocumentFiling.filing_system.in_(["companies_house_api"]),
            DocumentFiling.filing_status.in_(["submitted", "pending"]),
            DocumentFiling.filing_reference.isnot(None)
        ).all()
        
        if not filings:
            return {
                "polled": 0,
                "updated": 0,
                "failed": 0,
                "results": []
            }
        
        polled = 0
        updated = 0
        failed = 0
        results = []
        
        for filing in filings:
            try:
                result = self.poll_filing_status(filing.id)
                polled += 1
                
                if result.get("status_updated"):
                    updated += 1
                elif result.get("error"):
                    failed += 1
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error polling filing {filing.id}: {e}")
                failed += 1
                results.append({
                    "filing_id": filing.id,
                    "status_updated": False,
                    "error": str(e)
                })
        
        return {
            "polled": polled,
            "updated": updated,
            "failed": failed,
            "results": results
        }

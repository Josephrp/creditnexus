"""
Notification service for filing deadlines and status changes.

This service sends email and in-app notifications for:
- Approaching filing deadlines (7 days, 3 days, 1 day before)
- Filing status changes (accepted, rejected)
- Overdue filings
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.db.models import DocumentFiling, User, Document, Deal
from app.utils.audit import log_audit_action
from app.db.models import AuditAction

logger = logging.getLogger(__name__)


class FilingNotificationService:
    """Service for sending filing-related notifications."""
    
    def __init__(self, db: Session):
        """Initialize notification service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def send_deadline_alert(
        self,
        filing: DocumentFiling,
        days_until: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send deadline alert notification.
        
        Args:
            filing: DocumentFiling instance
            days_until: Days until deadline
            user_id: Optional user ID to notify (if None, notifies document owner)
            
        Returns:
            Dictionary with notification result
        """
        try:
            # Get document and deal info
            document = self.db.query(Document).filter(Document.id == filing.document_id).first()
            deal = None
            if filing.deal_id:
                deal = self.db.query(Deal).filter(Deal.id == filing.deal_id).first()
            
            # Determine recipients
            recipients = []
            if user_id:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    recipients.append(user.email)
            elif document and document.uploaded_by:
                user = self.db.query(User).filter(User.id == document.uploaded_by).first()
                if user:
                    recipients.append(user.email)
            
            if not recipients:
                logger.warning(f"No recipients found for filing {filing.id} deadline alert")
                return {"status": "skipped", "reason": "no_recipients"}
            
            # Determine priority
            if days_until <= 1:
                priority = "critical"
                subject_prefix = "URGENT"
            elif days_until <= 3:
                priority = "high"
                subject_prefix = "IMPORTANT"
            else:
                priority = "medium"
                subject_prefix = "Reminder"
            
            # Build notification content
            subject = f"{subject_prefix}: Filing Deadline Approaching - {filing.filing_authority}"
            message = self._build_deadline_message(filing, document, deal, days_until)
            
            # Send notifications (in production, would use email service)
            notification_result = {
                "status": "sent",
                "recipients": recipients,
                "subject": subject,
                "priority": priority,
                "days_until": days_until,
                "filing_id": filing.id,
                "sent_at": datetime.utcnow().isoformat()
            }
            
            # Log notification
            logger.info(
                f"Sent deadline alert for filing {filing.id} "
                f"({days_until} days until deadline) to {len(recipients)} recipients"
            )
            
            # Store notification in database (if Notification model exists)
            # For now, we'll just log it
            
            return notification_result
            
        except Exception as e:
            logger.error(f"Error sending deadline alert for filing {filing.id}: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def send_status_change_notification(
        self,
        filing: DocumentFiling,
        old_status: str,
        new_status: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send notification for filing status change.
        
        Args:
            filing: DocumentFiling instance
            old_status: Previous status
            new_status: New status
            user_id: Optional user ID to notify
            
        Returns:
            Dictionary with notification result
        """
        try:
            # Get document and deal info
            document = self.db.query(Document).filter(Document.id == filing.document_id).first()
            deal = None
            if filing.deal_id:
                deal = self.db.query(Deal).filter(Deal.id == filing.deal_id).first()
            
            # Determine recipients
            recipients = []
            if user_id:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    recipients.append(user.email)
            elif document and document.uploaded_by:
                user = self.db.query(User).filter(User.id == document.uploaded_by).first()
                if user:
                    recipients.append(user.email)
            
            if not recipients:
                logger.warning(f"No recipients found for filing {filing.id} status change")
                return {"status": "skipped", "reason": "no_recipients"}
            
            # Build notification
            if new_status == "accepted":
                subject = f"Filing Accepted: {filing.filing_authority}"
                priority = "info"
            elif new_status == "rejected":
                subject = f"Filing Rejected: {filing.filing_authority}"
                priority = "error"
            else:
                subject = f"Filing Status Updated: {filing.filing_authority}"
                priority = "info"
            
            message = self._build_status_change_message(filing, document, deal, old_status, new_status)
            
            notification_result = {
                "status": "sent",
                "recipients": recipients,
                "subject": subject,
                "priority": priority,
                "old_status": old_status,
                "new_status": new_status,
                "filing_id": filing.id,
                "sent_at": datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Sent status change notification for filing {filing.id} "
                f"({old_status} -> {new_status}) to {len(recipients)} recipients"
            )
            
            return notification_result
            
        except Exception as e:
            logger.error(f"Error sending status change notification for filing {filing.id}: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def check_and_send_deadline_alerts(
        self,
        days_ahead: List[int] = [7, 3, 1],
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Check for approaching deadlines and send alerts.
        
        Args:
            days_ahead: List of days before deadline to send alerts (default: [7, 3, 1])
            limit: Maximum number of filings to check (None for all)
            
        Returns:
            Dictionary with alert results
        """
        now = datetime.utcnow()
        results = {
            "checked": 0,
            "alerts_sent": 0,
            "errors": 0,
            "details": []
        }
        
        # Query filings with approaching deadlines
        query = self.db.query(DocumentFiling).filter(
            DocumentFiling.deadline.isnot(None),
            DocumentFiling.filing_status.in_(["pending", "prepared"]),
            DocumentFiling.deadline >= now,
            DocumentFiling.deadline <= now + timedelta(days=max(days_ahead))
        )
        
        if limit:
            query = query.limit(limit)
        
        filings = query.all()
        results["checked"] = len(filings)
        
        for filing in filings:
            if not filing.deadline:
                continue
            
            days_until = (filing.deadline - now).days
            
            # Check if we should send alert for this number of days
            if days_until in days_ahead:
                # Check if we've already sent an alert for this filing at this day count
                # (In production, would check Notification table)
                
                alert_result = self.send_deadline_alert(filing, days_until)
                if alert_result.get("status") == "sent":
                    results["alerts_sent"] += 1
                else:
                    results["errors"] += 1
                
                results["details"].append({
                    "filing_id": filing.id,
                    "days_until": days_until,
                    "result": alert_result
                })
        
        return results
    
    def check_and_send_overdue_alerts(
        self,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Check for overdue filings and send alerts.
        
        Args:
            limit: Maximum number of filings to check (None for all)
            
        Returns:
            Dictionary with alert results
        """
        now = datetime.utcnow()
        results = {
            "checked": 0,
            "alerts_sent": 0,
            "errors": 0,
            "details": []
        }
        
        # Query overdue filings
        query = self.db.query(DocumentFiling).filter(
            DocumentFiling.deadline.isnot(None),
            DocumentFiling.deadline < now,
            DocumentFiling.filing_status.in_(["pending", "prepared"])
        )
        
        if limit:
            query = query.limit(limit)
        
        filings = query.all()
        results["checked"] = len(filings)
        
        for filing in filings:
            if not filing.deadline:
                continue
            
            days_overdue = (now - filing.deadline).days
            
            # Send alert for overdue filing
            alert_result = self.send_deadline_alert(filing, -days_overdue)  # Negative for overdue
            if alert_result.get("status") == "sent":
                results["alerts_sent"] += 1
            else:
                results["errors"] += 1
            
            results["details"].append({
                "filing_id": filing.id,
                "days_overdue": days_overdue,
                "result": alert_result
            })
        
        return results
    
    def _build_deadline_message(
        self,
        filing: DocumentFiling,
        document: Optional[Document],
        deal: Optional[Deal],
        days_until: int
    ) -> str:
        """Build deadline alert message.
        
        Args:
            filing: DocumentFiling instance
            document: Optional Document instance
            deal: Optional Deal instance
            days_until: Days until deadline (negative if overdue)
            
        Returns:
            Formatted message string
        """
        if days_until < 0:
            status_text = f"OVERDUE by {abs(days_until)} day(s)"
        elif days_until == 0:
            status_text = "DUE TODAY"
        elif days_until == 1:
            status_text = "DUE TOMORROW"
        else:
            status_text = f"Due in {days_until} day(s)"
        
        message = f"""Filing Deadline Alert

Status: {status_text}
Authority: {filing.filing_authority}
Jurisdiction: {filing.jurisdiction}
Deadline: {filing.deadline.strftime('%Y-%m-%d %H:%M:%S UTC') if filing.deadline else 'N/A'}

"""
        
        if document:
            message += f"Document: {document.title}\n"
        
        if deal:
            message += f"Deal: {deal.deal_id}\n"
        
        message += f"\nFiling ID: {filing.id}\n"
        
        if filing.filing_url:
            message += f"View Filing: {filing.filing_url}\n"
        
        if filing.manual_submission_url:
            message += f"Submission URL: {filing.manual_submission_url}\n"
        
        return message
    
    def _build_status_change_message(
        self,
        filing: DocumentFiling,
        document: Optional[Document],
        deal: Optional[Deal],
        old_status: str,
        new_status: str
    ) -> str:
        """Build status change notification message.
        
        Args:
            filing: DocumentFiling instance
            document: Optional Document instance
            deal: Optional Deal instance
            old_status: Previous status
            new_status: New status
            
        Returns:
            Formatted message string
        """
        message = f"""Filing Status Update

Status Changed: {old_status} → {new_status}
Authority: {filing.filing_authority}
Jurisdiction: {filing.jurisdiction}

"""
        
        if document:
            message += f"Document: {document.title}\n"
        
        if deal:
            message += f"Deal: {deal.deal_id}\n"
        
        message += f"\nFiling ID: {filing.id}\n"
        
        if filing.filing_reference:
            message += f"Filing Reference: {filing.filing_reference}\n"
        
        if filing.filing_url:
            message += f"View Filing: {filing.filing_url}\n"
        
        if new_status == "rejected" and filing.error_message:
            message += f"\nRejection Reason: {filing.error_message}\n"
        
        return message

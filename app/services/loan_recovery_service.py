"""
Loan Recovery Service for detecting defaults and managing recovery actions.

This service handles:
- Payment default detection
- Covenant breach detection
- Recovery action triggering and execution
- Automated communication workflows
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.models import (
    LoanDefault, RecoveryAction, BorrowerContact, Deal, LoanAsset, 
    PaymentEvent, User
)
from app.models.cdm_events import generate_cdm_loan_default, generate_cdm_recovery_action
from app.services.twilio_service import TwilioService
from app.services.recovery_template_service import RecoveryTemplateService

logger = logging.getLogger(__name__)


class LoanRecoveryService:
    """Service for managing loan recovery workflows."""
    
    def __init__(self, db: Session):
        """
        Initialize loan recovery service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.twilio_service = TwilioService()
        self.template_service = RecoveryTemplateService()
    
    def detect_payment_defaults(self, deal_id: Optional[int] = None) -> List[LoanDefault]:
        """
        Detect payment defaults from overdue PaymentEvent records.
        
        Args:
            deal_id: Optional deal ID to filter by
            
        Returns:
            List of detected LoanDefault records
        """
        defaults = []
        now = datetime.utcnow()
        
        try:
            # Query PaymentEvent for pending payments that are overdue
            # Note: PaymentEvent doesn't have scheduled_date, so we'll use created_at + expected_days
            # In production, you'd have a PaymentSchedule table with scheduled_date
            query = self.db.query(PaymentEvent).filter(
                PaymentEvent.payment_status == "pending"
            )
            
            if deal_id:
                query = query.filter(PaymentEvent.related_deal_id == deal_id)
            
            pending_payments = query.all()
            logger.info(f"Found {len(pending_payments)} pending payments for deal_id={deal_id}")
        except Exception as e:
            logger.error(f"Error querying PaymentEvent: {e}", exc_info=True)
            raise
        
        for payment in pending_payments:
            # Calculate days past due (assuming payment was due 30 days after creation)
            # In production, use actual scheduled_date from PaymentSchedule
            payment_due_date = payment.created_at + timedelta(days=30)
            days_past_due = (now - payment_due_date).days
            
            if days_past_due > 0:
                # Check if default already exists for this payment
                query = self.db.query(LoanDefault).filter(
                    LoanDefault.deal_id == payment.related_deal_id,
                    LoanDefault.default_type == "payment_default",
                    LoanDefault.status.in_(["open", "in_recovery"])
                )
                if payment.related_loan_id:
                    query = query.filter(LoanDefault.loan_id == str(payment.related_loan_id))
                existing_default = query.first()
                
                if not existing_default:
                    # Determine severity based on days past due
                    if days_past_due <= 7:
                        severity = "low"
                    elif days_past_due <= 30:
                        severity = "medium"
                    elif days_past_due <= 60:
                        severity = "high"
                    else:
                        severity = "critical"
                    
                    # Create LoanDefault record
                    loan_default = LoanDefault(
                        loan_id=str(payment.related_loan_id) if payment.related_loan_id else None,
                        deal_id=payment.related_deal_id,
                        default_type="payment_default",
                        default_date=payment_due_date,
                        default_reason=f"Payment overdue: {payment.payment_type}",
                        amount_overdue=payment.amount,
                        days_past_due=days_past_due,
                        severity=severity,
                        status="open"
                    )
                    
                    # Generate CDM event
                    cdm_event = generate_cdm_loan_default(
                        default_id=str(loan_default.id) if loan_default.id else f"default_{payment.id}",
                        loan_id=str(payment.related_loan_id) if payment.related_loan_id else None,
                        deal_id=str(payment.related_deal_id) if payment.related_deal_id else None,
                        default_type="payment_default",
                        default_date=payment_due_date,
                        amount_overdue=float(payment.amount),
                        days_past_due=days_past_due,
                        severity=severity
                    )
                    
                    loan_default.cdm_events = [cdm_event]
                    
                    self.db.add(loan_default)
                    self.db.flush()  # Get the ID
                    
                    # Update default_id in CDM event
                    cdm_event = generate_cdm_loan_default(
                        default_id=str(loan_default.id),
                        loan_id=str(payment.related_loan_id) if payment.related_loan_id else None,
                        deal_id=str(payment.related_deal_id) if payment.related_deal_id else None,
                        default_type="payment_default",
                        default_date=payment_due_date,
                        amount_overdue=float(payment.amount),
                        days_past_due=days_past_due,
                        severity=severity
                    )
                    loan_default.cdm_events = [cdm_event]
                    
                    defaults.append(loan_default)
                    logger.info(f"Detected payment default: loan_id={loan_default.loan_id}, days_past_due={days_past_due}, severity={severity}")
        
        self.db.commit()
        return defaults
    
    def detect_covenant_breaches(self, deal_id: Optional[int] = None) -> List[LoanDefault]:
        """
        Detect covenant breaches from LoanAsset records with BREACH status.
        
        Args:
            deal_id: Optional deal ID to filter by
            
        Returns:
            List of detected LoanDefault records
        """
        defaults = []
        now = datetime.utcnow()
        
        # Query LoanAsset for BREACH status
        query = self.db.query(LoanAsset).filter(
            LoanAsset.risk_status == "BREACH"
        )
        
        # Note: LoanAsset doesn't have deal_id directly, so we'd need to join through deals
        # For now, check all breaches
        breached_assets = query.all()
        
        for asset in breached_assets:
            # Check if breach is new (compare last_verified_at with existing defaults)
            existing_default = self.db.query(LoanDefault).filter(
                LoanDefault.loan_id == asset.loan_id,
                LoanDefault.default_type == "covenant_breach",
                LoanDefault.status.in_(["open", "in_recovery"])
            ).first()
            
            if not existing_default or (asset.last_verified_at and existing_default.default_date < asset.last_verified_at):
                # Determine severity based on breach type (simplified)
                severity = "high"  # Breaches are typically high severity
                
                # Create LoanDefault record
                loan_default = LoanDefault(
                    loan_id=asset.loan_id,
                    deal_id=None,  # Would need to join to get deal_id
                    default_type="covenant_breach",
                    default_date=asset.last_verified_at or now,
                    default_reason=f"Covenant breach detected: {asset.risk_status}",
                    amount_overdue=None,
                    days_past_due=0,
                    severity=severity,
                    status="open"
                )
                
                # Generate CDM event
                cdm_event = generate_cdm_loan_default(
                    default_id=str(loan_default.id) if loan_default.id else f"breach_{asset.id}",
                    loan_id=asset.loan_id,
                    deal_id=None,
                    default_type="covenant_breach",
                    default_date=asset.last_verified_at or now,
                    days_past_due=0,
                    severity=severity,
                    default_reason=f"Covenant breach: {asset.risk_status}"
                )
                
                loan_default.cdm_events = [cdm_event]
                
                self.db.add(loan_default)
                self.db.flush()
                
                # Update with actual ID
                cdm_event = generate_cdm_loan_default(
                    default_id=str(loan_default.id),
                    loan_id=asset.loan_id,
                    deal_id=None,
                    default_type="covenant_breach",
                    default_date=asset.last_verified_at or now,
                    days_past_due=0,
                    severity=severity,
                    default_reason=f"Covenant breach: {asset.risk_status}"
                )
                loan_default.cdm_events = [cdm_event]
                
                defaults.append(loan_default)
                logger.info(f"Detected covenant breach: loan_id={asset.loan_id}, severity={severity}")
        
        self.db.commit()
        return defaults
    
    def get_active_defaults(
        self, 
        deal_id: Optional[int] = None, 
        status: Optional[str] = None
    ) -> List[LoanDefault]:
        """
        Get active loan defaults with optional filters.
        
        Args:
            deal_id: Optional deal ID to filter by
            status: Optional status to filter by (defaults to non-resolved)
            
        Returns:
            List of active LoanDefault records
        """
        query = self.db.query(LoanDefault)
        
        if deal_id:
            query = query.filter(LoanDefault.deal_id == deal_id)
        
        if status:
            query = query.filter(LoanDefault.status == status)
        else:
            # Default to non-resolved defaults
            query = query.filter(LoanDefault.status != "resolved")
        
        return query.order_by(LoanDefault.default_date.desc()).all()
    
    def get_defaults_by_severity(
        self, 
        severity: str, 
        deal_id: Optional[int] = None
    ) -> List[LoanDefault]:
        """
        Get defaults filtered by severity.
        
        Args:
            severity: Severity level (low, medium, high, critical)
            deal_id: Optional deal ID to filter by
            
        Returns:
            List of LoanDefault records with specified severity
        """
        query = self.db.query(LoanDefault).filter(
            LoanDefault.severity == severity,
            LoanDefault.status != "resolved"
        )
        
        if deal_id:
            query = query.filter(LoanDefault.deal_id == deal_id)
        
        return query.order_by(LoanDefault.default_date.desc()).all()
    
    def trigger_recovery_actions(
        self, 
        default_id: int, 
        action_types: Optional[List[str]] = None
    ) -> List[RecoveryAction]:
        """
        Trigger recovery actions for a loan default.
        
        Args:
            default_id: ID of the LoanDefault
            action_types: Optional list of action types to trigger (auto-determined if not provided)
            
        Returns:
            List of created RecoveryAction records
        """
        loan_default = self.db.query(LoanDefault).filter(LoanDefault.id == default_id).first()
        
        if not loan_default:
            raise ValueError(f"LoanDefault {default_id} not found")
        
        # Get borrower contact for deal
        borrower_contact = None
        if loan_default.deal_id:
            borrower_contact = self.db.query(BorrowerContact).filter(
                BorrowerContact.deal_id == loan_default.deal_id,
                BorrowerContact.is_active == True,
                BorrowerContact.is_primary == True
            ).first()
        
        # Determine action types based on severity and days past due if not provided
        if not action_types:
            if loan_default.days_past_due <= 3:
                action_types = ["sms_reminder"]
            elif loan_default.days_past_due <= 7:
                action_types = ["sms_reminder", "voice_call"]
            elif loan_default.days_past_due <= 30:
                action_types = ["sms_reminder", "voice_call", "email"]
            else:
                action_types = ["sms_reminder", "voice_call", "email", "escalation"]
        
        actions = []
        now = datetime.utcnow()
        
        for action_type in action_types:
            # Determine communication method
            if action_type == "sms_reminder":
                communication_method = "sms"
                recipient = borrower_contact.phone_number if borrower_contact else None
            elif action_type == "voice_call":
                communication_method = "voice"
                recipient = borrower_contact.phone_number if borrower_contact else None
            elif action_type == "email":
                communication_method = "email"
                recipient = borrower_contact.email if borrower_contact else None
            else:
                communication_method = "email"  # Default for escalation
                recipient = borrower_contact.email if borrower_contact else None
            
            if not recipient:
                logger.warning(f"No recipient found for action {action_type} on default {default_id}")
                continue
            
            # Generate message content using template service
            try:
                template_name = f"{communication_method}_{loan_default.default_type}" if loan_default.default_type == "payment_default" else f"{communication_method}_covenant_breach"
                if loan_default.severity in ["high", "critical"] and action_type != "email":
                    template_name = f"{communication_method}_escalation"
                
                message_content = self.template_service.render_template(
                    template_name=template_name,
                    default=loan_default,
                    contact=borrower_contact,
                    action_type=action_type
                )
            except Exception as e:
                logger.warning(f"Error rendering template, using fallback: {e}")
                message_content = self._generate_message_content(loan_default, action_type)
            
            # Create RecoveryAction record
            action = RecoveryAction(
                loan_default_id=default_id,
                action_type=action_type,
                communication_method=communication_method,
                recipient_phone=borrower_contact.phone_number if communication_method in ["sms", "voice"] else None,
                recipient_email=borrower_contact.email if communication_method == "email" else None,
                message_template=action_type,
                message_content=message_content,
                status="pending",
                scheduled_at=now  # Immediate execution
            )
            
            self.db.add(action)
            self.db.flush()
            
            actions.append(action)
            
            # Execute immediately
            try:
                self.execute_recovery_action(action.id)
            except Exception as e:
                logger.error(f"Error executing recovery action {action.id}: {e}")
                action.status = "failed"
                action.error_message = str(e)
        
        self.db.commit()
        return actions
    
    def execute_recovery_action(self, action_id: int) -> RecoveryAction:
        """
        Execute a recovery action (send SMS, make call, etc.).
        
        Args:
            action_id: ID of the RecoveryAction
            
        Returns:
            Updated RecoveryAction record
        """
        action = self.db.query(RecoveryAction).filter(RecoveryAction.id == action_id).first()
        
        if not action:
            raise ValueError(f"RecoveryAction {action_id} not found")
        
        if action.status != "pending":
            logger.warning(f"RecoveryAction {action_id} is not pending (status: {action.status})")
            return action
        
        loan_default = action.loan_default
        now = datetime.utcnow()
        
        try:
            if action.communication_method == "sms":
                if not action.recipient_phone:
                    raise ValueError("No recipient phone number for SMS")
                
                result = self.twilio_service.send_sms(
                    to_phone=action.recipient_phone,
                    message=action.message_content,
                    status_callback=action.metadata.get("status_callback") if action.metadata else None
                )
                
                if result["status"] == "sent":
                    action.twilio_message_sid = result.get("message_sid")
                    action.status = "sent"
                    action.sent_at = now
                else:
                    action.status = "failed"
                    action.error_message = result.get("message", "Failed to send SMS")
            
            elif action.communication_method == "voice":
                if not action.recipient_phone:
                    raise ValueError("No recipient phone number for voice call")
                
                result = self.twilio_service.make_voice_call(
                    to_phone=action.recipient_phone,
                    message=action.message_content,
                    status_callback=action.metadata.get("status_callback") if action.metadata else None
                )
                
                if result["status"] in ["queued", "ringing", "in-progress"]:
                    action.twilio_call_sid = result.get("call_sid")
                    action.status = "sent"
                    action.sent_at = now
                else:
                    action.status = "failed"
                    action.error_message = result.get("message", "Failed to make voice call")
            
            elif action.communication_method == "email":
                # Email sending would be implemented here
                # For now, mark as sent
                action.status = "sent"
                action.sent_at = now
                logger.info(f"Email action {action_id} marked as sent (email service not implemented)")
            
            # Generate CDM event for recovery action
            cdm_event = generate_cdm_recovery_action(
                action_id=str(action.id),
                loan_default_id=str(action.loan_default_id),
                action_type=action.action_type,
                communication_method=action.communication_method,
                message_content=action.message_content,
                status=action.status,
                twilio_message_sid=action.twilio_message_sid,
                twilio_call_sid=action.twilio_call_sid,
                sent_at=action.sent_at
            )
            
            # Store CDM event in action metadata
            if not action.metadata:
                action.metadata = {}
            action.metadata["cdm_event"] = cdm_event
            
            # Update loan default status
            if loan_default.status == "open":
                loan_default.status = "in_recovery"
            
        except Exception as e:
            logger.error(f"Error executing recovery action {action_id}: {e}")
            action.status = "failed"
            action.error_message = str(e)
        
        action.updated_at = now
        self.db.commit()
        
        return action
    
    def process_scheduled_actions(self) -> Dict[str, Any]:
        """
        Process all scheduled recovery actions that are due.
        
        Returns:
            Summary with counts of processed actions
        """
        now = datetime.utcnow()
        
        scheduled_actions = self.db.query(RecoveryAction).filter(
            RecoveryAction.status == "pending",
            RecoveryAction.scheduled_at <= now
        ).all()
        
        processed = 0
        failed = 0
        
        for action in scheduled_actions:
            try:
                self.execute_recovery_action(action.id)
                if action.status == "sent":
                    processed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Error processing scheduled action {action.id}: {e}")
                failed += 1
        
        self.db.commit()
        
        return {
            "status": "success",
            "processed": processed,
            "failed": failed,
            "total": len(scheduled_actions)
        }
    
    def _generate_message_content(self, loan_default: LoanDefault, action_type: str) -> str:
        """
        Generate message content for recovery action.
        
        Args:
            loan_default: LoanDefault record
            action_type: Type of action
            
        Returns:
            Message content string
        """
        # Simplified message generation - would use template service
        if loan_default.default_type == "payment_default":
            amount = f"${loan_default.amount_overdue}" if loan_default.amount_overdue else "amount"
            return (
                f"Hi, your loan payment of {amount} is {loan_default.days_past_due} days overdue. "
                f"Please contact us immediately to arrange payment."
            )
        else:
            return (
                f"Important: A covenant breach has been detected on your loan. "
                f"Please contact us immediately to discuss."
            )

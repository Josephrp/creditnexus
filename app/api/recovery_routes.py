"""
Recovery API routes for CreditNexus.

Provides endpoints for loan recovery operations including:
- Default detection and management
- Recovery action triggering and execution
- Borrower contact management
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.db.models import User, LoanDefault, RecoveryAction, BorrowerContact
from app.auth.jwt_auth import get_current_user, require_auth
from app.services.loan_recovery_service import LoanRecoveryService
from app.models.recovery_models import (
    LoanDefaultResponse,
    RecoveryActionResponse,
    BorrowerContactResponse,
    RecoveryActionCreate,
    BorrowerContactCreate,
    BorrowerContactUpdate,
    DetectDefaultsRequest,
    LoanDefaultListResponse,
    RecoveryActionListResponse,
    BorrowerContactListResponse
)
from app.utils.audit import log_audit_action, AuditAction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recovery", tags=["recovery"])


def get_recovery_service(db: Session = Depends(get_db)) -> LoanRecoveryService:
    """Get loan recovery service instance."""
    return LoanRecoveryService(db)


@router.get("/defaults", response_model=LoanDefaultListResponse)
async def get_defaults(
    deal_id: Optional[int] = Query(None, description="Filter by deal ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    recovery_service: LoanRecoveryService = Depends(get_recovery_service)
):
    """Get list of loan defaults with optional filters."""
    try:
        # Get defaults
        if severity:
            defaults = recovery_service.get_defaults_by_severity(severity, deal_id)
        else:
            defaults = recovery_service.get_active_defaults(deal_id, status)
        
        # Pagination
        total = len(defaults)
        start = (page - 1) * limit
        end = start + limit
        paginated_defaults = defaults[start:end]
        
        # Convert to response models
        default_responses = []
        for default in paginated_defaults:
            default_dict = default.to_dict()
            # Load recovery actions
            actions = db.query(RecoveryAction).filter(
                RecoveryAction.loan_default_id == default.id
            ).all()
            default_dict["recovery_actions"] = [action.to_dict() for action in actions]
            default_responses.append(LoanDefaultResponse(**default_dict))
        
        return LoanDefaultListResponse(
            defaults=default_responses,
            total=total,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error getting defaults: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get defaults: {str(e)}")


@router.post("/defaults/detect", response_model=List[LoanDefaultResponse])
async def detect_defaults(
    request: DetectDefaultsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
    recovery_service: LoanRecoveryService = Depends(get_recovery_service)
):
    """Detect payment defaults and covenant breaches."""
    try:
        logger.info(f"Detecting defaults for deal_id={request.deal_id}")
        
        # Detect payment defaults
        try:
            payment_defaults = recovery_service.detect_payment_defaults(request.deal_id)
            logger.info(f"Detected {len(payment_defaults)} payment defaults")
        except Exception as e:
            logger.error(f"Error detecting payment defaults: {e}", exc_info=True)
            payment_defaults = []
        
        # Detect covenant breaches
        try:
            covenant_breaches = recovery_service.detect_covenant_breaches(request.deal_id)
            logger.info(f"Detected {len(covenant_breaches)} covenant breaches")
        except Exception as e:
            logger.error(f"Error detecting covenant breaches: {e}", exc_info=True)
            covenant_breaches = []
        
        all_defaults = payment_defaults + covenant_breaches
        
        # Audit log
        try:
            log_audit_action(
                db=db,
                action=AuditAction.CREATE,
                target_type="loan_default",
                user_id=current_user.id,
                metadata={
                    "deal_id": request.deal_id,
                    "count": len(all_defaults),
                    "payment_defaults": len(payment_defaults),
                    "covenant_breaches": len(covenant_breaches)
                }
            )
            db.commit()
        except Exception as e:
            logger.warning(f"Error logging audit action: {e}", exc_info=True)
            db.rollback()
        
        # Convert to response models
        return [LoanDefaultResponse(**default.to_dict()) for default in all_defaults]
    except Exception as e:
        logger.error(f"Error detecting defaults: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to detect defaults: {str(e)}")


@router.get("/defaults/{default_id}", response_model=LoanDefaultResponse)
async def get_default(
    default_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    recovery_service: LoanRecoveryService = Depends(get_recovery_service)
):
    """Get a specific loan default by ID."""
    try:
        default = db.query(LoanDefault).filter(LoanDefault.id == default_id).first()
        
        if not default:
            raise HTTPException(status_code=404, detail=f"LoanDefault {default_id} not found")
        
        # Load recovery actions
        actions = db.query(RecoveryAction).filter(
            RecoveryAction.loan_default_id == default_id
        ).all()
        
        default_dict = default.to_dict()
        default_dict["recovery_actions"] = [action.to_dict() for action in actions]
        
        return LoanDefaultResponse(**default_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting default {default_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get default: {str(e)}")


@router.post("/defaults/{default_id}/actions", response_model=List[RecoveryActionResponse])
async def trigger_recovery_actions(
    default_id: int,
    request: RecoveryActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
    recovery_service: LoanRecoveryService = Depends(get_recovery_service)
):
    """Trigger recovery actions for a loan default."""
    try:
        actions = recovery_service.trigger_recovery_actions(
            default_id=default_id,
            action_types=request.action_types
        )
        
        # Audit log
        log_audit_action(
            db=db,
            action=AuditAction.CREATE,
            target_type="recovery_action",
            user_id=current_user.id,
            metadata={
                "default_id": default_id,
                "action_count": len(actions),
                "action_types": request.action_types or "auto"
            }
        )
        db.commit()
        
        return [RecoveryActionResponse(**action.to_dict()) for action in actions]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering recovery actions: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to trigger actions: {str(e)}")


@router.get("/actions", response_model=RecoveryActionListResponse)
async def get_actions(
    default_id: Optional[int] = Query(None, description="Filter by default ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    deal_id: Optional[int] = Query(None, description="Filter by deal ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of recovery actions with optional filters."""
    try:
        query = db.query(RecoveryAction)
        
        if default_id:
            query = query.filter(RecoveryAction.loan_default_id == default_id)
        
        if status:
            query = query.filter(RecoveryAction.status == status)
        
        if deal_id:
            # Join with LoanDefault to filter by deal_id
            query = query.join(LoanDefault).filter(LoanDefault.deal_id == deal_id)
        
        total = query.count()
        
        # Pagination
        actions = query.order_by(RecoveryAction.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        
        return RecoveryActionListResponse(
            actions=[RecoveryActionResponse(**action.to_dict()) for action in actions],
            total=total,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error getting actions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get actions: {str(e)}")


@router.get("/actions/{action_id}", response_model=RecoveryActionResponse)
async def get_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific recovery action by ID."""
    try:
        action = db.query(RecoveryAction).filter(RecoveryAction.id == action_id).first()
        
        if not action:
            raise HTTPException(status_code=404, detail=f"RecoveryAction {action_id} not found")
        
        return RecoveryActionResponse(**action.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting action {action_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get action: {str(e)}")


@router.post("/actions/{action_id}/execute", response_model=RecoveryActionResponse)
async def execute_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
    recovery_service: LoanRecoveryService = Depends(get_recovery_service)
):
    """Manually trigger execution of a recovery action."""
    try:
        action = recovery_service.execute_recovery_action(action_id)
        
        # Audit log
        log_audit_action(
            db=db,
            action=AuditAction.UPDATE,
            target_type="recovery_action",
            target_id=action_id,
            user_id=current_user.id,
            metadata={"status": action.status}
        )
        db.commit()
        
        return RecoveryActionResponse(**action.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing action {action_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to execute action: {str(e)}")


@router.post("/actions/scheduled/process")
async def process_scheduled_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
    recovery_service: LoanRecoveryService = Depends(get_recovery_service)
):
    """Process all scheduled recovery actions (background task endpoint)."""
    try:
        result = recovery_service.process_scheduled_actions()
        
        # Audit log
        log_audit_action(
            db=db,
            action=AuditAction.UPDATE,
            target_type="recovery_actions",
            user_id=current_user.id,
            metadata=result
        )
        db.commit()
        
        return result
    except Exception as e:
        logger.error(f"Error processing scheduled actions: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process actions: {str(e)}")


@router.get("/contacts", response_model=BorrowerContactListResponse)
async def get_contacts(
    deal_id: Optional[int] = Query(None, description="Filter by deal ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of borrower contacts."""
    try:
        query = db.query(BorrowerContact)
        
        if deal_id:
            query = query.filter(BorrowerContact.deal_id == deal_id)
        
        contacts = query.filter(BorrowerContact.is_active == True).all()
        
        return BorrowerContactListResponse(
            contacts=[BorrowerContactResponse(**contact.to_dict()) for contact in contacts]
        )
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get contacts: {str(e)}")


@router.post("/contacts", response_model=BorrowerContactResponse)
async def create_contact(
    request: BorrowerContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Create a new borrower contact."""
    try:
        contact = BorrowerContact(
            deal_id=request.deal_id,
            user_id=request.user_id,
            contact_name=request.contact_name,
            phone_number=request.phone_number,
            email=request.email,
            preferred_contact_method=request.preferred_contact_method,
            contact_preferences=request.contact_preferences,
            is_primary=request.is_primary,
            is_active=request.is_active
        )
        
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        # Audit log
        log_audit_action(
            db=db,
            action=AuditAction.CREATE,
            target_type="borrower_contact",
            target_id=contact.id,
            user_id=current_user.id,
            metadata={"deal_id": request.deal_id}
        )
        db.commit()
        
        return BorrowerContactResponse(**contact.to_dict())
    except Exception as e:
        logger.error(f"Error creating contact: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create contact: {str(e)}")


@router.put("/contacts/{contact_id}", response_model=BorrowerContactResponse)
async def update_contact(
    contact_id: int,
    request: BorrowerContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Update a borrower contact."""
    try:
        contact = db.query(BorrowerContact).filter(BorrowerContact.id == contact_id).first()
        
        if not contact:
            raise HTTPException(status_code=404, detail=f"BorrowerContact {contact_id} not found")
        
        # Update fields
        if request.contact_name is not None:
            contact.contact_name = request.contact_name
        if request.phone_number is not None:
            contact.phone_number = request.phone_number
        if request.email is not None:
            contact.email = request.email
        if request.preferred_contact_method is not None:
            contact.preferred_contact_method = request.preferred_contact_method
        if request.contact_preferences is not None:
            contact.contact_preferences = request.contact_preferences
        if request.is_primary is not None:
            contact.is_primary = request.is_primary
        if request.is_active is not None:
            contact.is_active = request.is_active
        
        db.commit()
        db.refresh(contact)
        
        # Audit log
        log_audit_action(
            db=db,
            action=AuditAction.UPDATE,
            target_type="borrower_contact",
            target_id=contact_id,
            user_id=current_user.id
        )
        db.commit()
        
        return BorrowerContactResponse(**contact.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact {contact_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update contact: {str(e)}")

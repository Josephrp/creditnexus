"""
Pydantic models for loan recovery API requests and responses.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class LoanDefaultResponse(BaseModel):
    """Response model for LoanDefault."""
    id: int
    loan_id: Optional[str] = None
    deal_id: Optional[int] = None
    default_type: str
    default_date: str
    default_reason: Optional[str] = None
    amount_overdue: Optional[str] = None  # Decimal as string
    days_past_due: int
    severity: str
    status: str
    resolved_at: Optional[str] = None
    cdm_events: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    recovery_actions: Optional[List["RecoveryActionResponse"]] = None
    
    class Config:
        from_attributes = True


class RecoveryActionResponse(BaseModel):
    """Response model for RecoveryAction."""
    id: int
    loan_default_id: int
    action_type: str
    communication_method: str
    recipient_phone: Optional[str] = None
    recipient_email: Optional[str] = None
    message_template: str
    message_content: str
    twilio_message_sid: Optional[str] = None
    twilio_call_sid: Optional[str] = None
    status: str
    scheduled_at: Optional[str] = None
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    response_received_at: Optional[str] = None
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class BorrowerContactResponse(BaseModel):
    """Response model for BorrowerContact."""
    id: int
    deal_id: int
    user_id: Optional[int] = None
    contact_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    preferred_contact_method: str
    contact_preferences: Optional[Dict[str, Any]] = None
    is_primary: bool
    is_active: bool
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class RecoveryActionCreate(BaseModel):
    """Request model for creating recovery actions."""
    action_types: Optional[List[str]] = Field(
        None, 
        description="List of action types to trigger (auto-determined if not provided)"
    )


class BorrowerContactCreate(BaseModel):
    """Request model for creating borrower contacts."""
    deal_id: int = Field(..., description="Deal ID")
    user_id: Optional[int] = Field(None, description="User ID if borrower is a user")
    contact_name: str = Field(..., description="Contact name")
    phone_number: Optional[str] = Field(None, description="Phone number (E.164 format)")
    email: Optional[str] = Field(None, description="Email address")
    preferred_contact_method: str = Field("sms", description="Preferred contact method (sms, voice, email)")
    contact_preferences: Optional[Dict[str, Any]] = Field(None, description="Contact preferences (timezone, hours, etc.)")
    is_primary: bool = Field(True, description="Is primary contact")
    is_active: bool = Field(True, description="Is active contact")


class BorrowerContactUpdate(BaseModel):
    """Request model for updating borrower contacts."""
    contact_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    contact_preferences: Optional[Dict[str, Any]] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class DetectDefaultsRequest(BaseModel):
    """Request model for detecting defaults."""
    deal_id: Optional[int] = Field(None, description="Optional deal ID to filter by")


class LoanDefaultListResponse(BaseModel):
    """Response model for paginated list of defaults."""
    defaults: List[LoanDefaultResponse]
    total: int
    page: int
    limit: int


class RecoveryActionListResponse(BaseModel):
    """Response model for paginated list of recovery actions."""
    actions: List[RecoveryActionResponse]
    total: int
    page: int
    limit: int


class BorrowerContactListResponse(BaseModel):
    """Response model for list of borrower contacts."""
    contacts: List[BorrowerContactResponse]


# Update forward references
LoanDefaultResponse.model_rebuild()
RecoveryActionResponse.model_rebuild()

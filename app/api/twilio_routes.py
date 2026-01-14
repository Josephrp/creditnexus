"""
Twilio webhook routes for SMS and voice status callbacks.

Handles webhook callbacks from Twilio for:
- SMS message status updates
- Voice call status updates
- Status callback updates
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Form, Response, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from datetime import datetime
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import VoiceResponse

from app.db import get_db
from app.db.models import RecoveryAction
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/twilio", tags=["twilio"])


def verify_twilio_signature(request: Request, form_data: dict) -> bool:
    """
    Verify Twilio request signature for security.
    
    Args:
        request: FastAPI Request object
        form_data: Form data from request
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not settings.TWILIO_ENABLED or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio not enabled or auth token missing, skipping signature verification")
        return True  # Allow in development if Twilio not configured
    
    try:
        # Get signature from headers
        signature = request.headers.get("X-Twilio-Signature", "")
        if not signature:
            logger.warning("Missing X-Twilio-Signature header")
            return False
        
        # Get the full URL
        url = str(request.url)
        
        # Get raw body (form data as string)
        # Twilio sends form-encoded data, so we need to reconstruct it
        body = "&".join([f"{k}={v}" for k, v in form_data.items()])
        
        # Validate signature
        auth_token = settings.TWILIO_AUTH_TOKEN.get_secret_value() if hasattr(settings.TWILIO_AUTH_TOKEN, 'get_secret_value') else settings.TWILIO_AUTH_TOKEN
        validator = RequestValidator(auth_token)
        
        is_valid = validator.validate(url, body.encode('utf-8'), signature)
        
        if not is_valid:
            logger.warning(f"Invalid Twilio signature for URL: {url}")
        
        return is_valid
    except Exception as e:
        logger.error(f"Error verifying Twilio signature: {e}")
        return False


@router.post("/webhook/sms")
async def twilio_sms_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle SMS status webhook from Twilio.
    
    Expected form data:
    - MessageSid: Twilio message SID
    - From: Sender phone number
    - To: Recipient phone number
    - Body: Message body (for incoming messages)
    - MessageStatus: Status (queued, sent, delivered, failed, etc.)
    """
    try:
        # Get form data
        form_data = await request.form()
        form_dict = dict(form_data)
        
        # Verify signature
        if not verify_twilio_signature(request, form_dict):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")
        
        message_sid = form_dict.get("MessageSid")
        message_status = form_dict.get("MessageStatus")
        from_number = form_dict.get("From")
        to_number = form_dict.get("To")
        body = form_dict.get("Body")
        
        logger.info(f"Received SMS webhook: MessageSid={message_sid}, Status={message_status}")
        
        # Update RecoveryAction if message_sid matches
        if message_sid:
            action = db.query(RecoveryAction).filter(
                RecoveryAction.twilio_message_sid == message_sid
            ).first()
            
            if action:
                # Update status based on message status
                status_mapping = {
                    "queued": "pending",
                    "sent": "sent",
                    "delivered": "delivered",
                    "failed": "failed",
                    "undelivered": "failed"
                }
                
                new_status = status_mapping.get(message_status, action.status)
                action.status = new_status
                
                if message_status == "delivered":
                    action.delivered_at = datetime.utcnow()
                elif message_status == "failed" or message_status == "undelivered":
                    action.error_message = f"Twilio status: {message_status}"
                
                action.updated_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"Updated RecoveryAction {action.id} status to {new_status}")
            else:
                logger.warning(f"RecoveryAction not found for MessageSid: {message_sid}")
        
        # Return empty 200 OK response (Twilio expects this)
        return Response(status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}")
        # Still return 200 to prevent Twilio retries for our errors
        return Response(status_code=200)


@router.post("/webhook/voice")
async def twilio_voice_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle voice call status webhook from Twilio.
    
    Expected form data:
    - CallSid: Twilio call SID
    - From: Caller phone number
    - To: Recipient phone number
    - CallStatus: Status (queued, ringing, in-progress, completed, failed, etc.)
    - Duration: Call duration in seconds (if completed)
    """
    try:
        # Get form data
        form_data = await request.form()
        form_dict = dict(form_data)
        
        # Verify signature
        if not verify_twilio_signature(request, form_dict):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")
        
        call_sid = form_dict.get("CallSid")
        call_status = form_dict.get("CallStatus")
        from_number = form_dict.get("From")
        to_number = form_dict.get("To")
        duration = form_dict.get("Duration")
        
        logger.info(f"Received voice webhook: CallSid={call_sid}, Status={call_status}")
        
        # Update RecoveryAction if call_sid matches
        if call_sid:
            action = db.query(RecoveryAction).filter(
                RecoveryAction.twilio_call_sid == call_sid
            ).first()
            
            if action:
                # Update status based on call status
                status_mapping = {
                    "queued": "pending",
                    "ringing": "sent",
                    "in-progress": "sent",
                    "completed": "delivered",
                    "failed": "failed",
                    "busy": "failed",
                    "no-answer": "failed",
                    "canceled": "failed"
                }
                
                new_status = status_mapping.get(call_status, action.status)
                action.status = new_status
                
                if call_status == "completed":
                    action.delivered_at = datetime.utcnow()
                    if duration:
                        if not action.metadata:
                            action.metadata = {}
                        action.metadata["call_duration"] = int(duration)
                elif call_status in ["failed", "busy", "no-answer", "canceled"]:
                    action.error_message = f"Twilio call status: {call_status}"
                
                action.updated_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"Updated RecoveryAction {action.id} status to {new_status}")
            else:
                logger.warning(f"RecoveryAction not found for CallSid: {call_sid}")
        
        # Return empty 200 OK response
        return Response(status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice webhook: {e}")
        return Response(status_code=200)


@router.post("/webhook/status")
async def twilio_status_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle generic status callback webhook from Twilio.
    
    Can handle both SMS and voice status updates.
    Expected form data:
    - MessageSid or CallSid: Identifier
    - MessageStatus or CallStatus: Status
    """
    try:
        # Get form data
        form_data = await request.form()
        form_dict = dict(form_data)
        
        # Verify signature
        if not verify_twilio_signature(request, form_dict):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")
        
        message_sid = form_dict.get("MessageSid")
        call_sid = form_dict.get("CallSid")
        message_status = form_dict.get("MessageStatus")
        call_status = form_dict.get("CallStatus")
        
        # Handle SMS status
        if message_sid and message_status:
            action = db.query(RecoveryAction).filter(
                RecoveryAction.twilio_message_sid == message_sid
            ).first()
            
            if action:
                status_mapping = {
                    "queued": "pending",
                    "sent": "sent",
                    "delivered": "delivered",
                    "failed": "failed",
                    "undelivered": "failed"
                }
                new_status = status_mapping.get(message_status, action.status)
                action.status = new_status
                
                if message_status == "delivered":
                    action.delivered_at = datetime.utcnow()
                
                action.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Updated RecoveryAction {action.id} via status webhook: {new_status}")
        
        # Handle voice status
        elif call_sid and call_status:
            action = db.query(RecoveryAction).filter(
                RecoveryAction.twilio_call_sid == call_sid
            ).first()
            
            if action:
                status_mapping = {
                    "queued": "pending",
                    "ringing": "sent",
                    "in-progress": "sent",
                    "completed": "delivered",
                    "failed": "failed"
                }
                new_status = status_mapping.get(call_status, action.status)
                action.status = new_status
                
                if call_status == "completed":
                    action.delivered_at = datetime.utcnow()
                
                action.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Updated RecoveryAction {action.id} via status webhook: {new_status}")
        
        # Return empty 200 OK response
        return Response(status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing status webhook: {e}")
        return Response(status_code=200)


@router.post("/webhook/voice/response")
async def twilio_voice_response(
    request: Request
):
    """
    Generate TwiML response for voice calls.
    
    This endpoint can be used as the URL for Twilio voice calls
    to generate dynamic TwiML responses.
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        from_number = form_data.get("From")
        to_number = form_data.get("To")
        
        logger.info(f"Generating TwiML response for call: CallSid={call_sid}")
        
        # Generate basic TwiML response
        response = VoiceResponse()
        response.say(
            "Thank you for calling. Please contact us during business hours.",
            language="en-US"
        )
        
        return Response(
            content=str(response),
            media_type="application/xml",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error generating TwiML response: {e}")
        # Return minimal TwiML on error
        response = VoiceResponse()
        response.say("An error occurred. Please try again later.", language="en-US")
        return Response(
            content=str(response),
            media_type="application/xml",
            status_code=200
        )

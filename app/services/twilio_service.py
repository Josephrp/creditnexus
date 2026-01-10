"""Twilio service for loan recovery communications."""

import logging
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from app.core.config import settings

logger = logging.getLogger(__name__)


class TwilioService:
    """Service for sending SMS messages via Twilio."""
    
    def __init__(self):
        self.client = None
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and hasattr(settings, 'TWILIO_AUTH_TOKEN'):
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    def send_sms(self, to_phone: str, message: str, from_phone: Optional[str] = None) -> dict:
        """Send SMS message via Twilio."""
        if not self.client:
            return {"status": "error", "message": "Twilio not configured"}
        
        try:
            from_number = from_phone or getattr(settings, 'TWILIO_PHONE_NUMBER', None)
            if not from_number:
                return {"status": "error", "message": "No sender phone number configured"}
            
            message_obj = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully: {message_obj.sid}")
            return {
                "status": "sent",
                "message_sid": message_obj.sid,
                "to": to_phone
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            return {"status": "error", "message": "Failed to send SMS"}


"""Twilio service for loan recovery communications."""

import logging
import re
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException
from twilio.twiml.voice_response import VoiceResponse

from app.core.config import settings

logger = logging.getLogger(__name__)


class TwilioService:
    """Service for sending SMS and voice messages via Twilio."""
    
    def __init__(self):
        """Initialize Twilio service with credentials from settings."""
        self.client = None
        if settings.TWILIO_ENABLED and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            account_sid = settings.TWILIO_ACCOUNT_SID.get_secret_value() if hasattr(settings.TWILIO_ACCOUNT_SID, 'get_secret_value') else settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN.get_secret_value() if hasattr(settings.TWILIO_AUTH_TOKEN, 'get_secret_value') else settings.TWILIO_AUTH_TOKEN
            self.client = Client(account_sid, auth_token)
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format (E.164).
        
        E.164 format: +[country code][number] (e.g., +1234567890)
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid E.164 format, False otherwise
        """
        # E.164 regex: + followed by 1-15 digits
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone_number))
    
    def send_sms(
        self, 
        to_phone: str, 
        message: str, 
        from_phone: Optional[str] = None,
        status_callback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS message via Twilio.
        
        Args:
            to_phone: Recipient phone number (E.164 format)
            message: SMS message content
            from_phone: Sender phone number (optional, uses TWILIO_PHONE_NUMBER if not provided)
            status_callback: URL for status callbacks (optional)
            
        Returns:
            Dict with status, message_sid, to, and error_code if any
        """
        if not settings.TWILIO_ENABLED or not settings.TWILIO_SMS_ENABLED:
            return {"status": "error", "message": "Twilio SMS is not enabled"}
        
        if not self.client:
            return {"status": "error", "message": "Twilio not configured"}
        
        if not self.validate_phone_number(to_phone):
            return {"status": "error", "message": f"Invalid phone number format: {to_phone}. Must be E.164 format (e.g., +1234567890)"}
        
        try:
            from_number = from_phone or settings.TWILIO_PHONE_NUMBER
            if not from_number:
                return {"status": "error", "message": "No sender phone number configured"}
            
            if not self.validate_phone_number(from_number):
                return {"status": "error", "message": f"Invalid sender phone number format: {from_number}"}
            
            create_params = {
                "body": message,
                "from_": from_number,
                "to": to_phone
            }
            
            if status_callback:
                create_params["status_callback"] = status_callback
            
            message_obj = self.client.messages.create(**create_params)
            
            logger.info(f"SMS sent successfully: {message_obj.sid} to {to_phone}")
            return {
                "status": "sent",
                "message_sid": message_obj.sid,
                "to": to_phone,
                "error_code": None
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio REST error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "error_code": e.code if hasattr(e, 'code') else None
            }
        except TwilioException as e:
            logger.error(f"Twilio error: {e}")
            return {"status": "error", "message": str(e), "error_code": None}
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            return {"status": "error", "message": "Failed to send SMS", "error_code": None}
    
    def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get message status from Twilio API.
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Dict with status, error_code, date_sent, date_updated
        """
        if not self.client:
            return {"status": "error", "message": "Twilio not configured"}
        
        try:
            message = self.client.messages(message_sid).fetch()
            return {
                "status": message.status,
                "error_code": message.error_code,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                "date_updated": message.date_updated.isoformat() if message.date_updated else None
            }
        except TwilioException as e:
            logger.error(f"Error fetching message status: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_twiml_response(self, message: str, language: str = "en-US") -> str:
        """
        Generate TwiML response for voice calls.
        
        Args:
            message: Text message to speak
            language: Language code (default: en-US)
            
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        response.say(message, language=language)
        return str(response)
    
    def generate_twiml_with_options(self, message: str, gather_digits: bool = False) -> str:
        """
        Generate TwiML response with optional digit gathering.
        
        Args:
            message: Text message to speak
            gather_digits: Whether to gather digits from caller
            
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        if gather_digits:
            gather = response.gather(num_digits=1, timeout=10)
            gather.say(message)
            # Fallback if no input
            response.say("We didn't receive any input. Goodbye.")
        else:
            response.say(message)
        return str(response)
    
    def make_voice_call(
        self,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None,
        status_callback: Optional[str] = None,
        twiml_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make voice call via Twilio.
        
        Args:
            to_phone: Recipient phone number (E.164 format)
            message: Message to speak (used if twiml_url not provided)
            from_phone: Sender phone number (optional)
            status_callback: URL for status callbacks (optional)
            twiml_url: URL to TwiML response (optional, generates inline if not provided)
            
        Returns:
            Dict with call_sid, status, and error_code if any
        """
        if not settings.TWILIO_ENABLED or not settings.TWILIO_VOICE_ENABLED:
            return {"status": "error", "message": "Twilio voice is not enabled"}
        
        if not self.client:
            return {"status": "error", "message": "Twilio not configured"}
        
        if not self.validate_phone_number(to_phone):
            return {"status": "error", "message": f"Invalid phone number format: {to_phone}"}
        
        try:
            from_number = from_phone or settings.TWILIO_PHONE_NUMBER
            if not from_number:
                return {"status": "error", "message": "No sender phone number configured"}
            
            if not self.validate_phone_number(from_number):
                return {"status": "error", "message": f"Invalid sender phone number format: {from_number}"}
            
            create_params = {
                "from_": from_number,
                "to": to_phone
            }
            
            if twiml_url:
                create_params["url"] = twiml_url
            else:
                # Generate TwiML inline
                twiml = self.generate_twiml_response(message)
                create_params["twiml"] = twiml
            
            if status_callback:
                create_params["status_callback"] = status_callback
            
            call = self.client.calls.create(**create_params)
            
            logger.info(f"Voice call initiated: {call.sid} to {to_phone}")
            return {
                "status": call.status,
                "call_sid": call.sid,
                "to": to_phone,
                "error_code": None
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio REST error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "error_code": e.code if hasattr(e, 'code') else None
            }
        except TwilioException as e:
            logger.error(f"Twilio error: {e}")
            return {"status": "error", "message": str(e), "error_code": None}
        except Exception as e:
            logger.error(f"Unexpected error making voice call: {e}")
            return {"status": "error", "message": "Failed to make voice call", "error_code": None}
    
    def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        """
        Get call status from Twilio API.
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Dict with status, duration, start_time, end_time
        """
        if not self.client:
            return {"status": "error", "message": "Twilio not configured"}
        
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "status": call.status,
                "duration": call.duration,
                "start_time": call.start_time.isoformat() if call.start_time else None,
                "end_time": call.end_time.isoformat() if call.end_time else None
            }
        except TwilioException as e:
            logger.error(f"Error fetching call status: {e}")
            return {"status": "error", "message": str(e)}


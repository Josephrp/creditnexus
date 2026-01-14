"""
Recovery Template Service for managing message templates.

Provides methods for loading and rendering recovery message templates
using Jinja2 templating.
"""

import logging
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.db.models import LoanDefault, BorrowerContact

logger = logging.getLogger(__name__)


class RecoveryTemplateService:
    """Service for managing recovery message templates."""
    
    def __init__(self):
        """Initialize recovery template service."""
        template_dir = Path(__file__).parent.parent / "templates" / "recovery"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False  # Text templates don't need HTML escaping
        )
    
    def get_template(
        self, 
        template_name: str, 
        default_type: str, 
        severity: str
    ) -> str:
        """
        Load and return template content.
        
        Args:
            template_name: Name of template file (e.g., "sms_payment_reminder")
            default_type: Type of default (payment_default, covenant_breach)
            severity: Severity level (low, medium, high, critical)
            
        Returns:
            Template content as string
        """
        # Try severity-specific template first, then fall back to default
        template_files = [
            f"{template_name}_{severity}.txt",
            f"{template_name}_{default_type}.txt",
            f"{template_name}.txt"
        ]
        
        for template_file in template_files:
            template_path = self.template_dir / template_file
            if template_path.exists():
                try:
                    return template_path.read_text(encoding="utf-8")
                except Exception as e:
                    logger.error(f"Error reading template {template_file}: {e}")
        
        # Return default template if none found
        logger.warning(f"Template not found: {template_name}, using default")
        return self._get_default_template(template_name, default_type)
    
    def render_template(
        self,
        template_name: str,
        default: LoanDefault,
        contact: Optional[BorrowerContact] = None,
        action_type: str = "sms_reminder",
        **kwargs
    ) -> str:
        """
        Render template with provided context.
        
        Args:
            template_name: Name of template file
            default: LoanDefault record
            contact: BorrowerContact record (optional)
            action_type: Type of action
            **kwargs: Additional template variables
            
        Returns:
            Rendered message string
        """
        try:
            template_content = self.get_template(
                template_name, 
                default.default_type, 
                default.severity
            )
            
            template = self.env.from_string(template_content)
            
            # Build context
            context = {
                "borrower_name": contact.contact_name if contact else "Valued Customer",
                "loan_id": default.loan_id or "N/A",
                "deal_id": str(default.deal_id) if default.deal_id else "N/A",
                "amount_overdue": f"${default.amount_overdue:,.2f}" if default.amount_overdue else "N/A",
                "days_past_due": default.days_past_due,
                "due_date": default.default_date.strftime("%Y-%m-%d") if default.default_date else "N/A",
                "severity": default.severity,
                "default_type": default.default_type,
                "default_reason": default.default_reason or "Payment overdue",
                "contact_phone": contact.phone_number if contact else None,
                "contact_email": contact.email if contact else None,
                **kwargs
            }
            
            return template.render(**context)
            
        except TemplateNotFound as e:
            logger.error(f"Template not found: {e}")
            return self.generate_custom_message(default, contact, action_type)
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return self.generate_custom_message(default, contact, action_type)
    
    def generate_custom_message(
        self,
        default: LoanDefault,
        contact: Optional[BorrowerContact] = None,
        action_type: str = "sms_reminder"
    ) -> str:
        """
        Generate custom message based on default details.
        
        Args:
            default: LoanDefault record
            contact: BorrowerContact record (optional)
            action_type: Type of action
            
        Returns:
            Formatted message string
        """
        borrower_name = contact.contact_name if contact else "Valued Customer"
        
        if default.default_type == "payment_default":
            amount_str = f"${default.amount_overdue:,.2f}" if default.amount_overdue else "your payment"
            
            if action_type == "sms_reminder":
                return (
                    f"Hi {borrower_name}, your loan {default.loan_id or 'payment'} "
                    f"of {amount_str} is {default.days_past_due} days overdue. "
                    f"Please contact us immediately to arrange payment."
                )
            elif action_type == "voice_call":
                return (
                    f"Hello {borrower_name}, this is a reminder that your loan payment "
                    f"of {amount_str} is {default.days_past_due} days overdue. "
                    f"Please contact us immediately to arrange payment."
                )
            elif action_type == "escalation":
                return (
                    f"URGENT: {borrower_name}, your loan {default.loan_id or 'payment'} "
                    f"of {amount_str} is {default.days_past_due} days overdue. "
                    f"This matter requires immediate attention. Please contact us today."
                )
            else:
                return (
                    f"Dear {borrower_name}, your loan payment of {amount_str} "
                    f"is {default.days_past_due} days overdue. Please contact us to arrange payment."
                )
        else:
            # Covenant breach
            return (
                f"Important Notice: {borrower_name}, a covenant breach has been detected "
                f"on your loan {default.loan_id or 'facility'}. "
                f"Please contact us immediately to discuss this matter."
            )
    
    def _get_default_template(self, template_name: str, default_type: str) -> str:
        """Get default template content if file not found."""
        if "sms" in template_name:
            if default_type == "payment_default":
                return "Hi {{borrower_name}}, your loan {{loan_id}} payment of {{amount_overdue}} is {{days_past_due}} days overdue. Please contact us immediately."
            else:
                return "Hi {{borrower_name}}, a covenant breach has been detected on your loan {{loan_id}}. Please contact us immediately."
        elif "voice" in template_name:
            if default_type == "payment_default":
                return "Hello {{borrower_name}}, this is a reminder that your loan payment of {{amount_overdue}} is {{days_past_due}} days overdue. Please contact us immediately."
            else:
                return "Hello {{borrower_name}}, a covenant breach has been detected on your loan. Please contact us immediately."
        else:
            return "Dear {{borrower_name}}, please contact us regarding your loan {{loan_id}}."

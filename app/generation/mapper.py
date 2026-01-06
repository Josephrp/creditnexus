"""
CDM to template field mapper.

Maps CDM CreditAgreement data to template placeholder values.
"""

import logging
from decimal import Decimal
from datetime import date
from typing import Dict, List, Optional, Any

from app.models.cdm import CreditAgreement, Frequency, PeriodEnum, Currency
from app.db.models import LMATemplate, TemplateFieldMapping
from app.generation.field_parser import FieldPathParser

logger = logging.getLogger(__name__)


class FieldMapper:
    """
    Maps CDM CreditAgreement data to template field values.
    
    Supports:
    - Direct field mapping: "parties[role='Borrower'].name" -> "ACME Corp"
    - Computed field mapping: "facilities" -> sum of commitment amounts
    - Formatting: dates, currency, spreads, payment frequencies
    """
    
    def __init__(self, template: LMATemplate, field_mappings: Optional[List[TemplateFieldMapping]] = None):
        """
        Initialize field mapper.
        
        Args:
            template: LMATemplate instance
            field_mappings: Optional list of TemplateFieldMapping instances
                If not provided, will be loaded from template relationship
        """
        self.template = template
        self.field_mappings = field_mappings or []
        self.parser = FieldPathParser()
        
        logger.debug(f"Initialized FieldMapper for template {template.template_code}")
    
    def map_cdm_to_template(self, cdm_data: CreditAgreement) -> Dict[str, Any]:
        """
        Map CDM data to template field values.
        
        Args:
            cdm_data: CreditAgreement instance
            
        Returns:
            Dictionary mapping template field names to values
            Example: {"[BORROWER_NAME]": "ACME Corp", "[COMMITMENT_AMOUNT]": "10,000,000.00 USD"}
        """
        result = {}
        
        # Load field mappings if not provided
        if not self.field_mappings:
            self.field_mappings = self.template.field_mappings
        
        # Map each field
        for mapping in self.field_mappings:
            template_field = mapping.template_field
            cdm_field = mapping.cdm_field
            mapping_type = mapping.mapping_type or "direct"
            
            try:
                if mapping_type == "direct":
                    value = self._map_direct_field(cdm_data, cdm_field)
                elif mapping_type == "computed":
                    value = self._map_computed_field(
                        cdm_data, 
                        cdm_field, 
                        mapping.transformation_rule
                    )
                elif mapping_type == "ai_generated":
                    # AI-generated fields are handled separately
                    continue
                else:
                    logger.warning(f"Unknown mapping type: {mapping_type} for field {template_field}")
                    continue
                
                if value is not None:
                    result[template_field] = value
                else:
                    logger.debug(f"No value found for field {template_field} (path: {cdm_field})")
                    
            except Exception as e:
                logger.warning(f"Error mapping field {template_field}: {e}")
                continue
        
        return result
    
    def _map_direct_field(self, cdm_data: CreditAgreement, cdm_field_path: str) -> Optional[Any]:
        """
        Map a direct field from CDM data.
        
        Args:
            cdm_data: CreditAgreement instance
            cdm_field_path: CDM field path (e.g., "parties[role='Borrower'].name")
            
        Returns:
            Field value or None if not found
        """
        if not cdm_field_path:
            return None
        
        value = self.parser.get_nested_value(cdm_data, cdm_field_path)
        
        # Handle special formatting for common field types
        if isinstance(value, date):
            return self._format_date(value)
        elif isinstance(value, Decimal):
            # Check if this is a currency amount
            # Try to get currency from context
            if "commitment_amount" in cdm_field_path or "amount" in cdm_field_path:
                currency = self.parser.get_nested_value(
                    cdm_data, 
                    cdm_field_path.replace(".amount", ".currency")
                )
                if currency:
                    return self._format_currency(value, currency.value if hasattr(currency, 'value') else str(currency))
            return str(value)
        elif isinstance(value, Frequency):
            return self._format_payment_frequency(value)
        elif hasattr(value, 'value'):  # Enum
            return value.value
        
        return value
    
    def _map_computed_field(
        self, 
        cdm_data: CreditAgreement, 
        cdm_field_path: str, 
        transformation_rule: Optional[str]
    ) -> Optional[Any]:
        """
        Map a computed field using transformation rule.
        
        Args:
            cdm_data: CreditAgreement instance
            cdm_field_path: CDM field path (may be used for context)
            transformation_rule: Transformation rule name (e.g., "format_currency", "sum_commitment_amounts")
            
        Returns:
            Computed value or None
        """
        if not transformation_rule:
            # Fallback to direct mapping
            return self._map_direct_field(cdm_data, cdm_field_path)
        
        # Handle common transformation rules
        if transformation_rule == "format_currency":
            amount = self.parser.get_nested_value(cdm_data, cdm_field_path)
            if amount and isinstance(amount, Decimal):
                # Try to get currency
                currency_path = cdm_field_path.replace(".amount", ".currency")
                currency = self.parser.get_nested_value(cdm_data, currency_path)
                if currency:
                    return self._format_currency(amount, currency.value if hasattr(currency, 'value') else str(currency))
                return str(amount)
        
        elif transformation_rule == "format_date":
            date_value = self.parser.get_nested_value(cdm_data, cdm_field_path)
            if date_value and isinstance(date_value, date):
                return self._format_date(date_value)
        
        elif transformation_rule == "format_spread":
            spread_bps = self.parser.get_nested_value(cdm_data, cdm_field_path)
            if spread_bps is not None:
                return self._format_spread(float(spread_bps))
        
        elif transformation_rule == "sum_commitment_amounts":
            # Sum all facility commitment amounts
            if cdm_data.facilities:
                total = Decimal("0")
                currency = None
                for facility in cdm_data.facilities:
                    if facility.commitment_amount:
                        total += facility.commitment_amount.amount
                        if not currency:
                            currency = facility.commitment_amount.currency
                if currency:
                    return self._format_currency(total, currency.value if hasattr(currency, 'value') else str(currency))
                return str(total)
        
        elif transformation_rule == "extract_facility_type":
            # Extract facility type from facility name
            facility_name = self.parser.get_nested_value(cdm_data, cdm_field_path)
            if facility_name:
                # Simple extraction: "Term Loan B" -> "Term Loan"
                parts = str(facility_name).split()
                if len(parts) >= 2:
                    return f"{parts[0]} {parts[1]}"
                return str(facility_name)
        
        elif transformation_rule == "format_pricing":
            # Format interest rate option as "Benchmark + Spread"
            rate_option = self.parser.get_nested_value(cdm_data, cdm_field_path)
            if rate_option and hasattr(rate_option, 'benchmark') and hasattr(rate_option, 'spread_bps'):
                benchmark = rate_option.benchmark
                spread = self._format_spread(rate_option.spread_bps)
                return f"{benchmark} + {spread}"
        
        # Unknown transformation rule - try direct mapping
        logger.warning(f"Unknown transformation rule: {transformation_rule}")
        return self._map_direct_field(cdm_data, cdm_field_path)
    
    def _format_date(self, date_value: date) -> str:
        """
        Format date as "DD MMMM YYYY" (e.g., "15 January 2024").
        
        Args:
            date_value: Date to format
            
        Returns:
            Formatted date string
        """
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return f"{date_value.day} {months[date_value.month - 1]} {date_value.year}"
    
    def _format_currency(self, amount: Decimal, currency: str) -> str:
        """
        Format currency amount with thousand separators and currency symbol.
        
        Args:
            amount: Decimal amount
            currency: Currency code (USD, EUR, GBP, JPY)
            
        Returns:
            Formatted string (e.g., "10,000,000.00 USD")
        """
        # Format with thousand separators
        amount_str = f"{amount:,.2f}"
        
        # Add currency symbol/code
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥"
        }
        
        symbol = currency_symbols.get(currency, currency)
        return f"{symbol}{amount_str} {currency}"
    
    def _format_spread(self, spread_bps: float) -> str:
        """
        Format spread from basis points to percentage.
        
        Args:
            spread_bps: Spread in basis points (e.g., 250.0 for 2.5%)
            
        Returns:
            Formatted string (e.g., "2.50%" or "250 bps")
        """
        # Convert basis points to percentage
        percentage = spread_bps / 100.0
        
        # Format as percentage with 2 decimal places
        return f"{percentage:.2f}%"
    
    def _format_payment_frequency(self, frequency: Frequency) -> str:
        """
        Format payment frequency as human-readable string.
        
        Args:
            frequency: Frequency instance
            
        Returns:
            Formatted string (e.g., "Quarterly", "Semi-annually", "Monthly")
        """
        period = frequency.period
        multiplier = frequency.period_multiplier
        
        # Common frequencies
        if period == PeriodEnum.Month:
            if multiplier == 1:
                return "Monthly"
            elif multiplier == 3:
                return "Quarterly"
            elif multiplier == 6:
                return "Semi-annually"
            elif multiplier == 12:
                return "Annually"
            else:
                return f"Every {multiplier} months"
        elif period == PeriodEnum.Year:
            if multiplier == 1:
                return "Annually"
            else:
                return f"Every {multiplier} year(s)"
        elif period == PeriodEnum.Week:
            if multiplier == 1:
                return "Weekly"
            else:
                return f"Every {multiplier} week(s)"
        elif period == PeriodEnum.Day:
            if multiplier == 1:
                return "Daily"
            else:
                return f"Every {multiplier} day(s)"
        
        return f"{multiplier} {period.value}(s)"
    
    def validate_required_fields(self, cdm_data: CreditAgreement) -> List[str]:
        """
        Validate that all required fields are present in CDM data.
        
        Args:
            cdm_data: CreditAgreement instance
            
        Returns:
            List of missing required field paths
        """
        missing_fields = []
        
        # Get required fields from template
        required_fields = self.template.required_fields or []
        if isinstance(required_fields, dict):
            required_fields = required_fields.get("fields", [])
        
        # Also check field mappings marked as required
        for mapping in self.field_mappings:
            if mapping.is_required and mapping.mapping_type != "ai_generated":
                if mapping.cdm_field not in required_fields:
                    required_fields.append(mapping.cdm_field)
        
        # Validate each required field
        for field_path in required_fields:
            value = self.parser.get_nested_value(cdm_data, field_path)
            if value is None:
                missing_fields.append(field_path)
        
        return missing_fields




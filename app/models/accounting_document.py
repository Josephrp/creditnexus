"""Accounting document models for quantitative financial data extraction.

This module defines Pydantic models for extracting structured accounting data
from balance sheets, income statements, cash flow statements, and tax returns.
All models follow CDM compliance principles and use Decimal for monetary amounts.
"""

from decimal import Decimal
from datetime import date
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.cdm import Money, Currency, ExtractionStatus


class DocumentType(str, Enum):
    """Types of accounting documents."""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW_STATEMENT = "cash_flow"
    TAX_RETURN = "tax_return"


class PeriodType(str, Enum):
    """Reporting period types."""
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    MONTHLY = "monthly"
    YEAR_TO_DATE = "year_to_date"


class FilingStatus(str, Enum):
    """Tax filing status."""
    SINGLE = "Single"
    MARRIED_FILING_JOINTLY = "Married Filing Jointly"
    MARRIED_FILING_SEPARATELY = "Married Filing Separately"
    HEAD_OF_HOUSEHOLD = "Head of Household"
    QUALIFYING_WIDOW = "Qualifying Widow(er) with Dependent Child"


# ============================================================================
# Balance Sheet Models
# ============================================================================


class CurrentAssets(BaseModel):
    """Current assets section of balance sheet."""
    cash: Optional[Money] = Field(None, description="Cash and cash equivalents")
    accounts_receivable: Optional[Money] = Field(None, description="Accounts receivable")
    inventory: Optional[Money] = Field(None, description="Inventory")
    prepaid_expenses: Optional[Money] = Field(None, description="Prepaid expenses")
    other_current_assets: Optional[Money] = Field(None, description="Other current assets")
    total_current_assets: Optional[Money] = Field(None, description="Total current assets")


class NonCurrentAssets(BaseModel):
    """Non-current assets section of balance sheet."""
    property_plant_equipment: Optional[Money] = Field(None, description="Property, plant, and equipment")
    intangible_assets: Optional[Money] = Field(None, description="Intangible assets")
    investments: Optional[Money] = Field(None, description="Long-term investments")
    other_non_current_assets: Optional[Money] = Field(None, description="Other non-current assets")
    total_non_current_assets: Optional[Money] = Field(None, description="Total non-current assets")


class CurrentLiabilities(BaseModel):
    """Current liabilities section of balance sheet."""
    accounts_payable: Optional[Money] = Field(None, description="Accounts payable")
    short_term_debt: Optional[Money] = Field(None, description="Short-term debt")
    accrued_expenses: Optional[Money] = Field(None, description="Accrued expenses")
    other_current_liabilities: Optional[Money] = Field(None, description="Other current liabilities")
    total_current_liabilities: Optional[Money] = Field(None, description="Total current liabilities")


class NonCurrentLiabilities(BaseModel):
    """Non-current liabilities section of balance sheet."""
    long_term_debt: Optional[Money] = Field(None, description="Long-term debt")
    deferred_tax_liabilities: Optional[Money] = Field(None, description="Deferred tax liabilities")
    other_non_current_liabilities: Optional[Money] = Field(None, description="Other non-current liabilities")
    total_non_current_liabilities: Optional[Money] = Field(None, description="Total non-current liabilities")


class Equity(BaseModel):
    """Equity section of balance sheet."""
    common_stock: Optional[Money] = Field(None, description="Common stock")
    retained_earnings: Optional[Money] = Field(None, description="Retained earnings")
    additional_paid_in_capital: Optional[Money] = Field(None, description="Additional paid-in capital")
    other_equity: Optional[Money] = Field(None, description="Other equity components")
    total_equity: Optional[Money] = Field(None, description="Total equity")


class BalanceSheet(BaseModel):
    """Balance sheet with assets, liabilities, and equity."""
    extraction_status: ExtractionStatus = Field(
        default=ExtractionStatus.SUCCESS,
        description="Status of extraction: success, partial_data_missing, or irrelevant_document"
    )
    reporting_period_start: Optional[date] = Field(None, description="Start date of reporting period (ISO 8601: YYYY-MM-DD)")
    reporting_period_end: Optional[date] = Field(None, description="End date of reporting period (ISO 8601: YYYY-MM-DD)")
    period_type: Optional[PeriodType] = Field(None, description="Type of reporting period")
    currency: Optional[Currency] = Field(None, description="Currency code for all amounts")
    
    current_assets: Optional[CurrentAssets] = Field(None, description="Current assets")
    non_current_assets: Optional[NonCurrentAssets] = Field(None, description="Non-current assets")
    total_assets: Optional[Money] = Field(None, description="Total assets")
    
    current_liabilities: Optional[CurrentLiabilities] = Field(None, description="Current liabilities")
    non_current_liabilities: Optional[NonCurrentLiabilities] = Field(None, description="Non-current liabilities")
    total_liabilities: Optional[Money] = Field(None, description="Total liabilities")
    
    equity: Optional[Equity] = Field(None, description="Equity")
    total_equity: Optional[Money] = Field(None, description="Total equity")
    
    @model_validator(mode='after')
    def validate_balance_sheet_equation(self) -> 'BalanceSheet':
        """Validate that Assets = Liabilities + Equity (CDM principle: validate at creation point)."""
        if self.total_assets and self.total_liabilities and self.total_equity:
            assets_amount = self.total_assets.amount
            liabilities_equity_amount = self.total_liabilities.amount + self.total_equity.amount
            
            # Allow small rounding differences (0.01)
            if abs(assets_amount - liabilities_equity_amount) > Decimal('0.01'):
                if self.extraction_status == ExtractionStatus.SUCCESS:
                    object.__setattr__(self, 'extraction_status', ExtractionStatus.PARTIAL)
        
        return self


# ============================================================================
# Income Statement Models
# ============================================================================


class Revenue(BaseModel):
    """Revenue section of income statement."""
    gross_revenue: Optional[Money] = Field(None, description="Gross revenue")
    net_revenue: Optional[Money] = Field(None, description="Net revenue (after returns/allowances)")
    revenue_by_segment: Optional[Dict[str, Money]] = Field(None, description="Revenue by business segment")
    total_revenue: Optional[Money] = Field(None, description="Total revenue")


class Expenses(BaseModel):
    """Expenses section of income statement."""
    cost_of_goods_sold: Optional[Money] = Field(None, description="Cost of goods sold (COGS)")
    selling_general_administrative: Optional[Money] = Field(None, description="Selling, general, and administrative expenses")
    research_development: Optional[Money] = Field(None, description="Research and development expenses")
    depreciation: Optional[Money] = Field(None, description="Depreciation expense")
    amortization: Optional[Money] = Field(None, description="Amortization expense")
    other_operating_expenses: Optional[Money] = Field(None, description="Other operating expenses")
    total_operating_expenses: Optional[Money] = Field(None, description="Total operating expenses")


class OtherIncomeExpenses(BaseModel):
    """Other income and expenses section."""
    interest_income: Optional[Money] = Field(None, description="Interest income")
    interest_expense: Optional[Money] = Field(None, description="Interest expense")
    tax_expense: Optional[Money] = Field(None, description="Tax expense")
    other_income: Optional[Money] = Field(None, description="Other income")
    other_expenses: Optional[Money] = Field(None, description="Other expenses")


class IncomeStatement(BaseModel):
    """Income statement with revenue, expenses, and net income."""
    extraction_status: ExtractionStatus = Field(
        default=ExtractionStatus.SUCCESS,
        description="Status of extraction: success, partial_data_missing, or irrelevant_document"
    )
    reporting_period_start: Optional[date] = Field(None, description="Start date of reporting period (ISO 8601: YYYY-MM-DD)")
    reporting_period_end: Optional[date] = Field(None, description="End date of reporting period (ISO 8601: YYYY-MM-DD)")
    period_type: Optional[PeriodType] = Field(None, description="Type of reporting period")
    currency: Optional[Currency] = Field(None, description="Currency code for all amounts")
    
    revenue: Optional[Revenue] = Field(None, description="Revenue")
    total_revenue: Optional[Money] = Field(None, description="Total revenue")
    
    expenses: Optional[Expenses] = Field(None, description="Expenses")
    total_expenses: Optional[Money] = Field(None, description="Total expenses")
    
    other_income_expenses: Optional[OtherIncomeExpenses] = Field(None, description="Other income and expenses")
    
    net_income_before_tax: Optional[Money] = Field(None, description="Net income before tax")
    net_income_after_tax: Optional[Money] = Field(None, description="Net income after tax")
    net_income: Optional[Money] = Field(None, description="Net income")
    
    earnings_per_share: Optional[Decimal] = Field(None, description="Earnings per share (EPS)")
    
    @model_validator(mode='after')
    def validate_income_statement_equation(self) -> 'IncomeStatement':
        """Validate that Revenue - Expenses = Net Income (CDM principle: validate at creation point)."""
        if self.total_revenue and self.total_expenses and self.net_income:
            revenue_amount = self.total_revenue.amount
            expenses_amount = self.total_expenses.amount
            net_income_amount = self.net_income.amount
            
            calculated_net = revenue_amount - expenses_amount
            
            # Allow small rounding differences (0.01)
            if abs(calculated_net - net_income_amount) > Decimal('0.01'):
                if self.extraction_status == ExtractionStatus.SUCCESS:
                    object.__setattr__(self, 'extraction_status', ExtractionStatus.PARTIAL)
        
        return self


# ============================================================================
# Cash Flow Statement Models
# ============================================================================


class OperatingActivities(BaseModel):
    """Operating activities section of cash flow statement."""
    net_income: Optional[Money] = Field(None, description="Net income")
    depreciation: Optional[Money] = Field(None, description="Depreciation")
    amortization: Optional[Money] = Field(None, description="Amortization")
    changes_in_working_capital: Optional[Money] = Field(None, description="Changes in working capital")
    other_operating_adjustments: Optional[Money] = Field(None, description="Other operating adjustments")
    cash_from_operations: Optional[Money] = Field(None, description="Cash from operations")


class InvestingActivities(BaseModel):
    """Investing activities section of cash flow statement."""
    capital_expenditures: Optional[Money] = Field(None, description="Capital expenditures (negative)")
    asset_sales: Optional[Money] = Field(None, description="Asset sales (positive)")
    investments: Optional[Money] = Field(None, description="Investments (negative)")
    other_investing: Optional[Money] = Field(None, description="Other investing activities")
    cash_from_investing: Optional[Money] = Field(None, description="Cash from investing activities")


class FinancingActivities(BaseModel):
    """Financing activities section of cash flow statement."""
    debt_issuance: Optional[Money] = Field(None, description="Debt issuance (positive)")
    debt_repayment: Optional[Money] = Field(None, description="Debt repayment (negative)")
    equity_issuance: Optional[Money] = Field(None, description="Equity issuance (positive)")
    dividends_paid: Optional[Money] = Field(None, description="Dividends paid (negative)")
    other_financing: Optional[Money] = Field(None, description="Other financing activities")
    cash_from_financing: Optional[Money] = Field(None, description="Cash from financing activities")


class CashFlowStatement(BaseModel):
    """Cash flow statement with operating, investing, and financing activities."""
    extraction_status: ExtractionStatus = Field(
        default=ExtractionStatus.SUCCESS,
        description="Status of extraction: success, partial_data_missing, or irrelevant_document"
    )
    reporting_period_start: Optional[date] = Field(None, description="Start date of reporting period (ISO 8601: YYYY-MM-DD)")
    reporting_period_end: Optional[date] = Field(None, description="End date of reporting period (ISO 8601: YYYY-MM-DD)")
    period_type: Optional[PeriodType] = Field(None, description="Type of reporting period")
    currency: Optional[Currency] = Field(None, description="Currency code for all amounts")
    
    operating_activities: Optional[OperatingActivities] = Field(None, description="Operating activities")
    cash_from_operations: Optional[Money] = Field(None, description="Cash from operations")
    
    investing_activities: Optional[InvestingActivities] = Field(None, description="Investing activities")
    cash_from_investing: Optional[Money] = Field(None, description="Cash from investing activities")
    
    financing_activities: Optional[FinancingActivities] = Field(None, description="Financing activities")
    cash_from_financing: Optional[Money] = Field(None, description="Cash from financing activities")
    
    beginning_cash: Optional[Money] = Field(None, description="Beginning cash balance")
    ending_cash: Optional[Money] = Field(None, description="Ending cash balance")
    net_change_in_cash: Optional[Money] = Field(None, description="Net change in cash")
    
    @model_validator(mode='after')
    def validate_cash_flow_equation(self) -> 'CashFlowStatement':
        """Validate that Operating + Investing + Financing = Net Change (CDM principle: validate at creation point)."""
        if (self.cash_from_operations and self.cash_from_investing and 
            self.cash_from_financing and self.net_change_in_cash):
            operating_amount = self.cash_from_operations.amount
            investing_amount = self.cash_from_investing.amount
            financing_amount = self.cash_from_financing.amount
            net_change_amount = self.net_change_in_cash.amount
            
            calculated_change = operating_amount + investing_amount + financing_amount
            
            # Allow small rounding differences (0.01)
            if abs(calculated_change - net_change_amount) > Decimal('0.01'):
                if self.extraction_status == ExtractionStatus.SUCCESS:
                    object.__setattr__(self, 'extraction_status', ExtractionStatus.PARTIAL)
        
        return self


# ============================================================================
# Tax Return Models
# ============================================================================


class TaxReturn(BaseModel):
    """Tax return with filing information, income, deductions, and tax liability."""
    extraction_status: ExtractionStatus = Field(
        default=ExtractionStatus.SUCCESS,
        description="Status of extraction: success, partial_data_missing, or irrelevant_document"
    )
    filing_status: Optional[FilingStatus] = Field(None, description="Filing status")
    tax_year: Optional[int] = Field(None, description="Tax year")
    filing_date: Optional[date] = Field(None, description="Filing date (ISO 8601: YYYY-MM-DD)")
    currency: Optional[Currency] = Field(None, description="Currency code for all amounts")
    
    adjusted_gross_income: Optional[Money] = Field(None, description="Adjusted gross income (AGI)")
    taxable_income: Optional[Money] = Field(None, description="Taxable income")
    
    standard_deduction: Optional[Money] = Field(None, description="Standard deduction")
    itemized_deductions: Optional[Money] = Field(None, description="Itemized deductions")
    business_deductions: Optional[Money] = Field(None, description="Business deductions")
    total_deductions: Optional[Money] = Field(None, description="Total deductions")
    
    federal_tax_owed: Optional[Money] = Field(None, description="Federal tax owed")
    state_tax_owed: Optional[Money] = Field(None, description="State tax owed")
    tax_credits: Optional[Money] = Field(None, description="Tax credits")
    total_tax_liability: Optional[Money] = Field(None, description="Total tax liability")
    
    tax_withheld: Optional[Money] = Field(None, description="Tax withheld")
    estimated_payments: Optional[Money] = Field(None, description="Estimated payments")
    refund_amount: Optional[Money] = Field(None, description="Refund amount (if positive)")
    amount_owed: Optional[Money] = Field(None, description="Amount owed (if positive)")
    
    @model_validator(mode='after')
    def validate_tax_return_equation(self) -> 'TaxReturn':
        """Validate that Income - Deductions = Taxable Income (CDM principle: validate at creation point)."""
        if self.adjusted_gross_income and self.total_deductions and self.taxable_income:
            agi_amount = self.adjusted_gross_income.amount
            deductions_amount = self.total_deductions.amount
            taxable_amount = self.taxable_income.amount
            
            calculated_taxable = agi_amount - deductions_amount
            
            # Allow small rounding differences (0.01)
            if abs(calculated_taxable - taxable_amount) > Decimal('0.01'):
                if self.extraction_status == ExtractionStatus.SUCCESS:
                    object.__setattr__(self, 'extraction_status', ExtractionStatus.PARTIAL)
        
        return self


# ============================================================================
# Union Type for Accounting Documents
# ============================================================================


AccountingDocument = Union[BalanceSheet, IncomeStatement, CashFlowStatement, TaxReturn]


# ============================================================================
# Extraction Result Envelope
# ============================================================================


class AccountingExtractionResult(BaseModel):
    """Envelope for accounting document extraction responses.
    
    Similar to ExtractionResult pattern, allows irrelevant documents
    to return FAILURE without requiring populated document fields.
    """
    extraction_status: ExtractionStatus = Field(
        default=ExtractionStatus.SUCCESS,
        description="Extraction status: success, partial_data_missing, or irrelevant_document"
    )
    agreement: Optional[AccountingDocument] = Field(
        None,
        description="The extracted accounting document when status is success or partial_data_missing"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message when status is failure/irrelevant_document"
    )
    
    @model_validator(mode='after')
    def validate_status_consistency(self) -> 'AccountingExtractionResult':
        """Adjust status if agreement is missing or incomplete."""
        if self.extraction_status == ExtractionStatus.FAILURE:
            return self
        if self.agreement is None:
            object.__setattr__(self, 'extraction_status', ExtractionStatus.FAILURE)
            object.__setattr__(self, 'message', "Could not extract data from this accounting document")
        elif hasattr(self.agreement, 'extraction_status') and self.agreement.extraction_status != ExtractionStatus.SUCCESS:
            object.__setattr__(self, 'extraction_status', self.agreement.extraction_status)
        return self

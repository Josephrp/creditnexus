"""LangChain orchestration for extracting structured accounting data.

Follows existing chain patterns from app/chains/extraction_chain.py
"""

import logging
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal
from pydantic import ValidationError

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_client import get_chat_model
from app.models.accounting_document import (
    BalanceSheet,
    IncomeStatement,
    CashFlowStatement,
    TaxReturn,
    AccountingExtractionResult
)

logger = logging.getLogger(__name__)

# Threshold for map-reduce (same as existing extraction chain)
MAP_REDUCE_THRESHOLD = 50000


def create_accounting_extraction_chain() -> BaseChatModel:
    """
    Create and configure the LangChain accounting extraction chain.
    
    Follows existing pattern from create_extraction_chain():
    - Uses LLM client abstraction
    - Temperature=0 for deterministic extraction
    - Binds Pydantic model as structured output
    
    Returns:
        BaseChatModel instance configured with structured output
        bound to AccountingExtractionResult Pydantic model.
    """
    # Use global LLM configuration (set at startup)
    llm = get_chat_model(temperature=0)  # Deterministic extraction
    
    # Bind the Pydantic model as a structured output tool
    structured_llm = llm.with_structured_output(AccountingExtractionResult)
    
    return structured_llm


def create_accounting_extraction_prompt() -> ChatPromptTemplate:
    """
    Create prompt template for accounting document extraction.
    
    Follows existing pattern from create_extraction_prompt():
    - System prompt with clear extraction responsibilities
    - User prompt with placeholder for document text
    - Emphasizes quantitative accuracy and CDM compliance
    """
    system_prompt = """You are an expert Financial Accountant and Quantitative Data Analyst. Your task is to extract comprehensive structured data from accounting documents with absolute numerical accuracy.

CORE EXTRACTION RESPONSIBILITIES:

1. BALANCE SHEET EXTRACTION:
   - Extract Assets:
     * Current Assets: Cash, Accounts Receivable, Inventory, Prepaid Expenses
     * Non-Current Assets: Property/Plant/Equipment, Intangible Assets, Investments
   - Extract Liabilities:
     * Current Liabilities: Accounts Payable, Short-term Debt, Accrued Expenses
     * Non-Current Liabilities: Long-term Debt, Deferred Tax Liabilities
   - Extract Equity:
     * Common Stock, Retained Earnings, Additional Paid-in Capital
   - VALIDATION: Total Assets MUST equal Total Liabilities + Total Equity
   - All amounts must use Decimal type (never float)
   - All amounts must include currency code (USD, EUR, GBP, etc.)

2. INCOME STATEMENT EXTRACTION:
   - Extract Revenue:
     * Gross Revenue, Net Revenue, Revenue by Segment (if available)
   - Extract Cost of Goods Sold (COGS):
     * Direct costs, Materials, Labor
   - Extract Operating Expenses:
     * SG&A, R&D, Depreciation, Amortization
   - Extract Other Income/Expenses:
     * Interest Income, Interest Expense, Tax Expense
   - Extract Net Income:
     * Net Income Before Tax, Net Income After Tax
   - VALIDATION: Revenue - COGS - Operating Expenses - Other Expenses = Net Income
   - Extract Earnings Per Share (EPS) if available

3. CASH FLOW STATEMENT EXTRACTION:
   - Extract Operating Activities:
     * Net Income, Depreciation, Changes in Working Capital, Cash from Operations
   - Extract Investing Activities:
     * Capital Expenditures, Asset Sales, Investments
   - Extract Financing Activities:
     * Debt Issuance/Repayment, Equity Issuance, Dividends Paid
   - Extract Net Change in Cash:
     * Beginning Cash, Ending Cash, Net Change
   - VALIDATION: Operating + Investing + Financing = Net Change in Cash

4. TAX RETURN EXTRACTION:
   - Extract Filing Information:
     * Filing Status (Single, Married Filing Jointly, etc.)
     * Tax Year, Filing Date
   - Extract Income:
     * Adjusted Gross Income (AGI), Taxable Income
   - Extract Deductions:
     * Standard Deduction, Itemized Deductions, Business Deductions
   - Extract Tax Liability:
     * Federal Tax Owed, State Tax Owed, Tax Credits
   - Extract Refund/Payment:
     * Tax Withheld, Estimated Payments, Refund Amount, Amount Owed

5. REPORTING PERIOD EXTRACTION:
   - Extract Period Type: Annual, Quarterly, Monthly, Year-to-Date
   - Extract Period Dates: Start Date (ISO 8601), End Date (ISO 8601)
   - Extract Fiscal Year if different from calendar year
   - Extract Comparative Period Data if available (prior year, prior quarter)

6. QUANTITATIVE VALIDATION:
   - Balance Sheet: Assets = Liabilities + Equity (must balance)
   - Income Statement: Revenue - Expenses = Net Income
   - Cash Flow: Operating + Investing + Financing = Net Change in Cash
   - Tax Return: Income - Deductions = Taxable Income
   - If validation fails, mark extraction_status as "partial_data_missing"

7. EXTRACTION STATUS:
   - success: All data extracted and validated correctly
   - partial_data_missing: Some fields missing or validation failed
   - irrelevant_document: Not an accounting document

CRITICAL RULES:
- If a field is not explicitly stated, return None/Null. Do not guess or infer values.
- All monetary amounts MUST use Decimal type (never float)
- All dates MUST be in ISO 8601 format (YYYY-MM-DD)
- All amounts MUST include currency code
- For percentages, convert to decimal (e.g., 5% = 0.05)
- Preserve original text structure when possible for audit purposes
- If text appears corrupted or unreadable, mark appropriate fields as missing
- Handle multi-period documents (e.g., quarterly statements with 4 quarters)
- Extract footnotes and notes if they contain quantitative data
"""

    user_prompt = """Extract accounting data from the following document text:

Document Text:
{text}

Document Type (if known): {document_type}

Extract all available quantitative data and return it in the structured format.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    return prompt


def extract_accounting_data(
    text: str,
    document_type: Optional[str] = None,
    max_retries: int = 3
) -> AccountingExtractionResult:
    """
    Extract structured accounting data from unstructured text.
    
    Follows existing pattern from extract_data():
    - Implements Reflexion retry pattern
    - Handles validation errors with feedback
    - Logs extraction attempts
    
    Args:
        text: The raw text content of an accounting document
        document_type: Optional document type hint (balance_sheet, income_statement, etc.)
        max_retries: Maximum number of validation retries (default: 3)
        
    Returns:
        An AccountingExtractionResult Pydantic model instance
        
    Raises:
        ValueError: If extraction fails after retries
    """
    prompt = create_accounting_extraction_prompt()
    structured_llm = create_accounting_extraction_chain()
    extraction_chain = prompt | structured_llm
    
    last_error: Exception | None = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Accounting extraction attempt {attempt + 1}/{max_retries}...")
            
            if attempt == 0:
                # First attempt: normal extraction
                result = extraction_chain.invoke({
                    "text": text,
                    "document_type": document_type or "unknown"
                })
            else:
                # Retry attempts: include validation error feedback
                error_feedback = f"""
Previous extraction attempt failed with validation error:
{str(last_error)}

Please correct the following issues:
1. Review the validation error above
2. Ensure all dates are valid and in ISO 8601 format (YYYY-MM-DD)
3. Ensure all monetary amounts use Decimal type
4. Verify balance sheet equation: Assets = Liabilities + Equity
5. Verify income statement equation: Revenue - Expenses = Net Income
6. Verify cash flow equation: Operating + Investing + Financing = Net Change in Cash

Original Document Text:
{text}
"""
                result = extraction_chain.invoke({
                    "text": error_feedback,
                    "document_type": document_type or "unknown"
                })
            
            # Validate quantitative relationships
            if result.agreement:
                validation_errors = _validate_accounting_data(result.agreement)
                if validation_errors:
                    logger.warning(f"Quantitative validation errors: {validation_errors}")
                    if result.extraction_status.value == "success":
                        from app.models.cdm import ExtractionStatus
                        object.__setattr__(result, 'extraction_status', ExtractionStatus.PARTIAL)
            
            logger.info("Accounting extraction completed successfully")
            return result
            
        except ValidationError as e:
            last_error = e
            logger.warning(f"Validation error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                logger.info("Retrying with validation feedback...")
                continue
            raise ValueError(f"Accounting extraction failed validation after {max_retries} attempts: {e}") from e
            
        except Exception as e:
            logger.error(f"Unexpected error during accounting extraction: {e}")
            raise ValueError(f"Accounting extraction failed: {e}") from e


def _validate_accounting_data(document: Union[BalanceSheet, IncomeStatement, CashFlowStatement, TaxReturn]) -> List[str]:
    """
    Validate quantitative relationships in accounting data.
    
    Returns list of validation error messages (empty if valid).
    """
    errors = []
    
    if isinstance(document, BalanceSheet):
        # Validate: Assets = Liabilities + Equity
        if document.total_assets and document.total_liabilities and document.total_equity:
            total_assets = document.total_assets.amount
            total_liabilities_equity = document.total_liabilities.amount + document.total_equity.amount
            if abs(total_assets - total_liabilities_equity) > Decimal('0.01'):
                errors.append(
                    f"Balance sheet does not balance: "
                    f"Assets ({total_assets}) != Liabilities + Equity ({total_liabilities_equity})"
                )
    
    elif isinstance(document, IncomeStatement):
        # Validate: Revenue - Expenses = Net Income
        if document.total_revenue and document.total_expenses and document.net_income:
            revenue = document.total_revenue.amount
            expenses = document.total_expenses.amount
            net_income = document.net_income.amount
            calculated_net = revenue - expenses
            if abs(calculated_net - net_income) > Decimal('0.01'):
                errors.append(
                    f"Income statement does not balance: "
                    f"Revenue ({revenue}) - Expenses ({expenses}) = {calculated_net}, "
                    f"but Net Income is {net_income}"
                )
    
    elif isinstance(document, CashFlowStatement):
        # Validate: Operating + Investing + Financing = Net Change
        if (document.cash_from_operations and document.cash_from_investing and 
            document.cash_from_financing and document.net_change_in_cash):
            operating = document.cash_from_operations.amount
            investing = document.cash_from_investing.amount
            financing = document.cash_from_financing.amount
            net_change = document.net_change_in_cash.amount
            calculated_change = operating + investing + financing
            if abs(calculated_change - net_change) > Decimal('0.01'):
                errors.append(
                    f"Cash flow statement does not balance: "
                    f"Operating ({operating}) + Investing ({investing}) + Financing ({financing}) = {calculated_change}, "
                    f"but Net Change is {net_change}"
                )
    
    elif isinstance(document, TaxReturn):
        # Validate: Income - Deductions = Taxable Income
        if (document.adjusted_gross_income and document.total_deductions and 
            document.taxable_income):
            agi = document.adjusted_gross_income.amount
            deductions = document.total_deductions.amount
            taxable = document.taxable_income.amount
            calculated_taxable = agi - deductions
            if abs(calculated_taxable - taxable) > Decimal('0.01'):
                errors.append(
                    f"Tax return does not balance: "
                    f"AGI ({agi}) - Deductions ({deductions}) = {calculated_taxable}, "
                    f"but Taxable Income is {taxable}"
                )
    
    return errors


def create_partial_accounting_extraction_chain() -> BaseChatModel:
    """
    Create a chain for extracting partial accounting data from document sections.
    
    Returns:
        BaseChatModel instance configured with structured output
        bound to AccountingExtractionResult (with partial data).
    """
    llm = get_chat_model(temperature=0)
    structured_llm = llm.with_structured_output(AccountingExtractionResult)
    return structured_llm


def create_partial_accounting_extraction_prompt() -> ChatPromptTemplate:
    """
    Create prompt for partial extraction from accounting document sections.
    
    Returns:
        ChatPromptTemplate optimized for extracting partial accounting data.
    """
    system_prompt = """You are an expert Financial Accountant extracting data from a SECTION of an accounting document.

This is only ONE SECTION of a larger document. Extract whatever information is present in this section.
Do not worry if some fields are missing - they may be in other sections.

Your task:
1. Extract any monetary amounts and currencies from this section
2. Extract any dates (reporting period, fiscal year)
3. Extract any account balances (Assets, Liabilities, Equity, Revenue, Expenses)
4. Extract any financial ratios or percentages
5. Identify the document type if mentioned (Balance Sheet, Income Statement, etc.)

CRITICAL RULES:
- Only extract what is EXPLICITLY stated in this section
- Return None/Null for fields not present in this section
- All monetary amounts MUST use Decimal type (never float)
- All dates MUST be in ISO 8601 format (YYYY-MM-DD)
- All amounts MUST include currency code
- Do not infer or guess values
- If document type is unclear, use "unknown"
"""

    user_prompt = """Document Section:
{text}

Document Type (if known): {document_type}

Extract all relevant accounting data from this section."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    return prompt


def create_accounting_reducer_chain() -> BaseChatModel:
    """
    Create a reducer chain for merging partial accounting extractions.
    
    Returns:
        BaseChatModel instance configured with structured output
        bound to AccountingExtractionResult.
    """
    llm = get_chat_model(temperature=0)
    structured_llm = llm.with_structured_output(AccountingExtractionResult)
    return structured_llm


def create_accounting_reducer_prompt() -> ChatPromptTemplate:
    """
    Create prompt for the reducer agent that merges partial accounting extractions.
    
    Returns:
        ChatPromptTemplate for merging partial accounting data.
    """
    system_prompt = """You are an expert Financial Accountant tasked with MERGING partial extractions from multiple sections of an accounting document into a single, complete accounting document.

You will receive multiple AccountingExtractionResult objects extracted from different sections of the document.

Your task:
1. Merge all monetary amounts, preferring the most complete values
2. Combine reporting period information (prefer the most specific dates)
3. Ensure currency consistency across all amounts
4. Validate quantitative relationships (Assets = Liabilities + Equity, etc.)
5. Select the most appropriate document type if multiple types were detected

CRITICAL RULES:
- If the same field appears multiple times, prefer the most complete value
- Ensure all amounts use the same currency (convert if necessary)
- Validate that equations balance (Assets = Liabilities + Equity, etc.)
- If validation fails, mark extraction_status as "partial_data_missing"
- All dates must be in ISO 8601 format (YYYY-MM-DD)
- All amounts must use Decimal type
"""

    user_prompt = """Partial Extractions from Document Sections:

{partial_extractions}

Merge these partial extractions into a single, complete accounting document.
Ensure all quantitative relationships are validated."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    return prompt


def _split_accounting_document(text: str, max_chunk_size: int = 8000) -> List[Dict[str, Any]]:
    """
    Split accounting document into chunks for map-reduce processing.
    
    Tries to split by logical sections (ASSETS, LIABILITIES, REVENUE, etc.),
    otherwise splits by paragraphs.
    
    Args:
        text: The full document text
        max_chunk_size: Maximum characters per chunk
        
    Returns:
        List of chunk dictionaries with text and metadata
    """
    import re
    
    chunks = []
    
    # Try to split by common accounting document sections
    section_patterns = [
        r'(ASSETS?|ASSETS\s+AND\s+LIABILITIES?)',
        r'(LIABILITIES?|LIABILITIES\s+AND\s+EQUITY)',
        r'(EQUITY|SHAREHOLDERS?\s+EQUITY)',
        r'(REVENUE|INCOME|REVENUES?)',
        r'(EXPENSES?|COSTS?)',
        r'(OPERATING\s+ACTIVITIES?)',
        r'(INVESTING\s+ACTIVITIES?)',
        r'(FINANCING\s+ACTIVITIES?)',
    ]
    
    combined_pattern = re.compile(
        '|'.join(f'({pattern})' for pattern in section_patterns),
        re.IGNORECASE | re.MULTILINE
    )
    
    section_matches = list(combined_pattern.finditer(text))
    
    if section_matches and len(section_matches) > 1:
        # Split by sections
        for idx, match in enumerate(section_matches):
            start_pos = match.start()
            end_pos = section_matches[idx + 1].start() if idx + 1 < len(section_matches) else len(text)
            section_text = text[start_pos:end_pos].strip()
            
            # If section is too long, split it further
            if len(section_text) > max_chunk_size:
                # Split by paragraphs
                paragraphs = section_text.split('\n\n')
                current_chunk = ""
                for para in paragraphs:
                    if len(current_chunk) + len(para) > max_chunk_size and current_chunk:
                        chunks.append({
                            "text": current_chunk,
                            "section": match.group(0),
                            "chunk_index": len(chunks)
                        })
                        current_chunk = para
                    else:
                        current_chunk += "\n\n" + para if current_chunk else para
                
                if current_chunk:
                    chunks.append({
                        "text": current_chunk,
                        "section": match.group(0),
                        "chunk_index": len(chunks)
                    })
            else:
                chunks.append({
                    "text": section_text,
                    "section": match.group(0),
                    "chunk_index": len(chunks)
                })
    else:
        # No sections found, split by paragraphs
        paragraphs = text.split('\n\n')
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) > max_chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk,
                    "section": None,
                    "chunk_index": len(chunks)
                })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append({
                "text": current_chunk,
                "section": None,
                "chunk_index": len(chunks)
            })
    
    return chunks


def extract_accounting_data_map_reduce(
    text: str,
    document_type: Optional[str] = None,
    max_retries: int = 3
) -> AccountingExtractionResult:
    """
    Extract structured accounting data from a long document using Map-Reduce strategy.
    
    This function:
    1. Splits the document into sections
    2. Extracts partial data from each section (MAP phase)
    3. Merges all partials into a complete accounting document (REDUCE phase)
    
    Args:
        text: The full text content of an accounting document
        document_type: Optional document type hint
        max_retries: Maximum number of validation retries
        
    Returns:
        AccountingExtractionResult instance
        
    Raises:
        ValueError: If extraction or merging fails
    """
    try:
        logger.info("Starting Map-Reduce extraction for long accounting document...")
        
        # Step 1: Split document into chunks
        chunks = _split_accounting_document(text)
        logger.info(f"Split document into {len(chunks)} chunks")
        
        if not chunks:
            raise ValueError("Document splitting produced no chunks")
        
        # Step 2: MAP phase - Extract partial data from each chunk
        partial_chain = create_partial_accounting_extraction_prompt() | create_partial_accounting_extraction_chain()
        partial_extractions = []
        
        for chunk in chunks:
            try:
                logger.info(f"Extracting from chunk {chunk['chunk_index'] + 1}/{len(chunks)}...")
                partial_result = partial_chain.invoke({
                    "text": chunk["text"],
                    "document_type": document_type or "unknown"
                })
                partial_extractions.append(partial_result)
            except Exception as e:
                logger.warning(f"Failed to extract from chunk {chunk['chunk_index']}: {e}")
                continue
        
        if not partial_extractions:
            raise ValueError("No partial extractions succeeded")
        
        logger.info(f"Successfully extracted from {len(partial_extractions)} chunks")
        
        # Step 3: REDUCE phase - Merge partial extractions
        reducer_chain = create_accounting_reducer_prompt() | create_accounting_reducer_chain()
        
        # Format partial extractions for reducer
        partial_extractions_text = "\n\n---\n\n".join([
            f"Partial Extraction {i+1}:\n{extraction.model_dump_json(indent=2)}"
            for i, extraction in enumerate(partial_extractions)
        ])
        
        logger.info("Merging partial extractions...")
        final_result = reducer_chain.invoke({
            "partial_extractions": partial_extractions_text
        })
        
        # Step 4: Validate quantitative relationships
        if final_result.agreement:
            validation_errors = _validate_accounting_data(final_result.agreement)
            if validation_errors:
                logger.warning(f"Quantitative validation errors after merge: {validation_errors}")
                from app.models.cdm import ExtractionStatus
                if final_result.extraction_status.value == "success":
                    object.__setattr__(final_result, 'extraction_status', ExtractionStatus.PARTIAL)
        
        logger.info("Map-Reduce extraction completed successfully")
        return final_result
        
    except Exception as e:
        logger.error(f"Map-Reduce extraction failed: {e}", exc_info=True)
        raise ValueError(f"Accounting extraction (map-reduce) failed: {e}") from e


def extract_accounting_data_smart(
    text: str,
    document_type: Optional[str] = None,
    force_map_reduce: bool = False,
    max_retries: int = 3
) -> AccountingExtractionResult:
    """
    Extract accounting data with automatic strategy selection.
    
    Follows existing pattern from extract_data_smart():
    - Automatically chooses between simple and map-reduce
    - Uses map-reduce for documents >50k characters
    
    Args:
        text: The raw text content
        document_type: Optional document type hint
        force_map_reduce: If True, always use map-reduce
        max_retries: Maximum number of validation retries
        
    Returns:
        AccountingExtractionResult instance
    """
    text_length = len(text)
    
    if force_map_reduce or text_length > MAP_REDUCE_THRESHOLD:
        logger.info(f"Document length ({text_length} chars) exceeds threshold, using Map-Reduce strategy")
        return extract_accounting_data_map_reduce(text, document_type, max_retries)
    else:
        logger.info(f"Document length ({text_length} chars) within threshold, using simple extraction")
        return extract_accounting_data(text, document_type, max_retries)

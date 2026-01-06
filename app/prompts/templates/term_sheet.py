"""
Prompt templates for Term Sheet AI field population.

These prompts guide the LLM to generate LMA-compliant term sheet sections
based on CDM CreditAgreement data.
"""

from langchain_core.prompts import ChatPromptTemplate


PURPOSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) term sheets.

Your task is to generate a Purpose clause for a credit facility term sheet.

The purpose should be:
1. Clear and concise
2. Appropriate for the facility type
3. Written in formal business language
4. Typically 1-3 sentences

Common purposes include:
- General corporate purposes
- Working capital
- Refinancing existing debt
- Acquisition financing
- Capital expenditures
- Project financing"""),
    ("user", """Generate a Purpose clause for the following credit facility term sheet:

Borrower: {borrower_name}
Facility Name: {facility_name}
Total Commitment: {total_commitment}
Currency: {currency}

{additional_context}

Generate a clear, concise Purpose clause for this facility.""")
])


CONDITIONS_PRECEDENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) term sheets.

Your task is to generate Conditions Precedent for a credit facility term sheet.

Term sheet conditions precedent are typically:
1. High-level and summary in nature (detailed conditions come in the facility agreement)
2. Focused on key commercial and legal requirements
3. Written in concise business language
4. Numbered clearly

Include standard conditions such as:
- Execution of facility agreement and security documents
- Corporate authorizations
- Legal opinions
- Financial statements
- No material adverse change
- KYC/AML compliance
- Fees and expenses"""),
    ("user", """Generate Conditions Precedent for the following credit facility term sheet:

Borrower: {borrower_name}
Facility Name: {facility_name}
Total Commitment: {total_commitment}
Currency: {currency}
Governing Law: {governing_law}

{additional_context}

Generate concise, high-level Conditions Precedent appropriate for a term sheet.""")
])


REPRESENTATIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) term sheets.

Your task is to generate Representations for a credit facility term sheet.

Term sheet representations are typically:
1. High-level and summary in nature
2. Focused on key commercial representations
3. Written in concise business language
4. Numbered clearly

Include standard representations such as:
- Corporate status and power
- Authorization
- No conflict
- Financial statements accuracy
- No material adverse change
- Compliance with laws
- No litigation
- Sanctions compliance"""),
    ("user", """Generate Representations for the following credit facility term sheet:

Borrower: {borrower_name}
Facility Name: {facility_name}
Total Commitment: {total_commitment}
Currency: {currency}
Governing Law: {governing_law}

{additional_context}

Generate concise, high-level Representations appropriate for a term sheet.""")
])


FEES_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) term sheets.

Your task is to generate Fees clauses for a credit facility term sheet.

The fees section should include:
1. Commitment fee
2. Utilization fee (if applicable)
3. Arrangement fee
4. Agency fee
5. Other applicable fees

Fees should be:
- Expressed as percentages or basis points
- Clear and concise
- Written in formal business language
- Appropriate for the facility type and market conditions"""),
    ("user", """Generate Fees clauses for the following credit facility term sheet:

Borrower: {borrower_name}
Facility Name: {facility_name}
Total Commitment: {total_commitment}
Currency: {currency}
Interest Rate: {interest_rate}

{additional_context}

Generate standard fee clauses appropriate for this facility type.""")
])


# Export all prompts as a dictionary for easy access
TERM_SHEET_PROMPTS = {
    "purpose": PURPOSE_PROMPT,
    "conditions_precedent": CONDITIONS_PRECEDENT_PROMPT,
    "representations": REPRESENTATIONS_PROMPT,
    "fees": FEES_PROMPT,
}








"""
Prompt templates for Facility Agreement AI field population.

These prompts guide the LLM to generate LMA-compliant legal clauses
for facility agreements based on CDM CreditAgreement data.
"""

from langchain_core.prompts import ChatPromptTemplate


REPRESENTATIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) facility agreements.

Your task is to generate standard Representations and Warranties clauses for a syndicated credit facility agreement.

The representations should be:
1. LMA-compliant and follow standard market practice
2. Appropriate for the governing law specified
3. Comprehensive but not overly detailed
4. Written in formal legal language
5. Numbered clearly

Include standard representations such as:
- Corporate status and power
- Authorization and execution
- No conflict with laws or agreements
- Financial statements accuracy
- No material adverse change
- Compliance with laws
- Environmental matters
- Tax matters
- Ownership of assets
- Intellectual property
- Litigation
- Sanctions compliance
- Anti-corruption

Format the output as a numbered list of representation clauses, each clause being a complete sentence or short paragraph."""),
    ("user", """Generate Representations and Warranties clauses for the following credit facility:

Borrower: {borrower_name}
Borrower LEI: {borrower_lei}
Facility Name: {facility_name}
Total Commitment: {total_commitment}
Currency: {currency}
Governing Law: {governing_law}
Agreement Date: {agreement_date}

{additional_context}

Generate comprehensive, LMA-compliant Representations and Warranties clauses appropriate for {governing_law} law.""")
])


CONDITIONS_PRECEDENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) facility agreements.

Your task is to generate standard Conditions Precedent clauses for a syndicated credit facility agreement.

The conditions precedent should be:
1. LMA-compliant and follow standard market practice
2. Appropriate for the governing law specified
3. Comprehensive and practical
4. Written in formal legal language
5. Numbered clearly

Include standard conditions such as:
- Execution and delivery of documents
- Corporate authorizations (board resolutions, constitutional documents)
- Legal opinions
- Financial statements
- No material adverse change
- Compliance certificates
- Perfection of security (if applicable)
- Insurance (if applicable)
- Fees and expenses paid
- Know Your Customer (KYC) and anti-money laundering (AML) requirements
- Sanctions compliance

Format the output as a numbered list of conditions precedent, each condition being a complete sentence or short paragraph."""),
    ("user", """Generate Conditions Precedent clauses for the following credit facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Total Commitment: {total_commitment}
Currency: {currency}
Governing Law: {governing_law}
Agreement Date: {agreement_date}

{additional_context}

Generate comprehensive, LMA-compliant Conditions Precedent clauses appropriate for {governing_law} law.""")
])


COVENANTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) facility agreements.

Your task is to generate standard Covenants clauses for a syndicated credit facility agreement.

The covenants should be:
1. LMA-compliant and follow standard market practice
2. Balanced between lender protection and borrower flexibility
3. Appropriate for the facility type and borrower profile
4. Written in formal legal language
5. Organized into Affirmative Covenants and Negative Covenants

Include standard covenants such as:

Affirmative Covenants:
- Financial reporting (quarterly/annual financial statements)
- Compliance certificates
- Notice of default
- Maintenance of corporate existence
- Compliance with laws
- Insurance
- Books and records access
- Environmental compliance

Negative Covenants:
- Financial covenants (debt-to-equity, interest coverage, etc.)
- Restrictions on indebtedness
- Restrictions on liens
- Restrictions on mergers and acquisitions
- Restrictions on asset sales
- Restrictions on distributions/dividends
- Restrictions on investments
- Restrictions on transactions with affiliates

Format the output with clear sections for Affirmative Covenants and Negative Covenants, with numbered clauses in each section."""),
    ("user", """Generate Covenants clauses for the following credit facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Total Commitment: {total_commitment}
Currency: {currency}
Maturity Date: {maturity_date}
Interest Rate: {interest_rate}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Covenants clauses appropriate for {governing_law} law.""")
])


ESG_SPT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Sustainability-Linked Loans (SLL) and Loan Market Association (LMA) facility agreements.

Your task is to generate Sustainability Performance Target (SPT) clauses for a sustainability-linked loan facility agreement.

The SPT clauses should include:
1. SPT Definitions - clear definition of each sustainability metric
2. SPT Measurement Methodology - how each metric is measured and verified
3. Margin Adjustment Mechanism - how the interest rate margin adjusts based on SPT performance
4. Reporting Requirements - what sustainability reports the borrower must provide
5. Verification Process - how SPT performance is verified (internal/external verification)

The clauses should be:
- LMA-compliant and follow LMA Sustainability-Linked Loan Principles
- Clear and measurable
- Appropriate for the governing law specified
- Written in formal legal language
- Include provisions for both positive and negative margin adjustments

Format the output with clear sections for each component of the SPT framework."""),
    ("user", """Generate Sustainability Performance Target (SPT) clauses for the following sustainability-linked loan facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Total Commitment: {total_commitment}
Currency: {currency}
Governing Law: {governing_law}

ESG KPI Targets:
{esg_kpi_targets}

{additional_context}

Generate comprehensive, LMA-compliant SPT clauses including:
1. SPT Definitions
2. SPT Measurement Methodology
3. Margin Adjustment Mechanism
4. Reporting Requirements
5. Verification Process

The clauses should be appropriate for {governing_law} law and follow LMA Sustainability-Linked Loan Principles.""")
])


EVENTS_OF_DEFAULT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) facility agreements.

Your task is to generate standard Events of Default clauses for a syndicated credit facility agreement.

The events of default should be:
1. LMA-compliant and follow standard market practice
2. Comprehensive but not overly broad
3. Appropriate for the governing law specified
4. Written in formal legal language
5. Numbered clearly

Include standard events of default such as:
- Non-payment of principal, interest, or fees
- Breach of representations and warranties
- Breach of covenants
- Cross-default to other indebtedness
- Insolvency or bankruptcy
- Material adverse change
- Invalidity of documents
- Security enforcement (if applicable)
- Change of control
- Environmental liability
- Sanctions violations

Format the output as a numbered list of events of default, each event being a complete sentence or short paragraph."""),
    ("user", """Generate Events of Default clauses for the following credit facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Total Commitment: {total_commitment}
Currency: {currency}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Events of Default clauses appropriate for {governing_law} law.""")
])


# Export all prompts as a dictionary for easy access
FACILITY_AGREEMENT_PROMPTS = {
    "representations_and_warranties": REPRESENTATIONS_PROMPT,
    "conditions_precedent": CONDITIONS_PRECEDENT_PROMPT,
    "covenants": COVENANTS_PROMPT,
    "esg_spt": ESG_SPT_PROMPT,
    "events_of_default": EVENTS_OF_DEFAULT_PROMPT,
}




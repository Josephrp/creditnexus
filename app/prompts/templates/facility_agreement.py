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


GOVERNING_LAW_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) facility agreements.

Your task is to generate a Governing Law clause for a syndicated credit facility agreement.

The governing law clause should:
1. Specify the governing law jurisdiction
2. Include jurisdiction and venue provisions
3. Include service of process provisions
4. Be appropriate for the specified governing law
5. Follow LMA standard practice
6. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate a Governing Law clause for the following credit facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Governing Law: {governing_law}
Agreement Date: {agreement_date}

{additional_context}

Generate a comprehensive, LMA-compliant Governing Law clause appropriate for {governing_law} law.""")
])


# REF (Real Estate Finance) Specific Prompts

PROPERTY_DESCRIPTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) real estate finance facility agreements.

Your task is to generate Property Description clauses for a real estate finance facility agreement.

The property description should:
1. Clearly identify the property or properties securing the loan
2. Include physical address, legal description, and property type
3. Describe the property's use (commercial, residential, mixed-use, etc.)
4. Include any relevant property characteristics (size, zoning, etc.)
5. Be appropriate for the governing law specified
6. Follow LMA standard practice
7. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate Property Description clauses for the following real estate finance facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Property Address: {property_address}
Property Type: {property_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Property Description clauses appropriate for {governing_law} law.""")
])


SECURITY_PACKAGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) real estate finance facility agreements.

Your task is to generate Security Package clauses for a real estate finance facility agreement.

The security package should:
1. Describe all security interests granted to secure the facility
2. Include mortgages, charges, assignments, and other security interests
3. Specify the ranking and priority of security interests
4. Include provisions for additional security if required
5. Be appropriate for the governing law specified
6. Follow LMA standard practice
7. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate Security Package clauses for the following real estate finance facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Security Type: {security_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Security Package clauses appropriate for {governing_law} law.""")
])


VALUATION_REQUIREMENTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) real estate finance facility agreements.

Your task is to generate Valuation Requirements clauses for a real estate finance facility agreement.

The valuation requirements should:
1. Specify when valuations are required (initial, periodic, event-driven)
2. Define the type and standard of valuations required
3. Specify who may perform valuations (qualified valuers)
4. Include provisions for valuation disputes
5. Specify loan-to-value (LTV) requirements and triggers
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate Valuation Requirements clauses for the following real estate finance facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Valuation Frequency: {valuation_frequency}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Valuation Requirements clauses appropriate for {governing_law} law.""")
])


# SLL (Sustainability-Linked Loan) Specific Prompts

SPT_MEASUREMENT_METHODOLOGY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Sustainability-Linked Loans (SLL) and Loan Market Association (LMA) facility agreements.

Your task is to generate SPT Measurement Methodology clauses for a sustainability-linked loan facility agreement.

The measurement methodology should:
1. Clearly define how each Sustainability Performance Target (SPT) is measured
2. Specify the measurement period and frequency
3. Define the data sources and calculation methods
4. Include provisions for data quality and verification
5. Address any adjustments or normalization required
6. Be appropriate for the governing law specified
7. Follow LMA Sustainability-Linked Loan Principles
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate SPT Measurement Methodology clauses for the following sustainability-linked loan facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
ESG KPI Targets: {esg_kpi_targets}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant SPT Measurement Methodology clauses appropriate for {governing_law} law.""")
])


MARGIN_ADJUSTMENT_MECHANISM_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Sustainability-Linked Loans (SLL) and Loan Market Association (LMA) facility agreements.

Your task is to generate Margin Adjustment Mechanism clauses for a sustainability-linked loan facility agreement.

The margin adjustment mechanism should:
1. Clearly define how the interest rate margin adjusts based on SPT performance
2. Specify the base margin and adjustment ranges
3. Define performance thresholds and corresponding margin adjustments
4. Include provisions for both positive and negative adjustments
5. Specify when adjustments take effect
6. Address calculation methods and rounding
7. Be appropriate for the governing law specified
8. Follow LMA Sustainability-Linked Loan Principles
9. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate Margin Adjustment Mechanism clauses for the following sustainability-linked loan facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Base Margin: {base_margin}
Adjustment Range: {adjustment_bps} basis points
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Margin Adjustment Mechanism clauses appropriate for {governing_law} law.""")
])


REPORTING_REQUIREMENTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Sustainability-Linked Loans (SLL) and Loan Market Association (LMA) facility agreements.

Your task is to generate Reporting Requirements clauses for a sustainability-linked loan facility agreement.

The reporting requirements should:
1. Specify what sustainability reports the borrower must provide
2. Define the reporting frequency and deadlines
3. Specify the format and content of reports
4. Include provisions for third-party verification reports
5. Address confidentiality and disclosure of sustainability data
6. Be appropriate for the governing law specified
7. Follow LMA Sustainability-Linked Loan Principles
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate Reporting Requirements clauses for the following sustainability-linked loan facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Reporting Frequency: {reporting_frequency}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Reporting Requirements clauses appropriate for {governing_law} law.""")
])


VERIFICATION_PROCESS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Sustainability-Linked Loans (SLL) and Loan Market Association (LMA) facility agreements.

Your task is to generate Verification Process clauses for a sustainability-linked loan facility agreement.

The verification process should:
1. Define how SPT performance is verified (internal/external verification)
2. Specify who may perform verification (internal auditors, external verifiers)
3. Define verification standards and methodologies
4. Include provisions for verification reports and certificates
5. Address costs and timing of verification
6. Include provisions for verification disputes
7. Be appropriate for the governing law specified
8. Follow LMA Sustainability-Linked Loan Principles
9. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate Verification Process clauses for the following sustainability-linked loan facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Verification Type: {verification_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Verification Process clauses appropriate for {governing_law} law.""")
])


# Export all prompts as a dictionary for easy access
FACILITY_AGREEMENT_PROMPTS = {
    "representations_and_warranties": REPRESENTATIONS_PROMPT,
    "conditions_precedent": CONDITIONS_PRECEDENT_PROMPT,
    "covenants": COVENANTS_PROMPT,
    "esg_spt": ESG_SPT_PROMPT,
    "events_of_default": EVENTS_OF_DEFAULT_PROMPT,
    "governing_law_clause": GOVERNING_LAW_PROMPT,
    # REF (Real Estate Finance) prompts
    "property_description": PROPERTY_DESCRIPTION_PROMPT,
    "security_package": SECURITY_PACKAGE_PROMPT,
    "valuation_requirements": VALUATION_REQUIREMENTS_PROMPT,
    # SLL (Sustainability-Linked Loan) prompts
    "spt_measurement_methodology": SPT_MEASUREMENT_METHODOLOGY_PROMPT,
    "margin_adjustment_mechanism": MARGIN_ADJUSTMENT_MECHANISM_PROMPT,
    "reporting_requirements": REPORTING_REQUIREMENTS_PROMPT,
    "verification_process": VERIFICATION_PROCESS_PROMPT,
}

















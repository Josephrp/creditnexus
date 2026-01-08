"""
Prompt templates for Origination Documents AI field population.

These prompts guide the LLM to generate LMA-compliant clauses
for origination documents based on CDM CreditAgreement data.
"""

from langchain_core.prompts import ChatPromptTemplate


COMMITMENT_LETTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) origination documents.

Your task is to generate Commitment Letter clauses for a loan origination commitment letter.

The commitment letter should:
1. Clearly state the commitment amount and terms
2. Specify conditions precedent to the commitment
3. Include provisions for syndication and underwriting
4. Address fees and expenses
5. Include provisions for termination and withdrawal
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a commitment letter."""),
    ("user", """Generate Commitment Letter clauses for the following loan origination:

Borrower: {borrower_name}
Facility Name: {facility_name}
Commitment Amount: {commitment_amount}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Commitment Letter clauses appropriate for {governing_law} law.""")
])


UNDERWRITING_TERMS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) origination documents.

Your task is to generate Underwriting Terms clauses for a loan origination document.

The underwriting terms should:
1. Define the underwriting structure and responsibilities
2. Specify the underwriting commitment and allocation
3. Include provisions for underwriting fees and expenses
4. Address conditions to underwriting obligations
5. Include provisions for termination and withdrawal
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into an origination document."""),
    ("user", """Generate Underwriting Terms clauses for the following loan origination:

Borrower: {borrower_name}
Facility Name: {facility_name}
Underwriting Type: {underwriting_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Underwriting Terms clauses appropriate for {governing_law} law.""")
])


SYNDICATION_TERMS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) origination documents.

Your task is to generate Syndication Terms clauses for a loan origination document.

The syndication terms should:
1. Define the syndication structure and process
2. Specify the roles of arrangers, lead managers, and participants
3. Include provisions for syndication fees and expenses
4. Address allocation and distribution of commitments
5. Include provisions for syndication timeline and conditions
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into an origination document."""),
    ("user", """Generate Syndication Terms clauses for the following loan origination:

Borrower: {borrower_name}
Facility Name: {facility_name}
Syndication Structure: {syndication_structure}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Syndication Terms clauses appropriate for {governing_law} law.""")
])


# Export all prompts as a dictionary
ORIGINATION_PROMPTS = {
    "commitment_letter": COMMITMENT_LETTER_PROMPT,
    "underwriting_terms": UNDERWRITING_TERMS_PROMPT,
    "syndication_terms": SYNDICATION_TERMS_PROMPT,
}

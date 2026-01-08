"""
Prompt templates for Supporting Documents AI field population.

These prompts guide the LLM to generate LMA-compliant clauses
for supporting documents based on CDM CreditAgreement data.
"""

from langchain_core.prompts import ChatPromptTemplate


LEGAL_OPINION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) supporting documents.

Your task is to generate Legal Opinion clauses for a loan facility agreement.

The legal opinion should:
1. Define the legal opinion requirements and scope
2. Specify who may provide legal opinions (qualified counsel)
3. Include provisions for legal opinion content and form
4. Address legal opinion delivery and timing
5. Include provisions for legal opinion updates and qualifications
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate Legal Opinion clauses for the following facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Opinion Type: {opinion_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Legal Opinion clauses appropriate for {governing_law} law.""")
])


COMPLIANCE_CERTIFICATE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) supporting documents.

Your task is to generate Compliance Certificate clauses for a loan facility agreement.

The compliance certificate should:
1. Define the compliance certificate requirements and scope
2. Specify who may provide compliance certificates (authorized officers)
3. Include provisions for compliance certificate content and form
4. Address compliance certificate delivery and timing
5. Include provisions for compliance certificate updates and qualifications
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate Compliance Certificate clauses for the following facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Compliance Type: {compliance_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Compliance Certificate clauses appropriate for {governing_law} law.""")
])


AUTHORIZATION_RESOLUTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) supporting documents.

Your task is to generate Authorization Resolution clauses for a loan facility agreement.

The authorization resolution should:
1. Define the authorization resolution requirements and scope
2. Specify who may provide authorization resolutions (board of directors, shareholders)
3. Include provisions for authorization resolution content and form
4. Address authorization resolution delivery and timing
5. Include provisions for authorization resolution updates and qualifications
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a facility agreement."""),
    ("user", """Generate Authorization Resolution clauses for the following facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Authorization Type: {authorization_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Authorization Resolution clauses appropriate for {governing_law} law.""")
])


# Export all prompts as a dictionary
SUPPORTING_PROMPTS = {
    "legal_opinion": LEGAL_OPINION_PROMPT,
    "compliance_certificate": COMPLIANCE_CERTIFICATE_PROMPT,
    "authorization_resolution": AUTHORIZATION_RESOLUTION_PROMPT,
}

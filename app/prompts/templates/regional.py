"""
Prompt templates for Regional Documents AI field population.

These prompts guide the LLM to generate LMA-compliant clauses
for regional documents based on CDM CreditAgreement data.
"""

from langchain_core.prompts import ChatPromptTemplate


REGIONAL_COMPLIANCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) regional documents.

Your task is to generate Regional Compliance clauses for a regional loan facility agreement.

The regional compliance should:
1. Define the regional regulatory requirements applicable to the facility
2. Specify compliance obligations and reporting requirements
3. Include provisions for regional regulatory approvals and licenses
4. Address regional tax and withholding requirements
5. Include provisions for regional enforcement and remedies
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a regional facility agreement."""),
    ("user", """Generate Regional Compliance clauses for the following regional facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Region: {region}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Regional Compliance clauses appropriate for {governing_law} law.""")
])


JURISDICTION_SPECIFIC_PROVISIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) regional documents.

Your task is to generate Jurisdiction-Specific Provisions clauses for a regional loan facility agreement.

The jurisdiction-specific provisions should:
1. Define the specific legal requirements of the jurisdiction
2. Specify jurisdiction-specific compliance obligations
3. Include provisions for jurisdiction-specific approvals and licenses
4. Address jurisdiction-specific tax and regulatory requirements
5. Include provisions for jurisdiction-specific enforcement
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a regional facility agreement."""),
    ("user", """Generate Jurisdiction-Specific Provisions clauses for the following regional facility:

Borrower: {borrower_name}
Facility Name: {facility_name}
Jurisdiction: {jurisdiction}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Jurisdiction-Specific Provisions clauses appropriate for {governing_law} law.""")
])


# Export all prompts as a dictionary
REGIONAL_PROMPTS = {
    "regional_compliance": REGIONAL_COMPLIANCE_PROMPT,
    "jurisdiction_specific_provisions": JURISDICTION_SPECIFIC_PROVISIONS_PROMPT,
}

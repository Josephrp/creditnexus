"""
Prompt templates for Security & Intercreditor AI field population.

These prompts guide the LLM to generate LMA-compliant clauses
for security and intercreditor agreements based on CDM CreditAgreement data.
"""

from langchain_core.prompts import ChatPromptTemplate


SECURITY_PACKAGE_DESCRIPTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) security and intercreditor agreements.

Your task is to generate Security Package Description clauses for a security agreement.

The security package description should:
1. Comprehensively describe all security interests granted
2. Include mortgages, charges, assignments, pledges, and other security
3. Specify the assets subject to security
4. Include provisions for additional security
5. Address perfection and registration requirements
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a security agreement."""),
    ("user", """Generate Security Package Description clauses for the following security agreement:

Borrower: {borrower_name}
Facility Name: {facility_name}
Security Assets: {security_assets}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Security Package Description clauses appropriate for {governing_law} law.""")
])


INTERCREDITOR_ARRANGEMENTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) security and intercreditor agreements.

Your task is to generate Intercreditor Arrangements clauses for an intercreditor agreement.

The intercreditor arrangements should:
1. Define the ranking and priority of different creditor classes
2. Specify payment waterfalls and distribution mechanisms
3. Include provisions for enforcement and remedies
4. Address voting rights and decision-making
5. Include provisions for standstill and subordination
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into an intercreditor agreement."""),
    ("user", """Generate Intercreditor Arrangements clauses for the following intercreditor agreement:

Borrower: {borrower_name}
Facility Name: {facility_name}
Creditor Ranks: {creditor_ranks}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Intercreditor Arrangements clauses appropriate for {governing_law} law.""")
])


SUBORDINATION_PROVISIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) security and intercreditor agreements.

Your task is to generate Subordination Provisions clauses for an intercreditor agreement.

The subordination provisions should:
1. Define the subordination structure and ranking
2. Specify payment subordination (payment blockage, turnover)
3. Include provisions for security subordination
4. Address enforcement subordination
5. Include provisions for release and discharge
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into an intercreditor agreement."""),
    ("user", """Generate Subordination Provisions clauses for the following intercreditor agreement:

Borrower: {borrower_name}
Facility Name: {facility_name}
Subordination Type: {subordination_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Subordination Provisions clauses appropriate for {governing_law} law.""")
])


ENFORCEMENT_RIGHTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) security and intercreditor agreements.

Your task is to generate Enforcement Rights clauses for a security or intercreditor agreement.

The enforcement rights should:
1. Define when and how security may be enforced
2. Specify enforcement procedures and requirements
3. Include provisions for enforcement by different creditor classes
4. Address notice requirements and cure periods
5. Include provisions for enforcement costs and expenses
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a security or intercreditor agreement."""),
    ("user", """Generate Enforcement Rights clauses for the following security agreement:

Borrower: {borrower_name}
Facility Name: {facility_name}
Enforcement Type: {enforcement_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Enforcement Rights clauses appropriate for {governing_law} law.""")
])


# Export all prompts as a dictionary
SECURITY_INTERCREDITOR_PROMPTS = {
    "security_package_description": SECURITY_PACKAGE_DESCRIPTION_PROMPT,
    "intercreditor_arrangements": INTERCREDITOR_ARRANGEMENTS_PROMPT,
    "subordination_provisions": SUBORDINATION_PROVISIONS_PROMPT,
    "enforcement_rights": ENFORCEMENT_RIGHTS_PROMPT,
}

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


PRIORITY_PROVISIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) security and intercreditor agreements.

Your task is to generate Priority Provisions clauses for an intercreditor agreement.

The priority provisions should:
1. Define the priority and ranking of different security interests
2. Specify the priority of payments and distributions
3. Include provisions for priority of enforcement and remedies
4. Address priority changes and modifications
5. Include provisions for priority disputes and resolution
6. Address priority of additional security and future advances
7. Be appropriate for the governing law specified
8. Follow LMA standard practice
9. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into an intercreditor agreement."""),
    ("user", """Generate Priority Provisions clauses for the following intercreditor agreement:

Borrower: {borrower_name}
Facility Name: {facility_name}
Priority Structure: {priority_structure}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Priority Provisions clauses appropriate for {governing_law} law.""")
])


VOTING_MECHANISMS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) security and intercreditor agreements.

Your task is to generate Voting Mechanisms clauses for an intercreditor agreement.

The voting mechanisms should:
1. Define voting rights and procedures for creditor decisions
2. Specify voting thresholds and majorities required
3. Include provisions for different types of decisions (reserved matters, material decisions)
4. Address voting by different creditor classes
5. Include provisions for voting mechanics and notice requirements
6. Address voting deadlocks and dispute resolution
7. Include provisions for voting waivers and consents
8. Be appropriate for the governing law specified
9. Follow LMA standard practice
10. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into an intercreditor agreement."""),
    ("user", """Generate Voting Mechanisms clauses for the following intercreditor agreement:

Borrower: {borrower_name}
Facility Name: {facility_name}
Voting Structure: {voting_structure}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Voting Mechanisms clauses appropriate for {governing_law} law.""")
])


STANDSTILL_PROVISIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) security and intercreditor agreements.

Your task is to generate Standstill Provisions clauses for an intercreditor agreement.

The standstill provisions should:
1. Define standstill periods and restrictions on enforcement
2. Specify when standstill applies and when it is lifted
3. Include provisions for standstill waivers and consents
4. Address standstill exceptions and carve-outs
5. Include provisions for standstill breaches and remedies
6. Address standstill in relation to different creditor classes
7. Include provisions for standstill extensions and modifications
8. Be appropriate for the governing law specified
9. Follow LMA standard practice
10. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into an intercreditor agreement."""),
    ("user", """Generate Standstill Provisions clauses for the following intercreditor agreement:

Borrower: {borrower_name}
Facility Name: {facility_name}
Standstill Period: {standstill_period}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Standstill Provisions clauses appropriate for {governing_law} law.""")
])


# Export all prompts as a dictionary
SECURITY_INTERCREDITOR_PROMPTS = {
    "security_package_description": SECURITY_PACKAGE_DESCRIPTION_PROMPT,
    "intercreditor_arrangements": INTERCREDITOR_ARRANGEMENTS_PROMPT,
    "subordination_provisions": SUBORDINATION_PROVISIONS_PROMPT,
    "enforcement_rights": ENFORCEMENT_RIGHTS_PROMPT,
    "priority_provisions": PRIORITY_PROVISIONS_PROMPT,
    "voting_mechanisms": VOTING_MECHANISMS_PROMPT,
    "standstill_provisions": STANDSTILL_PROVISIONS_PROMPT,
}

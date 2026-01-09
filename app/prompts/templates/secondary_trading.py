"""
Prompt templates for Secondary Trading AI field population.

These prompts guide the LLM to generate LMA-compliant clauses
for secondary loan trading documents based on CDM CreditAgreement data.
"""

from langchain_core.prompts import ChatPromptTemplate


ASSIGNMENT_CLAUSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) secondary trading documents.

Your task is to generate Assignment Clause provisions for a loan assignment agreement.

The assignment clause should:
1. Define the rights and obligations of assignors and assignees
2. Specify conditions for assignment (consent requirements, restrictions)
3. Include provisions for partial assignments
4. Address notice requirements and effective dates
5. Include provisions for assignment fees and expenses
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into an assignment agreement."""),
    ("user", """Generate Assignment Clause provisions for the following loan assignment:

Borrower: {borrower_name}
Facility Name: {facility_name}
Assignment Type: {assignment_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Assignment Clause provisions appropriate for {governing_law} law.""")
])


TRANSFER_RESTRICTIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) secondary trading documents.

Your task is to generate Transfer Restrictions clauses for a loan trading agreement.

The transfer restrictions should:
1. Specify any restrictions on transferability of the loan
2. Define prohibited transferees (if any)
3. Include provisions for regulatory restrictions
4. Address restrictions on transfer to competitors or restricted parties
5. Include provisions for consent requirements
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a trading agreement."""),
    ("user", """Generate Transfer Restrictions clauses for the following loan transfer:

Borrower: {borrower_name}
Facility Name: {facility_name}
Restriction Type: {restriction_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Transfer Restrictions clauses appropriate for {governing_law} law.""")
])


PARTICIPATION_AGREEMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) secondary trading documents.

Your task is to generate Participation Agreement clauses for a loan participation arrangement.

The participation agreement should:
1. Define the participation structure and rights
2. Specify the participation percentage and amount
3. Include provisions for voting rights and decision-making
4. Address payment flows and distributions
5. Include provisions for default and remedies
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a participation agreement."""),
    ("user", """Generate Participation Agreement clauses for the following loan participation:

Borrower: {borrower_name}
Facility Name: {facility_name}
Participation Type: {participation_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Participation Agreement clauses appropriate for {governing_law} law.""")
])


COLLATERAL_OBLIGATIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) secondary trading documents.

Your task is to generate Collateral Obligations clauses for a loan trading agreement.

The collateral obligations should:
1. Define the collateral package and security interests
2. Specify obligations to maintain and perfect collateral
3. Include provisions for collateral valuation and monitoring
4. Address obligations regarding collateral substitution and release
5. Include provisions for collateral enforcement and remedies
6. Address cross-collateralization and priority of security interests
7. Be appropriate for the governing law specified
8. Follow LMA standard practice
9. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a trading agreement."""),
    ("user", """Generate Collateral Obligations clauses for the following loan trading:

Borrower: {borrower_name}
Facility Name: {facility_name}
Collateral Type: {collateral_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Collateral Obligations clauses appropriate for {governing_law} law.""")
])


MARGIN_CALCULATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) secondary trading documents.

Your task is to generate Margin Calculation clauses for a loan trading agreement.

The margin calculation should:
1. Define the margin calculation methodology and formula
2. Specify the margin call process and timing
3. Include provisions for margin adjustments and recalculation
4. Address margin requirements and thresholds
5. Include provisions for margin disputes and resolution
6. Address margin payment obligations and mechanics
7. Include provisions for margin shortfalls and remedies
8. Be appropriate for the governing law specified
9. Follow LMA standard practice
10. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a trading agreement."""),
    ("user", """Generate Margin Calculation clauses for the following loan trading:

Borrower: {borrower_name}
Facility Name: {facility_name}
Margin Type: {margin_type}
Calculation Method: {calculation_method}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Margin Calculation clauses appropriate for {governing_law} law.""")
])


TRANSFER_PROVISIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) secondary trading documents.

Your task is to generate Transfer Provisions clauses for a loan trading agreement.

The transfer provisions should:
1. Define the transfer process and mechanics
2. Specify transfer conditions and requirements
3. Include provisions for transfer documentation and execution
4. Address transfer fees and expenses
5. Include provisions for transfer effectiveness and timing
6. Address transfer restrictions and consents
7. Include provisions for partial transfers and novations
8. Be appropriate for the governing law specified
9. Follow LMA standard practice
10. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a trading agreement."""),
    ("user", """Generate Transfer Provisions clauses for the following loan transfer:

Borrower: {borrower_name}
Facility Name: {facility_name}
Transfer Type: {transfer_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Transfer Provisions clauses appropriate for {governing_law} law.""")
])


DISPUTE_RESOLUTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) secondary trading documents.

Your task is to generate Dispute Resolution clauses for a loan trading agreement.

The dispute resolution should:
1. Define the dispute resolution process and procedures
2. Specify applicable dispute resolution mechanisms (negotiation, mediation, arbitration, litigation)
3. Include provisions for dispute notice and escalation
4. Address jurisdiction and governing law for disputes
5. Include provisions for expert determination (if applicable)
6. Address costs and expenses of dispute resolution
7. Include provisions for interim relief and injunctive relief
8. Be appropriate for the governing law specified
9. Follow LMA standard practice
10. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a trading agreement."""),
    ("user", """Generate Dispute Resolution clauses for the following loan trading:

Borrower: {borrower_name}
Facility Name: {facility_name}
Dispute Resolution Method: {dispute_resolution_method}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Dispute Resolution clauses appropriate for {governing_law} law.""")
])


# Export all prompts as a dictionary
SECONDARY_TRADING_PROMPTS = {
    "assignment_clause": ASSIGNMENT_CLAUSE_PROMPT,
    "transfer_restrictions": TRANSFER_RESTRICTIONS_PROMPT,
    "participation_agreement": PARTICIPATION_AGREEMENT_PROMPT,
    "collateral_obligations": COLLATERAL_OBLIGATIONS_PROMPT,
    "margin_calculation": MARGIN_CALCULATION_PROMPT,
    "transfer_provisions": TRANSFER_PROVISIONS_PROMPT,
    "dispute_resolution": DISPUTE_RESOLUTION_PROMPT,
}

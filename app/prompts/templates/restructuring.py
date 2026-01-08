"""
Prompt templates for Restructuring Documents AI field population.

These prompts guide the LLM to generate LMA-compliant clauses
for restructuring documents based on CDM CreditAgreement data.
"""

from langchain_core.prompts import ChatPromptTemplate


RESTRUCTURING_TERMS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) restructuring documents.

Your task is to generate Restructuring Terms clauses for a loan restructuring agreement.

The restructuring terms should:
1. Define the restructuring structure and terms
2. Specify the amended payment terms and schedules
3. Include provisions for debt rescheduling and modification
4. Address conditions precedent to restructuring
5. Include provisions for restructuring fees and expenses
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a restructuring agreement."""),
    ("user", """Generate Restructuring Terms clauses for the following loan restructuring:

Borrower: {borrower_name}
Facility Name: {facility_name}
Restructuring Type: {restructuring_type}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Restructuring Terms clauses appropriate for {governing_law} law.""")
])


WORKOUT_AGREEMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) restructuring documents.

Your task is to generate Workout Agreement clauses for a loan workout arrangement.

The workout agreement should:
1. Define the workout structure and process
2. Specify the workout terms and conditions
3. Include provisions for workout monitoring and reporting
4. Address workout fees and expenses
5. Include provisions for workout termination and remedies
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a workout agreement."""),
    ("user", """Generate Workout Agreement clauses for the following loan workout:

Borrower: {borrower_name}
Facility Name: {facility_name}
Workout Terms: {workout_terms}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Workout Agreement clauses appropriate for {governing_law} law.""")
])


FORBEARANCE_PROVISIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) restructuring documents.

Your task is to generate Forbearance Provisions clauses for a loan forbearance agreement.

The forbearance provisions should:
1. Define the forbearance period and terms
2. Specify the conditions for forbearance
3. Include provisions for forbearance monitoring and reporting
4. Address forbearance fees and expenses
5. Include provisions for forbearance termination and remedies
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a forbearance agreement."""),
    ("user", """Generate Forbearance Provisions clauses for the following loan forbearance:

Borrower: {borrower_name}
Facility Name: {facility_name}
Forbearance Period: {forbearance_period}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Forbearance Provisions clauses appropriate for {governing_law} law.""")
])


DEBT_COMPROMISE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document drafting assistant specializing in Loan Market Association (LMA) restructuring documents.

Your task is to generate Debt Compromise clauses for a debt compromise arrangement.

The debt compromise should:
1. Define the compromise structure and terms
2. Specify the compromised amount and payment terms
3. Include provisions for compromise conditions and releases
4. Address compromise fees and expenses
5. Include provisions for compromise enforcement and remedies
6. Be appropriate for the governing law specified
7. Follow LMA standard practice
8. Be written in formal legal language

Format the output as a complete legal clause suitable for insertion into a debt compromise agreement."""),
    ("user", """Generate Debt Compromise clauses for the following debt compromise:

Borrower: {borrower_name}
Facility Name: {facility_name}
Compromise Terms: {compromise_terms}
Governing Law: {governing_law}

{additional_context}

Generate comprehensive, LMA-compliant Debt Compromise clauses appropriate for {governing_law} law.""")
])


# Export all prompts as a dictionary
RESTRUCTURING_PROMPTS = {
    "restructuring_terms": RESTRUCTURING_TERMS_PROMPT,
    "workout_agreement": WORKOUT_AGREEMENT_PROMPT,
    "forbearance_provisions": FORBEARANCE_PROVISIONS_PROMPT,
    "debt_compromise": DEBT_COMPROMISE_PROMPT,
}

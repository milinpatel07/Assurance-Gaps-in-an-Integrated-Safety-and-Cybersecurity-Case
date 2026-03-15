"""ISO 21448:2022 — Road vehicles — Safety of the intended functionality (SOTIF).

This module implements the claim extraction (Step 1) and lifecycle mapping
(Step 2) for ISO 21448 as applied to an AI-based perception component.

Key clauses relevant to the integrated argument:
- Clause 5: Four-area model (known safe, known hazardous, unknown hazardous, unknown safe)
- Clause 6.5: Acceptance criteria for residual risk
- Clauses 7-8: Specification and design of SOTIF measures
- Clauses 9-11: V&V with triggering condition coverage
- Clause 13: Field monitoring
- Annex A.1: GSN argument structure (Example 2)
"""

from src.standards.base import (
    Standard,
    Clause,
    Claim,
    ClaimType,
    LifecyclePhase,
)


def _build_clauses() -> list[Clause]:
    return [
        Clause(
            standard_id="ISO21448",
            reference="Cl.5",
            title="Four-area model and SOTIF strategy",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "The four-area model partitions operational space into: "
                "Area 1 (known safe), Area 2 (known potentially hazardous), "
                "Area 3 (unknown potentially hazardous), Area 4 (unknown safe). "
                "Objective: reduce Area 3 to an acceptable level."
            ),
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.6",
            title="Specification and functional requirements",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.6.5",
            title="Acceptance criteria for residual risk",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Defines qualitative acceptance criteria but provides no "
                "quantitative formula. This contributes to Gap-1."
            ),
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.7",
            title="Identification of hazardous scenarios and triggering conditions",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.8",
            title="Functional modifications and design measures",
            lifecycle_phases=[LifecyclePhase.DESIGN],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.9",
            title="Verification of known hazardous scenarios",
            lifecycle_phases=[LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.10",
            title="Evaluation of unknown hazardous scenarios",
            lifecycle_phases=[LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.11",
            title="Verification strategy for SOTIF",
            lifecycle_phases=[LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.12",
            title="SOTIF evaluation criteria and release decision",
            lifecycle_phases=[LifecyclePhase.INTEGRATION],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.13",
            title="Field monitoring for SOTIF",
            lifecycle_phases=[LifecyclePhase.OPERATION],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Cl.1",
            title="Scope (explicitly excludes cybersecurity threats)",
            lifecycle_phases=[],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Clause 1 explicitly excludes threats from cybersecurity. "
                "This creates the cybersecurity-SOTIF boundary ambiguity (I-5)."
            ),
        ),
        # Annex A.1 (informative)
        Clause(
            standard_id="ISO21448",
            reference="Annex A.1",
            title="GSN argument structure — Example 2",
            lifecycle_phases=[
                LifecyclePhase.CONCEPT,
                LifecyclePhase.VERIFICATION,
                LifecyclePhase.OPERATION,
            ],
            normative=False,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Table A.8",
            title="Specification completeness items (17 items)",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=False,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Table A.9",
            title="SOTIF design measures",
            lifecycle_phases=[LifecyclePhase.DESIGN],
            normative=False,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Tables A.7-A.14",
            title="Assurance Claim Points (ACPs)",
            lifecycle_phases=[LifecyclePhase.VERIFICATION],
            normative=False,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Tables A.13-A.14",
            title="Field monitoring evidence",
            lifecycle_phases=[LifecyclePhase.OPERATION],
            normative=False,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21448",
            reference="Table A.10",
            title="Acceptance criteria evidence",
            lifecycle_phases=[LifecyclePhase.VERIFICATION],
            normative=False,
            ai_applicable=True,
        ),
    ]


def _build_claims(clauses: list[Clause]) -> list[Claim]:
    clause_map = {c.reference: c for c in clauses}

    return [
        Claim(
            claim_id="CLM-21448-AREA-01",
            text=(
                "The operational space shall be partitioned using the four-area "
                "model, and Area 3 (unknown potentially hazardous) shall be "
                "reduced to an acceptable level."
            ),
            source_clause=clause_map["Cl.5"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G7",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["Four-area model evaluation"],
        ),
        Claim(
            claim_id="CLM-21448-ACC-01",
            text=(
                "Acceptance criteria for residual risk from functional "
                "insufficiencies shall be defined."
            ),
            source_clause=clause_map["Cl.6.5"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G7",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["Acceptance criteria document"],
        ),
        Claim(
            claim_id="CLM-21448-TRIG-01",
            text=(
                "Triggering conditions that cause functional insufficiencies "
                "shall be identified."
            ),
            source_clause=clause_map["Cl.7"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G2",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["Triggering condition catalogue"],
        ),
        Claim(
            claim_id="CLM-21448-SPEC-01",
            text=(
                "The specification shall be complete with respect to 17 "
                "specification completeness items (Table A.8)."
            ),
            source_clause=clause_map["Table A.8"],
            claim_type=ClaimType.INFORMATIVE_GUIDANCE,
            gsn_goal="G2",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["Specification completeness checklist"],
        ),
        Claim(
            claim_id="CLM-21448-DES-01",
            text=(
                "SOTIF design measures shall avoid, reduce, or mitigate "
                "identified hazardous behaviours."
            ),
            source_clause=clause_map["Table A.9"],
            claim_type=ClaimType.INFORMATIVE_GUIDANCE,
            gsn_goal="G4",
            lifecycle_phase=LifecyclePhase.DESIGN,
            evidence_types=["SOTIF measures report"],
        ),
        Claim(
            claim_id="CLM-21448-VER-01",
            text=(
                "Known hazardous scenarios shall be verified through "
                "scenario-based testing with triggering condition coverage."
            ),
            source_clause=clause_map["Cl.9"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G5",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=[
                "Scenario test results",
                "Triggering condition coverage report",
            ],
        ),
        Claim(
            claim_id="CLM-21448-UNK-01",
            text=(
                "Unknown hazardous scenarios shall be evaluated to demonstrate "
                "that Area 3 is sufficiently small."
            ),
            source_clause=clause_map["Cl.10"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G5",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=["Area 3 evaluation report"],
        ),
        Claim(
            claim_id="CLM-21448-VSTRAT-01",
            text="A verification strategy for SOTIF shall be defined and executed.",
            source_clause=clause_map["Cl.11"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G5",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=["SOTIF verification strategy document"],
        ),
        Claim(
            claim_id="CLM-21448-REL-01",
            text=(
                "A SOTIF release decision shall confirm that acceptance criteria "
                "are met."
            ),
            source_clause=clause_map["Cl.12"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G7",
            lifecycle_phase=LifecyclePhase.INTEGRATION,
            evidence_types=["SOTIF release decision report"],
        ),
        Claim(
            claim_id="CLM-21448-MON-01",
            text=(
                "Field monitoring shall track SOTIF performance and identify "
                "new triggering conditions post-deployment."
            ),
            source_clause=clause_map["Cl.13"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G6",
            lifecycle_phase=LifecyclePhase.OPERATION,
            evidence_types=["Field monitoring report", "New triggering conditions log"],
        ),
        Claim(
            claim_id="CLM-21448-RISK-01",
            text=(
                "Residual risk from functional insufficiencies shall meet "
                "the defined acceptance criteria."
            ),
            source_clause=clause_map["Table A.10"],
            claim_type=ClaimType.INFORMATIVE_GUIDANCE,
            gsn_goal="G7",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=["Residual risk assessment"],
        ),
    ]


class ISO21448(Standard):
    """ISO 21448:2022 — Road vehicles — Safety of the intended functionality.

    Provides the SOTIF four-area model, triggering condition analysis,
    and residual risk acceptance framework.
    """

    def __init__(self):
        clauses = _build_clauses()
        claims = _build_claims(clauses)
        super().__init__(
            standard_id="ISO21448",
            full_name="ISO 21448:2022 — Road vehicles — Safety of the intended functionality",
            year=2022,
            scope=(
                "Safety of the intended functionality for road vehicles. "
                "Applies to the AI perception component because the intended "
                "function can produce hazardous behaviour under adverse conditions "
                "(rain, fog) without any hardware or software fault."
            ),
            clauses=clauses,
            claims=claims,
        )

"""ISO/IEC TR 5469:2024 — AI — Functional safety and AI systems.

This is a technical report (informative, not normative). It assesses which
established functional safety techniques apply to AI components and which
do not. Referenced as supplementary guidance in the integrated GSN.

Key clauses:
- Clause 6.1: AI error classification (systematic failure)
- Clause 6.2: AI technology classes (Table 1)
- Clause 8.5.1: Security vs. safety properties tension
- Clause 9.2.2: Non-separability of training data effects
- Clause 9.3.2: Data distributions linked to HARA risks
- Clause 9.3.3: Four criteria for training data
- Table A.8: Guidance on change protocols and regression validation
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
            standard_id="TR5469",
            reference="Cl.6.1",
            title="AI error classified as systematic failure",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=False,
            ai_applicable=True,
            ai_applicability_note=(
                "Classifies AI behavioural errors as systematic failures, "
                "creating terminological inconsistency I-3 with ISO 21448 "
                "(functional insufficiency) and ISO 26262 (out of scope)."
            ),
        ),
        Clause(
            standard_id="TR5469",
            reference="Cl.6.2, Table 1",
            title="AI technology classification by usage level",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=False,
            ai_applicable=True,
            ai_applicability_note=(
                "Classifies AI by technology class but no mapping to ASIL "
                "exists."
            ),
        ),
        Clause(
            standard_id="TR5469",
            reference="Cl.8.5.1",
            title="Security vs. safety properties tension",
            lifecycle_phases=[LifecyclePhase.DESIGN, LifecyclePhase.VERIFICATION],
            normative=False,
            ai_applicable=True,
            ai_applicability_note=(
                "NOTE 2 states that properties against intentional malevolent "
                "inputs contradict functional safety properties. Contributes "
                "to inconsistency I-5."
            ),
        ),
        Clause(
            standard_id="TR5469",
            reference="Cl.9.2.2",
            title="Non-separability of training data effects",
            lifecycle_phases=[LifecyclePhase.DESIGN],
            normative=False,
            ai_applicable=True,
            ai_applicability_note=(
                "Adding training data for one risk mitigation can affect other "
                "mitigations. Makes quantitative targets difficult (Gap-1)."
            ),
        ),
        Clause(
            standard_id="TR5469",
            reference="Cl.9.3.2",
            title="Data distributions linked to HARA risks",
            lifecycle_phases=[LifecyclePhase.DESIGN],
            normative=False,
            ai_applicable=True,
        ),
        Clause(
            standard_id="TR5469",
            reference="Cl.9.3.3",
            title="Four criteria for training data",
            lifecycle_phases=[LifecyclePhase.DESIGN],
            normative=False,
            ai_applicable=True,
        ),
        Clause(
            standard_id="TR5469",
            reference="Table A.8",
            title="Change protocols and regression validation guidance",
            lifecycle_phases=[LifecyclePhase.MODIFICATION],
            normative=False,
            ai_applicable=True,
            ai_applicability_note=(
                "Provides guidance on impact analysis, change protocols, "
                "and regression validation for AI model modifications, "
                "but without normative force (Gap-2)."
            ),
        ),
    ]


def _build_claims(clauses: list[Clause]) -> list[Claim]:
    clause_map = {c.reference: c for c in clauses}

    return [
        Claim(
            claim_id="CLM-TR5469-DATA-01",
            text=(
                "Training data distributions should be linked to "
                "HARA-identified risks."
            ),
            source_clause=clause_map["Cl.9.3.2"],
            claim_type=ClaimType.INFORMATIVE_GUIDANCE,
            gsn_goal="G3",
            lifecycle_phase=LifecyclePhase.DESIGN,
            evidence_types=["Data-risk mapping document"],
        ),
        Claim(
            claim_id="CLM-TR5469-DATA-02",
            text=(
                "Training data should satisfy four criteria: completeness, "
                "balance, relevance, and accuracy."
            ),
            source_clause=clause_map["Cl.9.3.3"],
            claim_type=ClaimType.INFORMATIVE_GUIDANCE,
            gsn_goal="G3",
            lifecycle_phase=LifecyclePhase.DESIGN,
            evidence_types=["Data quality assessment against four criteria"],
        ),
        Claim(
            claim_id="CLM-TR5469-MOD-01",
            text=(
                "AI model modifications should follow impact analysis, "
                "change protocols, and regression validation."
            ),
            source_clause=clause_map["Table A.8"],
            claim_type=ClaimType.INFORMATIVE_GUIDANCE,
            gsn_goal="G9",
            lifecycle_phase=LifecyclePhase.MODIFICATION,
            evidence_types=[
                "Impact analysis report",
                "Change protocol document",
                "Regression validation results",
            ],
        ),
    ]


class TR5469(Standard):
    """ISO/IEC TR 5469:2024 — AI — Functional safety and AI systems.

    Informative technical report providing supplementary guidance on
    AI technology classification, data quality, and change management.
    Not normative — referenced for completeness.
    """

    def __init__(self):
        clauses = _build_clauses()
        claims = _build_claims(clauses)
        super().__init__(
            standard_id="TR5469",
            full_name="ISO/IEC TR 5469:2024 — AI — Functional safety and AI systems",
            year=2024,
            scope=(
                "Informative technical report assessing which functional safety "
                "techniques apply to AI systems. Referenced as supplementary "
                "guidance in the integrated argument."
            ),
            clauses=clauses,
            claims=claims,
        )

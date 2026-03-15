"""ISO/SAE 21434:2021 — Road vehicles — Cybersecurity engineering.

This module implements the claim extraction (Step 1) and lifecycle mapping
(Step 2) for ISO/SAE 21434 as applied to an AI-based perception component.

Key clauses relevant to the integrated argument:
- Clause 9: Concept phase cybersecurity requirements
- Clause 10: Product development cybersecurity requirements
- Clause 15: Threat analysis and risk assessment (TARA)
- Clause 8: Continuous cybersecurity activities
- Clause 3.1.11: Cybersecurity case definition
- [RQ-06-01]: Cybersecurity specification requirements
- [RQ-15-06]: Safety-cybersecurity bridge requirement
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
            standard_id="ISO21434",
            reference="Cl.9",
            title="Concept phase — cybersecurity relevance and requirements",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21434",
            reference="Cl.10",
            title="Product development — cybersecurity requirements and controls",
            lifecycle_phases=[
                LifecyclePhase.DESIGN,
                LifecyclePhase.VERIFICATION,
                LifecyclePhase.INTEGRATION,
            ],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21434",
            reference="Cl.15",
            title="Threat analysis and risk assessment (TARA)",
            lifecycle_phases=[LifecyclePhase.CONCEPT, LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "TARA identifies threat scenarios for the AI perception component: "
                "LiDAR spoofing, adversarial point cloud perturbation, model poisoning."
            ),
        ),
        Clause(
            standard_id="ISO21434",
            reference="Cl.15.8",
            title="Risk value determination",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Assigns risk values (1-5) based on impact rating and attack "
                "feasibility. Incompatible scale with ASIL (I-1)."
            ),
        ),
        Clause(
            standard_id="ISO21434",
            reference="Cl.8",
            title="Continuous cybersecurity activities",
            lifecycle_phases=[
                LifecyclePhase.OPERATION,
                LifecyclePhase.MODIFICATION,
            ],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21434",
            reference="Cl.3.1.11",
            title="Cybersecurity case definition",
            lifecycle_phases=[
                LifecyclePhase.CONCEPT,
                LifecyclePhase.DESIGN,
                LifecyclePhase.VERIFICATION,
            ],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Defines the cybersecurity case but has not been integrated "
                "with safety argument structures in published work."
            ),
        ),
        Clause(
            standard_id="ISO21434",
            reference="[RQ-06-01]",
            title="Cybersecurity specification requirements",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO21434",
            reference="[RQ-15-06]",
            title="Safety-cybersecurity bridge requirement",
            lifecycle_phases=[LifecyclePhase.CONCEPT, LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Requires that the safety impact of each threat scenario is "
                "assessed using ISO 26262-3 severity classes. This is the bridge "
                "between G8 (cybersecurity) and G1 (functional safety)."
            ),
        ),
    ]


def _build_claims(clauses: list[Clause]) -> list[Claim]:
    clause_map = {c.reference: c for c in clauses}

    return [
        Claim(
            claim_id="CLM-21434-TARA-01",
            text=(
                "A threat analysis and risk assessment (TARA) shall identify "
                "threat scenarios and assign risk values."
            ),
            source_clause=clause_map["Cl.15"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G1",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["TARA report", "Threat scenario catalogue"],
        ),
        Claim(
            claim_id="CLM-21434-RISK-01",
            text=(
                "Cybersecurity risk values (1-5) shall be assigned based on "
                "impact rating and attack feasibility."
            ),
            source_clause=clause_map["Cl.15.8"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G8",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["Risk value matrix"],
        ),
        Claim(
            claim_id="CLM-21434-SPEC-01",
            text=(
                "Cybersecurity requirements shall be specified for the component."
            ),
            source_clause=clause_map["[RQ-06-01]"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G2",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["Cybersecurity requirements specification"],
        ),
        Claim(
            claim_id="CLM-21434-CTRL-01",
            text=(
                "Cybersecurity controls shall be designed and implemented "
                "to treat identified threats."
            ),
            source_clause=clause_map["Cl.10"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G4",
            lifecycle_phase=LifecyclePhase.DESIGN,
            evidence_types=["Cybersecurity control design document"],
        ),
        Claim(
            claim_id="CLM-21434-VER-01",
            text=(
                "Vulnerability analysis and penetration testing shall verify "
                "cybersecurity controls."
            ),
            source_clause=clause_map["Cl.10"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G5",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=[
                "Vulnerability analysis report",
                "Penetration test results",
            ],
        ),
        Claim(
            claim_id="CLM-21434-BRIDGE-01",
            text=(
                "The safety impact of each threat scenario shall be assessed "
                "using ISO 26262-3 severity classes."
            ),
            source_clause=clause_map["[RQ-15-06]"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G8",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["Safety-cybersecurity impact assessment"],
        ),
        Claim(
            claim_id="CLM-21434-MON-01",
            text=(
                "Continuous cybersecurity monitoring shall detect vulnerabilities "
                "and incidents post-deployment."
            ),
            source_clause=clause_map["Cl.8"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G6",
            lifecycle_phase=LifecyclePhase.OPERATION,
            evidence_types=["Cybersecurity monitoring log", "Incident response plan"],
        ),
        Claim(
            claim_id="CLM-21434-CASE-01",
            text=(
                "A cybersecurity case shall provide the argument that "
                "cybersecurity risks are treated to an acceptable level."
            ),
            source_clause=clause_map["Cl.3.1.11"],
            claim_type=ClaimType.WORK_PRODUCT,
            gsn_goal="G8",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=["Cybersecurity case document"],
        ),
        Claim(
            claim_id="CLM-21434-TREAT-01",
            text=(
                "Cybersecurity risks identified through TARA shall be treated "
                "to an acceptable level."
            ),
            source_clause=clause_map["Cl.15"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G8",
            lifecycle_phase=LifecyclePhase.DESIGN,
            evidence_types=["Risk treatment plan", "Residual risk assessment"],
        ),
    ]


class ISOSAE21434(Standard):
    """ISO/SAE 21434:2021 — Road vehicles — Cybersecurity engineering.

    Provides the TARA framework, cybersecurity case structure, and the
    safety-cybersecurity bridge requirement [RQ-15-06].
    """

    def __init__(self):
        clauses = _build_clauses()
        claims = _build_claims(clauses)
        super().__init__(
            standard_id="ISO21434",
            full_name="ISO/SAE 21434:2021 — Road vehicles — Cybersecurity engineering",
            year=2021,
            scope=(
                "Cybersecurity engineering for road vehicle systems. "
                "Applies to the AI perception component because it processes "
                "sensor data subject to adversarial manipulation (LiDAR spoofing, "
                "adversarial point cloud perturbation, model poisoning)."
            ),
            clauses=clauses,
            claims=claims,
        )

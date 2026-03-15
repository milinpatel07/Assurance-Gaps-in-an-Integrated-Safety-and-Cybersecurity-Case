"""ISO/PAS 8800:2024 — Road vehicles — Safety and artificial intelligence.

This module implements the claim extraction (Step 1) and lifecycle mapping
(Step 2) for ISO/PAS 8800 as applied to an AI-based perception component.

ISO/PAS 8800 Annex B serves as the BASE STRUCTURE for the integrated GSN.
Its six goals (G1-G6) form the skeleton that is extended with claims from
the other applicable standards.

Key clauses:
- Clause 5-6: AI specification and requirements
- Clause 7-8: AI design and training
- Clause 8-9: AI verification and validation
- Clause 14: Operational monitoring and re-assurance
- Annex B: GSN argument pattern (G1-G6, S1, A1.4)
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
            standard_id="ISOPAS8800",
            reference="Cl.5",
            title="AI safety requirements specification",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISOPAS8800",
            reference="Cl.6",
            title="AI safety requirements allocation",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISOPAS8800",
            reference="Cl.7",
            title="AI design principles",
            lifecycle_phases=[LifecyclePhase.DESIGN],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISOPAS8800",
            reference="Cl.8",
            title="AI development (training and design)",
            lifecycle_phases=[LifecyclePhase.DESIGN, LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISOPAS8800",
            reference="Cl.8.4",
            title="Data quality requirements",
            lifecycle_phases=[LifecyclePhase.DESIGN],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Prescribes data quality requirements but no operationalised "
                "threshold for data sufficiency (Gap-6, I-7)."
            ),
        ),
        Clause(
            standard_id="ISOPAS8800",
            reference="Cl.9",
            title="AI verification and validation",
            lifecycle_phases=[LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Prescribes AI-specific evaluation including uncertainty "
                "quantification and robustness testing."
            ),
        ),
        Clause(
            standard_id="ISOPAS8800",
            reference="Cl.14",
            title="Operational monitoring of AI",
            lifecycle_phases=[LifecyclePhase.OPERATION],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Prescribes runtime OOD detection, distributional drift monitoring."
            ),
        ),
        Clause(
            standard_id="ISOPAS8800",
            reference="Cl.14.8.3",
            title="Partial re-approval after modification",
            lifecycle_phases=[LifecyclePhase.MODIFICATION],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Addresses partial re-approval but does not define conditions "
                "under which partial re-assurance is sufficient (Gap-2)."
            ),
        ),
        # Annex B (informative) — the base GSN pattern
        Clause(
            standard_id="ISOPAS8800",
            reference="Annex B",
            title="GSN argument pattern for AI components",
            lifecycle_phases=[
                LifecyclePhase.CONCEPT,
                LifecyclePhase.DESIGN,
                LifecyclePhase.VERIFICATION,
                LifecyclePhase.OPERATION,
            ],
            normative=False,
            ai_applicable=True,
            ai_applicability_note=(
                "The only published GSN pattern designed for AI components "
                "in road vehicles. Contains G1 (top-level), S1 (strategy), "
                "G2-G6 (sub-goals), and A1.4 (HW fault assumption)."
            ),
        ),
        Clause(
            standard_id="ISOPAS8800",
            reference="Annex B, A1.4",
            title="Assumption: HW faults delegated to ISO 26262",
            lifecycle_phases=[],
            normative=False,
            ai_applicable=True,
        ),
    ]


def _build_claims(clauses: list[Clause]) -> list[Claim]:
    clause_map = {c.reference: c for c in clauses}

    return [
        # G1: Top-level goal
        Claim(
            claim_id="CLM-8800-G1",
            text=(
                "The AI component satisfies its allocated safety requirements."
            ),
            source_clause=clause_map["Annex B"],
            claim_type=ClaimType.INFORMATIVE_GUIDANCE,
            gsn_goal="G1",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=["Complete safety argument"],
        ),
        # G2: Specification sufficiency
        Claim(
            claim_id="CLM-8800-G2",
            text=(
                "The AI specification is sufficient to define the required "
                "AI behaviour."
            ),
            source_clause=clause_map["Cl.5"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G2",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["AI specification review report"],
        ),
        # G3: Data set sufficiency
        Claim(
            claim_id="CLM-8800-G3",
            text=(
                "Training and test data are sufficient in quantity, "
                "distribution coverage, annotation quality, and domain "
                "representativeness."
            ),
            source_clause=clause_map["Cl.8.4"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G3",
            lifecycle_phase=LifecyclePhase.DESIGN,
            evidence_types=[
                "Data quality report",
                "Distribution analysis",
                "Annotation quality metrics",
            ],
        ),
        # G4: Design sufficiency
        Claim(
            claim_id="CLM-8800-G4",
            text="The AI design is sufficient for the intended safety function.",
            source_clause=clause_map["Cl.7"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G4",
            lifecycle_phase=LifecyclePhase.DESIGN,
            evidence_types=["AI design review report"],
        ),
        # G5: V&V sufficiency
        Claim(
            claim_id="CLM-8800-G5",
            text=(
                "AI-specific verification and validation evidence is sufficient, "
                "including uncertainty quantification and robustness testing."
            ),
            source_clause=clause_map["Cl.9"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G5",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=[
                "AI evaluation metrics report",
                "Uncertainty quantification results",
                "Robustness testing results",
            ],
        ),
        # G6: Monitoring sufficiency
        Claim(
            claim_id="CLM-8800-G6",
            text=(
                "Operational monitoring of AI behaviour is sufficient, "
                "including out-of-distribution detection and drift monitoring."
            ),
            source_clause=clause_map["Cl.14"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G6",
            lifecycle_phase=LifecyclePhase.OPERATION,
            evidence_types=[
                "OOD detection capability report",
                "Drift monitoring configuration",
            ],
        ),
        # S1: Strategy
        Claim(
            claim_id="CLM-8800-S1",
            text=(
                "AI-specific insufficiencies have been prevented, minimised, "
                "or mitigated."
            ),
            source_clause=clause_map["Annex B"],
            claim_type=ClaimType.INFORMATIVE_GUIDANCE,
            gsn_goal="S1",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=[],
        ),
        # Modification
        Claim(
            claim_id="CLM-8800-MOD-01",
            text=(
                "Partial re-approval shall be performed after AI model modification."
            ),
            source_clause=clause_map["Cl.14.8.3"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G9",
            lifecycle_phase=LifecyclePhase.MODIFICATION,
            evidence_types=["Partial re-approval report"],
        ),
    ]


class ISOPAS8800(Standard):
    """ISO/PAS 8800:2024 — Road vehicles — Safety and artificial intelligence.

    Provides the base GSN pattern (Annex B) and AI-specific safety requirements
    for specification, data quality, design, verification, and monitoring.
    """

    def __init__(self):
        clauses = _build_clauses()
        claims = _build_claims(clauses)
        super().__init__(
            standard_id="ISOPAS8800",
            full_name="ISO/PAS 8800:2024 — Road vehicles — Safety and artificial intelligence",
            year=2024,
            scope=(
                "Safety properties specific to AI components in road vehicles. "
                "Applies to the perception component because its detection function "
                "is implemented by a trained neural network (SECOND architecture "
                "with deep ensemble)."
            ),
            clauses=clauses,
            claims=claims,
        )

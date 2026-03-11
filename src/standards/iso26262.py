"""ISO 26262:2018 — Road vehicles — Functional safety.

This module implements the claim extraction (Step 1) and lifecycle mapping
(Step 2) for ISO 26262 as applied to an AI-based perception component.

Key clauses relevant to the integrated argument:
- Part 3, Clause 6: HARA and ASIL assignment
- Part 4, Clause 6: Technical safety concept (limited AI applicability)
- Part 4, Clause 7: System integration and testing
- Part 4, Clause 8: Safety validation
- Part 6, Clause 8: Software unit design (limited AI applicability)
- Part 6, Clause 9: Software unit testing (limited AI applicability)
- Part 8, Clause 8: Change management
- Part 5, Clause 9: Hardware metrics (SPFM, LFM, PMHF)
"""

from src.standards.base import (
    Standard,
    Clause,
    Claim,
    ClaimType,
    LifecyclePhase,
)


def _build_clauses() -> list[Clause]:
    """Build the clause set for ISO 26262 relevant to AI perception."""
    return [
        Clause(
            standard_id="ISO26262",
            reference="Part 3, Cl.6",
            title="Hazard analysis and risk assessment (HARA)",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "HARA applies to the system function regardless of implementation. "
                "At SAE Level 4+, controllability is C3 (no human driver), "
                "yielding ASIL D for high severity/exposure events."
            ),
        ),
        Clause(
            standard_id="ISO26262",
            reference="Part 3, Cl.6.4.3",
            title="Controllability classification",
            lifecycle_phases=[LifecyclePhase.CONCEPT],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Clause 6.4.3.8: At SAE Level 4+, C3 is the common assignment "
                "because the human driver is absent and cannot intervene."
            ),
        ),
        Clause(
            standard_id="ISO26262",
            reference="Part 4, Cl.6",
            title="Technical safety concept",
            lifecycle_phases=[LifecyclePhase.DESIGN],
            normative=True,
            ai_applicable=None,
            ai_applicability_note=(
                "Limited applicability for trained AI models. The technical safety "
                "concept assumes requirements can be decomposed to software units, "
                "which is not directly applicable to neural network weights."
            ),
        ),
        Clause(
            standard_id="ISO26262",
            reference="Part 4, Cl.7",
            title="System integration and testing",
            lifecycle_phases=[LifecyclePhase.INTEGRATION],
            normative=True,
            ai_applicable=True,
        ),
        Clause(
            standard_id="ISO26262",
            reference="Part 4, Cl.8",
            title="Safety validation",
            lifecycle_phases=[LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Safety validation at system level applies. However, the prescribed "
                "methods (fault injection, FMEA) have limited applicability to "
                "learned behaviours."
            ),
        ),
        Clause(
            standard_id="ISO26262",
            reference="Part 5, Cl.9",
            title="Evaluation of HW architectural metrics",
            lifecycle_phases=[LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=True,
            ai_applicability_note=(
                "Hardware metrics (SPFM >= 99% at ASIL D, LFM >= 90%, "
                "PMHF < 10^-8 h^-1) apply to the hardware platform. "
                "No equivalent exists for AI component failures (Gap-1)."
            ),
        ),
        Clause(
            standard_id="ISO26262",
            reference="Part 6, Cl.8",
            title="Software unit design and implementation",
            lifecycle_phases=[LifecyclePhase.DESIGN],
            normative=True,
            ai_applicable=None,
            ai_applicability_note=(
                "Limited applicability. Salay et al. (2018) and TR 5469 assess "
                "that many Part 6 techniques assume deterministic, "
                "requirements-traceable software."
            ),
        ),
        Clause(
            standard_id="ISO26262",
            reference="Part 6, Cl.9",
            title="Software unit testing",
            lifecycle_phases=[LifecyclePhase.VERIFICATION],
            normative=True,
            ai_applicable=None,
            ai_applicability_note=(
                "Limited applicability. MC/DC structural coverage at ASIL D "
                "applies to the non-AI wrapper code but not to the neural "
                "network inference path."
            ),
        ),
        Clause(
            standard_id="ISO26262",
            reference="Part 8, Cl.8",
            title="Change management",
            lifecycle_phases=[LifecyclePhase.MODIFICATION],
            normative=True,
            ai_applicable=None,
            ai_applicability_note=(
                "Assumes conventional software where change impact can be traced "
                "to specific requirements. For a retrained neural network, "
                "the entire weight space changes (Gap-2)."
            ),
        ),
        Clause(
            standard_id="ISO26262",
            reference="Part 2, Cl.6.4",
            title="Safety case",
            lifecycle_phases=[
                LifecyclePhase.CONCEPT,
                LifecyclePhase.DESIGN,
                LifecyclePhase.VERIFICATION,
                LifecyclePhase.INTEGRATION,
            ],
            normative=True,
            ai_applicable=True,
        ),
    ]


def _build_claims(clauses: list[Clause]) -> list[Claim]:
    """Extract claims from ISO 26262 clauses (Step 1)."""
    clause_map = {c.reference: c for c in clauses}

    return [
        Claim(
            claim_id="CLM-26262-HARA-01",
            text=(
                "A hazard analysis and risk assessment shall be performed "
                "to identify hazardous events and assign an ASIL."
            ),
            source_clause=clause_map["Part 3, Cl.6"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G1",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["HARA report", "ASIL assignment"],
        ),
        Claim(
            claim_id="CLM-26262-CTRL-01",
            text=(
                "At SAE Level 4+, controllability shall be classified as C3 "
                "because no human driver is available to intervene."
            ),
            source_clause=clause_map["Part 3, Cl.6.4.3"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G1",
            lifecycle_phase=LifecyclePhase.CONCEPT,
            evidence_types=["Controllability justification"],
        ),
        Claim(
            claim_id="CLM-26262-TSC-01",
            text=(
                "A technical safety concept shall be derived from the "
                "functional safety concept."
            ),
            source_clause=clause_map["Part 4, Cl.6"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G2",
            lifecycle_phase=LifecyclePhase.DESIGN,
            evidence_types=["Technical safety concept document"],
        ),
        Claim(
            claim_id="CLM-26262-INTG-01",
            text=(
                "System integration testing shall verify that the integrated "
                "system satisfies the technical safety concept."
            ),
            source_clause=clause_map["Part 4, Cl.7"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G5",
            lifecycle_phase=LifecyclePhase.INTEGRATION,
            evidence_types=["Integration test report"],
        ),
        Claim(
            claim_id="CLM-26262-SVAL-01",
            text="Safety validation shall confirm that safety goals are achieved.",
            source_clause=clause_map["Part 4, Cl.8"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G5",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=["Safety validation report"],
        ),
        Claim(
            claim_id="CLM-26262-HWMET-01",
            text=(
                "Hardware architectural metrics shall meet ASIL D targets: "
                "SPFM >= 99%, LFM >= 90%, PMHF < 10^-8 h^-1."
            ),
            source_clause=clause_map["Part 5, Cl.9"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G5",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=["Hardware metric report"],
        ),
        Claim(
            claim_id="CLM-26262-MCDC-01",
            text=(
                "At ASIL D, modified condition/decision coverage (MC/DC) "
                "shall be achieved for software unit testing."
            ),
            source_clause=clause_map["Part 6, Cl.9"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G5",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=["MC/DC coverage report (non-AI code)"],
        ),
        Claim(
            claim_id="CLM-26262-CHG-01",
            text=(
                "Changes to the element shall be managed through an impact "
                "analysis and re-qualification process."
            ),
            source_clause=clause_map["Part 8, Cl.8"],
            claim_type=ClaimType.NORMATIVE_REQUIREMENT,
            gsn_goal="G9",
            lifecycle_phase=LifecyclePhase.MODIFICATION,
            evidence_types=["Change impact analysis", "Re-qualification report"],
        ),
        Claim(
            claim_id="CLM-26262-CASE-01",
            text=(
                "A safety case shall provide the argument that the safety "
                "requirements are satisfied."
            ),
            source_clause=clause_map["Part 2, Cl.6.4"],
            claim_type=ClaimType.WORK_PRODUCT,
            gsn_goal="G1",
            lifecycle_phase=LifecyclePhase.VERIFICATION,
            evidence_types=["Safety case document"],
        ),
    ]


class ISO26262(Standard):
    """ISO 26262:2018 — Road vehicles — Functional safety.

    Provides the HARA/ASIL framework and prescribes functional safety
    requirements at ASIL D for the case study perception component.
    """

    def __init__(self):
        clauses = _build_clauses()
        claims = _build_claims(clauses)
        super().__init__(
            standard_id="ISO26262",
            full_name="ISO 26262:2018 — Road vehicles — Functional safety",
            year=2018,
            scope=(
                "Functional safety of electrical and electronic systems "
                "in road vehicles. Applies to the AI perception component "
                "because a perception failure can contribute to a hazardous "
                "event rated up to ASIL D."
            ),
            clauses=clauses,
            claims=claims,
        )

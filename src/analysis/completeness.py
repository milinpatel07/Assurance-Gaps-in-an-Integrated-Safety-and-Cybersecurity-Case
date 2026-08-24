"""GSN extension completeness argument and related work comparison.

Provides systematic evidence that the 9-goal GSN extension is complete:
- Every claim maps to at least one goal
- Every lifecycle phase is covered by at least one goal
- No orphaned claims exist

Also provides a structured comparison with related assurance case approaches.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.standards.registry import StandardsRegistry
from src.gsn.integrated_pattern import build_integrated_gsn


@dataclass
class CompletenessCheckResult:
    """Result of the GSN completeness check."""

    total_claims: int
    mapped_claims: int
    unmapped_claims: list[str]
    out_of_scope_claims: list[str]
    phases_covered: list[str]
    phases_uncovered: list[str]
    goals_with_claims: dict[str, int]
    goals_without_claims: list[str]
    is_complete: bool
    explanation: str


def check_gsn_completeness() -> CompletenessCheckResult:
    """Check that the 9-goal GSN extension is structurally complete.

    Verifies:
    1. Every claim from every standard maps to a GSN element, unless it is
       recorded as out of scope for the AI-component argument
    2. Every lifecycle phase is addressed by at least one goal
    3. No goal is without supporting claims (except G9 which is undeveloped)
    """
    registry = StandardsRegistry()
    gsn = build_integrated_gsn()

    # 1. Check claim coverage (goals AND strategies are valid targets)
    all_claims = registry.get_all_claims()
    all_element_ids = set(gsn.elements.keys())
    goal_ids = {g.element_id for g in gsn.get_goals()}
    goals_with_claims: dict[str, int] = {g: 0 for g in goal_ids}
    unmapped = []

    out_of_scope = []

    for claim in all_claims:
        if claim.gsn_goal in all_element_ids:
            if claim.gsn_goal in goal_ids:
                goals_with_claims[claim.gsn_goal] += 1
            # Claims mapping to strategies (e.g., S1) are valid
        elif claim.is_out_of_scope:
            # Deliberately outside the AI-component argument, with a recorded
            # reason. Not a mapping defect. See Claim.out_of_scope_reason.
            out_of_scope.append(f"{claim.claim_id}: {claim.out_of_scope_reason}")
        else:
            unmapped.append(f"{claim.claim_id} -> {claim.gsn_goal}")

    # 2. Check lifecycle phase coverage
    from src.standards.base import LifecyclePhase
    all_phases = [p.display_name for p in LifecyclePhase]
    covered_phases = set()
    for claim in all_claims:
        covered_phases.add(claim.lifecycle_phase.display_name)
    uncovered = [p for p in all_phases if p not in covered_phases]

    # 3. Check goals without claims (G9 is expected to have none)
    no_claims = [g for g, c in goals_with_claims.items() if c == 0]

    is_complete = (
        len(unmapped) == 0
        and len(uncovered) == 0
        and all(g == "G9" for g in no_claims)
    )

    if is_complete:
        explanation = (
            f"The 9-goal GSN is structurally complete. "
            f"{len(all_claims) - len(unmapped) - len(out_of_scope)} of "
            f"{len(all_claims)} claims from {len(registry.all_standards)} standards "
            f"map to GSN nodes; {len(out_of_scope)} recorded as outside the "
            f"AI-component scope; none unmapped. "
            f"All {len(all_phases)} lifecycle phases are covered. "
            f"G9 is intentionally undeveloped (Gap-2: no re-assurance workflow). "
            f"The extension from 6 to 9 goals is justified: G7 (SOTIF), G8 (cybersecurity), "
            f"and G9 (modification) are required to host claims that have no home in the "
            f"base ISO/PAS 8800 Annex B pattern."
        )
    else:
        explanation = (
            f"Completeness check found issues: "
            f"{len(unmapped)} unmapped claims, "
            f"{len(uncovered)} uncovered phases, "
            f"{len([g for g in no_claims if g != 'G9'])} unexpected goals without claims."
        )

    return CompletenessCheckResult(
        total_claims=len(all_claims),
        mapped_claims=len(all_claims) - len(unmapped) - len(out_of_scope),
        unmapped_claims=unmapped,
        out_of_scope_claims=out_of_scope,
        phases_covered=sorted(covered_phases),
        phases_uncovered=uncovered,
        goals_with_claims=goals_with_claims,
        goals_without_claims=no_claims,
        is_complete=is_complete,
        explanation=explanation,
    )


@dataclass
class RelatedApproach:
    """A related assurance case integration approach for comparison."""

    name: str
    authors: str
    year: int
    standards_covered: list[str]
    methodology: str
    identifies_integration_gaps: bool
    uses_gsn: bool
    case_study_domain: str
    key_limitation: str


def get_related_work_comparison() -> list[RelatedApproach]:
    """Return structured comparison with related work."""
    return [
        RelatedApproach(
            name="AMLAS (Assurance of ML in Autonomous Systems)",
            authors="Hawkins et al.",
            year=2021,
            standards_covered=["UL 4600", "ISO/PAS 8800 (partial)"],
            methodology=(
                "Six-stage lifecycle for ML assurance with explicit "
                "argument patterns per stage"
            ),
            identifies_integration_gaps=False,
            uses_gsn=True,
            case_study_domain="Autonomous driving (general)",
            key_limitation=(
                "Focuses on ML lifecycle only; does not integrate "
                "cybersecurity or SOTIF standards, so cannot identify "
                "cross-standard gaps like Gap-3 and Gap-4"
            ),
        ),
        RelatedApproach(
            name="SACE (Safety Assurance Cases for AI Ethics)",
            authors="Bloomfield & Rushby",
            year=2020,
            standards_covered=["ISO 26262 (conceptual)", "AI ethics frameworks"],
            methodology=(
                "Structured argument framework extending safety cases "
                "to include AI ethical considerations"
            ),
            identifies_integration_gaps=False,
            uses_gsn=True,
            case_study_domain="General AI systems",
            key_limitation=(
                "Conceptual framework without concrete standard clause "
                "mapping; does not perform systematic claim extraction "
                "or junction-point analysis"
            ),
        ),
        RelatedApproach(
            name="Integrated safety-security using STPA-Sec",
            authors="Friedberg et al.",
            year=2017,
            standards_covered=["ISO 26262", "ISO/SAE 21434 (precursor)"],
            methodology=(
                "Combined STPA analysis for safety and security, "
                "identifying interactions between hazards and threats"
            ),
            identifies_integration_gaps=False,
            uses_gsn=False,
            case_study_domain="Automotive ECU",
            key_limitation=(
                "Focuses on hazard/threat analysis only (HARA/TARA equivalent); "
                "does not address assurance evidence, V&V, or AI-specific "
                "concerns. No SOTIF or AI safety standards."
            ),
        ),
        RelatedApproach(
            name="This work: Five-step constructive integration",
            authors="Patel & Jung",
            year=2026,
            standards_covered=[
                "ISO 26262", "ISO 21448", "ISO/SAE 21434",
                "ISO/PAS 8800", "ISO/IEC TR 5469",
            ],
            methodology=(
                "Claim extraction -> lifecycle mapping -> GSN extension -> "
                "junction-point analysis -> gap classification, with "
                "CARLA-based evaluation"
            ),
            identifies_integration_gaps=True,
            uses_gsn=True,
            case_study_domain="AI-based LiDAR perception (SAE L4+)",
            key_limitation=(
                "Case-study specific goals (G7-G9); synthetic CARLA "
                "evaluation rather than empirical; inconsistency "
                "catalogue from expert analysis (single assessor)"
            ),
        ),
    ]


def print_related_work_table(approaches: list[RelatedApproach]):
    """Print a comparison table of related approaches."""
    print("=" * 100)
    print("COMPARISON WITH RELATED WORK")
    print("=" * 100)

    for a in approaches:
        print(f"\n{'─' * 100}")
        print(f"  {a.name} ({a.authors}, {a.year})")
        print(f"{'─' * 100}")
        print(f"  Standards:         {', '.join(a.standards_covered)}")
        print(f"  Methodology:       {a.methodology}")
        print(f"  Uses GSN:          {'Yes' if a.uses_gsn else 'No'}")
        print(f"  Integration gaps:  {'Yes' if a.identifies_integration_gaps else 'No'}")
        print(f"  Domain:            {a.case_study_domain}")
        print(f"  Key limitation:    {a.key_limitation}")

    print(f"\n{'=' * 100}")
    print("KEY DIFFERENTIATOR: This work is the only approach that:")
    print("  1. Integrates 5 standards (including AI-specific: ISO/PAS 8800, TR 5469)")
    print("  2. Systematically identifies integration-induced gaps (Gap-3, Gap-4)")
    print("  3. Provides quantitative evaluation under SOTIF triggering conditions")
    print("=" * 100)

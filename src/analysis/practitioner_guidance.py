"""Practitioner guidance for resolving the identified gaps.

Addresses the question: What concrete guidance does the paper offer
practitioners for resolving the identified gaps?

For each gap, this module provides:
- Immediate actions (what a project team can do now)
- Required decisions (what must be decided before proceeding)
- Evidence to produce (what documentation is needed)
- Open research questions (what remains unsolved)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GapResolutionGuidance:
    """Practitioner guidance for resolving one assurance gap."""

    gap_id: str
    description: str
    immediate_actions: list[str]
    required_decisions: list[str]
    evidence_to_produce: list[str]
    open_research_questions: list[str]
    estimated_effort: str  # "low", "medium", "high", "requires_research"
    prerequisite_gaps: list[str] = field(default_factory=list)


def build_practitioner_guidance() -> list[GapResolutionGuidance]:
    """Build concrete practitioner guidance for each gap."""
    return [
        GapResolutionGuidance(
            gap_id="Gap-1",
            description="No AI-specific quantitative reliability target",
            immediate_actions=[
                "Define project-specific AI reliability targets based on "
                "ASIL D hardware metrics as reference (SPFM >= 99%, "
                "LFM >= 90%, PMHF < 10^-8 h^-1)",
                "Document rationale for chosen AI metric thresholds "
                "(e.g., AUROC >= 0.95 for OOD detection) with reference "
                "to ISO/PAS 8800 Cl.9",
                "Use ISO 26262-4 Cl.8 documented rationale mechanism: "
                "record why the chosen threshold corresponds to ASIL D "
                "assurance depth",
            ],
            required_decisions=[
                "Which AI metric(s) serve as the reliability indicator? "
                "(Options: AUROC, mAP, per-class recall, ensemble disagreement)",
                "What threshold value corresponds to 'sufficient' at ASIL D?",
                "Is the threshold static or does it depend on operational conditions?",
            ],
            evidence_to_produce=[
                "AI reliability target specification document",
                "Mapping table: ASIL level -> AI metric threshold -> rationale",
                "Validation report demonstrating the component meets the target",
            ],
            open_research_questions=[
                "Can AI reliability be decomposed analogously to SPFM/LFM/PMHF?",
                "What is the theoretical basis for a quantitative AI reliability "
                "target at ASIL D?",
                "How to account for the non-separability of training data effects "
                "(TR 5469 Cl.9.2.2)?",
            ],
            estimated_effort="requires_research",
        ),
        GapResolutionGuidance(
            gap_id="Gap-2",
            description="No complete OTA re-assurance workflow",
            immediate_actions=[
                "Define change categories for AI components: "
                "(a) hyperparameter change only, (b) architecture preserved / "
                "data changed, (c) architecture changed",
                "For each category, define minimum re-assurance scope "
                "(which tests must be re-run, which evidence must be updated)",
                "Establish regression test suite with coverage criteria",
            ],
            required_decisions=[
                "Under what conditions is partial re-assurance sufficient vs. "
                "full re-assurance required?",
                "What constitutes 'equivalent performance' after retraining?",
                "Who approves the re-assurance decision?",
            ],
            evidence_to_produce=[
                "AI change management procedure (extending ISO 26262-8 Cl.8)",
                "Re-assurance decision matrix (change type x required actions)",
                "Regression test report for each update",
                "Performance comparison report (before vs. after update)",
            ],
            open_research_questions=[
                "Can change impact analysis be performed on neural network weights?",
                "What is the minimum test set for re-assurance after retraining?",
                "How to detect silent regressions in AI component updates?",
            ],
            estimated_effort="high",
        ),
        GapResolutionGuidance(
            gap_id="Gap-3",
            description="Adversarial-SOTIF boundary unowned",
            immediate_actions=[
                "Create project-level ownership policy: assign each identified "
                "failure mode to either G7 (SOTIF) or G8 (cybersecurity) "
                "with documented justification",
                "For dual-domain failure modes (adversarial inputs that exploit "
                "functional insufficiencies): assign to BOTH G7 and G8 with "
                "explicit cross-references",
                "Add dual-domain failure modes to both the SOTIF triggering "
                "condition catalogue and the TARA threat scenario list",
            ],
            required_decisions=[
                "Who owns dual-domain failure modes? (Options: safety team, "
                "cybersecurity team, joint review board)",
                "Is the adversarial perturbation a triggering condition (SOTIF) "
                "or a threat scenario (cybersecurity) or both?",
                "What evidence is required for dual-domain failure modes?",
            ],
            evidence_to_produce=[
                "Dual-domain failure mode register with ownership assignments",
                "Cross-reference table: TARA threat scenarios <-> SOTIF triggering "
                "conditions for overlapping failure modes",
                "Joint SOTIF-cybersecurity review report",
            ],
            open_research_questions=[
                "Should ISO 21448 remove the cybersecurity exclusion (Cl.1) "
                "for AI components?",
                "Can STPA-Sec (combined hazard/threat analysis) resolve the "
                "boundary problem systematically?",
            ],
            estimated_effort="medium",
        ),
        GapResolutionGuidance(
            gap_id="Gap-4",
            description="No cross-domain release decision criteria",
            immediate_actions=[
                "Define a cross-domain release checklist that requires sign-off "
                "from all four assurance domains before release",
                "Establish a release review board with representatives from "
                "functional safety, SOTIF, cybersecurity, and AI safety",
                "Use ISO 26262-4 Cl.8 documented rationale: record how "
                "the four evidence sets jointly support the release decision",
            ],
            required_decisions=[
                "What is the decision rule? (Options: conjunctive (all must pass), "
                "weighted, majority with documented rationale for overrides)",
                "Can release proceed if one domain passes with reservations?",
                "What is the escalation path for conflicting evidence?",
            ],
            evidence_to_produce=[
                "Cross-domain release criteria specification",
                "Release review board charter and membership",
                "Integrated release report combining all four domain assessments",
                "Residual risk summary across all domains",
            ],
            open_research_questions=[
                "How to formally combine four evidence types with different "
                "scales into a single sufficiency judgement? "
                "(The evidence asymmetry problem at G5)",
                "Can Subjective Logic (Burton et al., 2024) be extended to "
                "cross-strand combination?",
            ],
            estimated_effort="high",
            prerequisite_gaps=["Gap-1"],
        ),
        GapResolutionGuidance(
            gap_id="Gap-5",
            description="No ASIL-to-AI-class mapping",
            immediate_actions=[
                "Create a project-specific mapping table from ASIL levels to "
                "AI technology classes (TR 5469 Table 1)",
                "Use conservative defaults: ASIL D -> highest AI assurance class",
                "Document the mapping rationale with reference to TR 5469 Cl.6.2",
            ],
            required_decisions=[
                "Which AI technology class applies to the specific component?",
                "Does ASIL decomposition (ISO 26262-9) affect the AI class?",
            ],
            evidence_to_produce=[
                "ASIL-to-AI-class mapping table with rationale",
                "AI technology classification report for the component",
            ],
            open_research_questions=[
                "Should ISO/PAS 8800 define a normative ASIL-to-AI-class mapping?",
                "Can ASIL decomposition be applied meaningfully to AI components?",
            ],
            estimated_effort="low",
        ),
        GapResolutionGuidance(
            gap_id="Gap-6",
            description="Data acceptance threshold undefined",
            immediate_actions=[
                "Define project-specific data acceptance criteria based on "
                "the four dimensions: quantity, distribution coverage, "
                "annotation quality, domain representativeness",
                "Use HARA-identified risks (from ISO 26262-3 Cl.6) to prioritise "
                "which data distributions must be covered",
                "Define minimum inter-annotator agreement thresholds "
                "(e.g., Cohen's kappa >= 0.8)",
            ],
            required_decisions=[
                "What distribution coverage is sufficient? (Options: ODD coverage, "
                "edge case coverage, adversarial coverage)",
                "What annotation quality metrics are required?",
                "How to handle long-tail distributions?",
            ],
            evidence_to_produce=[
                "Data acceptance criteria specification",
                "Data distribution coverage report",
                "Annotation quality report with inter-annotator agreement",
                "Data gap analysis (ODD areas not covered by training data)",
            ],
            open_research_questions=[
                "Can data sufficiency be defined formally for a given ODD?",
                "What is the relationship between data quantity and AI reliability?",
                "How to detect and measure distribution shift between training "
                "and operational data?",
            ],
            estimated_effort="medium",
        ),
    ]


def get_gap_resolution_summary() -> dict:
    """Summarise the resolution guidance."""
    guidance = build_practitioner_guidance()
    effort_counts = {}
    for g in guidance:
        effort_counts[g.estimated_effort] = effort_counts.get(g.estimated_effort, 0) + 1

    total_actions = sum(len(g.immediate_actions) for g in guidance)
    total_decisions = sum(len(g.required_decisions) for g in guidance)
    total_evidence = sum(len(g.evidence_to_produce) for g in guidance)
    total_research = sum(len(g.open_research_questions) for g in guidance)

    return {
        "total_gaps": len(guidance),
        "effort_distribution": effort_counts,
        "total_immediate_actions": total_actions,
        "total_required_decisions": total_decisions,
        "total_evidence_items": total_evidence,
        "total_research_questions": total_research,
    }


def print_practitioner_guidance():
    """Print the practitioner guidance."""
    guidance = build_practitioner_guidance()
    summary = get_gap_resolution_summary()

    print("=" * 80)
    print("PRACTITIONER GUIDANCE FOR GAP RESOLUTION")
    print("=" * 80)
    print(f"\n  {summary['total_immediate_actions']} immediate actions across "
          f"{summary['total_gaps']} gaps")
    print(f"  {summary['total_required_decisions']} decisions to make")
    print(f"  {summary['total_evidence_items']} evidence items to produce")
    print(f"  {summary['total_research_questions']} open research questions")

    for g in guidance:
        print(f"\n{'─' * 80}")
        print(f"  {g.gap_id}: {g.description}")
        print(f"  Effort: {g.estimated_effort.upper()}")
        if g.prerequisite_gaps:
            print(f"  Prerequisites: {', '.join(g.prerequisite_gaps)}")
        print(f"\n  IMMEDIATE ACTIONS:")
        for a in g.immediate_actions:
            print(f"    1. {a}")
        print(f"\n  DECISIONS REQUIRED:")
        for d in g.required_decisions:
            print(f"    ? {d}")
        print(f"\n  EVIDENCE TO PRODUCE:")
        for e in g.evidence_to_produce:
            print(f"    > {e}")

"""Constructive integration of the GSN argument pattern (Step 3).

This module builds the integrated GSN by:
1. Starting with ISO/PAS 8800 Annex B as the base structure (G1-G6, S1, A1.4)
2. Adding context nodes C1 (ASIL from HARA) and C2 (TARA results)
3. Augmenting existing goals with claims from ISO 21448 and ISO/SAE 21434
4. Adding new goals G7 (SOTIF residual risk), G8 (cybersecurity risk), G9 (modification)

The output is the integrated GSN shown in Figure 2 and Table 3 of the paper.
"""

from src.gsn.model import (
    Goal,
    Strategy,
    Context,
    Assumption,
    Solution,
    GSNArgument,
    GoalStatus,
)


def build_integrated_gsn() -> GSNArgument:
    """Build the complete integrated GSN argument pattern.

    Returns the GSN argument with all nine goals, the integrated strategy,
    context nodes, assumption, and solution references.
    """
    gsn = GSNArgument(
        name="Integrated Safety and Cybersecurity Case",
        description=(
            "Integrated GSN argument pattern for an AI-based LiDAR perception "
            "component in highly automated driving (SAE Level 4+). Extends "
            "ISO/PAS 8800 Annex B with claims from ISO 26262, ISO 21448, "
            "and ISO/SAE 21434."
        ),
    )

    # ── Context nodes ──────────────────────────────────────────────
    c1 = Context(
        element_id="C1",
        element_type=None,  # set in __post_init__
        text=(
            "ASIL D assigned from HARA. At SAE Level 4+, controllability is C3 "
            "(no human driver). High severity and exposure yield ASIL D."
        ),
        source_standards=["ISO26262"],
        clause_references=["ISO 26262-3 Cl.6", "ISO 26262-3 Cl.6.4.3"],
    )

    c2 = Context(
        element_id="C2",
        element_type=None,
        text=(
            "TARA results: threat scenarios identified for the LiDAR perception "
            "component — LiDAR spoofing, adversarial point cloud perturbation, "
            "model poisoning — with associated risk values (1-5)."
        ),
        source_standards=["ISO21434"],
        clause_references=["ISO/SAE 21434 Cl.15"],
    )

    # ── Assumption ─────────────────────────────────────────────────
    a14 = Assumption(
        element_id="A1.4",
        element_type=None,
        text=(
            "Hardware random faults and systematic faults in non-AI elements "
            "are controlled by established ISO 26262 processes."
        ),
        source_standards=["ISO26262", "ISOPAS8800"],
        clause_references=["ISO/PAS 8800 Annex B A1.4", "ISO 26262 Part 5"],
    )

    # ── G1: Top-level goal (reformulated) ──────────────────────────
    g1 = Goal(
        element_id="G1",
        element_type=None,
        text=(
            "The AI-based perception component satisfies the integrated "
            "safety and cybersecurity requirements allocated to it."
        ),
        source_standards=["ISOPAS8800", "ISO26262", "ISO21434"],
        clause_references=[
            "ISO/PAS 8800 Annex B G1 (reformulated)",
            "ISO 26262-3 Cl.6 (ASIL context)",
            "ISO/SAE 21434 Cl.15 (TARA context)",
        ],
        origin="retained",
        supported_by=["S1"],
        in_context_of=["C1", "C2"],
    )

    # ── S1: Integrated strategy ────────────────────────────────────
    s1 = Strategy(
        element_id="S1",
        element_type=None,
        text=(
            "Argue over four assurance domains: (a) AI-specific insufficiencies "
            "are controlled (ISO/PAS 8800), (b) functional insufficiencies produce "
            "acceptable residual risk (ISO 21448), (c) cybersecurity risks are "
            "managed to an acceptable level (ISO/SAE 21434), (d) hardware random "
            "faults and systematic faults in non-AI elements are controlled "
            "(ISO 26262, via A1.4)."
        ),
        source_standards=["ISOPAS8800", "ISO21448", "ISO21434", "ISO26262"],
        clause_references=["ISO/PAS 8800 Annex B S1 (extended)"],
        supported_by=["G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"],
        in_context_of=["A1.4"],
    )

    # ── G2: Specification sufficiency (retained, augmented) ────────
    g2 = Goal(
        element_id="G2",
        element_type=None,
        text=(
            "The specification is sufficient for all applicable assurance "
            "domains: AI-specific completeness (ISO/PAS 8800), ODD and "
            "triggering condition completeness (ISO 21448), and cybersecurity "
            "requirement completeness (ISO/SAE 21434)."
        ),
        source_standards=["ISOPAS8800", "ISO21448", "ISO21434"],
        clause_references=[
            "ISO/PAS 8800 Cl.5 (AI specification)",
            "ISO 21448 Table A.8 (17 specification items)",
            "ISO/SAE 21434 [RQ-06-01] (cybersecurity specification)",
        ],
        origin="retained",
        augmented_from=["ISO21448", "ISO21434"],
        supported_by=["Sn-G2-spec-review", "Sn-G2-trig-catalogue", "Sn-G2-cyber-spec"],
    )

    # ── G3: Data set sufficiency (retained, single standard) ───────
    g3 = Goal(
        element_id="G3",
        element_type=None,
        text=(
            "Training and test data are sufficient in quantity, distribution "
            "coverage, annotation quality, and domain representativeness."
        ),
        source_standards=["ISOPAS8800"],
        clause_references=[
            "ISO/PAS 8800 Cl.8.4 (data quality)",
            "ISO/IEC TR 5469 Cl.9.3.2 (data linked to HARA, informative)",
        ],
        origin="retained",
        supported_by=["Sn-G3-data-quality", "Sn-G3-distribution", "Sn-G3-annotation"],
        metadata={
            "note": (
                "Only goal where a single standard (ISO/PAS 8800) is the sole "
                "source of normative claims. Data quality for AI remains isolated "
                "from other applicable standards."
            )
        },
    )

    # ── G4: Design sufficiency (retained, augmented) ───────────────
    g4 = Goal(
        element_id="G4",
        element_type=None,
        text=(
            "The AI design satisfies safety and cybersecurity requirements. "
            "Architecture decisions reconcile AI model design with SOTIF "
            "mitigation strategies and cybersecurity controls."
        ),
        source_standards=["ISOPAS8800", "ISO21448", "ISO21434"],
        clause_references=[
            "ISO/PAS 8800 Cl.7 (AI design principles)",
            "ISO 21448 Table A.9 (SOTIF design measures)",
            "ISO/SAE 21434 Cl.10 (cybersecurity control design)",
        ],
        origin="retained",
        augmented_from=["ISO21448", "ISO21434"],
        supported_by=["Sn-G4-ai-design", "Sn-G4-sotif-measures", "Sn-G4-cyber-controls"],
    )

    # ── G5: V&V sufficiency (retained, ALL standards) ──────────────
    g5 = Goal(
        element_id="G5",
        element_type=None,
        text=(
            "Verification and validation evidence is sufficient across all "
            "assurance domains. Four evidence types converge: (a) MC/DC "
            "structural coverage (ISO 26262), (b) scenario-based testing with "
            "triggering condition coverage (ISO 21448), (c) AI-specific metrics "
            "and uncertainty evaluation (ISO/PAS 8800), (d) vulnerability "
            "analysis and penetration testing (ISO/SAE 21434)."
        ),
        source_standards=["ISOPAS8800", "ISO26262", "ISO21448", "ISO21434"],
        clause_references=[
            "ISO/PAS 8800 Cl.8-9 (AI V&V)",
            "ISO 26262-6 Cl.9 (MC/DC at ASIL D)",
            "ISO 21448 Cl.9-11 (scenario testing, triggering conditions)",
            "ISO/SAE 21434 Cl.10 (vulnerability analysis, pen testing)",
        ],
        origin="retained",
        augmented_from=["ISO26262", "ISO21448", "ISO21434"],
        supported_by=[
            "Sn-G5-mcdc", "Sn-G5-scenario", "Sn-G5-ensemble-uncertainty",
            "Sn-G5-pentest",
        ],
        metadata={
            "note": (
                "Only node where ALL four applicable standards contribute "
                "claims simultaneously. Evidence type asymmetry (I-2) is "
                "the central finding of the analysis."
            ),
            "inconsistency": "I-2",
        },
    )

    # ── G6: Monitoring sufficiency (retained, augmented) ───────────
    g6 = Goal(
        element_id="G6",
        element_type=None,
        text=(
            "Operational monitoring covers AI (OOD detection, distributional "
            "drift), SOTIF (field performance, new triggering conditions), "
            "and cybersecurity (vulnerabilities, incidents)."
        ),
        source_standards=["ISOPAS8800", "ISO21448", "ISO21434"],
        clause_references=[
            "ISO/PAS 8800 Cl.14 (AI monitoring)",
            "ISO 21448 Tables A.13-A.14 (field monitoring)",
            "ISO/SAE 21434 Cl.8 (continuous cybersecurity monitoring)",
        ],
        origin="retained",
        augmented_from=["ISO21448", "ISO21434"],
        supported_by=["Sn-G6-ood", "Sn-G6-sotif-field", "Sn-G6-cyber-monitor"],
        metadata={"inconsistency": "I-6"},
    )

    # ── G7: SOTIF residual risk acceptance (NEW) ───────────────────
    g7 = Goal(
        element_id="G7",
        element_type=None,
        text=(
            "Residual risk from functional insufficiencies meets the "
            "acceptance criteria defined per ISO 21448 Clause 6.5. "
            "Area 3 (unknown potentially hazardous) is reduced to an "
            "acceptable level."
        ),
        source_standards=["ISO21448"],
        clause_references=[
            "ISO 21448 Cl.6.5 (acceptance criteria)",
            "ISO 21448 Table A.10 (acceptance criteria evidence)",
            "ISO 21448 Annex A.1 (GSN, Example 2)",
        ],
        origin="new",
        supported_by=["Sn-G7-area-eval", "Sn-G7-acceptance"],
        metadata={
            "note": (
                "Separate goal (not sub-goal of G5) because it represents "
                "an acceptability judgement about residual risk, not a "
                "verification activity."
            ),
            "inconsistency": "I-5",
        },
    )

    # ── G8: Cybersecurity risk management (NEW) ────────────────────
    g8 = Goal(
        element_id="G8",
        element_type=None,
        text=(
            "Cybersecurity risks identified through TARA are treated to an "
            "acceptable level. The safety impact of each threat scenario is "
            "assessed using ISO 26262-3 severity classes ([RQ-15-06])."
        ),
        source_standards=["ISO21434", "ISO26262"],
        clause_references=[
            "ISO/SAE 21434 Cl.3.1.11 (cybersecurity case)",
            "ISO/SAE 21434 Cl.15 (TARA)",
            "ISO/SAE 21434 [RQ-15-06] (safety bridge)",
        ],
        origin="new",
        supported_by=["Sn-G8-tara", "Sn-G8-treatment", "Sn-G8-bridge"],
        metadata={
            "note": (
                "Separate goal for same reason as G7: cybersecurity risk "
                "treatment is an acceptability judgement, not a verification "
                "activity."
            ),
            "inconsistency": "I-5",
        },
    )

    # ── G9: Modification assurance (UNDEVELOPED / GAP) ─────────────
    g9 = Goal(
        element_id="G9",
        element_type=None,
        text=(
            "AI model modifications (OTA updates, retraining) are controlled "
            "with re-assurance criteria. [UNDEVELOPED — no single standard "
            "prescribes the complete re-assurance workflow.]"
        ),
        source_standards=[],
        clause_references=[
            "ISO 26262-8 Cl.8 (change management, partial)",
            "ISO/PAS 8800 Cl.14.8.3 (partial re-approval, partial)",
            "ISO/IEC TR 5469 Table A.8 (change protocols, informative)",
        ],
        status=GoalStatus.UNDEVELOPED,
        origin="undeveloped",
        metadata={
            "gap": "Gap-2",
            "note": (
                "Undeveloped because no standard prescribes a complete "
                "workflow for re-assuring an AI component after modification. "
                "For a retrained neural network, the entire weight space changes."
            ),
        },
    )

    # ── Solution nodes (evidence references) ───────────────────────
    solutions = _build_solutions()

    # ── Add all elements to the GSN ────────────────────────────────
    for element in [c1, c2, a14, g1, s1, g2, g3, g4, g5, g6, g7, g8, g9]:
        gsn.add_element(element)

    for sol in solutions:
        gsn.add_element(sol)

    return gsn


def _build_solutions() -> list[Solution]:
    """Build solution (evidence) nodes for the integrated GSN."""
    return [
        # G2 solutions
        Solution(
            element_id="Sn-G2-spec-review",
            element_type=None,
            text="AI specification review report (ISO/PAS 8800 Cl.5)",
            source_standards=["ISOPAS8800"],
            evidence_type="document_review",
            evidence_description="Review of AI specification against 8800 requirements.",
        ),
        Solution(
            element_id="Sn-G2-trig-catalogue",
            element_type=None,
            text="Triggering condition catalogue (ISO 21448 Cl.7)",
            source_standards=["ISO21448"],
            evidence_type="analysis_report",
            evidence_description="Catalogue of triggering conditions for the perception component.",
        ),
        Solution(
            element_id="Sn-G2-cyber-spec",
            element_type=None,
            text="Cybersecurity requirements specification (ISO/SAE 21434 [RQ-06-01])",
            source_standards=["ISO21434"],
            evidence_type="specification",
            evidence_description="Cybersecurity requirements for the perception component.",
        ),
        # G3 solutions
        Solution(
            element_id="Sn-G3-data-quality",
            element_type=None,
            text="Data quality report (ISO/PAS 8800 Cl.8.4)",
            source_standards=["ISOPAS8800"],
            evidence_type="quality_report",
            evidence_description=(
                "Training data quality assessment: quantity, distribution, "
                "annotation quality, domain representativeness."
            ),
        ),
        Solution(
            element_id="Sn-G3-distribution",
            element_type=None,
            text="Distribution coverage analysis",
            source_standards=["ISOPAS8800"],
            evidence_type="statistical_analysis",
            evidence_description="Analysis of training data distribution vs. operational domain.",
        ),
        Solution(
            element_id="Sn-G3-annotation",
            element_type=None,
            text="Annotation quality metrics",
            source_standards=["ISOPAS8800"],
            evidence_type="quality_metrics",
            evidence_description="Inter-annotator agreement, labelling error rates.",
        ),
        # G4 solutions
        Solution(
            element_id="Sn-G4-ai-design",
            element_type=None,
            text="AI design review (ISO/PAS 8800 Cl.7)",
            source_standards=["ISOPAS8800"],
            evidence_type="design_review",
            evidence_description="Review of SECOND architecture and deep ensemble design.",
        ),
        Solution(
            element_id="Sn-G4-sotif-measures",
            element_type=None,
            text="SOTIF design measures report (ISO 21448 Table A.9)",
            source_standards=["ISO21448"],
            evidence_type="design_measures",
            evidence_description="Avoidance, reduction, and mitigation measures for SOTIF.",
        ),
        Solution(
            element_id="Sn-G4-cyber-controls",
            element_type=None,
            text="Cybersecurity control design (ISO/SAE 21434 Cl.10)",
            source_standards=["ISO21434"],
            evidence_type="security_controls",
            evidence_description="Design of cybersecurity controls against identified threats.",
        ),
        # G5 solutions — THE FOUR CONVERGING EVIDENCE TYPES
        Solution(
            element_id="Sn-G5-mcdc",
            element_type=None,
            text="MC/DC structural coverage of non-AI wrapper code (ISO 26262-6 Cl.9)",
            source_standards=["ISO26262"],
            evidence_type="deterministic_coverage",
            evidence_description=(
                "Modified condition/decision coverage at ASIL D. "
                "Deterministic pass/fail metric. Applies to non-AI code only."
            ),
        ),
        Solution(
            element_id="Sn-G5-scenario",
            element_type=None,
            text=(
                "Scenario-based testing with triggering condition coverage "
                "(ISO 21448 Cl.9-11)"
            ),
            source_standards=["ISO21448"],
            evidence_type="scenario_coverage",
            evidence_description=(
                "CARLA evaluation under parametrically controlled rain and fog. "
                "Scenario count with demonstrated triggering condition coverage."
            ),
        ),
        Solution(
            element_id="Sn-G5-ensemble-uncertainty",
            element_type=None,
            text=(
                "Deep ensemble uncertainty quantification "
                "(ISO/PAS 8800 Cl.8-9)"
            ),
            source_standards=["ISOPAS8800"],
            evidence_type="statistical_metric",
            evidence_description=(
                "Geometric divergence metric from independently trained SECOND "
                "instances. AUROC for out-of-distribution detection. "
                "Statistical distribution, not binary."
            ),
        ),
        Solution(
            element_id="Sn-G5-pentest",
            element_type=None,
            text=(
                "Adversarial penetration testing results "
                "(ISO/SAE 21434 Cl.10)"
            ),
            source_standards=["ISO21434"],
            evidence_type="attack_success_rate",
            evidence_description=(
                "Attack success rates against LiDAR spoofing and point cloud "
                "perturbation under defined threat models."
            ),
        ),
        # G6 solutions
        Solution(
            element_id="Sn-G6-ood",
            element_type=None,
            text="OOD detection and drift monitoring (ISO/PAS 8800 Cl.14)",
            source_standards=["ISOPAS8800"],
            evidence_type="runtime_monitor",
            evidence_description="Runtime ensemble disagreement as OOD indicator.",
        ),
        Solution(
            element_id="Sn-G6-sotif-field",
            element_type=None,
            text="SOTIF field monitoring (ISO 21448 Tables A.13-A.14)",
            source_standards=["ISO21448"],
            evidence_type="field_monitoring",
            evidence_description="Field performance tracking and new triggering condition discovery.",
        ),
        Solution(
            element_id="Sn-G6-cyber-monitor",
            element_type=None,
            text="Continuous cybersecurity monitoring (ISO/SAE 21434 Cl.8)",
            source_standards=["ISO21434"],
            evidence_type="security_monitoring",
            evidence_description="Vulnerability scanning, incident detection, threat intelligence.",
        ),
        # G7 solutions
        Solution(
            element_id="Sn-G7-area-eval",
            element_type=None,
            text="Four-area model evaluation (ISO 21448 Cl.5)",
            source_standards=["ISO21448"],
            evidence_type="risk_evaluation",
            evidence_description="Evaluation of Area 3 reduction to acceptable level.",
        ),
        Solution(
            element_id="Sn-G7-acceptance",
            element_type=None,
            text="Acceptance criteria assessment (ISO 21448 Cl.6.5, Table A.10)",
            source_standards=["ISO21448"],
            evidence_type="acceptance_decision",
            evidence_description="Comparison of residual risk to defined acceptance criteria.",
        ),
        # G8 solutions
        Solution(
            element_id="Sn-G8-tara",
            element_type=None,
            text="TARA report (ISO/SAE 21434 Cl.15)",
            source_standards=["ISO21434"],
            evidence_type="threat_analysis",
            evidence_description="Complete threat analysis and risk assessment.",
        ),
        Solution(
            element_id="Sn-G8-treatment",
            element_type=None,
            text="Risk treatment plan (ISO/SAE 21434 Cl.15)",
            source_standards=["ISO21434"],
            evidence_type="treatment_plan",
            evidence_description="Cybersecurity risk treatment decisions and residual risk.",
        ),
        Solution(
            element_id="Sn-G8-bridge",
            element_type=None,
            text="Safety-cybersecurity impact assessment (ISO/SAE 21434 [RQ-15-06])",
            source_standards=["ISO21434", "ISO26262"],
            evidence_type="impact_assessment",
            evidence_description=(
                "Assessment of safety impact of each threat scenario "
                "using ISO 26262-3 severity classes."
            ),
        ),
    ]

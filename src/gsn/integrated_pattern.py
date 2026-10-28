"""Constructive integration of the GSN argument pattern (Step 3).

This module builds the integrated GSN by:
1. Starting with ISO/PAS 8800 Annex B as the base structure (G1-G6, S1, A1.4)
2. Adding context nodes C1 (ASIL from HARA) and C2 (TARA results)
3. Augmenting existing goals with claims from ISO 21448 and ISO/SAE 21434
4. Adding new goals G7 (SOTIF residual risk), G8 (cybersecurity risk), G9 (modification)

The output is the integrated GSN shown in Fig. 1 and Table 2 of the WAISE paper.
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
            "ASIL D for the case study, from the ISO 26262-3 hazard analysis "
            "and risk assessment (HARA): at SAE Level 4 and above, "
            "controllability is commonly rated C3 in the absence of a driver; "
            "with severity S3 and exposure E4 this gives ASIL D (Cl.6.4.3, "
            "classification of hazardous events)."
        ),
        source_standards=["ISO26262"],
        clause_references=["ISO 26262-3 Cl.6", "ISO 26262-3 Cl.6.4.3"],
    )

    c2 = Context(
        element_id="C2",
        element_type=None,
        text=(
            "Results of the threat analysis and risk assessment (TARA): threat "
            "scenarios identified for the LiDAR perception component (LiDAR "
            "spoofing, adversarial point cloud perturbation, model poisoning), "
            "each with a risk value from 1 to 5."
        ),
        source_standards=["ISO21434"],
        clause_references=["ISO/SAE 21434 Cl.15"],
    )

    # ── Assumption ─────────────────────────────────────────────────
    a14 = Assumption(
        element_id="A1.4",
        element_type=None,
        text=(
            "Hardware faults in the non-AI elements are controlled under "
            "ISO 26262 (Annex B Assumption A1.4)."
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
            "managed to an acceptable level (ISO/SAE 21434), (d) hardware faults "
            "in the non-AI elements are controlled (ISO 26262, delegated "
            "through Assumption A1.4)."
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
            "domains: AI-specific completeness of the semantic and syntactic "
            "input space derived from the system-level operational design "
            "domain (ISO/PAS 8800), SOTIF triggering condition coverage "
            "(ISO 21448), and cybersecurity requirements (ISO/SAE 21434)."
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
                "Of the four standards in scope, only ISO/PAS 8800 contributes "
                "normative claims to G3, so G3 is the only retained goal (G2 to "
                "G6) with a single contributing standard. ISO/IEC TR 5469 "
                "Cl.9.3.2 links data distributions to HARA-identified risks but "
                "is an informative technical report."
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
            "assurance domains. The case-study evidence set includes one "
            "evidence type per standard: (a) MC/DC structural coverage of the "
            "surrounding non-AI software (ISO 26262), (b) SOTIF triggering "
            "condition coverage in scenario testing (ISO 21448), (c) deep "
            "ensemble disagreement as uncertainty indicator, measured by AUROC "
            "(ISO/PAS 8800), (d) adversarial penetration testing against LiDAR "
            "spoofing and perturbation (ISO/SAE 21434)."
        ),
        source_standards=["ISOPAS8800", "ISO26262", "ISO21448", "ISO21434"],
        clause_references=[
            "ISO/PAS 8800 Cl.8-9 (AI V&V)",
            "ISO 26262-6 Cl.9 (software unit verification, MC/DC at ASIL D)",
            "ISO 21448 Cl.9-11 (scenario testing, triggering conditions)",
            "ISO/SAE 21434 Cl.10 (integration and verification, incl. "
            "penetration testing)",
        ],
        origin="retained",
        augmented_from=["ISO26262", "ISO21448", "ISO21434"],
        supported_by=[
            "Sn-G5-mcdc", "Sn-G5-scenario", "Sn-G5-ensemble-uncertainty",
            "Sn-G5-pentest",
        ],
        metadata={
            "note": (
                "G5 is the goal where all four standards contribute claims. "
                "The four evidence types are disjoint by design, each on its "
                "own measurement scale, and no standard prescribes how they "
                "combine into a single sufficiency claim at G5 (decision point "
                "DP-2)."
            ),
            "inconsistency": "I-2",
        },
    )

    # ── G6: Monitoring sufficiency (retained, augmented) ───────────
    g6 = Goal(
        element_id="G6",
        element_type=None,
        text=(
            "Operational monitoring covers AI (out-of-distribution detection, "
            "distributional drift), SOTIF (safety of the intended "
            "functionality: field performance, new triggering conditions), "
            "and cybersecurity (cybersecurity events, vulnerabilities)."
        ),
        source_standards=["ISOPAS8800", "ISO21448", "ISO21434"],
        clause_references=[
            "ISO/PAS 8800 Cl.14 (AI monitoring)",
            "ISO 21448 Tables A.13-A.14 (field monitoring)",
            "ISO/SAE 21434 Cl.8 (continual cybersecurity activities, "
            "cybersecurity monitoring)",
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
            "Areas 2 and 3 (known and unknown hazardous scenarios) are "
            "reduced to an acceptable level."
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
                "A separate goal (not a sub-goal of G5) because it represents "
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
            "acceptable level. Safety impact ratings of damage scenarios are "
            "derived from ISO 26262-3 Cl.6.4.3 severity classes ([RQ-15-06])."
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
                "A separate goal for the same reason as G7: the claim that "
                "residual cybersecurity risk is acceptable is an acceptability "
                "judgement, not a verification activity."
            ),
            "inconsistency": "I-5",
        },
    )

    # ── G9: Modification assurance (undeveloped; finding F-2) ──────
    g9 = Goal(
        element_id="G9",
        element_type=None,
        text=(
            "AI model modifications (OTA updates, retraining) are controlled "
            "with re-assurance criteria. [UNDEVELOPED: no single standard "
            "prescribes the complete re-assurance workflow.]"
        ),
        source_standards=[],
        clause_references=[
            "ISO 26262-8 Cl.8 (change management, partial)",
            "ISO/PAS 8800 Cl.14.8.3 (does not define when partial "
            "re-assurance is sufficient)",
            "ISO/IEC TR 5469 Table A.8 (change protocols, informative)",
        ],
        status=GoalStatus.UNDEVELOPED,
        origin="undeveloped",
        metadata={
            "gap": "Gap-2",
            "note": (
                "Undeveloped because no single standard prescribes the "
                "complete re-assurance workflow for a modified AI model; "
                "partial coverage exists across the cited standards. For a "
                "retrained neural network, the entire weight space changes."
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
        # G5 solutions: the four evidence types (a) to (d)
        Solution(
            element_id="Sn-G5-mcdc",
            element_type=None,
            text=(
                "MC/DC coverage of the surrounding non-AI software "
                "(ISO 26262-6 Cl.9)"
            ),
            source_standards=["ISO26262"],
            evidence_type="MC/DC coverage ratio",
            evidence_description=(
                "Modified condition/decision coverage (MC/DC), a coverage "
                "ratio: the fraction of conditions shown to independently "
                "affect the decision outcome. Structural coverage at software "
                "unit level, highly recommended for ASIL D (ISO 26262-6 Cl.9). "
                "Applies to the non-AI software around the network only."
            ),
            # Fig. 1(b): evidence type (a), dashed.
            instantiation="not produced",
        ),
        Solution(
            element_id="Sn-G5-scenario",
            element_type=None,
            text=(
                "SOTIF triggering condition coverage in scenario testing "
                "(ISO 21448 Cl.9-11)"
            ),
            source_standards=["ISO21448"],
            evidence_type="triggering-condition coverage fraction",
            evidence_description=(
                "Fraction of the identified triggering conditions covered by "
                "scenario tests, under parametrically controlled conditions "
                "such as rain and fog intensity."
            ),
            # Fig. 1(b): evidence type (b), dashed.
            instantiation="not produced",
        ),
        Solution(
            element_id="Sn-G5-ensemble-uncertainty",
            element_type=None,
            text=(
                "Deep ensemble disagreement, measured by AUROC "
                "(ISO/PAS 8800 Cl.8-9)"
            ),
            source_standards=["ISOPAS8800"],
            evidence_type="AUROC of ensemble disagreement",
            evidence_description=(
                "Geometric disagreement among ensemble members as the "
                "uncertainty indicator. AUROC, a scalar between 0 and 1, "
                "scores how well the indicator separates correct from "
                "incorrect detections. Reported on simulated ensemble outputs "
                "calibrated to published LiDAR uncertainty distributions; "
                "validation with trained ensemble inference is future work."
            ),
            # Fig. 1(b): evidence type (c), solid: the one evidence type the
            # case study instantiates, on simulated outputs.
            instantiation="provided (simulated)",
        ),
        Solution(
            element_id="Sn-G5-pentest",
            element_type=None,
            text=(
                "Adversarial penetration testing against LiDAR spoofing "
                "(ISO/SAE 21434 Cl.10)"
            ),
            source_standards=["ISO21434"],
            evidence_type="attack success rate",
            evidence_description=(
                "Attack success rate against LiDAR spoofing and point cloud "
                "perturbation under defined threat models."
            ),
            # Fig. 1(b): evidence type (d), dashed.
            instantiation="not produced",
        ),
        # G6 solutions
        Solution(
            element_id="Sn-G6-ood",
            element_type=None,
            text=(
                "Out-of-distribution (OOD) detection and drift monitoring "
                "(ISO/PAS 8800 Cl.14)"
            ),
            source_standards=["ISOPAS8800"],
            evidence_type="runtime_monitor",
            evidence_description=(
                "Runtime ensemble disagreement as an out-of-distribution "
                "indicator."
            ),
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
            text=(
                "Cybersecurity monitoring under the continual cybersecurity "
                "activities (ISO/SAE 21434 Cl.8)"
            ),
            source_standards=["ISO21434"],
            evidence_type="security_monitoring",
            evidence_description=(
                "Collection and triage of cybersecurity information into "
                "cybersecurity events (Cl.8.3), event evaluation (Cl.8.4), and "
                "vulnerability analysis and management (Cl.8.5 to 8.6)."
            ),
        ),
        # G7 solutions
        Solution(
            element_id="Sn-G7-area-eval",
            element_type=None,
            text="Four-area model evaluation (ISO 21448 Cl.5)",
            source_standards=["ISO21448"],
            evidence_type="risk_evaluation",
            evidence_description=(
                "Evaluation of the reduction of Areas 2 and 3 (known and "
                "unknown hazardous scenarios) to an acceptable level."
            ),
        ),
        Solution(
            element_id="Sn-G7-acceptance",
            element_type=None,
            text="Acceptance criteria evaluation (ISO 21448 Cl.6.5, Table A.10)",
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
            evidence_description=(
                "Threat analysis and risk assessment (TARA) of the perception "
                "component (Cl.15)."
            ),
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
            text=(
                "Safety impact ratings of damage scenarios "
                "(ISO/SAE 21434 [RQ-15-06])"
            ),
            source_standards=["ISO21434", "ISO26262"],
            evidence_type="impact_assessment",
            evidence_description=(
                "Safety impact ratings of damage scenarios, derived from "
                "ISO 26262-3 Cl.6.4.3 severity classes. ISO 26262 enters here "
                "as a normative bridge, not as a source of claims at G8."
            ),
        ),
    ]

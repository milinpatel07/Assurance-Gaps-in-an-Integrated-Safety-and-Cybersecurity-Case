"""Evidence convergence analysis at G5 (decision point DP-2).

This module analyses the evidence type asymmetry, decision point DP-2 (I-2 in
the code): the four evidence types at the V&V goal are disjoint by design,
each on its own measurement scale, and no standard prescribes how they combine
into a single sufficiency claim.

The single-failure-event view (a missed pedestrian detection) is repository
analysis, not in either paper.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvidenceType:
    """One of the four evidence types that converge at G5."""

    name: str
    standard: str
    clause: str
    what_measured: str
    how_produced: str
    scale: str
    case_study_instance: str


@dataclass
class FailureEvent:
    """A single failure event analysed through three paths."""

    description: str
    analysis_paths: list[AnalysisPath] = field(default_factory=list)


@dataclass
class AnalysisPath:
    """One analysis path from a failure event to an evidence type."""

    standard: str
    analysis_method: str
    output: str
    evidence_type: str
    gsn_node: str


class EvidenceConvergenceAnalysis:
    """Analysis of evidence convergence at G5.

    Demonstrates the central finding: a single failure event enters the
    integrated argument through multiple paths, each producing a different
    evidence type at G5, with no standard defining how to combine them.
    """

    def __init__(self):
        self.evidence_types = self._build_evidence_types()
        self.failure_event = self._build_failure_event()

    def _build_evidence_types(self) -> list[EvidenceType]:
        return [
            EvidenceType(
                name="Structural coverage (MC/DC)",
                standard="ISO 26262",
                clause="Part 6, Cl.9",
                what_measured="Code structure of the surrounding non-AI software",
                how_produced="Structural coverage analysis in software unit verification",
                scale=(
                    "Coverage ratio (fraction of conditions shown to "
                    "independently affect the decision outcome)"
                ),
                case_study_instance=(
                    "MC/DC coverage of the non-AI code surrounding the SECOND "
                    "detector (pre-processing, post-processing, interface code)"
                ),
            ),
            EvidenceType(
                name="SOTIF triggering condition coverage in scenario testing",
                standard="ISO 21448",
                clause="Cl.9-11",
                what_measured="Scenario space and triggering condition coverage",
                how_produced="Scenario simulation in CARLA under controlled rain and fog",
                scale=(
                    "Coverage fraction (identified triggering conditions "
                    "covered by scenario tests)"
                ),
                case_study_instance=(
                    "CARLA evaluation under parametrically controlled rain "
                    "(0-100mm/h) and fog (visibility 10-500m) at 5 intensity "
                    "levels each, producing 25 weather combinations"
                ),
            ),
            EvidenceType(
                name="Deep ensemble disagreement as uncertainty indicator",
                standard="ISO/PAS 8800",
                clause="Cl.8-9",
                what_measured=(
                    "How well the uncertainty indicator separates correct from "
                    "incorrect detections"
                ),
                how_produced="Deep ensemble inference with geometric disagreement",
                scale=(
                    "AUROC, a scalar in [0, 1] (separation of correct from "
                    "incorrect detections)"
                ),
                case_study_instance=(
                    "Deep ensemble of 5 independently trained SECOND instances. "
                    "Geometric disagreement of predicted 3D bounding boxes. "
                    "AUROC of the disagreement for separating correct from "
                    "incorrect detections."
                ),
            ),
            EvidenceType(
                name="Adversarial penetration testing against LiDAR spoofing and perturbation",
                standard="ISO/SAE 21434",
                clause="Cl.10",
                what_measured="Attacker capability against the component",
                how_produced="Penetration testing with defined threat models",
                scale="Attack success rate under the threat model",
                case_study_instance=(
                    "LiDAR spoofing attacks (injected ghost points) and "
                    "adversarial point cloud perturbations (PGD on voxel features). "
                    "Attack success rate at varying perturbation budgets."
                ),
            ),
        ]

    def _build_failure_event(self) -> FailureEvent:
        """Build the example failure event (repository analysis)."""
        return FailureEvent(
            description=(
                "LiDAR detector misses a pedestrian: a single physical event "
                "that enters the integrated argument through three analysis paths"
            ),
            analysis_paths=[
                AnalysisPath(
                    standard="ISO 26262",
                    analysis_method="HARA (Part 3, Cl.6)",
                    output="ASIL D (severity S3, exposure E4, controllability C3)",
                    evidence_type="MC/DC structural coverage (coverage ratio)",
                    gsn_node="G5",
                ),
                AnalysisPath(
                    standard="ISO 21448",
                    analysis_method="Triggering condition identification (Cl.7)",
                    output="Triggering condition: heavy rain reduces point density",
                    evidence_type=(
                        "Triggering-condition coverage in scenario testing"
                    ),
                    gsn_node="G5",
                ),
                AnalysisPath(
                    standard="ISO/SAE 21434",
                    analysis_method="TARA threat scenario (Cl.15)",
                    output="Threat: LiDAR spoofing causes false negative",
                    evidence_type="Penetration testing (attack success rate)",
                    gsn_node="G5",
                ),
            ],
        )

    def get_evidence_comparison_matrix(self) -> list[dict]:
        """Return the evidence comparison as a list of dicts for tabulation."""
        return [
            {
                "Evidence Type": et.name,
                "Standard": et.standard,
                "What Measured": et.what_measured,
                "How Produced": et.how_produced,
                "Scale": et.scale,
            }
            for et in self.evidence_types
        ]

    def print_analysis(self):
        """Print the evidence convergence analysis."""
        print("=" * 80)
        print("EVIDENCE CONVERGENCE AT G5 (decision point DP-2)")
        print("=" * 80)

        print("\n--- Four Evidence Types at G5 ---")
        for i, et in enumerate(self.evidence_types, 1):
            print(f"\n  [{i}] {et.name}")
            print(f"      Standard:     {et.standard} {et.clause}")
            print(f"      Measures:     {et.what_measured}")
            print(f"      Produced by:  {et.how_produced}")
            print(f"      Scale:        {et.scale}")
            print(f"      Case study:   {et.case_study_instance[:80]}...")

        print("\n--- Single failure event (repository analysis, not in either paper) ---")
        print(f"\n  Event: {self.failure_event.description}")
        for path in self.failure_event.analysis_paths:
            print(f"\n  Path via {path.standard}:")
            print(f"    Method:   {path.analysis_method}")
            print(f"    Output:   {path.output}")
            print(f"    Evidence: {path.evidence_type}")
            print(f"    Node:     {path.gsn_node}")

        print("\n--- Decision point DP-2 ---")
        print(
            "  The four evidence types are disjoint by design, each on its own "
            "measurement scale, and no standard prescribes how they combine "
            "into a single sufficiency claim at G5; the integrated V&V strategy "
            "is the engineer's responsibility."
        )

    def get_solution_sketch(self) -> dict:
        """Return a sketch of possible approaches to combining the four evidence types.

        Repository analysis, not in either paper. It does not solve the
        combination problem; it records directions for further work. The
        example threshold values are illustrative: no clause in the four
        standards gives any of them.
        """
        label = "Repository analysis, not in either paper."
        return {
            "label": label,
            "problem": (
                f"{label} At G5, the four evidence types (a) to (d) are disjoint "
                "by design, each on its own measurement scale (coverage ratio, "
                "count, AUROC, attack success rate), and none of the four "
                "standards prescribes how they combine into a single sufficiency "
                "claim at G5."
            ),
            "approaches": [
                {
                    "name": "Threshold per evidence type with a conjunctive rule",
                    "description": (
                        "Define a minimum threshold for each evidence type independently "
                        "and claim sufficiency only if all thresholds are met. Example "
                        "values, illustrative only and not taken from any standard: "
                        "MC/DC 100%, scenario coverage 95%, AUROC 0.95, attack success "
                        "rate at most 5%."
                    ),
                    "pros": [
                        "It is simple to implement and to audit.",
                        "It is conservative, because every evidence type must pass.",
                    ],
                    "cons": [
                        "It does not capture interactions between evidence types.",
                        "No clause in the four standards gives the threshold values, "
                        "so each value is an engineering decision that needs its own "
                        "justification.",
                        "It cannot trade strength in one evidence type against "
                        "weakness in another.",
                    ],
                    "feasibility": (
                        "It could be applied with existing tooling once the threshold "
                        "values are chosen and justified."
                    ),
                },
                {
                    "name": "Weighted Dempster-Shafer belief combination",
                    "description": (
                        "Map each evidence type to a belief mass function over "
                        "{sufficient, insufficient, uncertain}. Combine using "
                        "Dempster's rule of combination. Claim sufficiency when "
                        "Bel(sufficient) exceeds a threshold."
                    ),
                    "pros": [
                        "It represents uncertainty and conflicting evidence formally.",
                        "It can model partial confidence in each evidence type.",
                    ],
                    "cons": [
                        "Mapping each scale to belief masses is a subjective step.",
                        "Dempster's rule can give counterintuitive results when the "
                        "evidence conflicts strongly.",
                        "The combination is harder to audit than a set of thresholds.",
                    ],
                    "feasibility": (
                        "It needs expert elicitation to assign the belief masses."
                    ),
                },
                {
                    "name": "Multi-criteria decision analysis (MCDA)",
                    "description": (
                        "Treat each evidence type as a criterion. Use MCDA methods "
                        "(e.g., TOPSIS, AHP) to rank the overall assurance level. "
                        "Weight criteria by safety relevance."
                    ),
                    "pros": [
                        "The weighting scheme is flexible.",
                        "The decision process is transparent.",
                        "It can take stakeholder preferences into account.",
                    ],
                    "cons": [
                        "The weights are subjective.",
                        "It is not standard practice in functional safety.",
                        "Regulatory auditors may not accept it.",
                    ],
                    "feasibility": (
                        "The methods are well understood, but they have not been "
                        "applied to this combination problem."
                    ),
                },
            ],
            "recommendation": (
                f"{label} The threshold-per-type approach is the most auditable "
                "starting point for practical use, provided each threshold value "
                "is justified as an engineering decision. The Dempster-Shafer "
                "approach gives a formal combination of heterogeneous evidence "
                "under uncertainty and is a candidate for further research."
            ),
        }

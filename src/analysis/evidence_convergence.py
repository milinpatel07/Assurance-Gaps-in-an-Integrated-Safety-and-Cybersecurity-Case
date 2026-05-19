"""Evidence convergence analysis at G5 (the central finding).

This module analyses the evidence type asymmetry identified as I-2:
four fundamentally different evidence types converge at the V&V goal,
and no standard defines how to combine them.

Figure 3 in the paper illustrates this convergence for a single failure
event (missed pedestrian detection).
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
                what_measured="Code structure of non-AI wrapper",
                how_produced="Static analysis / instrumented testing",
                scale="Binary (pass/fail per condition)",
                case_study_instance=(
                    "MC/DC coverage of the non-AI code surrounding the SECOND "
                    "detector (pre-processing, post-processing, interface code)"
                ),
            ),
            EvidenceType(
                name="Scenario-based testing with triggering condition coverage",
                standard="ISO 21448",
                clause="Cl.9-11",
                what_measured="Scenario space and triggering condition coverage",
                how_produced="Simulation (CARLA) with parametric weather variation",
                scale="Count (scenarios tested / triggering conditions covered)",
                case_study_instance=(
                    "CARLA evaluation under parametrically controlled rain "
                    "(0-100mm/h) and fog (visibility 10-500m) at 5 intensity "
                    "levels each, producing 25 weather combinations"
                ),
            ),
            EvidenceType(
                name="AI-specific uncertainty quantification",
                standard="ISO/PAS 8800",
                clause="Cl.8-9",
                what_measured="Model prediction confidence / OOD detection",
                how_produced="Deep ensemble inference with geometric divergence",
                scale="Statistical distribution (e.g., AUROC for OOD detection)",
                case_study_instance=(
                    "Deep ensemble of 5 independently trained SECOND instances. "
                    "Geometric divergence of predicted 3D bounding boxes. "
                    "AUROC for detecting out-of-distribution inputs."
                ),
            ),
            EvidenceType(
                name="Adversarial penetration testing",
                standard="ISO/SAE 21434",
                clause="Cl.10",
                what_measured="Attacker capability against the component",
                how_produced="Red-teaming with defined threat models",
                scale="Rate (attack success rate under threat model)",
                case_study_instance=(
                    "LiDAR spoofing attacks (injected ghost points) and "
                    "adversarial point cloud perturbations (PGD on voxel features). "
                    "Attack success rate at varying perturbation budgets."
                ),
            ),
        ]

    def _build_failure_event(self) -> FailureEvent:
        """Build the example failure event from Figure 3."""
        return FailureEvent(
            description=(
                "LiDAR detector misses a pedestrian — a single physical event "
                "that enters the integrated argument through three analysis paths"
            ),
            analysis_paths=[
                AnalysisPath(
                    standard="ISO 26262",
                    analysis_method="HARA (Part 3, Cl.6)",
                    output="ASIL D (severity S3, exposure E4, controllability C3)",
                    evidence_type="MC/DC coverage (deterministic, binary)",
                    gsn_node="G5",
                ),
                AnalysisPath(
                    standard="ISO 21448",
                    analysis_method="Triggering condition analysis (Cl.9)",
                    output="Triggering condition: heavy rain reduces point density",
                    evidence_type=(
                        "Scenario coverage + ensemble uncertainty (statistical)"
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
        print("EVIDENCE CONVERGENCE ANALYSIS AT G5 (Central Finding)")
        print("=" * 80)

        print("\n--- Four Evidence Types at G5 ---")
        for i, et in enumerate(self.evidence_types, 1):
            print(f"\n  [{i}] {et.name}")
            print(f"      Standard:     {et.standard} {et.clause}")
            print(f"      Measures:     {et.what_measured}")
            print(f"      Produced by:  {et.how_produced}")
            print(f"      Scale:        {et.scale}")
            print(f"      Case study:   {et.case_study_instance[:80]}...")

        print(f"\n--- Single Failure Event Analysis (Figure 3) ---")
        print(f"\n  Event: {self.failure_event.description}")
        for path in self.failure_event.analysis_paths:
            print(f"\n  Path via {path.standard}:")
            print(f"    Method:   {path.analysis_method}")
            print(f"    Output:   {path.output}")
            print(f"    Evidence: {path.evidence_type}")
            print(f"    Node:     {path.gsn_node}")

        print("\n--- Key Finding ---")
        print(
            "  No standard defines how to combine these four evidence types "
            "into a single sufficiency claim at G5, or what 'sufficient' means "
            "when all four are present."
        )

    def get_solution_sketch(self) -> dict:
        """Return a sketch of potential approaches to combine the four evidence types.

        This does not solve the problem fully — it provides direction for future
        research and demonstrates that the authors have considered resolution paths.
        """
        return {
            "problem": (
                "Four incommensurable evidence types converge at G5. Each uses a "
                "different scale (binary, count, probability, rate). No standard "
                "defines a combination rule or joint sufficiency criterion."
            ),
            "approaches": [
                {
                    "name": "Threshold-per-type with conjunctive rule",
                    "description": (
                        "Define a minimum threshold for each evidence type independently "
                        "(e.g., MC/DC >= 100%, scenario coverage >= 95%, AUROC >= 0.95, "
                        "attack success rate <= 5%). Claim sufficiency iff ALL thresholds met."
                    ),
                    "pros": [
                        "Simple to implement and audit",
                        "Each threshold can be justified from its source standard",
                        "Conservative (all must pass)",
                    ],
                    "cons": [
                        "Does not capture interactions between evidence types",
                        "No principled basis for threshold values",
                        "Cannot trade off strength in one area against weakness in another",
                    ],
                    "feasibility": "HIGH — can be implemented immediately",
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
                        "Handles uncertainty and conflicting evidence formally",
                        "Well-established in safety assessment literature",
                        "Can model partial confidence in each evidence type",
                    ],
                    "cons": [
                        "Requires mapping each scale to belief masses (subjective)",
                        "Dempster's rule can give counterintuitive results with high conflict",
                        "Computationally more complex to audit",
                    ],
                    "feasibility": "MEDIUM — requires expert elicitation for mass assignments",
                },
                {
                    "name": "Multi-criteria decision analysis (MCDA)",
                    "description": (
                        "Treat each evidence type as a criterion. Use MCDA methods "
                        "(e.g., TOPSIS, AHP) to rank the overall assurance level. "
                        "Weight criteria by safety relevance."
                    ),
                    "pros": [
                        "Flexible weighting scheme",
                        "Transparent decision process",
                        "Can incorporate stakeholder preferences",
                    ],
                    "cons": [
                        "Weights are subjective",
                        "Not standard practice in functional safety",
                        "May not satisfy regulatory auditors",
                    ],
                    "feasibility": "MEDIUM — well-understood but novel in this context",
                },
            ],
            "recommendation": (
                "We recommend starting with the threshold-per-type approach for "
                "practical deployments, as it is the most auditable and aligns with "
                "existing standard practices. For research, the Dempster-Shafer "
                "approach offers the most principled combination of heterogeneous "
                "evidence under uncertainty. Both warrant further investigation."
            ),
        }

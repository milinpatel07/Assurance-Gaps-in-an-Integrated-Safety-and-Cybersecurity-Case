"""Finding identification and classification (Step 5 of the method).

Identifies the findings F-1 to F-5 of the WAISE paper (Table 5), written
`Gap-1` to `Gap-5` in the code. The paper's Step 5 (Section 3.2) uses two
categories:
- integration-induced finding (II): emerges only between the scopes of
  individual standards and is not detectable from any single standard in
  isolation (F-3, F-4);
- open methodological problem (OM): the standards prescribe a framework, but no
  published method specifies application-specific values for AI components
  (F-1, F-2, F-5).

The category is held in `AssuranceGap.integration_induced` (True for II).

Each finding also carries a `gap_type` code (MC missing claim, ME missing
evidence, UI unresolved inconsistency). That code is an older
repository-only classification. It is not in either paper, is kept only
because tests and filters in the code use it, and is not exported to the
committed findings file.
"""

from __future__ import annotations

from src.standards.base import AssuranceGap, GapType, LifecyclePhase


# Where each finding sits in the argument. Single source: counterfactual.py and
# traceability.py both read this rather than keeping their own copies, because a
# fact written down twice with nothing holding the copies together is how G2 came
# to contradict a published claim (see tests/test_representation_consistency.py).
GAP_GOAL_MAP: dict[str, list[str]] = {
    "Gap-1": ["G1"],
    "Gap-2": ["G9"],
    "Gap-3": ["G7", "G8"],
    "Gap-4": ["G5"],
    "Gap-5": ["G3"],
}


class GapClassification:
    """The five findings F-1 to F-5 (code ids Gap-1 to Gap-5).

    Each finding corresponds to a row of WAISE Table 5. Two are
    integration-induced findings (F-3, F-4); three are open methodological
    problems (F-1, F-2, F-5).
    """

    def __init__(self):
        self.gaps = self._build_classification()

    def _build_classification(self) -> list[AssuranceGap]:
        return [
            AssuranceGap(
                gap_id="Gap-1",
                # Camera-ready title (WAISE Table 5): "Quantitative acceptance
                # criteria for AI components". The paper's claim is a deferral
                # plus a research gap, not a flat absence: the standards
                # establish frameworks but defer values to context, and no
                # published method derives application-specific targets.
                description=(
                    "Quantitative acceptance criteria for AI components: ISO "
                    "21448 Cl.6.5 establishes the framework but defers "
                    "quantitative values to context, and no published method "
                    "derives application-specific targets for an AI component"
                ),
                gap_type=GapType.MISSING_EVIDENCE,
                lifecycle_phase=LifecyclePhase.VERIFICATION,
                # The camera-ready findings table (WAISE Table 5) gives "Concept, Verification".
                additional_lifecycle_phases=[LifecyclePhase.CONCEPT],
                partial_coverage=[
                    "ISO 26262-5 Cl.8 (SPFM >= 99%, LFM >= 90%) and Cl.9 "
                    "(PMHF < 10^-8 h^-1), ASIL D, hardware only",
                    "ISO 21448 Cl.6.5 (establishes the acceptance-criteria framework, "
                    "including risk tolerability principles, but defers "
                    "quantitative values to context)",
                    "ISO/IEC TR 5469 Cl.9.2.2 (non-separability acknowledged)",
                ],
                integration_induced=False,
            ),
            AssuranceGap(
                gap_id="Gap-2",
                description=(
                    "Over-the-air (OTA) re-assurance workflow (partial "
                    "coverage): no single standard prescribes the complete "
                    "re-assurance workflow for a modified AI model"
                ),
                gap_type=GapType.MISSING_CLAIM,
                lifecycle_phase=LifecyclePhase.MODIFICATION,
                partial_coverage=[
                    "ISO 26262-8 Cl.8 (change management, assumes conventional "
                    "software)",
                    "ISO/PAS 8800 Cl.14.8.3 (does not define when partial "
                    "re-assurance is sufficient)",
                    "ISO 24089 (software update engineering; specifies the update "
                    "process, not re-assurance of a modified AI model's argument)",
                    "ISO/IEC TR 5469 Table A.8 (change protocols, informative "
                    "only)",
                ],
                integration_induced=False,
            ),
            AssuranceGap(
                gap_id="Gap-3",
                description=(
                    "Adversarial-SOTIF boundary unowned: adversarial inputs that "
                    "exploit functional insufficiencies fall between G7 and G8 "
                    "without belonging to either"
                ),
                gap_type=GapType.UNRESOLVED_INCONSISTENCY,
                lifecycle_phase=LifecyclePhase.VERIFICATION,
                # The camera-ready findings table (WAISE Table 5) gives "Verification, Operation".
                additional_lifecycle_phases=[LifecyclePhase.OPERATION],
                partial_coverage=[
                    "ISO 21448 Cl.1 (explicitly excludes cybersecurity threats)",
                    "ISO/SAE 21434 Cl.15 (includes threat scenarios such as "
                    "LiDAR spoofing)",
                ],
                integration_induced=True,
            ),
            AssuranceGap(
                gap_id="Gap-4",
                description=(
                    "No cross-domain release decision criteria: a component "
                    "can satisfy each standard individually, yet no standard "
                    "requires evaluating the combined residual risk across "
                    "domains"
                ),
                gap_type=GapType.MISSING_CLAIM,
                lifecycle_phase=LifecyclePhase.INTEGRATION,
                partial_coverage=[
                    "ISO 26262-2 Cl.6.4.8 (the encompassing system safety case collects "
                    "the per-domain assessments but does not define how their "
                    "residual risks combine into one release decision)",
                    "ISO/SAE 21434 Cl.3.1.11 (cybersecurity case)",
                    "ISO 21448 Cl.12 (evaluation of the achievement of SOTIF; "
                    "release recommendation)",
                ],
                integration_induced=True,
            ),
            AssuranceGap(
                gap_id="Gap-5",
                # Camera-ready title (WAISE Table 5): "Data acceptance criteria for
                # AI components". As with Gap-1, the paper's claim is a
                # deferral: ISO/PAS 8800 Cl.8.4 and TR 5469 Cl.9.3.3 prescribe
                # frameworks and criteria but defer thresholds to context.
                description=(
                    "Data acceptance criteria for AI components: ISO/PAS 8800 "
                    "Cl.8.4 prescribes data quality requirements but defers "
                    "thresholds to context, and no published method derives an "
                    "application-specific threshold"
                ),
                gap_type=GapType.MISSING_EVIDENCE,
                lifecycle_phase=LifecyclePhase.DESIGN,
                partial_coverage=[
                    "ISO/PAS 8800 Cl.8.4, Annex B G3 (prescribes data quality "
                    "requirements as a framework, but defers thresholds to context)",
                    "ISO/IEC TR 5469 Cl.9.3.2 (data linked to HARA, informative)",
                    "ISO/IEC TR 5469 Cl.9.3.3 (four criteria, informative)",
                ],
                integration_induced=False,
            ),
        ]

    def get_by_id(self, gap_id: str) -> AssuranceGap | None:
        for g in self.gaps:
            if g.gap_id == gap_id:
                return g
        return None

    def get_by_type(self, gap_type: GapType) -> list[AssuranceGap]:
        return [g for g in self.gaps if g.gap_type == gap_type]

    def get_integration_induced(self) -> list[AssuranceGap]:
        return [g for g in self.gaps if g.integration_induced]

    def get_by_phase(self, phase: LifecyclePhase) -> list[AssuranceGap]:
        # Match any phase the paper lists for the finding, not only the primary
        # one. WAISE Table 5 gives two phases each for F-1 and F-3.
        return [g for g in self.gaps if phase in g.lifecycle_phases]

    def print_classification(self):
        """Print the findings in the paper's two categories (WAISE Table 5)."""
        print("=" * 80)
        print("FINDINGS (Step 5 output; WAISE Table 5)")
        print("=" * 80)
        print("II = integration-induced finding, OM = open methodological problem")

        for gap in self.gaps:
            finding_id = gap.gap_id.replace("Gap-", "F-", 1)
            category = "II" if gap.integration_induced else "OM"
            print(f"\n{finding_id} ({gap.gap_id}) [{category}]: {gap.description}")
            print(f"  Lifecycle phase: {gap.lifecycle_phase_label}")
            print("  Partial coverage:")
            for pc in gap.partial_coverage:
                print(f"    - {pc}")

    def severity_scores(self) -> list[dict]:
        """Compute severity scores for each finding.

        Repository analysis, not in either paper.

        Scoring dimensions (each 1-5):
        - Safety impact: potential harm if the finding is not addressed
        - Exploitability: how likely the finding leads to a real failure
        - Detectability: how hard the finding is to detect without integration
        - Remediation complexity: effort needed to close the finding

        Overall severity = mean of the four dimensions.
        """
        scores = {
            "Gap-1": {
                "gap_id": "Gap-1",
                "description": "Quantitative acceptance criteria for AI components",
                "safety_impact": 4,
                "exploitability": 3,
                "detectability": 2,
                "remediation_complexity": 5,
                "rationale": (
                    "High safety impact (no numeric target for AI reliability at ASIL D). "
                    "Moderate exploitability (systematic failures can occur). "
                    "Easy to detect (known limitation). "
                    "Very hard to remediate (requires new research on AI reliability metrics)."
                ),
            },
            "Gap-2": {
                "gap_id": "Gap-2",
                "description": "OTA re-assurance workflow (partial coverage)",
                "safety_impact": 4,
                "exploitability": 4,
                "detectability": 2,
                "remediation_complexity": 4,
                "rationale": (
                    "High safety impact (OTA updates can introduce regressions). "
                    "High exploitability (OTA updates are frequent for AI). "
                    "Easy to detect (assessors know about OTA). "
                    "Hard to remediate (requires cross-standard workflow)."
                ),
            },
            "Gap-3": {
                "gap_id": "Gap-3",
                "description": "Adversarial-SOTIF boundary unowned",
                "safety_impact": 5,
                "exploitability": 4,
                "detectability": 5,
                "remediation_complexity": 4,
                "rationale": (
                    "Critical safety impact (adversarial attacks that exploit a functional "
                    "insufficiency fall between G7 and G8, and no standard assigns them). "
                    "High exploitability (adversarial LiDAR attacks are demonstrated). "
                    "Very hard to detect (visible only when the standards are integrated). "
                    "Hard to remediate (requires ISO 21448/21434 scope alignment)."
                ),
            },
            "Gap-4": {
                "gap_id": "Gap-4",
                "description": "No cross-domain release decision criteria",
                "safety_impact": 5,
                "exploitability": 5,
                "detectability": 4,
                "remediation_complexity": 5,
                "rationale": (
                    "Critical safety impact (release without evaluating the combined "
                    "residual risk). "
                    "Very high exploitability (every release decision is affected). "
                    "Hard to detect (each standard has its own release criteria). "
                    "Very hard to remediate (requires a cross-domain release criterion "
                    "for combined residual risk; distinct from the G5 evidence-combination "
                    "decision point DP-2)."
                ),
            },
            "Gap-5": {
                "gap_id": "Gap-5",
                "description": "Data acceptance criteria for AI components",
                "safety_impact": 3,
                "exploitability": 3,
                "detectability": 2,
                "remediation_complexity": 4,
                "rationale": (
                    "Moderate safety impact (data quality affects model performance). "
                    "Moderate exploitability (unclear when data is sufficient). "
                    "Easy to detect (known limitation). "
                    "Hard to remediate (domain-specific, no universal threshold)."
                ),
            },
        }

        result = []
        for gap in self.gaps:
            s = scores.get(gap.gap_id, {})
            dims = [s.get("safety_impact", 0), s.get("exploitability", 0),
                    s.get("detectability", 0), s.get("remediation_complexity", 0)]
            overall = sum(dims) / len(dims) if dims else 0
            result.append({
                **s,
                # The classification above is the single source for the
                # description; the copies in the scores dict had already
                # drifted from it once.
                "description": gap.description,
                "integration_induced": gap.integration_induced,
                "overall_severity": round(overall, 1),
                "priority": "CRITICAL" if overall >= 4.0 else "HIGH" if overall >= 3.0 else "MEDIUM",
            })

        return result

    def summary_statistics(self) -> dict:
        return {
            "total": len(self.gaps),
            "missing_claim": len(self.get_by_type(GapType.MISSING_CLAIM)),
            "missing_evidence": len(self.get_by_type(GapType.MISSING_EVIDENCE)),
            "unresolved_inconsistency": len(
                self.get_by_type(GapType.UNRESOLVED_INCONSISTENCY)
            ),
            "integration_induced": len(self.get_integration_induced()),
        }

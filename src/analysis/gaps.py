"""Assurance gap identification and classification (Step 5 of the methodology).

Identifies nodes in the integrated GSN where no applicable standard provides
the required claim or evidence.

Three gap types (Section 3.2, Step 5):
- Missing Claim (MC): argument requires a claim but no standard contains it
- Missing Evidence (ME): claim exists but no standard prescribes evidence for AI
- Unresolved Inconsistency (UI): inconsistency requires resolution no standard provides
"""

from __future__ import annotations

from src.standards.base import AssuranceGap, GapType, LifecyclePhase


class GapClassification:
    """The six assurance gaps identified in the analysis.

    Each gap corresponds to a row in Table 6 of the paper.
    Two gaps (Gap-3, Gap-4) are integration-induced.
    """

    def __init__(self):
        self.gaps = self._build_classification()

    def _build_classification(self) -> list[AssuranceGap]:
        return [
            AssuranceGap(
                gap_id="Gap-1",
                description="No AI-specific quantitative reliability target",
                gap_type=GapType.MISSING_EVIDENCE,
                lifecycle_phase=LifecyclePhase.VERIFICATION,
                partial_coverage=[
                    "ISO 26262-5 Cl.9 (HW metrics: SPFM >= 99%, LFM >= 90%, "
                    "PMHF < 10^-8 h^-1 — hardware only)",
                    "ISO 21448 Cl.6.5 (qualitative acceptance criteria)",
                    "ISO/IEC TR 5469 Cl.9.2.2 (non-separability acknowledged)",
                ],
                integration_induced=False,
            ),
            AssuranceGap(
                gap_id="Gap-2",
                description="No complete OTA re-assurance workflow for AI",
                gap_type=GapType.MISSING_CLAIM,
                lifecycle_phase=LifecyclePhase.MODIFICATION,
                partial_coverage=[
                    "ISO 26262-8 Cl.8 (change management — assumes conventional SW)",
                    "ISO/PAS 8800 Cl.14.8.3 (partial re-approval — incomplete)",
                    "ISO/IEC TR 5469 Table A.8 (change protocols — informative only)",
                ],
                integration_induced=False,
            ),
            AssuranceGap(
                gap_id="Gap-3",
                description=(
                    "Adversarial-SOTIF boundary unowned — adversarial inputs that "
                    "exploit functional insufficiencies fall between G7 and G8"
                ),
                gap_type=GapType.UNRESOLVED_INCONSISTENCY,
                lifecycle_phase=LifecyclePhase.VERIFICATION,
                partial_coverage=[
                    "ISO 21448 Cl.1 (explicitly excludes cybersecurity threats)",
                    "ISO/SAE 21434 Cl.15 (includes adversarial scenarios)",
                ],
                integration_induced=True,
            ),
            AssuranceGap(
                gap_id="Gap-4",
                description=(
                    "No cross-domain release decision criteria — four separate "
                    "evidence sets with no combined evaluation"
                ),
                gap_type=GapType.MISSING_CLAIM,
                lifecycle_phase=LifecyclePhase.INTEGRATION,
                partial_coverage=[
                    "ISO 26262-2 Cl.6.4 (functional safety assessment)",
                    "ISO/SAE 21434 Cl.3.1.11 (cybersecurity case)",
                    "ISO 21448 Cl.12 (SOTIF release decision)",
                ],
                integration_induced=True,
            ),
            AssuranceGap(
                gap_id="Gap-5",
                description=(
                    "No ASIL-to-AI-class mapping — cannot derive AI assurance "
                    "depth from ASIL D assignment"
                ),
                gap_type=GapType.MISSING_EVIDENCE,
                lifecycle_phase=LifecyclePhase.CONCEPT,
                partial_coverage=[
                    "ISO 26262-3 Cl.6 (ASIL assignment)",
                    "ISO/IEC TR 5469 Cl.6.2, Table 1 (AI technology classes)",
                ],
                integration_induced=False,
            ),
            AssuranceGap(
                gap_id="Gap-6",
                description=(
                    "Data acceptance threshold undefined — no standard prescribes "
                    "when training data are sufficient"
                ),
                gap_type=GapType.MISSING_EVIDENCE,
                lifecycle_phase=LifecyclePhase.DESIGN,
                partial_coverage=[
                    "ISO/PAS 8800 Cl.8.4, Annex B G3 (claim exists)",
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
        return [g for g in self.gaps if g.lifecycle_phase == phase]

    def print_classification(self):
        """Print the gap classification (Table 6)."""
        print("=" * 80)
        print("ASSURANCE GAPS (Step 5 Output — Table 6)")
        print("=" * 80)

        type_labels = {
            GapType.MISSING_CLAIM: "MC",
            GapType.MISSING_EVIDENCE: "ME",
            GapType.UNRESOLVED_INCONSISTENCY: "UI",
        }

        for gap in self.gaps:
            tl = type_labels[gap.gap_type]
            ind = " [INTEGRATION-INDUCED]" if gap.integration_induced else ""
            print(f"\n{gap.gap_id} [{tl}]{ind} — {gap.description}")
            print(f"  Lifecycle phase: {gap.lifecycle_phase.display_name}")
            print(f"  Partial coverage:")
            for pc in gap.partial_coverage:
                print(f"    - {pc}")

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

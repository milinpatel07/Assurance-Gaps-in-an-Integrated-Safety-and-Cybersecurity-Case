"""Counterfactual analysis: what each standard misses when applied in isolation.

Demonstrates that Gap-3 and Gap-4 are integration-induced — they only
become visible when standards are combined. This is the strongest
contribution of the paper.

For each standard, we show:
- What it covers
- What it explicitly excludes or does not address
- Which gaps remain invisible from its perspective alone
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StandardPerspective:
    """What an assessor sees when following a single standard."""

    standard_id: str
    standard_name: str
    covers: list[str]
    excludes: list[str]
    visible_gaps: list[str]
    invisible_gaps: list[str]
    blind_spots: list[str]


class CounterfactualAnalysis:
    """Counterfactual analysis showing what each standard misses alone.

    Key insight: Gap-3 (adversarial-SOTIF boundary) and Gap-4 (cross-domain
    release criteria) are only visible when standards are integrated.
    """

    def __init__(self):
        self.perspectives = self._build_perspectives()

    def _build_perspectives(self) -> list[StandardPerspective]:
        return [
            StandardPerspective(
                standard_id="ISO 26262",
                standard_name="Functional Safety",
                covers=[
                    "HARA and ASIL classification (Part 3, Cl.6)",
                    "Technical safety concept (Part 4, Cl.6)",
                    "MC/DC structural coverage (Part 6, Cl.9)",
                    "HW metrics: SPFM, LFM, PMHF (Part 5, Cl.9)",
                    "Change management (Part 8, Cl.8)",
                    "Safety case structure (Part 2, Cl.6.4)",
                ],
                excludes=[
                    "AI/ML components (assumes deterministic SW)",
                    "Cybersecurity threats (deferred to ISO/SAE 21434)",
                    "SOTIF / functional insufficiencies",
                    "Data quality for training",
                    "Runtime monitoring for ML",
                ],
                visible_gaps=["Gap-1 (no AI reliability target)", "Gap-2 (no OTA re-assurance)"],
                invisible_gaps=[
                    "Gap-3 (adversarial-SOTIF boundary — not aware SOTIF excludes cyber)",
                    "Gap-4 (cross-domain release — only sees safety assessment)",
                ],
                blind_spots=[
                    "An assessor following only ISO 26262 assumes cybersecurity is "
                    "handled elsewhere and SOTIF does not apply. They would produce "
                    "a complete safety case that is structurally sound but misses "
                    "AI-specific failure modes and adversarial threats entirely.",
                ],
            ),
            StandardPerspective(
                standard_id="ISO 21448",
                standard_name="SOTIF",
                covers=[
                    "Four-area model for functional insufficiency (Cl.5)",
                    "Triggering condition identification (Cl.7)",
                    "Scenario-based V&V (Cl.9-11)",
                    "SOTIF acceptance criteria (Cl.6.5)",
                    "SOTIF release decision (Cl.12)",
                    "Field monitoring for unknown scenarios (Cl.13)",
                ],
                excludes=[
                    "Cybersecurity threats (Cl.1 explicitly excludes them)",
                    "Random hardware failures (deferred to ISO 26262)",
                    "AI training data quality",
                    "Model uncertainty quantification",
                ],
                visible_gaps=["Gap-1 (qualitative, not quantitative acceptance)"],
                invisible_gaps=[
                    "Gap-3 (adversarial-SOTIF boundary — excludes cyber by scope, "
                    "so adversarial inputs that exploit functional insufficiency "
                    "fall into a void)",
                    "Gap-4 (cross-domain release — only SOTIF release decision, "
                    "no combined evaluation with safety/cyber evidence)",
                ],
                blind_spots=[
                    "An assessor following only ISO 21448 would identify triggering "
                    "conditions and test scenarios but would explicitly exclude "
                    "adversarial perturbations (Cl.1). An adversarial LiDAR spoofing "
                    "attack that exploits a functional insufficiency (e.g., rain-like "
                    "point patterns) would not be analysed under SOTIF alone.",
                ],
            ),
            StandardPerspective(
                standard_id="ISO/SAE 21434",
                standard_name="Cybersecurity Engineering",
                covers=[
                    "TARA: threat analysis and risk assessment (Cl.15)",
                    "Cybersecurity concept and requirements (Cl.9-10)",
                    "Penetration testing and vulnerability analysis (Cl.10)",
                    "Continuous cybersecurity monitoring (Cl.8)",
                    "Cybersecurity case (Cl.3.1.11)",
                    "Safety-cybersecurity interface requirement (RQ-15-06)",
                ],
                excludes=[
                    "Functional safety assessment (deferred to ISO 26262)",
                    "SOTIF / performance insufficiency",
                    "AI/ML-specific threats beyond standard software",
                    "Training data poisoning (not explicitly covered)",
                ],
                visible_gaps=[],
                invisible_gaps=[
                    "Gap-3 (adversarial-SOTIF boundary — cybersecurity includes "
                    "adversarial scenarios but does not classify them as SOTIF "
                    "triggering conditions, so the functional impact is unowned)",
                    "Gap-4 (cross-domain release — only cybersecurity case, "
                    "no combined evaluation)",
                ],
                blind_spots=[
                    "An assessor following only ISO/SAE 21434 would identify LiDAR "
                    "spoofing as a cybersecurity threat and require penetration "
                    "testing. But they would not recognise that the same attack "
                    "also triggers a SOTIF functional insufficiency (false negative "
                    "under rain-like point injection). The functional safety impact "
                    "falls outside their scope.",
                ],
            ),
            StandardPerspective(
                standard_id="ISO/PAS 8800",
                standard_name="Safety and AI",
                covers=[
                    "AI safety requirements specification (Cl.5-6)",
                    "AI design and architecture (Cl.7)",
                    "Data quality requirements (Cl.8.4)",
                    "AI V&V with uncertainty quantification (Cl.9)",
                    "Base GSN pattern (Annex B, 6 goals)",
                    "Partial re-approval for AI changes (Cl.14.8.3)",
                ],
                excludes=[
                    "Cybersecurity (deferred to ISO/SAE 21434)",
                    "SOTIF triggering conditions (deferred to ISO 21448)",
                    "Concrete ASIL decomposition for AI",
                    "Combined release criteria",
                ],
                visible_gaps=[
                    "Gap-2 (incomplete OTA re-assurance)",
                    "Gap-5 (data acceptance threshold undefined)",
                ],
                invisible_gaps=[
                    "Gap-3 (adversarial-SOTIF boundary — defers both to other standards)",
                    "Gap-4 (cross-domain release — base pattern has no combined node)",
                ],
                blind_spots=[
                    "An assessor following only ISO/PAS 8800 would build a 6-goal "
                    "GSN argument covering AI-specific concerns. They would defer "
                    "cybersecurity and SOTIF to their respective standards but "
                    "would not verify that those standards actually cover the AI "
                    "component. The 3 new goals (G7, G8, G9) would never be added.",
                ],
            ),
        ]

    def get_perspective(self, standard_id: str) -> StandardPerspective | None:
        for p in self.perspectives:
            if p.standard_id == standard_id:
                return p
        return None

    def get_gap_visibility_matrix(self) -> dict[str, dict[str, bool]]:
        """Return which gaps are visible from each standard's perspective."""
        all_gaps = ["Gap-1", "Gap-2", "Gap-3", "Gap-4", "Gap-5"]
        matrix = {}
        for p in self.perspectives:
            visible_ids = set()
            for g in p.visible_gaps:
                for gap_id in all_gaps:
                    if gap_id in g:
                        visible_ids.add(gap_id)
            matrix[p.standard_id] = {g: g in visible_ids for g in all_gaps}
        # Integration sees all
        matrix["Integrated"] = {g: True for g in all_gaps}
        return matrix

    def print_analysis(self):
        """Print the full counterfactual analysis."""
        print("=" * 80)
        print("COUNTERFACTUAL ANALYSIS: What Each Standard Misses Alone")
        print("=" * 80)

        for p in self.perspectives:
            print(f"\n{'─' * 80}")
            print(f"If an assessor follows ONLY {p.standard_id} ({p.standard_name}):")
            print(f"{'─' * 80}")
            print(f"\n  COVERS:")
            for c in p.covers:
                print(f"    + {c}")
            print(f"\n  EXCLUDES / DOES NOT ADDRESS:")
            for e in p.excludes:
                print(f"    - {e}")
            print(f"\n  GAPS VISIBLE from this perspective:")
            for g in p.visible_gaps:
                print(f"    ! {g}")
            if not p.visible_gaps:
                print(f"    (none)")
            print(f"\n  GAPS INVISIBLE (only visible through integration):")
            for g in p.invisible_gaps:
                print(f"    ? {g}")
            print(f"\n  BLIND SPOT:")
            for b in p.blind_spots:
                print(f"    >> {b}")

        print(f"\n{'=' * 80}")
        print("CONCLUSION: Gap-3 and Gap-4 are invisible from ANY single standard.")
        print("They emerge only when the four standards are integrated into one GSN.")
        print("=" * 80)

"""Traceability matrix: cross-reference from GSN goals to claims, inconsistencies, and gaps.

Produces a consolidated view showing, for every goal node in the integrated GSN:
  - Which standards contribute claims
  - Which inconsistencies manifest at that node
  - Which assurance gaps affect that node
  - The net assurance status (covered / partially covered / gap)

This supports ISO 26262 Part 8 traceability requirements and provides
a single-page overview of the argument's structural completeness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.standards.registry import StandardsRegistry
from src.gsn.integrated_pattern import build_integrated_gsn
from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification


@dataclass
class GoalTraceEntry:
    """Traceability entry for a single GSN goal node."""

    goal_id: str
    goal_text: str
    contributing_standards: list[str]
    num_claims: int
    inconsistencies: list[str]
    gaps: list[str]
    integration_induced_gaps: list[str]
    status: str  # "covered", "partial", "gap"


class TraceabilityMatrix:
    """Cross-reference matrix linking GSN goals to claims, inconsistencies, and gaps.

    This provides the auditor-facing view: for each goal, what evidence
    exists, what conflicts remain, and where assurance is incomplete.
    """

    def __init__(self):
        self.registry = StandardsRegistry()
        self.gsn = build_integrated_gsn()
        self.catalogue = DecisionPointCatalogue()
        self.gap_classification = GapClassification()
        self.entries = self._build_entries()

    def _build_entries(self) -> list[GoalTraceEntry]:
        # Build lookup: goal -> inconsistency IDs
        goal_inconsistencies: dict[str, list[str]] = {}
        for inc in self.catalogue.inconsistencies:
            for node in inc.gsn_nodes:
                goal_inconsistencies.setdefault(node, []).append(
                    inc.inconsistency_id
                )

        # Build lookup: goal -> gap IDs (approximate by matching description keywords)
        goal_gaps: dict[str, list[str]] = {}
        goal_int_gaps: dict[str, list[str]] = {}
        gap_goal_mapping = {
            "Gap-1": ["G1"],   # Quantitative acceptance criteria undefined
            "Gap-2": ["G9"],   # No complete OTA re-assurance workflow
            "Gap-3": ["G7", "G8"],  # Adversarial-SOTIF boundary
            "Gap-4": ["G5"],   # No cross-domain release decision criteria
            "Gap-5": ["G3"],   # Data acceptance threshold undefined
        }
        for g in self.gap_classification.gaps:
            nodes = gap_goal_mapping.get(g.gap_id, [])
            for node in nodes:
                goal_gaps.setdefault(node, []).append(g.gap_id)
                if g.integration_induced:
                    goal_int_gaps.setdefault(node, []).append(g.gap_id)

        # Build entries for each goal
        entries = []
        density = self.registry.compute_goal_density()

        for goal in self.gsn.get_goals():
            gid = goal.element_id
            contributing = []
            num_claims = 0

            if gid in density:
                for std_id, active in density[gid].items():
                    if active:
                        contributing.append(std_id)
                # Count claims for this goal
                for std in self.registry.all_standards:
                    for claim in std.claims:
                        if claim.gsn_goal == gid:
                            num_claims += 1

            incs = goal_inconsistencies.get(gid, [])
            gps = goal_gaps.get(gid, [])
            int_gps = goal_int_gaps.get(gid, [])

            # Determine status
            if gps:
                status = "gap"
            elif incs:
                status = "partial"
            elif contributing:
                status = "covered"
            else:
                status = "gap"

            entries.append(GoalTraceEntry(
                goal_id=gid,
                goal_text=goal.text,
                contributing_standards=contributing,
                num_claims=num_claims,
                inconsistencies=incs,
                gaps=gps,
                integration_induced_gaps=int_gps,
                status=status,
            ))

        entries.sort(key=lambda e: e.goal_id)
        return entries

    def get_summary(self) -> dict:
        """Return summary counts."""
        covered = sum(1 for e in self.entries if e.status == "covered")
        partial = sum(1 for e in self.entries if e.status == "partial")
        gap = sum(1 for e in self.entries if e.status == "gap")
        return {
            "total_goals": len(self.entries),
            "covered": covered,
            "partial": partial,
            "gap": gap,
        }

    def to_csv_rows(self) -> list[dict]:
        """Return rows suitable for CSV export."""
        return [
            {
                "Goal": e.goal_id,
                "Text": e.goal_text[:60],
                "Standards": "; ".join(e.contributing_standards),
                "Claims": e.num_claims,
                "Inconsistencies": "; ".join(e.inconsistencies) if e.inconsistencies else "---",
                "Gaps": "; ".join(e.gaps) if e.gaps else "---",
                "Integration-Induced": "; ".join(e.integration_induced_gaps) if e.integration_induced_gaps else "---",
                "Status": e.status,
            }
            for e in self.entries
        ]

    def print_matrix(self):
        """Print the traceability matrix to stdout."""
        print("=" * 100)
        print("TRACEABILITY MATRIX: GSN Goals → Claims, Inconsistencies, Gaps")
        print("=" * 100)

        summary = self.get_summary()
        print(f"\nOverall: {summary['covered']} covered, "
              f"{summary['partial']} partial, {summary['gap']} gap "
              f"(of {summary['total_goals']} goals)")
        print()

        for e in self.entries:
            status_marker = {"covered": "+", "partial": "~", "gap": "!"}[e.status]
            print(f"  [{status_marker}] {e.goal_id}: {e.goal_text[:65]}")
            print(f"      Standards: {', '.join(e.contributing_standards) or 'NONE'} "
                  f"({e.num_claims} claims)")
            if e.inconsistencies:
                print(f"      Inconsistencies: {', '.join(e.inconsistencies)}")
            if e.gaps:
                gap_str = ", ".join(e.gaps)
                if e.integration_induced_gaps:
                    gap_str += f" (integration-induced: {', '.join(e.integration_induced_gaps)})"
                print(f"      Gaps: {gap_str}")
            print()

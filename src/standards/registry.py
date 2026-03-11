"""Standards registry — central access point for all applicable standards.

Implements Step 2 (lifecycle-phase mapping) by aggregating claims from
all standards and providing cross-standard queries.
"""

from __future__ import annotations

from collections import defaultdict

from src.standards.base import (
    Standard,
    Claim,
    LifecyclePhase,
)
from src.standards.iso26262 import ISO26262
from src.standards.iso21448 import ISO21448
from src.standards.iso21434 import ISOSAE21434
from src.standards.iso8800 import ISOPAS8800
from src.standards.tr5469 import TR5469


class StandardsRegistry:
    """Central registry of all applicable standards.

    Provides methods for cross-standard queries used in the integration
    and analysis steps of the methodology.
    """

    def __init__(self):
        self.standards: dict[str, Standard] = {}
        self._register_all()

    def _register_all(self):
        """Register all applicable standards."""
        for std in [ISO26262(), ISO21448(), ISOSAE21434(), ISOPAS8800(), TR5469()]:
            self.standards[std.standard_id] = std

    def get_standard(self, standard_id: str) -> Standard:
        return self.standards[standard_id]

    @property
    def all_standards(self) -> list[Standard]:
        return list(self.standards.values())

    @property
    def normative_standards(self) -> list[Standard]:
        """Return only normative standards (excluding TR 5469)."""
        return [s for s in self.standards.values() if s.standard_id != "TR5469"]

    def get_all_claims(self) -> list[Claim]:
        """Return all claims across all standards."""
        claims = []
        for std in self.standards.values():
            claims.extend(std.claims)
        return claims

    def get_claims_for_goal(self, goal_id: str) -> dict[str, list[Claim]]:
        """Return claims for a GSN goal, grouped by standard.

        This is the primary method used in Step 3 (GSN construction)
        to identify which standards contribute to each goal node.
        """
        result: dict[str, list[Claim]] = {}
        for std_id, std in self.standards.items():
            claims = std.get_claims_for_goal(goal_id)
            if claims:
                result[std_id] = claims
        return result

    def get_claims_for_phase(
        self, phase: LifecyclePhase
    ) -> dict[str, list[Claim]]:
        """Return claims for a lifecycle phase, grouped by standard."""
        result: dict[str, list[Claim]] = {}
        for std_id, std in self.standards.items():
            claims = std.get_claims_for_phase(phase)
            if claims:
                result[std_id] = claims
        return result

    def compute_coverage_matrix(self) -> dict[str, dict[str, int]]:
        """Compute the clause coverage matrix (Table 2 in the paper).

        Returns a dict mapping standard_id -> {phase_name: clause_count}.
        """
        matrix: dict[str, dict[str, int]] = {}
        for std_id, std in self.standards.items():
            phase_counts: dict[str, int] = {}
            for phase in LifecyclePhase:
                count = len(std.get_clauses_for_phase(phase))
                phase_counts[phase.display_name] = count
            matrix[std_id] = phase_counts
        return matrix

    def compute_goal_density(self) -> dict[str, dict[str, bool]]:
        """Compute the standard coverage density per goal (Table 4).

        Returns a dict mapping goal_id -> {standard_id: contributes}.
        """
        goal_ids = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "S1"]
        density: dict[str, dict[str, bool]] = {}
        for gid in goal_ids:
            claims_by_std = self.get_claims_for_goal(gid)
            density[gid] = {
                std_id: std_id in claims_by_std
                for std_id in self.standards
            }
        return density

    def count_standards_per_goal(self) -> dict[str, int]:
        """Count how many standards contribute claims to each goal."""
        density = self.compute_goal_density()
        return {
            gid: sum(1 for v in stds.values() if v)
            for gid, stds in density.items()
        }

    def get_evidence_types_for_goal(self, goal_id: str) -> dict[str, list[str]]:
        """Return evidence types required at a goal, grouped by standard.

        This is used in the evidence convergence analysis (I-2).
        """
        result: dict[str, list[str]] = defaultdict(list)
        claims_by_std = self.get_claims_for_goal(goal_id)
        for std_id, claims in claims_by_std.items():
            for claim in claims:
                result[std_id].extend(claim.evidence_types)
        return dict(result)

    def print_coverage_summary(self):
        """Print a human-readable coverage summary."""
        print("=" * 70)
        print("STANDARDS COVERAGE MATRIX (Step 2 Output)")
        print("=" * 70)

        matrix = self.compute_coverage_matrix()
        phases = [p.display_name for p in LifecyclePhase]

        # Header
        header = f"{'Standard':<15}" + "".join(f"{p:<22}" for p in phases)
        print(header)
        print("-" * len(header))

        for std_id, phase_counts in matrix.items():
            row = f"{std_id:<15}"
            for phase in phases:
                count = phase_counts.get(phase, 0)
                row += f"{count if count > 0 else '---':<22}"
            print(row)

        print()
        print("=" * 70)
        print("GOAL COVERAGE DENSITY (Table 4)")
        print("=" * 70)

        density = self.compute_goal_density()
        std_ids = list(self.standards.keys())
        header = f"{'Goal':<8}" + "".join(f"{s:<15}" for s in std_ids) + "Active"
        print(header)
        print("-" * len(header))

        for gid, stds in density.items():
            row = f"{gid:<8}"
            for std_id in std_ids:
                mark = "Y" if stds.get(std_id, False) else "---"
                row += f"{mark:<15}"
            active = sum(1 for v in stds.values() if v)
            row += str(active)
            print(row)

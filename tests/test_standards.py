"""Tests for the standards traceability framework."""

import pytest

from src.standards.base import LifecyclePhase, ClaimType, InconsistencyType, GapType
from src.standards.iso26262 import ISO26262
from src.standards.iso21448 import ISO21448
from src.standards.iso21434 import ISOSAE21434
from src.standards.iso8800 import ISOPAS8800
from src.standards.tr5469 import TR5469
from src.standards.registry import StandardsRegistry


class TestStandardInstantiation:
    """Test that each standard can be instantiated with claims and clauses."""

    def test_iso26262(self):
        std = ISO26262()
        assert std.standard_id == "ISO26262"
        assert len(std.clauses) > 0
        assert len(std.claims) > 0
        assert std.year == 2018

    def test_iso21448(self):
        std = ISO21448()
        assert std.standard_id == "ISO21448"
        assert len(std.clauses) > 0
        assert len(std.claims) > 0

    def test_iso21434(self):
        std = ISOSAE21434()
        assert std.standard_id == "ISO21434"
        assert len(std.clauses) > 0
        assert len(std.claims) > 0

    def test_iso8800(self):
        std = ISOPAS8800()
        assert std.standard_id == "ISOPAS8800"
        assert len(std.clauses) > 0
        assert len(std.claims) > 0

    def test_tr5469(self):
        std = TR5469()
        assert std.standard_id == "TR5469"
        assert len(std.clauses) > 0
        # TR 5469 is informative, so fewer claims
        assert all(c.claim_type == ClaimType.INFORMATIVE_GUIDANCE for c in std.claims)


class TestStandardsRegistry:
    """Test the standards registry and cross-standard queries."""

    @pytest.fixture
    def registry(self):
        return StandardsRegistry()

    def test_all_standards_registered(self, registry):
        assert len(registry.standards) == 5
        assert "ISO26262" in registry.standards
        assert "ISO21448" in registry.standards
        assert "ISO21434" in registry.standards
        assert "ISOPAS8800" in registry.standards
        assert "TR5469" in registry.standards

    def test_normative_standards(self, registry):
        normative = registry.normative_standards
        assert len(normative) == 4
        assert all(s.standard_id != "TR5469" for s in normative)

    def test_claims_for_g5(self, registry):
        """G5 should have claims from all four normative standards."""
        claims = registry.get_claims_for_goal("G5")
        # ISO 26262, ISO 21448, ISO/PAS 8800 should all contribute
        assert "ISO26262" in claims
        assert "ISO21448" in claims
        assert "ISOPAS8800" in claims
        assert "ISO21434" in claims

    def test_claims_for_g3(self, registry):
        """G3 should have claims from only ISO/PAS 8800 (normative)."""
        claims = registry.get_claims_for_goal("G3")
        assert "ISOPAS8800" in claims
        # TR 5469 is informative and may also contribute
        normative_contributors = [
            k for k in claims.keys() if k != "TR5469"
        ]
        assert len(normative_contributors) == 1

    def test_goal_density_g5_is_most_dense(self, registry):
        """G5 should have the most standards active."""
        counts = registry.count_standards_per_goal()
        assert counts["G5"] == max(
            v for k, v in counts.items() if k.startswith("G")
        )

    def test_coverage_matrix(self, registry):
        matrix = registry.compute_coverage_matrix()
        assert len(matrix) == 5
        for std_id, phases in matrix.items():
            assert len(phases) == 6  # six lifecycle phases

    def test_evidence_types_for_g5(self, registry):
        """G5 should have evidence types from multiple standards."""
        evidence = registry.get_evidence_types_for_goal("G5")
        assert len(evidence) >= 3


class TestLifecyclePhases:
    """Test lifecycle phase coverage."""

    @pytest.fixture
    def registry(self):
        return StandardsRegistry()

    def test_all_phases_have_coverage(self, registry):
        """At least one standard should cover each lifecycle phase."""
        for phase in LifecyclePhase:
            claims = registry.get_claims_for_phase(phase)
            assert len(claims) > 0, f"No claims for phase {phase.display_name}"

    def test_verification_has_most_standards(self, registry):
        """Verification phase should have the most standard coverage."""
        verification_claims = registry.get_claims_for_phase(
            LifecyclePhase.VERIFICATION
        )
        assert len(verification_claims) >= 3

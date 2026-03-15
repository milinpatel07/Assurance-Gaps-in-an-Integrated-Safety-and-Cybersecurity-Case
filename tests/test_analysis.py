"""Tests for the inconsistency and gap analysis (Steps 4-5)."""

import pytest

from src.standards.base import InconsistencyType, GapType, LifecyclePhase
from src.analysis.inconsistencies import InconsistencyCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis


class TestInconsistencyCatalogue:
    """Test the requirement inconsistencies (Step 4)."""

    @pytest.fixture
    def catalogue(self):
        return InconsistencyCatalogue()

    def test_seven_inconsistencies(self, catalogue):
        assert len(catalogue.inconsistencies) == 7

    def test_three_structural(self, catalogue):
        structural = catalogue.get_structural()
        assert len(structural) == 3
        ids = {i.inconsistency_id for i in structural}
        assert ids == {"I-1", "I-2", "I-5"}

    def test_two_terminological(self, catalogue):
        term = catalogue.get_by_type(InconsistencyType.TERMINOLOGICAL)
        assert len(term) == 2

    def test_two_methodological(self, catalogue):
        meth = catalogue.get_by_type(InconsistencyType.METHODOLOGICAL)
        assert len(meth) == 2

    def test_i2_is_central_finding(self, catalogue):
        """I-2 (evidence type asymmetry) should involve all four standards."""
        i2 = catalogue.get_by_id("I-2")
        assert i2 is not None
        assert len(i2.standards_involved) == 4
        assert "G5" in i2.gsn_nodes

    def test_i5_boundary_ambiguity(self, catalogue):
        """I-5 should affect both G7 and G8."""
        i5 = catalogue.get_by_id("I-5")
        assert "G7" in i5.gsn_nodes
        assert "G8" in i5.gsn_nodes

    def test_all_have_clause_references(self, catalogue):
        for inc in catalogue.inconsistencies:
            assert len(inc.clause_references) >= 2


class TestGapClassification:
    """Test the assurance gaps (Step 5)."""

    @pytest.fixture
    def gaps(self):
        return GapClassification()

    def test_six_gaps(self, gaps):
        assert len(gaps.gaps) == 6

    def test_two_integration_induced(self, gaps):
        integration = gaps.get_integration_induced()
        assert len(integration) == 2
        ids = {g.gap_id for g in integration}
        assert ids == {"Gap-3", "Gap-4"}

    def test_gap_types(self, gaps):
        stats = gaps.summary_statistics()
        assert stats["missing_claim"] == 2
        assert stats["missing_evidence"] == 3
        assert stats["unresolved_inconsistency"] == 1

    def test_gap2_modification_phase(self, gaps):
        gap2 = gaps.get_by_id("Gap-2")
        assert gap2 is not None
        assert gap2.lifecycle_phase == LifecyclePhase.MODIFICATION
        assert gap2.gap_type == GapType.MISSING_CLAIM

    def test_all_gaps_have_partial_coverage(self, gaps):
        for gap in gaps.gaps:
            assert len(gap.partial_coverage) >= 2


class TestEvidenceConvergence:
    """Test the evidence convergence analysis."""

    @pytest.fixture
    def analysis(self):
        return EvidenceConvergenceAnalysis()

    def test_four_evidence_types(self, analysis):
        assert len(analysis.evidence_types) == 4

    def test_failure_event_has_three_paths(self, analysis):
        assert len(analysis.failure_event.analysis_paths) == 3

    def test_all_paths_lead_to_g5(self, analysis):
        for path in analysis.failure_event.analysis_paths:
            assert path.gsn_node == "G5"

    def test_evidence_scales_differ(self, analysis):
        scales = {et.scale for et in analysis.evidence_types}
        assert len(scales) == 4  # All four should be different

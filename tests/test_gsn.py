"""Tests for the GSN model and integrated pattern construction."""

import pytest

from src.gsn.model import GSNArgument, Goal, Strategy, Context, GoalStatus
from src.gsn.integrated_pattern import build_integrated_gsn


class TestIntegratedGSN:
    """Test the integrated GSN pattern (Step 3 output)."""

    @pytest.fixture
    def gsn(self):
        return build_integrated_gsn()

    def test_has_nine_goals(self, gsn):
        """The integrated pattern should have 9 goals (G1-G9)."""
        goals = gsn.get_goals()
        assert len(goals) == 9

    def test_goal_ids(self, gsn):
        """Goals should be G1 through G9."""
        goal_ids = {g.element_id for g in gsn.get_goals()}
        expected = {f"G{i}" for i in range(1, 10)}
        assert goal_ids == expected

    def test_g1_is_top_level(self, gsn):
        """G1 should have no parent goals."""
        g1 = gsn.get_element("G1")
        assert g1 is not None
        assert isinstance(g1, Goal)
        assert "S1" in g1.supported_by

    def test_g1_has_contexts(self, gsn):
        """G1 should have C1 (ASIL) and C2 (TARA) as context."""
        g1 = gsn.get_element("G1")
        assert "C1" in g1.in_context_of
        assert "C2" in g1.in_context_of

    def test_s1_supports_all_subgoals(self, gsn):
        """S1 should support G2-G9."""
        s1 = gsn.get_element("S1")
        assert isinstance(s1, Strategy)
        for i in range(2, 10):
            assert f"G{i}" in s1.supported_by

    def test_g9_is_undeveloped(self, gsn):
        """G9 (modification) should be marked as undeveloped."""
        g9 = gsn.get_element("G9")
        assert isinstance(g9, Goal)
        assert g9.status == GoalStatus.UNDEVELOPED
        assert g9.origin == "undeveloped"

    def test_g5_has_four_standards(self, gsn):
        """G5 should have sources from all four normative standards."""
        g5 = gsn.get_element("G5")
        assert len(g5.source_standards) == 4

    def test_g3_is_single_standard(self, gsn):
        """G3 should have only ISO/PAS 8800 as source."""
        g3 = gsn.get_element("G3")
        assert g3.source_standards == ["ISOPAS8800"]

    def test_retained_goals(self, gsn):
        """G2-G6 should be retained from Annex B."""
        for i in range(2, 7):
            goal = gsn.get_element(f"G{i}")
            assert goal.origin == "retained"

    def test_new_goals(self, gsn):
        """G7 and G8 should be new goals."""
        g7 = gsn.get_element("G7")
        g8 = gsn.get_element("G8")
        assert g7.origin == "new"
        assert g8.origin == "new"

    def test_junction_points(self, gsn):
        """There should be multiple junction points (2+ standards)."""
        junctions = gsn.get_junction_points()
        assert len(junctions) >= 4  # G1, G2, G4, G5, G6, G8

    def test_has_solutions(self, gsn):
        """The GSN should have solution (evidence) nodes."""
        solutions = gsn.get_solutions()
        assert len(solutions) > 0

    def test_g5_has_four_solutions(self, gsn):
        """G5 should have four solution nodes (four evidence types)."""
        g5 = gsn.get_element("G5")
        assert len(g5.supported_by) == 4

    def test_statistics(self, gsn):
        """Statistics should be computed correctly."""
        stats = gsn.compute_statistics()
        assert stats["goals"] == 9
        assert stats["undeveloped_goals"] == 1
        assert stats["retained_goals"] == 6  # G1-G6
        assert stats["new_goals"] == 2  # G7, G8

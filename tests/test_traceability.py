"""Tests for the traceability matrix and sensitivity analysis modules."""

import pytest

from src.analysis.traceability import TraceabilityMatrix
from src.analysis.sensitivity import run_sensitivity_analysis


class TestTraceabilityMatrix:
    """Tests for the GSN goal traceability matrix."""

    @pytest.fixture(scope="class")
    def matrix(self):
        return TraceabilityMatrix()

    def test_has_nine_entries(self, matrix):
        assert len(matrix.entries) == 9

    def test_all_goals_present(self, matrix):
        goal_ids = {e.goal_id for e in matrix.entries}
        expected = {f"G{i}" for i in range(1, 10)}
        assert goal_ids == expected

    def test_g5_has_four_standards(self, matrix):
        g5 = next(e for e in matrix.entries if e.goal_id == "G5")
        assert len(g5.contributing_standards) == 4

    def test_g5_has_inconsistencies(self, matrix):
        g5 = next(e for e in matrix.entries if e.goal_id == "G5")
        assert len(g5.inconsistencies) >= 1

    def test_g5_has_gap4(self, matrix):
        g5 = next(e for e in matrix.entries if e.goal_id == "G5")
        assert "Gap-4" in g5.gaps

    def test_summary_counts(self, matrix):
        s = matrix.get_summary()
        assert s["total_goals"] == 9
        assert s["covered"] + s["partial"] + s["gap"] == 9

    def test_csv_rows(self, matrix):
        rows = matrix.to_csv_rows()
        assert len(rows) == 9
        assert all("Goal" in r for r in rows)
        assert all("Status" in r for r in rows)

    def test_no_goal_without_status(self, matrix):
        for e in matrix.entries:
            assert e.status in ("covered", "partial", "gap")


class TestSensitivityAnalysis:
    """Tests for the multi-seed sensitivity analysis."""

    def test_runs_with_two_seeds(self):
        result = run_sensitivity_analysis(seeds=[42, 123], scenes_per_weather=10)
        assert len(result.seeds) == 2
        assert len(result.overall_recall) == 2

    def test_recall_gap_positive(self):
        result = run_sensitivity_analysis(seeds=[42], scenes_per_weather=10)
        assert result.recall_gap[0] > 0, "Non-triggering should outperform triggering"

    def test_summary_has_all_keys(self):
        result = run_sensitivity_analysis(seeds=[42], scenes_per_weather=10)
        s = result.summary()
        required = [
            "num_seeds", "overall_recall_mean", "triggering_recall_mean",
            "non_triggering_recall_mean", "recall_gap_mean",
        ]
        for key in required:
            assert key in s, f"Missing key: {key}"

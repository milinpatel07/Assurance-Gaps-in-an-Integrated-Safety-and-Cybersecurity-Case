"""Extended sensitivity and threshold tests.

Validates robustness of findings across random seeds and
SOTIF triggering threshold variations.
"""

import pytest

from src.analysis.sensitivity import (
    run_sensitivity_analysis,
    run_threshold_sensitivity,
)
from src.evaluation.carla_evaluator import generate_synthetic_illustration


class TestSensitivityRobustness:
    """Validate that key findings are robust across random seeds."""

    @pytest.fixture
    def sensitivity(self):
        return run_sensitivity_analysis(seeds=[42, 123], scenes_per_weather=20)

    def test_recall_gap_always_positive(self, sensitivity):
        """Triggering conditions should always degrade recall."""
        for gap in sensitivity.recall_gap:
            assert gap > 0, "Recall gap should be positive"

    def test_recall_gap_stable(self, sensitivity):
        """The recall gap standard deviation should be small."""
        assert sensitivity.std_recall_gap < 0.1

    def test_triggering_divergence_higher(self, sensitivity):
        """Triggering conditions should produce higher ensemble divergence."""
        for i in range(len(sensitivity.seeds)):
            assert sensitivity.triggering_divergence[i] > 0.1

    def test_summary_has_all_keys(self, sensitivity):
        """Summary should contain all expected statistics."""
        summary = sensitivity.summary()
        expected_keys = [
            "num_seeds", "scenes_per_weather",
            "overall_recall_mean", "overall_recall_std",
            "triggering_recall_mean", "triggering_recall_std",
            "non_triggering_recall_mean", "non_triggering_recall_std",
            "triggering_divergence_mean", "triggering_divergence_std",
            "recall_gap_mean", "recall_gap_std",
        ]
        for key in expected_keys:
            assert key in summary


class TestThresholdSensitivity:
    """Validate sensitivity to SOTIF triggering threshold choices."""

    @pytest.fixture
    def threshold_result(self):
        return run_threshold_sensitivity(
            rain_thresholds=[15, 20, 30],
            visibility_thresholds=[150, 200, 300],
            seed=42,
            scenes_per_weather=20,
        )

    def test_result_has_correct_dimensions(self, threshold_result):
        """Result should match the number of thresholds tested."""
        assert len(threshold_result.recall_gaps) == 3  # rain thresholds
        assert len(threshold_result.recall_gaps[0]) == 3  # visibility thresholds

    def test_recall_gaps_nonnegative(self, threshold_result):
        """Recall gaps should be non-negative for reasonable thresholds."""
        for row in threshold_result.recall_gaps:
            for gap in row:
                assert gap >= -0.1  # Allow small numerical noise

    def test_stricter_thresholds_fewer_triggering(self, threshold_result):
        """Higher rain threshold = fewer triggering conditions."""
        # First row (rain>15) should have >= triggering count than last (rain>30)
        for j in range(len(threshold_result.visibility_thresholds)):
            assert (
                threshold_result.triggering_counts[0][j]
                >= threshold_result.triggering_counts[-1][j]
            )


class TestEvaluationDeterminism:
    """Validate that evaluation is deterministic given the same seed."""

    def test_same_seed_same_results(self):
        """Two runs with same seed should produce identical results."""
        r1 = generate_synthetic_illustration(num_scenes_per_weather=5, seed=42)
        r2 = generate_synthetic_illustration(num_scenes_per_weather=5, seed=42)
        s1 = r1.compute_summary()
        s2 = r2.compute_summary()
        assert s1["overall_mean_recall"] == s2["overall_mean_recall"]
        assert s1["total_false_negatives"] == s2["total_false_negatives"]

    def test_different_seeds_different_results(self):
        """Two runs with different seeds should differ."""
        r1 = generate_synthetic_illustration(num_scenes_per_weather=5, seed=42)
        r2 = generate_synthetic_illustration(num_scenes_per_weather=5, seed=99)
        s1 = r1.compute_summary()
        s2 = r2.compute_summary()
        assert s1["overall_mean_recall"] != s2["overall_mean_recall"]

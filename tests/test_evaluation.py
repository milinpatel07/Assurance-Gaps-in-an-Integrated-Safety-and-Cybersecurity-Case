"""Tests for the weather grid and the synthetic weather-grid illustration (no CARLA)."""

import pytest

from src.evaluation.weather_conditions import (
    WeatherCondition,
    generate_weather_grid,
    get_triggering_conditions,
    compute_triggering_coverage,
    RAIN_LEVELS,
    VISIBILITY_LEVELS,
)
from src.evaluation.carla_evaluator import (
    generate_synthetic_illustration,
    SceneEvaluation,
)


class TestWeatherConditions:
    """Test weather condition generation."""

    def test_default_grid_size(self):
        """Default grid: 5 rain x 5 fog = 25 conditions."""
        conditions = generate_weather_grid()
        assert len(conditions) == 25

    def test_triggering_conditions_exist(self):
        conditions = generate_weather_grid()
        triggering = get_triggering_conditions(conditions)
        assert len(triggering) > 0
        assert len(triggering) < len(conditions)

    def test_from_parameters_clear(self):
        cond = WeatherCondition.from_parameters(0, 500)
        assert not cond.sotif_triggering
        assert cond.carla_fog_density == 0.0

    def test_from_parameters_heavy_rain(self):
        cond = WeatherCondition.from_parameters(100, 500)
        assert cond.sotif_triggering
        assert cond.carla_precipitation == 100.0

    def test_from_parameters_dense_fog(self):
        cond = WeatherCondition.from_parameters(0, 10)
        assert cond.sotif_triggering
        assert cond.carla_fog_density > 0

    def test_condition_names_are_unique_and_use_documented_levels(self):
        """Names follow the level names in weather_grid.yaml, one per condition."""
        names = [c.name for c in generate_weather_grid()]
        assert len(set(names)) == len(names)
        assert WeatherCondition.from_parameters(50, 500).name == "heavy_rain_clear"
        assert WeatherCondition.from_parameters(100, 500).name == "extreme_rain_clear"
        assert WeatherCondition.from_parameters(0, 50).name == "no_rain_dense_fog"
        assert WeatherCondition.from_parameters(0, 10).name == "no_rain_very_dense_fog"

    def test_triggering_coverage_statistics(self):
        conditions = generate_weather_grid()
        coverage = compute_triggering_coverage(conditions)
        assert coverage["total_conditions"] == 25
        assert coverage["triggering_conditions"] > 0
        assert coverage["triggering_fraction"] > 0
        assert coverage["triggering_fraction"] < 1


class TestSyntheticEvaluation:
    """Test the synthetic weather-grid illustration (no detector, no CARLA)."""

    def test_generates_results(self):
        result = generate_synthetic_illustration(num_scenes_per_weather=5, seed=42)
        assert len(result.weather_results) == 25  # 5x5 grid

    def test_summary_statistics(self):
        result = generate_synthetic_illustration(num_scenes_per_weather=5, seed=42)
        summary = result.compute_summary()
        assert summary["total_weather_conditions"] == 25
        assert 0 < summary["overall_mean_recall"] < 1
        assert summary["triggering_mean_recall"] < summary["non_triggering_mean_recall"]

    def test_triggering_worse_than_non_triggering(self):
        """Severe weather should degrade performance (by design)."""
        result = generate_synthetic_illustration(num_scenes_per_weather=20, seed=42)
        summary = result.compute_summary()
        # Triggering conditions should have lower recall
        assert summary["triggering_mean_recall"] < summary["non_triggering_mean_recall"]
        # Triggering conditions should have higher divergence
        assert summary["triggering_mean_divergence"] > summary.get(
            "non_triggering_mean_divergence", 0
        )

    def test_scene_metrics(self):
        result = generate_synthetic_illustration(num_scenes_per_weather=3, seed=42)
        for wr in result.weather_results:
            for scene in wr.scene_results:
                assert 0 <= scene.precision <= 1
                assert 0 <= scene.recall <= 1
                assert scene.num_gt_objects > 0

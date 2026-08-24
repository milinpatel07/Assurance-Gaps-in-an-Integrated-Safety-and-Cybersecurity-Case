"""Check that the descriptive YAML files still match the values the code uses.

The YAML files under ``configs/`` and ``data/carla_configs/`` document parameters
for readers. No module loads them, so nothing else stops them drifting away from
the constants in ``src/``. These tests are that stop.

A failure here means a documented value and a used value disagree. Fix the file
that is wrong. Do not edit a constant in ``src/`` to make a test pass.
"""

from __future__ import annotations

import os

import pytest

yaml = pytest.importorskip("yaml")

from src.evaluation.weather_conditions import (  # noqa: E402
    RAIN_LEVELS,
    VISIBILITY_LEVELS,
    compute_triggering_coverage,
    generate_weather_grid,
)
from src.perception.voxelization import KITTI_VOXEL_CONFIG  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(*parts: str) -> dict:
    with open(os.path.join(REPO_ROOT, *parts), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@pytest.fixture(scope="module")
def weather_yaml() -> dict:
    return _load("data", "carla_configs", "weather_grid.yaml")["weather_grid"]


@pytest.fixture(scope="module")
def detector_yaml() -> dict:
    return _load("data", "carla_configs", "detector_config.yaml")


@pytest.fixture(scope="module")
def case_study_yaml() -> dict:
    return _load("configs", "case_study.yaml")


class TestWeatherGridDocumentation:
    """weather_grid.yaml against src/evaluation/weather_conditions.py."""

    def test_rain_levels_match(self, weather_yaml):
        assert weather_yaml["rain_intensity_levels_mm_h"] == RAIN_LEVELS

    def test_visibility_levels_match(self, weather_yaml):
        assert weather_yaml["fog_visibility_levels_m"] == VISIBILITY_LEVELS

    def test_condition_counts_match(self, weather_yaml):
        coverage = compute_triggering_coverage(generate_weather_grid())
        assert weather_yaml["total_conditions"] == coverage["total_conditions"]
        assert weather_yaml["triggering_conditions"] == coverage["triggering_conditions"]
        assert (
            weather_yaml["non_triggering_conditions"] == coverage["non_triggering_conditions"]
        )

    def test_documented_thresholds_reproduce_the_split(self, weather_yaml):
        """The documented thresholds must be the ones that classify the grid.

        Rather than compare against a constant, re-derive the triggering count
        from the documented thresholds and require the same answer.
        """
        rain_threshold = weather_yaml["triggering_thresholds"]["rain_mm_h"]
        visibility_threshold = weather_yaml["triggering_thresholds"]["visibility_m"]

        expected = sum(
            1
            for condition in generate_weather_grid()
            if condition.rain_intensity > rain_threshold
            or condition.fog_density < visibility_threshold
        )
        assert expected == weather_yaml["triggering_conditions"]

    def test_seed_and_scene_count_match_documented_defaults(self, weather_yaml):
        fixed = weather_yaml["fixed_parameters"]
        assert fixed["random_seed"] == 42
        assert fixed["scenes_per_condition"] == 50


class TestDetectorDocumentation:
    """detector_config.yaml against src/perception/voxelization.py."""

    def test_voxel_size_matches(self, detector_yaml):
        documented = detector_yaml["detector"]["voxelization"]["voxel_size"]
        assert [float(v) for v in documented] == [
            float(v) for v in KITTI_VOXEL_CONFIG.voxel_size
        ]

    def test_point_cloud_range_matches(self, detector_yaml):
        documented = detector_yaml["detector"]["voxelization"]["point_cloud_range"]
        assert [float(v) for v in documented] == [
            float(v) for v in KITTI_VOXEL_CONFIG.point_cloud_range
        ]

    def test_voxel_limits_match(self, detector_yaml):
        voxelization = detector_yaml["detector"]["voxelization"]
        assert voxelization["max_points_per_voxel"] == KITTI_VOXEL_CONFIG.max_points_per_voxel
        assert voxelization["max_voxels"] == KITTI_VOXEL_CONFIG.max_voxels

    def test_ensemble_size_agrees_with_case_study(self, detector_yaml, case_study_yaml):
        assert detector_yaml["ensemble"]["num_members"] == 5
        assert case_study_yaml["ensemble"]["num_members"] == 5


class TestCaseStudyDocumentation:
    """configs/case_study.yaml against the values the case study uses."""

    def test_detector_geometry_agrees_with_code(self, case_study_yaml):
        detector = case_study_yaml["detector"]
        assert [float(v) for v in detector["voxel_size"]] == [
            float(v) for v in KITTI_VOXEL_CONFIG.voxel_size
        ]
        assert detector["max_voxels"] == KITTI_VOXEL_CONFIG.max_voxels

    def test_class_names_are_the_three_kitti_classes(self, case_study_yaml):
        assert case_study_yaml["detector"]["class_names"] == ["Car", "Pedestrian", "Cyclist"]

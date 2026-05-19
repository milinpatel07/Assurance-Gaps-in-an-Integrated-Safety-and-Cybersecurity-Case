"""CARLA evaluation pipeline for the deep ensemble under weather conditions.

This module defines the evaluation protocol and result structures for the
deep ensemble under parametrically controlled weather conditions, together
with a synthetic illustration routine.

CARLA (Dosovitskiy et al., 2017) provides weather and sensor degradation
parameters that can be varied independently, allowing controlled coverage of
the triggering conditions that ISO 21448 Clauses 9-11 require.

The `generate_synthetic_illustration` function in this module produces
illustration output, not measurements: it does not connect to CARLA and does
not run a detector. It generates deterministic seeded values that demonstrate
the pipeline format. Real empirical evaluation results are in
`data/empirical_results/`. A live CARLA connection requires a running CARLA
instance and the carla Python package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from src.evaluation.weather_conditions import (
    WeatherCondition,
    generate_weather_grid,
    compute_triggering_coverage,
)
from src.perception.deep_ensemble import EnsemblePrediction


@dataclass
class SceneEvaluation:
    """Evaluation results for a single scene under one weather condition.

    Attributes:
        scene_id: Unique identifier for the scene.
        weather: The weather condition applied.
        num_gt_objects: Number of ground truth objects in the scene.
        num_detections: Number of ensemble detections.
        true_positives: Number of correctly detected objects.
        false_positives: Number of false detections.
        false_negatives: Number of missed objects (critical for safety).
        mean_divergence: Mean geometric divergence across detections.
        max_divergence: Maximum geometric divergence (most uncertain detection).
        uncertain_detections: Number of detections flagged as uncertain.
        predictions: Individual ensemble predictions with uncertainty.
    """

    scene_id: str
    weather: WeatherCondition
    num_gt_objects: int = 0
    num_detections: int = 0
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    mean_divergence: float = 0.0
    max_divergence: float = 0.0
    uncertain_detections: int = 0
    predictions: list[EnsemblePrediction] = field(default_factory=list)

    @property
    def precision(self) -> float:
        if self.num_detections == 0:
            return 0.0
        return self.true_positives / self.num_detections

    @property
    def recall(self) -> float:
        if self.num_gt_objects == 0:
            return 1.0
        return self.true_positives / self.num_gt_objects

    @property
    def f1_score(self) -> float:
        p, r = self.precision, self.recall
        if p + r == 0:
            return 0.0
        return 2 * p * r / (p + r)


@dataclass
class WeatherEvaluation:
    """Aggregated evaluation results for one weather condition across scenes.

    Attributes:
        weather: The weather condition.
        scene_results: Results for individual scenes.
        num_scenes: Number of scenes evaluated.
    """

    weather: WeatherCondition
    scene_results: list[SceneEvaluation] = field(default_factory=list)

    @property
    def num_scenes(self) -> int:
        return len(self.scene_results)

    @property
    def mean_recall(self) -> float:
        if not self.scene_results:
            return 0.0
        return np.mean([s.recall for s in self.scene_results]).item()

    @property
    def mean_precision(self) -> float:
        if not self.scene_results:
            return 0.0
        return np.mean([s.precision for s in self.scene_results]).item()

    @property
    def mean_divergence(self) -> float:
        if not self.scene_results:
            return 0.0
        return np.mean([s.mean_divergence for s in self.scene_results]).item()

    @property
    def total_false_negatives(self) -> int:
        return sum(s.false_negatives for s in self.scene_results)


@dataclass
class FullEvaluationResult:
    """Complete evaluation across all weather conditions.

    This is the primary output of the CARLA evaluation pipeline,
    providing the evidence required at G5 for ISO 21448 Cl.9-11.
    """

    weather_results: list[WeatherEvaluation] = field(default_factory=list)
    triggering_coverage: dict = field(default_factory=dict)

    def get_result_for_weather(
        self, weather_name: str
    ) -> Optional[WeatherEvaluation]:
        for wr in self.weather_results:
            if wr.weather.name == weather_name:
                return wr
        return None

    def get_triggering_results(self) -> list[WeatherEvaluation]:
        return [wr for wr in self.weather_results if wr.weather.sotif_triggering]

    def compute_summary(self) -> dict:
        """Compute summary statistics for the full evaluation."""
        all_results = self.weather_results
        trig_results = self.get_triggering_results()
        non_trig = [wr for wr in all_results if not wr.weather.sotif_triggering]

        return {
            "total_weather_conditions": len(all_results),
            "triggering_conditions": len(trig_results),
            "overall_mean_recall": (
                np.mean([wr.mean_recall for wr in all_results]).item()
                if all_results else 0.0
            ),
            "triggering_mean_recall": (
                np.mean([wr.mean_recall for wr in trig_results]).item()
                if trig_results else 0.0
            ),
            "non_triggering_mean_recall": (
                np.mean([wr.mean_recall for wr in non_trig]).item()
                if non_trig else 0.0
            ),
            "overall_mean_divergence": (
                np.mean([wr.mean_divergence for wr in all_results]).item()
                if all_results else 0.0
            ),
            "triggering_mean_divergence": (
                np.mean([wr.mean_divergence for wr in trig_results]).item()
                if trig_results else 0.0
            ),
            "non_triggering_mean_divergence": (
                np.mean([wr.mean_divergence for wr in non_trig]).item()
                if non_trig else 0.0
            ),
            "triggering_false_negatives": sum(
                wr.total_false_negatives for wr in trig_results
            ),
            "non_triggering_false_negatives": sum(
                wr.total_false_negatives for wr in non_trig
            ),
            "total_false_negatives": sum(
                wr.total_false_negatives for wr in all_results
            ),
        }


def generate_synthetic_illustration(
    num_scenes_per_weather: int = 10,
    seed: int = 42,
) -> FullEvaluationResult:
    """Generate a synthetic illustration of the evaluation output.

    This produces deterministic seeded values that demonstrate the evaluation
    pipeline structure and the relationship between weather severity,
    detection performance, and ensemble uncertainty. The output is an
    illustration of the pipeline format, not a measurement: no detector is
    run and CARLA is not contacted.

    Real empirical evaluation results are in `data/empirical_results/`.
    """
    rng = np.random.RandomState(seed)
    conditions = generate_weather_grid()

    weather_results = []
    for cond in conditions:
        scene_results = []
        for scene_idx in range(num_scenes_per_weather):
            # More severe weather -> worse performance + higher uncertainty
            severity = 0.0
            if cond.rain_intensity > 0:
                severity += cond.rain_intensity / 100.0
            if cond.fog_density < 500:
                severity += (500.0 - cond.fog_density) / 500.0
            severity = min(severity, 1.0)

            # Base performance degrades with severity
            base_recall = 0.95 - 0.4 * severity
            base_precision = 0.92 - 0.25 * severity
            base_divergence = 0.1 + 0.5 * severity

            num_gt = rng.randint(3, 15)
            recall = max(0.1, base_recall + rng.normal(0, 0.05))
            precision = max(0.1, base_precision + rng.normal(0, 0.05))

            tp = max(0, min(num_gt, int(num_gt * recall)))
            fp = max(0, int(tp / max(precision, 0.1) - tp))
            fn = num_gt - tp

            divergence = max(0.0, base_divergence + rng.normal(0, 0.1))
            max_div = min(1.0, divergence + rng.exponential(0.15))
            uncertain = int((divergence > 0.5) * max(1, int(tp * 0.3)))

            scene_eval = SceneEvaluation(
                scene_id=f"scene_{cond.name}_{scene_idx:03d}",
                weather=cond,
                num_gt_objects=num_gt,
                num_detections=tp + fp,
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                mean_divergence=divergence,
                max_divergence=max_div,
                uncertain_detections=uncertain,
            )
            scene_results.append(scene_eval)

        weather_eval = WeatherEvaluation(
            weather=cond, scene_results=scene_results
        )
        weather_results.append(weather_eval)

    trig_coverage = compute_triggering_coverage(conditions)

    return FullEvaluationResult(
        weather_results=weather_results,
        triggering_coverage=trig_coverage,
    )

"""Sensitivity analysis: how evaluation metrics change across random seeds.

Runs the synthetic CARLA evaluation across multiple seeds to demonstrate
that the qualitative findings (triggering conditions degrade performance)
are robust and not artefacts of a single random initialisation.

Results show the mean and standard deviation of key metrics across seeds,
confirming that the triggering/non-triggering gap is statistically stable.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.evaluation.carla_evaluator import generate_synthetic_illustration
from src.seeds import DEFAULT_SEED, DEFAULT_SCENES, SENSITIVITY_SEEDS


@dataclass
class SensitivityResult:
    """Results from a multi-seed sensitivity analysis."""

    seeds: list[int]
    scenes_per_weather: int
    overall_recall: list[float]
    triggering_recall: list[float]
    non_triggering_recall: list[float]
    triggering_divergence: list[float]
    recall_gap: list[float]  # non_triggering - triggering

    @property
    def mean_recall_gap(self) -> float:
        return float(np.mean(self.recall_gap))

    @property
    def std_recall_gap(self) -> float:
        return float(np.std(self.recall_gap))

    def summary(self) -> dict:
        """Return summary statistics across seeds."""
        return {
            "num_seeds": len(self.seeds),
            "scenes_per_weather": self.scenes_per_weather,
            "overall_recall_mean": float(np.mean(self.overall_recall)),
            "overall_recall_std": float(np.std(self.overall_recall)),
            "triggering_recall_mean": float(np.mean(self.triggering_recall)),
            "triggering_recall_std": float(np.std(self.triggering_recall)),
            "non_triggering_recall_mean": float(np.mean(self.non_triggering_recall)),
            "non_triggering_recall_std": float(np.std(self.non_triggering_recall)),
            "triggering_divergence_mean": float(np.mean(self.triggering_divergence)),
            "triggering_divergence_std": float(np.std(self.triggering_divergence)),
            "recall_gap_mean": self.mean_recall_gap,
            "recall_gap_std": self.std_recall_gap,
        }


def run_sensitivity_analysis(
    seeds: list[int] | None = None,
    scenes_per_weather: int = DEFAULT_SCENES,
) -> SensitivityResult:
    """Run evaluation across multiple seeds and collect metrics.

    Args:
        seeds: List of random seeds. Defaults to ``SENSITIVITY_SEEDS``
            in ``src/seeds.py``.
        scenes_per_weather: Scenes per weather condition per seed.

    Returns:
        SensitivityResult with per-seed and aggregate statistics.
    """
    if seeds is None:
        seeds = list(SENSITIVITY_SEEDS)

    overall_recall = []
    triggering_recall = []
    non_triggering_recall = []
    triggering_divergence = []
    recall_gap = []

    for seed in seeds:
        result = generate_synthetic_illustration(
            num_scenes_per_weather=scenes_per_weather,
            seed=seed,
        )
        s = result.compute_summary()

        overall_recall.append(s["overall_mean_recall"])
        triggering_recall.append(s["triggering_mean_recall"])
        non_triggering_recall.append(s["non_triggering_mean_recall"])
        triggering_divergence.append(s["triggering_mean_divergence"])
        recall_gap.append(
            s["non_triggering_mean_recall"] - s["triggering_mean_recall"]
        )

    return SensitivityResult(
        seeds=seeds,
        scenes_per_weather=scenes_per_weather,
        overall_recall=overall_recall,
        triggering_recall=triggering_recall,
        non_triggering_recall=non_triggering_recall,
        triggering_divergence=triggering_divergence,
        recall_gap=recall_gap,
    )


@dataclass
class ThresholdSensitivityResult:
    """Results from varying the SOTIF triggering thresholds."""

    rain_thresholds: list[float]
    visibility_thresholds: list[float]
    recall_gaps: list[list[float]]  # [rain_idx][vis_idx]
    triggering_counts: list[list[int]]
    seed: int
    scenes_per_weather: int


def run_threshold_sensitivity(
    rain_thresholds: list[float] | None = None,
    visibility_thresholds: list[float] | None = None,
    seed: int = DEFAULT_SEED,
    scenes_per_weather: int = DEFAULT_SCENES,
) -> ThresholdSensitivityResult:
    """Vary the SOTIF triggering thresholds and measure the recall gap.

    The default thresholds (rain > 20 mm/h OR visibility < 200m) are from
    ISO 21448 Cl.7. This analysis shows how sensitive the findings are to
    different threshold choices.

    Args:
        rain_thresholds: Rain thresholds to test. Default: [10, 15, 20, 25, 30, 40, 50].
        visibility_thresholds: Visibility thresholds to test. Default: [100, 150, 200, 250, 300].
        seed: Random seed for evaluation.
        scenes_per_weather: Scenes per weather condition.

    Returns:
        ThresholdSensitivityResult with recall gaps for each threshold combination.
    """
    if rain_thresholds is None:
        rain_thresholds = [10, 15, 20, 25, 30, 40, 50]
    if visibility_thresholds is None:
        visibility_thresholds = [100, 150, 200, 250, 300]

    # Run evaluation once (the data doesn't change; only the classification changes)
    result = generate_synthetic_illustration(
        num_scenes_per_weather=scenes_per_weather,
        seed=seed,
    )

    recall_gaps = []
    triggering_counts = []

    for rain_thresh in rain_thresholds:
        gap_row = []
        count_row = []
        for vis_thresh in visibility_thresholds:
            # Reclassify triggering conditions with new thresholds
            trig_recalls = []
            non_trig_recalls = []
            n_trig = 0
            for wr in result.weather_results:
                is_trig = (
                    wr.weather.rain_intensity > rain_thresh
                    or wr.weather.fog_density < vis_thresh
                )
                if is_trig:
                    trig_recalls.append(wr.mean_recall)
                    n_trig += 1
                else:
                    non_trig_recalls.append(wr.mean_recall)

            if trig_recalls and non_trig_recalls:
                gap = float(np.mean(non_trig_recalls) - np.mean(trig_recalls))
            else:
                gap = 0.0
            gap_row.append(gap)
            count_row.append(n_trig)

        recall_gaps.append(gap_row)
        triggering_counts.append(count_row)

    return ThresholdSensitivityResult(
        rain_thresholds=rain_thresholds,
        visibility_thresholds=visibility_thresholds,
        recall_gaps=recall_gaps,
        triggering_counts=triggering_counts,
        seed=seed,
        scenes_per_weather=scenes_per_weather,
    )


def print_threshold_sensitivity_report(result: ThresholdSensitivityResult):
    """Print the threshold sensitivity analysis report."""
    print("=" * 80)
    print("THRESHOLD SENSITIVITY: Recall Gap vs. SOTIF Triggering Threshold")
    print("=" * 80)
    print(f"  Seed: {result.seed}, Scenes/weather: {result.scenes_per_weather}")
    print(f"  ISO 21448 Cl.7 default: rain > 20 mm/h OR visibility < 200m")
    print()

    # Header
    header = f"{'Rain>':>8}"
    for vis in result.visibility_thresholds:
        header += f"  vis<{vis:>3}m"
    print(header)
    print("-" * len(header))

    for i, rain in enumerate(result.rain_thresholds):
        row = f"{rain:>5}mm/h"
        for j in range(len(result.visibility_thresholds)):
            gap = result.recall_gaps[i][j]
            marker = " *" if (rain == 20 and result.visibility_thresholds[j] == 200) else "  "
            row += f"  {gap:>6.3f}{marker}"
        print(row)

    print()
    print("  * = ISO 21448 Cl.7 default threshold")
    print("  Values show recall gap (non-triggering - triggering).")
    print("  Positive values indicate performance degradation under triggering conditions.")


def print_sensitivity_report(result: SensitivityResult):
    """Print the sensitivity analysis report."""
    s = result.summary()
    print("=" * 70)
    print("SENSITIVITY ANALYSIS: Robustness Across Random Seeds")
    print("=" * 70)
    print(f"  Seeds tested:          {result.seeds}")
    print(f"  Scenes per weather:    {s['scenes_per_weather']}")
    print()
    print(f"  Overall recall:        {s['overall_recall_mean']:.4f} +/- {s['overall_recall_std']:.4f}")
    print(f"  Triggering recall:     {s['triggering_recall_mean']:.4f} +/- {s['triggering_recall_std']:.4f}")
    print(f"  Non-triggering recall: {s['non_triggering_recall_mean']:.4f} +/- {s['non_triggering_recall_std']:.4f}")
    print(f"  Triggering divergence: {s['triggering_divergence_mean']:.4f} +/- {s['triggering_divergence_std']:.4f}")
    print()
    print(f"  Recall gap (non-trig - trig): {s['recall_gap_mean']:.4f} +/- {s['recall_gap_std']:.4f}")
    print()
    if s['recall_gap_std'] < 0.05:
        print("  Conclusion: The triggering condition degradation is robust.")
        print("  The recall gap is stable across seeds (std < 0.05).")
    else:
        print("  Note: Some variability observed. Consider increasing scenes_per_weather.")

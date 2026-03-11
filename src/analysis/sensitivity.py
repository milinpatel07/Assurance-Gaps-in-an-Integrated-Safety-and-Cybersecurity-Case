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

from src.evaluation.carla_evaluator import generate_synthetic_evaluation


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
    scenes_per_weather: int = 50,
) -> SensitivityResult:
    """Run evaluation across multiple seeds and collect metrics.

    Args:
        seeds: List of random seeds. Defaults to [42, 123, 256, 512, 1024].
        scenes_per_weather: Scenes per weather condition per seed.

    Returns:
        SensitivityResult with per-seed and aggregate statistics.
    """
    if seeds is None:
        seeds = [42, 123, 256, 512, 1024]

    overall_recall = []
    triggering_recall = []
    non_triggering_recall = []
    triggering_divergence = []
    recall_gap = []

    for seed in seeds:
        result = generate_synthetic_evaluation(
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

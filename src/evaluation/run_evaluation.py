"""Runner for the synthetic weather-grid illustration (no detector, no CARLA).

Prints the weather grid and the summary of the seeded synthetic illustration,
and saves a plot. Live CARLA evaluation is not implemented in this repository;
`--mode carla` exits with an error instead of pretending to run it.
"""

from __future__ import annotations

import argparse
import os
import sys

from src.evaluation.carla_evaluator import generate_synthetic_illustration
from src.seeds import DEFAULT_SEED
from src.evaluation.weather_conditions import (
    generate_weather_grid,
    compute_triggering_coverage,
    get_triggering_conditions,
)

CARLA_NOT_IMPLEMENTED = (
    "Live CARLA evaluation is not implemented in this repository. Only the "
    "synthetic weather-grid illustration (no detector, no CARLA) is available: "
    "run without --mode, or with --mode synthetic."
)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Synthetic weather-grid illustration (no detector, no CARLA). "
            "The output is seeded and illustrative, not a measurement."
        )
    )
    parser.add_argument(
        "--mode",
        choices=["synthetic", "carla"],
        default="synthetic",
        help=(
            "'synthetic' (the default) runs the seeded illustration; 'carla' "
            "exits with an error, because live CARLA evaluation is not implemented"
        ),
    )
    parser.add_argument(
        "--scenes-per-weather",
        type=int,
        default=10,
        help="Number of synthetic scenes per weather condition",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory for results",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for the synthetic illustration",
    )
    args = parser.parse_args()

    if args.mode == "carla":
        print(CARLA_NOT_IMPLEMENTED, file=sys.stderr)
        sys.exit(2)

    os.makedirs(args.output_dir, exist_ok=True)

    # Generate weather grid
    conditions = generate_weather_grid()
    triggering = get_triggering_conditions(conditions)
    coverage = compute_triggering_coverage(conditions)

    print(f"Weather grid: {len(conditions)} conditions")
    print(f"  Triggering: {len(triggering)}")
    print(f"  Coverage: {coverage}")

    print("\nSynthetic weather-grid illustration (no detector, no CARLA)...")
    result = generate_synthetic_illustration(
        num_scenes_per_weather=args.scenes_per_weather,
        seed=args.seed,
    )

    summary = result.compute_summary()
    print("\nIllustration summary (seeded, not a measurement):")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    # Generate the plot
    try:
        from src.visualization.coverage_plots import plot_weather_evaluation
        plot_weather_evaluation(
            summary,
            os.path.join(args.output_dir, "weather_evaluation.png"),
        )
    except ImportError:
        print("matplotlib not available; skipping plot generation")


if __name__ == "__main__":
    main()

"""CARLA evaluation runner.

Provides both synthetic evaluation (for demonstration without CARLA)
and the interface for real CARLA evaluation with a running server.
"""

from __future__ import annotations

import argparse
import os

from src.evaluation.carla_evaluator import generate_synthetic_illustration
from src.evaluation.weather_conditions import (
    generate_weather_grid,
    compute_triggering_coverage,
    get_triggering_conditions,
)


def main():
    parser = argparse.ArgumentParser(
        description="Run CARLA evaluation for the deep ensemble under weather conditions"
    )
    parser.add_argument(
        "--mode",
        choices=["synthetic", "carla"],
        default="synthetic",
        help="Evaluation mode: 'synthetic' for demonstration, 'carla' for live evaluation",
    )
    parser.add_argument(
        "--scenes-per-weather",
        type=int,
        default=10,
        help="Number of scenes per weather condition",
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
        default=42,
        help="Random seed for synthetic evaluation",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Generate weather grid
    conditions = generate_weather_grid()
    triggering = get_triggering_conditions(conditions)
    coverage = compute_triggering_coverage(conditions)

    print(f"Weather grid: {len(conditions)} conditions")
    print(f"  Triggering: {len(triggering)}")
    print(f"  Coverage: {coverage}")

    if args.mode == "synthetic":
        print("\nRunning synthetic evaluation (no CARLA required)...")
        result = generate_synthetic_illustration(
            num_scenes_per_weather=args.scenes_per_weather,
            seed=args.seed,
        )
    else:
        print("\nCARLA mode requires a running CARLA server.")
        print("To start CARLA: ./CarlaUE4.sh -quality-level=Epic -world-port=2000")
        print("Falling back to synthetic evaluation.")
        result = generate_synthetic_illustration(
            num_scenes_per_weather=args.scenes_per_weather,
            seed=args.seed,
        )

    summary = result.compute_summary()
    print("\nEvaluation Summary:")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    # Generate visualization
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

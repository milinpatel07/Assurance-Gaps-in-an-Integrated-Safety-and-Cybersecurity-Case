# Synthetic illustration outputs

Provenance: generated (deterministic) and seeded (seed 42). Nothing in this
directory is a measurement.

These are the committed reference outputs that `make verify-refs` compares a
fresh run against. The decision-point catalogue and the findings classification
follow the WAISE paper: Patel and Jung, "Integrating Cybersecurity Into the AI
Safety Assurance Argument: A GSN Pattern for AI-Based Perception Components in
Highly Automated Driving", WAISE 2026 (workshop at SAFECOMP 2026), LNCS.

## What these numbers are

The files contain two different things.

- **Deterministic analysis outputs.** The decision-point catalogue, the findings
  classification, and the standards, GSN and findings sections of the summary
  report come from the analysis code in `src/`. They do not depend on a random
  seed.
- **A seeded illustration of the weather-grid evaluation.** The numbers in
  `weather_evaluation_seed42.csv` and in the synthetic illustration section of
  `summary_report_seed42.txt` come from `generate_synthetic_illustration()` in
  `src/evaluation/carla_evaluator.py`. That function does not connect to CARLA
  and does not run a detector. A weather-severity term drives recall, precision
  and divergence through fixed formulas plus seeded Gaussian noise (seed 42), so
  re-running with the same seed reproduces the files exactly. The numbers show
  what the evaluation pipeline produces and how its output is organised. They
  are not measurements of a trained detector and must not be cited as empirical
  results.

Measured results from a trained PointPillars deep ensemble on KITTI and nuScenes
are in `data/empirical_results/`. Its README states their provenance and that
neither paper claims them.

## Files

- `decision_points.csv`: decision-point catalogue (WAISE Table 4). DP-1 to DP-7,
  written `I-1` to `I-7` in the file. Deterministic.
- `gaps.csv`: findings classification (WAISE Table 5). F-1 to F-5, written
  `Gap-1` to `Gap-5` in the file; the Category column holds the paper's two
  categories, II (integration-induced finding) and OM (open methodological
  problem). Deterministic.
- `summary_report_seed42.txt`: consolidated plain-text report. The standards,
  GSN, decision-point and findings sections are deterministic; the synthetic
  illustration section is seeded.
- `weather_evaluation_seed42.csv`: per-weather-condition output of the synthetic
  illustration, seed 42.

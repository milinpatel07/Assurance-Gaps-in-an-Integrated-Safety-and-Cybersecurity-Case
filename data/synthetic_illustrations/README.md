# Synthetic Illustration Outputs

This directory holds reference outputs of the synthetic illustration pipeline. The
files demonstrate the format and structure of the analysis and evaluation outputs.
They are not empirical measurements.

## Origin

The weather-evaluation outputs are produced by `src/evaluation/carla_evaluator.py`,
function `generate_synthetic_illustration()`. That function does not connect to
CARLA and does not run a detector. It produces per-scene detection counts and
uncertainty values from a deterministic, seeded procedure (seed = 42): a weather-
severity term drives recall, precision, and divergence through fixed formulas plus
seeded Gaussian noise. Re-running with the same seed reproduces the files exactly.

The standards, GSN, inconsistency, and gap tables are deterministic outputs of the
analysis code in `src/`; they do not depend on a random seed.

## What these numbers are, and are not

The weather-evaluation numbers in `weather_evaluation_seed42.csv` and the CARLA
evaluation section of `summary_report_seed42.txt` are illustrative. They show what
the evaluation pipeline produces and how its output is organised. They are not
measurements of a trained detector and must not be cited as empirical results.

For real empirical evidence supporting the case study claims at G5 (V&V
sufficiency) and G6 (runtime monitoring), see `data/empirical_results/`. That
directory contains measured AUROC and MDR/MFAR results from a trained PointPillars
deep ensemble on KITTI and nuScenes, together with a provenance README.

## Files

- `gaps.csv` - assurance gap classification; deterministic output of the analysis
  code.
- `decision_points.csv` - requirement inconsistency catalogue; deterministic output
  of the analysis code.
- `summary_report_seed42.txt` - consolidated report. The standards, GSN, and gap
  sections are deterministic; the CARLA evaluation section is synthetic
  illustration.
- `weather_evaluation_seed42.csv` - per-weather-condition evaluation; synthetic
  illustration, seed = 42.

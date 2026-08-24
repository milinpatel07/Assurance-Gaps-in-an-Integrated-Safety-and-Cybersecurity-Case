# Reference Figures

Provenance: seeded-synthetic and derived. Nothing here is a measurement.

These four PNGs are committed copies of figures that `make results` writes to
`output/figures/`. They are kept so that a reader can see the outputs without
installing anything or running the pipeline.

| File | What it shows | How it is produced |
|---|---|---|
| `integrated_gsn.png` | The 9-goal integrated pattern | Graphviz rendering of `build_integrated_gsn()`, via `src/visualization/gsn_renderer.py` |
| `coverage_heatmap.png` | Clause coverage per lifecycle phase | `src/visualization/coverage_plots.py` from `StandardsRegistry.compute_coverage_matrix()` |
| `evidence_convergence.png` | The four evidence types meeting at G5 | `src/visualization/coverage_plots.py` from `src/analysis/evidence_convergence.py` |
| `weather_heatmap.png` | Detection performance across the weather grid | `src/visualization/coverage_plots.py` from the seeded illustration (seed = 42) in `src/evaluation/carla_evaluator.py` |

The first three derive from the hand-coded standards and GSN data in `src/` and
do not depend on the seed. The fourth comes from the seeded illustration
pipeline, which does not run a detector and does not connect to CARLA. Its
numbers illustrate the format of the evaluation output. They are not
measurements and must not be cited as results. See
`data/synthetic_illustrations/README.md`.

To regenerate:

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output
```

Graphviz must be installed for the GSN PNG. Without it the pipeline prints a
warning and carries on, still writing the `.dot` source.

Neither paper includes these files. Both papers draw their own figures in TikZ,
inside the `.tex` sources in `paper/`.

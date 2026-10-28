# Reference figures

Provenance: three figures are generated from hand-coded data in `src/`; one
(`weather_heatmap.png`) is seeded (seed 42). Nothing here is a measurement.

These four PNGs are repository renderings, committed copies of figures that
`make results` writes to `output/figures/`. They are kept so that a reader can
see the outputs without installing anything or running the pipeline. None of
them is a figure or table of either paper: the WAISE paper (Patel and Jung,
"Integrating Cybersecurity into the AI Safety Assurance Argument: A GSN Pattern
for AI-Based Perception Components in Highly Automated Driving", WAISE 2026) and
the position paper (Patel and Jung, "Operational Safety and Cybersecurity
Assurance of AI-Based Perception in Highly Automated Driving", SAFECOMP 2026)
draw their own figures in TikZ, inside the `.tex` sources in `paper/`.

| File | What it shows | How it is produced |
|---|---|---|
| `integrated_gsn.png` | The integrated GSN argument pattern as one Graphviz diagram: G1 to G9, strategy S1, contexts C1 and C2, assumption A1.4 and the solution nodes. Goals and solutions are coloured by source standard, with a legend for the four standards (ISO 26262, ISO 21448, ISO/PAS 8800, ISO/SAE 21434) and for the undeveloped goal G9. The WAISE paper draws the pattern as Fig. 1 | `src/visualization/gsn_renderer.py` from `build_integrated_gsn()` |
| `coverage_heatmap.png` | The number of applicable clauses per standard and lifecycle phase, including ISO/IEC TR 5469 (an informative technical report) | `src/visualization/coverage_plots.py` from `StandardsRegistry.compute_coverage_matrix()` |
| `evidence_convergence.png` | The four evidence types (a) to (d) at G5, the verification and validation (V&V) goal, one per standard: (a) MC/DC structural coverage under ISO 26262 (scale: coverage ratio), (b) triggering-condition coverage in scenario testing under ISO 21448, (c) deep-ensemble disagreement as uncertainty indicator under ISO/PAS 8800 (AUROC), (d) adversarial penetration testing under ISO/SAE 21434 (attack success rate). Fig. 1(b) of the WAISE paper shows the same four evidence types at G5 | `src/visualization/coverage_plots.py` (`plot_evidence_convergence`), colours from `src/visualization/standard_colors.py` |
| `weather_heatmap.png` | Mean recall and mean ensemble divergence over the 5 x 5 rain and fog grid, from the seeded synthetic illustration (seed 42, no detector is run). A red border marks the cells that meet the case study's thresholds, rain > 20 mm/h or visibility < 200 m; these thresholds are case-study choices, not values from ISO 21448 | `src/visualization/coverage_plots.py` from the seeded illustration in `src/evaluation/carla_evaluator.py` |

The first three do not depend on the seed. The fourth comes from the seeded
illustration, which runs no detector; `data/synthetic_illustrations/README.md`
states what its numbers are and are not.

To regenerate:

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output
cp output/figures/{integrated_gsn,coverage_heatmap,evidence_convergence,weather_heatmap}.png docs/figures/
```

Graphviz (the `dot` program) must be installed for the GSN PNG. Without it the
pipeline prints a warning and carries on, still writing the `.dot` source.

Neither paper includes these files: the WAISE paper (Patel and Jung,
"Integrating Cybersecurity Into the AI Safety Assurance Argument: A GSN Pattern
for AI-Based Perception Components in Highly Automated Driving", WAISE 2026) and
the position paper (Patel and Jung, "Operational Safety and Cybersecurity
Assurance of AI-Based Perception in Highly Automated Driving", SAFECOMP 2026)
draw their own figures in TikZ; the published papers carry them.

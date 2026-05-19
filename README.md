# Integrating Cybersecurity into the AI Safety Assurance Argument: A GSN Pattern for AI-Based Perception Components in Highly Automated Driving

Supplementary material for:

> **Integrating Cybersecurity into the AI Safety Assurance Argument: A GSN Pattern for AI-Based Perception Components in Highly Automated Driving**
>
> Milin Patel and Rolf Jung — Kempten University of Applied Sciences
>

The paper itself is published separately and is not included in this repository.


[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/blob/main/notebooks/assurance_gaps_analysis.ipynb)

---

## Overview

This repository contains the implementation of a five-step constructive integration methodology that combines assurance claims from ISO 26262, ISO 21448, ISO/SAE 21434, and ISO/PAS 8800 into a single GSN argument pattern for an AI-based LiDAR perception component. The integrated pattern extends ISO/PAS 8800 Annex B from 6 to 9 goals, identifies 7 decision points where the standards defer to application context, and classifies 5 assurance gaps — 2 of which are only visible through constructive integration.

The GSN argument structure is defined in machine-readable YAML files (`gsn/`) and rendered to SVG using [gsn2x](https://github.com/jonasthewolf/gsn2x), an open-source tool that produces standard-compliant GSN diagrams.

## Repository Structure

```
├── gsn/                        # GSN argument patterns (YAML for gsn2x)
│   ├── integrated_pattern.gsn.yaml   # Figure 2: 9-goal integrated pattern
│   └── evidence_convergence.gsn.yaml # Figure 3: evidence convergence at G5
│
├── src/
│   ├── standards/              # Claim extraction and lifecycle mapping (Steps 1-2)
│   ├── gsn/                    # GSN data model and construction (Step 3)
│   ├── analysis/               # Inconsistency and gap analysis (Steps 4-5)
│   ├── perception/             # Case study: SECOND detector + deep ensemble
│   ├── evaluation/             # CARLA evaluation under SOTIF triggering conditions
│   ├── results/                # Output generation (JSON, CSV, LaTeX tables)
│   └── visualization/          # Matplotlib figures
│
├── tests/                      # 192 tests
├── notebooks/                  # Interactive Jupyter/Colab notebook
├── configs/                    # YAML configuration
├── data/
│   ├── empirical_results/      # Measured KITTI/nuScenes results (PointPillars ensemble)
│   └── synthetic_illustrations/  # Deterministic seeded illustration outputs (seed=42)
├── docs/                       # LaTeX sections and reference figures
├── Makefile                    # Build targets
├── REPRODUCING.md              # Reproduction guide
└── pyproject.toml
```

## Three-layer repository structure

The repository separates three kinds of artefact, which should not be conflated:

1. **Methodology** — `src/`. The five-step constructive integration code: claim
   extraction, lifecycle mapping, GSN construction, inconsistency analysis, and gap
   classification, with the perception, evaluation, and results modules. This
   implements the method described in the paper.

2. **Synthetic illustrations** — `data/synthetic_illustrations/`. Reference outputs
   of the analysis and the synthetic evaluation pipeline. The weather-evaluation
   numbers are deterministic seeded output (seed = 42), not measurements. See
   `data/synthetic_illustrations/README.md`.

3. **Empirical evidence** — `data/empirical_results/`. Measured AUROC and MDR/MFAR
   results from a trained PointPillars deep ensemble on KITTI and nuScenes,
   supporting the G5 and G6 claims of the integrated pattern. See
   `data/empirical_results/README.md` for full provenance.

## GSN Diagrams

The integrated GSN argument and the evidence convergence diagram are defined as YAML files following the [gsn2x](https://github.com/jonasthewolf/gsn2x) format. This makes the argument structure machine-readable, diffable, and reproducible.

To render the diagrams:

```bash
# Download gsn2x (one-time setup)
make gsn-install

# Render all GSN diagrams to SVG
make gsn
```

Or manually:

```bash
gsn2x gsn/integrated_pattern.gsn.yaml
gsn2x gsn/evidence_convergence.gsn.yaml
```

The YAML files are the single source of truth for the argument structure. Each node includes its ISO clause reference.

## Installation

```bash
git clone https://github.com/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case.git
cd Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case

pip install -e ".[dev]"
```

## Usage

```bash
# Run the test suite
make test

# Generate all results (JSON, CSV, LaTeX tables, figures)
make results

# Run the five-step analysis with console output
python -m src.analysis.run_analysis

# Generate GSN diagrams
make gsn
```

The `make results` command produces structured outputs in `output/`:
- `analysis_results.json` — complete structured results
- `csv/` — coverage matrix, inconsistencies, gaps, counterfactual visibility, sensitivity analysis, weather evaluation
- `latex/` — 8 LaTeX tables in booktabs format for direct `\input{}` inclusion
- `figures/` — heatmaps, bar charts, and the GSN diagram (Graphviz)

## Tests

```bash
pytest tests/ -v
```

192 tests cover standards instantiation, GSN construction, inconsistency and gap classification, the perception module, the evaluation pipeline, result generation, paper claim validation, completeness checking, counterfactual analysis, generalisability classification, base pattern sensitivity, practitioner guidance, and threshold sensitivity.

## Reproducibility

All evaluation results are deterministic given the same random seed. See [REPRODUCING.md](REPRODUCING.md) for step-by-step instructions.

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output
```

## Citation

```bibtex
@inproceedings{PatelJung2026,
  author    = {Patel, Milin and Jung, Rolf},
  title     = {Integrating Cybersecurity into the {AI} Safety Assurance Argument:
               A {GSN} Pattern for {AI}-Based Perception Components in
               Highly Automated Driving},
  booktitle = {WAISE 2026 Workshop at SafeComp 2026},
  series    = {LNCS},
  publisher = {Springer},
  year      = {2026}
}
```

## License

MIT License

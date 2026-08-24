# Reproducing the Results

**"Integrating Cybersecurity into the AI Safety Assurance Argument: A GSN Pattern for AI-Based Perception Components in Highly Automated Driving"**
— Milin Patel, Rolf Jung — SafeComp 2026 WAISE Workshop

## Prerequisites

- Python >= 3.9
- pip
- gsn2x >= 4.2.3 (for GSN diagram rendering; optional)
- Graphviz (for legacy Graphviz-based GSN rendering; optional)

On Windows, clone with `git clone -c core.longpaths=true ...` or into a short
directory: the camera-ready paper filenames are long enough that a deep target
path exceeds the default 260-character limit and the checkout fails.

## Step 1: Clone and Install

```bash
git clone https://github.com/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case.git
cd Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case

pip install -r requirements.lock
pip install -e . --no-deps
```

`requirements.lock` pins the exact versions the results were verified with.
`pip install -e ".[dev]"` also works and takes the newest compatible versions
instead. PyTorch is not required: `src/perception/` falls back to numpy, and no
number either paper uses depends on it. Install it with
`pip install -e ".[perception]"` only if you want the perception module's torch
paths.

## Step 2: Run the Test Suite

```bash
pytest tests/ -v --tb=short
```

The full suite (285 tests) should pass.

## Step 3: Generate All Results

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output
```

Or equivalently:

```bash
make results SEED=42 SCENES=50
```

### Output Files

| Directory | Contents |
|-----------|----------|
| `output/analysis_results.json` | Complete structured results |
| `output/summary_report.txt` | Human-readable summary |
| `output/csv/` | Coverage matrix, goal density, inconsistencies, gaps, counterfactual visibility, sensitivity analysis, weather evaluation |
| `output/latex/` | 8 LaTeX tables (booktabs format) for direct `\input{}` inclusion |
| `output/figures/` | Heatmaps, bar charts, convergence diagram, GSN diagram |

## Step 4: Render GSN Diagrams

The GSN argument patterns are defined as YAML files in `gsn/` and rendered using [gsn2x](https://github.com/jonasthewolf/gsn2x):

```bash
# Download gsn2x (Linux)
make gsn-install

# Render diagrams
make gsn
```

This produces:
- `gsn/integrated_pattern.gsn.svg` — the 9-goal integrated pattern (Figure 2)
- `gsn/evidence_convergence.gsn.svg` — evidence convergence at G5 (Figure 3)

## One command, and the drift check

```bash
make reproduce
```

regenerates every artefact both papers use and then diffs the committed
reference outputs under `data/synthetic_illustrations/`, the traceability
index, and the interactive GSN view against a fresh regeneration. CI runs the
same check on every push. A non-empty diff means a source changed without its
references; the rule is to fix the cause, never to edit a reference.

## Seeds and the run manifest

Every seed lives in `src/seeds.py`. Each `generate_all` run writes
`output/run_manifest.json` recording the commit hash, timestamp, Python and
package versions, the seeds used, and the SHA-256 of every YAML input. The
manifest is the only run artefact allowed to differ between runs.

## Determinism

All outputs are byte-identical given the same seed; no output carries a
timestamp:

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run1
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run2
diff -r output_run1 output_run2
```

Only `run_manifest.json` differs, in its `run_at` field.

## What cannot be reproduced from this repository

`data/empirical_results/` holds measurements whose training and evaluation
scripts belong to a paper in preparation (P5) and are not in this repository.
`make reproduce` does not regenerate them; their provenance README states what
they are and where they come from. Neither paper in this repository claims
them.

## LaTeX Integration

```latex
\usepackage{booktabs}
% ...
\input{output/latex/table2_coverage.tex}
```

For GSN figures, include the SVG or convert to PDF:

```latex
\includegraphics[width=\textwidth]{gsn/integrated_pattern.gsn.pdf}
```

## Citation

```bibtex
@inproceedings{PatelJung2026,
  author    = {Patel, Milin and Jung, Rolf},
  title     = {Integrating Cybersecurity into the {AI} Safety Assurance Argument:
               A {GSN} Pattern for {AI}-Based Perception Components in Highly Automated Driving},
  booktitle = {SafeComp 2026 Workshops (WAISE)},
  series    = {LNCS},
  publisher = {Springer},
  year      = {2026}
}
```

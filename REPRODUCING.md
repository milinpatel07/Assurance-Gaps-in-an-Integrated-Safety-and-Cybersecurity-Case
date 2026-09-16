# Reproducing the results

**"Integrating Cybersecurity into the AI Safety Assurance Argument: A GSN
Pattern for AI-Based Perception Components in Highly Automated Driving"**

Milin Patel and Rolf Jung. WAISE 2026 Workshop at SAFECOMP 2026.

## Prerequisites

- Python >= 3.12 to install `requirements.lock` (it was frozen on Python 3.13,
  matching CI, and pins wheels that need 3.12). The package itself supports
  Python >= 3.9; on 3.9 to 3.11 use the `[dev]` install in Step 1 instead.
- pip
- gsn2x >= 4.2.3 (for GSN diagram rendering; optional)
- Graphviz (for legacy Graphviz-based GSN rendering; optional)

On Windows, clone with `git clone -c core.longpaths=true ...` or into a short
directory: the camera-ready paper filenames are long enough that a deep target
path exceeds the default 260-character limit and the checkout fails.

## Step 1: clone and install

```bash
git clone https://github.com/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case.git
cd Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case

pip install -r requirements.lock
pip install -e . --no-deps
```

`requirements.lock` pins the exact versions we verified the results against; it
was frozen on Python 3.13 and needs Python 3.12 or newer.
`pip install -e ".[dev]"` also works, takes the newest compatible versions
instead, and runs on Python 3.9 or newer. PyTorch is not required: `src/perception/` falls back to numpy, and no
number either paper uses depends on it. Install it with
`pip install -e ".[perception]"` only if you want the perception module's torch
paths.

## Step 2: run the test suite

```bash
pytest tests/ -v --tb=short
```

The full suite should pass.

## Step 3: generate all results

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output
```

Or equivalently:

```bash
make results SEED=42 SCENES=50
```

### Output files

| Directory | Contents |
|-----------|----------|
| `output/analysis_results.json` | Complete structured results |
| `output/summary_report.txt` | Human-readable summary |
| `output/csv/` | Coverage matrix, goal density, decision points, findings, counterfactual visibility, sensitivity analysis, weather evaluation |
| `output/latex/` | 8 LaTeX tables (booktabs format) for direct `\input{}` inclusion |
| `output/figures/` | Heatmaps, bar charts, convergence diagram, GSN diagram |

## Step 4: render GSN diagrams

`gsn/` holds the argument patterns as YAML. [gsn2x](https://github.com/jonasthewolf/gsn2x) renders them:

```bash
# Download the gsn2x binary for this platform
make gsn-install

# Render diagrams
make gsn
```

This produces:
- `gsn/integrated_pattern.gsn.svg`: the nine-goal integrated pattern (Figure 2)
- `gsn/evidence_convergence.gsn.svg`: evidence convergence at G5 (Figure 3)

## One command, and the drift check

```bash
make reproduce
```

regenerates every artefact both papers use and then diffs the committed
reference outputs under `data/synthetic_illustrations/`, the traceability
index, and the generated pages against a fresh regeneration. CI runs the
same check on every push. A non-empty diff means a source changed without its
references; the rule is to fix the cause, never to edit a reference.

## Seeds and the run manifest

Every seed lives in `src/seeds.py`. Each `generate_all` run writes
`output/run_manifest.json` recording the commit hash, timestamp, Python and
package versions, the seeds used, and the SHA-256 of every YAML input. The
manifest is the only run artefact allowed to differ between runs.

## Determinism

Given the same seed, every output is byte-identical except the run manifest,
which is the only file that carries a timestamp:

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run1
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run2
diff -r output_run1 output_run2
```

Only `run_manifest.json` differs, in its `run_at` field.

## What cannot be reproduced from this repository

`data/empirical_results/` holds measurements whose training and evaluation
scripts belong to a runtime-monitoring paper in preparation by the same
author, and are not in this repository. `make reproduce` does not regenerate
them; their provenance README states what
they are and where they come from. Neither paper in this repository claims
them.

## LaTeX integration

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

Cite the papers, not this repository. The BibTeX for both is in
[README.md](README.md#citation), and [CITATION.cff](CITATION.cff) carries the
same details in machine-readable form.

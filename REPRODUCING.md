# Reproducing the results

This file covers the WAISE paper: Milin Patel and Rolf Jung, **"Integrating
Cybersecurity Into the AI Safety Assurance Argument: A GSN Pattern for AI-Based
Perception Components in Highly Automated Driving"**, WAISE 2026 (workshop at
SAFECOMP 2026), LNCS.

The position paper, Milin Patel and Rolf Jung, "Operational Safety and
Cybersecurity Assurance of AI-Based Perception in Highly Automated Driving"
(SAFECOMP 2026), argues from clause text and uses no artefact generated here,
so it has nothing to reproduce.

## Prerequisites

- Python 3.12 or newer to install `requirements.lock`. The lockfile was frozen
  on Python 3.13, matching CI, and pins wheels that need 3.12. The package
  itself supports Python 3.9 or newer; on 3.9 to 3.11 use the `[dev]` install
  in Step 1 instead.
- pip
- gsn2x 4.2.3 or newer (optional; renders the GSN diagrams in Step 4)
- Graphviz (optional; needed only for `docs/figures/integrated_gsn.png`)

## Step 1: clone and install

```bash
git clone https://github.com/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case.git
cd Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case

pip install -r requirements.lock
pip install -e . --no-deps
```

`requirements.lock` pins the exact versions the results were verified against.
`pip install -e ".[dev]"` also works: it takes the newest compatible versions
instead, and it is the install to use on Python 3.9 to 3.11.

PyTorch is not required: `src/perception/` falls back to numpy, and no number
in either paper depends on it. Install it with `pip install -e ".[perception]"`
only if you want the perception module's torch paths.

## Step 2: run the test suite

```bash
pytest tests/ -v --tb=short
```

All tests pass on a correct install. The notebook-execution tests are skipped
unless the notebook extra is installed (`pip install -e ".[notebooks]"`), because
`requirements.lock` does not include `nbclient`.

## Step 3: generate all results

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output
```

`make results SEED=42 SCENES=50` runs the same command.

### Output files

| Directory | Contents |
|-----------|----------|
| `output/analysis_results.json` | Complete structured results |
| `output/summary_report.txt` | Human-readable summary |
| `output/csv/` | Coverage matrix, goal density, decision points, findings, counterfactual visibility, sensitivity analysis, weather evaluation |
| `output/latex/` | LaTeX tables (booktabs format) for direct `\input{}` inclusion: the clause coverage matrix, the goals, the decision points, the findings and the other analyses. They are the repository's own tables, not tables of the WAISE paper |
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
- `gsn/integrated_pattern.gsn.svg`: the nine-goal integrated pattern. The
  WAISE paper draws the same pattern in Fig. 1: its top two levels in
  Fig. 1(a) and the G5 branch in Fig. 1(b).
- `gsn/evidence_convergence.gsn.svg`: one failure event entering G5 through
  several analysis paths (repository analysis, not in the camera-ready).

## Regenerate everything and check for drift

```bash
make reproduce
```

regenerates every artefact the WAISE paper uses and every generated page, then
compares the fresh output against three committed sets: the reference outputs
in `data/synthetic_illustrations/`, the traceability index (`TRACEABILITY.md`
and its exports `docs/traceability.json` and `docs/traceability.csv`), and the
generated pages and notebooks. CI runs the same check on every push. A
non-empty diff means a source changed without its references. Fix the source
of the change; do not edit a committed reference to make the diff pass.

## Seeds, the run manifest and determinism

Every seed lives in `src/seeds.py`. Each `generate_all` run writes
`output/run_manifest.json`, recording the commit hash, timestamp, Python and
package versions, the seeds used, and the SHA-256 of every YAML input.

Given the same seed, every output is byte-identical except the run manifest,
which is the only file that carries a timestamp (its `run_at` field):

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run1
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run2
diff -r output_run1 output_run2
```

## What cannot be reproduced from this repository

`data/empirical_results/` holds measurements whose training and evaluation
scripts belong to a runtime-monitoring paper in preparation by the first
author (Patel), and are not in this repository. `make reproduce` does not
regenerate them. Their provenance README states what they are and where they
come from; neither paper claims them.

## LaTeX integration

```latex
\usepackage{booktabs}
% ...
\input{output/latex/<table>.tex}
```

Replace `<table>` with the name of a file in `output/latex/`, for example
`decision_points` or `coverage_matrix`. The files are named by content; none of
them is numbered like a table of the WAISE paper.

For GSN figures, include the SVG or convert to PDF:

```latex
\includegraphics[width=\textwidth]{gsn/integrated_pattern.gsn.pdf}
```

## Citation

To cite the research, cite the papers; to cite the code and data, use the
Zenodo DOI. The BibTeX for both papers and the DOI are in
[README.md](README.md#citation-and-archive), and [CITATION.cff](CITATION.cff)
carries the same details in machine-readable form.

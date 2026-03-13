# Reproducing the Results

**"Assurance Gaps in an Integrated Safety and Cybersecurity Case for an AI-Based Perception Component in Highly Automated Driving"**
— Milin Patel, Rolf Jung — SafeComp 2026 WAISE Workshop

## Prerequisites

- Python >= 3.9
- pip
- gsn2x >= 4.2.3 (for GSN diagram rendering; optional)
- Graphviz (for legacy Graphviz-based GSN rendering; optional)

## Step 1: Clone and Install

```bash
git clone https://github.com/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case.git
cd Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case

pip install -e ".[dev]"
```

## Step 2: Run the Test Suite

```bash
pytest tests/ -v --tb=short
```

All 95 tests should pass.

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
| `output/csv/` | Coverage matrix, goal density, inconsistencies, gaps, weather evaluation |
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
- `gsn/integrated_pattern.gsn.svg` — the 9-goal integrated pattern (Figure 3)
- `gsn/evidence_convergence.gsn.svg` — evidence convergence at G5 (Figure 4)

## Determinism

All evaluation results are deterministic given the same random seed:

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run1
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run2
diff output_run1/analysis_results.json output_run2/analysis_results.json
```

The JSON files will be identical except for the `generated` timestamp.

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
  title     = {Assurance Gaps in an Integrated Safety and Cybersecurity Case
               for an {AI}-Based Perception Component in Highly Automated Driving},
  booktitle = {SafeComp 2026 Workshops (WAISE)},
  series    = {LNCS},
  publisher = {Springer},
  year      = {2026}
}
```

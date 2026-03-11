# Reproducing the Results

This document explains how to reproduce all results reported in:

**"Assurance Gaps in an Integrated Safety and Cybersecurity Case for an AI-Based Perception Component in Highly Automated Driving"**
Milin Patel, Rolf Jung — SafeComp 2026 WAISE Workshop

## Prerequisites

- Python >= 3.9
- pip (package installer)
- Graphviz (optional, for rendering GSN diagrams to PNG/PDF)

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

All 69 tests should pass. The tests verify the correctness of:
- Standards instantiation (clauses, claims, lifecycle mappings)
- GSN construction (9 goals, junction points, undeveloped goals)
- Inconsistency and gap classification
- Perception module (voxelization, 3D IoU, geometric divergence, AUROC)
- Weather condition generation and evaluation pipeline

## Step 3: Generate All Results

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output
```

Or equivalently:

```bash
make results SEED=42 SCENES=50
```

This produces the following outputs:

### Structured Data
| File | Description |
|------|-------------|
| `output/analysis_results.json` | Complete structured results |
| `output/summary_report.txt` | Human-readable summary |

### CSV Tables
| File | Description |
|------|-------------|
| `output/csv/coverage_matrix.csv` | Clause coverage per lifecycle phase (Table 2) |
| `output/csv/goal_density.csv` | Standard density per GSN goal (Table 4) |
| `output/csv/inconsistencies.csv` | Requirement inconsistencies (Table 5) |
| `output/csv/gaps.csv` | Assurance gaps (Table 6) |
| `output/csv/weather_evaluation.csv` | Per-weather detection results |

### LaTeX Tables (for direct inclusion in papers)
| File | Description |
|------|-------------|
| `output/latex/table1_standards.tex` | Standards overview (Table 1) |
| `output/latex/table2_coverage.tex` | Coverage matrix (Table 2) |
| `output/latex/table3_gsn_goals.tex` | GSN goal structure (Table 3) |
| `output/latex/table4_density.tex` | Goal density (Table 4) |
| `output/latex/table5_inconsistencies.tex` | Inconsistencies (Table 5) |
| `output/latex/table6_gaps.tex` | Gaps (Table 6) |
| `output/latex/table7_evidence.tex` | Evidence types at G5 (Table 7) |
| `output/latex/table8_weather.tex` | Weather evaluation (Table 8) |

### Figures
| File | Description |
|------|-------------|
| `output/figures/integrated_gsn.{dot,png,pdf}` | Integrated GSN diagram (Figure 3) |
| `output/figures/coverage_heatmap.{png,pdf}` | Coverage matrix heatmap |
| `output/figures/goal_density.{png,pdf}` | Goal density chart |
| `output/figures/evidence_convergence.{png,pdf}` | Evidence convergence at G5 (Figure 4) |
| `output/figures/weather_evaluation.{png,pdf}` | Triggering vs non-triggering comparison |
| `output/figures/weather_heatmap.{png,pdf}` | Rain x fog performance heatmap |
| `output/figures/inconsistency_distribution.{png,pdf}` | Inconsistency distribution |
| `output/figures/gap_distribution.{png,pdf}` | Gap lifecycle distribution |

## Step 4: Run Individual Components

### Five-Step Analysis (console output)
```bash
python -m src.analysis.run_analysis
```

### GSN Diagram Only
```bash
python -m src.visualization.gsn_renderer
```

### CARLA Evaluation Only
```bash
python -m src.evaluation.run_evaluation --mode synthetic --seed 42 --scenes-per-weather 50
```

## Determinism

All evaluation results are deterministic given the same random seed. The default seed is 42. To verify reproducibility:

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run1
python -m src.results.generate_all --seed 42 --scenes 50 --output output_run2
diff output_run1/analysis_results.json output_run2/analysis_results.json
```

The JSON files will be identical except for the `generated` timestamp.

## Programmatic Access

```python
from src.standards.registry import StandardsRegistry
from src.gsn.integrated_pattern import build_integrated_gsn
from src.analysis.inconsistencies import InconsistencyCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis
from src.evaluation.carla_evaluator import generate_synthetic_evaluation

# Standards framework
registry = StandardsRegistry()
matrix = registry.compute_coverage_matrix()       # Table 2
density = registry.compute_goal_density()          # Table 4

# Integrated GSN
gsn = build_integrated_gsn()
stats = gsn.compute_statistics()
junction_points = gsn.get_junction_points()        # Step 4 input

# Analysis
catalogue = InconsistencyCatalogue()               # Table 5
gaps = GapClassification()                         # Table 6
convergence = EvidenceConvergenceAnalysis()        # Figure 4

# Evaluation
result = generate_synthetic_evaluation(seed=42, num_scenes_per_weather=50)
summary = result.compute_summary()
```

## Directory Structure

```
output/
├── analysis_results.json          # Complete structured data
├── summary_report.txt             # Human-readable summary
├── csv/
│   ├── coverage_matrix.csv
│   ├── goal_density.csv
│   ├── inconsistencies.csv
│   ├── gaps.csv
│   └── weather_evaluation.csv
├── latex/
│   ├── table1_standards.tex
│   ├── table2_coverage.tex
│   ├── table3_gsn_goals.tex
│   ├── table4_density.tex
│   ├── table5_inconsistencies.tex
│   ├── table6_gaps.tex
│   ├── table7_evidence.tex
│   └── table8_weather.tex
└── figures/
    ├── integrated_gsn.dot
    ├── integrated_gsn.png
    ├── integrated_gsn.pdf
    ├── coverage_heatmap.{png,pdf}
    ├── goal_density.{png,pdf}
    ├── evidence_convergence.{png,pdf}
    ├── weather_evaluation.{png,pdf}
    ├── weather_heatmap.{png,pdf}
    ├── inconsistency_distribution.{png,pdf}
    └── gap_distribution.{png,pdf}
```

## LaTeX Integration

To include the generated tables in your paper:

```latex
\usepackage{booktabs}
% ...
\input{output/latex/table2_coverage.tex}
```

To include figures:

```latex
\includegraphics[width=\textwidth]{output/figures/coverage_heatmap.pdf}
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

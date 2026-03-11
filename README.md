# Assurance Gaps in an Integrated Safety and Cybersecurity Case

**Assurance Gaps in an Integrated Safety and Cybersecurity Case for an AI-Based Perception Component in Highly Automated Driving**

SafeComp 2026 WAISE Workshop — LLNCS (Springer)

## Overview

This repository provides the implementation for constructing and analysing an integrated safety and cybersecurity assurance case for an AI-based LiDAR perception component in highly automated driving (SAE Level 4+). The implementation follows a five-step constructive integration methodology that extends the ISO/PAS 8800 Annex B GSN argument pattern with claims from ISO 26262, ISO 21448, and ISO/SAE 21434.

### Key Findings

- **7 requirement inconsistencies** at junction points between standards (3 structural, 2 terminological, 2 methodological)
- **6 assurance gaps** across four lifecycle phases (2 integration-induced)
- **Central finding**: Evidence type asymmetry at the V&V goal (G5) — four fundamentally different evidence types must support a single sufficiency claim, and no standard defines how to combine them

## Architecture

```
src/
├── standards/          # Standards traceability framework (Step 1-2)
│   ├── base.py         # Core data model (Standard, Clause, Claim, LifecyclePhase)
│   ├── iso26262.py     # ISO 26262:2018 — Functional safety
│   ├── iso21448.py     # ISO 21448:2022 — SOTIF
│   ├── iso21434.py     # ISO/SAE 21434:2021 — Cybersecurity
│   ├── iso8800.py      # ISO/PAS 8800:2024 — AI safety
│   ├── tr5469.py       # ISO/IEC TR 5469:2024 — AI functional safety
│   └── registry.py     # Cross-standard query engine
│
├── gsn/                # Goal Structuring Notation model (Step 3)
│   ├── model.py        # GSN elements: Goal, Strategy, Context, Assumption, Solution
│   └── integrated_pattern.py  # Constructive integration (extends Annex B)
│
├── perception/         # Case study: SECOND deep ensemble detector
│   ├── voxelization.py       # LiDAR point cloud to voxel grid
│   ├── second_detector.py    # SECOND architecture (Yan et al., 2018)
│   └── deep_ensemble.py      # Deep ensemble with geometric divergence
│
├── evaluation/         # CARLA evaluation under SOTIF triggering conditions
│   ├── weather_conditions.py  # Parametric weather grid (rain, fog)
│   ├── carla_evaluator.py     # Evaluation pipeline and synthetic results
│   └── run_evaluation.py      # Evaluation runner
│
├── analysis/           # Inconsistency and gap analysis (Steps 4-5)
│   ├── inconsistencies.py     # 7 requirement inconsistencies (Table 5)
│   ├── gaps.py                # 6 assurance gaps (Table 6)
│   ├── evidence_convergence.py # Evidence convergence at G5 (Figure 4)
│   └── run_analysis.py        # Main analysis runner (all 5 steps)
│
└── visualization/      # Diagram and plot generation
    ├── gsn_renderer.py       # GSN diagram via Graphviz (Figure 3)
    └── coverage_plots.py     # Coverage heatmaps, density plots, convergence
```

## Methodology

The implementation follows the five-step constructive integration process:

| Step | Description | Output |
|------|-------------|--------|
| **Step 1** | Claim extraction from standard clauses | Claim sets per standard |
| **Step 2** | Lifecycle-phase mapping | Clause coverage table |
| **Step 3** | GSN construction (extend Annex B) | Integrated GSN (9 goals) |
| **Step 4** | Junction-point analysis | Inconsistency catalogue (7 items) |
| **Step 5** | Gap identification and classification | Gap classification (6 items) |

## Integrated GSN Structure

The pattern extends ISO/PAS 8800 Annex B from 6 goals to 9:

| Goal | Claim | Origin | Standards Active |
|------|-------|--------|-----------------|
| G1 | Integrated safety & cybersecurity requirements satisfied | Retained (reformulated) | 1 + 2 context |
| G2 | Specification sufficient | Retained | 3 (8800, 21448, 21434) |
| G3 | Data sets sufficient | Retained | 1 (8800 only) |
| G4 | Design sufficient | Retained | 3 (8800, 21448, 21434) |
| G5 | V&V sufficient | Retained | **4 (all standards)** |
| G6 | Monitoring sufficient | Retained | 3 (8800, 21448, 21434) |
| G7 | SOTIF residual risk acceptable | **New** | 1 (21448) |
| G8 | Cybersecurity risks managed | **New** | 1 (21434) |
| G9 | Modification assurance | **Gap** (undeveloped) | 0 |

## Case Study

**Component**: LiDAR-based 3D object detection module
- **Architecture**: SECOND (Sparsely Embedded Convolutional Detection)
- **Uncertainty**: Deep ensemble of 5 independently trained SECOND instances
- **Metric**: Geometric divergence of predicted 3D bounding boxes
- **Evaluation**: CARLA simulator under parametric weather (5 rain x 5 fog = 25 conditions)
- **ASIL**: D (severity S3, exposure E4, controllability C3 at SAE Level 4+)

## Installation

```bash
# Clone the repository
git clone https://github.com/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case.git
cd Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case

# Install core dependencies
pip install -e .

# Install with perception support (requires PyTorch)
pip install -e ".[perception]"

# Install development dependencies
pip install -e ".[dev]"
```

## Usage

### Generate All Results

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output
```

Or using Make:

```bash
make results SEED=42 SCENES=50
```

This generates:
- `output/analysis_results.json` — Complete structured results
- `output/csv/` — CSV tables (coverage matrix, inconsistencies, gaps, weather evaluation)
- `output/latex/` — LaTeX tables ready for paper inclusion (Tables 1-8)
- `output/figures/` — All visualizations (GSN diagram, heatmaps, convergence diagram)
- `output/summary_report.txt` — Human-readable summary

See [REPRODUCING.md](REPRODUCING.md) for detailed reproduction instructions.

### Run Individual Components

```bash
# Five-step analysis (console output)
python -m src.analysis.run_analysis

# GSN diagram only
python -m src.visualization.gsn_renderer

# CARLA evaluation (synthetic mode)
python -m src.evaluation.run_evaluation --mode synthetic --seed 42

# Run tests
pytest tests/ -v
```

### Programmatic Usage

```python
from src.standards.registry import StandardsRegistry
from src.gsn.integrated_pattern import build_integrated_gsn
from src.analysis.inconsistencies import InconsistencyCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis

# Step 1-2: Standards framework
registry = StandardsRegistry()
coverage = registry.compute_coverage_matrix()     # Table 2
density = registry.compute_goal_density()          # Table 4

# Step 3: Build integrated GSN
gsn = build_integrated_gsn()
gsn.print_structure("G1")

# Step 4: Analyse inconsistencies
catalogue = InconsistencyCatalogue()               # Table 5
catalogue.print_catalogue()

# Step 5: Identify gaps
gaps = GapClassification()                         # Table 6
gaps.print_classification()

# Central finding: evidence convergence at G5
convergence = EvidenceConvergenceAnalysis()        # Figure 4
convergence.print_analysis()
```

## Tests

```bash
pytest tests/ -v --tb=short
```

Test coverage includes:
- Standards instantiation and claim extraction
- GSN construction and structural properties
- Inconsistency and gap classification
- Perception module (voxelization, IoU, divergence, AUROC)
- Weather condition generation and evaluation pipeline

## Applicable Standards

| Standard | Year | Scope | Role in Integration |
|----------|------|-------|-------------------|
| ISO 26262 | 2018 | Functional safety | ASIL framework, HW metrics, change management |
| ISO 21448 | 2022 | SOTIF | Four-area model, triggering conditions, acceptance criteria |
| ISO/SAE 21434 | 2021 | Cybersecurity | TARA, cybersecurity case, safety bridge [RQ-15-06] |
| ISO/PAS 8800 | 2024 | AI safety | **Base GSN pattern** (Annex B), AI-specific V&V, monitoring |
| ISO/IEC TR 5469 | 2024 | AI + functional safety | Supplementary guidance (informative) |

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

## Authors

- **Milin Patel** — Institute for Driver Assistance and Connected Mobility, Kempten University of Applied Sciences
- **Rolf Jung** — Faculty of Computer Science, Kempten University of Applied Sciences

## License

MIT License

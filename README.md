# Assurance Gaps in an Integrated Safety and Cybersecurity Case

**Assurance Gaps in an Integrated Safety and Cybersecurity Case for an AI-Based Perception Component in Highly Automated Driving**

Milin Patel and Rolf Jung — Kempten University of Applied Sciences
SafeComp 2026 WAISE Workshop — LNCS (Springer)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/blob/main/notebooks/assurance_gaps_analysis.ipynb)

---

## Motivation

When constructing a safety assurance case for an AI-based perception component in a highly automated vehicle (SAE Level 4+), practitioners must satisfy requirements from multiple standards simultaneously — ISO 26262 for functional safety, ISO 21448 for SOTIF, ISO/SAE 21434 for cybersecurity, and the newer ISO/PAS 8800 and ISO/IEC TR 5469 for AI-specific safety concerns.

These standards were developed independently and were not designed to work together. This repository investigates what happens when they are combined into a single integrated assurance argument: where do they conflict, where do they leave gaps, and what does that mean for the assessor who must decide whether the evidence is sufficient?

## What This Repository Does

This repository implements a **five-step constructive integration methodology** that:

1. **Extracts claims** from 52 clauses across 5 standards (40 normative claims)
2. **Maps claims** to 6 lifecycle phases, revealing coverage asymmetries
3. **Constructs an integrated GSN** extending ISO/PAS 8800 Annex B from 6 to 9 goals
4. **Analyses junction points** where standards overlap, identifying 7 requirement inconsistencies
5. **Classifies assurance gaps** — 6 total, of which 2 are integration-induced (invisible from any single standard)

A synthetic CARLA-based evaluation under 25 parametric weather conditions provides quantitative evidence for the identified gaps.

### Key Findings

| Finding | Detail |
|---------|--------|
| Requirement inconsistencies | 7 total: 3 structural, 2 terminological, 2 methodological |
| Assurance gaps | 6 total: 2 integration-induced |
| Central finding | Evidence type asymmetry at G5 — four incommensurable evidence types converge at the V&V goal, with no standard defining a combination rule |
| Triggering recall | 0.508 (vs 0.735 non-triggering) — 31% degradation under adverse weather |
| Triggering divergence | 0.555 (elevated ensemble uncertainty under SOTIF triggering conditions) |

## Repository Structure

```
├── src/
│   ├── standards/              # Step 1-2: Standards traceability framework
│   │   ├── base.py             # Data model (Standard, Clause, Claim, LifecyclePhase)
│   │   ├── iso26262.py         # ISO 26262:2018 — Functional safety
│   │   ├── iso21448.py         # ISO 21448:2022 — SOTIF
│   │   ├── iso21434.py         # ISO/SAE 21434:2021 — Cybersecurity
│   │   ├── iso8800.py          # ISO/PAS 8800:2024 — AI safety
│   │   ├── tr5469.py           # ISO/IEC TR 5469:2024 — AI + functional safety
│   │   └── registry.py         # Cross-standard query engine
│   │
│   ├── gsn/                    # Step 3: Goal Structuring Notation
│   │   ├── model.py            # GSN elements (Goal, Strategy, Context, Solution)
│   │   └── integrated_pattern.py  # Extends Annex B: 6 → 9 goals
│   │
│   ├── analysis/               # Steps 4-5: Gap and inconsistency analysis
│   │   ├── inconsistencies.py  # 7 requirement inconsistencies (Table 5)
│   │   ├── gaps.py             # 6 assurance gaps (Table 6)
│   │   ├── evidence_convergence.py  # Evidence convergence at G5 (Figure 4)
│   │   ├── traceability.py     # Goal-to-claim-to-gap traceability matrix
│   │   ├── sensitivity.py      # Multi-seed robustness analysis
│   │   └── run_analysis.py     # Five-step analysis runner
│   │
│   ├── perception/             # Case study: SECOND + deep ensemble
│   │   ├── voxelization.py     # LiDAR point cloud to voxel grid
│   │   ├── second_detector.py  # SECOND architecture (Yan et al., 2018)
│   │   └── deep_ensemble.py    # Geometric divergence uncertainty metric
│   │
│   ├── evaluation/             # CARLA evaluation under SOTIF triggering conditions
│   │   ├── weather_conditions.py   # 5×5 parametric weather grid
│   │   ├── carla_evaluator.py      # Evaluation pipeline (synthetic mode)
│   │   └── run_evaluation.py       # Evaluation entry point
│   │
│   ├── results/                # Publication output generation
│   │   ├── generate_all.py     # Master runner (JSON, CSV, LaTeX, figures)
│   │   ├── latex_tables.py     # Tables 1-8 (booktabs format)
│   │   └── export.py           # JSON, CSV, plain-text export
│   │
│   └── visualization/          # Figures and diagrams
│       ├── gsn_renderer.py     # GSN diagram via Graphviz (Figure 3)
│       └── coverage_plots.py   # Heatmaps, bar charts, convergence diagram
│
├── tests/                      # 95 tests across all modules
├── notebooks/                  # Interactive Jupyter/Colab notebook
├── configs/                    # YAML configuration (case study, standards)
├── data/
│   ├── carla_configs/          # Weather grid and detector configuration
│   └── sample_results/         # Reference outputs (seed=42)
├── docs/
│   ├── latex/                  # LaTeX sections for paper inclusion
│   └── figures/                # Reference figures (PNG)
├── Makefile                    # Reproducible build targets
├── REPRODUCING.md              # Step-by-step reproduction guide
└── pyproject.toml              # Package configuration
```

## Methodology

The five-step constructive integration process builds an integrated safety argument
starting from the ISO/PAS 8800 Annex B GSN pattern:

| Step | Input | Process | Output |
|------|-------|---------|--------|
| 1 | Standard clauses (52) | Claim extraction | 40 normative claims mapped to GSN goals |
| 2 | Claims + lifecycle phases | Phase mapping | Coverage matrix (5 standards × 6 phases) |
| 3 | Base GSN (Annex B, 6 goals) | Constructive extension | Integrated GSN (9 goals, 6 junction points) |
| 4 | Junction points | Inconsistency analysis | 7 inconsistencies (3S + 2T + 2M) |
| 5 | Inconsistencies + GSN | Gap identification | 6 gaps (2 integration-induced) |

### Integrated GSN (9 Goals)

| Goal | Description | Origin | Standards |
|------|-------------|--------|-----------|
| G1 | Integrated safety and cybersecurity requirements | Retained (reformulated) | ISO 26262, ISO 21448, ISO/SAE 21434 |
| G2 | Specification sufficiency | Retained | ISO/PAS 8800, ISO 21448, ISO/SAE 21434 |
| G3 | Data set sufficiency | Retained | ISO/PAS 8800 |
| G4 | Design sufficiency | Retained | ISO/PAS 8800, ISO 21448, ISO/SAE 21434 |
| G5 | V&V sufficiency | Retained | **All 4 normative standards** |
| G6 | Monitoring sufficiency | Retained | ISO/PAS 8800, ISO 21448, ISO/SAE 21434 |
| G7 | SOTIF residual risk acceptable | New | ISO 21448 |
| G8 | Cybersecurity risks managed | New | ISO/SAE 21434 |
| G9 | Modification and re-assurance | Undeveloped (gap) | None |

G5 is the critical node: it is the only goal where all four normative standards contribute claims, producing four fundamentally different evidence types with no defined combination rule.

## Case Study

**Component**: LiDAR-based 3D object detection for SAE Level 4+ automated driving

| Parameter | Value |
|-----------|-------|
| Detector architecture | SECOND (Yan et al., 2018) |
| Uncertainty method | Deep ensemble (5 members, geometric divergence) |
| ASIL classification | D (S3 × E4 × C3 from HARA) |
| Evaluation environment | CARLA 0.9.14, Town03 |
| Weather grid | 5 rain levels × 5 fog levels = 25 conditions |
| Scenes per condition | 50 (seed=42) |
| SOTIF triggering threshold | Rain > 20 mm/h OR visibility < 200 m |

## Installation

```bash
git clone https://github.com/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case.git
cd Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case

# Core installation
pip install -e .

# With development tools (pytest, ruff, black)
pip install -e ".[dev]"

# Optional: Graphviz for GSN diagram rendering
apt-get install graphviz  # or: brew install graphviz
```

## Usage

### Generate All Results

```bash
python -m src.results.generate_all --seed 42 --scenes 50 --output output
```

Or equivalently:

```bash
make results
```

This produces 33 output files:

| Directory | Contents |
|-----------|----------|
| `output/analysis_results.json` | Complete structured results (standards, GSN, inconsistencies, gaps, evaluation) |
| `output/summary_report.txt` | Human-readable summary of all findings |
| `output/csv/` | 5 CSV tables (coverage matrix, goal density, inconsistencies, gaps, weather evaluation) |
| `output/latex/` | 8 LaTeX tables ready for `\input{}` in papers (Tables 1-8, booktabs format) |
| `output/figures/` | 7 figure pairs (PNG + PDF) and GSN diagram (DOT + PNG + PDF) |

### Interactive Notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/blob/main/notebooks/assurance_gaps_analysis.ipynb)

The notebook walks through each methodology step with inline visualisations. It runs in Google Colab (installs dependencies automatically) or locally:

```bash
jupyter notebook notebooks/assurance_gaps_analysis.ipynb
```

### Run Individual Components

```bash
# Five-step analysis with console output
python -m src.analysis.run_analysis

# GSN diagram only
python -m src.visualization.gsn_renderer

# CARLA evaluation only
python -m src.evaluation.run_evaluation --mode synthetic --seed 42
```

### Programmatic API

```python
from src.standards.registry import StandardsRegistry
from src.gsn.integrated_pattern import build_integrated_gsn
from src.analysis.inconsistencies import InconsistencyCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis
from src.analysis.traceability import TraceabilityMatrix
from src.evaluation.carla_evaluator import generate_synthetic_evaluation

# Steps 1-2: Standards framework
registry = StandardsRegistry()
coverage = registry.compute_coverage_matrix()
density = registry.compute_goal_density()

# Step 3: Integrated GSN
gsn = build_integrated_gsn()

# Steps 4-5: Analysis
catalogue = InconsistencyCatalogue()
gaps = GapClassification()
convergence = EvidenceConvergenceAnalysis()
traceability = TraceabilityMatrix()

# Evaluation
result = generate_synthetic_evaluation(seed=42, num_scenes_per_weather=50)
summary = result.compute_summary()
```

## Tests

```bash
pytest tests/ -v
```

95 tests verify correctness across all modules:

| Test file | Count | Scope |
|-----------|-------|-------|
| `test_standards.py` | 14 | Standards instantiation, claim extraction, coverage matrix |
| `test_gsn.py` | 14 | GSN construction, junction points, undeveloped goals |
| `test_analysis.py` | 16 | Inconsistencies (7), gaps (6), evidence convergence (4 types) |
| `test_perception.py` | 15 | Voxelization, 3D IoU, geometric divergence, AUROC |
| `test_evaluation.py` | 10 | Weather grid, triggering conditions, evaluation pipeline |
| `test_results.py` | 15 | LaTeX tables, JSON/CSV export, summary report |
| `test_traceability.py` | 11 | Traceability matrix, sensitivity analysis |

## Standards Analysed

| Standard | Year | Domain | Role in Integration |
|----------|------|--------|-------------------|
| ISO 26262 | 2018 | Functional safety | ASIL assignment (HARA), structural coverage (MC/DC), change management |
| ISO 21448 | 2022 | SOTIF | Triggering conditions, four-area model, acceptance criteria |
| ISO/SAE 21434 | 2021 | Cybersecurity | TARA, penetration testing, cybersecurity-safety bridge (RQ-15-06) |
| ISO/PAS 8800 | 2024 | AI safety | **Base GSN pattern** (Annex B), AI-specific V&V, data sufficiency, monitoring |
| ISO/IEC TR 5469 | 2024 | AI + functional safety | Supplementary guidance on AI lifecycle within IEC 61508 framework |

## Reproducibility

All results are deterministic given the same random seed. See [REPRODUCING.md](REPRODUCING.md) for:
- Step-by-step reproduction instructions
- Complete output file listing
- Determinism verification procedure
- LaTeX integration guide

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

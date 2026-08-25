# Working Practices

Rules for anyone working in this repository, including the authors. They cover
what the repository is for, what may be written into it, and the checks that must
pass before a change is considered done.

## What this repository is

Supplementary material for academic papers on integrating cybersecurity into the AI safety
assurance argument for an AI-based LiDAR perception component in highly automated driving.
It is **not** a software product: the `src/` code exists to make the papers' claims
machine-checkable and reproducible, and `paper/` holds the LaTeX sources themselves.

There are **two papers** (see `paper/`), both by Patel & Jung, Kempten University:

- `paper/waise2026/` (LLNCS format) — the GSN integration pattern paper. The `src/` code
  backs *this* paper: the 9-goal integrated pattern, 7 decision points (DP-1 to
  DP-7 in the paper, I-1 to I-7 in the code), 5 findings (F-1 to F-5 in the paper,
  Gap-1 to Gap-5 in the code).
- `paper/safecomp2026-position/` (IEEEtran) — a position paper on the operational
  concern-assignment gap (assigning a runtime anomaly to SOTIF / AI-safety / cybersecurity).
  It is argued at the clause level and is not backed by the `src/` analysis code.

A poster is also in scope on this branch (`restructure/two-papers-plus-poster`).

## Commands

```bash
pip install -e ".[dev]"          # install (make install)
pytest tests/ -v --tb=short      # run all 203 tests (make test)
pytest tests/test_paper_claims.py -v                       # one file
pytest tests/test_paper_claims.py::TestGapClaims -v        # one class
pytest "tests/test_paper_claims.py::TestGapClaims::test_exactly_five_gaps" -v  # one test
python -m src.results.generate_all --seed 42 --scenes 50 --output output  # regenerate all outputs (make results)
python -m src.analysis.run_analysis   # five-step methodology with console output
black src tests && ruff check src tests   # format / lint (line-length 100, py39)
make gsn-install && make gsn      # render GSN YAML → SVG via gsn2x (Linux binary)
```

Note: `make gsn-install` downloads a **Linux** gsn2x binary; on Windows install gsn2x
manually. Graphviz is optional — `generate_all` warns and continues if PNG/PDF rendering
of the GSN diagram fails, still writing the `.dot` source.

## Architecture

The whole `src/` package is an executable encoding of the WAISE paper's five-step
"constructive integration" methodology. Data flows in one direction:

1. **Standards** (`src/standards/`) — one module per standard (`iso26262`, `iso21448`,
   `iso21434`, `iso8800`, `tr5469`), each a `Standard` (see `base.py`) holding hand-coded
   `Clause` and `Claim` objects. `registry.py`'s `StandardsRegistry` aggregates them and
   answers cross-standard queries (`compute_coverage_matrix`, `compute_goal_density`,
   `get_claims_for_goal`). This is Steps 1–2.
2. **GSN** (`src/gsn/`) — `model.py` is the GSN data model (`GSNArgument`, `Goal`,
   `Strategy`, `Context`, …). `integrated_pattern.py`'s `build_integrated_gsn()` constructs
   the 9-goal pattern by extending ISO/PAS 8800 Annex B (Step 3). This is the single source
   of truth for the argument structure in code.
3. **Analysis** (`src/analysis/`) — Steps 4–5 and validation. `decision_points.py`'s
   `DecisionPointCatalogue` holds the 7 **inconsistencies** (I-1…I-7); despite the file
   name, "decision points" and "inconsistencies" are the same objects (the file was
   renamed). `gaps.py`'s `GapClassification` holds the 5 gaps. `counterfactual.py`,
   `completeness.py`, `traceability.py`, `sensitivity.py`, `evidence_convergence.py` support
   the paper's secondary claims.
4. **Case study** (`src/perception/`, `src/evaluation/`) — the SECOND detector + deep
   ensemble and the CARLA weather evaluation. **The CARLA weather numbers are synthetic**:
   `evaluation/carla_evaluator.py::generate_synthetic_illustration()` never touches CARLA or
   a detector — it is a deterministic seeded function (seed=42). Do not present these as
   measurements.
5. **Results** (`src/results/`) — `generate_all.py` orchestrates the whole pipeline and
   writes JSON / CSV / LaTeX tables / figures to `output/`. `latex_tables.py` emits booktabs
   tables meant for `\input{}` into the paper.

### The paper↔code contract

`tests/test_paper_claims.py` is the contract: nearly every test docstring cites the exact
paper section, table, or figure it validates (e.g. "Section 4.2: G5 is the only node where
all four applicable standards contribute"). Load-bearing invariants the tests enforce:

- 9 goals total (6 retained from Annex B + 3 new/undeveloped); 2 contexts; 1 assumption.
- G5 is the only node where all 4 normative standards contribute (the "central finding", I-2).
- 7 inconsistencies = 3 structural + 2 terminological + 2 methodological.
- 5 gaps, of which exactly 2 (Gap-3, Gap-4) are integration-induced and invisible from any
  single standard.

**If you change a number in the paper, you must change the corresponding hard-coded value in
`src/` and its assertion in `test_paper_claims.py` together** — the three are kept in lockstep
by design. Run the test file after any such edit.

### Three-layer data separation (do not conflate)

`data/` is deliberately split, each layer with its own README documenting provenance:

- `data/synthetic_illustrations/` — deterministic seeded (seed=42) reference outputs of the
  analysis/evaluation pipeline. Illustrative, **not measurements**.
- `data/empirical_results/` — real measured AUROC and MDR/MFAR from a trained **PointPillars**
  deep ensemble on KITTI/nuScenes. **Neither paper cites these files** and no paper claim
  rests on them; they came from a separate runtime-monitoring project. The WAISE paper's
  own G5 evidence type (c) is the simulated VEHITS 2026 result instead. The paper text names
  SECOND as the case-study architecture; this data uses PointPillars (both OpenPCDet voxel
  single-stage detectors) — the substitution is stated in that README, not the paper.
- `gsn/*.gsn.yaml` — GSN argument in gsn2x YAML, the source of truth for the *rendered*
  figures (kept consistent with `build_integrated_gsn()` but separate from it).

## Conventions

- Python ≥3.9, `from __future__ import annotations` throughout; PEP 604-style hints.
- Deterministic by construction: same `--seed` must reproduce byte-identical output except
  for a `generated` timestamp (see REPRODUCING.md).
- The registry distinguishes `normative_standards` (excludes TR 5469) from `all_standards`;
  goal-density and "all four standards" claims count the four normative ones.

## Non-negotiable
- Accuracy over polish. Never state an unverified thing as fact. Write
  "unverified" and what would settle it.
- Never invent a citation, clause number, file path, result, or DOI.
- Do not change a computed number, threshold, or seed while doing structural work.
- Do not remove content without stating the justification first.
- Never update a reference output to make a failing test pass.
- Do not claim the repository proves anything the papers only argue.

## Terminology (must not drift)
- concern: one of the three assurance dimensions (SOTIF, AI safety, cybersecurity)
- concern label: the tag identifying which concern owns an anomaly
- one judgment: a single verdict on whether the assurance argument still holds
- one top claim: the root claim the argument supports
- assignment gap: no clause assigns an unlabeled runtime anomaly to a concern
- resolution gap: no clause resolves per-concern re-evaluations into one judgment

Use the papers' wording, not a paraphrase. Grep paper/ before inventing a phrasing.

## Decisions
Decide rather than asking. State the criterion used, and name the alternative
rejected and why. A decision with no stated criterion is subjective and is not
acceptable here. Where two options are equal on the criterion, pick the one a
reader can verify faster, and say so.

## Prose written into this repository
Applies to every README, comment, docstring, and commit message.

- No em-dashes. Parentheses or a full stop.
- Banned: comprehensive, novel, robust, significant, seamless, leverage, delve,
  crucial, key, powerful, cutting-edge, streamline, unlock, dive into,
  it is worth noting, in today's landscape.
- No sentence that restates its heading. No "This section explains".
- No tricolon padding ("faster, cleaner, and more maintainable").
- Vary sentence length. Uniform rhythm reads as generated.
- No bullet list where two sentences work.
- Scope claims exactly: "none of the four standards examined", not "no standard".
- A reader must be able to check every documented claim against a file in the
  repository. If they cannot, the claim does not belong in the docs.

## Visual and structural output
- One colour per standard (ISO 26262, ISO 21448, ISO/SAE 21434, ISO/PAS 8800),
  the same four across diagrams, the talk deck, and the poster. No fifth accent.
- Diagrams are generated from gsn/*.yaml at build time. Never hand-author node
  data into HTML or SVG.
- Anything reachable from the poster QR code must be readable on a phone in
  portrait at 380px in bright outdoor light. High contrast, no thin grey on white.
- No decorative element that carries no information.

## Working method
- Read symbols rather than whole files when working in src/ and tests/.
- Run review passes independently of each other, and independently of the work
  being reviewed. Record what each pass was asked to check.
- Verify by running the tests and Makefile targets, never by reasoning about
  what the code would do.

## Before declaring any phase done
Self-review as four readers and fix what each finds:
1. A domain expert checking the standards claims.
2. A first-time visitor arriving by phone from the poster.
3. A reviewer checking whether the repository supports what the papers claim.
4. A reader hunting for generated prose. Rewrite what they flag, do not delete it.

## Process
- Read before proposing. Propose before editing.
- Small commits, plain messages.
- Report findings in files, not in chat. In chat, at most ten lines naming the
  highest-severity items.

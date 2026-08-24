# Repository Audit

Read-only audit of the `assurance-gaps` repository on branch
`restructure/two-papers-plus-poster`, taken before any repair work began. Nothing
was changed except this file when it was written.

**Status.** This is a point-in-time record and is deliberately not rewritten as
findings are closed. `PROGRESS.md` logs what each iteration fixed. As of iteration
1, these findings are closed: the false "paper not included" line and the mangled
title (§8.1, §8.2), the `docs/` mislabelling (§8.3), the missing provenance READMEs
for `docs/figures/` and `data/carla_configs/` (§4, §8.8), the colliding generated
table labels (§3.4, §6.3), the inert-config drift risk (§2.1, now covered by
`tests/test_config_documentation.py`), the untracked tooling state (§1), and the
undeclared Windows gsn2x assumption (§7.3, now stated in the README). Iteration 1
also found a defect this audit missed: the camera-ready paper carries
classifications the code never absorbed (DP-2, F-1, F-2, F-3), described in
`PROGRESS.md`.

## Method and limits of verification

- `src/` and `tests/` were inspected with Grep for symbol signatures and hard-coded
  values, not read in full. Symbol-level tooling was unavailable in this session; Grep over raw file
  bytes was used instead.
- Full text was read for: `README.md`, `REPRODUCING.md`, `Makefile`, `pyproject.toml`,
  `gsn/*.gsn.yaml`, `configs/*.yaml`, both `data/*/README.md`, and both papers' `.tex`
  sources. The `.pdf` twins were not read; the `.tex` is treated as source of truth.
- The Read tool applied lossy stopword compression on larger reads (README, the
  empirical README, `configs/case_study.yaml` tails, parts of the GSN YAML and the
  paper). Where exact wording mattered it was re-checked with Grep on raw bytes.
  Items resting only on a compressed read are marked "unverified".
- `pytest` was not run. The claim "all 192 tests pass" is therefore unverified; the
  count of 192 test functions is verified (Grep `def test_` across `tests/` = 192).
- Empirical CSV/PDF contents were not opened row by row; their provenance rests on
  `data/empirical_results/README.md` only.

---

## 1. File inventory

Reachability key: **R** reachable from `README.md`, **M** from `Makefile`, **T** from a
test, **–** none found. Reachability means "named or imported", not "exercised".

### Top level
| Path | Purpose | Reach |
|---|---|---|
| `README.md` | Front-page description, structure, build/test/repro instructions | R |
| `REPRODUCING.md` | Step-by-step reproduction guide | R,M |
| `Makefile` | Build targets (install, test, results, figures, latex, gsn) | R |
| `pyproject.toml` | Package metadata, deps, entry-point scripts, pytest/ruff config | R |
| `.gitignore` | Ignore rules | – |

### `paper/`
| Path | Purpose | Reach |
|---|---|---|
| `paper/waise2026/CR_Submission_...HAD.tex` | WAISE 2026 GSN-integration paper (LLNCS), source of the DP/F/goal claims | – |
| `paper/waise2026/CR_Submission_...HAD.pdf` | Compiled twin of above | – |
| `paper/safecomp2026-position/CR_position_paper.tex` | SAFECOMP position paper (IEEEtran), concern-assignment gap | – |
| `paper/safecomp2026-position/CR_position_paper.pdf` | Compiled twin | – |

Neither paper is referenced by `README`, `Makefile`, or a test. README line 10 states
the paper is *not* included (see §8).

### `gsn/`
| Path | Purpose | Reach |
|---|---|---|
| `gsn/integrated_pattern.gsn.yaml` | Figure 2 GSN source (9 goals) for gsn2x | R,M |
| `gsn/evidence_convergence.gsn.yaml` | Figure 3 GSN source (G5 convergence) for gsn2x | R,M |

### `configs/`
| Path | Purpose | Reach |
|---|---|---|
| `configs/standards.yaml` | Five standards + clauses, hand-written | R only |
| `configs/case_study.yaml` | Case-study params (SECOND, HARA, TARA, ensemble) | R only |

Neither config is loaded by any code or test (Grep for `configs`, `yaml.load`,
`yaml.safe_load` in `src/` and `tests/` = no matches). They are a parallel,
unsynchronised copy of data that is hard-coded in `src/standards/*.py` and
`src/evaluation/`. See §2 and §3.

### `src/standards/` (Steps 1–2)
| Path | Purpose | Reach |
|---|---|---|
| `base.py` | `Standard`, `Clause`, `Claim` data model | T (via registry) |
| `iso26262.py` `iso21448.py` `iso21434.py` `iso8800.py` `tr5469.py` | One hand-coded `Standard` each | T |
| `registry.py` | `StandardsRegistry`; coverage matrix, goal density, claims-for-goal | R,M,T |

### `src/gsn/` (Step 3)
| Path | Purpose | Reach |
|---|---|---|
| `model.py` | GSN data model (`GSNArgument`, `Goal`, `Strategy`, `Context`, …) | T |
| `integrated_pattern.py` | `build_integrated_gsn()`; 9-goal pattern (code source of truth) | M,T |

### `src/analysis/` (Steps 4–5 and secondary claims)
| Path | Purpose | Reach |
|---|---|---|
| `decision_points.py` | `DecisionPointCatalogue`; 7 inconsistencies I-1..I-7 | M,T |
| `gaps.py` | `GapClassification`; 5 gaps Gap-1..Gap-5 | M,T |
| `evidence_convergence.py` | 4 evidence types / 3 paths converging at G5 | M,T |
| `counterfactual.py` | Which gaps vanish under single-standard views | M,T |
| `completeness.py` | GSN completeness check (G9 undeveloped) | M,T |
| `traceability.py` | Gap→goal traceability map | T |
| `sensitivity.py` | Multi-seed synthetic evaluation (seeds 42,123,256,512,1024) | M,T |
| `base_pattern_sensitivity.py` | Which findings survive base-pattern changes | T |
| `generalisability.py` | Finding-generalisability classification (uses `finding_id=I-*`) | T |
| `practitioner_guidance.py` | Per-gap practitioner guidance | T |
| `run_analysis.py` | Console runner for the five-step method | R (entry point) |

### `src/perception/` (case study)
| Path | Purpose | Reach |
|---|---|---|
| `second_detector.py` `deep_ensemble.py` `voxelization.py` | SECOND + deep-ensemble model code (needs `torch`) | T |

Not imported by `generate_all.py`; reachable only from `tests/test_perception.py`.

### `src/evaluation/`
| Path | Purpose | Reach |
|---|---|---|
| `carla_evaluator.py` | `generate_synthetic_illustration()` (seeded, no CARLA) | M,T |
| `weather_conditions.py` | Weather grid + triggering-coverage helpers | M,T |
| `run_evaluation.py` | Console runner for the ensemble/weather eval | R (entry point) |

### `src/results/`
| Path | Purpose | Reach |
|---|---|---|
| `generate_all.py` | Pipeline orchestrator; writes JSON/CSV/LaTeX/figures | R,M |
| `latex_tables.py` | `generate_table1..8`; booktabs tables | M (via generate_all) |
| `export.py` | JSON/CSV/summary-report writers | M (via generate_all) |

### `src/visualization/`
| Path | Purpose | Reach |
|---|---|---|
| `gsn_renderer.py` | GSN → Graphviz `.dot`/PNG | R, M (lazy import in generate_all) |
| `coverage_plots.py` | Matplotlib heatmaps/bar charts | M (lazy import) |

### `tests/` (192 `def test_`)
`test_standards.py` (14), `test_gsn.py` (14), `test_analysis.py` (16),
`test_extended_analysis.py` (27), `test_paper_claims.py` (61), `test_perception.py`
(15), `test_evaluation.py` (10), `test_results.py` (15), `test_sensitivity_extended.py`
(9), `test_traceability.py` (11). All R,M via the test target.

### `data/synthetic_illustrations/` (seed=42, with README)
`decision_points.csv`, `gaps.csv`, `summary_report_seed42.txt`,
`weather_evaluation_seed42.csv` — all regenerable by `generate_all` (committed
snapshots). `README.md` states provenance. Reach: R.

### `data/empirical_results/` (measured, with README)
`controlled_experiment/` (5 CSV), `kitti_v2_evidence/` (2 CSV + 2 PDF),
`nuscenes_evidence/` (3 CSV), `three_way_comparison/` (2 CSV + 5 PDF), `README.md`.
Reach: R. Not regenerable in this repo (see §7).

### `data/carla_configs/`
`detector_config.yaml`, `weather_grid.yaml` — hand-written, **not loaded by any code
or test**, **no README**. Reach: –.

### `docs/figures/`
`integrated_gsn.png`, `coverage_heatmap.png`, `evidence_convergence.png`,
`weather_heatmap.png` — committed image snapshots, **no provenance README**, not
`\includegraphics`-d by either paper. Reach: R (structure tree only).

### `notebooks/`
`assurance_gaps_analysis.ipynb` — Colab notebook. Reach: R (Colab badge + tree).

### Untracked tooling state (git status `??`)
Local editor and tooling state directories. Not repository content. Reach: –.
Now covered by `.gitignore` (iteration 1).

---

## 2. Dead weight (nothing in the executable pipeline references it)

1. **`configs/standards.yaml`, `configs/case_study.yaml`** — not loaded by `src/` or
   `tests/` (verified: no `configs`/`yaml.load` matches in either tree). The data they
   hold is separately hard-coded in `src/standards/*.py` and `src/evaluation/`. They
   read as configuration that drives the analysis but do not.
2. **`data/carla_configs/detector_config.yaml`, `weather_grid.yaml`** — not loaded by
   any code or test; `carla_evaluator.generate_synthetic_illustration()` uses its own
   hard-coded parameters. No README.
3. **`docs/figures/*.png`** — four committed PNG snapshots not included by either paper
   and regenerated (to `output/figures/`) by `generate_all`. Duplicate of generated
   output; no provenance statement (§3, §4).
4. **`src/perception/*` (`second_detector`, `deep_ensemble`, `voxelization`)** — not
   used by `generate_all` or by any produced artefact; exercised only by
   `tests/test_perception.py`. Pulls in the heavy `torch` dependency for code that
   backs no paper number (the empirical evidence comes from an external PointPillars
   run, not this code).
5. **Local tooling state directories** — untracked, now ignored via `.gitignore`.

Not dead but worth noting: the `output/` directory does not exist in the tree; all
`output/*` paths are generated on `make results`.

---

## 3. Duplication (same number/table/figure produced in more than one place)

1. **GSN argument structure — four representations.**
   (a) `gsn/integrated_pattern.gsn.yaml`, (b) `src/gsn/integrated_pattern.py`
   `build_integrated_gsn()`, (c) hand-drawn TikZ in the WAISE `.tex`
   (`\node[goal] (G5) …`), (d) `docs/figures/integrated_gsn.png` +
   `output/figures/`. docs/working-practices.md names (a) and (b) as two separate "sources of truth"
   kept consistent by hand. The paper's TikZ (c) is hand-authored node data, which
   docs/working-practices.md's visual-output rule forbids for repo diagrams; whether papers are exempt
   is not stated.
2. **Standards/case-study data — YAML vs Python.** `configs/standards.yaml` duplicates
   the clause data in `src/standards/*.py`; `configs/case_study.yaml` duplicates the
   HARA/TARA/ensemble parameters used in code. Two unsynchronised copies (§2.1).
3. **`decision_points.csv` and `gaps.csv`** exist both as committed files under
   `data/synthetic_illustrations/` and as regenerated `generate_all` outputs.
4. **LaTeX tables — generated vs hand-authored, and drifted.** `latex_tables.py`
   emits `table5_inconsistencies` (caption "Requirement inconsistencies",
   `\label{tab:inconsistencies}`) and `table6_gaps` (caption "Assurance gaps",
   `\label{tab:gaps}`). The WAISE paper hand-authors tables with the same labels but
   different content ("Decision points" DP-1..DP-7; "Integration-induced findings and
   open methodological problems" F-1..F-5). The paper `\input`s no generated table
   (Grep for `\input`/`includegraphics` in the `.tex` = no matches). So the generated
   tables are a second, stale copy (see §6).
5. **`docs/figures/*.png` vs `output/figures/*.png`** — same four figures, committed
   snapshot vs generated.

---

## 4. Provenance per artefact

| Artefact group | Provenance | Stated in its own file? |
|---|---|---|
| `data/synthetic_illustrations/*` | seeded-synthetic (seed=42) | Yes — directory README |
| `data/empirical_results/*` | measured (PointPillars ensemble, KITTI/nuScenes) | Yes — directory README |
| `gsn/*.gsn.yaml` | hand-written | Header comments describe role, not provenance label; adequate |
| `configs/*.yaml` | hand-written | No README; type is self-evident but role (unused) is not |
| `data/carla_configs/*.yaml` | hand-written | **No provenance statement** — FLAG |
| `docs/figures/*.png` | seeded-synthetic (matplotlib from analysis) | **No provenance statement** — FLAG |
| `notebooks/*.ipynb` | derived code | Not stated | 
| `src/**` | hand-written code | n/a |
| `output/**` (on build) | mixed (deterministic analysis + seeded synthetic) | Generated; `summary_report` labels the CARLA section synthetic |

**Provenance flags (own file does not state it):**
- `data/carla_configs/detector_config.yaml`, `weather_grid.yaml` — no README; a reader
  cannot tell these are unused hand-written stubs.
- `docs/figures/*.png` — no README in `docs/`; a reader cannot tell whether these are
  measured or seeded, or how to regenerate them. README calls `docs/` "LaTeX sections
  and reference figures" (there are no LaTeX sections; §8).
- `notebooks/assurance_gaps_analysis.ipynb` — provenance/derivation not stated in-file
  (unverified: notebook body not read).

---

## 5. Claim coverage, split by paper

### WAISE 2026 paper (`paper/waise2026/…HAD.tex`) — code-backed

| Paper claim | Supporting artefact (file · function) |
|---|---|
| Extends ISO/PAS 8800 Annex B from 6 to 9 goals | `src/gsn/integrated_pattern.py::build_integrated_gsn`; asserted `test_paper_claims.py::test_extends_annex_b_from_six_to_nine_goals` |
| 2 context nodes (C1, C2), 1 assumption (A1.4) | same builder; `test_adds_two_context_nodes`, `test_retains_one_assumption` |
| G5 is the only node where all four standards contribute (central finding = DP-2) | builder + `src/analysis/decision_points.py` (I-2); `test_g5_only_node_all_four_standards`, `test_i2_central_finding` |
| G5 has 4 evidence types / 3 analysis paths converge | `src/analysis/evidence_convergence.py`; `test_four_evidence_types_at_g5`, `test_failure_event_three_analysis_paths` |
| G9 is the only undeveloped goal | builder + `src/analysis/completeness.py`; `test_g9_is_only_undeveloped_goal` |
| 7 decision points (paper DP-1..7) = 3 structural + 2 terminological + 2 methodological | `src/analysis/decision_points.py::DecisionPointCatalogue` (I-1..I-7); `test_exactly_seven_inconsistencies`, `test_three_structural_two_terminological_two_methodological` |
| 5 findings (paper F-1..5), exactly 2 integration-induced (F-3, F-4) | `src/analysis/gaps.py::GapClassification` (Gap-1..5; Gap-3/Gap-4 integration-induced); `test_exactly_five_gaps`, `test_exactly_two_integration_induced` |
| Findings invisible from a single standard | `src/analysis/counterfactual.py`; `tests/test_extended_analysis.py` (unverified in detail) |
| Coverage matrix / goal density per node | `src/standards/registry.py::compute_coverage_matrix`, `compute_goal_density`; `tests/test_standards.py` |
| Weather/SOTIF evaluation table | `src/evaluation/carla_evaluator.py::generate_synthetic_illustration` → `latex_tables.py::generate_table8_weather_evaluation` — **seeded-synthetic; not a measurement** |
| Empirical AUROC / MDR-MFAR at G5/G6 | **no in-repo generator**; measured files under `data/empirical_results/` produced by an external PointPillars run (§7) |

Label mismatch between paper and code is systematic; see §6.

### SAFECOMP 2026 position paper (`…/CR_position_paper.tex`) — argued in text only

By design this paper is argued at the clause level and is **not** backed by `src/`.
Reported as a scope fact, not a finding:

| Position-paper claim | Artefact |
|---|---|
| Runtime anomaly carries no concern label | no artefact, argued in text only (Fig. 1 TikZ) |
| Assignment gap = missing step 1 (no clause assigns a concern) | no artefact, argued in text only |
| Resolution gap = missing step 2 (no clause resolves per-concern re-evaluations into one judgment) | no artefact, argued in text only |
| Per-concern standard clauses (e.g. ISO 21448 Cl.13.4) map result→argument | no artefact; hand-authored clause table |

No numeric claim in the position paper depends on `src/`. This is expected.

---

## 5b. Two findings from the derivation work (added after this audit was written)

Both are kept as evidence about how far these claims can be derived. Neither is a
failed attempt to be deleted.

### 5b.1 A derivation probe that disagreed with the published claim

An attempt to derive, rather than assert, which findings are invisible from a
single standard produced **{Gap-2, Gap-3}** against the published **{Gap-3,
Gap-4}**. The divergence traced to the probe's rule, not to the paper.

The rule was: an assessor applying standard S sees only goals that S sources, so
a gap is visible to S only if S sources every goal the gap occupies. It failed in
two distinct ways.

- **Gap-4 came out visible from all four.** G5 is sourced by all four standards,
  so under that rule every standard "sees" G5. But F-4 is about no standard
  requiring that per-domain assessments be *combined*. A single-standard assessor
  at G5 holds one evidence strand and cannot pose a combining question at all.
  The rule tested presence at a node where the claim concerns plurality at a node.
- **Gap-2 came out invisible from all.** G9 carries no `source_standards`, because
  it is the undeveloped goal. That empty list means "no standard fully covers
  this", not "no assessor could notice it". ISO 26262 and ISO/PAS 8800 each hold a
  claim at G9, and ISO/PAS 8800 Cl.14.8.3 by itself shows re-approval is partial.

What survived is narrower and now implemented in `counterfactual.py`: Gap-3 is
derived outright, Gap-4 is derived from a plurality premise stated as a premise,
and Gap-1, Gap-2 and Gap-5 are documented as asserted. The reason the other three
cannot be derived is that no machine-readable field records whether a single
standard's own text exhibits a deficiency alone, and adding one would relocate the
assertion rather than remove it.

### 5b.2 Two views of the argument had drifted, and the drift reached a published claim

The repository writes down "which standards contribute to which goal" twice: as
`source_standards` on each goal in `build_integrated_gsn()`, and as `gsn_goal` on
each `Claim`. Nothing held them together, and they disagreed at three goals.

The consequence was not cosmetic. `CLM-26262-TSC-01` ("A technical safety concept
shall be derived from the functional safety concept") carried `gsn_goal="G2"`,
which made **G2 report all four standards under `compute_goal_density()`**. The
paper's central structural claim is that G5 is the only such node. The claim
survived only because `test_g5_only_node_all_four_standards` reads
`source_standards`, where G2 stood at three. One clause assignment decided a
published claim, which is exactly the objection recorded in
`passes/04_adversarial_critic.md`.

**Resolution: the claim was out of scope, not mis-placed.** The clause evidence,
read by the authors from ISO 26262-4:

- Cl.6.2 defines the technical safety concept as the technical safety
  requirements together with the system architectural design.
- Cl.6.4.3.1 bases it on the item definition, the functional safety concept and
  the prior system architectural design.
- Cl.6.4.6.1 allocates technical safety requirements to system, hardware or
  software as the implementing technology.
- Cl.6.5 lists work products spanning specification (6.5.1), the technical safety
  concept (6.5.2) and architectural design (6.5.3), so Clause 6 is not a
  specification-only clause.
- Cl.6.3.1 makes the functional safety concept a prerequisite input produced
  under ISO 26262-3.

That activity belongs to the encompassing system safety case (ISO 26262-2
Cl.6.4.8), above the AI component this pattern is scoped to. Neither G2 nor G4
declares ISO 26262 as a source, both matching the paper's Table 2, and the
clause's own `ai_applicability_note` records that decomposition to software units
does not hold for network weights.

An intermediate move of the claim from G2 to G4 was tried and reverted: it
relocated the all-four count to G4 rather than removing it.

**What changed.** The claim is kept in `iso26262.py` with `gsn_goal=None` and a
new `out_of_scope_reason` field carrying the clause evidence, so the obligation
stays visible while staying out of the argument. Its clause reference was
narrowed from "Part 4, Cl.6" to "Part 4, Cl.6.4.3", recording Cl.6.5.2 as the
work product. The claim text was not touched. `check_gsn_completeness()` now
separates deliberate exclusions from unmapped claims, so the paper's "all
extracted claims map to GSN nodes" invariant keeps its real meaning rather than
being weakened to pass.

**Result.** G5 is now the only all-four node under *both* views. The two views
agree at seven of nine goals; G8 and G9 differ for reasons now recorded as
explicit exceptions (G8 lists ISO 26262 for the RQ-15-06 bridge, carried by an
ISO/SAE 21434 claim; G9 is undeveloped yet holds the partial-coverage claims for
F-2).

**Prevention.** `tests/test_representation_consistency.py` (13 tests) holds the
two views to each other, requires every exception to state a reason, requires an
exception to be deleted once it no longer applies, checks claim phase against
goal for the five single-phase goals, and asserts G5's uniqueness under both
views. Re-introducing the original assignment in memory makes both checks fail,
so they are not vacuous.

## 6. Lockstep integrity (src ↔ test ↔ paper)

**The numbers are in lockstep; the labels are not.**

Every hard-coded count in `src/` is asserted in `test_paper_claims.py` and matches the
current WAISE text:

| Quantity | src value | test assertion | paper text | Match |
|---|---|---|---|---|
| Total goals | 9 (builder) | `== 9` | "6 to 9 goals" | ✓ |
| Retained goals | 6 | `== 6` | Annex B G1–G6 | ✓ |
| Contexts / assumptions | 2 / 1 | `== 2` / `== 1` | C1,C2 / A1.4 | ✓ |
| Node with all 4 standards | G5 only | `test_g5_only_node…` | "G5 is the node where all the applicable standards contribute" | ✓ |
| Decision points | 7 | `== 7` | DP-1..DP-7 | ✓ |
| Structural/terminological/methodological | 3/2/2 | `3/2/2` | prose DP-1,2,5 / DP-3,4 / DP-6,7 | ✓ |
| Findings/gaps | 5 | `== 5` | F-1..F-5 | ✓ |
| Integration-induced | 2 (Gap-3, Gap-4) | `{"Gap-3","Gap-4"}` | F-3, F-4 (II) | ✓ |

**Drift found (labels/terminology, not values):**

1. **Prefix drift I-→DP- and Gap-→F-.** Code and generated LaTeX use `I-1..I-7`
   (`inconsistency_id`) and `Gap-1..Gap-5` (`gap_id`); the camera-ready paper uses
   `DP-1..DP-7` and `F-1..F-5`. The mapping is 1:1 by number (I-2 = DP-2 = central G5
   finding; Gap-3/Gap-4 = F-3/F-4 = integration-induced). README uses a third mix
   ("7 decision points", "5 assurance gaps"). A reader cross-referencing the paper's
   `DP-5` to the repo finds `I-5`, and `F-3` to `Gap-3`, with no crosswalk documented.

2. **Category-taxonomy drift.** `gaps.py` classifies by `gap_type`
   (`MISSING_CLAIM` ×2, `MISSING_EVIDENCE` ×2, `UNRESOLVED_INCONSISTENCY` ×1), and
   `test_gap_type_counts_match_table6` asserts these against "Table 6". The
   camera-ready paper's `tab:gaps` no longer uses that taxonomy; it uses
   `II` / `OM` (integration-induced finding / open methodological problem, 2/3). The
   test's cited "Table 6" taxonomy does not appear in the current paper.

3. **Generated LaTeX tables are stale.** `latex_tables.py::generate_table5/6` emit
   captions "Requirement inconsistencies" / "Assurance gaps" under labels
   `tab:inconsistencies` / `tab:gaps` — the paper's own labels — but with the old
   terminology and taxonomy. If anyone `\input`s them they collide with the
   hand-authored tables. Currently the paper `\input`s nothing, so the drift is latent.

4. **DP-2 dual type.** Paper `tab:inconsistencies` tags DP-2 as "S, M" (structural
   *and* methodological); the code counts I-2 as structural only, and the prose groups
   DP-2 under structural. The 3/2/2 split holds only because DP-2 is counted once. Not
   a value error, but the table's "S, M" is not represented in the code's single-type
   count. (Verified against the paper table; the code's type field was read via Grep.)

5. **GSN YAML uses `Gap-2`.** `gsn/integrated_pattern.gsn.yaml` G9 text says
   "[UNDEVELOPED - Gap-2]"; the paper ties G9 to finding **F-2** (OTA re-assurance).
   Same number, old prefix — consistent with the prefix drift above.

No case was found where the three disagree on a *value*. All drift is nominal
(labels/terminology/captions).

---

## 7. Reproducibility blockers

1. **Empirical results are not reproducible from this repo.** `data/empirical_results/`
   is presented as measured PointPillars/deep-ensemble output, but its README states
   the training and evaluation scripts are part of an unpublished paper "P5" and will
   be cited "once P5 is published". No training code, no raw KITTI/nuScenes data, and
   no command sequence are in the repo. The G5/G6 empirical claims cannot be
   independently regenerated here. (Verified from the empirical README; some detail
   rests on a compressed read.)
2. **Unpinned dependencies.** `pyproject.toml` pins only lower bounds
   (`numpy>=1.24`, `torch>=2.0`, `matplotlib>=3.7`, `pandas>=2.0`, …). "Byte-identical
   output for the same seed" (REPRODUCING.md, docs/working-practices.md) is not guaranteed across
   dependency upgrades; float formatting and RNG streams can move. No lockfile.
3. **Platform assumption in `make gsn-install`. Gate 3 violation, now closed.**
   The target downloaded the **Linux** gsn2x binary unconditionally, on every
   platform, producing a file that cannot run on the stated Windows host. The
   README and `docs/working-practices.md` told the reader to install manually, but
   the target itself stayed Linux-only, so "one command from a clone" was false off
   Linux. It now detects the platform and selects `gsn2x-Windows.exe`,
   `gsn2x-macOS`, or `gsn2x-Linux`. Those three asset names were read from the
   v4.2.3 release listing rather than guessed. Two caveats recorded rather than
   glossed: `make` is not installed on the development host, so the edited target
   has not been executed, and what would settle that is running it on each platform
   or in CI; and the gsn2x actually installed here is 4.3.1 while the target pins
   4.2.3, so the pinned version is not the one these diagrams were rendered with.
4. **`torch>=2.0` required to install the dev/test set.** The perception tests import
   torch though no paper number depends on that code (§2.4). A reviewer reproducing
   only the paper claims still pays the torch install cost.
5. **No runtime network calls in `src/`** (Grep for `requests`/`urllib`/`http`/socket =
   none). Randomness is seeded via `np.random.RandomState(seed)` with a fixed default
   seed=42 and an explicit multi-seed list. No absolute paths in `src/` (Grep for
   drive letters / `/home/` / `/Users/` = none). These are clean.
6. **Missing data for the synthetic path is not a blocker** — the synthetic
   illustration is self-contained and deterministic.

---

## 8. Reader-facing problems (a SAFECOMP reviewer would flag)

1. **README says the paper is not in the repo, but it is.** Line 10 (raw bytes):
   "The paper itself published separately not included in repository." `paper/`
   contains the camera-ready `.tex` and `.pdf` for **both** papers (added in commit
   cf460… "Add camera-ready sources for both papers"). The statement is false on this
   branch, and the README describes one paper while two exist.
2. **README title/intro have dropped words.** Line 1 / line 5 (raw): "…Assurance
   Argument: GSN Pattern AI-Based Perception Components…" — missing "A" and "for"
   versus the paper's real title. Line 10 is also ungrammatical ("published separately
   not included"). Reads as machine-stripped prose; conflicts with docs/working-practices.md's own
   prose rules.
3. **`docs/` is mislabelled.** README structure calls it "LaTeX sections and reference
   figures"; `docs/` contains only four PNGs and no LaTeX. The figures are not used by
   either paper.
4. **Terminology split will confuse cross-referencing.** README says "7 decision
   points" and "5 assurance gaps"; the paper says decision points **DP-N** and
   integration-induced findings / open methodological problems **F-N**; the code says
   inconsistencies **I-N** and gaps **Gap-N**. Three vocabularies for two object sets,
   no crosswalk (§6.1).
5. **`configs/` looks load-bearing but is inert.** README lists `configs/` as "YAML
   configuration"; nothing reads it (§2.1). A reviewer editing `configs/case_study.yaml`
   (e.g. epochs, voxel size) would see no effect and could reasonably assume the
   analysis is misconfigured.
6. **Empirical evidence is asserted but unverifiable in-repo (§7.1).** The empirical
   README is candid about the PointPillars-for-SECOND substitution and the FN-frame
   AUROC ≈ 0.55 ceiling, which is good. But a reviewer cannot check any empirical
   number against a runnable artefact; the honest framing does not remove the
   unverifiability.
7. **`make gsn` on the documented Windows host will fail out of the box** (§7.3),
   despite README/Makefile presenting `make gsn-install && make gsn` as the path.
8. **Missing provenance READMEs** for `docs/figures/` and `data/carla_configs/`
   (§4). docs/working-practices.md's own rule — "a reader must be able to check every documented claim
   against a file" — is unmet for these directories.

Positives worth recording: the synthetic-vs-empirical separation is clearly documented
and enforced in code (`generate_synthetic_illustration` is unmistakably seeded and
CARLA-free); the numeric lockstep between `src/` and `tests/` is intact; and the
position paper's text-only scope is appropriate and correctly not backed by `src/`.

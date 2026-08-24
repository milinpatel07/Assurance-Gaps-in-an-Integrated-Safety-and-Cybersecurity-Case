# Iteration 1 review — standards practitioner

Scope reviewed: `README.md` (diff), `src/results/latex_tables.py` (diff, captions/labels of
generated Tables 5 and 6), `docs/figures/README.md` (new), `data/carla_configs/README.md` (new).
Ground truth: `paper/waise2026/CR_Submission_WAISE_SafeCompAssuranceGaps_SafetySecurityCase_AI_Perception_HAD.tex`
(tab:inconsistencies at ~line 401, tab:gaps at ~line 442) and
`paper/safecomp2026-position/CR_position_paper.tex`, plus `src/analysis/decision_points.py`,
`src/analysis/gaps.py`, `src/standards/iso21448.py`, `src/evaluation/weather_conditions.py`,
and git history.

## Verdict

The scope-fidelity repair is largely accurate. The two-paper description in README.md is
correct, the new caption text is truthful about what it claims, and every clause reference I
checked in the changed material matches either the paper or the code it points at. However,
the captions' blanket correspondence claim ("I-n are the code's names for DP-n", "Gap-n are
the code's names for F-n") silently papers over three field-level divergences between the
code and the camera-ready paper, and two of those divergences appear in printed columns of
the generated tables. Those should be fixed in code or disclosed in the caption.

## Findings (severity-ranked)

### MAJOR

**M1. Generated Table 5 contradicts the paper on DP-2's type.**
`src/analysis/decision_points.py` I-2 ("Evidence type asymmetry at V&V") has
`inconsistency_type=STRUCTURAL` only, so the generated table prints Type `S`. The paper's
tab:inconsistencies row DP-2 gives Type **"S, M"** (structural *and* methodological; line 410).
The Type column is printed in the generated table, so the artifact the caption says
corresponds to DP-2 disagrees with the paper's own row. Either the code's type set for I-2
should carry both types, or the caption must disclose the delta.

**M2. Generated Table 6 contradicts the paper on F-3's lifecycle phase.**
Code Gap-3 has `lifecycle_phase=VERIFICATION`; the paper's tab:gaps row F-3 gives
**"Verification, Operation"** (line 450). Phase is a printed column of the generated table.
Same remedy as M1.

**M3. Generated Table 6 contradicts the paper on F-1's lifecycle phase.**
Code Gap-1 has `lifecycle_phase=VERIFICATION`; the paper's F-1 row gives
**"Concept, Verification"** (line 453, added in camera-ready `\crev`). Same remedy as M1.

All three are camera-ready paper revisions the code never absorbed. Per docs/working-practices.md's lockstep
rule ("If you change a number in the paper, you must change the corresponding hard-coded
value in src/"), the code fields are stale; the new captions assert correspondence without
qualification, which is now the overstated statement.

### MINOR

**m1. Gap-2 / F-2 partial coverage omits ISO 24089.** The camera-ready tab:gaps F-2 row and
the F-2 body text add ISO 24089 ("specifies the software-update engineering process but not
the re-assurance of a modified AI model's safety argument"). Code Gap-2's `partial_coverage`
lists only 26262-8 Cl.8, 8800 Cl.14.8.3, TR 5469 Table A.8. Not printed in the generated
table, so no visible contradiction, but it is code-vs-paper drift of the same kind as M1-M3.

**m2. Description wording drift, undisclosed.** Generated descriptions come from the code and
no longer match the softened camera-ready titles: I-1 "Incompatible risk classification
frameworks" vs paper DP-1 "Risk classification across three frameworks" (the paper
deliberately says the frameworks are "not interchangeable by design", not "incompatible" —
the code wording is stronger than the paper now claims); Gap-1 "No AI-specific quantitative
reliability target" vs F-1 "Quantitative acceptance criteria for AI components"; Gap-2 "No
complete OTA re-assurance workflow for AI" vs F-2 "OTA re-assurance workflow (partial
coverage)". A one-line caption note ("descriptions follow the code and may differ in wording
from the paper's revised titles") would cover this honestly.

**m3. `data/carla_configs/README.md` leaves the YAML's ISO 21448 misattribution standing.**
The new README itself makes no clause claim (good) and correctly presents 20 mm/h / 200 m as
case-study thresholds verified against `WeatherCondition.from_physical_parameters()` (the
21 triggering / 4 non-triggering split checks out against the code's strict `> 20` / `< 200`).
But the file it documents, `weather_grid.yaml`, asserts the thresholds are "per ISO 21448
Cl.7 definition of performance-limiting conditions". That is wrong on three counts: ISO 21448
defines no numeric thresholds anywhere; "performance-limiting conditions" is not the
standard's term (it uses "triggering condition" / "functional insufficiency", defined in
Clause 3, not Clause 7); and Cl.7 is the identification-and-evaluation activity (the repo's
own `iso21448.py` titles Cl.7 "Identification of hazardous scenarios and triggering
conditions"). Since this README's stated purpose is to gloss these YAMLs for readers, it
should add one sentence saying the thresholds are project-specific choices, not values from
ISO 21448, notwithstanding the YAML comment. (The YAML itself is pre-existing and outside
this change; its inline comments also mislabel 25 mm/h and 200 m as "the SOTIF triggering
threshold" — 200 m visibility is *non*-triggering under the code's strict inequality.)

**m4. `data/carla_configs/README.md` internal tension in the "Used by" column.** The row
"Ensemble size, epochs" lists `configs/case_study.yaml` under "Used by", two paragraphs
before the README states that `configs/*.yaml` "are documentation in the same sense, and are
likewise not loaded". Verified: nothing in `src/` or `tests/` reads `configs/case_study.yaml`
or `configs/standards.yaml`, so the root README's "no code loads them" is true and the
"Used by" entry is the misleading one. Drop it or reword to "documented also in".

### ADVISORY

**a1. "Both are published through their venues"** (README.md line 19) is not verifiable from
the repository and may be premature for 2026 venues; "the copies here are the accepted
sources" is supported. Consider "accepted for publication".

**a2. Terminology drift inside README.md.** The new top-of-file bullets correctly use the
camera-ready vocabulary ("seven decision points, the five findings"), but the untouched
Overview paragraph still says "classifies 5 assurance gaps — 2 of which are only visible
through constructive integration". The count and the II/OM split (F-3, F-4) are correct;
only the noun is the pre-revision one. Harmless but inconsistent within one file.

**a3. "removed one test (commit 4d782b0)"** is net-accurate but literally the commit removed
five test functions and added four (verified: 193 test functions at `4d782b0^`, 192 at
`4d782b0`). "reduced the suite by one test" would be exact.

## Checks that passed (no action)

- **Two-paper description (README.md):** WAISE = GSN integration paper, LLNCS, backed by
  `src/`; Annex B extended 6 → 9 goals (paper: G2-G6 retained, G7-G9 added); seven decision
  points DP-1..DP-7 (tab:inconsistencies); findings F-1..F-5 with exactly F-3, F-4
  integration-induced (tab:gaps, conclusion). Position paper = IEEEtran, operational
  concern-assignment gap "stated at the clause level" (its abstract's own words), no `src/`
  reference in it. All correct.
- **Identifier correspondence:** I-1..I-7 map to DP-1..DP-7 with identical standards
  involved, clause references, and GSN nodes on all seven rows (only exceptions: M1 type
  field; code I-2 cites "8800 Cl.8-9" where the paper's table prints "8800 Cl.8" — the paper
  body itself says Clauses 8-9, so the code is defensible). Gap-1..Gap-5 map to F-1..F-5
  with matching integration-induced flags and, except M2/M3, matching phases.
- **Caption claim about grouping:** "The paper's own table groups these as
  integration-induced findings and open methodological problems rather than by the three
  types above" — correct; tab:gaps uses an II/OM column and orders F-3, F-4 before F-1, F-2,
  F-5.
- **New labels** `tab:gen-decision-points` / `tab:gen-findings` no longer collide with the
  paper's `tab:inconsistencies` / `tab:gaps`; no test or source file references the old
  generated labels; `pytest tests/test_results.py tests/test_paper_claims.py` → 76 passed.
- **193-vs-192 test note:** the paper does say "An automated test suite of 193 tests"
  (Limitations); commit `4d782b0` exists and took the suite from 193 to 192 (see a3).
- **Empirical-evidence paragraph:** the WAISE paper's G5 evidence type (c) citation is the
  VEHITS 2026 companion study's *simulated* ensemble outputs (AUROC 0.982), exactly as the
  README says; neither .tex file references `data/empirical_results/`; PointPillars appears
  in the WAISE paper only in the VEHITS 2024 companion-study sentence, which does not rest
  on these files; `data/empirical_results/README.md` confirms the separate runtime-monitoring
  project (paper P5), the MDR/MFAR → G6 mapping, and the SECOND → PointPillars substitution
  rationale.
- **`docs/figures/README.md`:** all four provenance rows verified (`plot_coverage_heatmap`,
  `plot_evidence_convergence`, `plot_weather_heatmap` exist in
  `src/visualization/coverage_plots.py`; `gsn_renderer.py` exists;
  `carla_evaluator.py`'s own docstring confirms it "does not connect to CARLA"); both papers'
  figures are TikZ-only (the only `\includegraphics` in either .tex is the ORCID logo), so
  "these files are not included by either paper" is correct.
- **`configs/` "documentation only; no code loads them":** verified by search over `src/`
  and `tests/`.

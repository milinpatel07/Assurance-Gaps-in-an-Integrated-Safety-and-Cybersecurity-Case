# SAFECOMP reviewer verdict — iteration 1 (scope-fidelity repair)

Reviewer question: does the repository now SUPPORT more than it did, or merely
CONTAIN more? Method: every factual sentence the diff adds was checked against
the repository, the git history, and the two camera-ready `.tex` sources. I did
not read other reviews or PROGRESS.md.

## Verdict

**Accept the change. It adds support, not volume.** Almost every sentence added
is a checkable claim, and every one I checked, checks out. The change also
*removes* two standing false assertions (the "paper not included" line, and the
old table captions/labels that impersonated the paper's own tables). By the C2
scope-fidelity gate this is the right first move: the repo previously misstated
the papers; now it mostly states exactly what they state, and marks the seams.

Findings below, severity-ranked. None is a rejection-level gate violation; #1 is
the closest thing to one.

---

## Q1. What was added that a reader can check, vs. must trust?

**Checkable — and verified by this reviewer:**

1. *193-vs-192 test note* (`README.md`): paper W:487 says "193 tests"; commit
   `4d782b0` exists; the tree at `4d782b0^` contains 193 `def test_` functions,
   the tree at `4d782b0` contains 192; the current suite runs **192 passed**.
   Every element of the note is reproducible from `git` and `pytest`. Verified.
2. *Label collision fix* (`src/results/latex_tables.py`): the WAISE paper itself
   uses `\label{tab:inconsistencies}` (line 401) and `\label{tab:gaps}` (line
   442). The generated tables previously emitted those exact labels with stale
   captions ("Requirement inconsistencies", "Assurance gaps"). The new
   `tab:gen-decision-points` / `tab:gen-findings` labels collide with nothing in
   either paper. Verified; a real defect fixed, not wording.
3. *Identifier mapping in captions*: paper uses DP-1..DP-7 and F-1..F-5; code
   uses I-1..I-7 and Gap-1..Gap-5. Spot-checked correspondence: I-2 "Evidence
   type asymmetry at V&V" = DP-2 (same title, W:376); Gap-1 "No AI-specific
   quantitative reliability target" = F-1 "Quantitative acceptance criteria for
   AI components" (W:435). The claim that the paper's own table groups findings
   as "integration-induced findings and open methodological problems" is the
   paper's literal Table caption (line 442). Verified.
4. *`configs/` "documentation only; no code loads them"*: grep over `src/`,
   `tests/`, `Makefile`, `pyproject.toml` finds no load of `case_study.yaml`,
   `standards.yaml`, `detector_config.yaml`, or `weather_grid.yaml`, and no
   `import yaml` anywhere. Verified.
5. *`data/carla_configs/README.md` parameter table*: `RAIN_LEVELS = [0, 10, 25,
   50, 100]`, `VISIBILITY_LEVELS = [500, 200, 100, 50, 10]`, thresholds 20 mm/h
   / 200 m, and the 25 / 21 / 4 grid split all match
   `src/evaluation/weather_conditions.py` and `weather_grid.yaml`; voxel size
   `[0.16, 0.16, 4.0]` and point-cloud range match `voxelization.py` and
   `second_detector.py` defaults. Verified.
6. *`docs/figures/README.md`*: the four PNGs exist; "not included by either
   paper" is true — the only `\includegraphics` in either `.tex` is the ORCID
   logo; all paper figures are TikZ. Verified.
7. *Empirical-results framing*: "Neither paper cites these files" — grep for
   KITTI, nuScenes, `empirical_results` in both `.tex` files: zero hits
   (PointPillars appears once, W:203, but as the VEHITS 2024 per-scenario
   companion, not these files). "The WAISE paper cites a different result for
   its G5 evidence type (c), the simulated ensemble disagreement reported in
   the VEHITS 2026 companion study" — exactly W:376 (AUROC 0.982, "simulated
   ensemble outputs", `\cite{PatelJungVEHITS2026}`). Verified.

**Trust-required (a reader cannot check these from the repo):**

- "Both are published through their venues" (README) — see finding #1 below.
- "That count was correct when the paper was written" (test-count note) — the
  git fact is checkable; whether the paper predates commit `4d782b0` is not.
- "produced by a separate runtime-monitoring project" (README) — provenance
  assertion; the sub-README's pointer for it is an unresolvable internal label
  ("the parent project (paper P5)").
- "none is meant to" (position paper / `src/`) — an intent claim; the factual
  half ("no file in `src/` supports it") is checkable and plausible.
- `data/carla_configs/README.md`: "checked against the code on the date of this
  file" — the file carries no date and is not yet committed, and the README
  itself admits "Nothing enforces that agreement."

The ratio is strongly in favour of checkable. That is the right direction.

## Q2. Anything asserted that neither paper supports? (gate check)

No hard C2 violation. Two soft ones, severity-ranked with the rest below:

- **"Both are published through their venues"** asserts a publication status
  the repository cannot evidence and that may be premature for 2026 venues. The
  files are camera-ready ("CR_" prefix); "accepted" is supported, "published"
  is not. This replaced a *false* sentence ("not included in this repository"),
  so it is a net improvement — but it traded a checkable falsehood for an
  uncheckable maybe.
- **"These are the kinds of evidence G5 and G6 call for"** is interpretive:
  neither paper names MDR/MFAR anywhere, and G6 in the paper prescribes no
  metric. It is softened by the immediately following disclaimer and is far
  more honest than the old text ("supporting the G5 and G6 claims"), which
  impersonated paper evidence. Acceptable, but it is the repo speaking, not
  the paper.

## Q3. Is the 193-vs-192 note the right call?

Yes. Without it, any reader who runs `pytest` gets 192 against the paper's own
footnote claiming 193 — a silent contradiction that a hostile reviewer treats
as evidence of drift. The alternatives are worse: padding a test to reach 193
would be fabrication; silence would be concealment; the note is an erratum with
a verifiable mechanism and commit hash, and I verified both. It does not read
as the repo excusing itself; it reads as the repo refusing to fake agreement
("no test was added here to make it agree" is exactly the sentence a reviewer
wants to see). One refinement I would prefer: replace the unverifiable clause
"That count was correct when the paper was written" with the checkable form
"the tree before commit `4d782b0` contains 193 tests" — then the whole note is
reproducible by the reader.

## Q4. Is the empirical-results paragraph honest but damaging?

Honest, and the honesty is worth the cost. Yes, a reviewer will now ask: *why
does measured data that no paper cites sit in a supplementary repository at
all?* But the paragraph pre-answers it (separate project, evidence types G5/G6
name, provenance README), and the alternative — the old text claiming these
files support "the G5 and G6 claims of the integrated pattern" — was the
genuinely damaging position: it invited the fatal follow-up "then why does the
paper cite a *simulated* AUROC of 0.982 while the repo's *measured* severe-frame
AUROC is 0.67–0.82?" with no disclosure to stand on. The new text makes that
same question answerable. Uncited-but-labeled data is a curiosity; uncited data
dressed as paper evidence is a misconduct suspicion. The change picks the right
side.

## Q5. Anything now worse than before?

Nothing material, but three residuals, continuing the severity ranking:

3. **The retreat stops one level down.** The top-level README now says "no
   claim in either paper rests on them", but `data/empirical_results/README.md`
   (untouched by this diff) still says these files "support G5 (V&V sufficiency
   evidence...)" and "map to G6", and cites an unexplained "parent project
   (paper P5)". A reader following the pointer lands in the framing the top
   level just disavowed. The sub-README needs the same one-sentence retreat,
   and "paper P5" needs a resolvable reference.
4. **DP-2 type tag divergence is still silent.** The new Table 5 caption
   asserts I-k = DP-k identity (true by title), but the paper's table tags DP-2
   as "S, M" while the code tags I-2 `STRUCTURAL` only, so the generated table
   still disagrees with the paper in one cell. The caption should say so, or
   the code should carry both tags.
5. **The two new READMEs document agreement nothing enforces.** The
   carla-configs README says its grid values were "checked against the code on
   the date of this file" and admits nothing enforces it. The repo's own design
   principle (numbers in paper, `src/`, and tests kept in lockstep) suggests
   the cheap upgrade: one test that parses the two YAML files and asserts they
   match `RAIN_LEVELS`, `VISIBILITY_LEVELS`, the thresholds, and the 25/21/4
   split. That would convert the last purely-trusted table in this change into
   support. Same for the 25/21/4 numbers quoted in the README itself.

Regression checks done: full suite passes (192/192) after the caption/label
change; no test, doc, or committed output references the retired labels
`tab:inconsistencies`/`tab:gaps` outside the paper sources where they belong;
`data/synthetic_illustrations/` contains no generated `.tex`, so no stale
reference outputs were orphaned; the `docs/figures/` tree line now matches the
actual directory contents.

## Severity-ranked summary

| # | Severity | Finding | Fix |
|---|----------|---------|-----|
| 1 | Medium | "Both are published through their venues" — unverifiable, possibly premature | Say "accepted; camera-ready sources" |
| 2 | Low-Med | "kinds of evidence G5 and G6 call for" is repo interpretation, not paper text | Attribute: "in the categories the pattern's G5/G6 nodes name" or similar |
| 3 | Low-Med | `data/empirical_results/README.md` still uses "support G5/G6" framing and dangling "paper P5" | Align sub-README with top-level retreat |
| 4 | Low | Generated table types DP-2 "S" vs paper "S, M", unmentioned in the new caption | Note it, or dual-tag I-2 |
| 5 | Low | New READMEs' code-agreement tables enforced by nothing | One structural test over the two YAMLs |
| 6 | Info | "correct when the paper was written" is the one unverifiable clause in an otherwise reproducible note | Rephrase to the pre-`4d782b0` tree fact |

**Bottom line:** the change is what it claims to be — a scope-fidelity repair.
It converts false or trust-me statements into checkable ones, and the checkable
ones survive checking. Support increased; volume increased only in service of
that.

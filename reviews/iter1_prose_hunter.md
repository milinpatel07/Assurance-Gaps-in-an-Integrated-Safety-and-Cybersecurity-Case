# Iteration 1 prose review (machine-prose hunter)

Scope reviewed: README.md changed hunks only (two-papers block, repository-structure
comments, three-layer item 3, tests 193-vs-192 note, Windows gsn2x note),
docs/figures/README.md (all, new), data/carla_configs/README.md (all, new),
src/results/latex_tables.py (caption strings). Verified against `git diff` and the
paper sources where captions make claims about the paper.

Global checks first: no em-dashes anywhere in the added prose. No banned vocabulary
(comprehensive, novel, robust, significant, seamless, leverage, delve, crucial, key,
powerful, cutting-edge, streamline, unlock, dive into, worth noting, in today's
landscape): grep over all four files returned nothing. No "This section explains"
openers. No heading restated by its first sentence. The bullet lists that exist
(two-papers block, provenance tables) carry per-item facts that would tangle as
prose; they are earning their keep.

Findings, severity-ranked. Every rewrite preserves the information content.

## 1. Triple-negative tricolon (data/carla_configs/README.md, lines 3-4)

> "They are not measurements, they are not generated, and no code reads them."

Defect: anaphoric three-part negative parallel ("They are not X, they are not Y,
and no Z"). This is the single strongest generated-cadence tell in the batch. It
also half-duplicates "Provenance: hand-written" (hand-written already means not
generated).

Replacement (whole opening, lines 3-4):

> "Provenance: hand-written, not generated. These two files record parameters;
> no code reads them, and none of their numbers is a measurement."

## 2. Dangling "below" (data/carla_configs/README.md, lines 25-27)

> "matching `total_conditions`, `triggering_conditions`, and
> `non_triggering_conditions` below."

Defect: broken reference. Those keys are not below anything in this README; they
live in `weather_grid.yaml`. As written the reader scrolls down and finds nothing.

Replacement:

> "matching the `total_conditions`, `triggering_conditions`, and
> `non_triggering_conditions` entries in `weather_grid.yaml`."

## 3. Publication-status scope claim (README.md, line 19)

> "Both are published through their venues; the copies here are the accepted sources."

Defect: scope claim likely overstated, and "published through" is off idiom. The
sources are named `CR_Submission_...` and `CR_position_paper.tex`, i.e.
camera-ready accepted copies; for 2026 venues the proceedings are plausibly not
out. Say exactly what is true.

Replacement (if proceedings are not yet out, which the author must confirm):

> "Both papers have been accepted at their venues; the copies here are the
> camera-ready sources."

If both really are in print already, keep "published" but fix the idiom:

> "Both papers are published by their venues; the copies here are the accepted
> camera-ready sources."

## 4. Unverifiable time anchor (data/carla_configs/README.md, line 24)

> "The grid values here were checked against the code on the date of this file:"

Defect: hedge by vague anchor. A checked-out file carries no visible date; "the
date of this file" is unverifiable by the reader. The honesty of the passage (the
very next sentences admit "Nothing enforces that agreement") deserves a plain
anchor.

Replacement:

> "The grid values here were checked against the code when this file was written:"

## 5. Verb tricolon (docs/figures/README.md, lines 29-30)

> "Without it the pipeline warns, continues, and still writes the `.dot` source."

Defect: three-verb triad. Mild on its own (it describes a real behavior sequence),
but with finding 1 it starts to look like a habit. Break the rhythm without
losing a fact:

Replacement:

> "Without it the pipeline warns and carries on; it still writes the `.dot` source."

## 6. Doubled equivalence markers (data/carla_configs/README.md, lines 31-32)

> "`configs/case_study.yaml` and `configs/standards.yaml` at the repository root are
> documentation in the same sense, and are likewise not loaded."

Defect: "in the same sense" and "likewise" say the same thing twice in one
sentence.

Replacement:

> "`configs/case_study.yaml` and `configs/standards.yaml` at the repository root are
> documentation in the same sense; no code loads them either."

## 7. Asyndetic triad and mixed numeral style (README.md, lines 12-14)

> "The code in `src/` backs this paper: the 9-goal integrated pattern, the seven
> decision points, the five findings."

Defect: "the X, the Y, the Z" with the conjunction dropped is a rhetorical
flourish models reach for; the plain list wants an "and". Secondary: "9-goal"
(digit) against "seven"/"five" (words) in the same breath. The three items are
genuinely the three things the code backs, so this is low severity.

Replacement:

> "The code in `src/` backs this paper: the 9-goal integrated pattern, the seven
> decision points, and the five findings."

(Keep "9-goal" as is if that is the paper's own compound form; otherwise
"nine-goal" would settle the numeral mix.)

## 8. Passive "included by" (docs/figures/README.md, line 32)

> "These files are not included by either paper."

Defect: passive where the active is shorter and clearer. Lowest severity.

Replacement:

> "Neither paper includes these files."

(Claim verified: the only `\includegraphics` in either paper is an ORCID logo;
both papers draw their figures in TikZ.)

## Observation, not a rewrite

Three-layer list, README.md lines 66-84: the rewritten item 3 opens
"**Empirical evidence** (measured) at `data/empirical_results/`." while the
untouched items 1 and 2 still open "**Methodology** — `src/`." with em-dashes.
Item 3 now obeys the no-em-dash rule and its siblings do not, so one list shows
two authorial hands. Out of scope for iteration 1 (items 1 and 2 were not
changed), but a future pass should bring the siblings into line rather than
revert item 3.

## Passages that read human-written (do not overcorrect)

- README.md lines 152-156, the 193-vs-192 tests note. Concrete commit hash
  (verified: `4d782b0` exists), an admitted discrepancy with no hedging, sentence
  lengths of roughly 8, 10, 25, and 20 words, and the closing "and no test was
  added here to make it agree" is a wry, deliberate construction no model
  defaults to. Leave it alone.
- README.md lines 100-102, the gsn2x note. "it will download a binary that
  cannot run" is blunt and specific, followed by a plain imperative fix. Human.
- README.md lines 76-84, empirical-evidence item 3 body. Names the VEHITS 2026
  companion study, and the negative scope claims are exact: "Neither paper cites
  these files, and no claim in either paper rests on them." Varied rhythm, no
  filler.
- data/carla_configs/README.md, the table section and "The detector named here".
  "The values that the pipeline actually uses live in `src/`, hard-coded:" and
  "Editing a value in these files changes no behaviour, so if you change one,
  change the matching constant in `src/` too." Direct address, concrete
  consequence. Human.
- src/results/latex_tables.py captions. The apparent repetition "Decision points
  at junction points" is inherited, not generated: the paper's own Table caption
  is literally "Decision points at junction points of the integrated GSN"
  (CR_Submission_....tex line 401), and "junction point" is the paper's Step 4
  term of art. DP-1 to DP-7, F-1 to F-5, and the grouping into
  "integration-induced findings and open methodological problems" all verified
  present in the .tex. The parallel sentence template across the two captions
  ("Identifiers X are the code's names for the Y the paper calls Z") is what you
  want in paired table captions. Leave both captions as they are.

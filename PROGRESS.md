# Progress

One entry per iteration. What changed, what the four reviewers found, what the
iteration revealed, whether the ranking moved.

---

## Iteration 1: scope-fidelity repairs (IDEAS.md candidate 1)

**Why this first.** C2 (scope fidelity) is a gate, not a criterion to trade off.
The repository was actively misstating the papers, so no addition could outrank
stopping that.

**Risks named before building.** That a rewritten README would smuggle in claims
the papers do not make, in particular by promoting `data/empirical_results/` to
paper-cited evidence. That the 193-vs-192 test count might be fixable only by
changing paper text or by padding the suite, both forbidden. That relabelling
generated tables might alter a computed value or an emitted identifier.

**Changed.**

- README: replaced the false line "The paper itself is published separately and is
  not included in this repository" (both papers' camera-ready sources are in
  `paper/`). Added a plain-language statement of the finding and the argument
  figure at the top. Collapsed a duplicated 21-word title that filled a phone
  screen. Relabelled `docs/` as `docs/figures/`, and `configs/` as documentation
  that no code loads. Rewrote the empirical-results paragraph to say that neither
  paper cites those files. Recorded the 193-vs-192 test-count divergence with its
  cause. Added the Windows and macOS gsn2x path. Removed the remaining em-dashes.
- `src/results/latex_tables.py`: generated tables 5 and 6 previously emitted
  `\label{tab:inconsistencies}` and `\label{tab:gaps}`, the exact labels the WAISE
  paper uses for its own hand-authored tables. Relabelled to `tab:gen-decision-points`
  and `tab:gen-findings`. Captions now state that code identifiers I-1 to I-7 and
  Gap-1 to Gap-5 are the paper's DP-1 to DP-7 and F-1 to F-5. No identifier and no
  computed value changed.
- New `docs/figures/README.md` and `data/carla_configs/README.md`, each declaring
  provenance in the first line.
- `data/carla_configs/weather_grid.yaml`: the header claimed the 20 mm/h and 200 m
  thresholds came from ISO 21448 Cl.7. They are project choices. Corrected the
  attribution. The threshold values themselves were not touched.
- `data/empirical_results/README.md`: the opening claimed these results are "used
  as verification and monitoring evidence in the integrated GSN argument pattern".
  Neither paper cites them. Rewrote to say so, and marked the G5/G6 mapping section
  as a mapping made in this repository rather than a claim either paper makes.
- New `tests/test_config_documentation.py`: 11 tests comparing the descriptive YAML
  files against the constants in `src/`.
- `.gitignore`: `.claude/` and `.headroom/` were untracked but not ignored.

**Verification.** 192 tests passed before, 203 after (192 + 11 new). `generate_all`
runs; two runs at seed 42 are byte-identical except the `generated` timestamp. No
computed number, threshold, seed, or emitted identifier was changed.

**What the four reviewers found.**

*Standards practitioner.* Verified the identifier correspondence holds on
standards, clauses, and GSN nodes for all twelve items, and that the two-paper
description is correct. Found the camera-ready paper carries classifications the
code never absorbed: DP-2 is typed "S, M" in the paper and structural-only in the
code; F-1 is "Concept, Verification" against the code's verification-only; F-3 is
"Verification, Operation" against verification-only; F-2's coverage row gained ISO
24089. Also found the ISO 21448 Cl.7 misattribution in `weather_grid.yaml`, now
fixed.

*SAFECOMP reviewer.* Verdict: the change adds support rather than volume. Verified
independently that the tree at `4d782b0^` has 193 test functions and at `4d782b0`
has 192, that the paper does use `\label{tab:inconsistencies}` and `\label{tab:gaps}`,
and that no `.tex` file mentions KITTI, nuScenes, or `empirical_results`. Flagged
"Both are published through their venues" as unverifiable (now "accepted"), the
"kinds of evidence G5 and G6 call for" phrasing as repo interpretation (now marked
as such), the stale framing in the empirical README (now fixed), and that the new
READMEs' agreement tables were enforced by nothing (now enforced by the new tests).

*Phone visitor.* The first screen was two copies of a 21-word title, with the
actual finding two swipes down; no plain-language statement of the result existed;
no figure was shown although the repository is a poster QR target; navigation was
backticked paths rather than links. All fixed. Judged the 193-vs-192 note and the
gsn2x note as trust-building and correctly placed. Judged both new directory
READMEs exemplary and told the top-level README to imitate them.

*Prose hunter.* Found one anaphoric triple-negative tricolon ("They are not
measurements, they are not generated, and no code reads them"), a verb tricolon
("warns, continues, and still writes"), an asyndetic triad in the two-papers block,
a broken "below" cross-reference, an unverifiable time anchor ("on the date of this
file"), and a passive construction. All rewritten, none deleted. Cleared the
193-vs-192 paragraph, the gsn2x note, and both table captions as human-written, and
verified the captions' terminology against the paper before clearing them.

**What the iteration revealed.**

1. The camera-ready paper contains revisions the code never absorbed (DP-2 type,
   F-1 and F-3 lifecycle phases, F-2 clause coverage). The repository's declared
   three-way lockstep is broken in a direction the earlier audit missed: the audit
   checked counts and found them consistent, and these are classifications inside
   rows. New IDEAS.md candidate, and a stop-and-ask item, because the code is
   single-valued, the tests assert the single values, and making the fields
   multi-valued changes the 3/2/2 type split the paper's own prose relies on.
2. Descriptive files that no code loads will drift silently. The fix generalises:
   any documentation table asserting agreement with code should be enforced by a
   test. This became the new test module and is now a general rule for later
   iterations.
3. The empirical directory holds measured data that no paper claims. IDEAS.md §5B
   predicted a reviewer would read this as orphaned or overclaiming; the SAFECOMP
   reviewer did exactly that, independently. The criteria had no category for
   evidence awaiting its paper, which is confirmed as a real blind spot rather than
   a hypothetical one.
4. The README was written for someone who already knew the work. Every reviewer
   except the standards practitioner said so in different words.

**Ranking movement.** No criterion was overturned. C2 held as a gate and did the
work expected of it. One ordering change: the paper/code classification drift
enters as a new candidate ranked immediately after the crosswalk (candidate 3),
because it is the same defect class (paper and code disagreeing about the same
object) but with the paper carrying content the code lacks, which is worse than a
naming mismatch. Candidate 1 is closed apart from the two items awaiting a
decision.

**Attribution check (Gate 1).** No tooling trailer, author, or committer appears
anywhere in the history. Every commit is authored by Milin Patel. One violation was
found and resolved in this iteration: a tool-specific rules file was tracked at the
repository root. Its content was working practice worth keeping, so it moved to
`docs/working-practices.md` with the tool reference removed from the header, and the
old filename is now ignored. Three commit subjects still mention agent sessions and a
generated rules file; rewriting history is reserved to the authors and was not done.

**Decisions taken by the authors during this iteration.**

- The working rules move to `docs/working-practices.md`, not to a contributing
  guide, because they are practice rather than contribution guidance.
- Where the camera-ready table and the camera-ready prose disagree about DP-2, the
  prose wins. See iteration 2.

**Cost.** Roughly two hours of machine work: one baseline install and test run, six
verification runs of the suite, two full pipeline runs for the determinism check, one
history search, and four review passes run in parallel.

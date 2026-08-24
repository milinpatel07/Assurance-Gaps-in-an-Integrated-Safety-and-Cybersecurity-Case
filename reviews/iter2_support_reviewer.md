# Support reviewer — commits `f9a7902`, `21a9ecb` (+ `7240c4c`)

One question: does the repository now **support** more than it did, or merely **contain** more?

Method: every claim below was checked by mutation. I copied the tree to a scratch
directory, broke one thing at a time, and recorded which tests noticed. The
reviewed repository was not modified. Baseline: 231 passed.

**Verdict.** The commit is honest in intent and its central finding (the G2 drift)
is real and load-bearing. But three of its four mechanisms are under-guarded to
the point where they document a position rather than defend it, and one of them —
`check_gsn_completeness()` — ships a self-contradicting artefact that did not
exist before. Net: the argument in the source got better; the evidence a reader
downloads got worse.

---

## S1 — Blocking

### S1.1 The out-of-scope mechanism is an unbounded green-suite escape hatch

I took a second claim out of the argument:

```python
# src/standards/iso21448.py, CLM-21448-VER-01
gsn_goal=None,
out_of_scope_reason="Deemed a vehicle-level obligation."
```

Result: **231 passed.** `is_complete` still `True`. `mapped_claims` silently
38/40. Nothing failed. Not `test_no_silently_unmapped_claims` (the reason is
non-empty), not `test_g5_is_the_only_all_four_node_in_both_views` (ISO 21448 has
other claims at G5, so the standard-level set is unchanged), not the completeness
check (`is_complete` reads `unmapped` only).

The representation-consistency test compares **standard-level set membership**.
The escape hatch operates at **claim granularity**, one level below. Any claim
that is not the last of its standard at a goal can be removed with one sentence.

The commit message says the invariant "keeps its meaning rather than being
weakened to pass". As shipped, the invariant is: *every claim maps to a node, or
carries a non-empty string.* That is not an invariant a reviewer can check.

**Fix:** pin the count, which is the thing a reviewer actually checks.

```python
def test_exactly_one_claim_is_out_of_scope(self):
    oos = [c.claim_id for s in registry.all_standards for c in s.claims
           if c.is_out_of_scope]
    assert oos == ["CLM-26262-TSC-01"]
```

Then a second exclusion is a deliberate, reviewed edit to the test, not a
side-effect.

### S1.2 `check_gsn_completeness()` now exports a statement contradicting its own fields

Run as shipped:

```
total 40  mapped 39  unmapped 0  out_of_scope 1  is_complete True
EXPLANATION: "The 9-goal GSN is structurally complete. All 40 claims from
5 standards map to goal nodes. ..."
```

`explanation` (completeness.py:87) interpolates `len(all_claims)` unconditionally
and was not updated when `out_of_scope` was subtracted from `mapped_claims`
(completeness.py:105). Both fields are exported together —
`src/results/export.py:154-157` writes `mapped_claims`, `total_claims` and
`explanation` into `analysis_results.json`. **`out_of_scope_claims` is read by no
consumer at all** (grep: only completeness.py itself). Confirmed in generated
output:

```json
"completeness": {"is_complete": true, "total_claims": 40, "mapped_claims": 39,
 "explanation": "... All 40 claims from 5 standards map to goal nodes. ..."}
```

The notebook (cell at `notebooks/assurance_gaps_analysis.ipynb:358-359`) prints
mapped 39 and unmapped 0 against total 40 and does not print the out-of-scope
line, so a reader sees an unexplained missing claim.

This is a regression. Before the commit the JSON was consistent (40/40). Adding a
field and not wiring it to the two places that already ship is the definition of
containing more without supporting more.

**Also:** the camera-ready states, at
`paper/waise2026/CR_Submission_...tex:487`, that the suite "checks that all
extracted claims map to GSN nodes". After this commit that sentence is false, and
the paper is frozen. The repository should say so explicitly (a note in
`REPRODUCING.md` or the completeness docstring), not leave a reader to discover it.

---

## S2 — Material

### S2.1 The Gap-4 derivation does not discriminate; the default argument does

`counterfactual.py:295`:

```python
contributors_in_any_single_view = 1
```

A literal. `test_gap4_single_standard_view_has_one_contributor` asserts `== 1`
against it — **that assertion can never fail**. So

```python
invisible_under_premise = len(union_contributors) > 1 and 1 == 1
```

reduces to `union_contributor_count > 1`. I ran the derivation over all nine goals:

| goal | contributors | `invisible_under_premise` |
|---|---|---|
| G1 | 3 | **True** |
| G2 | 3 | **True** |
| G3 | 1 | False |
| G4 | 3 | **True** |
| G5 | 4 | **True** |
| G6 | 3 | **True** |
| G7 | 1 | False |
| G8 | 1 | False |
| G9 | 2 | **True** |

Six of nine goals come out "invisible under the premise". The docstring says
"The contrast is not automatic, which is what makes the computation worth
running: G3 and G7 draw on one standard even in the union." It cites two of the
three minority cases. `test_gap4_contrast_case_single_standard_goal` — whose
docstring says "Without this contrast the Gap-4 derivation would be vacuous" —
picks `goal="G3"`, one of those three. Pick `goal="G2"` and the same derivation
declares G2 Gap-4-like.

So the computation does not select G5. `goal: str = "G5"` selects G5, and that
association is hand-authored (see S2.2).

To be fair: the docstring is the most honest thing in the commit. It names the
premise, names it as asserted, and says a reader who rejects it is not compelled.
That is the right instinct. But the honesty is about *the premise* and the thing
that needs disclosing is *the discrimination*. Is it "a conclusion dressed as
computation"? Not in intent — but as written it is a conclusion dressed as a
**selective** computation, and the computation is not selective.

**Fix:** either (a) state in the docstring that the premise marks six of nine
goals and that the identification of G5 is the paper's, not the code's; or
(b) delete `contributors_in_any_single_view` and its test, and report the
derivation for what it is — `union_contributor_count`.

### S2.2 The derivation introduces a fourth un-reconciled copy of "which goal a finding sits at"

`counterfactual.py:251` hardcodes `boundary_goals = ["G7", "G8"]`;
`counterfactual.py:271` hardcodes `goal="G5"`. The same mapping already exists at
`src/analysis/traceability.py:64-70`:

```python
gap_goal_mapping = {
    "Gap-1": ["G1"], "Gap-2": ["G9"], "Gap-3": ["G7", "G8"],
    "Gap-4": ["G5"], "Gap-5": ["G3"],
}
```

Nothing binds them. Grep confirms `boundary_goals` appears only in
counterfactual.py and its own test; `gap_goal_mapping` only in traceability.py.

This is the *same defect class the commit was written to eliminate*, reintroduced
in the fix. And `test_gap3_derivation_uses_the_g7_g8_boundary` (line 481) asserts
`result["boundary_goals"] == ["G7", "G8"]` — a literal compared against itself.
**Cannot fail.**

**Fix:** read both anchors from `gap_goal_mapping`, and add that pair to
`test_representation_consistency.py`, which is exactly the file for it.

### S2.3 Iteration 2's "absorption" changes no output

`additional_lifecycle_phases`, `lifecycle_phases` and `lifecycle_phase_label` are
read by the new tests and nothing else. Every output path still reads the
singular field:

- `src/results/latex_tables.py:328` — `phase = gap.lifecycle_phase.display_name`
- `src/results/export.py:119`, `:266`
- `src/results/generate_all.py:131`
- `src/analysis/gaps.py:137` (`print_analysis`)

Generated `output/latex/table6_gaps.tex` after the change:

```
Gap-1 & ME & Verification & Validation & --- & No AI-specific quantitative ...
Gap-3 & UI & Verification & Validation & $\dagger$ & Adversarial-SOTIF ...
```

Gap-1 is still Verification-only and Gap-3 is still Verification-only — precisely
the divergence from Table 4 the iteration set out to close. Six new tests assert
a field that no artefact reads.

**Bonus defect visible in the same line** (pre-existing, but this is where it
surfaces): the Phase column is not LaTeX-escaped. The tabular is
`{@{}clllp{5.5cm}@{}}` — five columns, four ampersands per row. The header has
four; the Gap-1 row has five, because `Verification & Validation` goes in raw.
`_latex_escape` exists at `latex_tables.py:25` and is applied to `desc`
(line 330) but not to `phase` (line 328). **`table6_gaps.tex` does not compile.**
Nobody has ever compiled the generated tables. That is a sharper statement about
"contains vs supports" than anything in this commit.

### S2.4 Iteration 2 creates fresh drift, one commit after the drift lesson

```
get_by_phase(CONCEPT)                      -> []
gaps whose lifecycle_phases include CONCEPT -> ['Gap-1']
get_by_phase(OPERATION)                    -> []
```

`gaps.py:119` (`get_by_phase`) filters on the primary field; `lifecycle_phases`
returns the full set. Two ways to ask "which findings are in phase X", giving
different answers. No test catches it.

---

## S3 — Real but contained

**S3.1 The agreement test's candidate set is bounded by the answer.**
`test_derivation_agrees_with_the_published_integration_induced_set` builds
`derived_invisible` from `report["derived"]`, which has exactly the keys `Gap-3`
and `Gap-4`. So `derived_invisible ⊆ {Gap-3, Gap-4}` always. It falsifies in one
direction only — I flipped Gap-1 to `integration_induced=True` and got 3
failures, so it is not vacuous — but it can never *discover* a misclassified gap,
only detect that the published list moved. The docstring "The two derived gaps
are exactly the two the paper calls II" reads as convergent evidence; it is not.

**S3.2 `test_every_exception_states_a_reason` checks prose length.**
`assert len(reason) > 40`. `"a" * 41` passes. Length is not a reason. Either drop
it or check something structural (e.g. that the reason names a claim id or clause
that exists).

**S3.3 Three definitions of "which standards" now coexist.** `derive_gap3` uses
raw `source_standards` (TR 5469 unfiltered); `derive_gap4` uses
`registry.normative_standards`; `test_representation_consistency.py:28`
re-declares `NORMATIVE = {...}` as a literal instead of asking the registry. If
the registry's normative set ever changes, the test will not follow it.

**S3.4 The out-of-scope record does not cite the clause it argues from.**
`source_clause` is narrowed to `Part 4, Cl.6.4.3`, but `out_of_scope_reason`
argues from Cl.6.2 and Cl.6.4.6.1, and the test at
`test_representation_consistency.py:190` pins the narrowed reference. A reviewer
who opens Cl.6.4.3 does not find the argument. Either cite the clauses the reason
uses, or put the reference in the reason text.

Relatedly, `Claim.is_out_of_scope` requires `gsn_goal is None`. A claim that keeps
a goal *and* carries an `out_of_scope_reason` is counted as mapped, with a
dangling reason nothing checks.

**S3.5 The Makefile platform fix is half-applied.** `gsn-install` writes to
`$(GSN2X_BIN)` = `gsn/gsn2x.exe` on Windows, but the render rules at Makefile:112
and :116 invoke `$(GSN2X)` = `gsn/gsn2x`. `make gsn-install && make gsn` still
fails on Windows. And four documents still tell the reader the opposite of what
the Makefile now does: `README.md:133-135`, `REPRODUCING.md:57`,
`docs/working-practices.md:37-40`, and `CLAUDE.md`.

**S3.6 Test-count drift against a frozen paper.** The camera-ready cites
"193 tests"; the suite is 231 and each iteration widens the gap. Nothing in the
repository reconciles the two. A reader who counts will not get the paper's
number. Worth one line in `REPRODUCING.md` recording that the count has grown
since submission and why.

---

## What genuinely supports more

Not everything here is volume. Recorded because it is the standard the rest
should meet.

- **The G2 finding is real and the guard is not vacuous.** I restored
  `CLM-26262-TSC-01` to `gsn_goal="G2"`: **4 tests failed**
  (`test_the_two_views_agree_where_no_exception_is_recorded`,
  `test_g5_is_the_only_all_four_node_in_both_views`,
  `test_single_phase_goals_hold_only_that_phase[G2]`,
  `test_the_technical_safety_concept_claim_is_recorded_out_of_scope`). The
  regression the commit describes cannot silently return.
- **`REPRESENTATION_EXCEPTIONS` is not vacuous**, which was the thing to check.
  `test_recorded_exceptions_still_differ` forces an exception that no longer
  applies to be deleted — that is the right shape and it is rare to see it. And
  the paper-critical test (`test_g5_is_the_only_all_four_node_in_both_views`) sits
  *outside* the exception gate, so the escape hatch cannot swallow the published
  claim. Both exclusion lists are guarded:
  `test_multi_phase_goals_really_are_multi_phase` makes a listed goal earn its
  place, `test_every_goal_is_either_checked_or_excused` closes the set. This is
  the best-engineered part of the commit and the model for fixing S1.1.
  (One narrow hole: if `G5` were ever added to the exception list with
  four-member sets that differ in *membership*, every test still passes.)
- **Gap-3's derivation is falsifiable.** Adding `ISO26262` to G7's
  `source_standards`: **4 tests failed**, including the two Gap-3 tests and the
  agreement test. The result does follow from a file authored elsewhere. It is
  near-analytic — G7 and G8 are *defined* as the SOTIF goal and the cyber goal —
  but it is a real re-derivation across a file boundary, not a read-back.
- **Keeping the claim rather than deleting it is the right call**, and the
  standards reading (technical safety concept as a Part 4 system-level work
  product, above an AI-component argument) is defensible. The objection in S1.1
  is about the guard, not the decision.
- **Naming Gap-1/2/5 as asserted, and saying why a new field would only relocate
  the assertion**, is the correct answer to a question most repositories dodge.

---

## Ranked fix list

1. **S1.2** Branch `explanation` on `out_of_scope`; export `out_of_scope_claims`
   in `export.py:154-157` and the summary report. One-line changes, removes a
   false statement from a published artefact.
2. **S1.1** Add `test_exactly_one_claim_is_out_of_scope` pinning the id.
3. **S2.3** Route `lifecycle_phase_label` into `latex_tables.py:328`,
   `export.py:119/266`, `generate_all.py:131`; make `get_by_phase` use
   `lifecycle_phases` (fixes S2.4 too).
4. **S2.3-bonus** Wrap the Phase column in `_latex_escape`. `table6_gaps.tex`
   currently does not compile.
5. **S2.1** Delete `contributors_in_any_single_view` and its test, or disclose
   the six-of-nine result in the docstring.
6. **S2.2** Source `boundary_goals` and `goal` from
   `traceability.gap_goal_mapping`; add the pair to
   `test_representation_consistency.py`.
7. **S3.5** Use `$(GSN2X_BIN)` in the two render rules; update the four documents.
8. **S3.2/S3.3/S3.4/S3.6** as described.

# Iteration 2 — standards-practitioner review

Scope: commit `21a9ecb` ("Absorb the camera-ready classifications the code had not
taken up") only. Files touched: `src/analysis/gaps.py`,
`src/analysis/decision_points.py`, `src/standards/base.py`,
`tests/test_paper_claims.py` (plus `PROGRESS.md`, not reviewed).

Ground truth: `paper/waise2026/CR_Submission_WAISE_SafeCompAssuranceGaps_SafetySecurityCase_AI_Perception_HAD.tex`
and the compiled `.pdf` of the same name.

Remit: do the clause references and the classifications in the repository say what
the camera-ready and the cited standards actually say.

---

## Verification of the four points asked

### 1. Lifecycle phases for F-1 and F-3 — CONFIRMED

`tab:gaps` (tex lines 449, 452) reads verbatim:

```
\new{F-3} & Adversarial-SOTIF boundary unowned & Verification, Operation & \new{II} & 21448 Cl.1 (excludes); 21434 Cl.15 (includes) \\
F-1 & \new{Quantitative acceptance criteria for AI components} & \new{Concept, Verification} & \new{OM} & 26262-5 (HW only); 21448 Cl.6.5 \new{(framework)} \\
```

So F-1 = "Concept, Verification" (the phase cell is `\new`-marked, i.e. changed in
the revision round) and F-3 = "Verification, Operation" (unmarked). The other three
rows are single-phase: F-4 "Integration", F-2 "Modification", F-5 "Design".

The code now agrees. `python -c "from src.analysis.gaps import GapClassification; ..."`
gives:

```
Gap-1 | VERIFICATION | 'Concept, Verification'
Gap-2 | MODIFICATION | 'Modification'
Gap-3 | VERIFICATION | 'Verification, Operation'
Gap-4 | INTEGRATION  | 'Integration'
Gap-5 | DESIGN       | 'Design'
```

All five labels match the table, including the ordering ("Concept" before
"Verification"), which `lifecycle_phase_label` gets right by sorting on enum
declaration order rather than on insertion order. F-2, F-4 and F-5 correctly did
not acquire an extra phase. Point 4 of the brief is satisfied.

### 2. ISO 24089 in F-2's related-clauses column — CONFIRMED, and the characterisation is accurate

`tab:gaps` F-2 row (tex line 455):

```
F-2 & \new{OTA re-assurance workflow (partial coverage)} & Modification & \new{OM} & 26262-8 Cl.8; 8800 Cl.14.8.3; TR\,5469 Table A.8 \crev{; 24089} \\
```

`\crev` is defined at tex line 63 as the *camera-ready correction round* mark, so
"; 24089" is genuinely a camera-ready addition.

The F-2 prose (tex line 437) carries the matching `\crev` sentence:

> \crev{ISO~24089~\cite{ISO24089} specifies the software-update engineering process
> but not the re-assurance of a modified AI model's safety argument, so it does not
> close F-2.}

Bibliography entry (tex lines 531–532):

> \bibitem{ISO24089}
> \crev{ISO: Road vehicles --- Software update engineering. ISO~24089:2023. ISO,
> Geneva (2023)}

The repository's added string is

> "ISO 24089 (software update engineering; specifies the update process, not
> re-assurance of a modified AI model's argument)"

This is a faithful paraphrase and is correct as a statement about the standard:
ISO 24089:2023 is titled *Road vehicles — Software update engineering* and scopes
the update engineering process (organisational and project requirements, update
packages, campaigns); it does not address re-assurance of a safety argument for a
retrained model. **No misstatement of the standard here.** Two small notes are in
the findings list below (dropped word "safety"; ordering; no clause anchor).

### 3. DP-2 prose — three places CONFIRMED; provenance claim NOT confirmed; Table tag CONFIRMED

All three prose sites exist and say what the comment claims:

1. Structural list (tex line 372):
   > Structural \new{decision points} (DP-1, DP-2, DP-5) require decisions that no
   > standard prescribes and are discussed below.

2. Subsection heading (tex line 376):
   > \textbf{DP-2: Evidence type asymmetry at V\&V \new{(structural decision point)}.}

3. Discussion (tex line 469, opening `\subsection{Evidence Asymmetry and
   Integration-Induced Findings}`):
   > The evidence asymmetry at G5 (DP-2) is a structural property of the applicable
   > standards: the evidence types prescribed by the cited standards are disjoint by
   > design.

And `tab:inconsistencies` (tex line 410) does tag DP-2 "S, M":

```
DP-2 & Evidence type asymmetry at V\&V & All four & 26262-6 Cl.9; 21448 Cl.9--11; 8800 Cl.8; 21434 Cl.10 & G5 & S, M \\
```

with the legend `T\,=\,terminological, M\,=\,methodological, S\,=\,structural.`
DP-2 is the only row with two type letters.

**The substantive decision is right.** Resolving in favour of the prose is forced,
not merely preferred: line 372 partitions the seven decision points as
terminological (DP-3, DP-4), methodological (DP-6, DP-7), structural (DP-1, DP-2,
DP-5) — a 2/2/3 partition over exactly seven items. Counting DP-2 twice would give
eight tags over seven decision points and break the paper's own sentence, not just
`summary_statistics()`. Keeping `I-2` single-valued and STRUCTURAL is correct.

**The provenance sentence is wrong.** The comment ends "The last two are
camera-ready additions." The last two are the subsection heading and the discussion:
 - the heading parenthetical is wrapped in `\new`, the *earlier* revision-round mark
   (tex lines 20/23), not `\crev`, the camera-ready correction mark (lines 63/66);
 - the discussion sentence at line 469 carries **no change mark at all** — it is
   unmarked body text.

Under the strict reading (camera-ready = `\crev`), none of the three is a
camera-ready addition. Under the loose reading (`\new` counts too), exactly one is.
Neither reading yields two. See finding 6.

---

## Findings, severity-ranked

### 1. HIGH — Every table number the commit introduces is off by one

The commit's comments and tests cite "Table 4" for the findings table and "Table 3"
for the decision-point table. Both are wrong. From the compiled camera-ready PDF:

```
Table 1. Scope of published safety argumentation work for AI in automated driving.
Table 2. Sub-goal decomposition with clause-level traceability.
Table 3. Worked example for DP-5: one failure mode of the case study component ...
Table 4. Decision points at junction points of the integrated GSN.
Table 5. Integration-induced findings and open methodological problems.
```

`tab:gaps` is **Table 5**; `tab:inconsistencies` is **Table 4**. The shift is itself
a camera-ready artefact: `tab:dp5` (tex line 381) is a new table whose caption is
entirely `\crev`-wrapped, and it inserted itself ahead of both.

Affected, all added by `21a9ecb`:
 - `src/analysis/gaps.py` — two comments, "Table 4 of the camera-ready gives ..."
 - `src/standards/base.py` — `AssuranceGap` docstring, "Table 4 gives two phases"
 - `src/analysis/decision_points.py` — "Table 3 of the camera-ready tags DP-2 'S, M'"
 - `tests/test_paper_claims.py` — `TestCameraReadyClassifications` class docstring
   plus four test docstrings ("Table 4, F-1", "Table 4, F-3", "Table 4, F-2",
   "Table 4 gives F-2 'Modification' alone", "Table 3's 'S, M'")

This matters more than a typo would elsewhere: the whole justification for the
commit is that the repository should carry what the paper says, and `gaps.py` now
cites *two different wrong numbers* for the same table — the pre-existing class
docstring "Each gap corresponds to a row in Table 6 of the paper" and
`print_classification`'s "Table 6" (the camera-ready has only five tables), and now
"Table 4" as well. `src/results/latex_tables.py` also emits the artefact as
`table6_gaps.tex`.

Fix: Table 5 for findings, Table 4 for decision points, everywhere; and retire the
phantom "Table 6" while in the file.

### 2. HIGH — ISO 21448 Cl.6.5 is still mischaracterised in Gap-1, and the camera-ready explicitly corrected it

`gaps.py` Gap-1 carries:

```python
"ISO 21448 Cl.6.5 (qualitative acceptance criteria)",
```

The camera-ready replaced exactly this characterisation. `tab:gaps` F-1 now reads
`21448 Cl.6.5 \new{(framework)}`, and the `\new`-marked F-1 prose (tex line 435)
says:

> \new{ISO~21448 Clause~6.5 establishes the framework for residual-risk acceptance
> criteria, listing factors and risk tolerability principles (GAMAB, GAME, positive
> risk balance), but defers quantitative values to context ...}

"Qualitative acceptance criteria" is not what Clause 6.5 does — on the paper's own
account it establishes a framework and defers *quantitative values* to context,
which is not the same as prescribing qualitative criteria. This is the identical
defect class the commit set out to close (a camera-ready re-characterisation the
code had not absorbed), in the very row the commit edited a sibling of, and it is a
misstatement about a standard rather than only about the paper. It was missed.

Same pattern, smaller: Gap-5 carries `"ISO/PAS 8800 Cl.8.4, Annex B G3 (claim
exists)"` where `tab:gaps` F-5 now says `8800 Cl.8.4 \new{(framework)}`.

### 3. HIGH — The committed seed-42 reference output is now stale; the reproducibility contract is broken

`data/synthetic_illustrations/gaps.csv` is a committed reference artefact and was
not regenerated. Regenerating and diffing:

```
$ python -m src.results.generate_all --seed 42 --scenes 50 --output <tmp>
$ diff <tmp>/csv/gaps.csv data/synthetic_illustrations/gaps.csv
3c3
< Gap-2,...,"ISO 26262-8 Cl.8 (...); ISO/PAS 8800 Cl.14.8.3 (...); ISO 24089 (software update engineering; specifies the update process, not re-assurance of a modified AI model's argument); ISO/IEC TR 5469 Table A.8 (...)"
---
> Gap-2,...,ISO 26262-8 Cl.8 (...); ISO/PAS 8800 Cl.14.8.3 (...); ISO/IEC TR 5469 Table A.8 (...)
```

The commit message states "Pipeline output at seed 42 is unchanged apart from
ISO 24089 now appearing in the findings coverage" — i.e. the change was known and
the regenerated file simply was not committed. `REPRODUCING.md`'s promise that the
same seed reproduces byte-identical output (timestamp excepted) does not hold from
`21a9ecb` onwards. Still stale at HEAD.

### 4. MEDIUM — The two-phase fix does not reach any generated artefact except TRACEABILITY.md

`lifecycle_phase_label` has exactly one consumer,
`src/results/traceability_index.py:222`. Every other output site still emits the
single primary phase:

 - `src/results/latex_tables.py:328` — `phase = gap.lifecycle_phase.display_name`
 - `src/results/export.py:266` (CSV) and `:119` (JSON)
 - `src/results/generate_all.py:131`
 - `src/analysis/run_analysis.py:219`
 - `src/visualization/coverage_plots.py:435`
 - `src/analysis/gaps.py:136` (`print_classification`)

Result: the generated findings table still prints "Verification & Validation" for
both Gap-1 and Gap-3, contradicting camera-ready Table 5 in precisely the two cells
the commit exists to fix. `get_by_phase()` likewise still filters on the primary
phase only, so `get_by_phase(CONCEPT)` and `get_by_phase(OPERATION)` return empty
even though the paper places findings in both.

### 5. MEDIUM — The generated LaTeX findings table does not compile

`output/latex/table6_gaps.tex` declares five columns and emits six cells on any
row whose phase is VERIFICATION, because `display_name` is `"Verification &
Validation"` and the `&` is never escaped:

```latex
\begin{tabular}{@{}clllp{5.5cm}@{}}
  Gap-1 & ME & Verification & Validation & --- & No AI-specific quantitative reliability target \\
  Gap-3 & UI & Verification & Validation & $\dagger$ & Adversarial-SOTIF boundary unowned --- ...
```

`Extra alignment tab has been changed to \cr`. Pre-existing, not introduced here —
but the commit added the property that fixes it for free: `lifecycle_phase_label`
strips at `" &"` and `" /"`, so switching `latex_tables.py:328` to
`gap.lifecycle_phase_label` resolves finding 4 and finding 5 in one edit and makes
the generated table match Table 5.

### 6. MEDIUM — The provenance claim in the `I-2` comment is false

"The last two are camera-ready additions" — the discussion sentence carries no
change mark, and the heading parenthetical is `\new`, not `\crev`. See section 3
above. The classification decision stands; only the sentence justifying it is
wrong. In a repository that records paper provenance as fact in code comments, an
unverified provenance claim is the same defect class as an unverified clause
reference.

### 7. LOW-MEDIUM — The parallel camera-ready addition at F-4 was missed

The camera-ready sharpened F-4 with a `\crev` sentence (tex line 433):

> \crev{ISO~26262-2 Clause~6.4.8 collects the per-domain assessments in the
> encompassing system safety case but does not define how their residual risks
> combine into one release decision.}

`gaps.py` Gap-4 still carries only `"ISO 26262-2 Cl.6.4 (functional safety
assessment)"`. The finer clause is already known elsewhere in the codebase
(`src/standards/base.py:123`, `src/standards/iso26262.py:196,231`), so absorbing it
was a one-line change. This is the same `\crev` sweep that produced the ISO 24089
row; one of the two was picked up and the other was not.

### 8. LOW — DP-2's "M" tag leaves no trace in the code

The commit's own design principle for Table 5 was to add a secondary field
(`additional_lifecycle_phases`) so the paper's full statement is recorded while the
single-valued contract and the derived counts stay intact. The identical situation
at DP-2 ("S, M" in Table 4) was handled instead by a comment. An
`additional_types` field excluded from `summary_statistics()` would be the
consistent treatment and would let a test assert the paper's table content rather
than describe it in prose. Not wrong, but asymmetric.

### 9. LOW — `I-2` clause reference is broader than Table 4

Code: `"ISO/PAS 8800 Cl.8-9 (AI metrics, uncertainty quantification)"`.
Table 4: `8800 Cl.8`. All other clause references across DP-1…DP-7 match the table
exactly. Pre-existing; flagged because it sits in the entry this commit edited.

### 10. LOW — A now-loosened test was not tightened

`tests/test_paper_claims.py:289` still reads:

```python
phases_with_gaps = {g.lifecycle_phase for g in gaps.gaps}
# Paper claims gaps in: Verification, Modification, Integration, Concept, Design
assert len(phases_with_gaps) >= 4
```

The `>= 4` and the comment's five-phase list existed only because the code carried
one phase per finding. With `lifecycle_phases` the set is all six phases, and the
comment itself is now wrong (it omits Operation). This is the assertion the commit
made newly provable and left alone.

### 11. LOW — ISO 24089 entered without a clause anchor

Every other string in every `partial_coverage` list names a clause, part or table.
`"ISO 24089 (software update engineering; ...)"` names none. The camera-ready does
the same (`; 24089`), so the repository is faithful — but the repository's stated
contribution is clause-level traceability, and this entry cannot be traced. If a
clause anchor is added it must be verified against ISO 24089:2023 directly, not
inferred.

Two cosmetic notes on the same entry: the paper says "a modified AI model's
**safety** argument" and the code drops "safety", which weakens a claim that is
specifically about assurance argumentation rather than about engineering artefacts;
and the code inserts ISO 24089 *before* TR 5469 whereas Table 5 appends it last,
so generated coverage strings will not sit in the paper's order.

---

## Summary

The four points in the brief check out on the substance: the two-phase entries are
correctly absorbed and correctly ordered, F-2/F-4/F-5 correctly stayed single-phase,
ISO 24089 is genuinely a camera-ready addition and is characterised accurately
against both the paper and the standard, all three DP-2 prose sites exist and say
what the comment says, and Table 4 does tag DP-2 "S, M". Keeping `I-2` structural is
not just defensible but forced by the paper's own 2/2/3 partition of seven items.

What the commit gets wrong is provenance and reach. Every table number it introduces
is off by one because the camera-ready inserted a new table ahead of both
(findings = Table 5, decision points = Table 4). The claim that two of the three
DP-2 prose sites are camera-ready additions is false. The `\crev` sweep that found
ISO 24089 missed ISO 26262-2 Cl.6.4.8 at F-4, and the `\new` sweep that would have
found the Cl.6.5 "framework" re-characterisation at F-1 was not done — leaving an
inaccurate statement about ISO 21448 Clause 6.5 in place. And the fix stops at the
data model: no generated artefact except `TRACEABILITY.md` shows the second phase,
the committed seed-42 reference CSV was never regenerated and now differs from a
fresh run, and the generated findings table does not compile.

Suggested order: finding 2 (misstates a standard), finding 3 (breaks
reproducibility), finding 1 (wrong throughout the new comments and tests), findings
4 and 5 (one edit fixes both), then 6, 7 and the rest.

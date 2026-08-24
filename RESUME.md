# Resume Here

Written for whoever picks this up next, including a later session with no memory
of this one. It says where the work stands, what was settled and why, what is
authorised but unstarted, what is blocked, and what to do next.

`PROGRESS.md` is the running log. `REPO_AUDIT.md` is the point-in-time audit plus
the findings that came later. `IDEAS.md` is the ranked candidate list. `PLAN.md`
estimates the remaining phases. This file is the short version.

---

## Current state

Branch `restructure/two-papers-plus-poster`. Working tree clean. Five commits on
top of `79f9880`:

| Commit | What |
|---|---|
| `d81b838` | Corrected repository statements that misdescribed the papers |
| `f9a7902` | Derived the counterfactual claim; took a system-level claim out of scope |
| `21a9ecb` | Absorbed camera-ready classifications the code had not taken up |
| `7240c4c` | Per-platform gsn2x selection; added `PLAN.md` |
| `4f6dd9e` | Added the generated traceability index |

**244 tests pass.** Baseline at the start of this work was 192. The pipeline is
deterministic: two runs at seed 42 differ only in the `generated` timestamp.

**Attribution (Gate 1) is clean.** No tooling trailer, author or committer
anywhere in history. Every commit is authored by Milin Patel. One violation was
found and closed: a tool-specific rules file tracked at the root, whose content
moved to `docs/working-practices.md` with the tool reference removed. Three older
commit subjects still mention agent sessions; rewriting history is reserved to
the authors and was deliberately not done.

---

## What these iterations established

**1. The repository was misstating the papers, and now does not.** The README
claimed the paper was not included when both camera-ready sources are in
`paper/`. It mislabelled `docs/`, presented `configs/` as configuration although
nothing loads it, and described the measured PointPillars results as supporting
the G5 and G6 claims although neither paper cites them. All corrected.

**2. Two of the repository's load-bearing claims were asserted, not computed.**
`counterfactual.py` hand-wrote which findings are invisible from a single
standard, and its visibility matrix read those same literals back. Gap-3 is now
derived from the goal structure. Gap-4 is derived from a plurality premise which
the module states as a premise rather than proving. Gap-1, Gap-2 and Gap-5 stay
asserted and now say so, with the reason: no field records whether a single
standard's own text exhibits a deficiency alone, and adding one would relocate
the assertion rather than remove it.

**3. Representation drift reached a published claim.** This is the most important
finding and the one that should shape what comes next. The repository writes down
"which standards contribute to which goal" twice, in `source_standards` on each
goal and in `gsn_goal` on each claim, and nothing held the two together. They had
drifted. An ISO 26262 claim mapped to G2 made G2 report all four standards under
`compute_goal_density()`, so the paper's central structural claim, that G5 is the
only such node, survived only because the test happened to read the other
representation. Resolved by the authors on clause evidence: the technical safety
concept is a system-level artefact, so the claim was out of scope rather than
mis-placed. It is kept with `gsn_goal=None` and a recorded reason, so the
obligation stays visible while staying out of the argument.

**4. The camera-ready carries content the code had not absorbed.** Table 4 gives
two lifecycle phases each for F-1 and F-3 and adds ISO 24089 to F-2. All three are
now in the code. Table 3 tags DP-2 "S, M" while the prose calls it structural in
three places, two of them camera-ready additions; the authors resolved that in
favour of the prose, and the reasoning sits at the definition.

**5. Documentation that no code loads will drift silently.** `configs/` and
`data/carla_configs/` are read by nothing. They are now held to the constants in
`src/` by tests.

**6. The general lesson.** Every one of these was the same shape: a fact written
down twice with nothing keeping the copies together. That is now the first
question to ask of any new artefact.

---

## Authorised and unstarted

Scope for the session, given by the authors, in order:

1. ~~Remaining scope-fidelity repairs under the C2 gate~~ **done** (`d81b838`).
2. ~~The traceability index covering both papers~~ **done** (`4f6dd9e`).
3. **The edition-keyed clause-to-node export.** Partly delivered: the clause-to-node
   index and the identifier crosswalk are now in `TRACEABILITY.md`, generated and
   tested. What remains is the edition-keyed part, moving the 52 clause references
   out of Python string literals into data the code loads, with an `edition` field,
   so the analysis can be re-run against a revised standard. `configs/standards.yaml`
   looks like that file but is inert.

Explicitly **not** authorised in this session: notebooks, the visual layer, the
seam map, any restructuring.

---

## Blocked, and on what

**The top-level layout restructure** (the authors' "Phase 4") is authorised in
principle but was excluded from this session. It needs a decision on the layout
itself, which is public framing.

**`make` is not installed on the development host.** The `gsn-install` platform
fix is therefore unverified by running. Everything else was verified by running.
Settle it by running `make gsn-install` on each of the three platforms, or in CI.

**gsn2x version.** The Makefile pins v4.2.3. The binary installed locally is
4.3.1, which is what rendered the current SVGs. Decide whether to move the pin.

**The empirical layer cannot be made reproducible here.** The training and
evaluation scripts for `data/empirical_results/` belong to an unpublished
companion paper. Gate 3's "one command from clone to every artefact" is
achievable for everything the papers use, and impossible for that directory. It
is a boundary to document, not a task to size.

**History rewriting** is reserved to the authors.

---

## Next three items, in order

### 1. Check the GSN YAML against the builder

**Why first.** It is the same defect class as the finding that reached a
published claim, in the one place still unchecked. `gsn/integrated_pattern.gsn.yaml`
and `build_integrated_gsn()` both describe the nine-goal argument.
`docs/working-practices.md` calls them two sources of truth "kept consistent" by
hand, which is exactly what was said of the pair that had already drifted. The
YAML still tags G9 with the older `Gap-2` spelling, so at least one difference is
known to exist. The rendered SVGs a poster reader sees come from the YAML, while
every tested claim comes from the builder, so a drift here is visible to readers
and invisible to the suite.

**What it might assert beyond the papers.** Nothing, if it only compares. The risk
is deciding which side wins where they differ, which is a paper-fidelity judgment
and should be brought to the authors rather than settled in code.

**Model: Opus** for the comparison design and any difference found. Sonnet could
run the comparison once the rules are fixed.

### 2. Finish the edition-keyed clause data

**Why second.** It completes authorised item 3 and removes the last inert file
that looks load-bearing. It also gives the 2031 reader the ability to re-run the
analysis against a revised standard, which no part of the repository currently
supports.

**What it might assert beyond the papers.** An `edition` field invites the
impression that the analysis was run against editions it was not. State the one
edition each claim was extracted from and no more.

**Model: Opus** for the schema and for any case where two clause references
disagree with each other, which the audit never checked. **Sonnet** for the
mechanical transfer of 52 references once the schema is fixed, and the tests.

### 3. Reproducibility by a stranger (Gate 3)

**Why third.** It is not cuttable: without it a reviewer cannot verify, which
fails half the repository's purpose. It is third only because the two items above
protect claims that a reproduction would otherwise faithfully reproduce while
being wrong.

**Scope.** A lockfile, one command from clone, a run manifest recording commit
hash, Python version, package versions and input hashes, all seeds in one place,
and a verification done by actually cloning to a temporary directory and diffing.
Consider moving `torch` to an optional extra: it is pulled in for
`src/perception/`, which backs no paper number, and it dominates install time for
a reviewer who only wants to check the claims.

**Model: Sonnet** for the lockfile, manifest and clone-and-diff. **Opus** for
interpreting any non-empty diff, since the rule is to fix the cause and never to
update the reference.

---

## Standing rules that outlive this session

- Nothing enters that the papers do not support. This is a gate, not a tradeoff.
- Never change a computed number, threshold or seed to make things agree.
- Never update a reference output to make a failing test pass.
- Declare provenance on every artefact: measured, seeded, argued, or generated.
- Verify by running, never by reasoning about what the code would do.
- Full four-reviewer pass only for artefacts a reader sees. For internal changes,
  the standards practitioner and the support reviewer, and say which were skipped
  and why.
- Stop and ask when: a fix needs paper text changed, an item would assert
  something neither paper supports, paper and code and tests disagree and the
  right value is a judgment call, or a decision sets public framing.

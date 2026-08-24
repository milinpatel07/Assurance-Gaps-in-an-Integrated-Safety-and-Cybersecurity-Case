# Remaining Work: Estimate

Written before starting the phase the author calls Phase 4. Grounded in the
repository as it stands at commit `d81b838` and in what iteration 1 actually
cost, not in generic estimates.

## A note on the phase numbers

The names "Phase 4 migration", "Phase 6 reproducibility", "Phase 7 visual layer",
"Phase 8 release" and "Phase 9 adversarial pass" are not defined in `IDEAS.md`,
`CRITERIA.md`, `PROGRESS.md`, or any other file in this repository. They come
from the author's own plan, which this repository has not seen. Phases 1, 2, 3
and 5 are not mentioned in the instruction, so the numbering is not continuous
here either.

What follows maps each name onto the nearest actual body of work in the
repository, and states that mapping explicitly so a wrong guess is visible rather
than buried. If a mapping is wrong, the estimate under it is wrong too.

| Author's name | Mapped to | Confidence in the mapping |
|---|---|---|
| Phase 4 migration | **Corrected by the author.** Restructure the top-level directory layout so a visitor sees within five seconds which folder serves which paper and where the reproduction entry point is. `git mv` only, outputs byte-identical before and after. | High, stated directly by the author |
| (separate item) Clause data and crosswalk | Move the 52 clause references into edition-keyed data, and the DP↔I / F↔Gap crosswalk. Split out of Phase 4 on the author's instruction. | High |
| Phase 6 reproducibility | Gate 3: one command from clone to every artefact, a lockfile, a run manifest, and a clean-machine verification | High |
| Phase 7 visual layer | Diagrams generated from `gsn/*.yaml` at build time: the argument, the four-standard convergence at G5, and the two operational gaps; one colour per standard; readable at 380px | High |
| Notebooks | The notebook question set out in the standing instruction, plus the existing 47-cell notebook | High |
| Phase 8 release | Tag, archive, DOI, and the landing page the QR code resolves to | Medium. "Release" could also mean a paper-camera-ready deadline procedure, which is not repository work. |
| Phase 9 adversarial pass | A hostile end-to-end review of the finished repository, in the spirit of `passes/04_adversarial_critic.md` | High |

## What iteration 1 actually cost, as the calibration point

Iteration 1 was the smallest of the items on the list, and it still: touched 8
files, added 1 test module of 11 tests, ran the suite 6 times and the pipeline
4 times, ran 4 review passes in parallel, and produced 4 new candidates. It also
uncovered a defect the prior full audit had missed. Two conclusions carry into
every estimate below.

First, review is not the expensive part; the fixes the reviewers generate are.
All four reviewers returned findings, and three of the four returned findings
that required new work rather than a wording change.

Second, each iteration so far has produced more items than it closed. Iteration 1
closed one candidate and opened four. The estimates below assume this rate decays
but does not reach zero, and they include the follow-on work in the iteration
count. An estimate that assumed each iteration only closes its own item would be
too low by roughly a third.

---

## Phase 4: top-level layout restructure (re-sized after the author's correction)

**What must be done.** Reorganise the top level so a visitor can see in five
seconds which folder serves which paper and where the reproduction entry point
is. `git mv` only. Every generated output byte-identical before and after.

**Iterations: 1, plus 1 if the reviewers disagree about the layout.** This is
smaller than the clause migration it was previously conflated with. The moves are
mechanical; the risk is entirely in what breaks silently.

**Opus:** the layout itself, because it is the first thing the QR visitor sees
and therefore a public-framing decision. **Sonnet:** executing the moves and
running the before-and-after comparison.

**What makes it cost more.** Path strings are embedded in more places than a
`git mv` touches: `Makefile` targets, `pyproject.toml` entry points, the Colab
badge URL in `README.md`, the notebook's own `pip install` and import cells,
`REPRODUCING.md`, the new `tests/test_config_documentation.py` which reads
`data/carla_configs/` and `configs/` by relative path, and the docstrings that
name modules. The byte-identical requirement is the real constraint: any output
carrying a path string will change, so that has to be checked rather than
assumed. One known example already exists, found today: rendering
`gsn2x gsn/foo.yaml` versus `cd gsn && gsn2x foo.yaml` produces different CSS
class names in the SVG, because gsn2x derives a module name from the input path.
A layout change moves exactly that kind of string.

## Separate item: clause data and crosswalk

**What must be done.** There are 52 `Clause` objects and 40 `Claim` objects
across five modules (`iso21448.py` 17 clauses, `iso26262.py` 10, `iso8800.py` 10,
`iso21434.py` 8, `tr5469.py` 7). Each carries a `reference` string such as
`"Cl.8.4"` with no edition field. The work: define the data schema including
edition, move all 52 references into it, make `StandardsRegistry` load it, delete
or repoint the inert `configs/standards.yaml`, keep every existing assertion
passing, and add the label crosswalk (DP↔I, F↔Gap) as a loaded table with a test
rather than as prose.

**Iterations: 3.** One to migrate the data and prove the registry produces
identical output; one for the crosswalk plus its test; one for the follow-on the
first two will generate. Not 1, because the schema has to represent things the
current code cannot: a clause that belongs to two lifecycle phases, and the
multi-valued DP-2/F-1/F-3 classifications from iteration 2.

**Opus:** the schema design, and every decision about what a clause reference
means when the paper and the code disagree. This is the same class of judgment
that produced the DP-2 question, and it will recur roughly once per standard.
**Sonnet:** the mechanical transfer of 52 references once the schema is fixed,
the test writing against that fixed schema, and the verification runs.

**What makes it cost more.** If the migration reveals that two clause references
in different modules are inconsistent with each other, each instance is a
stop-and-ask, not a fix. I cannot predict how many exist without doing the
migration; the audit checked clause references against the papers, never against
each other. A second cost driver: `generate_all` output must stay byte-identical
through the migration, and any ordering change in a dict or list will break that
silently until the determinism check catches it.

## Phase 6: reproducibility

**What must be done.** Dependencies are lower-bound only (`numpy>=1.24`,
`torch>=2.0`, and six more) with no lockfile. There is no run manifest. Seeds are
spread across `carla_evaluator.py`, `sensitivity.py` (five seeds), `export.py`,
and the Makefile. Required: a lockfile, one command from clone to every artefact,
a manifest recording commit hash, Python version, package versions and input
hashes, all seeds gathered in one place, and a verification performed by actually
cloning to a temporary directory and diffing.

**Iterations: 2, plus 1 that I cannot size.** The lockfile, manifest and seed
consolidation are one iteration. The clean-clone verification is a second. The
unsizable third is what the diff reveals.

**Opus:** deciding what the manifest must record to make a claim checkable, and
interpreting any non-empty diff, since the rule is to fix the cause and never to
update the reference. **Sonnet:** generating the lockfile, writing the manifest
emitter, moving the seeds, and running the clone-and-diff.

**What makes it cost more, and one thing that blocks it outright.**
`data/empirical_results/` cannot be regenerated by this repository at all: the
training and evaluation scripts belong to an unpublished companion paper. So
"one command from clone to every artefact the papers use" is achievable for the
WAISE tables and figures, and impossible for the empirical layer. That is not a
task to be sized; it is a boundary to be documented. `torch>=2.0` is pulled in
for `src/perception/`, which backs no paper number, so the lockfile will be large
and slow to install for code the reviewer does not need. Dropping torch to an
optional extra is a small change with a large effect on clean-machine install
time, and it is worth doing inside this phase.

## Phase 7: visual layer

**What must be done.** Three diagrams generated from `gsn/*.yaml` at build time:
the nine-goal argument, the four-standard convergence at G5, and the position
paper's two operational gaps. One colour per standard, consistent across
diagrams, deck and poster. Legible at 380px in daylight.

**Iterations: 3 to 4.** One for the build path and the colour system, one per
diagram beyond the first, one for the phone-legibility pass. The full four-
reviewer pass applies here because a reader sees every output.

**Opus:** what each diagram must show, which is a claim-fidelity question, not a
drawing question. The G5 diagram in particular has to show four scales that do
not combine, and showing that without implying a combination rule is exactly the
kind of thing the C2 gate exists for. **Sonnet:** the rendering pipeline, the
colour tokens, and the size and contrast checks.

**What makes it cost more, and a blocker to clear first.** Neither `gsn2x` nor
Graphviz's `dot` is on the PATH on this machine. The Python `graphviz` package is
installed, but it is only a wrapper and needs the binary. So the current state is
that the repository cannot render its own diagrams here, and `make gsn-install`
downloads a Linux binary that will not run on this Windows host. Until a working
renderer exists locally, every visual iteration is unverifiable, and the rule is
to verify by running. **This blocks the phase and should be cleared before it
starts.** Second driver: the position paper's gap figure has no YAML source at
all; it exists only as TikZ inside the `.tex`. Generating it from `gsn/*.yaml`
means authoring that YAML first, and doing so without asserting more than the
position paper states.

## Notebooks

**What must be done.** First, decide which notebooks are warranted, using the
author's own test: does the reader's understanding depend on seeing a value
change? The existing notebook is 47 cells, 28 of them code, with no stored
outputs, a `pip install` cell, and references to the `I-` and `Gap-` identifiers
that iteration 1's crosswalk work will supersede. Its first cell claims it
"reproduces the complete five-step constructive integration methodology and all
publication results", which is a claim nobody has verified.

**Iterations: 1 for the analysis, then 1 per notebook that survives it.** My
current reading is that two survive: the counterfactual notebook, and the G5
four-scale notebook where the reader tries to combine the scales and cannot. The
counterfactual notebook is worth building only if the vanishing is derived rather
than read from the hard-coded `invisible_gaps` literals, which makes it depend on
IDEAS.md candidate 4. So: 1 + 2, plus 1 to bring the existing notebook into line
or retire it. **Total 4.**

**Opus:** the warranted-or-decoration judgment, and the prose, since the standing
instruction requires the prose to carry the argument and the code to be
secondary. **Sonnet:** CI execution, determinism, and the Colab path.

**What I cannot estimate.** Whether the existing 47-cell notebook currently runs
at all. It has never been executed in this session, stores no outputs, and is not
in CI. What would settle it: one execution run under a clean kernel. That single
run also settles whether its opening claim is true, which matters more than the
notebook itself, because a false claim in the first cell of the file the Colab
badge points at is a C2 gate violation sitting in the reader's likely entry point.

## Phase 8: release

**What must be done.** A tag, an archived snapshot with a DOI, and the landing
page the QR code resolves to. The landing page is the reader-facing artefact and
carries the four-reviewer pass.

**Iterations: 2.** One for the landing page, one for tag, archive and DOI.

**Opus:** the landing page, which is where the phone visitor's verdict from
iteration 1 applies most directly and where public framing is decided. **Sonnet:**
the tagging and archive mechanics.

**What makes it cost more, and what I cannot decide.** Whether the QR code
resolves to the GitHub repository or to a separate page is a public-framing
decision reserved to the author. Archiving to Zenodo mints a DOI and is a
one-way, outward-facing action, so it needs explicit authorisation and cannot be
done as part of a routine iteration. This phase also cannot honestly complete
before Phase 6, since a DOI on an unreproducible snapshot is worse than no DOI.

## Phase 9: adversarial pass

**What must be done.** A hostile end-to-end read of the finished repository,
attacking the claims rather than the prose: the universal negatives, the
single-assessor extraction, the counterfactual invisibility, and the
G5-uniqueness claim.

**Iterations: 1 to run it, then 1 to 3 to answer it.** The spread is the whole
difficulty. `passes/04_adversarial_critic.md` already predicts the finding: the
load-bearing modules (`counterfactual.py`, `base_pattern_sensitivity.py`) encode
their conclusions as literals rather than deriving them, so the repository is
internally consistent and externally unfalsifiable. If that critique survives the
pass, answering it means deriving those conclusions, which is IDEAS.md candidate
4 and part of candidate 7, and that is real work rather than a rewrite.

**Opus throughout.** This is the one phase with no mechanical component.

**What makes it cost more.** If the derivation is attempted and the answer comes
out differently from the hard-coded literal, the repository has found a defect in
a published claim, and that is a stop-and-ask that no iteration count covers.

---

## Totals

| Phase | Iterations | Sizable? |
|---|---|---|
| 4, clause migration and crosswalk | 3 | Yes |
| 6, reproducibility | 2 + 1 unsized | Partly |
| 7, visual layer | 3 to 4 | Yes, once the renderer blocker is cleared |
| Notebooks | 4 | Yes, after one execution run |
| 8, release | 2 | Yes, but gated on 6 and on author decisions |
| 9, adversarial pass | 2 to 4 | No, depends on what it finds |

**16 to 20 iterations**, of which roughly 8 need Opus judgment throughout, and
roughly 6 are mechanical enough for Sonnet once a spec is fixed. Two items are
not iteration-shaped: the empirical layer cannot be made reproducible here, and
the adversarial pass may surface a defect in a published claim.

## What could be cut without the repository failing its purpose

Its purpose is that a reviewer arriving from the poster can verify what the
papers claim, follow the argument without reading Python, and find nothing false,
stale or undeclared.

**Cuttable, in order of least loss.**

1. **Phase 8's DOI and archive.** A tag is enough for a conference. What is lost:
   citability of the exact snapshot, and permanence if the repository moves. The
   landing page is not cuttable; it is the QR target.
2. **Phase 4's clause migration.** The crosswalk within it is not cuttable, since
   a reviewer holding the paper and finding `I-5` in the code cannot verify
   anything, but that can be delivered as a checked table without the full
   edition-keyed migration. What is lost: the ability to re-run the analysis
   against a revised standard, which matters to the 2031 reader and to nobody at
   the conference.
3. **Two of the four notebooks.** The counterfactual and G5 notebooks earn their
   place under the author's own test. Verifying or retiring the existing 47-cell
   notebook is not cuttable, because the Colab badge points at it and its first
   cell makes an unverified claim.
4. **Phase 9's answering iterations, but not the pass itself.** Running the
   hostile read is cheap and tells the authors what a reviewer will say. Acting
   on it can wait. What is lost: the criticism stands unanswered, which is
   survivable if the repository states plainly which conclusions are asserted
   rather than derived.

**Not cuttable.** Phase 6 and Phase 7. Without reproducibility the reviewer
cannot verify, which fails the first half of the purpose. Without the visual
layer the reviewer must read Python to follow the argument, which fails the
second. Everything else on this list serves those two.

---

## Alternative ordering: the phone reader criterion

Added 2026-08-24 at the authors' request, after the YAML-versus-builder check
landed. The criterion: what does a reviewer arriving from the poster QR code,
on a phone, in daylight, with under a minute, actually encounter?

What that reader meets, in order: the QR target (Phase 8's landing page), the
README's first screen with the argument figure (Phase 7's output, framed by
Phase 4's layout), the top-level file list, and at most one tap further, most
likely the Colab badge, which is the notebooks item. That reader never meets
the edition-keyed clause data, the lockfile, the run manifest, the test suite,
or the GSN YAML source.

| Remaining item | The phone reader sees it? |
|---|---|
| Phase 7 visual layer | Yes; it is most of the first screen |
| Phase 8 landing page | Yes; it is the QR target itself |
| Phase 4 layout | Yes, one swipe down |
| Notebook verification | One tap away, and its first cell makes an unverified claim |
| Edition-keyed clause data | Never; it serves the 2031 re-runner |
| Phase 6 reproducibility | Never directly; it serves the desk reviewer |
| Phase 9 adversarial pass | Never; it serves the authors |

**What this criterion selects.** Reach: the sixty seconds in which most poster
visitors decide whether to return at a desk. Its pure ordering is visual layer,
landing page, layout, notebook verification, then everything invisible in any
order, with the edition-keyed clause data last.

**What it sacrifices.** Verifiability. It ships the shop window before the goods
are checked. Phase 8 is gated on Phase 6 by this plan's own rule, since a DOI on
an unreproducible snapshot is worse than no DOI, and the landing page invites
exactly the verification that Gate 3 makes possible. Ordering purely by
visibility reproduces, at repository scale, the defect class this session kept
finding: a public representation held to nothing.

**Where it beats the existing ranking.** It demotes the edition-keyed clause
data, which this plan already lists as the second most cuttable item and which
no conference reader meets. And it promotes the visual layer, whose main
fidelity risk, drift between the rendered YAML and the tested builder, was
closed by `tests/test_gsn_yaml_builder_consistency.py`. The renderer blocker
recorded under Phase 7 above is also stale: gsn2x 4.3.1 is on PATH on this host
and checked the YAML today.

**Recommended merged order.** Neither pure ordering. The phone criterion decides
what leads; the gating rule decides what may not trail.

1. Phase 7 visual layer (phone-visible; its prerequisites cleared today)
2. Phase 6 reproducibility (invisible, but gates the release)
3. Phase 4 layout
4. Notebook verification (the unverified first-cell claim sits one tap from the poster)
5. Phase 8 landing page and release
6. Edition-keyed clause data
7. Phase 9 adversarial pass

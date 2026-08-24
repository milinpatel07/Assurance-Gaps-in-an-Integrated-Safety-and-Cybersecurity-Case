# Selection Criteria

Stage 3 of the ideation task. These criteria were written after the dimensions
(DIMENSIONS.md) and after the seven generation passes were dispatched, but before
any pass output was read, so that the criteria derive from the papers' stated
purpose and not from the candidates they will rank. Each criterion names what it
would systematically miss; a criterion with no stated blind spot has not been
examined.

Sources cited as in DIMENSIONS.md: **W** = WAISE paper, **P** = position paper,
by line number in the `.tex`.

---

## C1. Checkability

**The criterion:** an artefact scores high if it lets a reader verify a stated
paper claim against a file in the repository, and low if a reader must take it on
trust.

**Derivation:** this is the repository's declared role. W:487 presents the repo
as "an automated test suite ... in the supplementary material [that] checks that
all extracted claims map to GSN nodes, all lifecycle phases are covered, and the
integration-induced findings do not appear in any single standard's claim set".
The repo's own working rules state the same duty for prose. Checkability is not
one goal among several here; it is the only function the papers assign to the
repository.

**What it systematically misses:** artefacts whose value is interpretive rather
than verificational: tutorials, worked instantiation examples, crosswalks that
explain rather than assert. It also cannot see anything serving P, because P's
claims are universal negatives over clause text ("no clause assigns...", P:19)
that no repository file can verify; only access to the standards' text can. A
selection run on C1 alone would conclude the position paper needs nothing, which
is false in an obvious way.

## C2. Scope fidelity

**The criterion:** an artefact scores high if it asserts exactly what the papers
assert; it scores low if building it would quietly claim more (supplying a method
P reserves for future work, fabricating evidence W marks "not produced") or less
(hedging a claim the papers make flatly).

**Derivation:** both papers draw their own scope lines with unusual care. P:19
"leaving the method to future work"; P:30 "We are aware of no published incident
that attributes a deployed automated-driving failure to this ambiguity"; W:376
"Evidence types (a), (b), and (d) are not instantiated for the case study"; W:489
scope exclusions. The repository must not blur lines the papers drew sharply.

**What it systematically misses:** the research-advancing artefacts, which are
arguably the most valuable things one could build from this material: a prototype
of the defeater-based method sketched at P:90, an attempt at the G5 combination
rule, produced adversarial evidence for type (d). C2 privileges the archival role
of the repo over the scientific one, and it will do so on every candidate,
without exception. That is a bias, held deliberately, and named here.

## C3. Occupation of a declared absence

**The criterion:** an artefact scores high if it occupies a cell of the space
that the papers themselves mark as empty: the dashed nodes at G5 (W:307–310), the
undeveloped G9 (W:334), the "no clause" steps of P (P:42–47), and the unstated
seam between the two papers (no passage in either maps DP-5 to the assignment
gap, or R1 to the four G5 scales). Making an absence *visible and precise* is in
scope; *filling* it is C2's business to police.

**Derivation:** absence is both papers' primary object. W's Step 5 output is a
classification of what is missing (W:218); P "states one gap at the clause level"
(P:19). An artefact that exhibits an absence exactly is in the papers' own genre.

**What it systematically misses:** maintenance and hygiene artefacts, which
occupy no interesting cell but keep every other artefact true: fixing the DP/F vs
I/Gap label drift, provenance READMEs, retiring stale generated tables, the
192-vs-193 test-count discrepancy. It also misses artefacts that strengthen an
already-occupied cell (better documentation of evidence type (c)).

## C4. Addressee service

**The criterion:** an artefact scores high if it serves an agent the papers
explicitly name as having to act: the engineer who "must resolve" the decision
points (W:133, W:372) and needs the two project policies (W:483); the
standardization committees P tells what to add (P:93); the researcher bound by
R1–R4 (P:90).

**Derivation:** RQ2 is phrased around an acting engineer; P's closing section is
titled "Implications for Industry and Standardization". The papers do not merely
report; they hand specific work to specific parties.

**What it systematically misses:** readers the papers never name: the 2031
reader who needs the analysis re-runnable against revised standards, and the
adversarial reader who needs the claim-extraction audit trail to attack the
universal negatives. Falsifiability and re-checkability artefacts are invisible
to C4 because the papers assign work only to allies.

## C5. Lockstep economy

**The criterion:** an artefact scores high if it adds no unsynchronised copy of
a paper number, label, or structure; it scores low in proportion to the number of
new copies it creates and the absence of a mechanism keeping them true.

**Derivation:** the repository already maintains a deliberate three-way lockstep
(src values, test assertions, paper text), and the audit (REPO_AUDIT.md §6)
found drift precisely and only where a copy escaped that mechanism: the label
prefixes, the generated LaTeX tables, the inert `configs/`. The evidence is
internal to this repo: copies without a keeper rot.

**What it systematically misses:** taken alone it selects for building nothing,
since every rendering, table, crosswalk, or dashboard is a copy. It penalises
exactly the artefacts richest for readers. It must never be the leading
criterion; it is a tie-breaker and a design constraint on the winners.

---

## Order of application

C2 (scope fidelity) acts as a gate: a candidate that fails it is not ranked
higher by excelling elsewhere, because the repository's first duty is not to
misstate the papers. Among candidates passing the gate, rank by C3, then C1, then
C4, with C5 as tie-breaker and design constraint. Criterion: this order follows
the papers' own priority of statements — they first bound their scope, then
exhibit absences, then offer verification, then address actors. The rejected
alternative (C1 first) would put the repo's mechanism above the papers' meaning.

---

## The strongest case against this criterion set

A different, equally defensible set is: **research value** (does building it
advance the open problem?), **adoption value** (would a supplier actually use
it next year?), and **community value** (can others build on it?). That set
would select, in roughly this order:

1. a working prototype of the defeater-based assignment-and-resolution method
   sketched at P:90, evaluated against R1–R4;
2. an instantiation kit: templates for the G7/G8 ownership policy and the G5
   evidence-admissibility policy (W:483), with a worked non-LiDAR example;
3. a public benchmark for attack-versus-insufficiency attribution, giving the
   field a measurable version of P's assignment step.

My set ranks all three low or gates them out: C2 blocks the prototype (it would
build what P explicitly defers), C1 undervalues the kit (it checks no claim), C5
penalises the benchmark (a large new artefact with no lockstep keeper).

What that says about the choice: the two sets encode two different answers to
what this repository *is*. Mine takes W:487 at its word: the repo is
supplementary material, an archive whose duty is fidelity to two fixed documents.
The alternative takes P's future-work framing at its word: the gap is open, the
authors intend to close it, and the repo is the natural vehicle. Both readings
are grounded in the papers. I chose the archival reading because both papers are
camera-ready and citable, so the repo's near-term readers are reviewers and
readers checking claims, not collaborators extending them; a reader can verify
that premise faster than the alternative's (which depends on unpublished
intentions, e.g. the "paper P5" the empirical README defers to). If the authors'
next act is the method paper, the alternative set becomes the right one, and the
ordering in IDEAS.md inverts.

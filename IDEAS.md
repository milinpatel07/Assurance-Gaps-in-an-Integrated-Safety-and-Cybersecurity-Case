# Ideas

Stage 4 of the ideation task. Every candidate from the seven passes in `passes/`
is listed, including the ones that lose. The ordering is a consequence of the
criteria in CRITERIA.md (C2 scope-fidelity gate, then C3 declared-absence, C1
checkability, C4 addressee, C5 lockstep economy as tie-breaker) and would change
if the criteria changed; CRITERIA.md's closing section states which alternative
set would invert it and what leads under that set (the method prototype, the
instantiation kit, the attribution benchmark).

Passes are cited as P1 (WAISE-only reader), P2 (position-only reader), P3
(both-papers reader), P4 (adversarial critic), P5 (adjacent field: a security,
b ML, c certification, d regulation), P6 (implementer/auditor), P7 (2031 reader).
Dimensions D1–D9 are from DIMENSIONS.md. Paper citations as there (W:, P:).

---

## 1. The space, crossed

The full D1×…×D9 cross is combinatorial; the informative crossings are the ones
the papers themselves put under load. Occupancy below; an empty cell is
information about the work.

**D3 (epistemic status) × D7 (temporal mode)** — the master crossing; the two
papers split it between them:

| | construction (design) | re-evaluation (operation) |
|---|---|---|
| prescribed | occupied: clauses→nodes (`src/standards/`, W tab. 2) | occupied in P text only (P Table 1); no repo artefact |
| deferred (DP) | occupied: DP-1..7 (`decision_points.py`) | **EMPTY.** No paper or artefact says what a design-time DP resolution becomes at runtime. This is the cell most of P3's wants point at: W:483's project ownership policy for G7/G8 *is* a design-time answer to P's assignment step, and neither paper says so. |
| integration-induced absence | occupied: F-3, F-4 (`gaps.py`) | occupied in P text only (assignment, resolution); no repo artefact |
| open methodological | occupied: F-1, F-5 | partially: F-2 / G9 / R4 meet here (modification); text only |

**D5 (evidence scale) × D9 (verification regime):**

| scale | machine-checked | measured/simulated | argued only |
|---|---|---|---|
| binary MC/DC | — | **EMPTY** ("not produced", W:307) | W text |
| coverage count | — | **EMPTY** ("not produced", W:308) | W text |
| statistical (AUROC) | — | occupied twice, oddly: W cites VEHITS2026 simulated 0.982 (W:376); the repo holds *different* measured PointPillars numbers that **neither paper cites** | W, P text |
| attack success rate | — | **EMPTY** ("not produced", W:310) | W, P text |
| risk rating | — | — | P text |

Two anomalies of occupancy worth naming: (i) three of the four G5 evidence
scales have no artefact in any regime except prose, which is exactly the
asymmetry DP-2 asserts, so the empty cells are the finding; (ii)
`data/empirical_results/` occupies the measured cell for a claim no paper makes:
an artefact without a claim, the inverse of the papers' gaps.

**D4 (resolution agent) × D9:** project-policy agents get prose only (no
templates); standardization gets prose only (no draft clause or placement map);
research gets prose only (R1–R4, no protocol). Every agent the papers task is
handed text.

**D8 (generalisation) × D9:** the outer value ("any multi-concern domain",
W:473, P:93) is argued only; no cross-domain instance, no check protocol. The
work's two most future-facing predictions occupy its least-verified cells (P7).

**D1 (lifecycle) × D2 (concern):** occupied and machine-checked (the coverage
matrix, `registry.py`), except modification × 21434, which P states is scoped to
requirements (P Table 1) — an empty cell the position paper itself exhibits.

---

## 2. Reconciliation notes

**Corrections to pass content** (verified against the raw `.tex`; the passes
read compressed text): P2 item 2 claims R4 is never defined — false, P:90
defines "R4, modification". P2 item 8 claims the Sato2025 bibliography entry is
corrupted — false, P:100 is complete. P2 item 10 claims the Gao2022 passage is
garbled — false, P:82 is legible. The *candidates* behind items 8 and 10 survive
(attack signature data; worked cross-validation example); the candidate behind
item 2 is dropped as based on a reading error.

**Conflicts kept, both sides named:**
- **Seam-assertion conflict.** P3 (and P2 item 12) want the repo to state the
  cross-paper mapping (DP-5↔assignment step, DP-2↔R1, F-4↔resolution step,
  G9/F-2↔R4). C2 warns that neither paper states this mapping, so encoding it
  asserts an unpublished claim. Kept as candidate 5 with the conflict marked:
  buildable only if labeled interpretation, not paper content.
- **Prototype conflict.** P2 (items 1, 5, 9), P5b (aggregation rule), P5a
  (triage rule) want the method P explicitly defers to future work. C2 gates
  these; CRITERIA.md's counter-case would select them first. Kept in §4.
- **Count conflict.** P7 wants structural tests that survive revisions; the
  papers claim exact counts (9/7/5/2) and the repo's contract enforces them.
  Resolution kept as "add structural tests alongside, not instead" (candidate 11).
- **Substitution conflict.** P1 (W13) wants SECOND evidence matching the paper;
  the empirical README's deliberate decision is to substitute PointPillars and
  say so. No artefact can satisfy P1-W13 without new training runs; what can be
  built is louder surfacing (candidate 1 includes it).

---

## 3. Ranked candidates (pass the C2 gate)

Format per entry: what — cell — passes — scores (C3 / C1 / C4 / C5) — risk of
asserting beyond the papers.

**1. Scope-fidelity repairs.** Fix the README's false "paper not included"
statement and dropped-word title; reconcile the 193 (W:487) vs 192 (repo) test
count; retire or relabel the stale generated `table5/6` whose captions collide
with the paper's `tab:inconsistencies`/`tab:gaps`; add provenance READMEs for
`docs/figures/` and `data/carla_configs/`; state in the top-level README that
the WAISE paper's evidence (c) cites the simulated VEHITS2026 result while
`data/empirical_results/` is a separate, uncited PointPillars body. — Cell: not
an occupant of the space; a repair of existing occupants. — Passes: P1(W13,
W14 adjacent), P7(C8), audit. — Scores: C3 low / C1 high / C4 med / C5 high
(removes copies). — Risk: none; it removes false assertions rather than adding
any. Ranked first because C2 is the gate: the repo currently misstates the
papers, and no addition should outrank stopping that.

**2. The consolidated machine-readable clause-to-node export.** One file (or
one generated artefact) holding the full node↔clause↔claim map, edition-keyed
(ISO/PAS 8800:2024 etc.), replacing the inert `configs/standards.yaml` and the
three scattered encodings. — Cell: D3 prescribed × D9 machine-checked, all D2
values. — Passes: P1(W2), P2(4), P4(W4), P6(W6, W12), P7(C1, C8). — Scores: C3
high (W:226 *promises* this exists "in machine-readable form in the
supplementary material"; today it is scattered, so the paper's own claim about
the repo is unmet) / C1 very high (the corpus every universal negative is
checked against) / C4 high (engineer, assessor, critic) / C5 high if it
*replaces* copies rather than adding one. — Risk: low; encodes only citations
the papers already make. Care: an edition field must not imply the analysis was
run against editions it was not.

**2b. Absorb the camera-ready classifications the code never took up.** (Added
after iteration 1; blocked pending an author decision.) The camera-ready WAISE
paper types DP-2 as "S, M", gives F-1 the phases "Concept, Verification" and F-3
"Verification, Operation", and adds ISO 24089 to F-2's coverage row. The code
carries a single type and a single phase per item, and the tests assert those
single values. — Cell: D3 × D9, the lockstep itself. — Passes: found by the
iteration-1 standards practitioner and independently by the SAFECOMP reviewer,
not by any generation pass. — Scores: C3 med / C1 very high (the repo's central
contract is that these three agree) / C4 high / C5 high (it removes drift). —
Risk: making the fields multi-valued changes the 3 structural / 2 terminological
/ 2 methodological split that the paper's own prose depends on (the prose groups
DP-2 under structural while the table types it "S, M"), so the correct value is a
judgment call for the authors, not a repair. Ranked here because it is the same
defect class as candidate 3 but worse: the paper carries content the code lacks,
rather than the two merely naming the same thing differently.

**3. The label crosswalk (intra-work).** A single table: paper DP-1..7 ↔ code
I-1..7; paper F-1..5 ↔ code Gap-1..5; README phrasing; the GSN YAML's stale
"Gap-2" tag on G9. — Cell: D9, spanning vocabularies. — Passes: P1(W3), P5c(2),
P6(W11), P7(C2); highest convergence of any candidate (with 5). — Scores: C3
med / C1 high (unblocks every other cross-check) / C4 high (auditor named by
W's own traceability claim) / C5 high (one small file, one keeper: a test could
assert it). — Risk: none; the identity of these objects is a fact of authorship,
not an interpretation.

**4. Derived, not asserted, counterfactual invisibility.** Recompute "Gap-3 and
Gap-4 appear in no single standard's claim set" from the claim corpus (candidate
2) instead of the hard-coded `invisible_gaps` literals in `counterfactual.py`.
— Cell: D3 integration-induced × D9 machine-checked. — Passes: P4(W3), P4(W8
partially). — Scores: C3 med / C1 very high (the papers' self-described central
verification, currently typed in; W:487 claims the tests check exactly this) /
C4 low (serves the critic, whom the papers never address; C4's stated blind
spot) / C5 high (removes a hand-set copy). — Risk: low, with one honest hazard:
the derivation could fail, in which case the repo must report that, not tune it.

**5. The seam map (cross-paper crosswalk).** A document pairing the two papers'
numbered objects with the textual basis for each pairing: DP-5/F-3 ↔ assignment
step; DP-2 ↔ R1; F-4 ↔ resolution step; G9/F-2 ↔ R4; G6/DP-6 ↔ anomaly source;
F-1 ↔ the missing anomaly threshold; and the one asymmetry that breaks the
pattern, attack success rate (design) vs binary event indicator (operation),
P3(15). — Cell: the empty D3-deferred × D7-re-evaluation cell, the largest
declared absence between the papers. — Passes: P3(1–12, 15), P2(12), P6(W14). —
Scores: C3 very high / C1 med (each pairing cites passages, checkable) / C4 med
/ C5 med. — Risk: **the named seam-assertion conflict**: neither paper states
these equivalences. Buildable only as clearly-labeled interpretation with
per-pairing citations; a version that presents the mapping as paper content
fails C2.

**6. Annex B base pattern encoded separately, with a computed delta.** The
six-goal base as its own YAML/builder, and the extension derived as a diff. —
Cell: D3 prescribed × D7 construction. — Passes: P1(W1, W12), P6(W1 partially).
— Scores: C3 med / C1 high (makes "extends from 6 to 9" mechanical rather than
narrated) / C4 med / C5 med (one new encoding, but diffable against the
integrated one by a test). — Risk: low; care that the base encoding is Annex B
as published, not a back-formation from the integrated pattern.

**7. The Warg & Skoglund arm in `base_pattern_sensitivity.py`.** Add the
concern-hierarchy alternative the paper itself names and rejects (W:233), and
derive rather than hand-set which findings survive it. — Cell: D3 × alternative
D6 topology. — Passes: P4(W5). — Scores: C3 med / C1 high / C4 low (critic) /
C5 med. — Risk: low; the paper opened this door itself. Same hazard as 4: the
answer must be reported even if it weakens W:233's retention argument.

**8. Position Figure 1 as a machine-readable argument file.** The top claim,
three concern re-evaluations, and the two dashed missing steps, in the same YAML
convention as `gsn/`. — Cell: D3 absence × D7 re-evaluation × D9
machine-readable. — Passes: P2(3), P3(7 partially). — Scores: C3 high (first
repo artefact for the position paper at all) / C1 med / C4 med / C5 med. —
Risk: low if it encodes exactly P's figure, dashes and all; a version that
develops the dashed nodes is candidate 24 and gated.

**9. The two project-policy templates.** Blank, fillable skeletons for the
G7/G8 ownership policy and the G5 evidence-admissibility policy that W:483 says
projects must write. — Cell: D4 project-policy × D9 (currently prose-only). —
Passes: P1(W6, W7), P6(W2, W3), P5a(2 partially). — Scores: C3 high (the papers
demand these artefacts of every adopter and provide none) / C1 low (checks no
claim; C1's stated blind spot) / C4 very high (the engineer, the most-named
addressee) / C5 med. — Risk: medium: a template's field choices quietly assert
what a compliant policy contains, which no standard prescribes; must be framed
as one possible shape, citing the DP-5 worked example (W:380) as its only
instance.

**10. Decision-point resolution register.** A per-DP log schema (decision,
rationale, owner, status) turning the catalogue into an auditable work product;
subsumes P5c's UL-4600-style gap register for F-1..5 and the three unproduced
evidence legs. — Cell: D4 project × D3 deferred. — Passes: P6(W4), P5c(1, 3),
P1(partially). — Scores: C3 med / C1 low / C4 high / C5 med. — Risk: same
family as 9; schema-as-assertion, framed as offering.

**11. Structural tests alongside the count tests.** Assertions phrased as the
durable claims are ("G5 receives claims from all normative standards", "at least
one finding absent from every single-standard view") in addition to `== 9`,
`== 7`. — Cell: D9 machine-checked × D8 durability. — Passes: P7(C3). —
Scores: C3 low / C1 high / C4 miss (2031 reader unnamed; C4's blind spot) / C5
high. — Risk: none if added alongside; replacing the count tests would breach
the repo's own contract.

**12. Revision-sensitivity map.** A short table: which finding closes under
which plausible amendment (8800 adds quantitative targets → F-1; 21434 adds case
re-evaluation → P's gap narrows; Table 1-1 adds 21434 → that observation dies).
— Cell: D8 × D3. — Passes: P7(C6). — Scores: C3 med / C1 med / C4 miss / C5
high (small, prose, one file). — Risk: low; the papers themselves predict these
closures (P:93, W F-2 discussion of ISO 24089).

**13. Falsifiable-prediction registry.** The two generalisation predictions
(W:473, P:93) restated as checkable propositions with confirm/refute conditions
and a template for a cross-domain instance. — Cell: D8 outer × D9. — Passes:
P7(C4), P1(W16). — Scores: C3 med / C1 med-high (makes an argued claim
checkable in principle) / C4 miss / C5 high. — Risk: medium: writing the
refutation condition is itself an interpretive act the papers did not perform.

**14. Second-assessor extraction kit.** The Step-1 claim set exported as a
per-standard worksheet a second reader can independently re-do, with a
reconciliation log format. — Cell: D9 × the single-assessor limitation (W:485).
— Passes: P1(W15), P4(W8), P5c(4), P6(W12). — Scores: C3 med (the papers name
this limitation themselves) / C1 high in principle (the only path to an external
oracle) / C4 low / C5 med. — Risk: low for the kit; the actual second extraction
is new research work the repo can invite but not contain.

**15. Operation-phase clause tagging.** Attach P Table 1's operation-phase
clauses (21448 Cl.13.4; 8800 re-evaluation; 21434 Cl.8) to the goals they sit
under in the registry, tagged by phase. — Cell: D1 operation × D2 × D9. —
Passes: P3(11). — Scores: C3 med / C1 med / C4 med / C5 med. — Risk: low;
encodes P's own table, though the goal attachment is a mild seam assertion
(shares candidate 5's caveat).

**16. Saturation statement for the DP catalogue.** Either an enumeration
argument over all junction nodes showing no eighth deferral, or an explicit
"seven is a floor" note in the catalogue. — Cell: D3 deferred, completeness of.
— Passes: P4(W2). — Scores: C3 low / C1 med / C4 low / C5 high (a sentence). —
Risk: none for the floor-statement; the enumeration variant could fail and must
then be reported.

**17. Instantiation guide for the five-step method.** A how-to walking a new
component through Steps 1–5, separating pattern from instance. — Cell: D8 inner
→ class transfer × D4 project. — Passes: P1(W11), P6(W1, W7). — Scores: C3 low
/ C1 low / C4 high / C5 low (a long prose artefact needing maintenance). —
Risk: medium: generalises the method beyond its one published application.

**18. Supplier/OEM interface note for C1/C2.** What the encompassing system
must supply into C1 (ASIL) and C2 (TARA) and what returns upward, per W:231. —
Cell: D6 system-interface (nearly empty). — Passes: P6(W9). — Scores: C3 med /
C1 low / C4 med / C5 high. — Risk: medium; away-goal semantics beyond what W
states.

**19. Cross-domain release checklist (F-4).** Sign-off gate instrument across
the four domains. — Cell: D4 project × D3 II. — Passes: P6(W10), P5d(3). —
Scores: C3 med / C1 low / C4 high / C5 med. — Risk: medium-high: F-4's point is
that no criteria exist; a checklist with content asserts some.

**20. SACM/interchange export.** — Cell: D9 tooling. — Passes: P6(W5). —
Scores: C3 low / C1 low / C4 med / C5 low (a fourth argument encoding to keep
true). — Risk: low conceptually, high maintenance.

**21. Conformance checker for user-supplied arguments.** Tests that ingest a
project's GSN and check pattern conformance. — Cell: D9 × D4 project. —
Passes: P6(W8). — Scores: C3 low / C1 med / C4 high / C5 low (large moving
artefact). — Risk: medium: defining "conforms to the pattern" makes normative
choices the paper does not.

**22. Monitor-signal inventory for G6.** Concrete list of runtime signals with
detectors and thresholds. — Cell: D1 operation × D5. — Passes: P5b(4), P3(5
partially). — Scores: C3 med / C1 low / C4 med / C5 med. — Risk: medium-high;
G6's finding is that the interaction is undefined, and a stack answers it.

**23. Threat catalogue keyed to TARA and goals.** Structured expansion of the
three TS entries now stranded in the inert `configs/case_study.yaml`. — Cell:
D2 21434 × D9. — Passes: P5a(1). — Scores: C3 low / C1 med (would make
`configs/` loaded or retired, echoing candidate 2) / C4 med / C5 med. — Risk:
medium; new threat scenarios beyond the paper's TARA context.

---

## 4. Gated candidates (fail the C2 gate; listed, not discarded)

Each of these is what the alternative criterion set in CRITERIA.md would select
first. Building any of them asserts something the papers deliberately withheld.

**24. Defeater-propagation model.** Extend `src/gsn/model.py` with
defeater/eliminative constructs and propagate status to G1. — Passes: P2(5),
P3(8). — Would assert: the candidate direction P:90 sketches and explicitly
leaves open ("Whether this satisfies R1–R4 in full ... remain open"). Encoding
P's sketch as a static diagram is candidate 8; making it execute is the method.

**25. Attack-vs-insufficiency benchmark.** Labeled anomaly instances with
ground-truth cause. — Passes: P2(6), P5b(2). — Would assert: that the
assignment problem is a solvable two-class task with this data; also the
strongest research artefact on the list, per CRITERIA.md's counter-case.

**26. Worked step-2 resolution example.** — Passes: P2(9). — Would assert: a
combination rule where P:82–84 argues none exists.

**27. Evidence-aggregation prototype (common-scale fusion).** — Passes:
P5b(3), P1(W5). — Would assert: an answer to DP-2, the central finding that no
rule exists; even as a strawman it shifts the claim.

**28. Synthetic attack-success-rate generator for leg (d).** — Passes: P5a(4).
— Would assert: an occupied fourth evidence leg where the paper's figure
deliberately shows a dashed "not produced" node; a seeded illustration here is
more misleadable than the weather one, because the absence is the finding.

**29. Field-occurrence reporting schema / incident record.** — Passes: P5a(3),
P5d(1), P7(C5), P3(14). — Would assert: the report format R3 says is undefined.
The nearest C2-safe artefact is candidate 8 plus a prose note; the schema itself
is method design.

**30. Draft clause / placement map for standardization.** — Passes: P2(13). —
Would assert: normative text P:93 only calls for. (A placement map alone, citing
existing clause structure, is closer to the gate than a draft clause.)

**31. Regulatory obligation matrix (WP.29 / R155 / R156 → missing steps).** —
Passes: P5d(2). — Would assert: an analysis W:489 explicitly scopes out.

**32. Triage-rule specification (Sigma-style).** — Passes: P5a(2). — Would
assert: the assignment method, gated as 24–26.

**33. OOD baseline sweep for the 0.982 indicator.** — Passes: P5b(1). — Out of
these papers' scope: that evidence belongs to the VEHITS2026 companion and the
unpublished P5; this repo asserting baselines for it would misattribute.

**34. Assignment-threshold definition (what counts as an anomaly).** — Passes:
P2(15, flagged weak there). — P scopes detection out deliberately (P:19); the
want is real but addressed to a different paper.

**35. Effort/resourcing model behind `estimated_effort`.** — Passes: P6(W15,
flagged weak). — Would assert: cost claims with no basis in either paper.

---

## 5. Selected by no criterion, judged to matter anyway

**A. The Windows-usable GSN render path** (P1-W14; audit §7.3). No criterion
sees it: it checks no claim (C1), occupies no absence (C3), serves no named
addressee (C4). Yet on the documented host the repo's own reproduction
instructions fail at `make gsn-install`. What this reveals: the criteria are
entirely about *meaning* (fidelity, absence, checkability) and blind to
*operability*. A criterion set derived from papers will always be, because
papers do not state their tooling assumptions.

**B. Making `data/empirical_results/` claimed or moved.** The measured
PointPillars layer supports a claim no paper makes (Section 1's occupancy
anomaly). No criterion selects resolving it: it is not an absence (C3 sees
missing artefacts, not unclaimed ones), and C2 polices artefacts asserting
beyond papers, not artefacts asserting nothing. Yet an unclaimed empirical body
inside a claims-checkable repo will read, to a reviewer, as either orphaned or
quietly overclaiming. What this reveals: the criteria assume every artefact
exists to serve a claim; they have no category for evidence awaiting its paper
(the unpublished P5), which is precisely this repo's situation.

**C. The pass files themselves.** Seven readers' unmet wants are now the best
map of this repository's audience, and no criterion values keeping them (they
check nothing, fill nothing, serve no named addressee). What this reveals: the
criteria optimise the repo for its two fixed papers, and assign no value to
knowing who reads it.

---

---

## 5c. Ranked first now: check the GSN YAML against the builder

Added after the representation-drift finding. This displaces the previous head of
the list, and the reason is evidence rather than preference.

**What it is.** `gsn/integrated_pattern.gsn.yaml` and `build_integrated_gsn()`
both describe the nine-goal argument. Nothing compares them. Compare node sets,
support relations, context and assumption links, and undeveloped status, and fail
the build on an unexplained difference, with the same recorded-exception
mechanism used in `tests/test_representation_consistency.py`.

**Why it now outranks everything else.** The identical defect class, a fact
written down twice with nothing holding the copies together, was found to have
reached a published claim (REPO_AUDIT.md section 5b.2). This is the one remaining
pair of that kind, and `docs/working-practices.md` describes it in the same words
that were used of the pair that had already drifted, "kept consistent" by hand.
One difference is known to exist: the YAML still tags G9 `Gap-2`. The asymmetry
that makes it urgent is that the rendered SVGs a poster reader sees come from the
YAML, while every tested claim comes from the builder. A drift here is visible to
readers and invisible to the suite.

**Cell:** D9 verification regime, over the D6 argument structure.
**Passes:** none. Found by building, which is itself worth noting: the seven
generation passes did not predict it, and the adversarial pass predicted only its
class.
**Scores:** C3 med / C1 very high / C4 med / C5 very high (it adds no copy; it
constrains two that exist).
**Risk:** none while it only compares. Deciding which side wins where they differ
is a paper-fidelity judgment for the authors, not a code change.

## 6. Added by iteration 1

**D. Enforce every documentation table that asserts agreement with code.**
`data/carla_configs/*.yaml` and `configs/*.yaml` are loaded by nothing, so their
values could drift from `src/` unnoticed. Iteration 1 added
`tests/test_config_documentation.py` (11 tests) to stop that. The general rule
this produced: any table in any README claiming that a documented value matches a
value in the code must be backed by a test, or it is an assertion the reader has
to trust. Apply to later candidates, in particular candidate 3 (the crosswalk,
which should be machine-checked, not just written) and candidate 2 (the clause
export). — Scores: C1 high, C5 high. — Risk: none; it checks the repository
against itself and asserts nothing about the papers.

**E. The notebook question, stated properly.** Deferred to its own analysis (see
the standing instruction). The criterion to apply is whether a reader's
understanding depends on seeing a value change, rather than on reading a result.
On that test the counterfactual notebook (remove a standard, watch which findings
vanish) is warranted only if the vanishing is derived rather than read from the
hard-coded `invisible_gaps` literals, which makes it depend on candidate 4. The
G5 four-scale notebook is warranted because the reader has to try the combination
and fail. A notebook that replays already-computed results is decoration. Full
ranked analysis still to be written into this file.

**F. Reproducibility by a stranger is not yet met.** Named as a gate in the
standing instruction and not yet satisfied: dependencies are lower-bound only
with no lockfile, there is no run manifest recording commit hash and package
versions, and the empirical layer is not regenerable at all. Iteration 1
confirmed the seeded path is deterministic across two runs, which is necessary
but not sufficient.

## Ordering statement

The order in Section 3 follows CRITERIA.md: C2 as gate, then C3, C1, C4, C5.
Under the alternative set stated there (research, adoption, community value),
Section 4's candidates 24, 25, and 27 and Section 3's candidate 9 would lead,
and Section 3's candidates 1–4 would drop to the bottom as housekeeping. The
ordering is a consequence of choosing the archival reading of what this
repository is; it is not a property of the candidates.

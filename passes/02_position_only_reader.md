# Pass 02: Position-paper-only reader

Persona: a reader who has read only the SAFECOMP position paper
(`paper/safecomp2026-position/CR_position_paper.tex`) and wants to act on it: build a
method that satisfies its requirements R1-R4, evaluate the defeater / eliminative-argumentation
direction it sketches, prepare a standardization comment, and check its clause-level claim that
no standard clause performs assignment or resolution. This reader does not know the WAISE paper;
it appears only as citation `[PatelJungWAISE2026]`. The reader has also skimmed `README.md` and
`REPO_AUDIT.md` to learn what the repository actually holds.

Prominent caveat, stated once for the whole list: the position paper is argued at the clause
level and by design ships no supporting artefacts. Everything executable in this repository
(`src/`, `gsn/*.gsn.yaml`, `data/`, `tests/`) backs the other paper, the WAISE GSN-integration
paper, in that paper's own vocabulary (goals G1-G9, labels DP/F/I). So most of the wants below
are unmet by construction, not by oversight. They are recorded anyway, because the point of the
pass is to name what a reader who wants to act on the position paper cannot get here.

Each item is one want: what it is, the passage that creates the need, and why the current
repository does not satisfy it.

## Wants

1. A reference implementation, or even a skeleton, of a method satisfying R1-R4. The paper's
   closing framing is "the paper specifies the requirements a method that closes the gap must
   satisfy" and then states R1, R2, R3. A reader who wants to attempt such a method has nothing
   to start from: the repository's entire `src/` tree is the WAISE five-step design-time
   integration, which stops at constructing the argument pattern and never touches an
   operation-phase assignment or resolution procedure. There is no module, no interface, and no
   stub named for R1-R4.

2. The text of R4. The requirements section names R1 (heterogeneous evidence), R2 (assignment),
   and R3 (traceability and currency), but the same paragraph then asks "Whether [the candidate]
   satisfies R1--R4 in full". R4 is referenced but never defined anywhere in the paper. A reader
   trying to implement or check the requirement set cannot, because the fourth requirement is
   missing from the paper and, since the repository does not encode the position paper at all,
   there is no second source to recover it from.

3. A machine-readable version of the Figure 1 top-claim structure with the two missing steps
   marked. Figure 1 is hand-drawn TikZ showing one top claim, three concern-specific
   re-evaluations (ISO 21448, ISO/PAS 8800, ISO/SAE 21434), and a dashed "missing step 2,
   resolution into one judgment (no clause)" plus a missing step 1 (assignment). A reader who
   wants to extend that argument structure wants it as GSN or similar. The repository's
   `gsn/integrated_pattern.gsn.yaml` and `gsn/evidence_convergence.gsn.yaml` encode the WAISE
   nine-goal pattern, not the position paper's top-claim-with-two-holes figure, so there is no
   editable source for Figure 1.

4. The clause corpus behind Table 1's negative claims. Table 1 asserts that ISO 21448 Clause 13.4
   defines a SOTIF argument on a field result but not the result-to-argument mapping, that
   ISO/PAS 8800 does not define which evidence re-opens an element, and that ISO/SAE 21434 defines
   no re-evaluation case; the table footer states that no standard assigns an unlabeled anomaly to
   a concern (missing step 1) or resolves concern-specific results into one judgment (missing
   step 2). A reader who wants to verify this negative existence claim needs the actual clause
   text, or at least a structured clause inventory to search. The repository has
   `configs/standards.yaml` and `src/standards/*.py`, but per `REPO_AUDIT.md` those are hand-coded
   claim objects built for the WAISE integration (and the `configs/` copy is loaded by nothing),
   not a faithful clause map of the three standards, so the reader cannot confirm "no clause does
   assignment or resolution" against any clause-level artefact here.

5. A defeater-annotated argument model to prototype the candidate direction. The paper proposes
   treating the anomaly as a defeater to the top claim, following eliminative argumentation and
   Assurance 2.0 (`Bloomfield2024`), with assignment attaching a defeater to a concern's sub-claim,
   resolution propagating its status to the top claim, and an unresolved defeater standing as R2's
   residual outcome. A reader who wants to evaluate whether this actually satisfies R1 and R2
   wants a model that carries defeaters and propagates their status. The repository's GSN data
   model (`src/gsn/model.py`) is plain GSN (Goal, Strategy, Context, Assumption) with no defeater,
   rebutter, or eliminative-argument concept, so there is nothing to build the prototype on.

6. A benchmark of unlabeled anomalies with ground-truth cause. The paper's core example is one
   missing scene region that could be a performance insufficiency (rain, sparse returns, rare
   object pose) or an attack (spoofing, relay), and it states plainly that "how to benchmark
   [the method] remain open". A reader who wants to build and test the R2 assignment step needs a
   set of anomaly instances each labeled attack versus insufficiency. The repository's `data/` has
   only seeded synthetic weather illustrations and measured PointPillars AUROC / MDR-MFAR; none of
   these carry an attack-versus-insufficiency cause label, and none are attack traces, so no
   assignment benchmark can be assembled from what is here.

7. Concrete instances of the four incommensurable evidence scales for one anomaly. R1 requires a
   method to accept evidence at "different measurement scales", and the paper names them: a
   calibrated probability, an ensemble disagreement value, a binary event indicator, and a risk
   rating. A reader who wants to test a combination-free treatment wants all four produced from a
   single anomaly. The repository can supply ensemble-disagreement and uncertainty numbers (tied
   to WAISE G5/G6), but has no binary cybersecurity event indicators and no risk ratings, and
   nothing that ties the four scales to one shared event.

8. The Sato on-road attack signature. The motivation rests explicitly on a "demonstrated on-road
   attack" (`Sato2025`) that produces a dropout indistinguishable from a performance insufficiency.
   A reader who wants to work the attack side of the assignment problem wants that attack's
   monitor-output signature to compare against a weather-induced dropout. The repository holds no
   attack data and no reproduction of Sato, and the bibliography entry for this line is itself
   corrupted in the source (an entry with only "LiDAR NDSS" and a partial page range, no author or
   title), so the reader cannot even chase the citation cleanly.

9. A worked resolution of concern-specific re-evaluations into one judgment (step 2). The paper
   argues that step 1 alone would not close the gap: even if every anomaly were labeled, the
   concern-specific results still meet at the top claim on different scales and "no rule combines
   them". A reader who wants to build step 2 wants at least one worked example resolving a SOTIF
   re-evaluation, an AI-safety re-evaluation, and a cybersecurity re-evaluation into a single
   judgment on the argument. No such artefact exists in the repository; the WAISE code integrates
   claims at design time and produces no operational resolution.

10. The 2022 cross-validation example, written out. The section "Assignment Resolution Anomaly"
    points to a 2022 autonomous-driving case that uses non-malicious multi-sensor cross-validation
    and maps re-evaluations across ISO 21448 and ISO/SAE 21434 (`Gao2022`), but the passage is
    garbled in the source and gives no usable detail. A reader who wants to reuse that
    cross-validation idea as a starting point for assignment wants the example spelled out with its
    inputs and outputs. Neither the compiled paper text nor the repository provides it.

11. A model of the operational conditions the method must run under. The paper states that
    operation adds conditions design-time analysis does not face: evidence arrives asynchronously,
    the component changes under updates, and the reporting obligation requires a current judgment on
    demand (`UNECE2026`). A reader who wants a method that maintains a current judgment over
    asynchronous, time-varying streams wants a temporal or state model to build against. Everything
    in the repository is static and single-shot (seeded one-pass analysis), so there is no
    operational or streaming model to extend.

12. A crosswalk from the position paper's step-1 / step-2 framing to the cited WAISE convergence
    point. The paper twice cites `[PatelJungWAISE2026]` as the place where the concern-specific
    activities meet under one top claim, which is exactly where it says the gap must be closed. A
    reader who has only the position paper wants to see how R1-R4 attach to that meeting point. But
    this reader does not have the WAISE paper, and the repository describes the meeting point only
    in WAISE vocabulary (node G5, and the DP/F/I labels) with no mapping back to the position
    paper's "assignment step" and "resolution step". So even the repository material that is
    relevant is not reachable from the position paper alone.

13. A draft clause or placement map for the standardization comment. The final section says a
    revised ISO/PAS 8800 and ISO/SAE 21434 "could add: an assignment step, a resolution step, and
    an interface between the concern-specific activities". A reader preparing a standardization
    comment wants a concrete draft clause, or at least a map of where in each standard's clause
    structure the addition would sit. The repository has no clause-change proposal, and its
    standards modules encode claims for the WAISE argument rather than the clause skeletons of
    ISO/PAS 8800 and ISO/SAE 21434 that a committee submission would annotate.

14. The scoping behind the two negative existence claims. Motivation rests on absence: "We are
    aware of no published incident that attributes a deployed automated-driving failure to this
    ambiguity" and, via the Relation-to-Existing-Work section, no existing method assigns runtime
    monitor output across concerns or resolves the results into one judgment. A reader who wants to
    trust and act on these negatives wants to see the search scope behind them. The repository holds
    no literature-scoping artefact; the related-work section lists five references (AMLAS,
    Denney, Warg, Johnson and Kelly, Cardoso) with no systematic survey to inspect. (Weaker want:
    a position paper is not obliged to ship a survey, but the reader still cannot check the claim.)

15. A definition of the anomaly-detection threshold that triggers the whole procedure. The
    introduction says re-evaluation is activated by "a change in monitor output or a software
    update" and treats an anomaly as an "abnormal monitor output", but never says what makes an
    output abnormal. A reader building the R2 assignment step needs the upstream threshold that
    decides an output counts as an anomaly at all. The paper leaves it undefined, and the
    repository's seeded uncertainty and weather thresholds are set for WAISE G5/G6 claims, not for
    an operational anomaly definition, so there is no threshold artefact to reuse. (Weaker want:
    the paper deliberately scopes detection out and focuses on assignment and resolution, so this
    may be out of scope by intent.)

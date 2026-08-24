# Pass 03: Both-Papers Reader

A reader who read the WAISE 2026 GSN-integration paper and the SAFECOMP 2026
position paper back to back keeps hitting objects that live only in the seam
between them. The position paper cites the WAISE paper (`PatelJungWAISE2026`)
four times but never maps its own numbered items (step 1, step 2, R1-R4) onto
the WAISE paper's numbered items (DP-1..DP-7, F-1..F-5). The WAISE paper never
mentions that its static pattern would later be re-evaluated in service. The
repository encodes only the WAISE design-time objects, under a third vocabulary
again (I-N, Gap-N). Below are the things this reader wants and cannot get.

## Wants

1. **The runtime instance of DP-5/F-3.** The WAISE paper's DP-5 is the
   cybersecurity-SOTIF boundary resolved at design time by allocating a failure
   mode (false negative from reduced point density) to G7 or G8 as "a project
   decision" (Table `tab:dp5`, F-3 "boundary unowned at the standards level").
   The position paper's whole step-1 problem is that the same boundary, faced at
   runtime, has "no concern label" and "does not show whether cause falls SOTIF,
   AI safety, cybersecurity" (Sec. Assignment/Resolution, Fig. 1). These are the
   identical boundary at two lifecycle phases, but neither paper says so. The
   repo has DP-5/F-3 hard-coded in `src/analysis/decision_points.py` and
   `src/analysis/gaps.py` with only a design-time framing; there is no object
   representing the same boundary as an operational assignment problem, and no
   crosswalk from `I-5`/`Gap-3` to the position paper's "missing step 1".

2. **R1 stated as the operational face of DP-2.** The WAISE DP-2 finding is that
   G5's four evidence types "are disjoint by design" and "no standard defines how
   the disjoint evidence types combine" (Sec. `sec:inconsistencies`, Fig. 2b:
   MC/DC, scenario coverage, ensemble AUROC, adversarial penetration). The
   position paper's R1 demands accepting "evidence different measurement scales
   one claim without imposing common scale" and lists "calibrated probability,
   ensemble disagreement value, binary event indicator, risk rating" (Sec. The
   Position; Sec. Assignment/Resolution). This is the same four-way scale
   asymmetry reappearing at operation. Neither paper states R1 is DP-2 read at
   runtime. The repo's `src/analysis/evidence_convergence.py` models only the
   design-time convergence at G5; it cannot express the same four scales
   aggregating over an asynchronous operation-phase evidence stream.

3. **Step 2 stated as F-4 at re-evaluation time.** WAISE F-4 says "no standard
   requires evaluating the combined residual risk across domains" and the
   "cross-domain release decision becomes visible only under a single top-level
   goal" (Sec. `sec:gaps`). The position paper's step-2 gap is that no clause
   "resolves concern-specific results into one judgment on assurance argument"
   (Table `tab:standards` footnote; Fig. 1 "Missing step 2"). F-4 is the release
   decision at design time; step 2 is the same decision on re-evaluation. Neither
   paper draws the equivalence. The repo carries F-4 as `Gap-4` with a static
   "Integration" lifecycle phase only, with no operational re-evaluation twin.

4. **The position paper as the development of WAISE's undeveloped G9.** The WAISE
   pattern marks G9 (modification re-assurance) "undeveloped because no single
   standard prescribes the complete re-assurance workflow" (F-2, OTA
   re-assurance). The position paper's R3/R4 require a judgment "re-opened,
   consistent modification provisions ISO/PAS 8800 ISO 26262" triggered by a
   "software update" under WP.29 (Sec. Introduction; Sec. The Position). The
   position paper is, in effect, the specification for what G9 must contain, yet
   neither paper says the position paper develops G9. The repo flags G9
   undeveloped in `src/analysis/completeness.py` and in
   `gsn/integrated_pattern.gsn.yaml` ("[UNDEVELOPED - Gap-2]") but has no link
   from that node to the position paper's R1-R4.

5. **G6 monitors as the source of the position paper's anomaly.** WAISE G6
   "coordinates three parallel monitoring scopes (AI, SOTIF, cybersecurity) whose
   interaction no standard defines" (DP-6, monitoring scope overlap). The
   position paper opens from exactly those monitor outputs: "predictive
   uncertainty ensemble disagreement, distribution-shift indicators,
   cybersecurity events" (Sec. Introduction). The anomaly needing assignment is
   the output of WAISE's G6, and DP-6's undefined interaction at design time is
   what produces the unlabeled anomaly at runtime. Neither paper connects G6/DP-6
   to the anomaly source. The repo has no monitor-output model; `I-6` in
   `decision_points.py` is a static scope-overlap entry, not a generator of
   operational anomalies.

6. **The one case-study artefact playing two roles.** Both papers rest on the
   same ensemble-disagreement result (`PatelJungVEHITS2026`): the WAISE paper
   uses it as G5 verification evidence at design time (AUROC 0.982, "three-
   indicator acceptance gate that retains 22.0% of detections"); the position
   paper uses the same ensemble disagreement as a runtime monitor output whose
   anomaly must be assigned (Sec. Introduction). Neither paper notes that the
   design-time acceptance gate is precisely the threshold whose runtime crossing
   is the anomaly. The repo (`src/perception/`, `src/evaluation/`) models the
   detector and gate as a one-shot design-time evaluation; nothing represents the
   same gate producing an operation-phase event.

7. **A single argument object that is the same G1 at design and at re-evaluation.**
   WAISE G1 is "the AI-based perception component satisfies the integrated safety
   and cybersecurity requirements allocated to it" constructed once. The position
   paper's "one top claim, item acceptably safe secure" is that same case, now
   requiring "current judgment on demand" under a reporting duty (Sec. The
   Position; Sec. Implications). The reader wants one GSN artefact that is G1 at
   both phases, but `src/gsn/integrated_pattern.py::build_integrated_gsn()` builds
   only the static design-time tree; there is no versioned or temporal
   representation of the same argument being re-opened in service.

8. **The WAISE pattern re-expressed in defeater / Assurance 2.0 terms.** The
   position paper's candidate direction "treats anomaly defeater top claim ...
   following eliminative argumentation" so that "assignment attaches defeater
   concern's sub-claim, resolution propagates its status top claim" (Sec. The
   Position, citing `Bloomfield2024`). This is a claim about how the WAISE 9-goal
   tree behaves under a defeater attached to G7, G8, or the AI leg, yet the WAISE
   paper never mentions defeaters and its GSN is classic goal/strategy/solution.
   The repo's `src/gsn/model.py` has no defeater or eliminative-argumentation
   construct, so the reader cannot see how a defeater on G7/G8 would propagate to
   G1.

9. **F-1 as the precondition for the runtime assignment threshold.** WAISE F-1
   says "no published method derives application-specific quantitative targets for
   an AI component such as the LiDAR detector AUROC metric" (Sec. `sec:gaps`). The
   position paper needs a defined outcome for an "unassignable case" (R2) and a
   threshold that decides when a monitor output counts as an anomaly reopening a
   concern. Without F-1's quantitative acceptance criterion there is nothing to
   test the monitor output against. Neither paper states that F-1 is the missing
   precondition for the position paper's step-1 threshold. The repo carries F-1
   as `Gap-1` with a static "Concept, Verification" phase and no operational
   threshold role.

10. **DP-1's three non-interchangeable frameworks reappearing as "which
    framework's threshold did the anomaly trip".** WAISE DP-1 is that ASIL
    (26262), residual-risk acceptance (21448), and cyber risk values (21434) are
    "not interchangeable by design" and no standard reconciles them into "a single
    sufficiency judgement" at G1. At runtime the same non-interchangeability
    decides which framework scores an anomaly, since the position paper notes the
    per-concern results are "evidence different measurement scales ... no rule
    combines them" (Sec. Assignment/Resolution). Neither paper links DP-1 to the
    runtime scoring choice. The repo's `I-1` in `decision_points.py` is
    design-time only.

11. **Operation-phase clauses mapped onto WAISE goals.** The position paper's
    Table `tab:standards` lists operation-phase clauses (ISO 21448 Cl.13.4;
    ISO/PAS 8800 re-evaluate-after-change; ISO/SAE 21434 monitor/evaluate/treat)
    and what each leaves undefined. The WAISE paper maps clauses to goals in
    Table `tab:goals` but its G6/G7/G8/G9 rows do not use these operation-phase
    clauses. A reader wants the position paper's operation-phase clauses attached
    to the WAISE goals they belong under. The repo's clause data in
    `src/standards/*.py` and `configs/standards.yaml` is weighted to the design
    lifecycle and does not tag clauses as operation-phase for these goals.

12. **The crosswalk table itself.** The reader most wants a single mapping:
    {DP-1..DP-7, F-1..F-5} against {step 1, step 2, R1, R2, R3, R4}, tagged by
    lifecycle phase (design vs operation). The position paper implies the mapping
    by citing WAISE at each requirement but never tabulates it; the WAISE paper
    never mentions the position paper's items. The repo already carries three
    vocabularies with no crosswalk (per REPO_AUDIT.md Sec. 6: code `I-N`/`Gap-N`,
    paper `DP-N`/`F-N`, README "decision points"/"assurance gaps"); the position
    paper adds a fourth (`R1-R4`, step-1/2) that appears nowhere in the repo.

13. **A machine-checkable contract for the position paper's requirements.** The
    WAISE paper is backed by a 193-test paper-code contract that checks claim
    extraction, goal counts, and the integration-induced findings (Sec.
    Verification and Limitations). The position paper's R1-R4 are argued in text
    only, with an explicit "each necessary, we do not claim set sufficient" claim
    that is exactly the kind of assertion the WAISE test suite would encode. The
    reader wants the same contract applied to R1-R4 (necessity, non-sufficiency,
    mapping to DP/F). REPO_AUDIT.md Sec. 5 confirms no `src/` artefact backs the
    position paper; there is no test that even asserts R1 corresponds to DP-2.

14. **An operation-phase evidence layer beside the two existing layers.** The
    repo separates design-time synthetic illustrations (`data/synthetic_illustrations/`,
    seed 42) from measured design-time results (`data/empirical_results/`,
    PointPillars ensemble). The position paper is entirely about operation-phase
    evidence that "arrives asynchronously, component changes under updates,
    reporting obligation requires current judgment on demand" (Sec.
    Assignment/Resolution). There is no third data layer or model representing a
    stream of operation-phase monitor outputs and anomalies, so nothing in the
    repo can exercise the position paper's step-1/step-2 loop even illustratively.

15. **The fourth evidence scale changing form between phases.** WAISE's G5 fourth
    evidence type is "attack success rate ... adds a fourth measurement scale"
    (Abstract, Sec. Conclusion), a measured design-time quantity. At operation the
    position paper has no ground truth and lists only a "binary event indicator"
    for cybersecurity (Sec. Assignment/Resolution). The cybersecurity scale is the
    one that most changes form between design (attack success rate) and operation
    (event indicator), which quietly breaks the DP-2 to R1 mapping the other three
    scales preserve. Neither paper flags this asymmetry, and the repo models the
    G5 evidence types (`evidence_convergence.py`) only in their design-time form.

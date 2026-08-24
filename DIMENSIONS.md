# Dimensions of the Work

Stage 1 of the ideation task. Each dimension below is derived from what the two
papers do, with the passage that shows it is present in the material. Line numbers
refer to the `.tex` sources in `paper/`. Dimensions considered and rejected are at
the end, with the reason each is absent from the material.

The two papers are cited as:
- **W** = `paper/waise2026/CR_Submission_WAISE_...HAD.tex` (GSN integration paper)
- **P** = `paper/safecomp2026-position/CR_position_paper.tex` (position paper)

---

## D1. Lifecycle phase

**Values:** concept and requirements · design and training · V&V · integration and
deployment · operation and monitoring · modification and re-assurance.

**Shown by:** W explicitly constructs this axis as Step 2 of its method: "The
extracted claims are mapped onto six lifecycle phases: concept and requirements,
design and training, V&V, integration and deployment, operation and monitoring, and
modification and re-assurance" (W:212). The findings table carries a "Lifecycle
phase" column (W:448–455). P occupies exactly one value of this axis and says so:
"Operation-phase evidence thus informs the safety case throughout deployment"
(P:26). The two papers divide the axis between them: W spans it, P sits at
operation, and both meet at modification (W's G9, P's R4).

## D2. Concern / standard of origin

**Values:** ISO 26262 (functional safety) · ISO 21448 (SOTIF) · ISO/SAE 21434
(cybersecurity) · ISO/PAS 8800 (AI safety) · ISO/IEC TR 5469 (informative) ·
**between standards / none** (the load-bearing value).

**Shown by:** W tags every goal with a "Source" column (W:343–357) and every
decision point with "Standards" involved (W:407–415). P defines the axis in one
sentence: sub-claims "are organized by concern, that is, by the scope of one
standard" (P:28). The value "between / none" is not an artifact of my analysis:
both papers make it their central object — W's integration-induced findings
"emerge only between the scopes of individual standards" (W:218), and P's anomaly
"carries no concern label" (P:30).

## D3. Epistemic status of a claim

**Values:** prescribed by a clause · deferred to application context (decision
point) · integration-induced absence (finding, II) · open methodological problem
(framework prescribed, values missing, OM).

**Shown by:** This four-way split is W's own results taxonomy, not an imported
one. Step 4 finds "decision points where the standards defer to application
context" (W:216); Step 5 "distinguishes integration-induced findings, which emerge
only between the scopes of individual standards ... from open methodological
problems, where the standards prescribe a framework ... but no published method
specifies application-specific values" (W:218, W:163). P's gap is the pure
"absence" value stated at clause grain: "no clause assigns such an anomaly to a
concern, and none states how the concern-specific activities resolve into a single
judgment" (P:19).

## D4. Resolution agent and kind of decision

**Values:** project vocabulary definition · project method selection · project
structural policy (ownership, admissibility) · standardization amendment ·
research method (new, requirement-constrained).

**Shown by:** W distinguishes these explicitly: terminological and methodological
decision points "can be resolved within a project by defining common vocabulary or
selecting a preferred method. Structural decision points (DP-1, DP-2, DP-5)
require decisions that no standard prescribes" (W:372), and the discussion names
the two project policies required (ownership policy at G7/G8, evidence
admissibility policy at G5, W:483). P addresses the remaining two agents: "The gap
identifies what a revised ISO/PAS 8800 and ISO/SAE 21434 could add" (P:93,
standardization) and "specifies the requirements a method that closes the gap must
satisfy" with R1–R4, "leaving the method to future work" (P:19, P:90, research).

## D5. Evidence type and measurement scale

**Values:** binary pass/fail (MC/DC) · coverage count (scenario/triggering
coverage) · statistical score (AUROC, calibrated probability, ensemble
disagreement) · attack success rate · risk rating · **absent** (claim argued
without evidence).

**Shown by:** W's central finding is defined on this axis: the G5 evidence set is
"(a) MC/DC ... (b) SOTIF triggering condition coverage ... (c) deep ensemble
disagreement ... measured by AUROC; and (d) adversarial penetration testing"
(W:376), and "the cybersecurity evidence type (attack success rate) adds a fourth
measurement scale to the three safety evidence types" (W:105, W:497). P re-derives
the same axis at operation: "the evidence has different measurement scales, such
as a calibrated probability, an ensemble disagreement value, a binary event
indicator, or a risk rating, and no rule combines them" (P:84). The value "absent"
is real in both: W marks three of four G5 evidence types "not produced" (W:307–310),
and P provides no artefact by design.

## D6. Argument altitude

**Values:** evidence/solution node · sub-goal · junction point / strategy · top
claim · interface between the component case and the encompassing system safety
case.

**Shown by:** W positions everything on this axis: the pattern sits "at the AI
component level ... inside the encompassing system safety case rooted in ISO
26262-2 Clause 6.4.8" (W:231), each decision point carries a "GSN node" column
(W:407), and junction-point analysis operates on "each node where claims from two
or more standards meet" (W:216). P locates its gap by altitude, not by phase
alone: the missing steps "sit between the operational evidence and the top claim
that evidence is meant to support" (P:57).

## D7. Temporal mode of the argument

**Values:** construction (design time, top-down decomposition) · re-evaluation
(operation, bottom-up from evidence) · update-triggered re-entry (the mode
switch: G9 / R4).

**Shown by:** W is entirely in construction mode: "the integrated argument is
built first and then examined" (W:198), Steps 1–3. P is entirely in re-evaluation
mode and marks the direction typographically: "Read upward from the evidence, as
in an assurance-case notation" (P:57), and locates itself off-vehicle: "closing it
is an in-service re-evaluation of the safety case, not an in-vehicle runtime
function" (P:30). The third value is shared: "Re-evaluation is activated by a
change in monitor output or by a software update" (P:26) meets W's G9
(modification re-assurance, W:334). The two papers are the two ends of this
dimension; that is the strongest single fact about how they relate.

## D8. Scope of generalisation

**Values:** case-study instance (LiDAR 3D detection, SECOND + deep ensemble) ·
automotive AI component class · any domain assuring one component against several
concern-specific standards.

**Shown by:** Both papers stake the outer value explicitly and separately from
their findings: "the distinction between integration-induced findings and open
methodological problems applies to any domain that assures one component against
several concern-specific standards, such as aviation or medical devices; the
specific findings reported here are automotive" (W:473); "We expect the same gap
wherever one component is assured against several concern-specific standards"
(P:93). The inner value is equally explicit (W:200–203 case study; instantiation
of only evidence type (c), W:376). The repo mirrors this with
`src/analysis/generalisability.py`.

## D9. Verification regime of a paper claim

**Values:** machine-checked (asserted by a test in the supplementary repo) ·
clause-cited (checkable against standard text) · measured/simulated (empirical or
synthetic companion-study result) · argued in text only.

**Shown by:** W builds this axis itself: "An automated test suite of 193 tests in
the supplementary material checks that all extracted claims map to GSN nodes, all
lifecycle phases are covered, and the integration-induced findings do not appear
in any single standard's claim set" (W:487), while its case-study evidence is
flagged "measured on simulated ensemble outputs" (W:376) and three G5 evidence
types "not produced" (W:307–310). P sits entirely at "argued in text only" and is
open about the strongest counter-fact: "We are aware of no published incident that
attributes a deployed automated-driving failure to this ambiguity" (P:30). (Noted:
W says 193 tests; the repository contains 192 test functions — a drift recorded in
chat because REPO_AUDIT.md is closed to edits in this task.)

---

## Dimensions considered and rejected

- **Risk level (ASIL / CAL / SOTIF acceptance level).** Fixed, not varied: the
  case study is ASIL D throughout (W:119, C1); risk level appears only as context
  carried at G1. The papers never compare across risk levels.
- **Attacker capability / threat taxonomy.** Spoofing, perturbation, poisoning
  appear as worked examples (W:378, P:30) but nothing in either paper is organized
  by attacker strength; the threat model is illustrative, not a dimension.
- **Notation / argument formalism.** GSN is fixed. The one alternative raised (a
  concern hierarchy per Warg & Skoglund) is considered and rejected inside W:233;
  the papers do not vary the formalism, they defend a choice within it.
- **Regulatory jurisdiction.** UNECE WP.29 is motivation in P (P:26), but the EU
  AI Act and UNECE R155/R156 are explicitly out of scope (W:489). Jurisdiction is
  a boundary of the work, not an axis it moves along.
- **Detector architecture / ML model class.** Held fixed in the papers (SECOND,
  W:203); the repo's PointPillars substitution is declared architecture-independent
  (`data/empirical_results/README.md` §4). A constant, not a dimension.
- **Human factors / driver interaction.** Absent by construction: SAE Level 4+
  removes the driver (W:115, C1 "Controllability C3"). No passage treats it as
  variable.
- **Quantitative performance level.** AUROC values etc. are *values of evidence*
  (points on D5), not an axis along which the papers' argument varies.
- **Addressee as a separate dimension.** Considered (engineer / committee /
  researcher are all addressed), but every addressee distinction the papers make
  coincides with the resolution-agent values of D4; keeping both would double-count
  the same passages (W:372, W:483, P:90, P:93).

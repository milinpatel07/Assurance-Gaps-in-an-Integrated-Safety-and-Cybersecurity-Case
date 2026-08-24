# Pass 05: Adjacent-Field Reframing

Ideation pass run as four adjacent-field sub-personas. Each would frame the same
problem (integrating cybersecurity into an AI safety assurance argument for a LiDAR
perception component, plus the operational concern-assignment gap) in the vocabulary of
their own discipline. For each sub-persona: a short reframe, then the concrete things
they would WANT from this repository under that framing that it currently cannot give.
No filtering; weak ideas are recorded alongside strong ones. Roughly 3-4 wants per
persona, 14 total. Em-dashes avoided throughout.

---

## (a) Security researcher (threat modelling, SOC / incident response, attack attribution)

Reframe: to a detection-engineering / SOC lead, the position paper's "assignment"
step is exactly what a SOC calls triage and attribution, and the WAISE paper's DP-5 /
F-3 "adversarial-SOTIF boundary" is just the classic benign-versus-malicious
disambiguation problem that every intrusion-detection pipeline faces. The whole
apparatus reads as an alert that fires with no source IP: a monitor says "detections
dropped in a scene region" and the responder must decide fault-versus-attack. This
persona thinks in threat models, kill chains, detection rules, and playbooks, and would
find the papers rich in framing but empty of anything a responder could actually run.

- WANT: a threat model / attack catalogue for the case-study component. Reframing:
  the position paper cites one demonstrated on-road LiDAR attack (Sato2025) and the
  WAISE paper repeatedly invokes "LiDAR spoofing and perturbation" (G5 evidence type
  (d), DP-5, F-3) as the adversarial branch. Reinterprets the sentence "adversarial
  point cloud perturbations can cause false negative detections" as a STRIDE / attack-tree
  claim that is never enumerated. Missing artefact: a structured threat catalogue
  (spoofing, relay, saturation, adversarial-object, sensor-blinding) mapped to the
  specific G-nodes and to TARA threat scenarios, so the "cybersecurity path" column of
  Table (DP-5) is backed by more than one exemplar.

- WANT: detection-rule / triage-signature specification for the assignment step.
  Reframing: R2 in the position paper ("contain an assignment step for an unlabeled
  anomaly") is a detection-engineering requirement, i.e. write the rule that maps a
  monitor output to a concern. Reinterprets Fig. 1's "missing step 1" (no clause assigns
  concern) as the absence of any triage logic. Missing artefact: even an illustrative
  decision procedure or feature set (point-density drop rate, temporal signature,
  cross-sensor disagreement, spatial coherence) that would distinguish a rain-induced
  insufficiency from a spoofing event, expressed the way a Sigma/YARA-style rule would be,
  with its stated false-assignment behaviour.

- WANT: an incident-attribution / forensics record schema. Reframing: WP.29 field
  reporting (position paper, R3, Implications section) is incident reporting; a SOC needs
  a case record with an evidence chain. Reinterprets "the reporting obligation requires a
  current judgment on demand" as an incident-ticket lifecycle with no defined ticket
  format. Missing artefact: a machine-readable anomaly/incident record (timestamp, monitor
  outputs, candidate concerns, assigned concern, residual-defeater status, re-evaluation
  trigger) that could be emitted per event and audited later; nothing in `data/` or `src/`
  represents a single operational anomaly instance.

- WANT: an adversarial-robustness evidence generator to populate G5 leg (d).
  Reframing: the "adversarial penetration test (21434 Cl.10)" node is a red-team
  deliverable. Reinterprets Fig. 2(b)'s dashed "(d) ... not produced" circle as an
  untested control. Missing artefact: even a synthetic, seeded attack-success-rate
  producer analogous to `carla_evaluator.generate_synthetic_illustration()`, so the
  fourth measurement scale (attack success rate) that the abstract and conclusion make
  the central asymmetry actually has a number attached rather than existing only as a
  named absence.

---

## (b) ML researcher (OOD detection, uncertainty calibration, distribution shift)

Reframe: to an ML researcher the entire "anomaly without a concern label" story is a
known open problem wearing standards clothing. The perception monitor emitting predictive
uncertainty and ensemble disagreement with no ground truth is precisely the unsupervised
OOD / distribution-shift-detection setting, and "assign the anomaly to SOTIF versus
cybersecurity" is OOD-source attribution (covariate shift versus adversarial shift), a
studied problem with datasets and baselines (ImageNet-C style corruptions vs adversarial
sets, ODIN, Mahalanobis, deep-ensemble disagreement, ADBench). This persona would want
the paper's single AUROC 0.982 headline situated against baselines and benchmarks, and
would treat the "disjoint evidence types" claim as a calibration/aggregation question.

- WANT: baselines and a benchmark for the uncertainty indicator. Reframing: the
  companion-study result (AUROC 0.982 geometric ensemble disagreement, 22.0% retained at
  no observed false accepts) is presented as evidence type (c) with no comparator.
  Reinterprets DP-2's evidence-(c) paragraph as an unbenchmarked detector claim.
  Missing artefact: a comparison table against standard OOD baselines (softmax response,
  entropy, Mahalanobis, MC-dropout, single-model max-logit) on the same SOTIF-PCOD frames,
  so the chosen indicator is shown to be best-of-class rather than best-of-three; the repo
  has `baseline_softmax_metrics.csv` but no side-by-side baseline sweep in the argument.

- WANT: a covariate-shift-versus-adversarial-shift attribution experiment.
  Reframing: F-3 / DP-5 (a failure mode that is both a triggering condition and a threat
  scenario) is the empirical question "can a monitor separate weather-induced from
  attack-induced point-density loss?". Reinterprets "the same missing region follows from
  rain ... or from spoofing" as a two-class discrimination task with a measurable
  separability. Missing artefact: a labelled dataset split (weather-degraded vs
  adversarially-degraded frames) plus a reported separability score; the paper asserts the
  boundary is "unowned" but never tests whether it is even statistically separable, which
  is the prior question an ML reviewer asks.

- WANT: calibration and an aggregation rule for the "four measurement scales".
  Reframing: the conclusion's central claim (attack success rate, MC/DC coverage,
  scenario coverage, ensemble uncertainty do not combine) is a multi-scale-fusion /
  calibration problem with candidate answers (Platt/temperature scaling to a common
  probability, conformal prediction, Dempster-Shafer, subjective logic). Reinterprets the
  "no standard prescribes the combination rule" sentence as an unexplored modelling gap,
  not merely a standards gap. Missing artefact: a worked prototype that maps each of the
  four evidence types to a comparable confidence scale and reports what a combined
  sufficiency score would look like, even as a strawman the paper argues against.

- WANT: distribution-shift and drift-detection tie-in for G6 monitoring. Reframing:
  G6 ("operational monitoring covers AI, SOTIF, cybersecurity") and the position paper's
  "distribution-shift indicators" are the deployment-monitoring literature (test-time
  drift, PSI, MMD, feature-space shift). Reinterprets DP-6 "monitoring scope overlap" as
  an unspecified drift-detector stack. Missing artefact: a concrete list of runtime
  monitor signals with their statistical detectors and thresholds, so G6 is more than a
  coordination claim; currently no `src/` module emits a drift statistic.

---

## (c) Certification / assessment engineer (audit trails, conformity assessment, UL 4600, assessor checklists)

Reframe: an independent assessor does not read the GSN for elegance; they read it to
check that every claim has admissible, traceable evidence and that nothing is asserted
without a work product behind it. To this persona the WAISE pattern is a conformity
argument whose leaf nodes are mostly "not produced" (three of four at G5), and the
"clause-level traceability" selling point is exactly what an audit needs, but the
crosswalk is incomplete. UL 4600's claim/evidence/gap discipline and the notion of a
review checklist are the native tools here, and the assessor would want the assessment
instrument, not just the argument.

- WANT: an assessor checklist / conformity-matrix artefact per goal. Reframing: the
  paper's contribution (ii) "catalogue of decision points the engineer must resolve" is,
  to an assessor, a checklist of open items to sign off. Reinterprets Table 2 (goals with
  clause traceability) and Table 3 (DP-1..DP-7) as the raw material for an audit form.
  Missing artefact: a per-node checklist mapping each goal/sub-claim to (required work
  product, evidence status present/absent, responsible party, acceptance criterion,
  assessor verdict), which the repo could generate from `build_integrated_gsn()` but does
  not; the assessor cannot currently tick anything.

- WANT: a documented terminology crosswalk (assessor cannot cross-reference the
  evidence). Reframing: an assessor moving between the paper and the supplementary code
  needs a defensible mapping. Reinterprets the paper's DP-3 / DP-4 (terminology decision
  points, "validation defined differently") as a threat to the audit trail, and mirrors
  the repo's own I-N / Gap-N versus DP-N / F-N split. Missing artefact: a published
  crosswalk table (I-2 = DP-2 = G5 central finding; Gap-3/Gap-4 = F-3/F-4) so an assessor
  reading `DP-5` in the paper and finding `I-5` / `Gap-3` in the code has a signed mapping;
  its absence is a direct conformity-of-evidence finding.

- WANT: a UL 4600-style claims-arguments-evidence gap register. Reframing: UL 4600
  requires an explicit list of unresolved items and their disposition. Reinterprets the
  F-1..F-5 "open methodological problems" and the three "not produced" G5 legs as a formal
  gap register. Missing artefact: a single register that records, for each gap, its
  criticality, interim mitigation, closure owner, and target date, in the format an
  independent assessor files; the paper narrates the gaps but supplies no disposition
  fields.

- WANT: an independent-review / inter-rater artefact for claim extraction.
  Reframing: the Limitations section concedes claim extraction was "performed by a single
  assessor; inter-rater reliability was not assessed". To a certification engineer this is
  a competence-and-independence non-conformity. Reinterprets that sentence as a missing
  review record. Missing artefact: a second-assessor extraction and a reconciliation log
  (agreement rate, disputed clauses), which would turn the 193-test suite from an internal
  consistency check into evidence of review independence.

---

## (d) Regulator / policy person (UNECE WP.29, in-service monitoring obligations, reporting formats)

Reframe: a WP.29 / type-approval official reads the position paper as being about
their own instrument: the 2026 framework obliges the manufacturer to monitor operation
and report field occurrences against the approved safety case, and the paper's thesis is
that no procedure turns a field anomaly into a current judgment. The regulator does not
care which GSN goal owns the boundary; they care whether the reporting duty is
dischargeable, auditable, and comparable across manufacturers. They think in reporting
schemas, in-service obligations, audit periodicity, and market surveillance, and would
want the reporting instrument the paper says is missing.

- WANT: a field-occurrence reporting schema tied to the safety case. Reframing: the
  position paper's Implications section ("no defined procedure to turn a field anomaly
  into a current judgment on the case") is, to a regulator, a missing reporting standard.
  Reinterprets R3 ("produce a judgment traceable to the operation-phase clauses ...
  in-service") as the specification of a report format. Missing artefact: a candidate
  in-service reporting template (fields: occurrence, monitor evidence, assigned concern,
  re-evaluation triggered, safety-case node affected, current verdict) that a regulator
  could mandate and that would make submissions comparable; the repo holds no report
  schema at all.

- WANT: a mapping from the concern-assignment gap to specific regulatory clauses and
  reporting triggers. Reframing: the regulator needs to know which obligation the gap
  defeats. Reinterprets Table 1 (operation-phase activity per standard, "element not
  defined") as an input to a regulatory-obligation matrix. Missing artefact: a crosswalk
  from WP.29 / R155 / R156 reporting and change-management duties to the missing step-1
  (assignment) and step-2 (resolution) of the paper, so a policymaker can see exactly
  which reporting requirement has no technical procedure behind it; the WAISE paper
  explicitly scopes R155/R156 out, leaving this untouched.

- WANT: an auditability / market-surveillance criterion for the re-evaluation
  decision. Reframing: a regulator must be able to re-check a manufacturer's on-demand
  judgment. Reinterprets the position paper's "reporting obligation requires a current
  judgment on demand" and F-4 ("no cross-domain release decision criteria") as a market
  surveillance gap: two manufacturers could assign the same anomaly differently and both
  claim compliance. Missing artefact: a stated set of acceptance/consistency criteria a
  regulator could apply to audit a re-evaluation outcome (reproducibility of the
  assignment, treatment of the unassignable residual, currency of the judgment), none of
  which the papers operationalise beyond naming R1-R3.

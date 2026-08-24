# Pass 06: Implementer and Auditor

Persona: a person who must **implement or audit** the integrated pattern inside an
organisation next year. Two concrete faces of the same persona: (a) a safety manager at
an automotive supplier who has been told to adopt the integrated GSN pattern for the
company's own perception component, and (b) an internal or external auditor checking that
a project's assurance argument actually conforms to the pattern the WAISE paper defines.
This pass records what that person WANTS from this repository but CANNOT get from it today.
Ideas are recorded without filtering, including weak ones (flagged as such).

Format of each want: operational need, the paper passage that creates the need, and why
the current repository does not satisfy it.

---

## W1. A re-instantiation guide for a different component

The safety manager's component is not a SECOND LiDAR detector in CARLA; it may be a camera
detector, a radar fusion block, or a differently trained LiDAR model at a different ASIL.
They need a step-by-step guide for swapping the case study out and re-instantiating the
nine goals for their own component and their own ODD. The paper states the pattern is
"instantiated for a LiDAR-based 3D object detection component" and that "the integrated
pattern identifies where evidence is needed", presenting the LiDAR case as one instance of
a general pattern. The repository does not support this: `build_integrated_gsn()`,
`src/evaluation/carla_evaluator.py`, and the case-study parameters hard-code SECOND, ASIL D,
CARLA rain and fog, and the specific evidence-type statuses. There is no parameterised
template, no "how to instantiate for your component" document, and `practitioner_guidance.py`
is organised per gap rather than per instantiation, so the manager has no path from the
published example to their own argument.

## W2. A blank ownership policy template for the G7/G8 boundary

The paper explicitly hands the reader a homework item: "The adversarial-SOTIF boundary
(DP-5, F-3) requires a project-level ownership policy that assigns each identified failure
mode to either G7 or G8, a decision no standard prescribes." The manager needs a fillable
policy skeleton (fields: failure mode, SOTIF path, cybersecurity path, assigned goal,
justification, approver, review date) that they can populate and put under configuration
control. The repository gets close but stops short: `practitioner_guidance.py` (Gap-3) lists
"Dual-domain failure mode register with ownership assignments" as an evidence item to
produce, and Table `tab:dp5` in the paper is a worked example for one failure mode, but
neither is a reusable blank template or a machine-readable schema the project can adopt.

## W3. A blank evidence admissibility policy template for G5

Parallel to W2, the paper states "The V&V sufficiency claim at G5 requires an evidence
admissibility policy defining how the prescribed evidence types relate to one another",
and points to "ISO 26262 Parts 4 and 6 ... the documented rationale required when an
alternative verification method replaces a recommended one" as a precedent to extend. The
manager needs a policy template that records, for the four disjoint evidence types
(MC/DC coverage, SOTIF scenario coverage, ensemble uncertainty AUROC, adversarial
penetration testing), the admissibility criterion and the combination rationale. The
repository has `evidence_convergence.py` describing the four types and the convergence at
G5, but no policy skeleton, no admissibility-criterion fields, and no worked rationale the
project could adapt.

## W4. An auditable resolution record for DP-1 to DP-7

Contribution (ii) of the paper is "a catalogue of decision points the engineer must
resolve where the standards defer to application context". A catalogue states the open
questions; the implementer must then record how their project resolved each one, and the
auditor must inspect those resolutions. The person needs a decision log per decision point
(fields: DP id, decision taken, rationale, evidence reference, owner, approver, date,
status) that is itself a configuration-controlled work product. The repository provides
`decision_points.py` (`DecisionPointCatalogue`, I-1 to I-7) as fixed descriptive data about
the standards, but nothing to record a project-specific resolution, no status field, and no
export of a resolution register. The auditor has no artefact to check against.

## W5. Export into commercial assurance-case tooling

The organisation does not keep safety cases in gsn2x YAML; it uses an assurance-case tool
(for example ASCE, AdvoCATE, Astah GSN, or a SACM-based repository). The paper says each
node "carr[ies] a reference to the clause from which its claim derives, encoded in
machine-readable form in the supplementary material", implying portability of the argument.
The repository's machine-readable forms are only `gsn/*.gsn.yaml` (gsn2x) and a Graphviz
`.dot` emitted by `gsn_renderer.py`. There is no export to OMG SACM / XMI, no GSN-tool
interchange format, and no importer, so the company's tool cannot ingest the pattern and
the argument has to be re-drawn by hand, breaking the clause-level traceability the paper
advertises.

## W6. A standards-revision delta path

Standards revise: ISO 21448 amendments, a future edition of ISO/PAS 8800, or ISO/SAE 21434
updates will move clause numbers and change requirements. The whole argument in the paper
rests on clause-level traceability (Table `tab:goals`, the clause columns of
`tab:inconsistencies` and `tab:gaps`), and F-2 already concerns re-assurance after change.
The implementer needs a way to see which goals, decision points, and findings are affected
when a cited clause changes, and to re-version the clause map. The repository hard-codes
clause strings inside `src/standards/*.py` (for example "ISO 26262-3 Cl.6", "ISO/SAE 21434
Cl.15.8") with no edition/version field, no diff mechanism, and no impact query, so a
standards revision forces a manual re-read of every module.

## W7. Training material and a worked tutorial for the five-step method

Before a team can apply the method they must learn it. The paper describes a five-step
constructive integration process (Section 3, Steps 1 to 5) in prose. The implementer wants
a teaching artefact: a worked tutorial that walks a new engineer through applying Steps 1
to 5 to a fresh component, with exercises. The repository has `run_analysis.py`, which
prints the already-computed results of the published analysis to the console, and a Colab
notebook whose provenance the audit could not confirm, but nothing pedagogical, no
step-by-step walkthrough on a new component, and no exercises or checklists a trainer could
use.

## W8. A conformance checker an assessor can run against a project's own argument

The paper offers verification as a strength: "An automated test suite of 193 tests in the
supplementary material checks that all extracted claims map to GSN nodes, all lifecycle
phases are covered, and the integration-induced findings do not appear in any single
standard's claim set." The external assessor wants to point that machinery at the project's
actual instantiated argument and get a pass/fail conformance report demonstrating the
pattern was followed. But the 192/193 tests validate the paper's own fixed argument
(`test_paper_claims.py` asserts the hard-coded 9 goals, 7 decision points, 5 findings);
they take no user-supplied GSN as input. There is no conformance tool that ingests a
project's argument and checks it against the pattern, so the assessor cannot use the repo
to demonstrate anything about a real project.

## W9. A supplier/OEM interface contract for the encompassing safety case

The supplier does not own the whole vehicle. The paper positions the pattern "at the AI
component level ... inside the encompassing system safety case rooted in ISO 26262-2
Clause 6.4.8", with Context C1 carrying the ASIL from the system HARA and C2 carrying the
TARA results. The safety manager needs a defined interface: what the OEM must supply into
C1 and C2 (away-goals / module boundary), and what the component argument returns upward.
The repository models C1 and C2 as internal context nodes with case-study values baked in
(ASIL D, LiDAR spoofing) and provides no module-interface or away-goal specification, so a
supplier cannot see the contract at the boundary with the encompassing system.

## W10. A cross-domain release checklist and sign-off gate

Finding F-4 states that "no standard requires evaluating the combined residual risk across
domains" and that "the cross-domain release decision becomes visible only under a single
top-level goal". The implementer needs an actual release gate: a checklist requiring
sign-off from functional safety, SOTIF, cybersecurity, and AI safety, with a stated
decision rule and an escalation path. The repository's `practitioner_guidance.py` (Gap-4)
lists desirable evidence items ("Cross-domain release criteria specification", "Release
review board charter") but provides no checklist artefact, no sign-off template, and no
decision-rule instrument the project could operate at a release milestone.

## W11. A documented crosswalk between paper labels and repository labels

The auditor reads the paper (DP-1 to DP-7, F-1 to F-5) and opens the repository to check
the claims, and immediately hits a naming mismatch: the code uses I-1 to I-7 for the
decision points and Gap-1 to Gap-5 for the findings, and the README uses yet a third
phrasing. The paper's contribution rests on these being the same objects (for example I-2
is the central G5 finding, later DP-2; Gap-3 and Gap-4 are the integration-induced
findings F-3 and F-4). The person needs a single crosswalk table mapping paper id to code
id to README phrasing. No such crosswalk exists in the repository, so an auditor
cross-referencing paper DP-5 finds I-5 with no documented link and must reverse-engineer
the mapping.

## W12. A reusable claim-extraction checklist for a second assessor

The paper concedes that "the claim extraction (Step 1) was performed by a single assessor;
inter-rater reliability was not assessed, and the extraction's completeness depends on the
assessor's reading". An auditor who wants to test that reading, or a second engineer
re-doing extraction for their component, needs the extracted claim set per standard as a
re-runnable checklist so a second reader can independently confirm or dispute each claim.
The repository holds the claims hard-coded inside `src/standards/*.py` as Python objects
inside a program, not as a per-standard extraction checklist or worksheet, so there is no
convenient instrument for a second assessor to reproduce or challenge Step 1.

## W13. A live evidence-coverage report for the project's real evidence

The implementer wants a running picture of which goals and clauses their project has
satisfied with real evidence and which it still owes, at any point during development.
Figure 2(b) already frames this: evidence type (c) is "provided (simulated)" while (a),
(b), and (d) are "not produced". But that status is hard-coded to the published case study.
The repository has `completeness.py`, which only checks that G9 is the single undeveloped
goal; there is no per-project evidence register, no goal-by-goal coverage dashboard, and no
"evidence owed" report the manager can update as evidence is produced.

## W14. An operational anomaly-assignment work product linking to the position paper

The same organisation must also operate the component in service. The position paper argues
that a runtime anomaly "carries no concern label" and specifies requirements R1 to R3 for a
method that assigns an unlabeled anomaly to SOTIF / AI-safety / cybersecurity and resolves
the concern-specific re-evaluations into one judgment on the safety case, driven by the
WP.29 reporting duty; the WAISE paper's G6 "coordinates three parallel monitoring scopes ...
whose interaction no standard defines". The in-service implementer needs a work product to
log each operational anomaly, its concern assignment, and the resulting re-evaluation of
the safety case. The repository is entirely design-time; it contains no operational
assignment log, no re-evaluation record template, and (by design, since the position paper
is not code-backed) nothing that operationalises R1 to R3.

## W15. A defensible adoption effort and resourcing estimate (weak)

Weak want, flagged. A manager asked to adopt the pattern must budget people and time. The
paper does not create this need strongly, but `practitioner_guidance.py` already assigns an
`estimated_effort` to each gap ("requires_research", "high", "medium"), which invites the
question. The manager would want those estimates grounded in something defensible (person-days,
prerequisite ordering, skill mix) to justify resourcing. The repository offers only the bare
effort labels with no basis, no cost model, and no planning artefact, so the label cannot be
defended to a programme manager.

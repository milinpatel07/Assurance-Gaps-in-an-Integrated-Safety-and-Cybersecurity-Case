# Pass 01: WAISE-only reader who wants to act

Persona: an engineer who has read only the WAISE 2026 paper (the GSN integration
pattern paper) in full and wants to act on it. They want to apply the integrated
GSN pattern to their own AI component, resolve decision points DP-1 to DP-7 in
their own project, and use findings F-1 to F-5. They do not read the position
paper and do not use it. They skim the README and REPO_AUDIT only to learn what
the repository holds today.

Each entry below is one thing this reader wants, the passage or table in the
WAISE paper that creates the need, and why the current repository does not
satisfy it. Weak ideas are kept, not filtered.

## Wants

**W1: A reusable, blank template of the 9-goal pattern.**
Section 4 and Figure 2 present the integrated pattern (G1 top goal, G2-G6
retained, G7-G9 added, C1, C2, A1.4) and the paper frames it as a pattern to be
instantiated. A reader wants a parameterised or blank version they can drop their
own component into. The repository ships `gsn/integrated_pattern.gsn.yaml`, but it
is hard-wired to the LiDAR case study (ASIL D in C1, the specific TARA in C2, the
SECOND detector at G5). There is no blank or parameterised template that strips
the case-study specifics, so the reader must reverse-engineer which parts are the
pattern and which are the instance.

**W2: The machine-readable clause-to-node mapping the paper promises.**
Section 4 states that each node "carries a reference to the clause from which its
claim derives, encoded in machine-readable form in the supplementary material,"
and Table 2 gives the per-goal clause sources. A reader wants to open one file and
read the full node-to-clause map to reuse the traceability. The mapping is spread
across `src/standards/*.py`, `src/gsn/integrated_pattern.py`, and the GSN YAML, in
three partly overlapping encodings, and the paper's own `configs/standards.yaml`
is not loaded by any code and may be stale. There is no single consumable export
of the clause-level traceability.

**W3: A crosswalk between the paper's DP-/F- labels and the code's I-/Gap-
labels.**
The paper names decision points DP-1 to DP-7 (Table 3) and findings F-1 to F-5
(Table 4). A reader who wants to find DP-5 or F-3 in the code needs the mapping.
The repository code uses `I-1..I-7` and `Gap-1..Gap-5`, the README uses a third
phrasing ("7 decision points", "5 assurance gaps"), and no crosswalk file
documents that DP-5 is I-5 or F-3 is Gap-3. The reader cross-referencing the paper
to the repository hits three vocabularies for the same two object sets.

**W4: A method to reconcile the three risk frameworks named in DP-1.**
DP-1 (Table 3 and Section 5.1) says G1 must carry ASIL from ISO 26262, residual
risk acceptance from ISO 21448, and risk values from ISO/SAE 21434, and that "no
standard defines how to reconcile these into a single sufficiency judgement." A
reader wants at least a worked procedure or decision aid to make that
reconciliation in their own top-level goal. The repository only catalogues DP-1 as
an open decision point (`decision_points.py`); it provides no reconciliation
method, template, or example resolution.

**W5: A combination rule for the disjoint evidence types at G5 (DP-2).**
DP-2 and the Conclusion state the four evidence types at G5 (MC/DC coverage,
scenario coverage, ensemble AUROC, attack success rate) are disjoint by design and
"no standard prescribes how they combine into a single sufficiency claim," listing
this as future work. A reader wants a way to combine them so they can actually
close G5. The repository's `evidence_convergence.py` only enumerates the four
types and the three analysis paths; it offers no aggregation rule, so the reader
is left exactly where the paper leaves them.

**W6: A project ownership policy template for the adversarial-SOTIF boundary
(DP-5, F-3).**
DP-5 and F-3 (Table 3, Table dp5, Section 5.2) show a failure mode that is both a
cybersecurity threat scenario and a SOTIF triggering condition, unowned between G7
and G8, with allocation left as "a project decision." The Discussion says this
"requires a project-level ownership policy that assigns each identified failure
mode to either G7 or G8." A reader wants that policy as a reusable checklist or
decision table. The repository provides only the DP-5 worked example for the one
LiDAR failure mode; there is no template a reader can apply to their own failure
modes.

**W7: An evidence admissibility policy example for G5.**
The Discussion (Project-Level Decisions) says the V&V sufficiency claim at G5
"requires an evidence admissibility policy defining how the prescribed evidence
types relate to one another" and points to ISO 26262 Parts 4 and 6 as a precedent
for documented rationale. A reader wants a concrete example of such a policy to
adapt. The repository contains no admissibility-policy artefact, so the reader has
only the prose pointer.

**W8: The three unbuilt G5 evidence legs, or a worked stub for each.**
Figure 2(b) shows four evidence types at G5 where only leg (c), ensemble
disagreement, is instantiated, and legs (a) MC/DC, (b) SOTIF scenario coverage,
and (d) adversarial penetration testing are marked "not produced." A reader who
wants a full worked V&V decomposition finds three of the four legs empty. The
repository does not contain any artefact, method, or placeholder for legs (a),
(b), or (d), so the reader cannot see how the other three evidence types would be
produced or attached.

**W9: A developed OTA re-assurance workflow for G9 (F-2).**
G9 is marked undeveloped in Figure 2 and Section 4.2, and F-2 (Table 4) states no
single standard prescribes the complete re-assurance workflow for a modified AI
model. A reader who must handle retraining or OTA updates wants the G9 sub-tree
built out. The repository also leaves G9 undeveloped (`completeness.py` confirms it
is the only undeveloped goal, and the GSN YAML still tags it with the old
"Gap-2"), so the reader gets no more than the paper's open statement.

**W10: Derived quantitative acceptance criteria and data thresholds (F-1, F-5).**
F-1 and F-5 (Table 4, Section 5.2) say no published method derives
application-specific quantitative acceptance criteria (for example an AUROC target)
or data-sufficiency thresholds for an AI perception component. A reader wants at
least a worked derivation or a scaffold to compute these for their own component.
The repository reports one AUROC figure (0.982) and a three-indicator acceptance
gate in the companion study framing, but it derives no acceptance threshold and no
data-sufficiency threshold, matching the paper's own "open" status and leaving the
reader without a starting method.

**W11: A step-by-step procedure to run the five-step method on a new component.**
Section 3.2 describes Steps 1-5 (claim extraction, lifecycle mapping, GSN
construction, junction-point analysis, finding identification) as a method the
paper applies. A reader wants a procedure or checklist to run those five steps on
their own standards set and component. The repository's `run_analysis.py` replays
the fixed LiDAR analysis and hard-codes the seven decision points and five
findings; there is no guide or reusable driver for extracting claims, finding
junction points, or classifying findings in a new argument.

**W12: The ISO/PAS 8800 Annex B base pattern encoded separately, to diff against.**
Section 2.1 and Step 3 describe the Annex B six-goal base pattern (G1-G6) that the
integrated pattern extends, retaining the activity-based decomposition and adding
nodes only where none exists. A reader wants the base pattern encoded on its own so
they can see exactly what was added versus retained and reproduce the extension
step. The repository ships only the finished integrated pattern; there is no
separate encoding of the Annex B base pattern to diff against, so the reader cannot
mechanically see the delta the paper claims.

**W13: Evidence that matches SECOND, the architecture the paper names.**
Section 3.1 names the SECOND architecture with a deep ensemble mapped to G5 and
G6. A reader who wants to reuse the case-study evidence for G5/G6 expects
SECOND-based results. The repository's measured evidence under
`data/empirical_results/` is from a PointPillars ensemble substituted for SECOND,
a substitution stated only in a data README and not in the paper. The reader
acting on the paper's G5/G6 claims finds the supporting numbers come from a
different detector than the one the paper describes.

**W14: A way to render Figures 2 and 3 on the reader's own machine.**
The paper presents the GSN as machine-readable and reproducible, and the README
offers `make gsn-install && make gsn`. A reader on Windows (the documented host)
wants to render the diagrams to inspect and adapt them. The `make gsn-install`
target downloads a Linux gsn2x binary that will not run on Windows, so the
out-of-the-box render path fails and the reader must find and install gsn2x
manually before they can view or fork the argument.

**W15: Validation that the extracted claims are trustworthy before reuse.**
Section 6 (Verification and Limitations) states claim extraction was performed by a
single assessor with no inter-rater reliability assessed, and that completeness
depends on that assessor's reading. A reader who wants to build on the extracted
claim set wants some independent check before trusting it. The repository's test
suite checks internal consistency (claims map to nodes, phases covered) but
contains no second-assessor extraction or inter-rater data, so the reader cannot
gauge the completeness or reliability of the claims they would reuse.

**W16: Actionable generalisation guidance beyond the LiDAR case.**
The Discussion says the distinction between integration-induced findings and open
methodological problems applies to any domain that assures one component against
several concern-specific standards, while the specific findings are automotive. A
reader with a camera, radar, or non-automotive AI component wants guidance on which
parts of the pattern, decision points, and findings carry over. The repository has
a `generalisability.py` module keyed to the internal I- identifiers, but it exposes
no reader-facing guidance mapping the automotive findings to another component or
domain, so the reader must infer the transfer themselves.

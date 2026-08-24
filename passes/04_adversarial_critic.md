# Pass 04 — The Adversarial Critic

**Persona.** A reviewer who thinks the central claims of both papers are artefacts of how the
analysis was set up, not properties of the standards, and who wants the repository to hand over the
material that would let the claims be falsified. The two targets under attack are the WAISE paper's
"G5 is the only node where all four standards contribute" plus its "F-3/F-4 are invisible from any
single standard," and the position paper's universal negative "no clause assigns an unlabelled
anomaly to a concern." Below is what this critic would demand the repository mount to settle each
attack, and why the artefacts that exist today cannot supply it.

---

## Want 1 — A claim-extraction table that could make G5's uniqueness fall over

The critic's first move is that "G5 is the only node where all four standards contribute" is a
consequence of which clause got stapled to which goal by one reader, not a structural fact. To
settle it, the repository would have to expose the full extraction with a per-claim rationale, so a
challenger could re-attach, say, ISO/SAE 21434 Cl.8 cyber-monitoring to G6 or a cyber-spec claim to
G2 and watch G5's exclusivity evaporate. What actually exists is `src/standards/iso21434.py` (and
its four siblings) hard-coding roughly eight clauses and nine claims apiece with a bare
`gsn_goal="G5"` field and no defence of the assignment, plus `registry.py::compute_coverage_matrix`
that merely tallies those same hand-set fields. The matrix cannot dissent from the mapping that
produced it: the verdict and the input are the same object.

## Want 2 — Evidence that the seven decision points are exhaustive, not merely the seven found

The paper enumerates DP-1 through DP-7 and never argues the list is closed. The critic wants a
saturation procedure: an enumeration over every junction node where two-plus standards meet, with a
demonstration that no eighth deferral was missed, or, failing that, an honest statement that seven is
a floor and not a ceiling. `src/analysis/decision_points.py` is a hand-written `list[Inconsistency]`
of exactly seven entries, and `completeness.py` checks only that GSN goals are developed (G9 aside),
never that the decision-point catalogue is complete. Nothing in the tree distinguishes "seven exist"
from "seven were noticed."

## Want 3 — A derivation, not an assertion, that F-3 and F-4 are invisible single-standard

The counterfactual claim is the paper's self-described "strongest contribution," so the critic
presses hardest here. Settling it requires showing mechanically that no clause in a given standard's
corpus yields the finding — a search, not a declaration. Instead `counterfactual.py` hard-codes
`invisible_gaps=["Gap-3 …", "Gap-4 …"]` as prose strings inside each `StandardPerspective`, and
`get_gap_visibility_matrix()` just reflects those hand-authored lists back. The conclusion "Gap-3 and
Gap-4 are invisible from ANY single standard" is typed in, not computed: the module asserts precisely
what it is meant to prove.

## Want 4 — A machine-readable clause corpus that could falsify the universal negatives

Both papers lean on universal negatives ("no standard defines how to combine," "None of the standards
assigns an unlabelled anomaly a concern") that range over thousands of real clauses. The critic wants
the full, exhaustive clause inventory of the suspect neighbourhoods (ISO 21448 Cl.13.4
result-to-argument mapping, ISO/SAE 21434 Cl.8 monitoring-to-triage, ISO/PAS 8800 Cl.14 operational
monitoring) so a reviewer can point to one candidate clause that does assign, and collapse the
negative. What exists is the sparse, hand-picked handful of clauses in `src/standards/*.py`, none
carrying clause text, and, for the position paper, REPO_AUDIT confirms zero backing code at all. A
universal negative over a corpus the repository never digitised cannot be checked against a file.

## Want 5 — A sensitivity run under Warg & Skoglund's concern hierarchy

The WAISE paper concedes an alternative top-level structure, the multi-concern concern hierarchy of
Warg & Skoglund, with SOTIF and functional safety as sub-concerns of safety and cybersecurity as a
co-concern, then keeps the flat four-domain decomposition "because it preserves the activity-based
structure." The critic's bet is that under that hierarchy DP-1's three-framework clash and F-3's
unowned boundary dissolve into an ordinary cross-concern interplay node. `base_pattern_sensitivity.py`
is exactly where this test belongs, yet it compares only Annex B, the SOTIF four-area model, AMLAS,
and SACE; the one alternative the paper itself names is absent, and even those verdicts are hand-set
`would_detect_*: bool` flags rather than re-derivations. The module that should stress the
decomposition instead hard-codes its survival.

## Want 6 — Any evidence that the gap has ever bitten

The position paper admits, in its own text, "We are aware of no published incident that attributes a
deployed automated-driving failure to this ambiguity." The critic wants a corpus — incident reports,
a worked misassignment, one field case where SOTIF and cybersecurity re-evaluations reached opposite
verdicts on the same anomaly. `data/empirical_results/` holds AUROC and MDR/MFAR from a PointPillars
ensemble on KITTI/nuScenes; none of it touches concern misassignment, and there is no incident
dataset anywhere in the tree. The motivation rests on a reporting duty and a lab attack, never on the
gap actually producing a wrong call.

## Want 7 — The V&V asymmetry faced with four real evidence legs, not one simulated

The central finding, four disjoint evidence types with no combination rule at G5, is illustrated by a
case study in which, per Figure 2(b) and the text, three of the four legs are "not produced" and the
fourth (ensemble disagreement, AUROC 0.982) is measured on simulated outputs. The critic argues you
cannot claim "no rule combines them" while never having held all four in hand at once. Settling this
needs real MC/DC, real CARLA scenario coverage, and a real adversarial pen-test alongside the
uncertainty number. `evaluation/carla_evaluator.py::generate_synthetic_illustration` is seeded and
CARLA-free by construction, and the empirical layer substitutes PointPillars for the paper's SECOND
— so the combination problem is asserted structurally but never once instantiated.

## Want 8 — An external oracle instead of the code grading its own homework

Underneath every attack is one structural complaint: the lockstep the repository advertises is
`tests/test_paper_claims.py` asserting the hard-coded constants in `src/` against the same hard-coded
constants ("9 goals," "G5 only," "exactly two integration-induced") with the paper's single-assessor
extraction as the shared source. The critic wants an independent ground truth: a second reader's
extraction, inter-rater agreement, or an external clause list the tests could disagree with. The
paper's own Limitations section confirms the extraction was done by one assessor with no inter-rater
reliability assessed, and no artefact in the tree remedies it. Every green test confirms the code is
consistent with itself, which is exactly the thing the critic already granted.

---

**Net.** The repository is internally airtight and externally unfalsifiable — and to this critic
those are the same sentence. The modules that carry the load-bearing claims (`counterfactual.py`,
`base_pattern_sensitivity.py`, `decision_points.py`) encode their conclusions as literals rather than
deriving them, the clause corpus is too sparse to test any universal negative, and the one paper that
states the sharpest negative ships with no backing code at all.

"""Counterfactual analysis: what each standard misses when applied in isolation.

Supports the paper's claim that Gap-3 and Gap-4 (F-3 and F-4 in the paper) are
integration-induced: they become visible only when the standards are combined.

What in this module is computed and what is asserted
----------------------------------------------------
The distinction matters, because a module that asserts its own conclusion proves
nothing. Read this before citing anything here.

**Gap-3 is derived.** ``derive_gap3_invisibility()`` computes it from the goal
structure in ``build_integrated_gsn()``, which is authored independently of this
file. Gap-3 sits on the boundary between G7 and G8. No standard sources both
goals, so no single-standard assessor holds both ends of the boundary, so the
boundary is in no single view. Nothing about the answer is written into this
module; change the goal sources and the computed answer changes with them.

**Gap-4 is derived from a stated premise, not proved.** ``derive_gap4_invisibility()``
computes the numbers, but the numbers only mean "invisible" under this premise:

    Plurality premise. Gap-4 is the absence of a rule for combining evidence
    across domains. That question exists at a node only where more than one
    standard contributes evidence to it, because each standard brings its own
    kind of evidence on its own measurement scale. Where one standard
    contributes, there are no scales to reconcile and no such rule is missing.

Under that premise the computation runs: G5 draws on all four normative standards
in the union and on one in any single-standard view, so the question is posed in
the union and in no restriction.

Be clear about the reach of that. The premise does not single out G5. Every node
with more than one contributing standard satisfies it, which is most of the
pattern; only G3, G7 and G8 fail it. So the computation establishes that the
finding is invisible from any single standard. It does not establish that G5 is
where the finding belongs. That comes from the paper, which locates F-4 there.
Restricting to one standard gives a contributor count of one by construction, and
that is not reported as a discovery.

The unit is the standard, not the claim. Counting claims would give the wrong
answer, because ISO 26262 alone carries several claims at G5 and they are all
functional-safety verification on one scale.

State the premise plainly rather than burying it, because the choice of premise
carries part of the conclusion. A reader who rejects the plurality premise is not
compelled by the computation. That is a real limit on this module and not a
presentational quibble.

**Gap-1, Gap-2 and Gap-5 are asserted, not computed.** The ``visible_gaps`` and
``invisible_gaps`` fields below are hand-authored. What separates these three
from Gap-3 and Gap-4 is whether a single standard's own text exhibits the
deficiency by itself: ISO 21448 Clause 6.5 gives an acceptance framework with no
values (Gap-1), ISO/PAS 8800 Clause 14.8.3 gives partial re-approval only
(Gap-2), ISO/PAS 8800 Clause 8.4 prescribes data requirements with no thresholds
(Gap-5). The repository holds no machine-readable representation of that
"exhibits it alone" property. Adding a field for it would move the assertion into
a new field rather than remove it, so it has not been added. These three remain
declared judgments traceable to the clauses named in ``gaps.py``.

An earlier derivation attempt produced {Gap-2, Gap-3} against the published
{Gap-3, Gap-4}; diagnosing why the rule rather than the paper was wrong exposed
the representation drift that ``tests/test_representation_consistency.py`` now
guards against (commit ``f9a7902``). The attempt is kept in the git history as
evidence about the limits of deriving these claims, not deleted as a failed
experiment.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StandardPerspective:
    """What an assessor sees when following a single standard."""

    standard_id: str
    standard_name: str
    covers: list[str]
    excludes: list[str]
    visible_gaps: list[str]
    invisible_gaps: list[str]
    blind_spots: list[str]


class CounterfactualAnalysis:
    """Counterfactual analysis showing what each standard misses alone.

    Key insight: Gap-3 (adversarial-SOTIF boundary) and Gap-4 (cross-domain
    release criteria) are only visible when standards are integrated.
    """

    def __init__(self):
        self.perspectives = self._build_perspectives()

    def _build_perspectives(self) -> list[StandardPerspective]:
        return [
            StandardPerspective(
                standard_id="ISO 26262",
                standard_name="Functional Safety",
                covers=[
                    "HARA and ASIL classification (Part 3, Cl.6)",
                    "Technical safety concept (Part 4, Cl.6.4.3)",
                    "MC/DC structural coverage (Part 6, Cl.9)",
                    "HW metrics: SPFM, LFM, PMHF (Part 5, Cl.9)",
                    "Change management (Part 8, Cl.8)",
                    "Safety case structure (Part 2, Cl.6.4)",
                ],
                excludes=[
                    "AI/ML components (assumes deterministic SW)",
                    "Cybersecurity threats (deferred to ISO/SAE 21434)",
                    "SOTIF / functional insufficiencies",
                    "Data quality for training",
                    "Runtime monitoring for ML",
                ],
                visible_gaps=[
                    "Gap-1 (no quantitative acceptance criteria)",
                    "Gap-2 (no OTA re-assurance)",
                ],
                invisible_gaps=[
                    "Gap-3 (adversarial-SOTIF boundary — not aware SOTIF excludes cyber)",
                    "Gap-4 (cross-domain release — only sees safety assessment)",
                ],
                blind_spots=[
                    "An assessor following only ISO 26262 assumes cybersecurity is "
                    "handled elsewhere and SOTIF does not apply. They would produce "
                    "a complete safety case that is structurally sound but misses "
                    "AI-specific failure modes and adversarial threats entirely.",
                ],
            ),
            StandardPerspective(
                standard_id="ISO 21448",
                standard_name="SOTIF",
                covers=[
                    "Four-area model for functional insufficiency (Cl.5)",
                    "Triggering condition identification (Cl.7)",
                    "Scenario-based V&V (Cl.9-11)",
                    "SOTIF acceptance criteria (Cl.6.5)",
                    "SOTIF release decision (Cl.12)",
                    "Field monitoring for unknown scenarios (Cl.13)",
                ],
                excludes=[
                    "Cybersecurity threats (Cl.1 explicitly excludes them)",
                    "Random hardware failures (deferred to ISO 26262)",
                    "AI training data quality",
                    "Model uncertainty quantification",
                ],
                visible_gaps=["Gap-1 (qualitative, not quantitative acceptance)"],
                invisible_gaps=[
                    "Gap-3 (adversarial-SOTIF boundary — excludes cyber by scope, "
                    "so adversarial inputs that exploit functional insufficiency "
                    "fall into a void)",
                    "Gap-4 (cross-domain release — only SOTIF release decision, "
                    "no combined evaluation with safety/cyber evidence)",
                ],
                blind_spots=[
                    "An assessor following only ISO 21448 would identify triggering "
                    "conditions and test scenarios but would explicitly exclude "
                    "adversarial perturbations (Cl.1). An adversarial LiDAR spoofing "
                    "attack that exploits a functional insufficiency (e.g., rain-like "
                    "point patterns) would not be analysed under SOTIF alone.",
                ],
            ),
            StandardPerspective(
                standard_id="ISO/SAE 21434",
                standard_name="Cybersecurity Engineering",
                covers=[
                    "TARA: threat analysis and risk assessment (Cl.15)",
                    "Cybersecurity concept and requirements (Cl.9-10)",
                    "Penetration testing and vulnerability analysis (Cl.10)",
                    "Continuous cybersecurity monitoring (Cl.8)",
                    "Cybersecurity case (Cl.3.1.11)",
                    "Safety-cybersecurity interface requirement (RQ-15-06)",
                ],
                excludes=[
                    "Functional safety assessment (deferred to ISO 26262)",
                    "SOTIF / performance insufficiency",
                    "AI/ML-specific threats beyond standard software",
                    "Training data poisoning (not explicitly covered)",
                ],
                visible_gaps=[],
                invisible_gaps=[
                    "Gap-3 (adversarial-SOTIF boundary — cybersecurity includes "
                    "adversarial scenarios but does not classify them as SOTIF "
                    "triggering conditions, so the functional impact is unowned)",
                    "Gap-4 (cross-domain release — only cybersecurity case, "
                    "no combined evaluation)",
                ],
                blind_spots=[
                    "An assessor following only ISO/SAE 21434 would identify LiDAR "
                    "spoofing as a cybersecurity threat and require penetration "
                    "testing. But they would not recognise that the same attack "
                    "also triggers a SOTIF functional insufficiency (false negative "
                    "under rain-like point injection). The functional safety impact "
                    "falls outside their scope.",
                ],
            ),
            StandardPerspective(
                standard_id="ISO/PAS 8800",
                standard_name="Safety and AI",
                covers=[
                    "AI safety requirements specification (Cl.5-6)",
                    "AI design and architecture (Cl.7)",
                    "Data quality requirements (Cl.8.4)",
                    "AI V&V with uncertainty quantification (Cl.9)",
                    "Base GSN pattern (Annex B, 6 goals)",
                    "Partial re-approval for AI changes (Cl.14.8.3)",
                ],
                excludes=[
                    "Cybersecurity (deferred to ISO/SAE 21434)",
                    "SOTIF triggering conditions (deferred to ISO 21448)",
                    "Concrete ASIL decomposition for AI",
                    "Combined release criteria",
                ],
                visible_gaps=[
                    "Gap-2 (incomplete OTA re-assurance)",
                    "Gap-5 (data acceptance threshold undefined)",
                ],
                invisible_gaps=[
                    "Gap-3 (adversarial-SOTIF boundary — defers both to other standards)",
                    "Gap-4 (cross-domain release — base pattern has no combined node)",
                ],
                blind_spots=[
                    "An assessor following only ISO/PAS 8800 would build a 6-goal "
                    "GSN argument covering AI-specific concerns. They would defer "
                    "cybersecurity and SOTIF to their respective standards but "
                    "would not verify that those standards actually cover the AI "
                    "component. The 3 new goals (G7, G8, G9) would never be added.",
                ],
            ),
        ]

    # ── Derivations ──────────────────────────────────────────────────
    # These compute from the goal structure rather than reading the
    # hand-authored lists above. They are the part of this module a
    # sceptical reader can check.

    @staticmethod
    def _goal_sources() -> dict[str, set[str]]:
        """Standards contributing to each goal, from the GSN builder.

        Imported here rather than at module scope to keep this module free of a
        hard dependency on the GSN package for callers that only want the
        hand-authored perspectives.
        """
        from src.gsn.integrated_pattern import build_integrated_gsn

        return {g.element_id: set(g.source_standards or []) for g in build_integrated_gsn().get_goals()}

    @classmethod
    def derive_gap3_invisibility(cls) -> dict:
        """Derive that Gap-3 is invisible from every single standard.

        Gap-3 is the unowned boundary between G7 (SOTIF residual risk, ISO 21448)
        and G8 (cybersecurity risk management, ISO/SAE 21434). Seeing a boundary
        requires holding both of the things it lies between. So Gap-3 is visible
        to a single-standard assessor only if that standard sources both G7 and
        G8.

        Nothing here encodes the answer. The result follows from which standards
        source which goals.
        """
        from src.analysis.gaps import GAP_GOAL_MAP

        sources = cls._goal_sources()
        boundary_goals = GAP_GOAL_MAP["Gap-3"]
        contributors = sorted({s for g in boundary_goals for s in sources.get(g, set())})

        sees_both = sorted(
            s for s in contributors if all(s in sources.get(g, set()) for g in boundary_goals)
        )
        return {
            "gap_id": "Gap-3",
            "boundary_goals": boundary_goals,
            "sources_per_goal": {g: sorted(sources.get(g, set())) for g in boundary_goals},
            "standards_sourcing_both": sees_both,
            "invisible_from_every_single_standard": sees_both == [],
            "derivation": (
                "Gap-3 lies between G7 and G8. A single-standard assessor sees the "
                "boundary only by sourcing both goals. No standard sources both, so "
                "the boundary appears in no single-standard view."
            ),
        }

    @classmethod
    def derive_gap4_invisibility(cls, goal: str = "G5") -> dict:
        """Derive Gap-4's invisibility under the plurality premise.

        See the module docstring. The premise is that a combining question can be
        posed only where an assessor holds more than one evidence strand at one
        node. The premise is asserted. Only what follows from it is computed.
        """
        from src.standards.registry import StandardsRegistry

        registry = StandardsRegistry()
        claims_per_standard = {
            standard.standard_id: len(
                [c for c in standard.claims if getattr(c, "gsn_goal", None) == goal]
            )
            for standard in registry.normative_standards
        }
        union_contributors = sorted([s for s, n in claims_per_standard.items() if n > 0])

        # The unit is the standard, not the claim. Each standard brings one kind
        # of evidence on its own measurement scale, so the cross-domain question
        # is posed by a plurality of standards at a node. Counting claims instead
        # would give the wrong answer: ISO 26262 alone carries several claims at
        # G5, but they are all functional-safety verification on one scale, and
        # no cross-domain combining question arises among them.
        #
        # Restricted to one standard the contributor count is 1 by construction,
        # for any node that standard reaches. That is not a computed discovery and
        # is not reported as one.
        contributors_in_any_single_view = 1 if union_contributors else 0

        return {
            "gap_id": "Gap-4",
            "goal": goal,
            "contributors_in_union": union_contributors,
            "union_contributor_count": len(union_contributors),
            "contributors_in_any_single_standard_view": contributors_in_any_single_view,
            "claims_per_standard_at_goal": claims_per_standard,
            "claims_note": (
                "Reported as context only. Claim counts are not the basis of the "
                "derivation; the basis is how many standards contribute."
            ),
            "premise": (
                "Plurality premise (asserted, not proved): the cross-domain "
                "combining question exists at a node only where more than one "
                "standard contributes evidence there, since each standard brings "
                "its own kind of evidence on its own measurement scale."
            ),
            "invisible_under_premise": (
                len(union_contributors) > 1 and contributors_in_any_single_view == 1
            ),
            "derivation": (
                f"In the union, {goal} draws on {len(union_contributors)} of the four "
                f"normative standards, so a cross-domain combining question is posed "
                f"there. Restricted to any one standard, one standard contributes, so "
                f"no such question is posed."
            ),
            "what_this_does_not_show": (
                "The premise does not single out this goal. Any node with more than "
                "one contributing standard satisfies it, which is most of the "
                "pattern; only the single-standard goals (G3, G7, G8) fail it. G5 is "
                "where F-4 sits because the paper locates it there, not because this "
                "computation selects it. What the computation establishes is the "
                "invisibility from a single standard, not the choice of node."
            ),
            "caveat": (
                "The premise carries part of the conclusion. A reader who rejects "
                "it is not compelled by these numbers."
            ),
        }

    @classmethod
    def derivation_report(cls) -> dict:
        """Both derivations, plus the status of the three asserted gaps."""
        return {
            "derived": {
                "Gap-3": cls.derive_gap3_invisibility(),
                "Gap-4": cls.derive_gap4_invisibility(),
            },
            "asserted_not_computed": {
                "Gap-1": "ISO 21448 Cl.6.5 gives a framework without values.",
                "Gap-2": "ISO/PAS 8800 Cl.14.8.3 gives partial re-approval only.",
                "Gap-5": "ISO/PAS 8800 Cl.8.4 prescribes requirements without thresholds.",
                "reason": (
                    "No machine-readable field records whether a single standard's own "
                    "text exhibits the deficiency alone. Adding one would relocate the "
                    "assertion rather than remove it."
                ),
            },
        }

    def get_perspective(self, standard_id: str) -> StandardPerspective | None:
        for p in self.perspectives:
            if p.standard_id == standard_id:
                return p
        return None

    def get_gap_visibility_matrix(self) -> dict[str, dict[str, bool]]:
        """Return which gaps are visible from each standard's perspective."""
        all_gaps = ["Gap-1", "Gap-2", "Gap-3", "Gap-4", "Gap-5"]
        matrix = {}
        for p in self.perspectives:
            visible_ids = set()
            for g in p.visible_gaps:
                for gap_id in all_gaps:
                    if gap_id in g:
                        visible_ids.add(gap_id)
            matrix[p.standard_id] = {g: g in visible_ids for g in all_gaps}
        # Integration sees all
        matrix["Integrated"] = {g: True for g in all_gaps}
        return matrix

    def print_analysis(self):
        """Print the full counterfactual analysis."""
        print("=" * 80)
        print("COUNTERFACTUAL ANALYSIS: What Each Standard Misses Alone")
        print("=" * 80)

        for p in self.perspectives:
            print(f"\n{'─' * 80}")
            print(f"If an assessor follows ONLY {p.standard_id} ({p.standard_name}):")
            print(f"{'─' * 80}")
            print(f"\n  COVERS:")
            for c in p.covers:
                print(f"    + {c}")
            print(f"\n  EXCLUDES / DOES NOT ADDRESS:")
            for e in p.excludes:
                print(f"    - {e}")
            print(f"\n  GAPS VISIBLE from this perspective:")
            for g in p.visible_gaps:
                print(f"    ! {g}")
            if not p.visible_gaps:
                print(f"    (none)")
            print(f"\n  GAPS INVISIBLE (only visible through integration):")
            for g in p.invisible_gaps:
                print(f"    ? {g}")
            print(f"\n  BLIND SPOT:")
            for b in p.blind_spots:
                print(f"    >> {b}")

        print(f"\n{'=' * 80}")
        print("CONCLUSION: Gap-3 and Gap-4 are invisible from ANY single standard.")
        print("They emerge only when the four standards are integrated into one GSN.")
        print("=" * 80)

        report = self.derivation_report()
        g3 = report["derived"]["Gap-3"]
        g4 = report["derived"]["Gap-4"]

        print("\nHow much of that conclusion is computed:")
        print(f"\n  Gap-3  DERIVED from the goal structure.")
        for goal, srcs in g3["sources_per_goal"].items():
            print(f"    {goal} sourced by: {', '.join(srcs) if srcs else '(none)'}")
        print(f"    Standards sourcing both: "
              f"{g3['standards_sourcing_both'] or 'none'}")
        print(f"    Invisible from every single standard: "
              f"{g3['invisible_from_every_single_standard']}")

        print(f"\n  Gap-4  DERIVED FROM A STATED PREMISE.")
        print(f"    {g4['premise']}")
        print(f"    Standards contributing at {g4['goal']}: "
              f"{g4['union_contributor_count']} in the union, "
              f"{g4['contributors_in_any_single_standard_view']} in any single view")
        print(f"    Invisible under the premise: {g4['invisible_under_premise']}")
        print(f"    {g4['caveat']}")

        print("\n  Gap-1, Gap-2, Gap-5  ASSERTED, not computed.")
        print(f"    {report['asserted_not_computed']['reason']}")
        print("=" * 80)

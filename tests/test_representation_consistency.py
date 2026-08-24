"""Hold the repository's two views of the argument to each other.

The same fact, which standards contribute to which goal, is written down twice:

  1. ``build_integrated_gsn()`` sets ``source_standards`` on each goal.
  2. Each ``Claim`` in ``src/standards/`` carries a ``gsn_goal``.

Nothing kept the two in step. They drifted, and the drift reached a published
claim: an ISO 26262 claim mapped to G2 made G2 appear to draw on all four
standards under ``compute_goal_density()``, which would have contradicted the
paper's claim that G5 is the only such node, while the goal's own
``source_standards`` still said three. The claim turned out to be a system-level
obligation outside the AI component's scope (commit ``f9a7902``).

These tests exist so that drift fails the build rather than surviving to a
reader. Where the two views differ for a reason, the reason is recorded here as
an explicit exception rather than left as a silent mismatch.
"""

from __future__ import annotations

import pytest

from src.gsn.integrated_pattern import build_integrated_gsn
from src.standards.base import LifecyclePhase
from src.standards.registry import StandardsRegistry

NORMATIVE = {"ISO26262", "ISO21448", "ISO21434", "ISOPAS8800"}

# Goals whose meaning fixes a single lifecycle phase. Every claim at one of
# these must sit in that phase.
GOAL_EXPECTED_PHASE = {
    "G2": LifecyclePhase.CONCEPT,
    "G3": LifecyclePhase.DESIGN,
    "G4": LifecyclePhase.DESIGN,
    "G6": LifecyclePhase.OPERATION,
    "G9": LifecyclePhase.MODIFICATION,
}

# Goals that legitimately hold claims from several phases, with the reason.
# These are excluded from the phase check rather than exempted silently.
MULTI_PHASE_GOALS = {
    "G1": "Top-level claim; gathers HARA and TARA inputs and the case itself.",
    "G5": "V&V sufficiency spans integration testing and validation.",
    "G7": "SOTIF residual risk is an acceptability judgement across phases.",
    "G8": "The cybersecurity case spans TARA, control design and verification.",
}

# Goals where source_standards and the claim mapping differ for a stated reason.
REPRESENTATION_EXCEPTIONS = {
    "G8": (
        "source_standards lists ISO26262 for the normative bridge RQ-15-06, which "
        "derives TARA impact ratings from ISO 26262-3 severity classes. The bridge "
        "is carried by an ISO/SAE 21434 claim (CLM-21434-BRIDGE-01), so ISO 26262 "
        "contributes a bridge rather than a claim of its own."
    ),
    "G9": (
        "G9 is undeveloped, so it declares no source_standards. Two claims map to "
        "it (CLM-26262-CHG-01, CLM-8800-MOD-01), which is the partial coverage the "
        "paper describes for F-2."
    ),
}


@pytest.fixture(scope="module")
def goal_sources() -> dict[str, set[str]]:
    return {
        g.element_id: {s for s in (g.source_standards or []) if s in NORMATIVE}
        for g in build_integrated_gsn().get_goals()
    }


@pytest.fixture(scope="module")
def claim_sources() -> dict[str, set[str]]:
    registry = StandardsRegistry()
    out: dict[str, set[str]] = {}
    for goal in {g.element_id for g in build_integrated_gsn().get_goals()}:
        out[goal] = {
            s.standard_id
            for s in registry.normative_standards
            if any(getattr(c, "gsn_goal", None) == goal for c in s.claims)
        }
    return out


class TestRepresentationsAgree:
    """source_standards against the claim-to-goal mapping."""

    def test_the_two_views_agree_where_no_exception_is_recorded(
        self, goal_sources, claim_sources
    ):
        mismatches = {
            goal: (sorted(goal_sources[goal]), sorted(claim_sources[goal]))
            for goal in goal_sources
            if goal not in REPRESENTATION_EXCEPTIONS
            and goal_sources[goal] != claim_sources[goal]
        }
        assert not mismatches, (
            "source_standards and the claim mapping disagree at: "
            f"{mismatches}. Either fix the mapping or record an exception with a "
            "reason in REPRESENTATION_EXCEPTIONS."
        )

    def test_recorded_exceptions_still_differ(self, goal_sources, claim_sources):
        """An exception that no longer applies must be removed, not left behind."""
        for goal in REPRESENTATION_EXCEPTIONS:
            assert goal_sources[goal] != claim_sources[goal], (
                f"{goal} is listed as an exception but the two views now agree. "
                "Delete the exception."
            )

    def test_every_exception_states_a_reason(self):
        for goal, reason in REPRESENTATION_EXCEPTIONS.items():
            assert len(reason) > 40, f"{goal} exception has no real reason"

    def test_g5_is_the_only_all_four_node_in_both_views(
        self, goal_sources, claim_sources
    ):
        """Section 4.2, the paper's central structural claim, under both views."""
        by_source = sorted(g for g, s in goal_sources.items() if len(s) == 4)
        by_claims = sorted(g for g, s in claim_sources.items() if len(s) == 4)
        assert by_source == ["G5"], f"all-four by source_standards: {by_source}"
        assert by_claims == ["G5"], f"all-four by claim mapping: {by_claims}"


class TestClaimPhaseMatchesGoal:
    """A claim's lifecycle phase against the goal it maps to."""

    @pytest.mark.parametrize("goal", sorted(GOAL_EXPECTED_PHASE))
    def test_single_phase_goals_hold_only_that_phase(self, goal):
        registry = StandardsRegistry()
        expected = GOAL_EXPECTED_PHASE[goal]
        wrong = [
            (c.claim_id, c.lifecycle_phase.value)
            for s in registry.all_standards
            for c in s.claims
            if getattr(c, "gsn_goal", None) == goal and c.lifecycle_phase != expected
        ]
        assert not wrong, (
            f"{goal} expects {expected.value} but holds {wrong}. This is the check "
            "that CLM-26262-TSC-01 would have failed while it sat at G2."
        )

    def test_multi_phase_goals_really_are_multi_phase(self):
        """Guard the exclusion list: a goal listed here must earn its place."""
        registry = StandardsRegistry()
        for goal in MULTI_PHASE_GOALS:
            phases = {
                c.lifecycle_phase
                for s in registry.all_standards
                for c in s.claims
                if getattr(c, "gsn_goal", None) == goal
            }
            assert len(phases) > 1, (
                f"{goal} is excluded from the phase check but has one phase "
                f"({phases}). Remove it from MULTI_PHASE_GOALS."
            )

    def test_every_goal_is_either_checked_or_excused(self, goal_sources):
        covered = set(GOAL_EXPECTED_PHASE) | set(MULTI_PHASE_GOALS)
        assert set(goal_sources) <= covered, (
            f"goals in neither list: {set(goal_sources) - covered}"
        )


class TestOutOfScopeClaimsAreDeclared:
    """A claim with no goal must say why, or it is an unmapped claim."""

    def test_no_silently_unmapped_claims(self):
        registry = StandardsRegistry()
        silent = [
            c.claim_id
            for s in registry.all_standards
            for c in s.claims
            if getattr(c, "gsn_goal", None) is None and not c.out_of_scope_reason
        ]
        assert not silent, f"claims with no goal and no reason: {silent}"

    def test_the_out_of_scope_set_is_exactly_what_was_agreed(self):
        """Pin the set, so the reason field cannot become an escape hatch.

        Without this, any claim could be quietly removed from the argument by
        setting gsn_goal=None and writing a sentence, and every other test would
        still pass while mapped_claims silently dropped.
        """
        registry = StandardsRegistry()
        out_of_scope = sorted(
            c.claim_id
            for s in registry.all_standards
            for c in s.claims
            if c.is_out_of_scope
        )
        assert out_of_scope == ["CLM-26262-TSC-01"], (
            "The set of claims held outside the AI-component argument changed. "
            "That is a scope decision for the authors, not a code change."
        )

    def test_completeness_numbers_reconcile(self):
        """mapped + out_of_scope + unmapped must equal total."""
        from src.analysis.completeness import check_gsn_completeness

        r = check_gsn_completeness()
        assert (
            r.mapped_claims + len(r.out_of_scope_claims) + len(r.unmapped_claims)
            == r.total_claims
        )
        assert str(r.total_claims) not in r.explanation.split("map to GSN nodes")[0].split(
            "of "
        )[0], "explanation must not claim all claims map"

    def test_the_technical_safety_concept_claim_is_recorded_out_of_scope(self):
        """It is kept, not deleted, so the obligation stays visible."""
        registry = StandardsRegistry()
        claim = next(
            c
            for s in registry.all_standards
            for c in s.claims
            if c.claim_id == "CLM-26262-TSC-01"
        )
        assert claim.is_out_of_scope
        assert "system safety case" in claim.out_of_scope_reason
        assert claim.source_clause.reference == "Part 4, Cl.6.4.3"

"""Hold the GSN YAML against the builder the test suite reads.

The nine-goal argument is written down twice:

  1. ``gsn/integrated_pattern.gsn.yaml`` — the source ``gsn2x`` renders into the
     SVG a poster reader sees.
  2. ``build_integrated_gsn()`` in ``src/gsn/integrated_pattern.py`` — the object
     every claim in the test suite is checked against.

Nothing kept the two in step. This is the same defect class as the drift that
reached a published claim at G2 (see ``REPO_AUDIT.md`` and
``tests/test_representation_consistency.py``), in the one place still unchecked:
the rendered diagram is visible to readers and, until this module, invisible to
the suite.

What is compared: the topology (the structural nodes and the support/context
edges among them, and the number of evidence solutions under each goal), the set
of standards contributing to each goal, and the two structural claims the paper
rests on — that G5 is the only four-standard node and G3 the only single-standard
retained goal.

What is NOT compared, and why:

  * Solution node identifiers. The YAML names evidence positionally (``Sn1`` …
    ``Sn21``); the builder names it semantically (``Sn-G5-mcdc`` …). The two
    cannot be joined by id, so this module compares the *count* of solutions
    under each goal, not their identity. Whether to align the two naming schemes
    is an open decision for the authors.
  * Clause-reference strings. The YAML deliberately carries a simplified subset
    so the rendered diagram stays legible at poster size; the full,
    edition-bearing references live in ``TRACEABILITY.md``. Comparing them would
    force the YAML to carry strings no reader could read on the poster.

Where the two differ for a reason, the reason is recorded here as an explicit
exception rather than left as a silent mismatch, mirroring
``test_representation_consistency.py``.
"""

from __future__ import annotations

import copy
import os
import re

import pytest

yaml = pytest.importorskip("yaml")

from src.gsn.integrated_pattern import build_integrated_gsn  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML_PATH = os.path.join(REPO_ROOT, "gsn", "integrated_pattern.gsn.yaml")

NORMATIVE = {"ISO26262", "ISO21448", "ISO21434", "ISOPAS8800"}

# A standard's number, as it appears in the cited clause text of a solution,
# maps to its id. The four numbers are mutually non-overlapping as substrings.
STANDARD_TOKENS = {
    "26262": "ISO26262",
    "21448": "ISO21448",
    "21434": "ISO21434",
    "8800": "ISOPAS8800",
}

# Goals where the YAML and the builder attribute a different standard set, each
# for a reason the authors have accepted.
STANDARD_EXCEPTIONS = {
    "G8": (
        "The builder lists ISO 26262 at G8 for the RQ-15-06 bridge, which derives "
        "TARA impact ratings from ISO 26262-3 severity classes. The YAML shows "
        "ISO/SAE 21434 only, matching the paper's Table 2: the bridge is a "
        "structural link between standards, not a source of claims at this goal."
    ),
}

# Goals excluded from the per-goal standard comparison, with the reason. G1 is
# the top goal: its standards enter through the strategy S1 and the contexts
# C1/C2, not through evidence solutions attached to it, so the YAML attributes no
# standard to G1 at the goal level.
STANDARD_UNCOMPARED = {
    "G1": (
        "Top goal, supported by the strategy rather than by evidence solutions; "
        "the YAML attaches no standard-bearing solution to it, so there is nothing "
        "to compare against the builder's source_standards at this node."
    ),
}

# The goals retained from ISO/PAS 8800 Annex B. The paper's single-standard claim
# is made about these; G7/G8 are new goals and G1/G9 are the top goal and the gap.
RETAINED_GOALS = ["G2", "G3", "G4", "G5", "G6"]


# ── YAML node classification ───────────────────────────────────────────
def _is_goal(node_id: str) -> bool:
    return re.fullmatch(r"G\d+", node_id) is not None


def _is_solution(node_id: str) -> bool:
    return re.fullmatch(r"Sn\d+", node_id) is not None


def _norm(node_id: str) -> str:
    """The YAML writes the assumption id as ``A1_4``; the builder as ``A1.4``."""
    return node_id.replace("_", ".")


@pytest.fixture(scope="module")
def yaml_nodes() -> dict:
    with open(YAML_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


# ── Skeletons: the same shape, drawn from each representation ───────────
def _yaml_skeleton(nodes: dict) -> dict:
    goals = sorted(nid for nid in nodes if _is_goal(nid))

    def supported(nid: str) -> list[str]:
        return nodes.get(nid, {}).get("supportedBy", []) or []

    def context(nid: str) -> list[str]:
        return [_norm(c) for c in (nodes.get(nid, {}).get("inContextOf", []) or [])]

    return {
        "goals": goals,
        "undeveloped": sorted(
            nid for nid in goals if nodes[nid].get("undeveloped")
        ),
        "g1_supported_by": sorted(c for c in supported("G1") if not _is_solution(c)),
        "g1_in_context_of": sorted(context("G1")),
        "s1_supports": sorted(c for c in supported("S1") if _is_goal(c)),
        "s1_in_context_of": sorted(context("S1")),
        "solution_fanout": {
            nid: sum(1 for c in supported(nid) if _is_solution(c)) for nid in goals
        },
    }


def _builder_skeleton() -> dict:
    gsn = build_integrated_gsn()
    solution_ids = {s.element_id for s in gsn.get_solutions()}

    def is_sol(cid: str) -> bool:
        return cid in solution_ids

    g1 = gsn.get_element("G1")
    s1 = gsn.get_element("S1")
    return {
        "goals": sorted(g.element_id for g in gsn.get_goals()),
        "undeveloped": sorted(g.element_id for g in gsn.get_undeveloped_goals()),
        "g1_supported_by": sorted(c for c in g1.supported_by if not is_sol(c)),
        "g1_in_context_of": sorted(g1.in_context_of),
        "s1_supports": sorted(c for c in s1.supported_by if _is_goal(c)),
        "s1_in_context_of": sorted(s1.in_context_of),
        "solution_fanout": {
            g.element_id: sum(1 for c in g.supported_by if is_sol(c))
            for g in gsn.get_goals()
        },
    }


# ── Per-goal standard sets ─────────────────────────────────────────────
def _standards_in_text(text: str) -> set[str]:
    return {sid for tok, sid in STANDARD_TOKENS.items() if tok in text}


def _yaml_goal_standards(nodes: dict) -> dict[str, set[str]]:
    """Which standards each goal draws on, read from its evidence solutions."""
    out: dict[str, set[str]] = {}
    for nid in nodes:
        if not _is_goal(nid):
            continue
        stds: set[str] = set()
        for child in nodes[nid].get("supportedBy", []) or []:
            if _is_solution(child):
                stds |= _standards_in_text(nodes[child].get("text", ""))
        out[nid] = stds
    return out


def _builder_goal_standards() -> dict[str, set[str]]:
    return {
        g.element_id: {s for s in (g.source_standards or []) if s in NORMATIVE}
        for g in build_integrated_gsn().get_goals()
    }


class TestTopologyMatches:
    """The two representations describe the same graph."""

    def test_the_skeletons_are_identical(self, yaml_nodes):
        assert _yaml_skeleton(yaml_nodes) == _builder_skeleton()

    def test_g9_is_the_only_undeveloped_goal_in_both(self, yaml_nodes):
        assert _yaml_skeleton(yaml_nodes)["undeveloped"] == ["G9"]
        assert _builder_skeleton()["undeveloped"] == ["G9"]

    def test_g5_carries_four_evidence_solutions_in_both(self, yaml_nodes):
        assert _yaml_skeleton(yaml_nodes)["solution_fanout"]["G5"] == 4
        assert _builder_skeleton()["solution_fanout"]["G5"] == 4


class TestPerGoalStandardsMatch:
    """The same fact — which standards contribute to which goal — in both."""

    def test_standards_match_the_builder(self, yaml_nodes):
        yaml_sets = _yaml_goal_standards(yaml_nodes)
        builder_sets = _builder_goal_standards()
        mismatches = {
            g: (sorted(yaml_sets[g]), sorted(builder_sets[g]))
            for g in builder_sets
            if g not in STANDARD_EXCEPTIONS
            and g not in STANDARD_UNCOMPARED
            and yaml_sets[g] != builder_sets[g]
        }
        assert not mismatches, (
            "The YAML diagram and the builder attribute different standards at: "
            f"{mismatches}. Fix the side that is wrong, or record an exception "
            "with a reason in STANDARD_EXCEPTIONS — do not silence it."
        )

    def test_recorded_exceptions_still_differ(self, yaml_nodes):
        """An exception that no longer applies must be removed, not left behind."""
        yaml_sets = _yaml_goal_standards(yaml_nodes)
        builder_sets = _builder_goal_standards()
        for g in STANDARD_EXCEPTIONS:
            assert yaml_sets[g] != builder_sets[g], (
                f"{g} is a recorded exception but the two views now agree. "
                "Delete the exception."
            )

    def test_uncompared_goals_carry_no_solution_standard(self, yaml_nodes):
        """Guard the exclusion: if the YAML gains evidence at G1, compare it."""
        yaml_sets = _yaml_goal_standards(yaml_nodes)
        for g in STANDARD_UNCOMPARED:
            assert yaml_sets[g] == set(), (
                f"{g} is excluded from the standard comparison because it has no "
                f"standard-bearing solution, but now it does: {sorted(yaml_sets[g])}. "
                "Remove it from STANDARD_UNCOMPARED and compare it."
            )

    def test_every_exception_states_a_reason(self):
        for g, reason in {**STANDARD_EXCEPTIONS, **STANDARD_UNCOMPARED}.items():
            assert len(reason) > 40, f"{g} exception has no real reason"


class TestPaperStructuralClaimsHoldInBoth:
    """The two claims Section 4.2 rests on, checked from both representations."""

    def test_g5_is_the_only_four_standard_node(self, yaml_nodes):
        yaml_sets = _yaml_goal_standards(yaml_nodes)
        builder_sets = _builder_goal_standards()
        assert sorted(g for g, s in yaml_sets.items() if len(s) == 4) == ["G5"]
        assert sorted(g for g, s in builder_sets.items() if len(s) == 4) == ["G5"]

    def test_g3_is_the_only_single_standard_retained_goal(self, yaml_nodes):
        yaml_sets = _yaml_goal_standards(yaml_nodes)
        builder_sets = _builder_goal_standards()
        yaml_single = sorted(g for g in RETAINED_GOALS if len(yaml_sets[g]) == 1)
        builder_single = sorted(g for g in RETAINED_GOALS if len(builder_sets[g]) == 1)
        assert yaml_single == ["G3"], f"single-standard retained goals (YAML): {yaml_single}"
        assert builder_single == ["G3"], f"single-standard retained goals (builder): {builder_single}"
        assert yaml_sets["G3"] == {"ISOPAS8800"}
        assert builder_sets["G3"] == {"ISOPAS8800"}


class TestTheCheckHasTeeth:
    """A checker that cannot fail is worthless. Perturb a copy and confirm the
    comparison notices, so this guard cannot rot into a no-op."""

    def test_a_dropped_solution_is_caught(self, yaml_nodes):
        broken = copy.deepcopy(yaml_nodes)
        broken["G5"]["supportedBy"] = broken["G5"]["supportedBy"][:-1]
        assert _yaml_skeleton(broken) != _builder_skeleton()

    def test_a_moved_context_edge_is_caught(self, yaml_nodes):
        broken = copy.deepcopy(yaml_nodes)
        broken["G1"]["inContextOf"] = ["C1"]
        assert _yaml_skeleton(broken) != _builder_skeleton()

    def test_a_standard_re_pointing_is_caught(self, yaml_nodes):
        broken = copy.deepcopy(yaml_nodes)
        broken["Sn4"]["text"] = broken["Sn4"]["text"] + " and ISO/SAE 21434 Cl.1"
        assert _yaml_goal_standards(broken)["G3"] != {"ISOPAS8800"}

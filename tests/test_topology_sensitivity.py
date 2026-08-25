"""F-3 and F-4 are not an artefact of the argument tree.

These tests hold the derivation in ``topology_sensitivity.py`` to its claim:
that the two integration-induced findings arise under both the activity-based
tree the paper uses and the Warg & Skoglund concern hierarchy it names but does
not adopt. The two topologies are encoded independently (one read from the
builder, one from the paper's description), so agreement between them is
evidence, not construction.
"""

from __future__ import annotations

from src.analysis.topology_sensitivity import (
    activity_based_topology,
    concern_hierarchy_topology,
    derive_gap3,
    derive_gap4,
    topologies,
    topology_report,
)
from src.gsn.integrated_pattern import build_integrated_gsn


class TestBothTopologiesAreEncoded:
    def test_two_topologies_are_compared(self):
        assert len(topologies()) == 2

    def test_activity_topology_is_read_from_the_builder(self):
        """Not hand-set: its node standards come from build_integrated_gsn."""
        goals = {g.element_id: set(g.source_standards or []) for g in build_integrated_gsn().get_goals()}
        activity = activity_based_topology()
        assert set(activity.node_standards["G5 (V&V)"]) == goals["G5"]
        assert set(activity.node_standards["G7 (SOTIF residual risk)"]) == goals["G7"]
        assert set(activity.node_standards["G8 (cybersecurity treatment)"]) == goals["G8"]

    def test_concern_hierarchy_groups_standards_by_subject(self):
        concern = concern_hierarchy_topology()
        assert concern.node_standards["SOTIF"] == frozenset({"ISO21448"})
        assert concern.node_standards["Cybersecurity"] == frozenset({"ISO21434"})
        assert concern.node_standards["AI safety"] == frozenset({"ISOPAS8800"})
        assert concern.node_standards["Functional safety"] == frozenset({"ISO26262"})


class TestFindingsAreDerivedNotAsserted:
    def test_gap3_arises_under_every_topology(self):
        for topology in topologies():
            result = derive_gap3(topology)
            assert result["arises"], topology.name
            assert result["standards_spanning_both"] == [], topology.name

    def test_gap4_arises_under_every_topology(self):
        for topology in topologies():
            result = derive_gap4(topology)
            assert result["arises"], topology.name
            assert result["contributor_count"] > 1, topology.name


class TestTheTreeQuestionHasAnAnswer:
    def test_the_findings_are_not_an_artefact_of_the_tree(self):
        report = topology_report()
        assert report["gap3_arises_under_every_topology"] is True
        assert report["gap4_arises_under_every_topology"] is True
        assert report["findings_are_an_artefact_of_the_tree"] is False

    def test_the_answer_states_the_invariance(self):
        assert "not an artefact" in topology_report()["answer"]

    def test_report_is_deterministic(self):
        assert topology_report() == topology_report()

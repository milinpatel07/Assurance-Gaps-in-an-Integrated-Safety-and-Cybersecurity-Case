"""The Annex B base and the 6-to-9 extension delta.

The WAISE paper's headline is that the integrated pattern extends ISO/PAS 8800
Annex B from six goals to nine. These tests hold that claim to two independent
encodings: the base pattern in ``annex_b_base.py`` and the integrated pattern in
``integrated_pattern.py``. The delta is computed from the difference, so "six to
nine" is checked rather than narrated, and the per-goal augmentation must agree
with the ``augmented_from`` field the integrated builder records separately.
"""

from __future__ import annotations

from src.gsn.annex_b_base import build_annex_b_base, compute_extension_delta
from src.gsn.integrated_pattern import build_integrated_gsn


class TestTheBaseIsAnnexBAsPublished:
    def test_the_base_has_exactly_six_goals(self):
        assert len(build_annex_b_base().get_goals()) == 6

    def test_the_base_goals_are_g1_to_g6(self):
        ids = {g.element_id for g in build_annex_b_base().get_goals()}
        assert ids == {"G1", "G2", "G3", "G4", "G5", "G6"}

    def test_every_base_goal_sources_iso_pas_8800_alone(self):
        """Annex B is an ISO/PAS 8800 artefact. If the base carried another
        standard it would be the integrated pattern, and the delta would prove
        nothing."""
        for goal in build_annex_b_base().get_goals():
            assert set(goal.source_standards or []) == {"ISOPAS8800"}, goal.element_id

    def test_the_base_carries_the_strategy_and_the_assumption(self):
        base = build_annex_b_base()
        assert base.get_element("S1") is not None
        assert base.get_element("A1.4") is not None


class TestTheExtensionIsSixToNine:
    def test_the_delta_reports_six_to_nine(self):
        delta = compute_extension_delta()
        assert delta["base_goal_count"] == 6
        assert delta["integrated_goal_count"] == 9
        assert delta["goals_added_count"] == 3

    def test_the_three_added_goals_are_g7_g8_g9(self):
        assert compute_extension_delta()["goals_added"] == ["G7", "G8", "G9"]

    def test_the_added_goals_are_exactly_the_non_retained_ones_in_the_builder(self):
        """The added set must match the integrated builder's own origin field:
        the goals it marks 'new' or 'undeveloped'."""
        integrated = build_integrated_gsn()
        by_origin = {
            g.element_id
            for g in integrated.get_goals()
            if g.origin in ("new", "undeveloped")
        }
        assert set(compute_extension_delta()["goals_added"]) == by_origin

    def test_the_retained_goals_are_the_builders_retained_ones(self):
        integrated = build_integrated_gsn()
        retained = {g.element_id for g in integrated.get_goals() if g.origin == "retained"}
        assert set(compute_extension_delta()["goals_retained"]) == retained


class TestTheAugmentationAgreesWithTheBuilder:
    """The computed per-goal augmentation must match the ``augmented_from``
    field the integrated builder records independently. Two representations of
    'what was added', held to each other."""

    def test_augmented_goals_match_their_augmented_from_field(self):
        integrated = {g.element_id: g for g in build_integrated_gsn().get_goals()}
        augmentation = compute_extension_delta()["augmentation_of_retained_goals"]
        for gid, goal in integrated.items():
            recorded = sorted(set(goal.augmented_from or []))
            if recorded:
                assert augmentation[gid] == recorded, gid

    def test_g3_is_the_single_standard_goal_and_is_unchanged(self):
        assert compute_extension_delta()["augmentation_of_retained_goals"]["G3"] == []

    def test_g1_is_reformulated_not_evidence_augmented(self):
        """G1 gains ISO 26262 and ISO/SAE 21434 through its contexts (ASIL,
        TARA) and the reformulated top claim, not through added evidence legs,
        so the builder records no ``augmented_from`` for it. The delta still
        sees the two standards on its integrated source list. This guards that
        one documented mismatch rather than letting it surprise a later reader."""
        integrated = {g.element_id: g for g in build_integrated_gsn().get_goals()}
        assert not integrated["G1"].augmented_from
        assert compute_extension_delta()["augmentation_of_retained_goals"]["G1"] == [
            "ISO21434",
            "ISO26262",
        ]

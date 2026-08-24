"""Tests that validate every numbered claim in the paper.

These tests serve as machine-checkable proof that the implementation
faithfully represents the paper's findings. Each test references the
specific section, table, or figure it validates.
"""

import pytest

from src.gsn.integrated_pattern import build_integrated_gsn
from src.gsn.model import Goal, Strategy, Context, Assumption, GoalStatus
from src.standards.registry import StandardsRegistry
from src.standards.base import InconsistencyType, GapType, LifecyclePhase
from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis
from src.analysis.completeness import check_gsn_completeness
from src.analysis.counterfactual import CounterfactualAnalysis
from src.analysis.traceability import TraceabilityMatrix


# ── Section 4: Integrated GSN Argument Pattern ──────────────────────


class TestTopLevelStructure:
    """Validate claims from Section 4.1 (Top-Level Structure)."""

    @pytest.fixture
    def gsn(self):
        return build_integrated_gsn()

    def test_extends_annex_b_from_six_to_nine_goals(self, gsn):
        """Section 4: 'extends the ISO/PAS 8800 Annex B structure from six
        goals to nine'."""
        goals = gsn.get_goals()
        assert len(goals) == 9
        retained = [g for g in goals if g.origin == "retained"]
        assert len(retained) == 6  # G1-G6 from Annex B

    def test_adds_two_context_nodes(self, gsn):
        """Section 4: 'adds two context nodes'."""
        contexts = gsn.get_contexts()
        assert len(contexts) == 2
        ids = {c.element_id for c in contexts}
        assert ids == {"C1", "C2"}

    def test_retains_one_assumption(self, gsn):
        """Section 4: 'retains one assumption'."""
        assumptions = gsn.get_assumptions()
        assert len(assumptions) == 1
        assert assumptions[0].element_id == "A1.4"

    def test_g1_reformulated_claim(self, gsn):
        """Section 4.1: G1 reformulated to include cybersecurity."""
        g1 = gsn.get_element("G1")
        assert "cybersecurity" in g1.text.lower()
        assert "integrated" in g1.text.lower()

    def test_c1_carries_asil(self, gsn):
        """Section 4.1: 'Context C1 carries the ASIL from ISO 26262-3 HARA'."""
        c1 = gsn.get_element("C1")
        assert "ASIL" in c1.text
        assert "ISO26262" in c1.source_standards

    def test_c2_carries_tara(self, gsn):
        """Section 4.1: 'Context C2 carries the TARA results'."""
        c2 = gsn.get_element("C2")
        assert "TARA" in c2.text
        assert "ISO21434" in c2.source_standards

    def test_s1_argues_over_four_domains(self, gsn):
        """Section 4.1: 'strategy argues over four assurance domains'."""
        s1 = gsn.get_element("S1")
        assert isinstance(s1, Strategy)
        assert len(s1.source_standards) == 4


class TestSubGoalDecomposition:
    """Validate claims from Section 4.2 (Sub-Goal Decomposition)."""

    @pytest.fixture
    def gsn(self):
        return build_integrated_gsn()

    def test_g2_three_types_of_completeness(self, gsn):
        """Section 4.2: G2 covers three types of completeness."""
        g2 = gsn.get_element("G2")
        assert len(g2.source_standards) == 3
        assert "ISOPAS8800" in g2.source_standards
        assert "ISO21448" in g2.source_standards
        assert "ISO21434" in g2.source_standards

    def test_g3_single_standard_source(self, gsn):
        """Section 4.2: 'G3 is the only goal where a single standard is
        the sole source of claims'."""
        g3 = gsn.get_element("G3")
        assert g3.source_standards == ["ISOPAS8800"]
        # Verify no other goal has only one standard (except G7, G9)
        for goal in gsn.get_goals():
            if goal.element_id in ("G7", "G9"):
                continue
            if goal.element_id != "G3":
                assert len(goal.source_standards) >= 2, (
                    f"{goal.element_id} also has single standard"
                )

    def test_g5_only_node_all_four_standards(self, gsn):
        """Section 4.2: 'G5 is the only node where all four applicable
        standards contribute claims'."""
        g5 = gsn.get_element("G5")
        assert len(g5.source_standards) == 4
        # Verify no other goal has 4 standards
        for goal in gsn.get_goals():
            if goal.element_id != "G5":
                assert len(goal.source_standards) < 4, (
                    f"{goal.element_id} also has 4 standards"
                )

    def test_g5_has_four_evidence_types(self, gsn):
        """Section 4.2: four evidence types at G5."""
        g5 = gsn.get_element("G5")
        assert len(g5.supported_by) == 4

    def test_g7_is_acceptability_judgement(self, gsn):
        """Section 4.2: G7 is 'separate from G5 because it represents an
        acceptability judgement, not a verification activity'."""
        g7 = gsn.get_element("G7")
        assert g7.origin == "new"
        assert "ISO21448" in g7.source_standards

    def test_g8_has_safety_bridge(self, gsn):
        """Section 4.2: G8 has '[RQ-15-06] safety bridge'."""
        g8 = gsn.get_element("G8")
        refs = " ".join(g8.clause_references)
        assert "RQ-15-06" in refs

    def test_g9_undeveloped_no_complete_workflow(self, gsn):
        """Section 4.2: G9 'marked as undeveloped because no single standard
        prescribes the complete re-assurance workflow'."""
        g9 = gsn.get_element("G9")
        assert g9.status == GoalStatus.UNDEVELOPED
        assert g9.origin == "undeveloped"

    def test_g9_is_only_undeveloped_goal(self, gsn):
        """G9 should be the only undeveloped goal."""
        undeveloped = gsn.get_undeveloped_goals()
        assert len(undeveloped) == 1
        assert undeveloped[0].element_id == "G9"

    def test_all_retained_goals_augmented(self, gsn):
        """Section 4: 'All five retained goals receive additional claims
        from at least one other standard'."""
        # G2-G6 are retained; all should have augmented_from or multiple standards
        for gid in ["G2", "G4", "G5", "G6"]:
            goal = gsn.get_element(gid)
            assert len(goal.source_standards) >= 2 or goal.augmented_from, (
                f"{gid} not augmented"
            )


# ── Section 5: Inconsistencies and Gaps ──────────────────────────────


class TestInconsistencyClaims:
    """Validate claims from Section 5.1 (Requirement Inconsistencies)."""

    @pytest.fixture
    def catalogue(self):
        return DecisionPointCatalogue()

    def test_exactly_seven_inconsistencies(self, catalogue):
        """Section 5.1: 'Step 4 identifies seven requirement
        inconsistencies'."""
        assert len(catalogue.inconsistencies) == 7

    def test_three_structural_two_terminological_two_methodological(self, catalogue):
        """Section 5.1: classification counts."""
        stats = catalogue.summary_statistics()
        assert stats["structural"] == 3
        assert stats["terminological"] == 2
        assert stats["methodological"] == 2

    def test_i1_incompatible_risk_classification(self, catalogue):
        """Section 5.1: I-1 involves three risk frameworks."""
        i1 = catalogue.get_by_id("I-1")
        assert i1.inconsistency_type == InconsistencyType.STRUCTURAL
        assert set(i1.standards_involved) == {"ISO26262", "ISO21448", "ISO21434"}
        assert "G1" in i1.gsn_nodes

    def test_i2_central_finding(self, catalogue):
        """Section 5.1: I-2 is 'the central finding of the analysis'."""
        i2 = catalogue.get_by_id("I-2")
        assert i2.inconsistency_type == InconsistencyType.STRUCTURAL
        assert len(i2.standards_involved) == 4  # All four
        assert "G5" in i2.gsn_nodes

    def test_i5_boundary_ambiguity(self, catalogue):
        """Section 5.1: I-5 affects both G7 and G8."""
        i5 = catalogue.get_by_id("I-5")
        assert i5.inconsistency_type == InconsistencyType.STRUCTURAL
        assert set(i5.gsn_nodes) == {"G7", "G8"}

    def test_terminological_resolvable(self, catalogue):
        """Section 5.1: 'Terminological (I-3, I-4) ... can be resolved
        within a project'."""
        for iid in ["I-3", "I-4"]:
            inc = catalogue.get_by_id(iid)
            assert inc.inconsistency_type == InconsistencyType.TERMINOLOGICAL

    def test_methodological_resolvable(self, catalogue):
        """Section 5.1: 'methodological (I-6, I-7) inconsistencies can be
        resolved within a project'."""
        for iid in ["I-6", "I-7"]:
            inc = catalogue.get_by_id(iid)
            assert inc.inconsistency_type == InconsistencyType.METHODOLOGICAL

    def test_structural_require_decisions(self, catalogue):
        """Section 5.1: 'Structural inconsistencies (I-1, I-2, I-5) require
        decisions that no standard prescribes'."""
        for iid in ["I-1", "I-2", "I-5"]:
            inc = catalogue.get_by_id(iid)
            assert inc.inconsistency_type == InconsistencyType.STRUCTURAL

    def test_all_inconsistencies_have_at_least_two_clause_references(self, catalogue):
        """Each inconsistency should reference clauses from multiple standards."""
        for inc in catalogue.inconsistencies:
            assert len(inc.clause_references) >= 2, (
                f"{inc.inconsistency_id} has fewer than 2 clause references"
            )


class TestGapClaims:
    """Validate claims from Section 5.2 (Assurance Gaps)."""

    @pytest.fixture
    def gaps(self):
        return GapClassification()

    def test_exactly_five_gaps(self, gaps):
        """Section 5.2: 'Step 5 identifies five assurance gaps'."""
        assert len(gaps.gaps) == 5

    def test_exactly_two_integration_induced(self, gaps):
        """Section 5.2: 'Two of the six (Gap-3 and Gap-4) are
        integration-induced'."""
        induced = gaps.get_integration_induced()
        assert len(induced) == 2
        assert {g.gap_id for g in induced} == {"Gap-3", "Gap-4"}

    def test_gap1_no_ai_reliability_target(self, gaps):
        """Section 5.2: Gap-1 description."""
        gap1 = gaps.get_by_id("Gap-1")
        assert gap1.gap_type == GapType.MISSING_EVIDENCE
        assert gap1.lifecycle_phase == LifecyclePhase.VERIFICATION

    def test_gap2_no_ota_reassurance(self, gaps):
        """Section 5.2: Gap-2 in modification phase."""
        gap2 = gaps.get_by_id("Gap-2")
        assert gap2.gap_type == GapType.MISSING_CLAIM
        assert gap2.lifecycle_phase == LifecyclePhase.MODIFICATION
        assert not gap2.integration_induced

    def test_gap3_adversarial_sotif_boundary(self, gaps):
        """Section 5.2: Gap-3 is integration-induced."""
        gap3 = gaps.get_by_id("Gap-3")
        assert gap3.gap_type == GapType.UNRESOLVED_INCONSISTENCY
        assert gap3.integration_induced

    def test_gap4_no_cross_domain_release(self, gaps):
        """Section 5.2: Gap-4 is integration-induced."""
        gap4 = gaps.get_by_id("Gap-4")
        assert gap4.gap_type == GapType.MISSING_CLAIM
        assert gap4.lifecycle_phase == LifecyclePhase.INTEGRATION
        assert gap4.integration_induced

    def test_gap5_data_threshold_undefined(self, gaps):
        """Section 5.2: Gap-5 in design phase."""
        gap5 = gaps.get_by_id("Gap-5")
        assert gap5.gap_type == GapType.MISSING_EVIDENCE
        assert gap5.lifecycle_phase == LifecyclePhase.DESIGN

    def test_gap_type_counts_match_table6(self, gaps):
        """Table 6: MC=2, ME=2, UI=1."""
        stats = gaps.summary_statistics()
        assert stats["missing_claim"] == 2
        assert stats["missing_evidence"] == 2
        assert stats["unresolved_inconsistency"] == 1

    def test_all_lifecycle_phases_have_at_least_one_gap(self, gaps):
        """Section 5.2 / Table 6: gaps span multiple phases."""
        phases_with_gaps = {g.lifecycle_phase for g in gaps.gaps}
        # Paper claims gaps in: Verification, Modification, Integration, Concept, Design
        assert len(phases_with_gaps) >= 4


class TestEvidenceConvergenceClaims:
    """Validate claims about the evidence convergence (central finding)."""

    @pytest.fixture
    def analysis(self):
        return EvidenceConvergenceAnalysis()

    def test_four_evidence_types_at_g5(self, analysis):
        """Section 5.1 (I-2): four evidence types converge at G5."""
        assert len(analysis.evidence_types) == 4

    def test_evidence_types_differ_in_scale(self, analysis):
        """Section 5.1: evidence types 'differ in measurement objective,
        production method, and scale'."""
        scales = {et.scale for et in analysis.evidence_types}
        assert len(scales) == 4

    def test_evidence_types_differ_in_method(self, analysis):
        """Each evidence type should have a different production method."""
        methods = {et.how_produced for et in analysis.evidence_types}
        assert len(methods) == 4

    def test_failure_event_three_analysis_paths(self, analysis):
        """Figure 3: single failure event enters through three paths."""
        assert len(analysis.failure_event.analysis_paths) == 3

    def test_all_paths_converge_at_g5(self, analysis):
        """Figure 3: all paths lead to G5."""
        for path in analysis.failure_event.analysis_paths:
            assert path.gsn_node == "G5"

    def test_solution_sketch_has_approaches(self, analysis):
        """The solution sketch should offer concrete combination approaches."""
        sketch = analysis.get_solution_sketch()
        assert len(sketch["approaches"]) >= 2
        assert sketch["recommendation"]

    def test_comparison_matrix_complete(self, analysis):
        """The evidence comparison matrix should have all four entries."""
        matrix = analysis.get_evidence_comparison_matrix()
        assert len(matrix) == 4
        for row in matrix:
            assert "Evidence Type" in row
            assert "Standard" in row
            assert "Scale" in row


# ── Completeness and Counterfactual Validation ───────────────────────


class TestCompletenessCheck:
    """Validate that the 9-goal GSN is structurally complete."""

    def test_gsn_is_complete(self):
        """All claims should map to goals, all phases covered."""
        result = check_gsn_completeness()
        assert result.is_complete, result.explanation

    def test_no_unmapped_claims(self):
        """Every extracted claim maps to a GSN element."""
        result = check_gsn_completeness()
        assert len(result.unmapped_claims) == 0

    def test_all_lifecycle_phases_covered(self):
        """All six lifecycle phases are addressed."""
        result = check_gsn_completeness()
        assert len(result.phases_uncovered) == 0

    def test_only_g9_without_claims(self):
        """Only G9 (undeveloped gap) should lack direct claims."""
        result = check_gsn_completeness()
        unexpected = [g for g in result.goals_without_claims if g != "G9"]
        assert len(unexpected) == 0


class TestCounterfactualValidation:
    """Validate that Gap-3 and Gap-4 are invisible from any single standard."""

    @pytest.fixture
    def counterfactual(self):
        return CounterfactualAnalysis()

    def test_gap3_invisible_from_all_single_standards(self, counterfactual):
        """Gap-3 should not be visible from any individual standard."""
        matrix = counterfactual.get_gap_visibility_matrix()
        for std_id, gaps in matrix.items():
            if std_id == "Integrated":
                assert gaps["Gap-3"] is True
            else:
                assert gaps["Gap-3"] is False, (
                    f"Gap-3 visible from {std_id} alone"
                )

    def test_gap4_invisible_from_all_single_standards(self, counterfactual):
        """Gap-4 should not be visible from any individual standard."""
        matrix = counterfactual.get_gap_visibility_matrix()
        for std_id, gaps in matrix.items():
            if std_id == "Integrated":
                assert gaps["Gap-4"] is True
            else:
                assert gaps["Gap-4"] is False, (
                    f"Gap-4 visible from {std_id} alone"
                )

    def test_integrated_view_sees_all_gaps(self, counterfactual):
        """The integrated perspective should see all five gaps."""
        matrix = counterfactual.get_gap_visibility_matrix()
        integrated = matrix["Integrated"]
        assert all(integrated.values())

    def test_four_standard_perspectives(self, counterfactual):
        """Should have perspectives for all four normative standards."""
        assert len(counterfactual.perspectives) == 4

    def test_each_standard_has_blind_spots(self, counterfactual):
        """Every standard has at least one blind spot."""
        for p in counterfactual.perspectives:
            assert len(p.blind_spots) >= 1, (
                f"{p.standard_id} has no blind spots"
            )


class TestCameraReadyClassifications:
    """Classifications the camera-ready carries that the code had not absorbed.

    Table 4 gives two lifecycle phases for F-1 and F-3, and adds ISO 24089 to
    F-2's coverage row. Table 3 tags DP-2 "S, M" while the prose calls it
    structural in three places; the authors resolved that in favour of the prose,
    so I-2 stays structural and the reasoning sits in decision_points.py.
    """

    @pytest.fixture
    def gaps(self):
        return GapClassification()

    def test_f1_spans_concept_and_verification(self, gaps):
        """Table 4, F-1: 'Concept, Verification'."""
        assert gaps.get_by_id("Gap-1").lifecycle_phase_label == "Concept, Verification"

    def test_f3_spans_verification_and_operation(self, gaps):
        """Table 4, F-3: 'Verification, Operation'."""
        assert gaps.get_by_id("Gap-3").lifecycle_phase_label == "Verification, Operation"

    def test_f2_coverage_includes_iso_24089(self, gaps):
        """Table 4, F-2, camera-ready addition."""
        coverage = " ".join(gaps.get_by_id("Gap-2").partial_coverage)
        assert "24089" in coverage

    def test_f2_stays_single_phase(self, gaps):
        """Table 4 gives F-2 'Modification' alone."""
        assert gaps.get_by_id("Gap-2").lifecycle_phase_label == "Modification"

    def test_primary_phase_is_unchanged_for_every_finding(self, gaps):
        """The added phases must not disturb the existing single-value contract."""
        primary = {g.gap_id: g.lifecycle_phase for g in gaps.gaps}
        assert primary["Gap-1"] == LifecyclePhase.VERIFICATION
        assert primary["Gap-2"] == LifecyclePhase.MODIFICATION
        assert primary["Gap-3"] == LifecyclePhase.VERIFICATION
        assert primary["Gap-4"] == LifecyclePhase.INTEGRATION
        assert primary["Gap-5"] == LifecyclePhase.DESIGN

    def test_i2_follows_the_prose_not_the_table(self):
        """DP-2 is structural per the prose; Table 3's 'S, M' is a known
        inconsistency inside the camera-ready, not a repository defect."""
        catalogue = DecisionPointCatalogue()
        assert catalogue.get_by_id("I-2").inconsistency_type == InconsistencyType.STRUCTURAL
        stats = catalogue.summary_statistics()
        assert stats["structural"] == 3
        assert stats["terminological"] == 2
        assert stats["methodological"] == 2


class TestCounterfactualDerivation:
    """Check the derived half of the counterfactual claim.

    The tests in TestCounterfactualValidation read back the hand-authored
    visibility lists, so they check self-consistency and not much else. These
    tests exercise the derivations, which compute from the goal structure in
    build_integrated_gsn() rather than from anything written in counterfactual.py.
    A change to which standards source G7, G8 or G5 will fail these.
    """

    def test_gap3_derivation_uses_the_g7_g8_boundary(self):
        """Section 5.2, F-3: the boundary lies between G7 and G8."""
        result = CounterfactualAnalysis.derive_gap3_invisibility()
        assert result["boundary_goals"] == ["G7", "G8"]

    def test_gap3_no_standard_sources_both_boundary_goals(self):
        """The derived reason Gap-3 is invisible: nobody holds both ends."""
        result = CounterfactualAnalysis.derive_gap3_invisibility()
        assert result["standards_sourcing_both"] == []
        assert result["invisible_from_every_single_standard"] is True

    def test_gap3_boundary_goals_come_from_different_standards(self):
        """G7 is SOTIF (21448); G8 is cybersecurity (21434, with 26262)."""
        sources = CounterfactualAnalysis.derive_gap3_invisibility()["sources_per_goal"]
        assert "ISO21448" in sources["G7"]
        assert "ISO21434" in sources["G8"]
        assert set(sources["G7"]).isdisjoint(set(sources["G8"]))

    def test_gap4_g5_draws_on_all_four_normative_standards(self):
        """Section 4.2: G5 is the node where all four contribute."""
        result = CounterfactualAnalysis.derive_gap4_invisibility()
        assert result["union_contributor_count"] == 4

    def test_gap4_single_standard_view_has_one_contributor(self):
        """Restricted to one standard, no cross-domain question is posed."""
        result = CounterfactualAnalysis.derive_gap4_invisibility()
        assert result["contributors_in_any_single_standard_view"] == 1
        assert result["invisible_under_premise"] is True

    def test_gap4_premise_does_not_by_itself_select_g5(self):
        """The premise holds at most nodes, so it cannot be sold as selective.

        Guards against overstating the derivation: if this ever returns only G5,
        the claim in the docstring has changed and must be re-read.
        """
        satisfying = [
            g
            for g in ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
            if CounterfactualAnalysis.derive_gap4_invisibility(g)["invisible_under_premise"]
        ]
        assert "G5" in satisfying
        assert len(satisfying) > 1, (
            "The premise is being presented as selective. It is not."
        )
        for single_standard_goal in ("G3", "G7"):
            assert single_standard_goal not in satisfying

    def test_gap4_states_the_limit_of_what_it_shows(self):
        result = CounterfactualAnalysis.derive_gap4_invisibility()
        assert "does not single out" in result["what_this_does_not_show"]

    def test_gap3_boundary_goals_come_from_the_shared_map(self):
        """counterfactual.py must not keep its own copy of the gap-to-goal map."""
        from src.analysis.gaps import GAP_GOAL_MAP

        result = CounterfactualAnalysis.derive_gap3_invisibility()
        assert result["boundary_goals"] == GAP_GOAL_MAP["Gap-3"]

    def test_gap4_derivation_states_its_premise(self):
        """The premise is asserted, so it must be visible to a reader."""
        result = CounterfactualAnalysis.derive_gap4_invisibility()
        assert "asserted, not proved" in result["premise"]
        assert result["caveat"]

    def test_gap4_contrast_case_single_standard_goal(self):
        """G3 draws on one standard, so no combining question arises there.

        Without this contrast the Gap-4 derivation would be vacuous.
        """
        result = CounterfactualAnalysis.derive_gap4_invisibility(goal="G3")
        assert result["union_contributor_count"] == 1
        assert result["invisible_under_premise"] is False

    def test_report_marks_the_three_asserted_gaps(self):
        """Gap-1, Gap-2 and Gap-5 must not be presented as computed."""
        asserted = CounterfactualAnalysis.derivation_report()["asserted_not_computed"]
        assert {"Gap-1", "Gap-2", "Gap-5"} <= set(asserted)
        assert "relocate the assertion" in asserted["reason"]

    def test_derivation_agrees_with_the_published_integration_induced_set(self):
        """The two derived gaps are exactly the two the paper calls II."""
        report = CounterfactualAnalysis.derivation_report()
        derived_invisible = {
            gap_id
            for gap_id, r in report["derived"].items()
            if r.get("invisible_from_every_single_standard") or r.get("invisible_under_premise")
        }
        published = {g.gap_id for g in GapClassification().gaps if g.integration_induced}
        assert derived_invisible == published == {"Gap-3", "Gap-4"}


class TestGapSeverityScoring:
    """Validate the gap severity scoring system."""

    @pytest.fixture
    def gaps(self):
        return GapClassification()

    def test_all_gaps_have_severity_scores(self, gaps):
        """Every gap should have a computed severity score."""
        scores = gaps.severity_scores()
        assert len(scores) == 5

    def test_integration_induced_have_higher_severity(self, gaps):
        """Gap-3 and Gap-4 (integration-induced) should have critical
        or high severity because they are invisible from single standards."""
        scores = gaps.severity_scores()
        for s in scores:
            if s.get("integration_induced"):
                assert s["priority"] in ("CRITICAL", "HIGH"), (
                    f"{s['gap_id']} is integration-induced but only {s['priority']}"
                )

    def test_severity_scores_have_all_dimensions(self, gaps):
        """Each score should have all four scoring dimensions."""
        scores = gaps.severity_scores()
        for s in scores:
            assert "safety_impact" in s
            assert "exploitability" in s
            assert "detectability" in s
            assert "remediation_complexity" in s
            assert "overall_severity" in s
            assert "rationale" in s


class TestTraceabilityMatrix:
    """Validate the traceability matrix linking goals to claims/gaps."""

    @pytest.fixture
    def matrix(self):
        return TraceabilityMatrix()

    def test_nine_entries(self, matrix):
        """Should have one entry per goal."""
        assert len(matrix.entries) == 9

    def test_g5_has_inconsistencies(self, matrix):
        """G5 should have inconsistencies listed."""
        g5_entry = next(e for e in matrix.entries if e.goal_id == "G5")
        assert len(g5_entry.inconsistencies) > 0

    def test_g9_is_gap(self, matrix):
        """G9 should have gap status."""
        g9_entry = next(e for e in matrix.entries if e.goal_id == "G9")
        assert g9_entry.status == "gap"

    def test_summary_totals(self, matrix):
        """Summary should account for all 9 goals."""
        summary = matrix.get_summary()
        total = summary["covered"] + summary["partial"] + summary["gap"]
        assert total == 9


# ── Table-level validation ───────────────────────────────────────────


class TestTableConsistency:
    """Validate that Table 5 and Table 6 data are internally consistent."""

    def test_table5_inconsistency_ids_sequential(self):
        """I-1 through I-7 should be present."""
        cat = DecisionPointCatalogue()
        ids = [i.inconsistency_id for i in cat.inconsistencies]
        assert ids == [f"I-{n}" for n in range(1, 8)]

    def test_table6_gap_ids_sequential(self):
        """Gap-1 through Gap-5 should be present."""
        gaps = GapClassification()
        ids = [g.gap_id for g in gaps.gaps]
        assert ids == [f"Gap-{n}" for n in range(1, 6)]

    def test_coverage_matrix_all_standards(self):
        """Table 2: all five standards should appear."""
        registry = StandardsRegistry()
        matrix = registry.compute_coverage_matrix()
        assert len(matrix) == 5

    def test_goal_density_g5_is_most_dense(self):
        """Table 4: G5 should have the most contributing standards."""
        registry = StandardsRegistry()
        density = registry.compute_goal_density()
        g5_count = sum(1 for v in density["G5"].values() if v)
        for gid, stds in density.items():
            if gid != "G5":
                count = sum(1 for v in stds.values() if v)
                assert count <= g5_count, (
                    f"{gid} has {count} standards, G5 has {g5_count}"
                )

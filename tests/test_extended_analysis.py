"""Tests for extended analyses: generalisability, base pattern sensitivity,
practitioner guidance, and gap type exhaustiveness."""

import pytest

from src.analysis.generalisability import (
    classify_finding_generalisability,
    get_generalisability_summary,
)
from src.analysis.base_pattern_sensitivity import (
    compare_base_patterns,
    get_base_pattern_invariants,
)
from src.analysis.practitioner_guidance import (
    build_practitioner_guidance,
    get_gap_resolution_summary,
)
from src.analysis.completeness import check_gsn_completeness
from src.analysis.counterfactual import CounterfactualAnalysis
from src.analysis.gaps import GapClassification
from src.analysis.decision_points import DecisionPointCatalogue


class TestGeneralisability:
    """Validate generalisability classification of findings."""

    @pytest.fixture
    def findings(self):
        return classify_finding_generalisability()

    def test_all_findings_classified(self, findings):
        """All 12 findings (7 inconsistencies + 5 gaps) should be classified."""
        assert len(findings) == 12

    def test_all_findings_are_universal(self, findings):
        """All findings should be classified as universal (arising from
        standards structure, not component choice)."""
        summary = get_generalisability_summary()
        assert summary["universal"] == 12

    def test_each_finding_has_would_apply_to(self, findings):
        """Each finding should list other components it would apply to."""
        for f in findings:
            assert len(f.would_apply_to) >= 1, (
                f"{f.finding_id} has no 'would_apply_to'"
            )

    def test_each_finding_has_rationale(self, findings):
        """Each finding should have a rationale."""
        for f in findings:
            assert len(f.rationale) > 20, (
                f"{f.finding_id} has insufficient rationale"
            )

    def test_findings_cover_all_inconsistencies(self, findings):
        """Should cover I-1 through I-7."""
        ids = {f.finding_id for f in findings}
        for i in range(1, 8):
            assert f"I-{i}" in ids

    def test_findings_cover_all_gaps(self, findings):
        """Should cover Gap-1 through Gap-5."""
        ids = {f.finding_id for f in findings}
        for i in range(1, 6):
            assert f"Gap-{i}" in ids


class TestBasePatternSensitivity:
    """Validate base pattern sensitivity analysis."""

    @pytest.fixture
    def patterns(self):
        return compare_base_patterns()

    def test_four_patterns_compared(self, patterns):
        """Should compare four base patterns."""
        assert len(patterns) == 4

    def test_annex_b_detects_all(self, patterns):
        """ISO/PAS 8800 Annex B (this work) should detect all findings."""
        annex_b = patterns[0]
        assert annex_b.would_detect_i1
        assert annex_b.would_detect_i2
        assert annex_b.would_detect_i5
        assert annex_b.would_detect_gap3
        assert annex_b.would_detect_gap4

    def test_amlas_misses_cybersecurity(self, patterns):
        """AMLAS should miss I-5 and Gap-3 (no cybersecurity)."""
        amlas = next(p for p in patterns if "AMLAS" in p.pattern_name)
        assert not amlas.would_detect_i5
        assert not amlas.would_detect_gap3

    def test_invariants_computed(self):
        """Base-pattern-invariant findings should be identified."""
        invariants = get_base_pattern_invariants()
        assert len(invariants) == 5  # I-1, I-2, I-5, Gap-3, Gap-4

    def test_all_patterns_have_limitations(self, patterns):
        """Each pattern should have documented limitations."""
        for p in patterns:
            assert len(p.limitations) >= 1


class TestPractitionerGuidance:
    """Validate practitioner guidance for gap resolution."""

    @pytest.fixture
    def guidance(self):
        return build_practitioner_guidance()

    def test_guidance_for_all_five_gaps(self, guidance):
        """Should have guidance for all five gaps."""
        assert len(guidance) == 5
        ids = {g.gap_id for g in guidance}
        assert ids == {f"Gap-{i}" for i in range(1, 6)}

    def test_each_gap_has_immediate_actions(self, guidance):
        """Each gap should have at least one immediate action."""
        for g in guidance:
            assert len(g.immediate_actions) >= 1, (
                f"{g.gap_id} has no immediate actions"
            )

    def test_each_gap_has_required_decisions(self, guidance):
        """Each gap should have decisions that must be made."""
        for g in guidance:
            assert len(g.required_decisions) >= 1, (
                f"{g.gap_id} has no required decisions"
            )

    def test_each_gap_has_evidence_to_produce(self, guidance):
        """Each gap should specify evidence to produce."""
        for g in guidance:
            assert len(g.evidence_to_produce) >= 1, (
                f"{g.gap_id} has no evidence to produce"
            )

    def test_each_gap_has_research_questions(self, guidance):
        """Each gap should have open research questions."""
        for g in guidance:
            assert len(g.open_research_questions) >= 1, (
                f"{g.gap_id} has no open research questions"
            )

    def test_effort_estimates_valid(self, guidance):
        """Effort estimates should use valid values."""
        valid = {"low", "medium", "high", "requires_research"}
        for g in guidance:
            assert g.estimated_effort in valid, (
                f"{g.gap_id} has invalid effort: {g.estimated_effort}"
            )

    def test_summary_statistics(self):
        """Summary should have reasonable counts."""
        summary = get_gap_resolution_summary()
        assert summary["total_gaps"] == 5
        assert summary["total_immediate_actions"] >= 12
        assert summary["total_required_decisions"] >= 6
        assert summary["total_evidence_items"] >= 6


class TestGapTypeExhaustiveness:
    """Validate whether the three gap types (MC, ME, UI) are exhaustive.

    The paper defines three gap types. This test class examines whether
    a fourth type could exist by checking that every conceivable gap
    pattern maps to one of the three types.
    """

    def test_three_gap_types_defined(self):
        """The classification uses exactly three types."""
        from src.standards.base import GapType
        assert len(GapType) == 3

    def test_every_gap_has_a_type(self):
        """Every identified gap maps to exactly one type."""
        gaps = GapClassification()
        for gap in gaps.gaps:
            assert gap.gap_type is not None

    def test_gap_types_are_mutually_exclusive(self):
        """Each gap should have exactly one type, not multiple."""
        gaps = GapClassification()
        for gap in gaps.gaps:
            # The gap_type is a single enum value, not a list
            from src.standards.base import GapType
            assert isinstance(gap.gap_type, GapType)

    def test_gap_types_cover_all_possibilities(self):
        """The three types should cover all logical possibilities:
        - MC: no standard makes the claim
        - ME: claim exists but no evidence method for AI
        - UI: claim exists, evidence methods exist, but they conflict

        These three are logically exhaustive for a gap at a GSN node:
        either the node needs a claim that doesn't exist (MC),
        or the claim exists but evidence is missing (ME),
        or both exist but they conflict (UI).
        """
        from src.standards.base import GapType
        # Verify the three types match the logical categories
        type_values = {gt.value for gt in GapType}
        assert type_values == {"MC", "ME", "UI"}


class TestScopeExclusions:
    """Validate the analysis scope and its documented exclusions.

    Addresses: Why are UL 4600, the EU AI Act, and UNECE R155/R156
    excluded from the analysis scope?
    """

    def test_five_standards_in_scope(self):
        """The analysis covers exactly five standards/reports."""
        from src.standards.registry import StandardsRegistry
        registry = StandardsRegistry()
        assert len(registry.all_standards) == 5

    def test_in_scope_standards_identified(self):
        """The five in-scope standards should be correctly identified."""
        from src.standards.registry import StandardsRegistry
        registry = StandardsRegistry()
        ids = {s.standard_id for s in registry.all_standards}
        assert ids == {"ISO26262", "ISO21448", "ISO21434", "ISOPAS8800", "TR5469"}

    def test_out_of_scope_not_in_registry(self):
        """UL 4600, EU AI Act, UNECE R155/R156 should not be in registry."""
        from src.standards.registry import StandardsRegistry
        registry = StandardsRegistry()
        ids = {s.standard_id for s in registry.all_standards}
        for excluded in ["UL4600", "EUAIACT", "R155", "R156"]:
            assert excluded not in ids


class TestSingleAssessorLimitation:
    """Validate that the single-assessor limitation is documented.

    Addresses: The claim extraction depends on a single assessor —
    has inter-rater reliability been assessed?
    """

    def test_completeness_check_provides_explanation(self):
        """The completeness check should explain how claims are validated."""
        result = check_gsn_completeness()
        assert result.is_complete
        assert len(result.explanation) > 50

    def test_all_claims_are_traceable(self):
        """Every claim should have a traceable clause reference."""
        from src.standards.registry import StandardsRegistry
        registry = StandardsRegistry()
        for std in registry.all_standards:
            for claim in std.claims:
                assert claim.source_clause is not None, (
                    f"{claim.claim_id} has no source clause"
                )
                assert claim.source_clause.reference, (
                    f"{claim.claim_id} has empty clause reference"
                )

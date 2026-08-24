"""Keep TRACEABILITY.md honest.

The index is generated from the same objects it describes, so it cannot drift
from them by accident. What it can do is sit stale in the repository after
someone changes a goal, a finding or a clause. These tests catch that, and check
that the index actually says what it promises to say.
"""

from __future__ import annotations

import os

import pytest

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.results.traceability_index import OUTPUT_PATH, build_index
from src.standards.registry import StandardsRegistry


@pytest.fixture(scope="module")
def generated() -> str:
    return build_index()


@pytest.fixture(scope="module")
def committed() -> str:
    if not os.path.exists(OUTPUT_PATH):
        pytest.fail("TRACEABILITY.md is missing. Run: python -m src.results.traceability_index")
    with open(OUTPUT_PATH, encoding="utf-8") as handle:
        return handle.read()


class TestIndexIsCurrent:
    def test_committed_index_matches_the_generator(self, generated, committed):
        assert committed == generated, (
            "TRACEABILITY.md is stale. Regenerate it with "
            "`python -m src.results.traceability_index`."
        )

    def test_generation_is_deterministic(self, generated):
        assert build_index() == generated


class TestIndexCoversWhatItPromises:
    def test_every_standard_appears_with_its_edition(self, generated):
        for standard in StandardsRegistry().all_standards:
            assert standard.full_name in generated, f"{standard.standard_id} missing"

    def test_every_decision_point_appears_in_both_vocabularies(self, generated):
        for inc in DecisionPointCatalogue().inconsistencies:
            number = inc.inconsistency_id.split("-")[1]
            assert f"`{inc.inconsistency_id}`" in generated
            assert f"DP-{number}" in generated

    def test_every_finding_appears_in_both_vocabularies(self, generated):
        for gap in GapClassification().gaps:
            number = gap.gap_id.split("-")[1]
            assert f"`{gap.gap_id}`" in generated
            assert f"F-{number}" in generated

    def test_every_claim_appears_in_the_clause_index(self, generated):
        for standard in StandardsRegistry().all_standards:
            for claim in standard.claims:
                assert claim.claim_id in generated, f"{claim.claim_id} missing"

    def test_out_of_scope_claims_state_their_reason(self, generated):
        for standard in StandardsRegistry().all_standards:
            for claim in standard.claims:
                if claim.is_out_of_scope:
                    assert "outside the argument" in generated
                    assert claim.text in generated

    def test_the_three_provenance_kinds_are_defined(self, generated):
        for kind in ("**PAPER**", "**CLAUSE**", "**COMMAND**"):
            assert kind in generated

    def test_both_papers_are_named_by_path(self, generated):
        assert "paper/waise2026/" in generated
        assert "paper/safecomp2026-position/" in generated

    def test_position_paper_is_marked_as_having_no_code(self, generated):
        assert "No file in `src/` supports it" in generated

    def test_known_inconsistencies_are_listed(self, generated):
        for marker in ("DP-2", "193 tests", "PointPillars", "G8 and G9"):
            assert marker in generated, f"missing known inconsistency: {marker}"

    def test_regeneration_command_is_stated(self, generated):
        assert "python -m src.results.traceability_index" in generated

    def test_every_artefact_row_declares_a_provenance(self, generated):
        start = generated.index("## 7. Artefacts")
        end = generated.index("## 8. The position paper")
        section = generated[start:end]
        rows = [
            line
            for line in section.splitlines()
            if line.startswith("| `") and "---" not in line
        ]
        assert rows, "no artefact rows found"
        allowed = ("measured", "seeded", "hand-written", "generated", "argued")
        for row in rows:
            assert any(word in row for word in allowed), f"undeclared provenance: {row}"

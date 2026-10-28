"""The numbers page: generated, current, self-contained, every count from code.

``docs/numbers.html`` answers the first question a reader asks about the
papers: why four, nine, seven and five. A wrong number on that page would do
more harm than no page, so these tests rebuild it, fail if the committed copy
differs, and check each count against the code that produces it.
"""

from __future__ import annotations

import os
import re

import pytest

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.findings import GapClassification
from src.gsn.integrated_pattern import build_integrated_gsn
from src.standards.base import LifecyclePhase
from src.standards.registry import StandardsRegistry
from src.visualization.numbers_page import OUTPUT_PATH, build_html


@pytest.fixture(scope="module")
def html() -> str:
    return build_html()


def _card(html: str, anchor: str) -> str:
    match = re.search(rf'<section class="card" id="{anchor}">(.*?)</section>', html)
    assert match, f"no card with id {anchor}"
    return match.group(1)


def _number(card: str) -> int:
    return int(re.search(r'<p class="num">(\d+)</p>', card).group(1))


class TestGeneratedFileIsCurrent:
    def test_committed_copy_matches_a_rebuild(self, html):
        assert os.path.exists(OUTPUT_PATH), (
            "docs/numbers.html is missing. "
            "Run: python -m src.visualization.numbers_page"
        )
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            assert handle.read() == html, (
                "docs/numbers.html is stale. "
                "Run: python -m src.visualization.numbers_page"
            )

    def test_build_is_deterministic(self, html):
        assert build_html() == html


class TestSelfContained:
    def test_no_external_scripts_styles_or_fonts(self, html):
        assert "<script" not in html
        assert "<link" not in html
        assert "@import" not in html
        assert "url(" not in html

    def test_outbound_links_go_only_to_the_repository(self, html):
        urls = re.findall(r'href="(https?://[^"]+)"', html)
        assert urls
        for url in urls:
            assert url.startswith("https://github.com/milinpatel07/"), url

    def test_relative_links_resolve_inside_docs(self, html):
        directory = os.path.dirname(OUTPUT_PATH)
        for link in re.findall(r'href="([^"#][^"]*)"', html):
            if not link.startswith("http"):
                path = link.split("#")[0]
                assert os.path.exists(os.path.join(directory, path)), link

    def test_size_fits_the_conference_wifi_budget(self, html):
        assert len(html.encode("utf-8")) < 30_000


class TestCountsComeFromTheCode:
    def test_standards(self, html):
        assert _number(_card(html, "standards")) == len(
            StandardsRegistry().normative_standards
        )

    def test_claims(self, html):
        assert _number(_card(html, "claims")) == len(
            StandardsRegistry().get_all_claims()
        )

    def test_phases(self, html):
        assert _number(_card(html, "phases")) == len(LifecyclePhase)

    def test_goals_and_their_split(self, html):
        goals = build_integrated_gsn().get_goals()
        card = _card(html, "goals")
        assert _number(card) == len(goals)
        reformulated = [
            g for g in goals
            if any("reformulated" in ref for ref in g.clause_references)
        ]
        assert [g.element_id for g in reformulated] == ["G1"]
        retained = sum(g.origin == "retained" for g in goals) - len(reformulated)
        added = sum(g.origin == "new" for g in goals)
        undeveloped = sum(g.origin == "undeveloped" for g in goals)
        assert len(reformulated) + retained + added + undeveloped == len(goals)
        assert f"{len(reformulated)} reformulated" in card
        assert f"{retained} retained" in card
        assert f"{added} added:" in card
        assert f"{undeveloped} added, undeveloped" in card

    def test_evidence_kinds_at_g5(self, html):
        g5 = next(g for g in build_integrated_gsn().get_goals() if g.element_id == "G5")
        assert _number(_card(html, "evidence")) == len(g5.source_standards)

    def test_decision_points_and_their_types(self, html):
        catalogue = DecisionPointCatalogue().inconsistencies
        card = _card(html, "decision-points")
        assert _number(card) == len(catalogue)
        for kind in ("structural", "terminological", "methodological"):
            count = sum(dp.inconsistency_type.value == kind for dp in catalogue)
            assert f"{count} {kind}" in card

    def test_findings_and_their_categories(self, html):
        gaps = GapClassification().gaps
        card = _card(html, "findings")
        assert _number(card) == len(gaps)
        induced = sum(g.integration_induced for g in gaps)
        assert f"{induced} integration-induced" in card
        assert f"{len(gaps) - induced} open methodological problems" in card


class TestProvenance:
    def test_the_position_paper_card_says_no_code_computes_it(self, html):
        """The position paper is argued from clause text. Its card must not
        read as if the repository computed it."""
        assert "no code computes it" in _card(html, "missing-steps")

    def test_page_declares_generation_and_rebuild_command(self, html):
        assert "Generated page; do not edit by hand" in html
        assert "python -m src.visualization.numbers_page" in html

    def test_every_card_says_what_kind_of_number_it_is(self, html):
        cards = re.findall(r'<section class="card"', html)
        assert html.count("Scope choice, result, or encoding?") == len(cards) >= 8

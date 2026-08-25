"""The landing page: generated, current, self-contained, honest about counts.

``docs/index.html`` is what the poster's QR code resolves to. These tests
rebuild it and fail if the committed copy differs, and they hold it to the
constraints the authors set: no external resource, the four standard colours
from ``standard_colors.py``, every count taken from the code that produces it,
and a size that loads fast on conference wifi.
"""

from __future__ import annotations

import os
import re

import pytest

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.gsn.integrated_pattern import build_integrated_gsn
from src.visualization.landing_page import OUTPUT_PATH, build_html
from src.visualization.standard_colors import STANDARD_COLORS, STANDARD_LABELS


@pytest.fixture(scope="module")
def html() -> str:
    return build_html()


class TestGeneratedFileIsCurrent:
    def test_committed_copy_matches_a_rebuild(self, html):
        assert os.path.exists(OUTPUT_PATH), (
            "docs/index.html is missing. "
            "Run: python -m src.visualization.landing_page"
        )
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            committed = handle.read()
        assert committed == html, (
            "docs/index.html is stale. "
            "Run: python -m src.visualization.landing_page"
        )

    def test_build_is_deterministic(self, html):
        assert build_html() == html


class TestSelfContained:
    def test_no_external_scripts_styles_or_fonts(self, html):
        assert "<script" not in html
        assert "<link" not in html
        assert "@import" not in html
        assert "url(" not in html

    def test_the_only_outbound_links_are_the_repository(self, html):
        urls = re.findall(r'href="(https?://[^"]+)"', html)
        assert urls, "the page should link out to the repository"
        for url in urls:
            assert url.startswith("https://github.com/milinpatel07/"), url

    def test_size_fits_the_conference_wifi_budget(self, html):
        assert len(html.encode("utf-8")) < 30_000


class TestThreePanels:
    def test_exactly_three_panels(self, html):
        assert html.count('class="panel ') == 3

    def test_the_three_destinations_are_present(self, html):
        assert 'href="gsn_view.html"' in html
        assert "/TRACEABILITY.md" in html
        assert "/paper" in html

    def test_the_gsn_view_link_is_relative_so_pages_serves_it(self, html):
        """Pages serves from /docs; the view sits beside this file."""
        assert 'href="gsn_view.html"' in html
        assert "docs/gsn_view.html" not in html


class TestCountsComeFromTheCode:
    """No hand-authored number on the page."""

    def test_goal_decision_point_and_finding_counts_match_the_analysis(self, html):
        goals = len(build_integrated_gsn().get_goals())
        decision_points = len(DecisionPointCatalogue().inconsistencies)
        findings = len(GapClassification().gaps)
        assert f"All {goals} goals" in html
        assert f"{decision_points} decision points" in html
        assert f"{findings} findings" in html

    def test_standard_count_matches_the_palette(self, html):
        assert f"across {len(STANDARD_COLORS)} standards" in html


class TestPalette:
    def test_the_four_standard_colors_are_used(self, html):
        for standard, color in STANDARD_COLORS.items():
            assert color in html, f"{standard} colour {color} missing"

    def test_every_standard_is_named_beside_its_colour(self, html):
        for label in STANDARD_LABELS.values():
            assert label in html


class TestProvenance:
    def test_page_declares_generation_and_rebuild_command(self, html):
        assert "Generated page; do not edit by hand" in html
        assert "python -m src.visualization.landing_page" in html

    def test_page_points_at_reproduction_and_errata(self, html):
        assert "make reproduce" in html
        assert "/REPRODUCING.md" in html
        assert "/ERRATA.md" in html

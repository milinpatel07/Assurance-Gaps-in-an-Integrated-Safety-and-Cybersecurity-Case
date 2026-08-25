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

    def test_outbound_links_go_only_to_the_repository_or_the_doi(self, html):
        """Two destinations are legitimate: the repository, and the DOI
        resolver for the archived release. Anything else on a page a
        conference visitor opens would be a surprise."""
        allowed = ("https://github.com/milinpatel07/", "https://doi.org/10.5281/")
        urls = re.findall(r'href="(https?://[^"]+)"', html)
        assert urls, "the page should link out to the repository"
        for url in urls:
            assert url.startswith(allowed), url

    def test_size_fits_the_conference_wifi_budget(self, html):
        assert len(html.encode("utf-8")) < 30_000


class TestPanels:
    def test_exactly_four_panels(self, html):
        assert html.count('class="panel ') == 4

    def test_the_four_destinations_are_present(self, html):
        assert 'href="gsn_view.html"' in html
        assert 'href="seam.html"' in html
        assert "/TRACEABILITY.md" in html
        assert "/paper" in html

    def test_each_panel_carries_a_different_standard_colour(self, html):
        """One panel per standard colour, so no two panels read as a pair."""
        accents = re.findall(r'class="panel accent-([a-z-]+)"', html)
        assert len(accents) == len(set(accents)) == 4

    def test_the_seam_panel_says_it_is_a_synthesis(self, html):
        """The QR visitor must not read the seam as a paper claim."""
        assert "not a claim either paper makes" in html

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


class TestSiteNavigation:
    """GitHub Pages serves this site from a subpath, so a link starting with a
    slash resolves above the site root and breaks. Every page must also offer a
    way onward: a reader arriving from the poster should never have to reach for
    the browser's back button."""

    PAGES = ["index.html", "gsn_view.html", "seam.html"]

    def _page(self, name: str) -> str:
        path = os.path.join(os.path.dirname(OUTPUT_PATH), name)
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    @pytest.mark.parametrize("name", PAGES)
    def test_no_root_relative_links(self, name):
        links = re.findall(r'href="([^"]+)"', self._page(name))
        offenders = [link for link in links if link.startswith("/")]
        assert not offenders, (
            f"{name} has root-relative links {offenders}, which resolve above "
            "the Pages subpath and 404."
        )

    @pytest.mark.parametrize("name", PAGES)
    def test_every_relative_link_resolves(self, name):
        directory = os.path.dirname(OUTPUT_PATH)
        links = [
            link for link in re.findall(r'href="([^"]+)"', self._page(name))
            if not link.startswith(("http", "#"))
        ]
        for link in links:
            assert os.path.exists(os.path.join(directory, link)), (
                f"{name} links to {link}, which is not in docs/"
            )

    @pytest.mark.parametrize("name", PAGES)
    def test_no_page_is_a_dead_end(self, name):
        links = [
            link for link in re.findall(r'href="([^"]+)"', self._page(name))
            if not link.startswith(("http", "#"))
        ]
        assert links, f"{name} offers no way onward"


class TestArchive:
    def test_the_concept_doi_is_published_on_the_page(self, html):
        assert "10.5281/zenodo.22091825" in html

    def test_the_page_uses_the_concept_doi_not_a_version_doi(self, html):
        """The concept DOI tracks the latest version; a version DOI on a page
        that is rebuilt every release would go stale."""
        assert "10.5281/zenodo.22091826" not in html

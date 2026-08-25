"""The G5 playground: generated, current, self-contained, asserts no rule.

``docs/g5_playground.html`` lets a reader drag four acceptance lines and watch
the release verdict flip. These tests rebuild it and fail if the committed copy
differs, hold it to the offline constraint the other pages carry, check the four
legs are the ones the argument holds, and check it presents the verdict as the
reader's own rather than asserting the combination rule finding F-4 says is
missing.
"""

from __future__ import annotations

import os
import re

import pytest

pytest.importorskip("yaml")

from src.analysis.g5_evidence import g5_legs  # noqa: E402
from src.visualization.playground_page import OUTPUT_PATH, build_html  # noqa: E402
from src.visualization.standard_colors import STANDARD_COLORS, STANDARD_LABELS  # noqa: E402


@pytest.fixture(scope="module")
def html() -> str:
    return build_html()


class TestGeneratedFileIsCurrent:
    def test_committed_copy_matches_a_rebuild(self, html):
        assert os.path.exists(OUTPUT_PATH), (
            "docs/g5_playground.html is missing. "
            "Run: python -m src.visualization.playground_page"
        )
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            assert handle.read() == html, (
                "docs/g5_playground.html is stale. "
                "Run: python -m src.visualization.playground_page"
            )

    def test_build_is_deterministic(self, html):
        assert build_html() == html


class TestSelfContained:
    def test_no_fetched_external_resource(self, html):
        assert "<script src" not in html
        assert "<link" not in html
        assert "<img" not in html
        assert "@import" not in html
        assert "url(" not in html

    def test_it_carries_its_own_inline_script(self, html):
        """The interactivity is inline; it fetches nothing."""
        assert "<script>" in html

    def test_only_navigational_links_reach_the_network(self, html):
        stripped = re.sub(r'href="[^"]*"', "", html)
        assert "http://" not in stripped
        assert "https://" not in stripped

    def test_size_fits_the_conference_wifi_budget(self, html):
        assert len(html.encode("utf-8")) < 40_000

    def test_no_dialog_functions(self, html):
        for fn in ("alert(", "confirm(", "prompt("):
            assert fn not in html


class TestTheFourLegsComeFromTheArgument:
    def test_every_standard_appears_with_its_colour(self, html):
        for standard, colour in STANDARD_COLORS.items():
            assert STANDARD_LABELS[standard] in html
            assert colour in html

    def test_the_four_scales_are_the_g5_scales(self, html):
        for leg in g5_legs():
            assert leg.scale in html

    def test_all_four_legs_are_present(self, html):
        assert html.count('class="leg"') == 4


class TestItAssertsNoCombinationRule:
    def test_both_verdicts_are_reachable(self, html):
        """A page that only ever said RELEASE would hide that the verdict is the
        reader's. Both outcomes must be in the page."""
        assert "RELEASE" in html
        assert "HOLD" in html

    def test_it_says_the_lines_are_the_readers(self, html):
        assert "no clause" in html.lower()
        assert "F-4" in html

    def test_it_defines_no_rule(self, html):
        """The page must not present an authoritative way to combine the scales;
        that would assert the rule F-4 records as missing."""
        assert "none exists to define" in html
        for claim in ("the correct verdict", "the right answer", "how to combine them is"):
            assert claim not in html.lower()

    def test_it_has_a_live_verdict_and_a_reset(self, html):
        assert 'id="verdict"' in html
        assert 'id="reset"' in html


class TestSiteFit:
    def test_it_offers_a_way_onward(self, html):
        for target in ("index.html", "seam.html", "gsn_view.html"):
            assert f'href="{target}"' in html

    def test_no_root_relative_links(self, html):
        offenders = [link for link in re.findall(r'href="([^"]+)"', html) if link.startswith("/")]
        assert not offenders

    def test_viewport_is_set_for_phones(self, html):
        assert 'name="viewport"' in html

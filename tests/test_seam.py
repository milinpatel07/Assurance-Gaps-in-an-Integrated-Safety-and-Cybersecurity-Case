"""The seam: the synthesis must stay tied to what the papers state.

The seam page is the one artefact in this repository that says something
neither paper says. These tests hold it to the conditions that make that
admissible: it is labelled a synthesis, it carries what differs as well as what
is shared, its design-time side is read from the analysis rather than retyped,
and its figure asserts no combination rule.
"""

from __future__ import annotations

import os
import re

import pytest

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.seam import (
    design_time_point,
    operation_time_point,
    seam,
    what_differs,
)
from src.gsn.integrated_pattern import build_integrated_gsn
from src.visualization.seam_page import OUTPUT_PATH, build_html


@pytest.fixture(scope="module")
def html() -> str:
    return build_html()


class TestGeneratedFileIsCurrent:
    def test_committed_copy_matches_a_rebuild(self, html):
        assert os.path.exists(OUTPUT_PATH), "docs/seam.html is missing"
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            assert handle.read() == html, (
                "docs/seam.html is stale. "
                "Run: python -m src.visualization.seam_page"
            )

    def test_build_is_deterministic(self, html):
        assert build_html() == html


class TestTheSynthesisIsDeclared:
    """The page may not present the unification as a paper claim."""

    def test_page_says_neither_paper_states_it(self, html):
        assert "synthesis drawn in this repository" in html
        assert "Neither paper states it" in html

    def test_the_declaration_precedes_the_figure(self, html):
        assert html.index("synthesis drawn in this repository") < html.index("<svg")

    def test_page_records_what_differs_not_only_what_is_shared(self, html):
        assert "What is not the same" in html
        for item in what_differs():
            assert item in html, f"difference dropped from the page: {item}"

    def test_both_paper_sources_are_named(self, html):
        assert "paper/waise2026/camera-ready.tex" in html
        assert "paper/safecomp2026-position/camera-ready.tex" in html


class TestDesignTimeSideComesFromTheAnalysis:
    """Not retyped: if the analysis changes, this page changes with it."""

    def test_scales_are_the_four_g5_evidence_types(self):
        g5 = build_integrated_gsn().get_element("G5")
        labels = [s.label for s in design_time_point().scales]
        assert len(labels) == len(g5.supported_by) == 4

    def test_identifiers_track_the_catalogues(self):
        point = design_time_point()
        assert point.paper_identifiers == ["DP-2", "F-4"]
        assert DecisionPointCatalogue().get_by_id("I-2") is not None
        assert GapClassification().get_by_id("Gap-4") is not None

    def test_missing_rule_is_the_findings_own_description(self):
        f4 = GapClassification().get_by_id("Gap-4")
        assert design_time_point().missing_rule == " ".join(f4.description.split())

    def test_assignment_seam_uses_the_recorded_f3(self):
        f3 = GapClassification().get_by_id("Gap-3")
        assert seam()["assignment_seam"]["design_time"] == " ".join(
            f3.description.split()
        )


class TestTheFigureAssertsNoRule:
    def test_both_junctions_mark_the_absence(self, html):
        assert html.count("No clause combines them") == 2

    def test_the_absence_bar_is_dashed_at_both_junctions(self, html):
        svg = html[html.index("<svg"): html.index("</svg>")]
        assert svg.count('stroke-dasharray="6 4"') == 2

    def test_no_arrowhead_is_drawn_anywhere(self, html):
        """An arrow through the gap would assert the missing rule."""
        svg = html[html.index("<svg"): html.index("</svg>")]
        assert "marker-end" not in svg
        assert "<polygon" not in svg

    def test_operation_side_names_its_four_scales(self, html):
        for scale in operation_time_point().scales:
            assert scale.label in html

    def test_no_scale_is_painted_over_by_the_absence_bar(self, html):
        """SVG paints in document order and the bar is opaque, so a bar that
        overlaps a chip erases it. This hid the cybersecurity evidence at both
        junctions once already."""
        svg = html[html.index("<svg"): html.index("</svg>")]
        chips = [
            int(m.group(1))
            for m in re.finditer(r'<rect x="14" y="(\d+)" width="12"', svg)
        ]
        bars = [
            (int(m.group(1)), int(m.group(1)) + 30)
            for m in re.finditer(r'<rect x="14" y="(\d+)" width="352"', svg)
        ]
        assert len(chips) == 8, "expected four scales at each of two junctions"
        for top, bottom in bars:
            covered = [y for y in chips if top - 25 <= y <= bottom]
            assert not covered, (
                f"absence bar {top}-{bottom} covers chips at {covered}"
            )

    def test_every_scale_label_sits_above_its_junction_bar(self, html):
        """The four labels must be readable, not just present in the source."""
        svg = html[html.index("<svg"): html.index("</svg>")]
        labels = [
            int(m.group(1))
            for m in re.finditer(r'<text x="33" y="(\d+)" class="t-kind"', svg)
        ]
        bars = [
            int(m.group(1))
            for m in re.finditer(r'<rect x="14" y="(\d+)" width="352"', svg)
        ]
        assert len(labels) == 8
        for bar_top in bars:
            in_bar = [y for y in labels if bar_top <= y <= bar_top + 30]
            assert not in_bar, f"scale text at {in_bar} falls inside the bar"


class TestSelfContained:
    def test_no_external_resource(self, html):
        assert "<script" not in html
        assert "<link" not in html
        # The SVG namespace URI is an identifier, never fetched. Nothing else
        # on the page may reach the network.
        without_ns = html.replace('xmlns="http://www.w3.org/2000/svg"', "")
        assert "http://" not in without_ns
        assert "https://" not in without_ns

    def test_figure_is_inline_and_scales_to_the_viewport(self, html):
        assert re.search(r'<svg viewBox="0 0 380 \d+" width="100%"', html)

    def test_size_fits_the_conference_wifi_budget(self, html):
        assert len(html.encode("utf-8")) < 40_000

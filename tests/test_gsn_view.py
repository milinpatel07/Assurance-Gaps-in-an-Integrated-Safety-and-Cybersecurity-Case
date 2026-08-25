"""The interactive GSN view: generated, current, self-contained, complete.

``docs/gsn_view.html`` is a tracked generated file. These tests rebuild it and
fail if the committed copy differs, so it cannot drift from its two sources —
the same guard TRACEABILITY.md carries. They also hold the file to the
constraints the authors set: no external resource, every node present, the
palette from ``standard_colors.py`` and nowhere else, and a size that loads
fast on conference wifi.
"""

from __future__ import annotations

import os
import re

import pytest

pytest.importorskip("yaml")

from src.visualization.interactive_view import (  # noqa: E402
    OUTPUT_PATH,
    build_html,
)
from src.visualization.standard_colors import (  # noqa: E402
    PLACEHOLDERS_PENDING,
    STANDARD_COLORS,
    STANDARD_LABELS,
)

STRUCTURAL_NODES = [
    "G1", "C1", "C2", "S1", "A1.4",
    "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9",
]


@pytest.fixture(scope="module")
def html() -> str:
    return build_html()


class TestGeneratedFileIsCurrent:
    def test_committed_copy_matches_a_rebuild(self, html):
        assert os.path.exists(OUTPUT_PATH), (
            "docs/gsn_view.html is missing. "
            "Run: python -m src.visualization.interactive_view"
        )
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            committed = handle.read()
        assert committed == html, (
            "docs/gsn_view.html is stale. "
            "Run: python -m src.visualization.interactive_view"
        )

    def test_build_is_deterministic(self, html):
        assert build_html() == html


class TestSelfContained:
    """Offline, no CDN: the file references nothing outside itself."""

    def test_no_external_scripts_styles_or_fonts(self, html):
        assert "<script src" not in html
        assert "<link" not in html
        assert "@import" not in html
        assert "url(" not in html

    def test_no_network_urls(self, html):
        assert "http://" not in html
        assert "https://" not in html

    def test_size_fits_the_conference_wifi_budget(self, html):
        assert len(html.encode("utf-8")) < 100_000

    def test_no_dialog_functions(self, html):
        """alert/confirm/prompt block the page; the view must not use them."""
        for fn in ("alert(", "confirm(", "prompt("):
            assert fn not in html


class TestEveryNodeIsPresent:
    def test_all_structural_nodes_are_tappable(self, html):
        for node in STRUCTURAL_NODES:
            assert f'data-node="{node}"' in html, f"{node} has no button"

    def test_every_structural_node_has_a_panel(self, html):
        for node in STRUCTURAL_NODES:
            assert f'id="panel-{node}"' in html, f"{node} has no panel"

    def test_g5_panel_carries_the_four_evidence_types(self, html):
        for kind in (
            "deterministic coverage",
            "scenario coverage",
            "statistical metric",
            "attack success rate",
        ):
            assert kind in html, f"G5 evidence kind missing: {kind}"

    def test_g5_shows_no_combined_score(self, html):
        """The four scales are shown side by side and never combined. A total,
        overall or combined figure at G5 would assert a combination rule no
        standard defines (finding F-4)."""
        g5_panel = re.search(
            r'<template id="panel-G5">(.*?)</template>', html, re.DOTALL
        )
        assert g5_panel is not None
        for word in ("Total", "Overall score", "Combined score", "aggregate"):
            assert word not in g5_panel.group(1)

    def test_g9_panel_states_undeveloped_and_why(self, html):
        g9_panel = re.search(
            r'<template id="panel-G9">(.*?)</template>', html, re.DOTALL
        )
        assert g9_panel is not None
        text = g9_panel.group(1)
        assert "undeveloped" in text
        assert "F-2" in text and "Gap-2" in text
        assert "What existing standards cover, and where they stop" in text

    def test_g5_evidence_carries_the_papers_instantiation_status(self, html):
        """Figure 2(b): one leg provided (simulated), three not produced.
        Without these the cards read as evidence that exists."""
        assert html.count("not produced") == 3
        assert html.count("provided (simulated)") == 1

    def test_all_seven_decision_points_are_surfaced(self, html):
        for n in range(1, 8):
            assert f"DP-{n}" in html, f"decision point DP-{n} missing"

    def test_paper_identifiers_lead(self, html):
        assert "F-2 (Gap-2 in the code)" in html
        assert "DP-2 (I-2 in the code)" in html


class TestPalette:
    def test_the_four_standard_colors_are_used(self, html):
        for standard, color in STANDARD_COLORS.items():
            assert color in html, f"{standard} colour {color} not in the view"

    def test_every_standard_label_appears(self, html):
        for label in STANDARD_LABELS.values():
            assert label in html

    def test_deck_palette_has_been_entered(self):
        """Fails while the placeholder greys stand in for the talk deck's
        palette, so the placeholder state cannot reach a release unnoticed.
        Enter the deck's four values in standard_colors.py and flip
        PLACEHOLDERS_PENDING to False."""
        assert not PLACEHOLDERS_PENDING, (
            "standard_colors.py still carries placeholder greys. The talk "
            "deck's four hex values are the source of truth; enter them and "
            "set PLACEHOLDERS_PENDING = False."
        )

    def test_placeholder_banner_tracks_the_flag(self, html):
        banner_shown = "Colour placeholders" in html
        assert banner_shown == PLACEHOLDERS_PENDING


class TestProvenance:
    def test_footer_declares_generation_and_sources(self, html):
        assert "Generated file; do not edit by hand" in html
        assert "gsn/integrated_pattern.gsn.yaml" in html
        assert "src/gsn/integrated_pattern.py" in html
        assert "src/analysis/gaps.py" in html
        assert "src/analysis/decision_points.py" in html
        assert "src/visualization/standard_colors.py" in html
        assert "python -m src.visualization.interactive_view" in html

"""The interactive GSN view: generated, current, self-contained, complete.

``docs/argument.html`` is a tracked generated file. These tests rebuild it and
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

from src.visualization.argument_page import (  # noqa: E402
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
            "docs/argument.html is missing. "
            "Run: python -m src.visualization.argument_page"
        )
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            committed = handle.read()
        assert committed == html, (
            "docs/argument.html is stale. "
            "Run: python -m src.visualization.argument_page"
        )

    def test_build_is_deterministic(self, html):
        assert build_html() == html


class TestNoGeneratorCorruption:
    """The current-file guard compares the committed copy against a rebuild, so
    a generator that emits corrupted bytes still passes: the committed copy
    carries the same corruption. These tests read the bytes themselves.

    An earlier version wrote the two status marks as "\\25CB" and "\\25CF"
    inside a non-raw Python string. Python read \\25 as the octal escape for
    byte 0x15, and the phone view showed a control character followed by "CB"
    or "CF" in place of a circle.
    """

    def test_no_ascii_control_characters(self, html):
        allowed = {"\t", "\n", "\r"}
        stray = sorted(
            ch for ch in set(html) if (ord(ch) < 0x20 or ord(ch) == 0x7F) and ch not in allowed
        )
        assert not stray, (
            "generated HTML holds control characters "
            f"{[hex(ord(c)) for c in stray]}; a string escape was likely "
            "misread (for example \\25 as octal, not a CSS hex escape)"
        )

    def test_evidence_status_markers_render_as_circles(self, html):
        """Fig. 1(b) of the WAISE paper marks provided evidence with a filled
        circle and not-produced evidence with an open one."""
        assert "○" in html, "open circle (not produced) is missing"
        assert "●" in html, "filled circle (provided) is missing"


class TestSelfContained:
    """Offline, no CDN: the file references nothing outside itself."""

    def test_no_external_scripts_styles_or_fonts(self, html):
        # One script, inline; the deep-link support lives in it.
        assert html.count("<script") == 1 and "<script>" in html
        assert "<script src" not in html
        assert "<link" not in html
        assert "@import" not in html
        assert "url(" not in html
        assert "<img" not in html

    def test_only_navigational_links_reach_the_network(self, html):
        """Offline rendering: nothing is fetched to display the page. Footer
        hyperlinks (to the traceability index and errata) are navigation, not
        fetched resources, so they are allowed. Strip href values, then no
        network reference may remain."""
        stripped = re.sub(r'href="[^"]*"', "", html)
        assert "http://" not in stripped
        assert "https://" not in stripped

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
        # Every panel is also reachable by URL fragment (argument.html#G5):
        # the inline script reads the hash on load and on hashchange.
        script = re.search(r"<script>(.*?)</script>", html, re.DOTALL).group(1)
        assert "location.hash" in script
        assert "addEventListener('hashchange', openFromHash)" in script
        assert "openFromHash();\n})();" in script

    def test_g5_panel_carries_the_four_evidence_types(self, html):
        for kind in (
            "MC/DC coverage ratio",
            "triggering-condition coverage fraction",
            "AUROC of ensemble disagreement",
            "attack success rate",
        ):
            assert kind in html, f"G5 evidence type missing: {kind}"
        # At G5 the field names the measurement scale; elsewhere the artefact.
        panels = dict(re.findall(
            r'<template id="panel-([^"]+)">(.*?)</template>', html, re.DOTALL
        ))
        assert panels["G5"].count('class="kind">Scale:') == 4
        assert "Artefact:" not in panels["G5"]
        assert 'class="kind">Artefact:' in panels["G3"]
        assert "Evidence kind" not in html
        assert "evidence types</span>" not in html  # badges count items

    def test_g5_shows_no_combined_score(self, html):
        """The four scales are shown side by side and never combined. A total,
        overall or combined figure at G5 would assert a combination rule no
        standard prescribes (decision point DP-2)."""
        g5_panel = re.search(
            r'<template id="panel-G5">(.*?)</template>', html, re.DOTALL
        )
        assert g5_panel is not None
        for word in ("Total", "Overall score", "Combined score", "aggregate"):
            assert word not in g5_panel.group(1)
        # The paper keeps F-4 (cross-domain release decision, combined
        # residual risk) apart from DP-2 (how the G5 evidence types combine).
        # Where the view shows F-4 at G5, it says which is which.
        assert "F-4 (Gap-4 in the code)" in g5_panel.group(1)
        assert "combined residual risk" in g5_panel.group(1)
        assert "is decision point DP-2" in g5_panel.group(1)
        # No overstatement of the combination problem anywhere on the page.
        for phrase in ("do not combine", "incommensurable", "cannot be combined",
                       "kinds of evidence"):
            assert phrase not in html, phrase

    def test_g9_panel_states_undeveloped_and_why(self, html):
        g9_panel = re.search(
            r'<template id="panel-G9">(.*?)</template>', html, re.DOTALL
        )
        assert g9_panel is not None
        text = g9_panel.group(1)
        assert "undeveloped" in text
        assert "F-2" in text and "Gap-2" in text
        assert "What existing standards cover, and where they stop" in text
        assert "no single standard prescribes" in text
        # GSN's sense of undeveloped, not "a gap in the standards".
        assert (
            "Undeveloped goal (see F-2)"
            in html
        )
        assert "a gap in the standards" not in html

    def test_g5_evidence_carries_the_papers_instantiation_status(self, html):
        """Fig. 1(b) of the WAISE paper: one evidence type provided (simulated),
        three not produced. Without these the cards read as evidence that
        exists."""
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
        assert "src/analysis/findings.py" in html
        assert "src/analysis/decision_points.py" in html
        assert "src/visualization/standard_colors.py" in html
        assert "python -m src.visualization.argument_page" in html
        # Title, heading and navigation use the page names of the style sheet.
        name = "The integrated GSN argument, node by node"
        assert f"<title>{name}</title>" in html
        assert f"<h1>{name}</h1>" in html
        for href, page in (
            ("index.html", "Start page"),
            ("numbers.html", "Where the numbers come from"),
            ("design-time-and-operation.html", "Design time and operation: the two papers side by side"),
            ("g5-playground.html",
             "G5 playground: set acceptance lines for the four evidence types"),
        ):
            assert re.search(
                rf'<a href="{re.escape(href)}">{re.escape(page)}</a>', html
            ), page
        assert "\u2014" not in html, "no em dashes in reader-facing text"

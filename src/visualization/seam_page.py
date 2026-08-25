"""Build the seam page and its figure: one problem, two lifecycle points.

Writes ``docs/seam.html``, including an inline SVG figure generated from
``src/analysis/seam.py``. No node text and no identifier is hand-authored here;
the design-time side is read from the analysis catalogues and the built
argument, so the page cannot drift from the code.

The page states in its first paragraph that the unification is a synthesis
drawn in this repository and not a claim either paper makes, and it carries a
section on what differs between the two points, so a reader cannot mistake the
synthesis for an identity.

The figure shows the scales meeting at each junction and marks the missing
combination rule with a dashed bar, following the papers' own convention for
an absence. It draws no arrow through that bar, because drawing one would
assert the very rule both papers report as missing.

Usage:
    python -m src.visualization.seam_page          # write docs/seam.html
    python -m src.visualization.seam_page --check  # exit 1 if out of date
"""

from __future__ import annotations

import argparse
import html
import os
import sys

from src.analysis.seam import PAPER_POSITION, PAPER_WAISE, seam
from src.visualization.standard_colors import GAP_GREY, STANDARD_COLORS, STANDARD_LABELS

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
OUTPUT_PATH = os.path.join(REPO_ROOT, "docs", "seam.html")
REBUILD_COMMAND = "python -m src.visualization.seam_page"

# The traceability index and errata live at the repository root, outside the
# docs/ tree GitHub Pages serves, so they are reachable only by absolute URL.
# These are navigation links, not fetched resources; the page renders offline.
BLOB_URL = (
    "https://github.com/milinpatel07/"
    "Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/blob/main"
)


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _colour(standard: str | None) -> str:
    return STANDARD_COLORS.get(standard, GAP_GREY) if standard else GAP_GREY


def _standard_label(standard: str | None) -> str:
    return STANDARD_LABELS.get(standard, "no single standard named")


# ── Figure ─────────────────────────────────────────────────────────────

def _junction_svg(point, top: int) -> list[str]:
    """One lifecycle point: a heading, four scale chips, a dashed absence bar."""
    parts = [
        f'<text x="14" y="{top}" class="t-lifecycle">{_esc(point.lifecycle)}</text>',
        f'<text x="14" y="{top + 17}" class="t-where">{_esc(point.where)}</text>',
    ]
    # One chip is a 12px swatch, a label line and a scale line: 36px of pitch.
    # The absence bar below has to clear the last of them, so the pitch is
    # written once here and reused to place the bar. An earlier version
    # advanced the chips by 36 and placed the bar as though the pitch were 24,
    # which painted the bar over the fourth chip at both junctions and hid the
    # cybersecurity evidence in a figure about four scales meeting.
    chip_pitch = 36
    chip_top = top + 30
    for index, scale in enumerate(point.scales):
        y = chip_top + index * chip_pitch
        colour = _colour(scale.standard)
        parts.append(
            f'<rect x="14" y="{y}" width="12" height="12" rx="2" fill="{colour}" '
            'stroke="#111" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="33" y="{y + 10}" class="t-scale">{_esc(scale.label)}</text>'
        )
        parts.append(
            f'<text x="33" y="{y + 21}" class="t-kind">scale: {_esc(scale.kind)}</text>'
        )
    last_chip_bottom = chip_top + (len(point.scales) - 1) * chip_pitch + 25
    bar_y = last_chip_bottom + 10
    parts.append(
        f'<rect x="14" y="{bar_y}" width="352" height="30" rx="4" fill="#f5f5f5" '
        'stroke="#757575" stroke-width="2" stroke-dasharray="6 4"/>'
    )
    parts.append(
        f'<text x="190" y="{bar_y + 19}" class="t-gap" text-anchor="middle">'
        "No clause combines them</text>"
    )
    return parts, bar_y + 30


def _figure_svg() -> str:
    data = seam()
    design, operation = data["points"]

    body: list[str] = []
    design_parts, design_end = _junction_svg(design, 24)
    body += design_parts

    link_y = design_end + 18
    body.append(
        f'<line x1="190" y1="{design_end + 4}" x2="190" y2="{link_y + 16}" '
        'stroke="#111" stroke-width="2" stroke-dasharray="3 3"/>'
    )
    body.append(
        f'<text x="190" y="{link_y + 34}" class="t-link" text-anchor="middle">'
        "Same structure, different lifecycle point</text>"
    )

    op_parts, op_end = _junction_svg(operation, link_y + 62)
    body += op_parts

    height = op_end + 14
    return (
        f'<svg viewBox="0 0 380 {height}" width="100%" height="auto" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="The same missing combination rule at two lifecycle points: '
        'the design-time release decision and the operation-time re-evaluation.">'
        "<style>"
        ".t-lifecycle{font:700 15px system-ui,sans-serif;fill:#111}"
        ".t-where{font:12px system-ui,sans-serif;fill:#444}"
        ".t-scale{font:12px system-ui,sans-serif;fill:#111}"
        ".t-kind{font:11px system-ui,sans-serif;fill:#555}"
        ".t-gap{font:700 12px system-ui,sans-serif;fill:#333}"
        ".t-link{font:italic 12px system-ui,sans-serif;fill:#333}"
        "</style>"
        + "".join(body)
        + "</svg>"
    )


# ── Page ───────────────────────────────────────────────────────────────

def _point_section(point) -> str:
    chips = "".join(
        f'<li><span class="dot" style="--c:{_colour(s.standard)}"></span>'
        f"<strong>{_esc(s.label)}</strong><br>"
        f'<span class="kind">Scale: {_esc(s.kind)}. '
        f"Source: {_esc(_standard_label(s.standard))}.</span></li>"
        for s in point.scales
    )
    extra = ""
    if point.extra_conditions:
        items = "".join(f"<li>{_esc(c)}</li>" for c in point.extra_conditions)
        extra = f"<p>Operation also adds:</p><ul class='plain'>{items}</ul>"
    return (
        '<section class="point">'
        f"<h2>{_esc(point.lifecycle)}: {_esc(point.where)}</h2>"
        f'<p class="question">{_esc(point.question)}</p>'
        f'<ul class="scales">{chips}</ul>'
        f'<p class="missing">{_esc(point.missing_rule)}.</p>'
        + extra
        + f'<p class="src">{_esc(point.source_note)} '
        f"Source file: <code>{_esc(point.paper)}</code></p>"
        "</section>"
    )


CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; background: #fff; color: #111;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 16px; line-height: 1.5;
}
header, main, footer { max-width: 720px; margin: 0 auto; padding: 0 16px; }
header { padding-top: 22px; }
h1 { font-size: 1.4rem; line-height: 1.25; margin: 0 0 10px; }
h2 { font-size: 1.1rem; margin: 0 0 6px; }
h3 { font-size: 1rem; margin: 18px 0 6px; }
.synthesis {
  border: 2px solid #111; border-radius: 8px; padding: 10px 12px;
  margin: 12px 0; background: #fafafa;
}
figure { margin: 18px 0; }
figcaption { font-size: 0.85rem; color: #444; margin-top: 6px; }
.point {
  border: 2px solid #222; border-radius: 8px; padding: 12px 14px; margin: 14px 0;
}
.question { font-style: italic; margin: 0 0 10px; }
ul.scales { list-style: none; margin: 0 0 10px; padding: 0; }
ul.scales li { margin-bottom: 8px; }
ul.plain { margin: 4px 0 10px; padding-left: 20px; }
.dot {
  display: inline-block; width: 12px; height: 12px; border-radius: 3px;
  background: var(--c); border: 1px solid #111; margin-right: 6px;
  vertical-align: -1px;
}
.kind { font-size: 0.85rem; color: #555; }
.missing {
  border: 2px dashed #757575; background: #f5f5f5;
  padding: 8px 10px; font-weight: 600; margin: 10px 0;
}
.src { font-size: 0.85rem; color: #444; margin: 8px 0 0; }
code {
  background: #f2f2f2; border: 1px solid #ddd; border-radius: 4px;
  padding: 1px 5px; font-size: 0.85rem;
}
footer {
  border-top: 1px solid #ccc; margin-top: 22px; padding-top: 12px;
  padding-bottom: 28px; font-size: 0.85rem; color: #333;
}
a { color: #111; }
"""


def build_html() -> str:
    data = seam()
    shared = "".join(f"<li>{_esc(item)}</li>" for item in data["shared"])
    differs = "".join(f"<li>{_esc(item)}</li>" for item in data["differs"])
    assignment = data["assignment_seam"]

    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>One problem at two lifecycle points</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n"
        "<header>\n"
        "<h1>One problem at two lifecycle points</h1>\n"
        '<div class="synthesis">'
        "<p><strong>What this page is.</strong> Each paper reports, "
        "separately, that evidence from several concerns has to support one "
        "claim on scales that do not convert into one another, and that no "
        "clause says how to combine it. One paper reports it before release, "
        "the other during service. Putting the two together is a synthesis "
        "drawn in this repository. Neither paper states it, and this page is "
        "not evidence for it beyond what each paper already says.</p>"
        "</div>\n"
        "</header>\n<main>\n"
        "<figure>"
        + _figure_svg()
        + "<figcaption>The same junction at two points in the lifecycle, set "
        "side by side by this repository rather than by either paper. Each "
        "paper reports its own end. The dashed bar marks the missing rule, "
        "following the papers' own convention for an absence. This figure "
        "draws nothing through that bar, because an arrow there would assert "
        "the rule both papers report as missing. MC/DC is modified "
        "condition/decision coverage. The figure's data comes from "
        "<code>src/analysis/seam.py</code>; the page is built by "
        "<code>src.visualization.seam_page</code>, the rebuild command in the "
        "footer.</figcaption></figure>\n"
        + _point_section(data["points"][0])
        + _point_section(data["points"][1])
        + f"<h3>What is the same at both points</h3><ul>{shared}</ul>"
        + f"<h3>What is not the same</h3><ul>{differs}</ul>"
        + "<h3>The same boundary, one step earlier</h3>"
        + "<p>Before the combination question can arise, the anomaly has to "
        "belong to a concern. Each paper reports a case that falls between "
        "concerns at that earlier step. Reading the two as one boundary is a "
        "second synthesis drawn here, and a looser one than the first: the "
        "two cases differ, as the note below says. SOTIF is safety of the "
        "intended functionality.</p>"
        + f"<p><strong>{_esc(assignment['design_time_identifier'])}, design "
        f"time.</strong> {_esc(assignment['design_time'])}.</p>"
        + f"<p><strong>{_esc(assignment['operation_time_identifier'])}, "
        f"operation time.</strong> {_esc(assignment['operation_time'])}.</p>"
        + f"<p>{_esc(assignment['note'])}</p>"
        + "</main>\n<footer>\n"
        "<p>Generated page; do not edit by hand. The design-time side is read "
        "from the analysis catalogues and the built argument; the "
        "operation-time side is transcribed from the position paper, which no "
        "code backs by design. Sources: "
        f"<code>{_esc(PAPER_WAISE)}</code> and "
        f"<code>{_esc(PAPER_POSITION)}</code>. "
        f"Rebuild: <code>{REBUILD_COMMAND}</code></p>\n"
        "<p>Every design-time identifier here is traced in "
        f'<a href="{BLOB_URL}/TRACEABILITY.md">TRACEABILITY.md</a>, and what '
        "this work found about the papers is in "
        f'<a href="{BLOB_URL}/ERRATA.md">ERRATA.md</a>.</p>\n'
        '<p><a href="index.html">Back to the start</a> · '
        '<a href="gsn_view.html">The argument, one node at a time</a> · '
        '<a href="g5_playground.html">Try to combine the four scales</a></p>\n'
        "</footer>\n</body>\n</html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="exit 1 if docs/seam.html is out of date",
    )
    args = parser.parse_args(argv)

    content = build_html()
    if args.check:
        try:
            with open(OUTPUT_PATH, encoding="utf-8") as handle:
                current = handle.read()
        except FileNotFoundError:
            print(f"MISSING: {OUTPUT_PATH}. Run: {REBUILD_COMMAND}")
            return 1
        if current != content:
            print(f"STALE: {OUTPUT_PATH}. Run: {REBUILD_COMMAND}")
            return 1
        print(f"OK: {OUTPUT_PATH} is current.")
        return 0

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    print(f"Wrote {OUTPUT_PATH} ({len(content)} bytes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

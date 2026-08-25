"""Build the landing page: what the poster's QR code resolves to.

Writes ``docs/index.html``, the root of the GitHub Pages site. A visitor
arriving from the poster has a phone, daylight, and under a minute, so the page
carries four panels and nothing else: the interactive argument, the seam
between the two papers, the traceability index, and the papers themselves. One
panel per standard colour, in the paper's legend order.

Generated, never edited by hand. ``tests/test_landing_page.py`` rebuilds it and
fails if the committed copy differs. Every count on the page comes from the code
that produces it, so no number here can drift from the analysis.

Pages serves from ``/docs``, so files inside ``docs/`` are linked relatively and
anything outside it is linked to the repository on GitHub.

Usage:
    python -m src.visualization.landing_page          # write docs/index.html
    python -m src.visualization.landing_page --check  # exit 1 if out of date
"""

from __future__ import annotations

import argparse
import html
import os
import sys

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.gsn.integrated_pattern import build_integrated_gsn
from src.visualization.standard_colors import STANDARD_COLORS, STANDARD_LABELS

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
OUTPUT_PATH = os.path.join(REPO_ROOT, "docs", "index.html")

REBUILD_COMMAND = "python -m src.visualization.landing_page"

REPO_URL = (
    "https://github.com/milinpatel07/"
    "Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case"
)
BLOB = f"{REPO_URL}/blob/main"

# The concept DOI, which always resolves to the latest archived version. The
# version DOI for a specific release lives in CITATION.cff.
CONCEPT_DOI = "10.5281/zenodo.22091825"

# Legend order follows the paper's Figure 2(a).
LEGEND_ORDER = ["ISOPAS8800", "ISO21448", "ISO21434", "ISO26262"]


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _counts() -> dict[str, int]:
    """Every number on the page, from the code that produces it."""
    gsn = build_integrated_gsn()
    return {
        "goals": len(gsn.get_goals()),
        "decision_points": len(DecisionPointCatalogue().inconsistencies),
        "findings": len(GapClassification().gaps),
        "standards": len(STANDARD_COLORS),
    }


def _standards_strip() -> str:
    chips = "".join(
        f'<span class="chip" style="--c:{STANDARD_COLORS[s]}">'
        f"{_esc(STANDARD_LABELS[s])}</span>"
        for s in LEGEND_ORDER
    )
    return f'<p class="chips">{chips}</p>'


def _panels(counts: dict[str, int]) -> str:
    panels = [
        {
            "href": "gsn_view.html",
            "kicker": "Explore",
            "title": "The argument, one node at a time",
            "body": (
                f"All {counts['goals']} goals, with the standards behind each, "
                "the evidence it calls for, and the points where the standards "
                "leave a gap. Built for a phone."
            ),
            "cta": "Open the argument",
            "accent": "four",
        },
        {
            "href": "seam.html",
            "kicker": "Connect",
            "title": "One problem at two lifecycle points",
            "body": (
                "Each paper reports the same junction: evidence on scales that "
                "do not convert, and no clause combining them. One before "
                "release, one in service. A synthesis drawn here, not a claim "
                "either paper makes."
            ),
            "cta": "See the connection",
            "accent": "seam",
        },
        {
            "href": f"{BLOB}/TRACEABILITY.md",
            "kicker": "Check",
            "title": "Where every claim comes from",
            "body": (
                "One index. Every number, table and figure traces to a passage "
                "in a paper, a clause in a named standard edition, or a command "
                "that regenerates it."
            ),
            "cta": "Open the index",
            "accent": "trace",
        },
        {
            "href": f"{BLOB}/paper",
            "kicker": "Read",
            "title": "The two papers",
            "body": (
                f"The design-time paper catalogues {counts['decision_points']} "
                f"decision points and {counts['findings']} findings across "
                f"{counts['standards']} standards. The position paper asks who "
                "owns an alarm once the vehicle is in service."
            ),
            "cta": "Open the camera-ready sources",
            "accent": "papers",
        },
    ]
    out = []
    for panel in panels:
        out.append(
            f'<a class="panel accent-{panel["accent"]}" href="{panel["href"]}">'
            f'<span class="kicker">{_esc(panel["kicker"])}</span>'
            f'<h2>{_esc(panel["title"])}</h2>'
            f'<p>{_esc(panel["body"])}</p>'
            f'<span class="cta">{_esc(panel["cta"])}</span>'
            "</a>"
        )
    return '<main class="panels">' + "".join(out) + "</main>"


CSS = """
:root {
  color-scheme: light;
  --c8800: %(ISOPAS8800)s;
  --c21448: %(ISO21448)s;
  --c21434: %(ISO21434)s;
  --c26262: %(ISO26262)s;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: #fff; color: #111;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 16px; line-height: 1.5;
}
header, .panels, footer { max-width: 720px; margin: 0 auto; padding: 0 16px; }
header { padding-top: 24px; }
h1 { font-size: 1.5rem; line-height: 1.25; margin: 0 0 8px; }
.byline { color: #333; margin: 0 0 12px; }
.lede { margin: 0 0 4px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0 4px; padding: 0; }
.chip {
  display: inline-block; padding: 3px 10px; border-radius: 999px;
  border: 2px solid var(--c); background: #fff; color: #111;
  font-size: 0.85rem; white-space: nowrap;
}
.chip::before {
  content: ""; display: inline-block; width: 10px; height: 10px;
  border-radius: 50%%; background: var(--c); margin-right: 6px;
}
.panels { display: grid; gap: 14px; margin: 20px auto 8px; }
.panel {
  display: block; border: 2px solid #222; border-radius: 10px;
  padding: 14px 16px; text-decoration: none; color: inherit;
  border-top-width: 8px;
}
.panel:focus-visible { outline: 3px solid #111; outline-offset: 3px; }
.accent-four { border-top-color: var(--c8800); }
.accent-seam { border-top-color: var(--c21448); }
.accent-trace { border-top-color: var(--c21434); }
.accent-papers { border-top-color: var(--c26262); }
.kicker {
  font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em;
  color: #444; font-weight: 700;
}
.panel h2 { font-size: 1.15rem; margin: 4px 0 6px; }
.panel p { margin: 0 0 10px; }
.cta { font-weight: 700; text-decoration: underline; }
footer {
  border-top: 1px solid #ccc; margin-top: 20px; padding-top: 14px;
  padding-bottom: 28px; font-size: 0.9rem; color: #333;
}
footer code {
  display: inline-block; background: #f2f2f2; border: 1px solid #ddd;
  border-radius: 4px; padding: 1px 6px; font-size: 0.85rem;
}
footer a { color: #111; }
@media (min-width: 620px) { .panels { grid-template-columns: 1fr 1fr; }
  .panel:first-child { grid-column: 1 / -1; } }
"""


def build_html() -> str:
    counts = _counts()
    css = CSS % STANDARD_COLORS
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Assurance gaps in an integrated safety and cybersecurity "
        "case</title>\n"
        '<meta name="description" content="Supplementary material for two '
        'SAFECOMP 2026 papers on integrating four standards into one assurance '
        'argument for AI-based perception.">\n'
        f"<style>{css}</style>\n</head>\n<body>\n"
        "<header>\n"
        "<h1>Assurance gaps in an integrated safety and cybersecurity case</h1>\n"
        '<p class="byline">Milin Patel and Rolf Jung, Kempten University of '
        "Applied Sciences. Two SAFECOMP 2026 papers, both accepted.</p>\n"
        '<p class="lede">Four standards apply at once to an AI perception '
        "component in a driverless vehicle, and each one prescribes its own "
        "evidence. These papers build the single argument the four jointly "
        "imply, then report what the combination exposes.</p>\n"
        + _standards_strip()
        + "</header>\n"
        + _panels(counts)
        + "<footer>\n"
        '<p>Play with it: <a href="g5_playground.html">drag the four V&amp;V '
        "scales and watch the release decision flip</a>, and see that no "
        "standard sets the lines.</p>\n"
        "<p>Reproduce every artefact both papers use, and fail if anything "
        f"drifted: <code>make reproduce</code>. See <a href=\"{BLOB}/"
        'REPRODUCING.md">REPRODUCING.md</a>, and '
        f'<a href="{BLOB}/ERRATA.md">ERRATA.md</a> for what this work found '
        "about the camera-ready papers.</p>\n"
        f'<p>Source: <a href="{REPO_URL}">github.com/milinpatel07</a>. '
        f'Cite the papers: <a href="{BLOB}/CITATION.cff">CITATION.cff</a>. '
        f'Archived: <a href="https://doi.org/{CONCEPT_DOI}">{CONCEPT_DOI}</a>. '
        "MIT licence.</p>\n"
        f"<p>Generated page; do not edit by hand. Rebuild: "
        f"<code>{REBUILD_COMMAND}</code></p>\n"
        "</footer>\n</body>\n</html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="exit 1 if docs/index.html is out of date",
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

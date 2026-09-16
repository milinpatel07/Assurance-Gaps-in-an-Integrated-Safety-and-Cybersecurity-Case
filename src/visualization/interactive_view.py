"""Build the interactive GSN view: one self-contained HTML file.

The file this writes, ``docs/gsn_view.html``, is the tap-to-explore version of
the integrated argument for a reader arriving from the poster on a phone. It is
generated, never edited by hand, and ``tests/test_gsn_view.py`` rebuilds it and
fails if the committed copy differs.

Generated sources, joined by node id, no hand-authored node data:

  * ``gsn/integrated_pattern.gsn.yaml`` — the argument structure and the short
    button text a poster reader sees. The YAML's solution ids are the
    builder's ids by the authors' decision, so the join is exact.
  * ``build_integrated_gsn()`` — the panel body text, clause references,
    evidence descriptions, instantiation status and recorded notes that the
    YAML deliberately omits to stay legible at poster size.
  * ``src/analysis/gaps.py`` — the findings shown at their goals.
  * ``src/analysis/decision_points.py`` — the decision points shown at their
    goals.
  * ``standard_colors.py`` — every colour.

``tests/test_gsn_yaml_builder_consistency.py`` fails if the YAML and the
builder disagree; this module trusts that and does not re-check them.

Display rules, decided by the authors:

  * Goal-level standard attribution follows the YAML (the paper's Table 2
    view): a goal's chips are the standards its own evidence cites. G8 shows
    ISO/SAE 21434 only; the ISO 26262 bridge appears at the bridge solution,
    where the builder records it. G1 and G9 carry no chip row: G1's standards
    enter through its contexts and strategy, G9 is undeveloped.
  * Paper identifiers lead, code identifiers follow: "F-2 (Gap-2 in the
    code)", "DP-2 (I-2 in the code)".
  * At G5 the four evidence types are shown together without a combined
    score, total, or shared axis: the point is that the scales do not
    combine. Each carries the instantiation status the paper's Figure 2(b)
    states: one provided (simulated), three not produced.
  * Colours come from ``standard_colors.py`` and nowhere else.

Output is byte-deterministic: no timestamp, fixed ordering throughout.

Usage:
    python -m src.visualization.interactive_view          # write docs/gsn_view.html
    python -m src.visualization.interactive_view --check  # exit 1 if out of date
"""

from __future__ import annotations

import argparse
import html
import os
import sys

import yaml

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GAP_GOAL_MAP, GapClassification
from src.gsn.integrated_pattern import build_integrated_gsn
from src.visualization.standard_colors import (
    GAP_GREY,
    PLACEHOLDERS_PENDING,
    STANDARD_COLORS,
    STANDARD_LABELS,
)

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
YAML_PATH = os.path.join(REPO_ROOT, "gsn", "integrated_pattern.gsn.yaml")
OUTPUT_PATH = os.path.join(REPO_ROOT, "docs", "gsn_view.html")

REBUILD_COMMAND = "python -m src.visualization.interactive_view"

# The traceability index and errata live at the repository root, outside the
# docs/ tree GitHub Pages serves, so they are reachable only by absolute URL.
# These are navigation links, not fetched resources; the page renders offline.
BLOB_URL = (
    "https://github.com/milinpatel07/"
    "Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/blob/main"
)

NORMATIVE = set(STANDARD_COLORS)

GAPS = GapClassification()
CATALOGUE = DecisionPointCatalogue()

# Legend order follows the paper's Figure 2(a) legend.
LEGEND_ORDER = ["ISOPAS8800", "ISO21448", "ISO21434", "ISO26262"]

# The paper's Figure 2(b) letters its G5 evidence legs (a) to (d); the
# builder's supported_by order matches.
G5_LEG_LETTERS = ["(a)", "(b)", "(c)", "(d)"]

# Goals whose chip row is intentionally absent (see module docstring).
NO_CHIP_ROW = {"G1", "G9"}


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _load_yaml() -> dict:
    with open(YAML_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _standards_in_text(text: str) -> set[str]:
    tokens = {"26262": "ISO26262", "21448": "ISO21448",
              "21434": "ISO21434", "8800": "ISOPAS8800"}
    return {sid for tok, sid in tokens.items() if tok in text}


def _yaml_goal_standards(nodes: dict, goal_id: str) -> list[str]:
    """A goal's standards as its own YAML evidence cites them (Table 2 view)."""
    stds: set[str] = set()
    for child in nodes[goal_id].get("supportedBy", []) or []:
        if child.startswith("Sn"):
            stds |= _standards_in_text(nodes[child].get("text", ""))
    return sorted(stds)


def _chip(standard_id: str) -> str:
    return (
        f'<span class="chip" style="--c:{STANDARD_COLORS[standard_id]}">'
        f"{_esc(STANDARD_LABELS[standard_id])}</span>"
    )


def _chip_row(standard_ids: list[str]) -> str:
    if not standard_ids:
        return ""
    return '<p class="chips">' + "".join(_chip(s) for s in standard_ids) + "</p>"


def _paper_name(code_id: str) -> str:
    """Gap-N -> F-N, I-N -> DP-N; the numbers correspond exactly."""
    if code_id.startswith("Gap-"):
        return f"F-{code_id.split('-')[1]} ({code_id} in the code)"
    if code_id.startswith("I-"):
        return f"DP-{code_id.split('-')[1]} ({code_id} in the code)"
    return code_id


def _clause_list(refs: list[str]) -> str:
    if not refs:
        return ""
    items = "".join(f"<li>{_esc(r)}</li>" for r in refs)
    return f"<h3>Clause references</h3><ul class='clauses'>{items}</ul>"


def _evidence_cards(gsn, solution_ids: list[str], grid: bool) -> str:
    """Evidence entries, from the builder, in the goal's declared order.

    These are the kinds of evidence the argument calls for, not claims that
    the evidence exists. Where the paper states whether the case study
    produced a leg (Figure 2(b) at G5), the card carries that status.
    """
    cards = []
    for index, sid in enumerate(solution_ids):
        sol = gsn.get_element(sid)
        stds = sorted(s for s in (sol.source_standards or []) if s in NORMATIVE)
        kind = _esc(sol.evidence_type.replace("_", " "))
        letter = f"{G5_LEG_LETTERS[index]} " if grid else ""
        status = ""
        if sol.instantiation:
            css_status = (
                "status-provided"
                if sol.instantiation.startswith("provided")
                else "status-missing"
            )
            status = (
                f'<p class="status {css_status}">Case study: '
                f"{_esc(sol.instantiation)}</p>"
            )
        cards.append(
            '<div class="evidence">'
            + _chip_row(stds)
            + f"<h4>{letter}{_esc(sol.text)}</h4>"
            + status
            + f'<p class="kind">Evidence kind: {kind}</p>'
            + f"<p>{_esc(sol.evidence_description)}</p>"
            + "</div>"
        )
    css = "evidence-grid" if grid else "evidence-list"
    return f'<div class="{css}">' + "".join(cards) + "</div>"


def _goal_panel(gsn, nodes: dict, goal_id: str) -> str:
    goal = gsn.get_element(goal_id)
    solution_ids = [
        c for c in (nodes[goal_id].get("supportedBy", []) or [])
        if c.startswith("Sn")
    ]

    # Panel body text comes from the builder: it writes acronyms out in full
    # where the YAML's poster text abbreviates them.
    parts = [f'<p class="node-text">{_esc(goal.text)}</p>']

    origin = getattr(goal, "origin", "")
    if origin == "retained":
        parts.append(
            '<p class="origin">The authors kept this goal from '
            "ISO/PAS 8800 Annex B.</p>"
        )
    elif origin == "new":
        parts.append(
            '<p class="origin">The authors added this goal; '
            "ISO/PAS 8800 Annex B has no equivalent.</p>"
        )

    if goal_id not in NO_CHIP_ROW:
        stds = _yaml_goal_standards(nodes, goal_id)
        parts.append("<h3>Contributing standards</h3>")
        parts.append(_chip_row(stds))

    # G9 gets one clause list, the partial-coverage list below, which carries
    # the same references with the reason each falls short.
    if goal_id != "G9":
        parts.append(_clause_list(getattr(goal, "clause_references", []) or []))

    note = (goal.metadata or {}).get("note")
    if note:
        parts.append(f'<p class="note">{_esc(note)}</p>')

    # Decision points at this goal, from the catalogue the analysis reads.
    for inc in CATALOGUE.get_for_goal(goal_id):
        parts.append(
            '<p class="crosswalk">Decision point '
            f"{_esc(_paper_name(inc.inconsistency_id))}: "
            f"{_esc(inc.description)}.</p>"
        )

    # Findings that sit at this goal, from the same map the analysis reads.
    for finding in GAPS.gaps:
        if goal_id not in GAP_GOAL_MAP.get(finding.gap_id, []):
            continue
        description = " ".join(finding.description.split())
        parts.append(
            f'<p class="finding">Finding {_esc(_paper_name(finding.gap_id))}: '
            f"{_esc(description)}.</p>"
        )
        if goal_id == "G9":
            coverage = "".join(
                f"<li>{_esc(pc)}</li>" for pc in finding.partial_coverage
            )
            parts.append(
                "<h3>What existing standards cover, and where they stop</h3>"
                f"<ul class='clauses'>{coverage}</ul>"
            )

    if goal_id == "G5":
        parts.append(
            "<h3>Four kinds of evidence, four scales that do not combine</h3>"
        )
        parts.append(_evidence_cards(gsn, solution_ids, grid=True))
    elif goal_id == "G9":
        gap = (goal.metadata or {}).get("gap", "")
        parts.insert(
            1,
            '<p class="undeveloped-banner">This goal is undeveloped. '
            f"The paper records it as finding {_esc(_paper_name(gap))}.</p>",
        )
    elif solution_ids:
        parts.append("<h3>Evidence the argument calls for</h3>")
        parts.append(_evidence_cards(gsn, solution_ids, grid=False))

    return "".join(parts)


def _support_panel(gsn, nodes: dict, node_id: str) -> str:
    """Panel for S1, C1, C2 and A1.4."""
    element = gsn.get_element(node_id)
    stds = sorted(
        s for s in (element.source_standards or []) if s in NORMATIVE
    )
    parts = [f'<p class="node-text">{_esc(element.text)}</p>']
    if stds:
        parts.append("<h3>Contributing standards</h3>")
        parts.append(_chip_row(stds))
    parts.append(_clause_list(getattr(element, "clause_references", []) or []))
    return "".join(parts)


# ── Diagram column ─────────────────────────────────────────────────────

KIND_LABEL = {
    "goal": "Goal",
    "strategy": "Strategy",
    "context": "Context",
    "assumption": "Assumption",
}


def _node_button(gsn, nodes: dict, node_id: str, kind: str) -> str:
    yaml_key = node_id.replace(".", "_")
    text = " ".join(nodes[yaml_key]["text"].split())
    if len(text) > 80:
        text = text[:77] + "..."
    undeveloped = bool(nodes[yaml_key].get("undeveloped"))

    dots = ""
    if kind == "goal" and node_id not in NO_CHIP_ROW:
        stds = _yaml_goal_standards(nodes, node_id)
        dots = "".join(
            f'<span class="dot" style="--c:{STANDARD_COLORS[s]}" '
            f'title="{_esc(STANDARD_LABELS[s])}"></span>'
            for s in stds
        )
    evidence_count = sum(
        1 for c in (nodes[yaml_key].get("supportedBy", []) or [])
        if c.startswith("Sn")
    )
    badge = (
        f'<span class="badge">{evidence_count} evidence types</span>'
        if evidence_count
        else ""
    )
    classes = f"node {kind}" + (" gap" if undeveloped else "")
    return (
        f'<li><button class="{classes}" data-node="{node_id}" '
        f'aria-haspopup="dialog">'
        f'<span class="node-id">{node_id}</span> '
        f'<span class="node-kind">{KIND_LABEL[kind]}</span>'
        f'<span class="node-label">{_esc(text)}</span>'
        f'<span class="node-meta">{dots}{badge}</span>'
        f"</button></li>"
    )


def _diagram(gsn, nodes: dict) -> str:
    rows = [
        _node_button(gsn, nodes, "G1", "goal"),
        _node_button(gsn, nodes, "C1", "context"),
        _node_button(gsn, nodes, "C2", "context"),
        _node_button(gsn, nodes, "S1", "strategy"),
        _node_button(gsn, nodes, "A1.4", "assumption"),
    ]
    for gid in ["G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]:
        rows.append(_node_button(gsn, nodes, gid, "goal"))
    return '<ol class="argument">' + "".join(rows) + "</ol>"


def _templates(gsn, nodes: dict) -> str:
    out = []
    for gid in ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]:
        out.append(
            f'<template id="panel-{gid}">{_goal_panel(gsn, nodes, gid)}</template>'
        )
    for nid in ["S1", "C1", "C2", "A1.4"]:
        out.append(
            f'<template id="panel-{nid}">{_support_panel(gsn, nodes, nid)}</template>'
        )
    return "".join(out)


def _legend() -> str:
    chips = "".join(_chip(s) for s in LEGEND_ORDER)
    return (
        f'<p class="chips legend">{chips}</p>'
        '<p class="chips legend">'
        f'<span class="chip" style="--c:{GAP_GREY}">'
        "Undeveloped goal (a gap in the standards)</span></p>"
    )


def _placeholder_banner() -> str:
    if not PLACEHOLDERS_PENDING:
        return ""
    return (
        '<p class="placeholder-warning">Placeholder colours. The final '
        "palette is set in standard_colors.py.</p>"
    )


CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; background: #fff; color: #111;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 16px; line-height: 1.45;
}
header, main, footer { max-width: 720px; margin: 0 auto; padding: 0 12px; }
header h1 { font-size: 1.25rem; margin: 16px 0 4px; }
header p { margin: 4px 0; }
.placeholder-warning {
  background: #fff3cd; border: 1px solid #856404; color: #533f03;
  padding: 8px; border-radius: 6px; font-weight: 600;
}
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; padding: 0; }
.chip {
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  border: 2px solid var(--c); color: #111; font-size: 0.85rem;
  background: #fff; white-space: nowrap;
}
.chip::before {
  content: ""; display: inline-block; width: 10px; height: 10px;
  border-radius: 50%; background: var(--c); margin-right: 6px;
}
.argument { list-style: none; margin: 12px 0 24px; padding: 0; }
.argument li + li { margin-top: 10px; }
.argument li + li::before {
  content: ""; display: block; width: 2px; height: 10px;
  background: #999; margin: -10px auto 0;
}
.node {
  display: block; width: 100%; text-align: left; cursor: pointer;
  background: #fff; color: #111; border: 2px solid #333;
  border-radius: 8px; padding: 10px 12px; font: inherit;
}
.node:focus-visible { outline: 3px solid #111; outline-offset: 2px; }
.node.strategy { border-radius: 0; transform: skewX(-6deg); }
.node.strategy > * { display: inline-block; transform: skewX(6deg); }
.node.context { border-radius: 999px; border-style: solid; }
.node.assumption { border-radius: 999px; border-style: dotted; }
.node.gap { border-style: dashed; border-color: #757575; background: #f5f5f5; }
.node-id { font-weight: 700; }
.node-kind {
  font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;
  color: #444; margin-left: 6px;
}
.node-label { display: block; margin-top: 2px; }
.node-meta { display: flex; align-items: center; gap: 4px; margin-top: 6px; }
.dot {
  width: 12px; height: 12px; border-radius: 50%;
  background: var(--c); border: 1px solid #111; display: inline-block;
}
.badge {
  margin-left: auto; font-size: 0.75rem; color: #333;
  border: 1px solid #999; border-radius: 4px; padding: 1px 6px;
}
#backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
}
#sheet {
  position: fixed; left: 0; right: 0; bottom: 0; max-height: 80vh;
  overflow-y: auto; background: #fff; border-top: 3px solid #111;
  border-radius: 12px 12px 0 0; padding: 12px 16px 24px;
  max-width: 720px; margin: 0 auto;
}
.sheet-head { display: flex; align-items: baseline; gap: 8px; }
.sheet-head h2 { font-size: 1.1rem; margin: 4px 0; }
.sheet-head button {
  margin-left: auto; font-size: 1.4rem; line-height: 1;
  background: none; border: 2px solid #333; border-radius: 6px;
  padding: 2px 10px; cursor: pointer;
}
#sheet h3 { font-size: 0.95rem; margin: 14px 0 4px; }
#sheet h4 { font-size: 0.9rem; margin: 6px 0 2px; }
.node-text { white-space: pre-line; }
.origin, .kind { color: #444; font-size: 0.85rem; margin: 2px 0; }
.note {
  background: #f5f5f5; border-left: 4px solid #757575;
  padding: 6px 10px; margin: 8px 0;
}
.undeveloped-banner {
  border: 2px dashed #757575; background: #f5f5f5;
  padding: 8px 10px; font-weight: 600;
}
.finding {
  background: #f5f5f5; border-left: 4px dashed #757575;
  padding: 6px 10px; margin: 8px 0; font-weight: 600;
}
.status { font-weight: 700; margin: 2px 0; }
.status-missing { color: #555; }
.status-missing::before { content: "○ "; }
.status-provided::before { content: "● "; }
.crosswalk { color: #444; font-size: 0.85rem; }
.clauses { margin: 4px 0; padding-left: 20px; }
.evidence { border: 1px solid #bbb; border-radius: 8px; padding: 8px 10px; }
.evidence-list .evidence + .evidence { margin-top: 8px; }
.evidence-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
@media (max-width: 460px) { .evidence-grid { grid-template-columns: 1fr; } }
footer {
  border-top: 1px solid #ccc; margin-top: 24px; padding: 12px;
  font-size: 0.8rem; color: #444;
}
[hidden] { display: none; }
"""

JS = """
(function () {
  var sheet = document.getElementById('sheet');
  var backdrop = document.getElementById('backdrop');
  var title = document.getElementById('sheet-title');
  var body = document.getElementById('sheet-body');
  var close = document.getElementById('sheet-close');
  var opener = null;

  function hide() {
    sheet.hidden = true;
    backdrop.hidden = true;
    if (opener) { opener.focus(); opener = null; }
  }
  function show(id, label) {
    var tpl = document.getElementById('panel-' + id);
    if (!tpl) { return; }
    body.replaceChildren(tpl.content.cloneNode(true));
    title.textContent = label;
    sheet.hidden = false;
    backdrop.hidden = false;
    close.focus();
  }
  document.querySelectorAll('[data-node]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      opener = btn;
      show(btn.dataset.node, btn.querySelector('.node-id').textContent + ': ' +
        btn.querySelector('.node-kind').textContent);
    });
  });
  close.addEventListener('click', hide);
  backdrop.addEventListener('click', hide);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { hide(); }
  });
})();
"""


def build_html() -> str:
    nodes = _load_yaml()
    gsn = build_integrated_gsn()

    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Integrated safety and cybersecurity argument: "
        "interactive GSN view</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n"
        "<header>\n"
        "<h1>Integrated safety and cybersecurity argument</h1>\n"
        "<p>This page shows a Goal Structuring Notation (GSN) argument: a "
        "claim at the top, a strategy for supporting it, and the sub-goals "
        "and evidence underneath. It integrates four standards for an "
        "AI-based perception component in a driverless vehicle, instantiated "
        "for LiDAR. Tap any node to see which standards it draws on, what "
        "evidence it calls for, and where the standards leave a gap.</p>\n"
        + _placeholder_banner()
        + _legend()
        + "</header>\n<main>\n"
        + _diagram(gsn, nodes)
        + "</main>\n"
        '<div id="backdrop" hidden></div>\n'
        '<div id="sheet" role="dialog" aria-modal="true" aria-labelledby="sheet-title" hidden>\n'
        '<div class="sheet-head"><h2 id="sheet-title"></h2>'
        '<button id="sheet-close" aria-label="Close">&times;</button></div>\n'
        '<div id="sheet-body"></div>\n</div>\n'
        + _templates(gsn, nodes)
        + "\n<footer>\n"
        "<p>Generated file; do not edit by hand. Structure and button text "
        "come from <code>gsn/integrated_pattern.gsn.yaml</code>; panel text, "
        "clause references and evidence detail from "
        "<code>src/gsn/integrated_pattern.py</code>; findings and decision "
        "points from <code>src/analysis/gaps.py</code> and "
        "<code>src/analysis/decision_points.py</code>; colours from "
        "<code>src/visualization/standard_colors.py</code>. "
        "<code>tests/test_gsn_yaml_builder_consistency.py</code> fails if the "
        "structure sources disagree. "
        f"Rebuild: <code>{REBUILD_COMMAND}</code></p>\n"
        # A reader tapping a node meets identifiers like DP-2 and clause
        # references; these give the path to where they are traced and to the
        # recorded caveats, without which the reader has nowhere to check them.
        "<p>Trace any node's clauses and identifiers in "
        f'<a href="{BLOB_URL}/TRACEABILITY.md">TRACEABILITY.md</a>. '
        "Where the paper cites a clause this view does not, see "
        f'<a href="{BLOB_URL}/ERRATA.md">ERRATA.md</a>.</p>\n'
        # Without these a reader arriving from the poster reaches this page and
        # has nowhere to go but the browser's back button.
        '<p><a href="index.html">Back to the start</a> · '
        '<a href="seam.html">One problem at two lifecycle points</a> · '
        '<a href="g5_playground.html">Try to combine the four scales</a></p>\n'
        "</footer>\n"
        f"<script>{JS}</script>\n"
        "</body>\n</html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if docs/gsn_view.html is out of date",
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

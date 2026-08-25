"""Build the G5 playground: drag the four scales, watch the verdict flip.

Writes ``docs/g5_playground.html``, an interactive page for the poster reader on
a phone, no install. At G5 four standards each require verification evidence on
a scale that does not convert into the others. The page hands the reader the
four scales and an acceptance line for each, and lets them try to combine the
four into one release verdict. Every line they draw is one no clause draws, and
moving any line flips the verdict, so the reader reaches the finding by playing
rather than by reading it: no standard says how to combine the four (F-4).

The page asserts no combination rule. The live verdict is explicitly the
reader's own, reached from lines they set; the point is that any verdict is
reachable, which is why the rule is missing. This is the web twin of
``notebooks/g5_evidence_walk.ipynb``.

The four legs, their standards and scales are read from the built argument via
``src/analysis/g5_evidence.py`` so the page cannot drift from it. The illustrative
values and slider ranges are the page's own, declared as illustrative, not
measurements. Colours come from ``standard_colors.py``.

Self-contained: inline CSS and one inline script, no fetched resource, so it
renders offline. Output is byte-deterministic. ``tests/test_playground.py``
rebuilds it and fails if the committed copy differs.

Usage:
    python -m src.visualization.playground_page          # write the page
    python -m src.visualization.playground_page --check  # exit 1 if out of date
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys

from src.analysis.g5_evidence import g5_legs
from src.visualization.standard_colors import STANDARD_COLORS, STANDARD_LABELS

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_PATH = os.path.join(REPO_ROOT, "docs", "g5_playground.html")
REBUILD_COMMAND = "python -m src.visualization.playground_page"

BLOB_URL = (
    "https://github.com/milinpatel07/"
    "Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/blob/main"
)

# Illustrative value, slider range and starting acceptance line for each leg,
# keyed by the standard that owns it. These are the page's own numbers for the
# reader to move, not measurements: three of the four legs were not produced in
# the case study at all. Range and step suit each scale.
_DIALS = {
    "ISO26262": {"value": 0.97, "min": 0.0, "max": 1.0, "step": 0.01, "line": 0.95, "unit": ""},
    "ISO21448": {"value": 1200, "min": 0, "max": 3000, "step": 50, "line": 1000, "unit": " scenarios"},
    "ISOPAS8800": {"value": 0.95, "min": 0.5, "max": 1.0, "step": 0.01, "line": 0.90, "unit": " AUROC"},
    "ISO21434": {"value": 0.15, "min": 0.0, "max": 1.0, "step": 0.01, "line": 0.20, "unit": ""},
}


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _legs_data() -> list[dict]:
    """The four legs for the page, joined from the argument and the dials."""
    data = []
    for leg in g5_legs():
        dial = _DIALS[leg.standard_id]
        data.append(
            {
                "letter": leg.letter,
                "standard": leg.standard_id,
                "label": STANDARD_LABELS[leg.standard_id],
                "colour": STANDARD_COLORS[leg.standard_id],
                "scale": leg.scale,
                "better": leg.better,
                "instantiation": leg.instantiation,
                **dial,
            }
        )
    return data


def _leg_rows(legs: list[dict]) -> str:
    rows = []
    for leg in legs:
        direction = "at least" if leg["better"] == "higher" else "at most"
        rows.append(
            f'<div class="leg" data-standard="{leg["standard"]}">'
            f'<div class="leg-head">'
            f'<span class="chip" style="--c:{leg["colour"]}">{_esc(leg["label"])}</span>'
            f'<span class="verdict-leg" data-role="leg-verdict">&mdash;</span>'
            f"</div>"
            f'<p class="leg-name">{leg["letter"]} {_esc(leg["scale"])}'
            f' <span class="muted">(evidence value {leg["value"]}{_esc(leg["unit"])},'
            f" illustrative)</span></p>"
            f'<label class="dial">Your acceptance line: pass if the value is '
            f'{direction} <output data-role="line-out">{leg["line"]}</output>'
            f'<input type="range" data-role="line" min="{leg["min"]}" '
            f'max="{leg["max"]}" step="{leg["step"]}" value="{leg["line"]}" '
            f'style="--c:{leg["colour"]}" aria-label="acceptance line for '
            f'{_esc(leg["label"])}"></label>'
            f"</div>"
        )
    return "".join(rows)


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
.intro { margin: 0 0 8px; }
.muted { color: #555; font-size: 0.85rem; }
.verdict {
  position: sticky; top: 0; z-index: 1; background: #fff;
  border: 2px solid #111; border-radius: 10px; padding: 12px 14px;
  margin: 14px 0; text-align: center;
}
.verdict .word { font-size: 1.6rem; font-weight: 800; letter-spacing: 0.02em; }
.verdict.release { border-color: #2E7D32; }
.verdict.release .word { color: #2E7D32; }
.verdict.hold { border-color: #C62828; }
.verdict.hold .word { color: #C62828; }
.verdict .why { font-size: 0.9rem; color: #333; margin: 4px 0 0; }
.leg { border: 2px solid #222; border-radius: 8px; padding: 12px 14px; margin: 12px 0; }
.leg-head { display: flex; align-items: center; gap: 8px; }
.chip {
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  border: 2px solid var(--c); color: #111; font-size: 0.85rem;
  background: #fff; white-space: nowrap;
}
.chip::before {
  content: ""; display: inline-block; width: 10px; height: 10px;
  border-radius: 50%; background: var(--c); margin-right: 6px;
}
.verdict-leg {
  margin-left: auto; font-weight: 700; font-size: 0.85rem;
  border: 1px solid #999; border-radius: 4px; padding: 1px 8px;
}
.verdict-leg.pass { color: #2E7D32; border-color: #2E7D32; }
.verdict-leg.fail { color: #C62828; border-color: #C62828; }
.leg-name { margin: 8px 0 6px; }
.dial { display: block; font-size: 0.9rem; }
.dial output { font-weight: 700; }
input[type=range] { width: 100%; margin: 8px 0 0; accent-color: var(--c); }
.controls { margin: 14px 0; }
.controls button {
  font: inherit; border: 2px solid #333; background: #fff; color: #111;
  border-radius: 6px; padding: 6px 12px; cursor: pointer;
}
.note {
  background: #f5f5f5; border-left: 4px solid #757575;
  padding: 8px 12px; margin: 14px 0; font-size: 0.95rem;
}
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

JS_TEMPLATE = """
(function () {
  var legs = LEGS_JSON;
  var byStandard = {};
  legs.forEach(function (leg) { byStandard[leg.standard] = leg; });

  var rows = document.querySelectorAll(".leg");
  var verdict = document.getElementById("verdict");
  var word = document.getElementById("verdict-word");
  var why = document.getElementById("verdict-why");

  function evaluate() {
    var allPass = true;
    rows.forEach(function (row) {
      var leg = byStandard[row.dataset.standard];
      var input = row.querySelector('[data-role="line"]');
      var out = row.querySelector('[data-role="line-out"]');
      var flag = row.querySelector('[data-role="leg-verdict"]');
      var line = parseFloat(input.value);
      out.textContent = line;
      var passed = leg.better === "higher" ? leg.value >= line : leg.value <= line;
      flag.textContent = passed ? "PASS" : "FAIL";
      flag.className = "verdict-leg " + (passed ? "pass" : "fail");
      if (!passed) { allPass = false; }
    });
    if (allPass) {
      verdict.className = "verdict release";
      word.textContent = "RELEASE";
    } else {
      verdict.className = "verdict hold";
      word.textContent = "HOLD";
    }
    why.textContent = "You reached this by drawing four acceptance lines. "
      + "No clause draws any of them; move one and the verdict changes. "
      + "That no standard sets these lines is finding F-4.";
  }

  rows.forEach(function (row) {
    row.querySelector('[data-role="line"]').addEventListener("input", evaluate);
  });
  document.getElementById("reset").addEventListener("click", function () {
    rows.forEach(function (row) {
      var leg = byStandard[row.dataset.standard];
      row.querySelector('[data-role="line"]').value = leg.line;
    });
    evaluate();
  });
  evaluate();
})();
"""


def build_html() -> str:
    legs = _legs_data()
    js = JS_TEMPLATE.replace("LEGS_JSON", json.dumps(legs, ensure_ascii=False))
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Try to combine the four scales at G5</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n"
        "<header>\n"
        "<h1>Try to combine the four scales</h1>\n"
        '<p class="intro">At G5, the goal that verification and validation are '
        "sufficient, four standards each require their own kind of evidence on a "
        "scale that does not convert into the others. Every prescribed activity "
        "is complete. You decide: is the evidence together enough to release?</p>\n"
        '<p class="intro">To decide, draw an acceptance line for each scale below '
        "and read the verdict. Only leg (c) was produced in the case study, on "
        "simulated outputs; the four values are illustrative, so move the lines "
        "and watch what happens.</p>\n"
        "</header>\n<main>\n"
        '<div class="verdict release" id="verdict" role="status" aria-live="polite">'
        '<div class="word" id="verdict-word">RELEASE</div>'
        '<p class="why" id="verdict-why"></p></div>\n'
        + _leg_rows(legs)
        + '<div class="controls"><button id="reset" type="button">Reset the '
        "lines</button></div>\n"
        '<p class="note">Whatever verdict you reach, you reached it by choosing '
        "four lines no clause draws, on four scales that share no common unit. "
        "That is the point: the release decision at G5 is underdetermined by the "
        "standards, and whoever combines the evidence supplies a rule no clause "
        "authorises. The design-time paper records this as decision point DP-2 "
        "and finding F-4; the position paper reports the same shape in service. "
        'This page draws the four scales from <code>src/analysis/g5_evidence.py</code>; '
        "it defines no combination rule, because none exists to define.</p>\n"
        "</main>\n<footer>\n"
        "<p>Generated page; do not edit by hand. The four legs, their standards "
        "and scales come from the built argument via "
        "<code>src/analysis/g5_evidence.py</code>; the values and ranges are "
        "illustrative. Rebuild: <code>" + REBUILD_COMMAND + "</code></p>\n"
        "<p>Trace the four legs in "
        f'<a href="{BLOB_URL}/TRACEABILITY.md">TRACEABILITY.md</a>, and see what '
        "this work found about the papers in "
        f'<a href="{BLOB_URL}/ERRATA.md">ERRATA.md</a>.</p>\n'
        '<p><a href="index.html">Back to the start</a> · '
        '<a href="seam.html">One problem at two lifecycle points</a> · '
        '<a href="gsn_view.html">The argument, one node at a time</a></p>\n'
        "</footer>\n"
        f"<script>{js}</script>\n"
        "</body>\n</html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if docs/g5_playground.html is out of date"
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

"""Build the G5 evidence-combination notebook.

Writes ``notebooks/g5_evidence_walk.ipynb``. The notebook hands the reader the
four kinds of V&V evidence that meet at G5 and asks them to combine the four into
one release verdict. Every attempt turns out to rest on a threshold, weight or
normalisation the reader supplied and no standard prescribes, and changing that
input flips the verdict. That is decision point DP-2 and finding F-4 made
something the reader does rather than reads.

Prose carries the argument and the code is secondary: every conclusion is stated
in Markdown before the cell that shows it, so a reader who runs nothing still
follows it. Generated, never edited by hand, stored with no outputs so the
committed file is byte-stable. ``tests/test_g5_notebook.py`` rebuilds it, checks
the committed copy is current, and executes it end to end.

Usage:
    python -m src.visualization.g5_notebook          # write the notebook
    python -m src.visualization.g5_notebook --check  # exit 1 if stale
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_PATH = os.path.join(REPO_ROOT, "notebooks", "g5_evidence_walk.ipynb")
REBUILD_COMMAND = "python -m src.visualization.g5_notebook"

REPO_URL = (
    "https://github.com/milinpatel07/"
    "Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case"
)
BLOB_URL = f"{REPO_URL}/blob/main"
PAGES_URL = (
    "https://milinpatel07.github.io/"
    "Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/"
)


def md(*lines: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": _as_source(lines)}


def code(*lines: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _as_source(lines),
    }


def _as_source(lines: tuple[str, ...]) -> list[str]:
    text = "\n".join(lines)
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + [parts[-1]]


def _cells() -> list[dict]:
    return [
        md(
            "# Can you combine the four kinds of V&V evidence into one verdict?",
            "",
            "At G5, the goal that verification and validation are sufficient, four",
            "standards each require their own kind of evidence: ISO 26262 wants",
            "structural coverage of the non-AI code, ISO 21448 wants scenario",
            "coverage, ISO/PAS 8800 wants a statistical uncertainty score, and",
            "ISO/SAE 21434 wants an attack success rate. Every prescribed activity",
            "is complete.",
            "",
            "You are the assessor. One question remains: is the evidence together",
            "enough to release? This notebook lets you try to answer it. Each",
            "attempt fails in the same way, and the failure is the point: no clause",
            "in any of the four standards says how to combine the four scales, so",
            "any single verdict you reach is one you supplied, not one the evidence",
            "forced. The WAISE paper records this as decision point DP-2 and finding",
            "F-4.",
            "",
            "You do not have to run anything. Each conclusion is stated before the",
            "cell that shows it. Running the cells lets you change a threshold or a",
            "weight and watch the verdict flip.",
        ),
        code(
            "# On Colab, fetch the repository. Locally, this does nothing.",
            "try:",
            "    import src.analysis.g5_evidence  # noqa: F401",
            "except ImportError:  # pragma: no cover - Colab only",
            "    import subprocess, sys, os",
            f'    subprocess.run(["git", "clone", "--quiet", "{REPO_URL}.git",'
            ' "repo"], check=True)',
            '    os.chdir("repo")',
            "    sys.path.insert(0, os.getcwd())",
            "",
            "from src.analysis.g5_evidence import (",
            "    g5_legs,",
            "    scales,",
            "    combine_all_must_pass,",
            "    combine_weighted,",
            "    no_standard_combines_the_scales,",
            ")",
        ),
        md(
            "## 1. The four kinds of evidence, and their scales",
            "",
            "The four legs are read from the built argument, so this notebook",
            "cannot drift from it. Read the scale column: a coverage fraction, a",
            "scenario count, an AUROC, and an attack success rate. They share no",
            "common unit.",
            "",
            "The instantiation column is from the paper's Figure 2(b): only leg (c)",
            "was produced in the case study, on simulated ensemble outputs. The",
            "other three are marked not produced. So before you can combine",
            "anything, you already have to supply three values the case study does",
            "not have.",
        ),
        code(
            "for leg in g5_legs():",
            '    print(f"{leg.letter} {leg.standard_id:11} {leg.scale:22}"',
            '          f" better={leg.better:7} {leg.instantiation}")',
        ),
        md(
            "## 2. First attempt: require every leg to pass a threshold",
            "",
            "The most natural rule: set an acceptance threshold for each scale and",
            "release only if every leg passes. To run it you must choose four",
            "thresholds. No clause gives you any of them, so the four below are",
            "stipulations. The values you feed in are stipulations too: only leg",
            "(c) is marked produced in the argument (on simulated outputs, per the",
            "paper's Figure 2b), and the four numbers here are illustrative inputs,",
            "not measurements, so change any of them.",
        ),
        code(
            "# Illustrative values on each leg's own scale. Change any of them.",
            "values = {",
            '    "ISO26262": 0.97,   # structural coverage fraction',
            '    "ISO21448": 1200,   # scenarios covered',
            '    "ISOPAS8800": 0.95, # AUROC',
            '    "ISO21434": 0.15,   # attack success rate',
            "}",
            "lenient = {",
            '    "ISO26262": 0.95, "ISO21448": 1000,',
            '    "ISOPAS8800": 0.90, "ISO21434": 0.20,',
            "}",
            "result = combine_all_must_pass(values, lenient)",
            'print("verdict:", result["verdict"])',
            'for sid, leg in result["per_leg"].items():',
            '    print(f"  {sid:11} value={leg[\'value\']:<7} "',
            '          f"threshold={leg[\'threshold\']:<7} passed={leg[\'passed\']}")',
        ),
        md(
            "## 3. Change one threshold, and the verdict flips",
            "",
            "Raise the structural-coverage threshold from 0.95 to 0.99 and nothing",
            "about the evidence changes, but the verdict does. The verdict was a",
            "property of the threshold you chose, not of the evidence. No clause",
            "tells you whether 0.95 or 0.99 is the right line at ASIL D for the",
            "non-AI wrapper, so both are yours.",
        ),
        code(
            "strict = dict(lenient, ISO26262=0.99)",
            'print("lenient ISO26262 threshold:", combine_all_must_pass(values, lenient)["verdict"])',
            'print("strict  ISO26262 threshold:", combine_all_must_pass(values, strict)["verdict"])',
        ),
        md(
            "## 4. Second attempt: a weighted score",
            "",
            "Perhaps a single number is better than four pass/fail gates. To add",
            "four scales together you first have to put them on one axis, so here",
            "each is normalised to 0-to-1, and then weighted. Both moves are yours:",
            "no clause defines how to normalise an attack success rate against a",
            "coverage fraction, and none sets the weights.",
            "",
            "The two weightings below use the same evidence and return different",
            "scores. A safety-led assessor and a security-led assessor read the same",
            "file and disagree, with nothing in the standards to settle it.",
        ),
        code(
            "# A normalisation you invented: map each leg to 0-1. There is no",
            "# standard one, which is the point.",
            "normalised = {",
            '    "ISO26262": 0.97, "ISO21448": 0.80,',
            '    "ISOPAS8800": 0.95, "ISO21434": 0.85,',
            "}",
            'safety_led = {"ISO26262": 3, "ISO21448": 3, "ISOPAS8800": 2, "ISO21434": 1}',
            'security_led = {"ISO26262": 1, "ISO21448": 1, "ISOPAS8800": 2, "ISO21434": 4}',
            'print("safety-led score:  ", round(combine_weighted(normalised, safety_led)["score"], 3))',
            'print("security-led score:", round(combine_weighted(normalised, security_led)["score"], 3))',
        ),
        md(
            "## 5. Why no attempt can be the right one",
            "",
            "Every rule above needed something the standards do not provide: a",
            "threshold, a weighting, a way to convert one scale into another. That",
            "is not a gap in your imagination. It is a property of the standards,",
            "and the cell below reads it off the argument: each of the four legs is",
            "sourced by exactly one standard, so no standard covers two of the",
            "scales, so none of them can define how the four combine.",
        ),
        code(
            "combines = no_standard_combines_the_scales()",
            'for sid, sc in combines["scales_per_standard"].items():',
            '    print(f"{sid:11} covers scales: {sc}")',
            'print("any standard spans more than one scale:", combines["any_standard_combines"])',
            'print(combines["derivation"])',
        ),
        md(
            "## 6. Change it yourself",
            "",
            "Put in your own values, thresholds and weights. You can reach either",
            "verdict from the same evidence by moving the inputs, which is the",
            "finding: the release decision at G5 is underdetermined by the",
            "standards, and whoever combines the evidence is supplying a rule no",
            "clause authorises.",
        ),
        code(
            "my_values = dict(values)",
            "my_thresholds = dict(lenient)",
            "# edit a value or a threshold and re-run:",
            'my_thresholds["ISO21434"] = 0.10  # demand a lower attack success rate',
            'print("your verdict:", combine_all_must_pass(my_values, my_thresholds)["verdict"])',
        ),
        md(
            "## Where this goes next",
            "",
            "This is the design-time end of one problem. Suppose the vehicle is in",
            "service instead, an anomaly fires, and each concern re-evaluates. Those",
            "results still have to meet one top claim on scales that do not convert,",
            "and no clause combines them there either. The position paper reports",
            "that operation-time end, and the seam page sets the two side by side as",
            "a synthesis this repository draws, not a claim either paper makes.",
            "",
            f"- [One problem at two lifecycle points]({PAGES_URL}seam.html)",
            f"- [The argument, one node at a time]({PAGES_URL}gsn_view.html)",
            f"- [Where every claim comes from]({BLOB_URL}/TRACEABILITY.md)",
            "",
            "The evidence legs and the combination attempts come from",
            "`src/analysis/g5_evidence.py`, read from the built argument, and",
            "`tests/test_g5_notebook.py` checks them.",
        ),
    ]


def build_notebook() -> str:
    cells = _cells()
    for index, cell in enumerate(cells):
        cell["id"] = f"cell-{index:02d}"
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return json.dumps(notebook, indent=1, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if the committed notebook is out of date",
    )
    args = parser.parse_args(argv)

    content = build_notebook()
    if args.check:
        if not os.path.exists(OUTPUT_PATH):
            print(f"MISSING: {OUTPUT_PATH}. Run: {REBUILD_COMMAND}")
            return 1
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            if handle.read() != content:
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

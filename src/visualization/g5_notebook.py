"""Build the G5 evidence-combination notebook.

Writes ``notebooks/2_g5_evidence_types.ipynb``. The notebook gives the reader the
four V&V evidence types at G5 and two rules for combining them into one
sufficiency judgement. Each rule rests on a threshold, weight or normalisation
the reader supplies and no standard prescribes, and changing that input can
change the result. That is decision point DP-2 of the WAISE paper, as an
exercise.

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
OUTPUT_PATH = os.path.join(REPO_ROOT, "notebooks", "2_g5_evidence_types.ipynb")
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
            "# Can the four G5 evidence types be combined into one sufficiency judgement?",
            "",
            "This notebook accompanies the WAISE 2026 paper *Integrating Cybersecurity",
            "Into the AI Safety Assurance Argument: A GSN Pattern for AI-Based",
            "Perception Components in Highly Automated Driving*. In its integrated",
            "GSN argument, G5 is the verification and validation (V&V) goal: it",
            "claims that the V&V evidence is sufficient. All four standards contribute",
            "to G5, and the case-study evidence set has one evidence type from each:",
            "",
            "- (a) MC/DC structural coverage of the surrounding non-AI software (ISO 26262)",
            "- (b) SOTIF triggering-condition coverage in scenario testing (ISO 21448)",
            "- (c) deep-ensemble disagreement as an uncertainty indicator, measured by AUROC (ISO/PAS 8800)",
            "- (d) adversarial penetration testing, measured as attack success rate (ISO/SAE 21434)",
            "",
            "The types are disjoint by design, each on its own measurement scale, and",
            "no standard prescribes how they combine into a single sufficiency claim",
            "at G5. The paper records this as decision point DP-2 and leaves the",
            "decision to the engineer who builds the integrated V&V strategy.",
            "",
            "Suppose every prescribed activity is complete, and you are that engineer.",
            "The notebook tries two rules for combining the four types. Each needs an",
            "input that no clause supplies, and changing that input can change the",
            "result. Each section states its conclusion before the cell that shows it;",
            "run the cells to see the output and to change the inputs.",
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
            "## 1. The four evidence types and their scales",
            "",
            "The evidence types are read from the built argument, so this notebook",
            "cannot drift from it. The scale column shows an MC/DC coverage ratio, a",
            "triggering-condition coverage fraction, an AUROC and an attack success",
            "rate. Two are fractions of different things, one is a ranking score and",
            "one is a rate of successful attacks; they share no common unit.",
            "",
            "The instantiation column follows the paper's Fig. 1(b): only evidence",
            "type (c) was produced in the case study, on simulated ensemble outputs",
            "(AUROC 0.982 in the paper). The other three are marked not produced, so",
            "the values used below are illustrative inputs.",
        ),
        code(
            "for leg in g5_legs():",
            '    print(f"{leg.letter} {leg.standard_id:11} {leg.scale:40}"',
            '          f" better={leg.better:7} {leg.instantiation}")',
        ),
        md(
            "## 2. First rule: every evidence type must pass its own threshold",
            "",
            "Set an acceptance threshold for each scale and accept G5 only if every",
            "evidence type passes. The rule needs four thresholds, and no clause",
            "gives any of them, so the four below are choices. The values are",
            "illustrative inputs, not measurements; change any of them.",
        ),
        code(
            "# Illustrative values on each leg's own scale. Change any of them.",
            "values = {",
            '    "ISO26262": 0.97,   # structural coverage fraction',
            '    "ISO21448": 0.90,   # triggering-condition coverage fraction',
            '    "ISOPAS8800": 0.95, # AUROC',
            '    "ISO21434": 0.15,   # attack success rate',
            "}",
            "lenient = {",
            '    "ISO26262": 0.95, "ISO21448": 0.85,',
            '    "ISOPAS8800": 0.90, "ISO21434": 0.20,',
            "}",
            "result = combine_all_must_pass(values, lenient)",
            'print("result:", result["verdict"])',
            'for sid, leg in result["per_leg"].items():',
            '    print(f"  {sid:11} value={leg[\'value\']:<7} "',
            '          f"threshold={leg[\'threshold\']:<7} passed={leg[\'passed\']}")',
        ),
        md(
            "## 3. Changing one threshold changes the result",
            "",
            "Raise the structural-coverage threshold from 0.95 to 0.99. The evidence",
            "does not change; the result does. No clause says whether 0.95 or 0.99",
            "is the right line at ASIL D for the surrounding non-AI software, so the",
            "choice is the engineer's.",
        ),
        code(
            "strict = dict(lenient, ISO26262=0.99)",
            'print("lenient ISO26262 threshold:", combine_all_must_pass(values, lenient)["verdict"])',
            'print("strict  ISO26262 threshold:", combine_all_must_pass(values, strict)["verdict"])',
        ),
        md(
            "## 4. Second rule: a weighted score",
            "",
            "A weighted score needs two inputs that no clause defines: a",
            "normalisation that puts the four scales on one 0-to-1 axis (for example,",
            "an attack success rate against a coverage fraction), and a set of",
            "weights.",
            "",
            "The two weightings below use the same evidence and give different",
            "scores. A safety-led and a security-led engineer would reach different",
            "results, and the standards do not settle which is right.",
        ),
        code(
            "# An illustrative normalisation of each evidence type to 0-1: the",
            "# two fractions and the AUROC as they are, the attack success rate",
            "# as 1 minus its value. No standard defines a normalisation.",
            "normalised = {",
            '    "ISO26262": 0.97, "ISO21448": 0.90,',
            '    "ISOPAS8800": 0.95, "ISO21434": 0.85,',
            "}",
            'safety_led = {"ISO26262": 3, "ISO21448": 3, "ISOPAS8800": 2, "ISO21434": 1}',
            'security_led = {"ISO26262": 1, "ISO21448": 1, "ISOPAS8800": 2, "ISO21434": 4}',
            'print("safety-led score:  ", round(combine_weighted(normalised, safety_led)["score"], 3))',
            'print("security-led score:", round(combine_weighted(normalised, security_led)["score"], 3))',
        ),
        md(
            "## 5. Why the standards do not settle it",
            "",
            "Both rules needed an input the standards do not provide: a threshold, a",
            "weighting, or a way to put one scale on another's axis. The WAISE paper",
            "assigns this choice to the project: an evidence admissibility policy",
            "with documented rationale, following the precedent in ISO 26262 Parts 4",
            "and 6 for replacing a recommended verification method. The cell below",
            "is a repository check consistent with DP-2: in this encoding each",
            "evidence type at G5 is contributed by exactly one standard, so no",
            "standard covers two of the four scales.",
        ),
        code(
            "combines = no_standard_combines_the_scales()",
            'for sid, sc in combines["scales_per_standard"].items():',
            '    print(f"{sid:11} covers scales: {sc}")',
            'print("any standard spans more than one scale:", combines["any_standard_combines"])',
            'print(combines["derivation"])',
        ),
        md(
            "## 6. Try your own inputs",
            "",
            "Put in your own values, thresholds and weights. From the same evidence",
            "you can reach either result by changing the inputs: the standards do not",
            "determine the sufficiency judgement at G5, and whoever combines the",
            "evidence supplies a rule that no clause prescribes.",
        ),
        code(
            "my_values = dict(values)",
            "my_thresholds = dict(lenient)",
            "# edit a value or a threshold and re-run:",
            'my_thresholds["ISO21434"] = 0.10  # demand a lower attack success rate',
            'print("your result:", combine_all_must_pass(my_values, my_thresholds)["verdict"])',
        ),
        md(
            "## Where this goes next",
            "",
            "The SAFECOMP 2026 position paper reports a corresponding problem in",
            "operation: after a runtime anomaly, the concern-specific re-evaluations",
            "meet at the top claim on different measurement scales, and no rule",
            "combines them. The comparison page sets the two side by side; that",
            "comparison is a synthesis drawn in this repository, not a claim either",
            "paper makes.",
            "",
            f"- [G5 playground: the same exercise in the browser]({PAGES_URL}g5-playground.html)",
            f"- [Design time and operation: the two papers side by side]({PAGES_URL}design-time-and-operation.html)",
            f"- [G5 in the integrated GSN argument]({PAGES_URL}argument.html#G5)",
            f"- [TRACEABILITY.md: where each claim comes from]({BLOB_URL}/TRACEABILITY.md)",
            "",
            "The evidence types and the two rules come from",
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

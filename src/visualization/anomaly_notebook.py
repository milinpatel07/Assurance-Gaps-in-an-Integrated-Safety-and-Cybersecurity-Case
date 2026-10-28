"""Build the anomaly notebook.

Writes ``notebooks/3_runtime_anomaly.ipynb``. The notebook follows one runtime
anomaly clause by clause and finds that no clause assigns it to a concern, the
position paper's missing step 1, as an executable example.

The prose carries the argument and the code is secondary: every code cell is
short, and every conclusion is stated in Markdown before the cell that shows it,
so a reader who runs nothing still follows the whole argument.

Generated, never edited by hand, and stored with no outputs so the committed
file is byte-stable. ``tests/test_anomaly_notebook.py`` rebuilds it, fails if
the committed copy differs, and executes it end to end.

Usage:
    python -m src.visualization.anomaly_notebook          # write the notebook
    python -m src.visualization.anomaly_notebook --check  # exit 1 if stale
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
OUTPUT_PATH = os.path.join(REPO_ROOT, "notebooks", "3_runtime_anomaly.ipynb")
REBUILD_COMMAND = "python -m src.visualization.anomaly_notebook"

REPO_URL = (
    "https://github.com/milinpatel07/"
    "Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case"
)
BLOB_URL = f"{REPO_URL}/blob/main"
# A Colab reader has no local checkout, so local paths are unreachable there.
PAGES_URL = (
    "https://milinpatel07.github.io/"
    "Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/"
)


def md(*lines: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": _as_source(lines),
    }


def code(*lines: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _as_source(lines),
    }


def _as_source(lines: tuple[str, ...]) -> list[str]:
    """nbformat stores source as a list of lines, each ending in a newline
    except the last."""
    text = "\n".join(lines)
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + [parts[-1]]


def _cells() -> list[dict]:
    return [
        md(
            "# Which concern is a runtime anomaly assigned to?",
            "",
            "This notebook accompanies the SAFECOMP 2026 position paper *Operational",
            "Safety and Cybersecurity Assurance of AI-Based Perception in Highly",
            "Automated Driving*. It demonstrates the paper's argument; it adds no",
            "evidence beyond the paper's clause-level reading.",
            "",
            "An automated vehicle is in operation. A runtime monitor reports an",
            "abnormal output: detections drop in one region of the scene. Before a",
            "concern-specific activity can act on it, the anomaly has to be",
            "assigned to a concern.",
            "",
            "Three concern-specific standards are candidates. A performance",
            "insufficiency points to the SOTIF activity of ISO 21448 and, where the",
            "cause lies in the AI component itself, to the AI-safety activity of",
            "ISO/PAS 8800. An attack points to the cybersecurity activity of",
            "ISO/SAE 21434. A random hardware fault lies outside this ambiguity,",
            "because ISO 26262 requires diagnostic mechanisms that label such a",
            "fault when it is detected; the notebook asks ISO 26262 first for that",
            "reason.",
            "",
            "The notebook asks each standard, clause by clause, whether it takes the",
            "anomaly. No clause assigns it. Each section states its conclusion",
            "before the cell that shows it; run the cells to see the output and to",
            "change the anomaly.",
        ),
        code(
            "# On Colab, fetch the repository. Locally, this does nothing.",
            "try:",
            "    import src.analysis.anomaly_walk  # noqa: F401",
            "except ImportError:  # pragma: no cover - Colab only",
            "    import subprocess, sys, os",
            f'    subprocess.run(["git", "clone", "--quiet", "{REPO_URL}.git",'
            ' "repo"], check=True)',
            '    os.chdir("repo")',
            "    sys.path.insert(0, os.getcwd())",
            "",
            "from src.visualization.standard_colors import STANDARD_LABELS",
            "from src.analysis.anomaly_walk import (",
            "    SCENARIOS,",
            "    AnomalyObservation,",
            "    Cause,",
            "    resolve_with_cause,",
            "    walk_result,",
            ")",
        ),
        md(
            "## 1. What the monitor sees",
            "",
            "A runtime monitor reports what it can measure. It reports that",
            "detections dropped and that the ensemble members disagree. It reports",
            "that the hardware diagnostic passed, so nothing indicates a random",
            "hardware fault.",
            "",
            "The monitor has no field for the cause, because a perception function",
            "has no ground truth to check its output against while the vehicle is",
            "driving.",
        ),
        code(
            'anomaly = SCENARIOS["detections_drop"]',
            "print(anomaly.description)",
            "for line in anomaly.observable_summary():",
            '    print("  ", line)',
        ),
        md(
            "## 2. Ask each standard whether it takes the anomaly",
            "",
            "Each standard answers from its own clauses. Read the reasons: each",
            "answer depends on something the monitor did not report.",
        ),
        code(
            "result = walk_result(anomaly)",
            "",
            'for v in result["verdicts"]:',
            '    print(f"{STANDARD_LABELS[v.standard_id]} {v.clause} ({v.clause_title})")',
            '    print(f"  answer:  {v.verdict.value}")',
            '    print(f"  because: {v.reason}")',
            "    print()",
        ),
        md(
            "## 3. No clause assigns the anomaly",
            "",
            "ISO 21448 takes the anomaly if the cause is a performance",
            "insufficiency, and its Clause 1 refers the attack case to ISO/SAE",
            "21434. ISO/SAE 21434 takes the anomaly if the cause is an attack, and",
            "does not address performance insufficiency. Each depends on the same",
            "fact, and no clause establishes it.",
            "",
            "So the anomaly is not assigned. Each standard is consistent within its",
            "own scope; the case falls between the scopes.",
        ),
        code(
            'print("assigned to:", result["assigned_to"] or "not assigned")',
            'print("taken only if the cause is known, which no clause establishes:")',
            'for v in result["conditional_on_cause"]:',
            '    print(f"  {STANDARD_LABELS[v.standard_id]} {v.clause}")',
        ),
        md(
            "## 4. Does a weather report settle it?",
            "",
            "An objection: if it was raining, the cause is weather, so ISO 21448",
            "takes it.",
            "",
            "The notebook reads one observable, the hardware diagnostic, and",
            "ignores the weather and security fields by construction, so the cell",
            "below returns the same answer for every variant. This follows from how",
            "the notebook is built; it is not an empirical result.",
            "",
            "It is built that way for the position paper's reason: the same",
            "missing region follows from rain, sparse returns or a rare object",
            "pose, which is a performance insufficiency, and from a spoofing or",
            "relay attack, which is a cybersecurity event. The observation is",
            "identical either way. A report that something else happened at the",
            "same time is a co-occurrence, and no clause turns a co-occurrence",
            "into a cause.",
        ),
        code(
            "for name, obs in SCENARIOS.items():",
            "    r = walk_result(obs)",
            '    print(f"{name:26} assigned to: {r[\'assigned_to\'] or \'not assigned\'}")',
        ),
        md(
            "## 5. The one case that does resolve",
            "",
            "A failing hardware diagnostic is the exception. ISO 26262 requires",
            "diagnostic mechanisms that label a random hardware fault when it is",
            "detected, so in that case a clause establishes the cause, and the",
            "assignment follows.",
            "",
            "The three concern-specific standards have no such mechanism for",
            "establishing the cause from what the vehicle can observe.",
        ),
        code(
            'hw = SCENARIOS["hardware_fault"]',
            "print(hw.description)",
            'print("assigned to:", walk_result(hw)["assigned_to"])',
        ),
        md(
            "## 6. What would settle it, and what would not",
            "",
            "For a cause that sits inside one concern, knowing it settles the",
            "assignment at once. The function below is not a proposal and not a",
            "method. It takes the cause as an input, which operation cannot",
            "observe, and shows what having it would buy.",
            "",
            "For a cause that belongs to one concern, the standards agree on the",
            "assignment. What is missing comes earlier: nothing turns an",
            "observation into a cause during operation, and the position paper",
            "calls that the missing assignment step.",
            "",
            "One row differs: an attack that exploits a performance insufficiency.",
            "It is both a threat scenario and a triggering condition. The WAISE",
            "paper finds this boundary unowned at design time (decision point DP-5,",
            "finding F-3), so knowing the cause does not settle the assignment",
            "there. Combining the two papers in this way is a synthesis drawn in",
            "this repository; neither paper states it.",
        ),
        code(
            "for cause in Cause:",
            "    owner = resolve_with_cause(anomaly, cause)",
            '    print(f"if the cause were {cause.value:52} -> {owner or \'no single owner\'}")',
        ),
        md(
            "## 7. Change the anomaly yourself",
            "",
            "Build any observation from what a monitor can report and run the",
            "notebook's check on it. Because the check reads only the hardware",
            "diagnostic, mirroring the paper's argument that the observation is the",
            "same for both causes, any observation without a hardware-fault",
            "indication stays unassigned.",
        ),
        code(
            "mine = AnomalyObservation(",
            '    "My own anomaly",',
            "    detections_dropped=True,",
            "    ensemble_disagreement_high=False,",
            "    hardware_diagnostic_passed=True,",
            "    security_event_reported=True,",
            "    adverse_weather_reported=True,",
            ")",
            'print("assigned to:", walk_result(mine)["assigned_to"] or "not assigned")',
        ),
        md(
            "## Where this goes next",
            "",
            "Assignment is the first of two missing steps. Suppose the anomaly had",
            "been assigned and each concern had re-evaluated its own claim. The",
            "results would still have to support one top claim, on different",
            "measurement scales, and no rule combines them: the missing resolution",
            "step.",
            "",
            "The WAISE paper reports a corresponding problem at design time, at G5,",
            "the goal to which all four standards contribute. The comparison page",
            "sets the two side by side and lists what differs as well as what they",
            "share; the comparison is a synthesis drawn in this repository.",
            "",
            f"- [Design time and operation: the two papers side by side]({PAGES_URL}design-time-and-operation.html)",
            f"- [The integrated GSN argument, node by node]({PAGES_URL}argument.html)",
            f"- [TRACEABILITY.md: where each claim comes from]({BLOB_URL}/TRACEABILITY.md)",
            "",
            "The clause-level reasons come from `src/analysis/anomaly_walk.py`,",
            "which cites the clause behind every answer, and",
            "`tests/test_anomaly_walk.py` checks them.",
        ),
    ]


def build_notebook() -> str:
    # nbformat 4.5 requires a cell id. Number them by position so the file
    # stays byte-stable across rebuilds; a random id would break the
    # currency check on every run.
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
        "--check", action="store_true",
        help="exit 1 if the committed notebook is out of date",
    )
    args = parser.parse_args(argv)

    content = build_notebook()
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

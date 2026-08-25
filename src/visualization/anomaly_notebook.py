"""Build the anomaly-walk notebook.

Writes ``notebooks/anomaly_walk.ipynb``. The notebook follows one runtime
anomaly clause by clause until no clause assigns it to a concern, which is the
position paper's missing step 1 made executable.

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
OUTPUT_PATH = os.path.join(REPO_ROOT, "notebooks", "anomaly_walk.ipynb")
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
            "# Who owns this alarm?",
            "",
            "An automated vehicle is in service. A monitor output goes abnormal:",
            "detections drop in one region of the scene. Before anyone can act on",
            "it, the anomaly has to belong to a concern.",
            "",
            "Four standards could own it: ISO 21448 if the cause is a performance",
            "insufficiency, ISO/SAE 21434 if it is an attack, ISO/PAS 8800 if the",
            "AI component itself has drifted, and ISO 26262 if the hardware has",
            "faulted. Section 2 asks all four.",
            "",
            "This notebook follows that single anomaly clause by clause and asks",
            "each standard whether it owns it. The walk ends without an answer.",
            "That absence is the subject of the position paper, and this notebook",
            "is the paper's argument made executable rather than a new claim.",
            "",
            "You do not have to run anything. Each conclusion is stated before the",
            "cell that shows it. Running the cells lets you change the anomaly and",
            "watch the same dead end appear.",
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
            "There is no field for the cause. That is not an omission in this",
            "notebook. It is the situation: a perception function has no ground",
            "truth to check its own output against while the vehicle is driving.",
        ),
        code(
            'anomaly = SCENARIOS["detections_drop"]',
            "print(anomaly.description)",
            "for line in anomaly.observable_summary():",
            '    print("  ", line)',
        ),
        md(
            "## 2. Ask each standard whether it owns the anomaly",
            "",
            "Each standard answers from its own clauses. Read the reasons rather",
            "than the verdicts: every one of them is conditional on something the",
            "monitor did not report.",
        ),
        code(
            "result = walk_result(anomaly)",
            "",
            'for v in result["verdicts"]:',
            '    print(f"{v.standard_id} {v.clause} ({v.clause_title})")',
            '    print(f"  verdict: {v.verdict.value}")',
            '    print(f"  because: {v.reason}")',
            "    print()",
        ),
        md(
            "## 3. The walk ends without an assignment",
            "",
            "ISO 21448 owns the anomaly if the cause is a performance",
            "insufficiency, and its Clause 1 refers the attack case away to",
            "ISO/SAE 21434. ISO/SAE 21434 owns the anomaly if the cause is an",
            "attack, and it does not address performance insufficiency. Each",
            "waits on the same fact, and no clause establishes it.",
            "",
            "So the anomaly is not assigned. Not assigned is different from",
            "assigned to nobody: every standard is behaving correctly inside its",
            "own scope. The gap is between the scopes.",
        ),
        code(
            'print("assigned to:", result["assigned_to"])',
            'print("conditional on a cause nobody establishes:")',
            'for v in result["conditional_on_cause"]:',
            '    print(f"  {v.standard_id} {v.clause}")',
        ),
        md(
            "## 4. Does a weather report settle it?",
            "",
            "The obvious objection: if it was raining, the cause is weather, so",
            "ISO 21448 owns it.",
            "",
            "It does not follow, and the walk does not pretend otherwise. The walk",
            "reads one observable, the hardware diagnostic. It ignores the weather",
            "and security fields by construction, so the cell below returns the",
            "same answer for every variant. That is a statement about the walk,",
            "not a discovery in it.",
            "",
            "The reason it is built that way is the position paper's: the same",
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
            '    print(f"{name:26} assigned to: {r[\'assigned_to\']}")',
        ),
        md(
            "## 5. The one case that does resolve",
            "",
            "The failing hardware diagnostic is the exception, and it is the",
            "exception for a reason worth noticing. ISO 26262 requires diagnostic",
            "mechanisms that identify random hardware faults, so in that one case",
            "a clause does establish the cause, and the assignment follows.",
            "",
            "That is what the other three concerns lack: any mechanism that",
            "establishes the cause from what the vehicle can observe.",
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
            "For those four causes the standards do not disagree about ownership.",
            "The missing thing is upstream: nothing turns an observation into a",
            "cause while the vehicle is in service, and the position paper calls",
            "that the missing assignment step.",
            "",
            "The last row is different, and it is why this is not merely a",
            "detection problem. An attack that exploits a performance",
            "insufficiency is at once a threat scenario and a triggering",
            "condition. The other paper finds that boundary unowned at design",
            "time, as decision point DP-5 and finding F-3, so knowing the cause",
            "settles nothing there. Even a perfect cause detector would leave",
            "that case without an owner.",
        ),
        code(
            "for cause in Cause:",
            "    owner = resolve_with_cause(anomaly, cause)",
            '    print(f"if the cause were {cause.value:28} -> {owner}")',
        ),
        md(
            "## 7. Change the anomaly yourself",
            "",
            "Build any observation from what a monitor can report and run the walk",
            "on it. The unassigned result is not a property of the example chosen",
            "here; it follows from the clause structure, so it survives any",
            "observation that does not indicate a hardware fault.",
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
            'print("assigned to:", walk_result(mine)["assigned_to"])',
        ),
        md(
            "## Where this goes next",
            "",
            "Assignment is the first of two missing steps. Suppose the anomaly had",
            "been assigned, and every concern re-evaluated its own claim. Those",
            "results still have to support one top claim, on measurement scales",
            "that do not convert into one another, and no clause combines them",
            "either.",
            "",
            "The other paper reports the same shape before release, at the goal",
            "where all four standards meet. Setting the two side by side is a",
            "synthesis this repository draws, not a claim either paper makes; the",
            "seam page says so and shows what differs as well as what is shared.",
            "",
            f"- [The argument, one node at a time]({PAGES_URL}gsn_view.html)",
            f"- [One problem at two lifecycle points]({PAGES_URL}seam.html)",
            f"- [Where every claim comes from]({BLOB_URL}/TRACEABILITY.md)",
            "",
            "The clause-level reasons in this notebook come from",
            "`src/analysis/anomaly_walk.py`, which cites the clause behind every",
            "verdict, and `tests/test_anomaly_walk.py` checks them.",
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

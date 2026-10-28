"""Build the page that explains where each number in the papers comes from.

Writes ``docs/numbers.html``. A reader meeting "four standards, nine goals,
seven decision points, five findings" for the first time asks why those
numbers and not others. Each card on this page answers three questions for one
number: which rule of the method produced it, what it breaks down into, and
whether it reflects a choice the authors made or a count of what the rule
found.

Generated, never edited by hand. ``tests/test_numbers_page.py`` rebuilds it and
fails if the committed copy differs. Every design-time number is computed from
the code that produces it. The position paper is not backed by code, so its
numbers are quoted from the paper's text, and the page says so on each card.

Usage:
    python -m src.visualization.numbers_page          # write docs/numbers.html
    python -m src.visualization.numbers_page --check  # exit 1 if out of date
"""

from __future__ import annotations

import argparse
import html
import os
import sys
from collections import Counter

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.topology_sensitivity import topology_report
from src.gsn.integrated_pattern import build_integrated_gsn
from src.standards.base import LifecyclePhase
from src.standards.registry import StandardsRegistry
from src.visualization.standard_colors import (
    GAP_GREY,
    STANDARD_COLORS,
    STANDARD_LABELS,
)

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
OUTPUT_PATH = os.path.join(REPO_ROOT, "docs", "numbers.html")

REBUILD_COMMAND = "python -m src.visualization.numbers_page"

REPO_URL = (
    "https://github.com/milinpatel07/"
    "Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case"
)
BLOB = f"{REPO_URL}/blob/main"

PHASE_NAMES = {
    LifecyclePhase.CONCEPT: "Concept and requirements",
    LifecyclePhase.DESIGN: "Design and training",
    LifecyclePhase.VERIFICATION: "Verification and validation",
    LifecyclePhase.INTEGRATION: "Integration and deployment",
    LifecyclePhase.OPERATION: "Operation and monitoring",
    LifecyclePhase.MODIFICATION: "Modification and re-assurance",
}

INFORMATIVE_LABELS = {"TR5469": "ISO/IEC TR 5469"}

WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine",
}


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _word(number: int) -> str:
    return WORDS.get(number, str(number))


def _paper_id(gap_id: str) -> str:
    """The papers write F-3 where the code writes Gap-3."""
    return gap_id.replace("Gap-", "F-")


def _facts() -> dict:
    """Everything the page states, read from the code that produces it."""
    registry = StandardsRegistry()
    gsn = build_integrated_gsn()
    goals = gsn.get_goals()
    catalogue = DecisionPointCatalogue().inconsistencies
    gaps = GapClassification().gaps

    origin = Counter(goal.origin for goal in goals)
    g5 = next(goal for goal in goals if goal.element_id == "G5")
    junctions = [goal.element_id for goal in goals if len(goal.source_standards) >= 2]
    dp_types = Counter(dp.inconsistency_type.value for dp in catalogue)

    report = topology_report()
    topology_names = [t["topology"] for t in report["topologies"]]
    f3_everywhere = all(t["gap3"]["arises"] for t in report["topologies"])
    f4_everywhere = all(t["gap4"]["arises"] for t in report["topologies"])

    return {
        "normative": [s.standard_id for s in registry.normative_standards],
        "informative": [
            s.standard_id
            for s in registry.all_standards
            if s not in registry.normative_standards
        ],
        "claims": len(registry.get_all_claims()),
        "documents": len(registry.all_standards),
        "phases": [PHASE_NAMES[p] for p in LifecyclePhase],
        "goals": [goal.element_id for goal in goals],
        "retained": [g.element_id for g in goals if g.origin == "retained"],
        "added": [g.element_id for g in goals if g.origin == "new"],
        "undeveloped": [g.element_id for g in goals if g.origin == "undeveloped"],
        "origin": origin,
        "g5_standards": sorted(g5.source_standards),
        "junctions": junctions,
        "decision_points": len(catalogue),
        "dp_types": dp_types,
        "findings": len(gaps),
        "integration_induced": [g for g in gaps if g.integration_induced],
        "open_problems": [g for g in gaps if not g.integration_induced],
        "topology_names": topology_names,
        "f3_everywhere": f3_everywhere,
        "f4_everywhere": f4_everywhere,
    }


def _chip(text: str, color: str | None = None) -> str:
    style = f' style="--c:{color}"' if color else ""
    cls = "chip dot" if color else "chip"
    return f'<span class="{cls}"{style}>{_esc(text)}</span>'


def _standard_chip(standard_id: str) -> str:
    return _chip(STANDARD_LABELS[standard_id], STANDARD_COLORS[standard_id])


def _card(
    *,
    anchor: str,
    number: int,
    title: str,
    breakdown: str,
    rule: str,
    choice: str,
    check: list[tuple[str, str]],
    source: str = "Computed from the code",
) -> str:
    links = " · ".join(
        f'<a href="{_esc(href)}">{_esc(label)}</a>' for label, href in check
    )
    return (
        f'<section class="card" id="{anchor}">'
        f'<p class="num">{number}</p>'
        f"<h2>{_esc(title)}</h2>"
        f'<p class="breakdown">{breakdown}</p>'
        "<details open><summary>How the method arrives at it</summary>"
        f"<p>{rule}</p></details>"
        "<details><summary>Chosen, or found?</summary>"
        f"<p>{choice}</p></details>"
        f'<p class="check"><span class="src">{_esc(source)}.</span> Check: {links}</p>'
        "</section>"
    )


def _cards(f: dict) -> str:
    normative = len(f["normative"])
    goals = len(f["goals"])
    retained, added, undeveloped = (
        len(f["retained"]), len(f["added"]), len(f["undeveloped"]),
    )
    ii, om = len(f["integration_induced"]), len(f["open_problems"])
    dp = f["dp_types"]
    g5 = len(f["g5_standards"])

    cards = []

    cards.append(_card(
        anchor="standards",
        number=normative,
        title="Standards that apply normatively",
        breakdown=(
            "".join(_standard_chip(s) for s in f["normative"])
            + "".join(
                _chip(f"{INFORMATIVE_LABELS.get(s, s)} (informative, not counted)")
                for s in f["informative"]
            )
        ),
        rule=(
            f"An AI-based perception component in a road vehicle draws on "
            f"{_word(normative)} standards: functional safety (ISO 26262), the safety of the intended "
            "functionality, or SOTIF (ISO 21448), cybersecurity (ISO/SAE 21434), and "
            "safety of AI (ISO/PAS 8800). ISO/IEC TR 5469 is read too, because the "
            "WAISE paper cites it, but it is an informative technical report. "
            "Any statement about &ldquo;all four standards&rdquo; counts only the "
            "normative ones."
        ),
        choice=(
            "This is the scope of the papers. The scope is not tuned to produce a "
            "result: it is the set the WAISE abstract names as the standards the "
            "component requires evidence from. A fifth normative standard, if one "
            "applied, would enter as another leg of the argument and could add "
            "junctions."
        ),
        check=[
            ("registry.py", f"{BLOB}/src/standards/registry.py"),
            ("TRACEABILITY.md §1", f"{BLOB}/TRACEABILITY.md"),
        ],
    ))

    cards.append(_card(
        anchor="claims",
        number=f["claims"],
        title="Clause-level claims extracted",
        breakdown=_esc(
            f"From {_word(f['documents'])} documents: the {_word(normative)} "
            "standards and the informative report."
        ),
        rule=(
            "Step 1 of the method reads each standard at clause level. A claim is "
            "a normative requirement, a defined work product, or a required "
            "lifecycle activity, and each one names the clause it comes from."
        ),
        choice=(
            "Found, with a caveat. The count depends on how finely a clause is "
            "split into claims, so it describes this encoding, not the standards. "
            "None of the findings depends on the total; they depend on which "
            "standards meet at which goal."
        ),
        check=[
            ("src/standards/", f"{REPO_URL}/tree/main/src/standards"),
        ],
    ))

    cards.append(_card(
        anchor="phases",
        number=len(f["phases"]),
        title="Lifecycle phases",
        breakdown="".join(_chip(p) for p in f["phases"]),
        rule=(
            "Step 2 places every claim on one phase of the component's life, from "
            "the first requirement to the retrained model in service. The grid "
            "shows where the standards cover the same phase and where none does."
        ),
        choice=(
            f"Chosen. The {_word(len(f['phases']))} phases are a mapping grid the "
            "WAISE paper defines in its method. A finer "
            "grid would move claims between cells but would not create or remove "
            "a junction in the argument."
        ),
        check=[
            ("base.py, LifecyclePhase", f"{BLOB}/src/standards/base.py"),
        ],
    ))

    cards.append(_card(
        anchor="goals",
        number=goals,
        title="Goals in the integrated argument",
        breakdown=(
            _chip(f"{retained} kept from ISO/PAS 8800 Annex B: " + ", ".join(f["retained"])
                  + " (G1 reworded)")
            + _chip(f"{added} added: " + ", ".join(f["added"]))
            + _chip(f"{undeveloped} left open: " + ", ".join(f["undeveloped"]), GAP_GREY)
        ),
        rule=(
            "Step 3 starts from the Annex B pattern, the published argument pattern "
            "for AI components in road vehicles, and keeps its goals. A claim from "
            "another standard is attached to an existing goal when it serves the "
            "same purpose. A new goal is created only when nothing in the base "
            "fits. That happened twice: G7 and G8 each claim that a residual risk "
            "is acceptable (SOTIF and cybersecurity), which is a judgement, not a "
            "verification activity, so neither belongs under G5. G9, re-assurance "
            "after an update or retraining, is drawn but left undeveloped, because "
            "no standard prescribes the complete workflow."
        ),
        choice=(
            f"The base pattern is a choice; the {_word(goals)} follows from it. "
            "With a different base (AMLAS or SACE, for example) the goals would be "
            "numbered and cut differently. What the papers rely on is not the "
            "count but where the standards meet, and that is checked separately: "
            "see the findings card below."
        ),
        check=[
            ("integrated_pattern.py", f"{BLOB}/src/gsn/integrated_pattern.py"),
            ("annex_b_base.py", f"{BLOB}/src/gsn/annex_b_base.py"),
            ("the argument, node by node", "gsn_view.html"),
        ],
    ))

    cards.append(_card(
        anchor="evidence",
        number=g5,
        title="Kinds of evidence at G5, the V&V goal",
        breakdown="".join(_standard_chip(s) for s in f["g5_standards"]),
        rule=(
            "G5 claims that verification and validation are sufficient. It is the "
            "one goal where every normative standard contributes, and each asks "
            "for its own evidence: structural coverage of the non-AI code "
            "(ISO 26262), scenario coverage against triggering conditions "
            "(ISO 21448), a statistical uncertainty score (ISO/PAS 8800), and an "
            "attack success rate from penetration testing (ISO/SAE 21434)."
        ),
        choice=(
            "Found. One kind of evidence per contributing standard, and the four "
            "measure on scales that do not convert into one another. That is the "
            "central result: no clause says how to combine them."
        ),
        check=[
            ("evidence_convergence.py", f"{BLOB}/src/analysis/evidence_convergence.py"),
            ("try it: the G5 playground", "g5_playground.html"),
        ],
    ))

    cards.append(_card(
        anchor="decision-points",
        number=f["decision_points"],
        title="Decision points",
        breakdown=(
            _chip(f"{dp.get('structural', 0)} structural")
            + _chip(f"{dp.get('terminological', 0)} terminological")
            + _chip(f"{dp.get('methodological', 0)} methodological")
        ),
        rule=(
            "Step 4 examines every goal where claims from two or more standards "
            f"meet ({', '.join(f['junctions'])}). A decision point is recorded "
            "wherever the standards leave a choice to the project instead of "
            "prescribing one. Terminological ones (two words for one thing) and "
            "methodological ones (two methods for one aim) a project can settle "
            "by agreeing on a vocabulary or a method. Structural ones need a "
            "decision that no standard prescribes."
        ),
        choice=(
            f"Found. {_word(f['decision_points']).capitalize()} is what the "
            "examination turned up, not a target. The "
            "three-way typing is the paper's, and ERRATA.md records the one place "
            "where the paper's own table and prose disagree on a type (DP-2)."
        ),
        check=[
            ("decision_points.py", f"{BLOB}/src/analysis/decision_points.py"),
            ("ERRATA.md §1", f"{BLOB}/ERRATA.md"),
        ],
    ))

    topologies = " and ".join(f["topology_names"])
    robust = f["f3_everywhere"] and f["f4_everywhere"]
    cards.append(_card(
        anchor="findings",
        number=f["findings"],
        title="Findings",
        breakdown=(
            _chip(f"{ii} integration-induced: "
                  + ", ".join(_paper_id(g.gap_id) for g in f["integration_induced"]))
            + _chip(f"{om} open methodological problems: "
                    + ", ".join(_paper_id(g.gap_id) for g in f["open_problems"]))
        ),
        rule=(
            "Step 5 sorts what the integrated argument exposes into two kinds. An "
            "integration-induced finding exists only between the scopes of the "
            "standards, so no reader of one standard alone can see it: the "
            "adversarial-SOTIF boundary that belongs to neither G7 nor G8 (F-3), "
            "and the release decision that has to combine all four kinds of "
            "evidence (F-4). An open methodological problem is a framework the "
            "standards do prescribe, with no published method yet for the numbers "
            "it needs (F-1, F-2, F-5). The code writes Gap-1 to Gap-5 for F-1 to F-5."
        ),
        choice=(
            "Found, and tested against the obvious objection that a different "
            "argument structure would make the integration-induced findings "
            "disappear. They were derived under two structures, "
            f"{_esc(topologies)}: "
            + ("both arise under each." if robust else "they do not both arise under each.")
            + " The derivation reports the result either way; it is not tuned."
        ),
        check=[
            ("gaps.py", f"{BLOB}/src/analysis/gaps.py"),
            ("topology_sensitivity.py", f"{BLOB}/src/analysis/topology_sensitivity.py"),
            ("counterfactual.py", f"{BLOB}/src/analysis/counterfactual.py"),
        ],
    ))

    cards.append(_card(
        anchor="missing-steps",
        number=2,
        title="Missing steps once the vehicle is in service",
        breakdown=_chip("Assignment: which concern owns the alarm?")
        + _chip("Resolution: one judgement from the concerns' results"),
        rule=(
            "The position paper follows a runtime alarm that arrives without a "
            "label. Rain and a spoofing attack can produce the same missing "
            "detections. ISO 21448, ISO/PAS 8800 and ISO/SAE 21434 each define "
            "an operation-phase activity within their own concern, but no "
            "clause assigns the alarm to one of them (step one), and none says "
            "how their results resolve into one judgement on the argument "
            "(step two)."
        ),
        choice=(
            "Argued. These are the two steps the paper finds missing, at clause "
            "level. Labelling every alarm would close the first and leave the "
            "second, which is why the paper keeps them apart. The paper then "
            "states four requirements (R1 to R4) a closing method must meet, each "
            "necessary, without claiming the set is sufficient."
        ),
        check=[
            ("the anomaly walk notebook", f"{BLOB}/notebooks/anomaly_walk.ipynb"),
            ("one problem, two lifecycle points", "seam.html"),
        ],
        source="From the position paper's text; no code computes it",
    ))

    return "".join(cards)


CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; background: #fff; color: #111;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 16px; line-height: 1.5;
}
header, main, footer { max-width: 760px; margin: 0 auto; padding: 0 16px; }
header { padding-top: 22px; }
h1 { font-size: 1.5rem; line-height: 1.25; margin: 0 0 8px; }
.lede { margin: 0 0 8px; }
nav.jump { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0 0; }
nav.jump a {
  border: 2px solid #222; border-radius: 999px; padding: 2px 10px;
  color: #111; text-decoration: none; font-size: 0.9rem; font-weight: 600;
}
main { display: grid; gap: 14px; margin-top: 18px; }
.card {
  border: 2px solid #222; border-radius: 10px; padding: 12px 16px 10px;
  display: grid; grid-template-columns: auto 1fr; column-gap: 14px;
}
.card > *:not(.num) { grid-column: 2; }
.num {
  grid-row: 1 / span 2; margin: 0; font-size: 2.6rem; font-weight: 800;
  line-height: 1; min-width: 2.2ch; text-align: center;
}
.card h2 { font-size: 1.15rem; margin: 2px 0 6px; }
.breakdown { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 8px; }
.chip {
  display: inline-block; padding: 2px 10px; border-radius: 999px;
  border: 2px solid #444; background: #fff; font-size: 0.85rem;
}
.chip.dot { border-color: var(--c); }
.chip.dot::before {
  content: ""; display: inline-block; width: 10px; height: 10px;
  border-radius: 50%; background: var(--c); margin-right: 6px;
}
details { margin: 0 0 6px; }
summary { cursor: pointer; font-weight: 700; }
details p { margin: 4px 0 6px; }
.check { font-size: 0.9rem; margin: 4px 0 2px; color: #222; }
.src { font-weight: 700; }
a { color: #111; }
footer {
  border-top: 1px solid #ccc; margin-top: 20px; padding-top: 14px;
  padding-bottom: 28px; font-size: 0.9rem; color: #333;
}
footer code {
  background: #f2f2f2; border: 1px solid #ddd; border-radius: 4px;
  padding: 1px 6px; font-size: 0.85rem;
}
@media (max-width: 420px) {
  .card { grid-template-columns: 1fr; }
  .card > *:not(.num) { grid-column: 1; }
  .num { grid-row: auto; text-align: left; }
}
"""

JUMPS = [
    ("standards", "Standards"),
    ("goals", "Goals"),
    ("evidence", "G5 evidence"),
    ("decision-points", "Decision points"),
    ("findings", "Findings"),
    ("missing-steps", "In service"),
]


def build_html() -> str:
    facts = _facts()
    jumps = "".join(f'<a href="#{a}">{_esc(t)}</a>' for a, t in JUMPS)
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Where the numbers come from</title>\n"
        '<meta name="description" content="Each count in the two papers, the '
        'rule that produced it, and whether it is a choice or a result.">\n'
        f"<style>{CSS}</style>\n</head>\n<body>\n"
        "<header>\n"
        "<h1>Where the numbers come from</h1>\n"
        f'<p class="lede">{_word(len(facts["normative"])).capitalize()} standards, '
        f'{_word(len(facts["goals"]))} goals, {_word(facts["decision_points"])} '
        f'decision points, {_word(facts["findings"])} findings. '
        "None of these was a target. Each is what one step of "
        "the method produced, and each card below names that step, shows "
        "what the number breaks down into, and says whether it reflects a "
        "choice or a result.</p>\n"
        f'<nav class="jump" aria-label="Jump to">{jumps}</nav>\n'
        "</header>\n"
        f"<main>{_cards(facts)}</main>\n"
        "<footer>\n"
        '<p><a href="index.html">Back to the overview</a> · '
        '<a href="gsn_view.html">the argument, node by node</a> · '
        f'<a href="{BLOB}/TRACEABILITY.md">TRACEABILITY.md</a>, where every '
        "number traces to a paper passage, a clause, or a command.</p>\n"
        f"<p>Generated page; do not edit by hand. Rebuild: "
        f"<code>{REBUILD_COMMAND}</code></p>\n"
        "</footer>\n</body>\n</html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="exit 1 if docs/numbers.html is out of date",
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

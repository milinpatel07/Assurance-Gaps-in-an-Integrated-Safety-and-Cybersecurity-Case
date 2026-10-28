"""Build the page that explains where each count in the papers comes from.

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
from src.analysis.findings import GapClassification
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


# Why a decision point attaches to a goal that is not a junction. Keyed by goal;
# the goals themselves are read from the catalogue.
_DP_EXTRA_REASON = {
    "G3": "there ISO/PAS 8800 meets the informative ISO/IEC TR 5469 on data "
          "sufficiency",
    "G7": "DP-3 concerns the AI-error terminology used at both G2 and G7, and "
          "DP-5 the boundary between G7 and G8",
}


def _dp_id(dp) -> str:
    """The papers write DP-2 where the code writes I-2."""
    return dp.inconsistency_id.replace("I-", "DP-")


def _facts() -> dict:
    """Everything the page states, read from the code that produces it."""
    registry = StandardsRegistry()
    gsn = build_integrated_gsn()
    goals = gsn.get_goals()
    catalogue = DecisionPointCatalogue().inconsistencies
    gaps = GapClassification().gaps

    g5 = next(goal for goal in goals if goal.element_id == "G5")
    reformulated = [
        g.element_id for g in goals
        if any("reformulated" in ref for ref in g.clause_references)
    ]
    dp_nodes = sorted({node for dp in catalogue for node in dp.gsn_nodes},
                      key=lambda n: int(n[1:]))
    junctions = [g.element_id for g in goals if len(g.source_standards) >= 2]
    dp_extra = {
        node: [_dp_id(dp) for dp in catalogue if node in dp.gsn_nodes]
        for node in dp_nodes if node not in junctions
    }
    # "also" only where the decision point sits at a junction as well.
    dp_also = {
        node: all(
            any(n in junctions for n in dp.gsn_nodes)
            for dp in catalogue if node in dp.gsn_nodes
        )
        for node in dp_extra
    }
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
        "reformulated": reformulated,
        "retained": [
            g.element_id for g in goals
            if g.origin == "retained" and g.element_id not in reformulated
        ],
        "added": [g.element_id for g in goals if g.origin == "new"],
        "undeveloped": [g.element_id for g in goals if g.origin == "undeveloped"],
        "g5_standards": sorted(g5.source_standards),
        "dp_nodes": dp_nodes,
        "junctions": junctions,
        "dp_extra": dp_extra,
        "dp_also": dp_also,
        "junctions_without_dp": [j for j in junctions if j not in dp_nodes],
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
        "<details open><summary>Where the number comes from</summary>"
        f"<p>{rule}</p></details>"
        "<details><summary>Scope choice, result, or encoding?</summary>"
        f"<p>{choice}</p></details>"
        f'<p class="check"><span class="src">{_esc(source)}.</span> Check: {links}</p>'
        "</section>"
    )


def _cards(f: dict) -> str:
    normative = len(f["normative"])
    goals = len(f["goals"])
    ii, om = len(f["integration_induced"]), len(f["open_problems"])
    dp = f["dp_types"]
    g5 = len(f["g5_standards"])

    cards = []

    cards.append(_card(
        anchor="standards",
        number=normative,
        title="Standards in scope",
        breakdown=(
            "".join(_standard_chip(s) for s in f["normative"])
            + "".join(
                _chip(f"{INFORMATIVE_LABELS.get(s, s)} (informative report, not counted)")
                for s in f["informative"]
            )
        ),
        rule=(
            "The WAISE paper gives one reason per standard: an AI-based "
            "perception component falls within the scope of all "
            f"{_word(normative)} at once. ISO 26262 applies because a perception "
            "failure can contribute to ASIL D hazardous events at SAE Level 4; "
            "ISO 21448 (SOTIF, the safety of the intended functionality) because "
            "the intended function can produce hazardous behaviour without a "
            "fault; ISO/SAE 21434 because the sensor data are vulnerable to "
            "adversarial manipulation; ISO/PAS 8800 because the component is a "
            "trained neural network. ISO/IEC TR 5469 is cited as an informative "
            "technical report and is not counted."
        ),
        choice=(
            "A scope choice of the papers. ISO/TS 5083 (safety at the level of "
            "the automated driving system), ISO 26262 Parts 9 to 12, UL 4600, "
            "the EU AI Act and UNECE R155/R156 are outside it. The position "
            "paper works with three of the four: ISO 21448, ISO/PAS 8800 and "
            "ISO/SAE 21434, each of which defines an operation-phase activity "
            "that uses runtime monitor evidence."
        ),
        source="Counted from the code",
        check=[
            ("registry.py", f"{BLOB}/src/standards/registry.py"),
            ("TRACEABILITY.md, section 1", f"{BLOB}/TRACEABILITY.md#1-standards-and-editions"),
        ],
    ))

    cards.append(_card(
        anchor="claims",
        number=f["claims"],
        title="Clause-level claims encoded",
        breakdown=_esc(
            f"From {_word(f['documents'])} documents: the {_word(normative)} "
            "standards and the informative report."
        ),
        rule=(
            "Step 1 of the WAISE method (claim extraction) reads each standard "
            "at clause level. A claim is a normative requirement, a defined work "
            "product, or a required lifecycle activity, and each one names the "
            "clause it comes from."
        ),
        choice=(
            "Repository encoding. Neither paper reports this count, and it "
            "depends on how finely a clause is split into claims. No decision "
            "point or finding depends on the total; they depend on which "
            "standards contribute to which goal."
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
            "Step 2 of the WAISE method (lifecycle-phase mapping) places every "
            "claim on one phase, from the first requirement to the retrained "
            "model in operation. The grid shows where the standards cover the "
            "same phase and where none of them does."
        ),
        choice=(
            "A choice of the WAISE paper: a mapping grid that spans the "
            "lifecycles of the four standards rather than the phase model of any "
            "one of them. A finer grid would move claims between cells but would "
            "not change which standards contribute to which goal."
        ),
        source="Counted from the code",
        check=[
            ("base.py, LifecyclePhase", f"{BLOB}/src/standards/base.py"),
        ],
    ))

    cards.append(_card(
        anchor="goals",
        number=goals,
        title="Goals in the integrated GSN argument",
        breakdown=(
            _chip(f"{len(f['reformulated'])} reformulated: " + ", ".join(f["reformulated"]))
            + _chip(f"{len(f['retained'])} retained: " + ", ".join(f["retained"]))
            + _chip(f"{len(f['added'])} added: " + ", ".join(f["added"]))
            + _chip(f"{len(f['undeveloped'])} added, undeveloped: "
                    + ", ".join(f["undeveloped"]), GAP_GREY)
        ),
        rule=(
            "Step 3 of the WAISE method starts from the GSN pattern in ISO/PAS "
            "8800 Annex B: a top-level goal G1 and five sub-goals G2 to G6. The "
            "rule is to attach claims from the other standards to an existing "
            "goal where the assurance domain matches, and to create a new goal "
            "only where no equivalent exists. G1 is reformulated to claim the "
            "integrated safety and cybersecurity requirements, because the "
            "strategy now argues over four assurance domains. G7 (SOTIF residual "
            "risk) and G8 (cybersecurity risk) are added because each claims "
            "that a residual risk is acceptable, which is a judgement rather "
            "than a verification activity. G9 (re-assurance after a modification) "
            "is added and left undeveloped, because no single standard "
            "prescribes the complete re-assurance workflow."
        ),
        choice=(
            "The base pattern is a choice; the count follows from it and from "
            "the rule above. The WAISE paper names an alternative top-level "
            "structure, the concern hierarchy of Warg and Skoglund, and keeps "
            "the Annex B structure because it preserves the activity-based "
            "decomposition and keeps each branch traceable to one standard."
        ),
        check=[
            ("integrated_pattern.py", f"{BLOB}/src/gsn/integrated_pattern.py"),
            ("annex_b_base.py", f"{BLOB}/src/gsn/annex_b_base.py"),
            ("the integrated GSN argument", "argument.html"),
        ],
    ))

    cards.append(_card(
        anchor="evidence",
        number=g5,
        title="Evidence types at G5, the V&V goal",
        breakdown="".join(_standard_chip(s) for s in f["g5_standards"]),
        rule=(
            "G5 claims that the verification and validation (V&V) evidence is "
            "sufficient. It is the goal to which all four standards contribute, "
            "and the case-study evidence set has one evidence type from each: "
            "(a) MC/DC structural coverage of the surrounding non-AI software "
            "(ISO 26262), (b) SOTIF triggering-condition coverage in scenario "
            "testing (ISO 21448), (c) deep-ensemble disagreement as an "
            "uncertainty indicator, measured by AUROC (ISO/PAS 8800), and (d) "
            "adversarial penetration testing, measured as attack success rate "
            "(ISO/SAE 21434)."
        ),
        choice=(
            "The count follows from the scope: one evidence type per "
            "contributing standard. The result is what the WAISE paper finds "
            "about them: the types are disjoint by design, each on its own "
            "measurement scale, and no standard prescribes how they combine "
            "into a single sufficiency claim at G5 (decision point DP-2)."
        ),
        check=[
            ("evidence_convergence.py", f"{BLOB}/src/analysis/evidence_convergence.py"),
            ("G5 playground", "g5-playground.html"),
            ("G5 in the argument", "argument.html#G5"),
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
            "Step 4 of the WAISE method (junction-point analysis) examines each "
            "goal where claims from two or more standards meet, and records a "
            "decision point wherever the standards defer to application context, "
            "so that the engineer has to decide. In this argument "
            f"{_word(len(f['junctions']))} goals are junctions: "
            f"{', '.join(f['junctions'])}. "
            + "".join(
                f"{' and '.join(ids)} "
                + ((f"also {'attaches' if len(ids) == 1 else 'attach'} to "
                    if f["dp_also"][node]
                    else f"{'sits' if len(ids) == 1 else 'sit'} at ")
                   + f"{node}, to ")
                + "which only one of the four standards contributes: "
                f"{_DP_EXTRA_REASON.get(node, 'see decision_points.py')}. "
                for node, ids in f["dp_extra"].items()
            )
            + (
                f"{', '.join(f['junctions_without_dp'])} is a junction without a "
                "decision point. " if f["junctions_without_dp"] else ""
            )
            + "The paper distinguishes three types: "
            "terminological (different terms for the same concept), "
            "methodological (different methods for the same objective), and "
            "structural (frameworks requiring decisions that no standard "
            "prescribes). A project can settle the first two by agreeing on a "
            "vocabulary or a method."
        ),
        choice=(
            "A result of the analysis: the count is what the examination found. "
            "The split by type follows the paper's prose; the paper's Table 4 "
            "types DP-2 as both structural and methodological, which ERRATA.md "
            "records."
        ),
        check=[
            ("decision_points.py", f"{BLOB}/src/analysis/decision_points.py"),
            ("ERRATA.md, entry 1", f"{BLOB}/ERRATA.md"),
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
            "Step 5 of the WAISE method sorts the findings into two categories. "
            "An integration-induced finding emerges only between the scopes of "
            "the standards and cannot be detected from any one of them alone: "
            "F-3, adversarial inputs that exploit a functional insufficiency "
            "fall between G7 and G8 and belong to neither; F-4, no standard "
            "requires evaluating the combined residual risk across domains for "
            "the release decision. An open methodological problem is one where "
            "the standards prescribe a framework, but no published method "
            "supplies what it needs: application-specific quantitative acceptance criteria (F-1) "
            "and data acceptance criteria (F-5) for AI components, and a "
            "complete re-assurance workflow after an over-the-air update (F-2)."
        ),
        choice=(
            "A result of the analysis. As a further check, not reported in "
            "either paper, this repository derives F-3 and F-4 under two "
            f"argument structures, {_esc(topologies)}: "
            + ("both findings arise under each." if robust
               else "they do not both arise under each.")
        ),
        check=[
            ("findings.py", f"{BLOB}/src/analysis/findings.py"),
            ("topology_sensitivity.py", f"{BLOB}/src/analysis/topology_sensitivity.py"),
        ],
    ))

    cards.append(_card(
        anchor="missing-steps",
        number=2,
        title="Missing steps in operation (position paper)",
        breakdown=_chip("Assignment of an anomaly to a concern")
        + _chip("Resolution of the concern-specific results into one judgement"),
        rule=(
            "In operation, a runtime monitor can report an abnormal output, for "
            "example a scene region where detections drop. The anomaly carries "
            "no concern label: rain and a spoofing attack can produce the same "
            "missing detections. ISO 21448, ISO/PAS 8800 and ISO/SAE 21434 each "
            "define an operation-phase activity within their own concern, but no "
            "clause in these standards assigns the anomaly to a concern "
            "(step 1), and none resolves the concern-specific results into one "
            "judgement on the assurance argument (step 2)."
        ),
        choice=(
            "Argued from clause text. The two steps are kept apart because "
            "labelling every anomaly would close the first and leave the second. "
            "The paper's position is that closing the gap is an in-service "
            "re-evaluation of the safety case, not an in-vehicle runtime "
            "function, and it states four requirements for a method that closes "
            "it: R1 heterogeneous evidence, R2 assignment, R3 traceability and "
            "currency, R4 modification. Each is necessary; the paper does not "
            "claim the set is sufficient."
        ),
        check=[
            ("the anomaly notebook", f"{BLOB}/notebooks/3_runtime_anomaly.ipynb"),
            ("the comparison page", "design-time-and-operation.html"),
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
    ("missing-steps", "Operation"),
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
        "Each card below names the step of the WAISE paper's five-step method "
        "that produced the number, shows what it breaks down into, and says "
        "whether it reflects a scope choice of the papers, a result of the "
        "analysis, or this repository's encoding.</p>\n"
        f'<nav class="jump" aria-label="Jump to">{jumps}</nav>\n'
        "</header>\n"
        f"<main>{_cards(facts)}</main>\n"
        "<footer>\n"
        '<p><a href="index.html">Start page</a> · '
        '<a href="argument.html">The integrated GSN argument, node by node</a> · '
        f'<a href="{BLOB}/TRACEABILITY.md">TRACEABILITY.md</a>, which traces '
        "each number to a paper passage, a clause, or a command.</p>\n"
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

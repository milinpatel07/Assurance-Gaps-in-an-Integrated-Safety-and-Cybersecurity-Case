"""Generate TRACEABILITY.md, the single index of where every claim comes from.

Every number, table, figure and non-obvious statement in this repository traces
to exactly one of three things, and the index says which:

  PAPER     a passage in one of the two papers, cited by section or table
  CLAUSE    a clause in a named edition of a named standard
  COMMAND   a command in this repository that regenerates it

Anything that traces to none of the three does not belong in the repository. The
index also carries a short list of known inconsistencies, so that a reader meets
them here rather than discovering them alone.

The file is generated, not hand-written, so it cannot drift from the code it
describes. ``tests/test_traceability_index.py`` regenerates it and fails if the
committed copy differs.

Usage:
    python -m src.results.traceability_index          # write TRACEABILITY.md
    python -m src.results.traceability_index --check  # exit 1 if out of date
"""

from __future__ import annotations

import argparse
import os
import sys

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.gsn.integrated_pattern import build_integrated_gsn
from src.standards.registry import StandardsRegistry

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_PATH = os.path.join(REPO_ROOT, "TRACEABILITY.md")

WAISE = "paper/waise2026/CR_Submission_WAISE_SafeCompAssuranceGaps_SafetySecurityCase_AI_Perception_HAD.tex"
POSITION = "paper/safecomp2026-position/CR_position_paper.tex"

GENERATE_ALL = "python -m src.results.generate_all --seed 42 --scenes 50 --output output"


def _header() -> list[str]:
    return [
        "# Traceability Index",
        "",
        "Where every claim in this repository comes from. One index, not scattered",
        "footnotes.",
        "",
        "Each row traces to exactly one of three kinds of source, and says which:",
        "",
        "| Kind | Meaning |",
        "|---|---|",
        "| **PAPER** | A passage in one of the two papers. Cited by section or table. |",
        "| **CLAUSE** | A clause in a named edition of a named standard. |",
        "| **COMMAND** | A command in this repository that regenerates it. |",
        "",
        "Anything that traces to none of the three does not belong here. Where the",
        "repository asserts something rather than computing it, the row says so.",
        "",
        "This file is generated. Do not edit it by hand:",
        "",
        "```bash",
        "python -m src.results.traceability_index",
        "```",
        "",
        "The two papers:",
        "",
        f"- WAISE 2026, GSN integration: `{WAISE}`",
        f"- SAFECOMP 2026 position: `{POSITION}`",
        "",
    ]


def _standards_section(registry: StandardsRegistry) -> list[str]:
    normative_ids = {s.standard_id for s in registry.normative_standards}
    lines = [
        "## 1. Standards and editions",
        "",
        "Every CLAUSE row elsewhere in this index refers to one of these editions.",
        "",
        "| Code id | Edition as cited | Year | Normative here | Clauses | Claims |",
        "|---|---|---|---|---|---|",
    ]
    for s in sorted(registry.all_standards, key=lambda x: x.standard_id):
        norm = "yes" if s.standard_id in normative_ids else "no (informative)"
        lines.append(
            f"| `{s.standard_id}` | {s.full_name} | {s.year} | {norm} | "
            f"{len(s.clauses)} | {len(s.claims)} |"
        )
    lines += [
        "",
        "The four normative standards are the ones counted by goal-density and by",
        'any claim in the papers about "all four standards". ISO/IEC TR 5469 is',
        "informative and is excluded from those counts.",
        "",
    ]
    return lines


def _crosswalk_section(catalogue: DecisionPointCatalogue, gaps: GapClassification) -> list[str]:
    lines = [
        "## 2. Identifier crosswalk, paper to code",
        "",
        "The papers and the code name the same objects differently. A reader holding",
        "the paper and reading the code needs this table.",
        "",
        "| Paper | Code | Object | Where in the code |",
        "|---|---|---|---|",
    ]
    for inc in catalogue.inconsistencies:
        n = inc.inconsistency_id.split("-")[1]
        lines.append(
            f"| DP-{n} | `{inc.inconsistency_id}` | {inc.description} | "
            f"`src/analysis/decision_points.py` |"
        )
    for gap in gaps.gaps:
        n = gap.gap_id.split("-")[1]
        lines.append(
            f"| F-{n} | `{gap.gap_id}` | {gap.description.splitlines()[0]} | "
            f"`src/analysis/gaps.py` |"
        )
    lines += [
        "",
        'The paper calls DP-N "decision points" and F-N "integration-induced',
        'findings and open methodological problems". The code calls them',
        "inconsistencies (`I-N`) and gaps (`Gap-N`). The numbers correspond exactly;",
        "only the prefixes differ. `gsn/integrated_pattern.gsn.yaml` still tags G9",
        'with the older "Gap-2" spelling.',
        "",
    ]
    return lines


def _goals_section(registry: StandardsRegistry) -> list[str]:
    gsn = build_integrated_gsn()
    normative_ids = [s.standard_id for s in registry.normative_standards]
    lines = [
        "## 3. Goals of the integrated pattern",
        "",
        f"PAPER: Table 2 and Figure 2 of the WAISE paper. COMMAND: `{GENERATE_ALL}`",
        "",
        "| Goal | Claim | Origin | Normative standards | Clause references |",
        "|---|---|---|---|---|",
    ]
    for goal in sorted(gsn.get_goals(), key=lambda g: g.element_id):
        srcs = [s for s in (goal.source_standards or []) if s in normative_ids]
        refs = "; ".join(getattr(goal, "clause_references", []) or []) or "(none)"
        text = " ".join(goal.text.split())
        if len(text) > 90:
            text = text[:87] + "..."
        lines.append(
            f"| {goal.element_id} | {text} | {getattr(goal, 'origin', '')} | "
            f"{', '.join(sorted(srcs)) or '(none)'} | {refs} |"
        )
    lines += [
        "",
        "G5 is the only goal drawing on all four normative standards. That is the",
        "paper's central structural claim, and it is checked from both of the",
        "repository's representations by",
        "`tests/test_representation_consistency.py`.",
        "",
    ]
    return lines


def _clause_section(registry: StandardsRegistry) -> list[str]:
    lines = [
        "## 4. Clause to node index",
        "",
        "Every extracted claim, the clause it comes from, and the node it supports.",
        "This is the machine-readable traceability the WAISE paper refers to in",
        "Section 4.",
        "",
        "| Standard | Clause | Claim | Node | Phase |",
        "|---|---|---|---|---|",
    ]
    rows = []
    for s in registry.all_standards:
        for c in s.claims:
            node = c.gsn_goal or "(out of scope)"
            phase = c.lifecycle_phase.display_name if c.lifecycle_phase else "(none)"
            rows.append(
                (s.standard_id, c.source_clause.reference, c.claim_id, node, phase)
            )
    for row in sorted(rows):
        lines.append("| " + " | ".join(f"`{row[0]}`" if i == 0 else row[i]
                                       for i in range(5)) + " |")

    out_of_scope = [
        c for s in registry.all_standards for c in s.claims if c.is_out_of_scope
    ]
    if out_of_scope:
        lines += ["", "### Claims deliberately outside the argument", ""]
        for c in out_of_scope:
            lines += [
                f"**`{c.claim_id}`** ({c.source_clause.standard_id} "
                f"{c.source_clause.reference})",
                "",
                f"> {c.text}",
                "",
                " ".join(c.out_of_scope_reason.split()),
                "",
            ]
    lines.append("")
    return lines


def _findings_section(gaps: GapClassification) -> list[str]:
    lines = [
        "## 5. Findings",
        "",
        "PAPER: Table 4 of the WAISE paper. Lifecycle phases follow that table.",
        "",
        "| Paper | Code | Lifecycle phase | Integration-induced | Partial coverage |",
        "|---|---|---|---|---|",
    ]
    for gap in gaps.gaps:
        n = gap.gap_id.split("-")[1]
        cover = "; ".join(" ".join(p.split()) for p in gap.partial_coverage)
        lines.append(
            f"| F-{n} | `{gap.gap_id}` | {gap.lifecycle_phase_label} | "
            f"{'yes' if gap.integration_induced else 'no'} | {cover} |"
        )
    lines += [
        "",
        "F-3 and F-4 are the integration-induced findings. F-3's invisibility from",
        "any single standard is derived in `src/analysis/counterfactual.py`. F-4's",
        "is derived there too, from a premise that module states as a premise rather",
        "than proves. F-1, F-2 and F-5 are asserted, and that module says so.",
        "",
    ]
    return lines


def _decision_points_section(catalogue: DecisionPointCatalogue) -> list[str]:
    stats = catalogue.summary_statistics()
    lines = [
        "## 6. Decision points",
        "",
        "PAPER: Table 3 of the WAISE paper.",
        "",
        "| Paper | Code | Type | Standards | GSN node |",
        "|---|---|---|---|---|",
    ]
    for inc in catalogue.inconsistencies:
        n = inc.inconsistency_id.split("-")[1]
        lines.append(
            f"| DP-{n} | `{inc.inconsistency_id}` | {inc.inconsistency_type.value} | "
            f"{', '.join(inc.standards_involved)} | {', '.join(inc.gsn_nodes)} |"
        )
    lines += [
        "",
        f"Split: {stats['structural']} structural, {stats['terminological']} "
        f"terminological, {stats['methodological']} methodological.",
        "",
    ]
    return lines


def _artefacts_section() -> list[str]:
    lines = [
        "## 7. Artefacts and their provenance",
        "",
        "Every artefact is measured, seeded, argued, or generated. No artefact is",
        "left undeclared.",
        "",
        "| Artefact | Provenance | Source |",
        "|---|---|---|",
        f"| `output/analysis_results.json` | generated | COMMAND: `{GENERATE_ALL}` |",
        f"| `output/csv/*` | generated | COMMAND: `{GENERATE_ALL}` |",
        f"| `output/latex/*.tex` | generated | COMMAND: `{GENERATE_ALL}` |",
        f"| `output/figures/*` | generated | COMMAND: `{GENERATE_ALL}` |",
        "| `docs/figures/*.png` | seeded and derived | COMMAND: as above. See `docs/figures/README.md` |",
        "| `data/synthetic_illustrations/*` | seeded, seed 42 | COMMAND: as above. Not measurements. See that directory's README |",
        "| `data/empirical_results/*` | measured | Trained PointPillars ensemble, external to this repository. Cited by neither paper. See that directory's README |",
        "| `data/carla_configs/*.yaml` | hand-written | Documentation only. Checked against `src/` by `tests/test_config_documentation.py` |",
        "| `configs/*.yaml` | hand-written | Documentation only. No code loads them |",
        "| `gsn/*.gsn.yaml` | hand-written | Source for the rendered GSN diagrams |",
        "| `gsn/*.svg` | generated | COMMAND: `make gsn`, or `gsn2x gsn/<file>.gsn.yaml` |",
        "",
        "The one number in the WAISE paper's case study that comes from measurement",
        "is the ensemble-disagreement AUROC at G5 evidence type (c), and the paper",
        "attributes it to the VEHITS 2026 companion study, measured on simulated",
        "ensemble outputs. Evidence types (a), (b) and (d) are marked not produced in",
        "the paper's own Figure 2(b).",
        "",
    ]
    return lines


def _position_paper_section() -> list[str]:
    return [
        "## 8. The position paper",
        "",
        "The position paper is argued at clause level. No file in `src/` supports it,",
        "and none is meant to. This is a fact about its scope, not a gap in the",
        "repository. Its claims trace to CLAUSE and to PAPER, never to COMMAND.",
        "",
        "| Claim | Kind | Source |",
        "|---|---|---|",
        "| A runtime anomaly carries no concern label | PAPER | Position paper, "
        "section on assignment and resolution; Figure 1 |",
        "| Missing step 1: no clause assigns an unlabelled anomaly to a concern | "
        "PAPER + CLAUSE | Position paper, Table 1 footnote, over ISO 21448:2022, "
        "ISO/PAS 8800:2024, ISO/SAE 21434:2021 |",
        "| Missing step 2: no clause resolves per-concern re-evaluations into one "
        "judgment | PAPER + CLAUSE | Position paper, Table 1 footnote, same three "
        "standards |",
        "| ISO 21448 defines a SOTIF argument on a field result | CLAUSE | "
        "ISO 21448:2022 Clause 13.4 |",
        "| ISO/SAE 21434 monitoring ends in risk treatment, with no re-evaluation "
        "of the cybersecurity case | CLAUSE | ISO/SAE 21434:2021, Clause 8 |",
        "| Requirements R1 to R4 that a closing method must satisfy | PAPER | "
        "Position paper, section stating the position |",
        "| No published incident is attributed to this ambiguity | PAPER | "
        "Stated by the authors in the position paper itself |",
        "",
    ]


def _known_inconsistencies_section() -> list[str]:
    return [
        "## 9. Known inconsistencies",
        "",
        "Recorded here so a reader meets them rather than discovering them alone.",
        "",
        "**DP-2 is typed differently in the paper's own table and prose.** Table 3",
        'tags DP-2 "S, M". The prose calls it structural in three places: the',
        'structural list "(DP-1, DP-2, DP-5)", the subsection heading "DP-2:',
        'Evidence type asymmetry at V&V (structural decision point)", and the',
        'discussion, "the evidence asymmetry at G5 (DP-2) is a structural property".',
        "The last two are camera-ready additions. The authors resolved this in favour",
        "of the prose, so the code types I-2 structural. This is an inconsistency",
        "inside the camera-ready, not a defect in this repository.",
        "",
        "**Test count.** The WAISE paper reports 193 tests. The suite has held at",
        "192 since the findings were revised from six to five, which removed one",
        "test (commit `4d782b0`), and has grown since with tests added after",
        "publication. The paper was correct when written. No test was added or",
        "removed here to make the numbers agree.",
        "",
        "**Two representations of goal sources.** `source_standards` on each goal and",
        "the claim-to-goal mapping are maintained separately. They agree everywhere",
        "except G8 and G9, where the reasons are recorded in",
        "`tests/test_representation_consistency.py` and enforced there.",
        "",
        "**Architecture substitution.** The WAISE paper names SECOND as the",
        "case-study architecture. The measured results in `data/empirical_results/`",
        "use PointPillars. Both are OpenPCDet voxel single-stage detectors. The",
        "substitution is stated in that directory's README and not in the paper.",
        "Neither paper cites those files.",
        "",
    ]


def build_index() -> str:
    registry = StandardsRegistry()
    catalogue = DecisionPointCatalogue()
    gaps = GapClassification()

    lines: list[str] = []
    lines += _header()
    lines += _standards_section(registry)
    lines += _crosswalk_section(catalogue, gaps)
    lines += _goals_section(registry)
    lines += _clause_section(registry)
    lines += _findings_section(gaps)
    lines += _decision_points_section(catalogue)
    lines += _artefacts_section()
    lines += _position_paper_section()
    lines += _known_inconsistencies_section()
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the traceability index.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the committed index differs from the generated one.",
    )
    args = parser.parse_args()

    content = build_index()

    if args.check:
        if not os.path.exists(OUTPUT_PATH):
            print("TRACEABILITY.md is missing. Run: python -m src.results.traceability_index")
            return 1
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            current = handle.read()
        if current != content:
            print("TRACEABILITY.md is out of date. Regenerate it.")
            return 1
        print("TRACEABILITY.md is up to date.")
        return 0

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    print(f"Wrote {OUTPUT_PATH} ({len(content.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

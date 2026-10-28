"""Generate TRACEABILITY.md, the index of where every number, table, figure and
statement in this repository comes from.

Every number, table, figure and non-obvious statement in this repository traces
to one or more of three source types, and the index says which:

  PAPER     a passage in one of the two papers, cited by section, table or figure
  CLAUSE    a clause in a named edition of a named standard
  COMMAND   a command in this repository that regenerates the artefact

Anything that traces to none of the three does not belong in the repository.
Known discrepancies between the camera-ready papers and this repository are
recorded in ERRATA.md; the index points there instead of restating them.

Table and figure numbers of the WAISE paper follow the published paper: Fig. 1
(the integrated GSN pattern, panels (a) and (b)), Table 2 (goals), Table 4
(decision points) and Table 5 (findings). The position paper's table is
Table I.

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
from src.analysis.findings import GapClassification
from src.gsn.annex_b_base import compute_extension_delta
from src.gsn.integrated_pattern import build_integrated_gsn
from src.standards.registry import StandardsRegistry

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_PATH = os.path.join(REPO_ROOT, "TRACEABILITY.md")

WAISE_DOI = "https://doi.org/10.1007/978-3-032-35506-5_55"

GENERATE_ALL = "python -m src.results.generate_all --seed 42 --scenes 50 --output output"


def _header() -> list[str]:
    return [
        "# Traceability Index",
        "",
        "Where every number, table, figure and statement in this repository comes",
        "from.",
        "",
        "Each row names its source type. A row may cite more than one, written for",
        "example PAPER + CLAUSE:",
        "",
        "| Source type | Meaning |",
        "|---|---|",
        "| **PAPER** | A passage in one of the two papers, cited by section, table or figure. |",
        "| **CLAUSE** | A clause in a named edition of a named standard. |",
        "| **COMMAND** | A command in this repository that regenerates the row's artefact. |",
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
        "The two papers, both by Milin Patel and Rolf Jung:",
        "",
        '- The WAISE paper: "Integrating Cybersecurity Into the AI Safety Assurance',
        "  Argument: A GSN Pattern for AI-Based Perception Components in Highly",
        '  Automated Driving". In: SAFECOMP 2026 Workshops (WAISE), LNCS, Springer,',
        f"  pp. 763-779. It covers design time. [doi:10.1007/978-3-032-35506-5_55]({WAISE_DOI}).",
        '- The position paper: "Operational Safety and Cybersecurity Assurance of',
        '  AI-Based Perception in Highly Automated Driving", SAFECOMP 2026, to appear.',
        "  It covers operation.",
        "",
        "Table and figure numbers of the WAISE paper follow the published paper:",
        "Fig. 1 is the integrated GSN pattern, with (a) the top two levels and (b) G5",
        "expanded; Table 2 lists the goals; Table 4 lists the decision points; Table 5",
        "lists the findings. The position paper's table is Table I.",
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
        "The four normative standards are the ones counted when this index says how",
        'many standards meet at a goal, and by any claim in the papers about "all',
        'four standards". ISO/IEC TR 5469 is an informative technical report and is',
        "excluded from those counts.",
        "",
    ]
    return lines


def _crosswalk_section(catalogue: DecisionPointCatalogue, gaps: GapClassification) -> list[str]:
    lines = [
        "## 2. Identifier crosswalk, paper to code",
        "",
        "The papers and the code name the same objects differently.",
        "",
        "| Paper | Code | Description in the code | Where in the code |",
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
            f"`src/analysis/findings.py` |"
        )
    lines += [
        "",
        'The paper calls DP-N "decision points" and F-N "integration-induced',
        'findings and open methodological problems". The code calls them',
        "inconsistencies (`I-N`) and gaps (`Gap-N`). The numbers correspond exactly;",
        "only the prefixes differ.",
        "",
        "The code's identifiers predate the camera-ready papers; where descriptions",
        "differ, the papers' terms are authoritative: decision point (DP-N) and",
        "finding (F-N), with the titles in Tables 4 and 5 of the WAISE paper.",
        "",
    ]
    return lines


def _goals_section(registry: StandardsRegistry) -> list[str]:
    gsn = build_integrated_gsn()
    normative_ids = [s.standard_id for s in registry.normative_standards]
    lines = [
        "## 3. Goals of the integrated pattern",
        "",
        f"PAPER: Table 2 and Fig. 1 of the WAISE paper. COMMAND: `{GENERATE_ALL}`",
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
        "G5 is the goal where all four normative standards contribute claims (WAISE",
        "paper, Section 4.2). The paper's headline result, the evidence asymmetry",
        "(DP-2), sits there. The repository checks that G5 is the only such goal,",
        "from both of its representations of goal sources, in",
        "`tests/test_representation_consistency.py`.",
        "",
        "The two representations, `source_standards` on each goal and the",
        "claim-to-goal mapping, are maintained separately. They agree everywhere",
        "except G8 and G9, where the reasons are recorded in",
        "`tests/test_representation_consistency.py` and enforced there.",
        "",
    ]
    lines += _extension_delta_lines()
    return lines


def _extension_delta_lines() -> list[str]:
    """The 6-to-9 extension, computed from the base and integrated builders."""
    delta = compute_extension_delta()
    lines = [
        "### From the six Annex B goals to the nine integrated goals",
        "",
        f"The pattern extends the {delta['base_goal_count']}-goal "
        f"{delta['base_pattern']} base "
        f"({', '.join(delta['base_goal_ids'])}) to "
        f"{delta['integrated_goal_count']} goals. The three added goals and the",
        "standards each draws on:",
        "",
        "| Added goal | Standards |",
        "|---|---|",
    ]
    for gid in delta["goals_added"]:
        stds = delta["added_goal_standards"][gid]
        lines.append(f"| {gid} | {', '.join(stds) if stds else '(undeveloped, no source)'} |")
    lines += [
        "",
        "Retained goals gain claims beyond the ISO/PAS 8800 base:",
        "",
    ]
    for gid, stds in delta["augmentation_of_retained_goals"].items():
        note = ", ".join(stds) if stds else "unchanged"
        lines.append(f"- {gid}: {note}")
    lines += [
        "",
        "G1 gains its two standards through its contexts (ASIL, TARA) and the",
        "reformulated top claim rather than through added evidence. Computed",
        "by `src/gsn/annex_b_base.py` from the base and integrated builders, and",
        "checked by `tests/test_base_pattern.py`.",
        "",
    ]
    return lines


def _clause_section(registry: StandardsRegistry) -> list[str]:
    lines = [
        "## 4. Clause to node index",
        "",
        "Every extracted claim, the clause it comes from, and the node it supports.",
        "This is the machine-readable traceability the WAISE paper refers to in",
        "Section 4. The same rows are exported for loading as",
        "`docs/traceability.json` and `docs/traceability.csv`, by",
        "`python -m src.results.traceability_export`.",
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
        "PAPER: Table 5 of the WAISE paper. Lifecycle phases follow",
        "that table.",
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
        "is derived there too, from a premise the module states explicitly and does",
        "not prove. F-1, F-2 and F-5 are asserted, and that module says so.",
        "",
    ]
    return lines


def _decision_points_section(catalogue: DecisionPointCatalogue) -> list[str]:
    stats = catalogue.summary_statistics()
    lines = [
        "## 6. Decision points",
        "",
        "PAPER: Table 4 of the WAISE paper.",
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
        "Each artefact carries one of five provenance labels:",
        "",
        "| Label | Meaning |",
        "|---|---|",
        "| argued | The method and the argument, as the WAISE paper describes them, encoded in `src/` and written out in `gsn/` |",
        "| hand-written | Files written by hand that no command regenerates: `gsn/*.gsn.yaml`, `data/case_study_parameters/`, `data/standards_reference/` |",
        "| generated | Written by a command from the code; a test or `make verify-refs` fails if a committed copy is out of date |",
        "| seeded | Generated from a fixed random seed (42); illustrations, not measurements |",
        "| measured | From trained models, outside this repository |",
        "",
        "The position paper's claims are made at clause level and produce no",
        "artefact; Section 8 traces them.",
        "",
        "| Artefact | Provenance | Source |",
        "|---|---|---|",
        "| `src/` | argued | The five-step method: standards, claims, goals, decision points, findings |",
        f"| `output/analysis_results.json` | generated | COMMAND: `{GENERATE_ALL}` |",
        f"| `output/csv/*` | generated | COMMAND: `{GENERATE_ALL}` |",
        f"| `output/latex/*.tex` | generated | COMMAND: `{GENERATE_ALL}` |",
        f"| `output/figures/*` | generated | COMMAND: `{GENERATE_ALL}` |",
        "| `docs/figures/*.png` | generated; `weather_heatmap.png` seeded, seed 42 | COMMAND: as above. See `docs/figures/README.md` |",
        "| `data/synthetic_illustrations/*` | seeded, seed 42 | COMMAND: as above. Not measurements. See that directory's README |",
        "| `data/empirical_results/*` | measured | Trained PointPillars ensemble, external to this repository. Cited by neither paper. See that directory's README |",
        "| `data/case_study_parameters/*.yaml` | hand-written | Documentation only. Checked against `src/` by `tests/test_config_documentation.py` |",
        "| `data/standards_reference/*.yaml` | hand-written | Documentation only. No module in `src/` loads them; `tests/test_config_documentation.py` checks part of `case_study.yaml`. See that directory's README |",
        "| `gsn/*.gsn.yaml` | hand-written | The argument in YAML; source for the rendered GSN diagrams |",
        "| `gsn/*.svg` | generated | COMMAND: `make gsn`, or `gsn2x gsn/<file>.gsn.yaml` |",
        "",
        "The WAISE paper reports two results for its case study, both for G5",
        "evidence type (c): an AUROC of 0.982 for geometric ensemble disagreement as the",
        "uncertainty indicator, and a three-indicator acceptance gate that retains",
        "22.0 % of detections with no false acceptances observed in the retained",
        "sample. The paper attributes both to the VEHITS 2026 companion study,",
        "measured on simulated ensemble outputs (WAISE paper, Section 5.1). Evidence",
        "types (a), (b) and (d) are marked not produced in Fig. 1(b) of the WAISE",
        "paper.",
        "",
        "The WAISE paper names SECOND as the case-study architecture. The measured",
        "results in `data/empirical_results/` use PointPillars. Both are single-stage",
        "LiDAR detectors in OpenPCDet: SECOND is voxel-based, PointPillars",
        "pillar-based. The substitution is stated in that directory's README and not",
        "in the paper. Neither paper cites those files.",
        "",
    ]
    return lines


def _position_paper_section() -> list[str]:
    return [
        "## 8. The position paper",
        "",
        "The position paper is argued at clause level. No file in `src/` supports it,",
        "and none is meant to. Its claims trace to CLAUSE and to PAPER, never to",
        "COMMAND.",
        "",
        "| Claim | Source type | Source |",
        "|---|---|---|",
        "| A runtime anomaly carries no concern label | PAPER | Position paper, "
        "Section I (Introduction); Fig. 1 |",
        "| Missing step 1: no clause assigns an unlabelled anomaly to a concern | "
        "PAPER + CLAUSE | Position paper, last row of Table I, over ISO 21448:2022, "
        "ISO/PAS 8800:2024, ISO/SAE 21434:2021 |",
        "| Missing step 2: no clause resolves per-concern re-evaluations into one "
        "judgement | PAPER + CLAUSE | Position paper, last row of Table I, same three "
        "standards |",
        "| ISO 21448 defines a SOTIF argument on a field result | CLAUSE | "
        "ISO 21448:2022 Clause 13.4 |",
        "| ISO/SAE 21434 monitoring ends in risk treatment, with no re-evaluation "
        "of the cybersecurity case | CLAUSE | ISO/SAE 21434:2021, Clause 8 |",
        "| Requirements R1 to R4 that a closing method must satisfy | PAPER | "
        "Position paper, Section V (The Position) |",
        "| The authors are aware of no published incident that attributes a "
        "deployed automated-driving failure to this ambiguity | PAPER | "
        "Position paper, Section I (Introduction) |",
        "",
    ]


def _known_discrepancies_section() -> list[str]:
    return [
        "## 9. Known discrepancies with the papers",
        "",
        "Discrepancies between the camera-ready papers and this repository are",
        "recorded in [ERRATA.md](ERRATA.md). Each entry states what the paper says,",
        "what the repository holds, and whether the difference is resolved.",
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
    lines += _known_discrepancies_section()
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

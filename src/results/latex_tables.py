"""LaTeX tables generated from the analysis code.

Each table is written to output/latex/ under a file name that says what it
holds. The names carry no table numbers, so that they cannot be confused with
the table numbers of the WAISE paper (Table 1 related work, Table 2 the goals,
Table 3 the DP-5 worked example, Table 4 the decision points, Table 5 the
findings). Where a generated table has a counterpart in the paper, it is named:
- standards_overview.tex: standards and their role in the integration
  (repository analysis, not in either paper)
- coverage_matrix.tex: clause coverage matrix across the six lifecycle phases
  (repository analysis, not in either paper)
- goals.tex: integrated GSN goal structure (counterpart: WAISE Table 2)
- goal_density.tex: documents contributing claims per goal (repository
  analysis, not in either paper)
- decision_points.tex: decision-point catalogue (counterpart: WAISE Table 4)
- findings.tex: findings in the paper's two categories (counterpart: WAISE
  Table 5)
- evidence_types_g5.tex: the evidence types (a) to (d) at G5 (repository
  analysis, not in either paper; WAISE Fig. 1(b) shows the four evidence types)
- weather_illustration.tex: synthetic weather-grid illustration, triggering
  against non-triggering conditions (seeded, no detector, no CARLA; not a
  measurement and not in either paper)

All tables use the booktabs package.
"""

from __future__ import annotations

import os
from typing import Optional

from src.standards.base import LifecyclePhase, InconsistencyType
from src.standards.registry import StandardsRegistry


def _latex_escape(text: str) -> str:
    """Escape special LaTeX characters in free text."""
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("_", r"\_"),
        ("#", r"\#"),
        ("—", "---"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text
from src.gsn.integrated_pattern import build_integrated_gsn
from src.gsn.model import Goal, GoalStatus
from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.findings import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis


def generate_standards_overview_table() -> str:
    """Standards and their role in the integration (standards_overview.tex)."""
    registry = StandardsRegistry()
    roles = {
        "ISO26262": "ASIL framework, HW metrics, change management",
        "ISO21448": "Four-area model, triggering conditions, acceptance criteria",
        "ISO21434": "TARA, cybersecurity case, safety--cybersecurity bridge [RQ-15-06]",
        "ISOPAS8800": "Base GSN pattern (Annex~B), AI-specific V\\&V, monitoring",
        "TR5469": "Supplementary guidance (informative, non-normative)",
    }

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Applicable standards for the AI-based perception component.}",
        r"\label{tab:standards}",
        r"\small",
        r"\begin{tabular}{@{}llp{5.8cm}@{}}",
        r"\toprule",
        r"\textbf{Standard} & \textbf{Year} & \textbf{Role in Integration} \\",
        r"\midrule",
    ]

    display_names = {
        "ISO26262": "ISO~26262",
        "ISO21448": "ISO~21448",
        "ISO21434": "ISO/SAE~21434",
        "ISOPAS8800": "ISO/PAS~8800",
        "TR5469": "ISO/IEC~TR~5469",
    }

    for std in registry.all_standards:
        name = display_names.get(std.standard_id, std.standard_id)
        role = roles.get(std.standard_id, "")
        lines.append(f"  {name} & {std.year} & {role} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def generate_coverage_matrix_table() -> str:
    """Clause coverage matrix across the six lifecycle phases (coverage_matrix.tex)."""
    registry = StandardsRegistry()
    matrix = registry.compute_coverage_matrix()

    display_names = {
        "ISO26262": "ISO~26262",
        "ISO21448": "ISO~21448",
        "ISO21434": "ISO/SAE~21434",
        "ISOPAS8800": "ISO/PAS~8800",
        "TR5469": "ISO/IEC~TR~5469",
    }

    phase_short = {
        "Concept / Requirements": "Concept",
        "Design / Training": "Design",
        "Verification & Validation": "V\\&V",
        "Integration / Deployment": "Integr.",
        "Operation / Monitoring": "Oper.",
        "Modification / Re-assurance": "Modif.",
    }

    phases = [p.display_name for p in LifecyclePhase]

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Clause applicability per lifecycle phase. Each cell shows the"
        r" number of applicable clauses from that standard in the given phase."
        r" Dashes indicate no applicable clauses.}",
        r"\label{tab:coverage}",
        r"\small",
        r"\begin{tabular}{@{}l" + "r" * len(phases) + r"@{}}",
        r"\toprule",
    ]

    header = r"\textbf{Standard}"
    for p in phases:
        header += f" & \\textbf{{{phase_short[p]}}}"
    header += r" \\"
    lines.append(header)
    lines.append(r"\midrule")

    for std_id, phase_counts in matrix.items():
        name = display_names.get(std_id, std_id)
        row = f"  {name}"
        for p in phases:
            count = phase_counts.get(p, 0)
            row += f" & {count if count > 0 else '---'}"
        row += r" \\"
        lines.append(row)

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def generate_goals_table() -> str:
    """Integrated GSN goal structure with origin and contributing documents (goals.tex)."""
    gsn = build_integrated_gsn()

    goal_data = [
        ("G1", "Integrated safety \\& cybersecurity requirements satisfied",
         "Reformulated from Annex~B G1", "3 + 2 context"),
        ("G2", "Specification sufficient across all domains",
         "Retained (augmented)", "3"),
        ("G3", "Data sets sufficient", "Retained", "1"),
        ("G4", "Design sufficient across all domains",
         "Retained (augmented)", "3"),
        ("G5", "V\\&V evidence sufficient", "Retained (augmented)",
         "\\textbf{4 (all)}"),
        ("G6", "Monitoring sufficient across all domains",
         "Retained (augmented)", "3"),
        ("G7", "SOTIF residual risk acceptable", "\\textbf{Added}", "1"),
        ("G8", "Cybersecurity risks managed", "\\textbf{Added}", "2"),
        ("G9", "Modification assurance", "\\textbf{Added} (undeveloped)", "0"),
    ]

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Integrated GSN goal structure. G1 is reformulated from"
        r" ISO/PAS~8800 Annex~B G1, G2 to G6 are retained, G7 and G8 are"
        r" added, and G9 is added and undeveloped, because no single standard"
        r" prescribes the complete re-assurance workflow for a modified AI"
        r" model.}",
        r"\label{tab:gsn-goals}",
        r"\small",
        r"\begin{tabular}{@{}clll@{}}",
        r"\toprule",
        r"\textbf{Goal} & \textbf{Claim} & \textbf{Origin} & "
        r"\textbf{Std.\ Active} \\",
        r"\midrule",
    ]

    for gid, claim, origin, active in goal_data:
        lines.append(f"  {gid} & {claim} & {origin} & {active} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def generate_goal_density_table() -> str:
    """Documents contributing claims per goal (goal_density.tex)."""
    registry = StandardsRegistry()
    density = registry.compute_goal_density()

    display_names = {
        "ISO26262": "26262",
        "ISO21448": "21448",
        "ISO21434": "21434",
        "ISOPAS8800": "8800",
        "TR5469": "5469",
    }
    std_ids = list(registry.standards.keys())

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Standard coverage density per goal node."
        r" \checkmark\ indicates the standard contributes at least one"
        r" normative claim to the goal. The rightmost column counts"
        r" contributing standards. G5 is the only node where all four"
        r" normative standards contribute.}",
        r"\label{tab:goal-density}",
        r"\small",
        r"\begin{tabular}{@{}l" + "c" * len(std_ids) + r"r@{}}",
        r"\toprule",
    ]

    header = r"\textbf{Goal}"
    for sid in std_ids:
        header += f" & \\textbf{{{display_names[sid]}}}"
    header += r" & \textbf{$\Sigma$} \\"
    lines.append(header)
    lines.append(r"\midrule")

    for gid in ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]:
        if gid not in density:
            continue
        stds = density[gid]
        row = f"  {gid}"
        active = 0
        for sid in std_ids:
            if stds.get(sid, False):
                row += r" & \checkmark"
                active += 1
            else:
                row += " & ---"
        row += f" & {active} \\\\"
        lines.append(row)

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def generate_decision_points_table() -> str:
    """Decision-point catalogue (decision_points.tex; WAISE Table 4: DP-1 to DP-7)."""
    catalogue = DecisionPointCatalogue()

    type_map = {
        InconsistencyType.STRUCTURAL: "S",
        InconsistencyType.TERMINOLOGICAL: "T",
        InconsistencyType.METHODOLOGICAL: "M",
    }

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Decision points at junction points of the integrated GSN,"
        r" generated from the analysis code. Types: S = structural,"
        r" T = terminological, M = methodological. Identifiers I-1 to I-7"
        r" are the code's names for the decision points the paper calls"
        r" DP-1 to DP-7.}",
        r"\label{tab:gen-decision-points}",
        r"\small",
        r"\begin{tabular}{@{}clclp{6.5cm}@{}}",
        r"\toprule",
        r"\textbf{ID} & \textbf{Type} & \textbf{Node} & "
        r"\textbf{Standards} & \textbf{Description} \\",
        r"\midrule",
    ]

    for inc in catalogue.inconsistencies:
        tl = type_map[inc.inconsistency_type]
        nodes = ", ".join(inc.gsn_nodes)
        stds = ", ".join(inc.standards_involved)
        desc = _latex_escape(inc.description)
        lines.append(f"  {inc.inconsistency_id} & {tl} & {nodes} & {stds} & {desc} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table*}",
    ]
    return "\n".join(lines)


def generate_findings_table() -> str:
    """Findings in the paper's two categories (findings.tex; WAISE Table 5: F-1 to F-5)."""
    gaps_cls = GapClassification()

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Findings by category and lifecycle phase, generated from the"
        r" analysis code. II = integration-induced finding, OM = open"
        r" methodological problem. Identifiers Gap-1 to Gap-5 are the code's"
        r" names for the findings the paper calls F-1 to F-5.}",
        r"\label{tab:gen-findings}",
        r"\small",
        r"\begin{tabular}{@{}cllp{6.5cm}@{}}",
        r"\toprule",
        r"\textbf{ID} & \textbf{Category} & \textbf{Phase} & "
        r"\textbf{Description} \\",
        r"\midrule",
    ]

    for gap in gaps_cls.gaps:
        category = "II" if gap.integration_induced else "OM"
        # Escape the phase. "Verification & Validation" contains an ampersand,
        # which unescaped opened an extra column and stopped the table compiling.
        # Use the paper's findings-table wording, which carries every phase for the
        # finding rather than only the primary one.
        phase = _latex_escape(gap.lifecycle_phase_label)
        desc = _latex_escape(gap.description)
        lines.append(f"  {gap.gap_id} & {category} & {phase} & {desc} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table*}",
    ]
    return "\n".join(lines)


def generate_evidence_types_table() -> str:
    """The evidence types (a) to (d) at G5 (evidence_types_g5.tex)."""
    analysis = EvidenceConvergenceAnalysis()

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Evidence types (a) to (d) at G5, the V\&V goal. They are"
        r" disjoint by design, each on its own measurement scale, and no"
        r" standard prescribes how they combine into a single sufficiency"
        r" claim at G5 (decision point DP-2).}",
        r"\label{tab:evidence-types}",
        r"\small",
        r"\begin{tabular}{@{}lllll@{}}",
        r"\toprule",
        r"\textbf{Evidence Type} & \textbf{Standard} & "
        r"\textbf{What Measured} & \textbf{How Produced} & "
        r"\textbf{Scale} \\",
        r"\midrule",
    ]

    for et in analysis.evidence_types:
        lines.append(
            f"  {et.name} & {et.standard} & {et.what_measured} & "
            f"{et.how_produced} & {et.scale} \\\\"
        )

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table*}",
    ]
    return "\n".join(lines)


def generate_weather_illustration_table(eval_summary: dict) -> str:
    """Synthetic weather-grid illustration, triggering against non-triggering
    conditions (weather_illustration.tex). No detector, no CARLA."""
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Synthetic weather-grid illustration (no detector, no CARLA):"
        r" seeded values for SOTIF triggering and non-triggering weather"
        r" conditions. Not a measurement.}",
        r"\label{tab:weather-eval}",
        r"\small",
        r"\begin{tabular}{@{}lrrr@{}}",
        r"\toprule",
        r"\textbf{Category} & \textbf{Mean Recall} & "
        r"\textbf{Mean Divergence} & \textbf{FN Count} \\",
        r"\midrule",
    ]

    overall_recall = eval_summary.get("overall_mean_recall", 0.0)
    trig_recall = eval_summary.get("triggering_mean_recall", 0.0)
    non_trig_recall = eval_summary.get("non_triggering_mean_recall", 0.0)
    overall_div = eval_summary.get("overall_mean_divergence", 0.0)
    trig_div = eval_summary.get("triggering_mean_divergence", 0.0)
    non_trig_div = eval_summary.get("non_triggering_mean_divergence", 0.0)
    trig_fn = eval_summary.get("triggering_false_negatives", 0)
    non_trig_fn = eval_summary.get("non_triggering_false_negatives", 0)
    total_fn = eval_summary.get("total_false_negatives", 0)

    lines.append(
        f"  Non-triggering & {non_trig_recall:.3f} & "
        f"{non_trig_div:.3f} & {non_trig_fn} \\\\"
    )
    lines.append(
        f"  Triggering & {trig_recall:.3f} & "
        f"{trig_div:.3f} & {trig_fn} \\\\"
    )
    lines.append(r"\midrule")
    lines.append(
        f"  Overall & {overall_recall:.3f} & "
        f"{overall_div:.3f} & {total_fn} \\\\"
    )

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def generate_all_tables(
    eval_summary: Optional[dict] = None,
    output_dir: str = "output/latex",
) -> dict[str, str]:
    """Generate all LaTeX tables and save to files.

    Returns a dict mapping file name (without .tex) to LaTeX source.
    """
    os.makedirs(output_dir, exist_ok=True)

    tables = {
        "standards_overview": generate_standards_overview_table(),
        "coverage_matrix": generate_coverage_matrix_table(),
        "goals": generate_goals_table(),
        "goal_density": generate_goal_density_table(),
        "decision_points": generate_decision_points_table(),
        "findings": generate_findings_table(),
        "evidence_types_g5": generate_evidence_types_table(),
    }

    if eval_summary:
        tables["weather_illustration"] = generate_weather_illustration_table(eval_summary)

    for name, latex in tables.items():
        path = os.path.join(output_dir, f"{name}.tex")
        with open(path, "w") as f:
            f.write(latex)

    return tables

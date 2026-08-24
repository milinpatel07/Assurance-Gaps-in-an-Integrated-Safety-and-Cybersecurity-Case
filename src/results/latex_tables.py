"""LaTeX table generation for direct inclusion in scientific publications.

Generates publication-ready LaTeX tables corresponding to:
- Table 1: Standards applicability overview
- Table 2: Clause coverage matrix across lifecycle phases
- Table 3: Integrated GSN goal structure
- Table 4: Standard coverage density per goal node
- Table 5: Requirement inconsistency catalogue
- Table 6: Assurance gap classification
- Table 7: Evidence type comparison at G5
- Table 8: Weather evaluation results (triggering vs non-triggering)

All tables use the booktabs package for professional formatting.
"""

from __future__ import annotations

import os
from typing import Optional

from src.standards.base import LifecyclePhase, InconsistencyType, GapType
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
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis


def generate_table1_standards_overview() -> str:
    """Table 1: Applicable standards with scope and role in integration."""
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


def generate_table2_coverage_matrix() -> str:
    """Table 2: Clause coverage matrix across six lifecycle phases."""
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


def generate_table3_gsn_structure() -> str:
    """Table 3: Integrated GSN goal structure showing origin and active standards."""
    gsn = build_integrated_gsn()

    goal_data = [
        ("G1", "Integrated safety \\& cybersecurity requirements satisfied",
         "Retained (reformulated)", "3 + 2 context"),
        ("G2", "Specification sufficient across all domains",
         "Retained (augmented)", "3"),
        ("G3", "Data sets sufficient", "Retained", "1"),
        ("G4", "Design sufficient across all domains",
         "Retained (augmented)", "3"),
        ("G5", "V\\&V evidence sufficient", "Retained (augmented)",
         "\\textbf{4 (all)}"),
        ("G6", "Monitoring sufficient across all domains",
         "Retained (augmented)", "3"),
        ("G7", "SOTIF residual risk acceptable", "\\textbf{New}", "1"),
        ("G8", "Cybersecurity risks managed", "\\textbf{New}", "2"),
        ("G9", "Modification assurance", "\\textbf{Gap} (undeveloped)", "0"),
    ]

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Integrated GSN goal structure. The base pattern"
        r" (ISO/PAS~8800 Annex~B) defines G1--G6. G7 and G8 are new goals"
        r" introduced by the integration. G9 is identified as an undeveloped"
        r" gap.}",
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


def generate_table4_goal_density() -> str:
    """Table 4: Standard coverage density per goal node."""
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


def generate_table5_inconsistencies() -> str:
    """Table 5: decision-point catalogue (paper: DP-1 to DP-7)."""
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


def generate_table6_gaps() -> str:
    """Table 6: findings classification (paper: F-1 to F-5)."""
    gaps_cls = GapClassification()

    type_map = {
        GapType.MISSING_CLAIM: "MC",
        GapType.MISSING_EVIDENCE: "ME",
        GapType.UNRESOLVED_INCONSISTENCY: "UI",
    }

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Findings classified by type and lifecycle phase,"
        r" generated from the analysis code. Types: MC = missing claim,"
        r" ME = missing evidence, UI = unresolved inconsistency."
        r" Findings marked with $\dagger$ are integration-induced."
        r" Identifiers Gap-1 to Gap-5 are the code's names for the findings"
        r" the paper calls F-1 to F-5. The paper's own table groups these"
        r" as integration-induced findings and open methodological problems"
        r" rather than by the three types above.}",
        r"\label{tab:gen-findings}",
        r"\small",
        r"\begin{tabular}{@{}clllp{5.5cm}@{}}",
        r"\toprule",
        r"\textbf{ID} & \textbf{Type} & \textbf{Phase} & "
        r"\textbf{Induced} & \textbf{Description} \\",
        r"\midrule",
    ]

    for gap in gaps_cls.gaps:
        tl = type_map[gap.gap_type]
        phase = gap.lifecycle_phase.display_name
        induced = r"$\dagger$" if gap.integration_induced else "---"
        desc = _latex_escape(gap.description)
        lines.append(f"  {gap.gap_id} & {tl} & {phase} & {induced} & {desc} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table*}",
    ]
    return "\n".join(lines)


def generate_table7_evidence_types() -> str:
    """Table 7: Evidence type comparison at G5."""
    analysis = EvidenceConvergenceAnalysis()

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Evidence types converging at G5 (V\&V sufficiency)."
        r" Each evidence type differs in measurement target, production"
        r" method, and scale. No standard defines a combination rule.}",
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


def generate_table8_weather_evaluation(eval_summary: dict) -> str:
    """Table 8: Weather evaluation results comparing triggering vs non-triggering."""
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Detection performance under SOTIF triggering vs."
        r" non-triggering weather conditions (CARLA evaluation,"
        r" 25 weather combinations, 50 scenes each).}",
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

    Returns a dict mapping table name to LaTeX source.
    """
    os.makedirs(output_dir, exist_ok=True)

    tables = {
        "table1_standards": generate_table1_standards_overview(),
        "table2_coverage": generate_table2_coverage_matrix(),
        "table3_gsn_goals": generate_table3_gsn_structure(),
        "table4_density": generate_table4_goal_density(),
        "table5_inconsistencies": generate_table5_inconsistencies(),
        "table6_gaps": generate_table6_gaps(),
        "table7_evidence": generate_table7_evidence_types(),
    }

    if eval_summary:
        tables["table8_weather"] = generate_table8_weather_evaluation(eval_summary)

    for name, latex in tables.items():
        path = os.path.join(output_dir, f"{name}.tex")
        with open(path, "w") as f:
            f.write(latex)

    return tables

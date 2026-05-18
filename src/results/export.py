"""Result export in multiple formats for reproducibility and analysis.

Generates:
- JSON: complete structured results for programmatic consumption
- CSV: tabular data for spreadsheet analysis
- Plain text: human-readable summary report
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime

import numpy as np

from src.standards.base import LifecyclePhase, InconsistencyType, GapType
from src.standards.registry import StandardsRegistry
from src.gsn.integrated_pattern import build_integrated_gsn
from src.gsn.model import Goal, GoalStatus
from src.analysis.inconsistencies import InconsistencyCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis
from src.evaluation.carla_evaluator import FullEvaluationResult
from src.analysis.completeness import check_gsn_completeness
from src.analysis.counterfactual import CounterfactualAnalysis


def _json_default(obj):
    """Custom JSON serializer for numpy types and enums."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if hasattr(obj, "value"):
        return obj.value
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def export_json(
    registry: StandardsRegistry,
    eval_result: FullEvaluationResult,
    output_dir: str = "output",
) -> str:
    """Export complete analysis results as structured JSON."""
    gsn = build_integrated_gsn()
    catalogue = InconsistencyCatalogue()
    gaps = GapClassification()
    convergence = EvidenceConvergenceAnalysis()

    results = {
        "metadata": {
            "title": (
                "Assurance Gaps in an Integrated Safety and Cybersecurity Case "
                "for an AI-Based Perception Component in Highly Automated Driving"
            ),
            "authors": ["Milin Patel", "Rolf Jung"],
            "affiliation": "Kempten University of Applied Sciences",
            "venue": "SafeComp 2026 WAISE Workshop",
            "generated": datetime.now().isoformat(),
            "methodology": "Five-step constructive integration",
            "base_pattern": "ISO/PAS 8800:2024 Annex B",
            "case_study": "LiDAR-based 3D object detection (SECOND + deep ensemble)",
            "random_seed": 42,
        },
        "standards": {
            std.standard_id: {
                "name": std.full_name,
                "year": std.year,
                "scope": std.scope,
                "num_clauses": len(std.clauses),
                "num_claims": len(std.claims),
            }
            for std in registry.all_standards
        },
        "coverage_matrix": registry.compute_coverage_matrix(),
        "goal_density": {
            goal: {std: active for std, active in stds.items()}
            for goal, stds in registry.compute_goal_density().items()
        },
        "gsn_statistics": gsn.compute_statistics(),
        "gsn_goals": [
            {
                "id": g.element_id,
                "text": g.text,
                "origin": g.origin,
                "status": g.status.value,
                "source_standards": g.source_standards,
                "clause_references": g.clause_references,
                "num_solutions": len(g.supported_by),
            }
            for g in gsn.get_goals()
        ],
        "inconsistencies": {
            "summary": catalogue.summary_statistics(),
            "items": [
                {
                    "id": i.inconsistency_id,
                    "description": i.description,
                    "type": i.inconsistency_type.value,
                    "standards": i.standards_involved,
                    "clause_references": i.clause_references,
                    "gsn_nodes": i.gsn_nodes,
                    "consequence": i.consequence,
                }
                for i in catalogue.inconsistencies
            ],
        },
        "gaps": {
            "summary": gaps.summary_statistics(),
            "items": [
                {
                    "id": g.gap_id,
                    "description": g.description,
                    "type": g.gap_type.value,
                    "lifecycle_phase": g.lifecycle_phase.value,
                    "partial_coverage": g.partial_coverage,
                    "integration_induced": g.integration_induced,
                }
                for g in gaps.gaps
            ],
        },
        "evidence_convergence": {
            "evidence_types": [
                {
                    "name": et.name,
                    "standard": et.standard,
                    "clause": et.clause,
                    "what_measured": et.what_measured,
                    "how_produced": et.how_produced,
                    "scale": et.scale,
                    "case_study_instance": et.case_study_instance,
                }
                for et in convergence.evidence_types
            ],
            "failure_event": {
                "description": convergence.failure_event.description,
                "paths": [
                    {
                        "standard": p.standard,
                        "method": p.analysis_method,
                        "output": p.output,
                        "evidence_type": p.evidence_type,
                        "gsn_node": p.gsn_node,
                    }
                    for p in convergence.failure_event.analysis_paths
                ],
            },
        },
        "completeness": {
            "is_complete": check_gsn_completeness().is_complete,
            "total_claims": check_gsn_completeness().total_claims,
            "mapped_claims": check_gsn_completeness().mapped_claims,
            "explanation": check_gsn_completeness().explanation,
        },
        "counterfactual": {
            "gap_visibility_matrix": CounterfactualAnalysis().get_gap_visibility_matrix(),
            "num_perspectives": len(CounterfactualAnalysis().perspectives),
        },
        "evaluation": eval_result.compute_summary(),
        "evaluation_per_weather": [
            {
                "weather": wr.weather.name,
                "rain_mm_h": wr.weather.rain_intensity,
                "visibility_m": wr.weather.fog_density,
                "sotif_triggering": wr.weather.sotif_triggering,
                "num_scenes": wr.num_scenes,
                "mean_recall": round(wr.mean_recall, 4),
                "mean_precision": round(wr.mean_precision, 4),
                "mean_divergence": round(wr.mean_divergence, 4),
                "total_false_negatives": wr.total_false_negatives,
            }
            for wr in eval_result.weather_results
        ],
    }

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "analysis_results.json")
    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=_json_default)

    return path


def export_csv_tables(
    registry: StandardsRegistry,
    eval_result: FullEvaluationResult,
    output_dir: str = "output/csv",
) -> list[str]:
    """Export tabular results as CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    files = []

    # Coverage matrix
    matrix = registry.compute_coverage_matrix()
    phases = [p.display_name for p in LifecyclePhase]
    path = os.path.join(output_dir, "coverage_matrix.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Standard"] + phases)
        for std_id, phase_counts in matrix.items():
            row = [std_id] + [phase_counts.get(p, 0) for p in phases]
            writer.writerow(row)
    files.append(path)

    # Goal density
    density = registry.compute_goal_density()
    std_ids = list(registry.standards.keys())
    path = os.path.join(output_dir, "goal_density.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Goal"] + std_ids + ["Active"])
        for gid in ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]:
            if gid not in density:
                continue
            stds = density[gid]
            row = [gid]
            active = 0
            for sid in std_ids:
                val = stds.get(sid, False)
                row.append("Y" if val else "N")
                if val:
                    active += 1
            row.append(active)
            writer.writerow(row)
    files.append(path)

    # Inconsistencies
    catalogue = InconsistencyCatalogue()
    path = os.path.join(output_dir, "inconsistencies.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID", "Type", "Description", "Standards",
            "GSN Nodes", "Clause References", "Consequence",
        ])
        for inc in catalogue.inconsistencies:
            writer.writerow([
                inc.inconsistency_id,
                inc.inconsistency_type.value,
                inc.description,
                "; ".join(inc.standards_involved),
                "; ".join(inc.gsn_nodes),
                "; ".join(inc.clause_references),
                inc.consequence,
            ])
    files.append(path)

    # Gaps
    gaps = GapClassification()
    path = os.path.join(output_dir, "gaps.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID", "Type", "Description", "Lifecycle Phase",
            "Integration Induced", "Partial Coverage",
        ])
        for gap in gaps.gaps:
            writer.writerow([
                gap.gap_id,
                gap.gap_type.value,
                gap.description,
                gap.lifecycle_phase.display_name,
                "Yes" if gap.integration_induced else "No",
                "; ".join(gap.partial_coverage),
            ])
    files.append(path)

    # Counterfactual gap visibility matrix
    counterfactual = CounterfactualAnalysis()
    gap_matrix = counterfactual.get_gap_visibility_matrix()
    path = os.path.join(output_dir, "counterfactual_gap_visibility.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        all_gaps = ["Gap-1", "Gap-2", "Gap-3", "Gap-4", "Gap-5"]
        writer.writerow(["Standard"] + all_gaps)
        for std_id, vis in gap_matrix.items():
            row = [std_id] + ["Yes" if vis.get(g, False) else "No" for g in all_gaps]
            writer.writerow(row)
    files.append(path)

    # Weather evaluation per condition
    path = os.path.join(output_dir, "weather_evaluation.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Weather", "Rain (mm/h)", "Visibility (m)",
            "SOTIF Triggering", "Scenes", "Mean Recall",
            "Mean Precision", "Mean Divergence", "False Negatives",
        ])
        for wr in eval_result.weather_results:
            writer.writerow([
                wr.weather.name,
                wr.weather.rain_intensity,
                wr.weather.fog_density,
                "Yes" if wr.weather.sotif_triggering else "No",
                wr.num_scenes,
                f"{wr.mean_recall:.4f}",
                f"{wr.mean_precision:.4f}",
                f"{wr.mean_divergence:.4f}",
                wr.total_false_negatives,
            ])
    files.append(path)

    return files


def export_summary_report(
    registry: StandardsRegistry,
    eval_result: FullEvaluationResult,
    output_dir: str = "output",
) -> str:
    """Export a plain-text summary report."""
    gsn = build_integrated_gsn()
    catalogue = InconsistencyCatalogue()
    gaps = GapClassification()
    convergence = EvidenceConvergenceAnalysis()
    eval_summary = eval_result.compute_summary()

    lines = []
    lines.append("=" * 80)
    lines.append("ANALYSIS RESULTS SUMMARY")
    lines.append("Assurance Gaps in an Integrated Safety and Cybersecurity Case")
    lines.append("for an AI-Based Perception Component in Highly Automated Driving")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Random seed: 42")
    lines.append("")

    # Standards summary
    lines.append("-" * 60)
    lines.append("STANDARDS FRAMEWORK")
    lines.append("-" * 60)
    total_claims = sum(len(s.claims) for s in registry.all_standards)
    total_clauses = sum(len(s.clauses) for s in registry.all_standards)
    lines.append(f"Standards analysed:    {len(registry.all_standards)}")
    lines.append(f"Total clauses:         {total_clauses}")
    lines.append(f"Total claims:          {total_claims}")
    lines.append("")

    # GSN summary
    lines.append("-" * 60)
    lines.append("INTEGRATED GSN")
    lines.append("-" * 60)
    stats = gsn.compute_statistics()
    for key, value in stats.items():
        lines.append(f"  {key}: {value}")
    lines.append("")

    # Inconsistencies
    lines.append("-" * 60)
    lines.append("REQUIREMENT INCONSISTENCIES")
    lines.append("-" * 60)
    inc_stats = catalogue.summary_statistics()
    lines.append(f"  Total: {inc_stats['total']}")
    lines.append(f"  Structural:      {inc_stats['structural']}")
    lines.append(f"  Terminological:  {inc_stats['terminological']}")
    lines.append(f"  Methodological:  {inc_stats['methodological']}")
    lines.append("")
    for inc in catalogue.inconsistencies:
        lines.append(f"  {inc.inconsistency_id}: {inc.description}")
    lines.append("")

    # Gaps
    lines.append("-" * 60)
    lines.append("ASSURANCE GAPS")
    lines.append("-" * 60)
    gap_stats = gaps.summary_statistics()
    lines.append(f"  Total: {gap_stats['total']}")
    lines.append(f"  Missing claim:               {gap_stats['missing_claim']}")
    lines.append(f"  Missing evidence:            {gap_stats['missing_evidence']}")
    lines.append(f"  Unresolved inconsistency:    {gap_stats['unresolved_inconsistency']}")
    lines.append(f"  Integration-induced:         {gap_stats['integration_induced']}")
    lines.append("")
    for gap in gaps.gaps:
        ind = " [INTEGRATION-INDUCED]" if gap.integration_induced else ""
        lines.append(f"  {gap.gap_id}: {gap.description}{ind}")
    lines.append("")

    # Evidence convergence
    lines.append("-" * 60)
    lines.append("EVIDENCE CONVERGENCE AT G5 (CENTRAL FINDING)")
    lines.append("-" * 60)
    lines.append("Four evidence types converge at the V&V goal:")
    for i, et in enumerate(convergence.evidence_types, 1):
        lines.append(f"  [{i}] {et.name} ({et.standard})")
        lines.append(f"      Scale: {et.scale}")
    lines.append("")
    lines.append("Finding: No standard defines how to combine these four")
    lines.append("evidence types into a single sufficiency claim at G5.")
    lines.append("")

    # Completeness
    completeness = check_gsn_completeness()
    lines.append("-" * 60)
    lines.append("GSN COMPLETENESS CHECK")
    lines.append("-" * 60)
    lines.append(f"  Complete: {completeness.is_complete}")
    lines.append(f"  Claims mapped: {completeness.mapped_claims}/{completeness.total_claims}")
    lines.append(f"  Phases covered: {', '.join(completeness.phases_covered)}")
    if completeness.phases_uncovered:
        lines.append(f"  Phases uncovered: {', '.join(completeness.phases_uncovered)}")
    lines.append(f"  {completeness.explanation}")
    lines.append("")

    # Counterfactual
    counterfactual = CounterfactualAnalysis()
    gap_matrix = counterfactual.get_gap_visibility_matrix()
    lines.append("-" * 60)
    lines.append("COUNTERFACTUAL ANALYSIS")
    lines.append("-" * 60)
    lines.append("Gap visibility from each standard's perspective:")
    for std_id, gaps_visible in gap_matrix.items():
        visible = [g for g, v in gaps_visible.items() if v]
        lines.append(f"  {std_id:15s}: {', '.join(visible) if visible else '(none)'}")
    lines.append("")
    lines.append("Key finding: Gap-3 and Gap-4 are invisible from any single standard.")
    lines.append("They emerge only when standards are integrated into one GSN.")
    lines.append("")

    # Evaluation
    lines.append("-" * 60)
    lines.append("CARLA EVALUATION RESULTS")
    lines.append("-" * 60)
    lines.append(f"  Weather conditions:        {eval_summary['total_weather_conditions']}")
    lines.append(f"  Triggering conditions:     {eval_summary['triggering_conditions']}")
    lines.append(f"  Overall mean recall:       {eval_summary['overall_mean_recall']:.4f}")
    lines.append(f"  Triggering mean recall:    {eval_summary['triggering_mean_recall']:.4f}")
    lines.append(f"  Non-triggering recall:     {eval_summary['non_triggering_mean_recall']:.4f}")
    lines.append(f"  Overall mean divergence:   {eval_summary['overall_mean_divergence']:.4f}")
    lines.append(f"  Triggering divergence:     {eval_summary['triggering_mean_divergence']:.4f}")
    lines.append(f"  Non-triggering divergence: {eval_summary['non_triggering_mean_divergence']:.4f}")
    lines.append(f"  Total false negatives:     {eval_summary['total_false_negatives']}")
    lines.append("")

    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "summary_report.txt")
    with open(path, "w") as f:
        f.write("\n".join(lines))

    return path

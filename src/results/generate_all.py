"""Master results generator — produces all outputs for the publication.

This script runs the complete five-step methodology and generates:
1. Structured JSON results (output/analysis_results.json)
2. CSV tables for each analysis component (output/csv/)
3. LaTeX tables ready for paper inclusion (output/latex/)
4. Visualization figures (output/figures/)
5. GSN diagram in DOT and rendered formats (output/figures/)
6. Plain-text summary report (output/summary_report.txt)

Usage:
    python -m src.results.generate_all [--seed 42] [--scenes 50] [--output output]

All results are deterministic given the same seed.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np

from src.standards.registry import StandardsRegistry
from src.gsn.integrated_pattern import build_integrated_gsn
from src.analysis.inconsistencies import InconsistencyCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis
from src.evaluation.carla_evaluator import generate_synthetic_evaluation
from src.evaluation.weather_conditions import generate_weather_grid, compute_triggering_coverage
from src.results.latex_tables import generate_all_tables
from src.results.export import export_json, export_csv_tables, export_summary_report
from src.analysis.completeness import check_gsn_completeness
from src.analysis.counterfactual import CounterfactualAnalysis
from src.analysis.sensitivity import run_sensitivity_analysis


def run_step1(registry: StandardsRegistry) -> dict:
    """Step 1: Claim extraction from standard clauses."""
    total_claims = 0
    total_clauses = 0
    per_standard = {}

    for std in registry.all_standards:
        n_claims = len(std.claims)
        n_clauses = len(std.clauses)
        total_claims += n_claims
        total_clauses += n_clauses
        per_standard[std.standard_id] = {
            "name": std.full_name,
            "year": std.year,
            "clauses": n_clauses,
            "claims": n_claims,
        }

    return {
        "total_standards": len(registry.all_standards),
        "total_clauses": total_clauses,
        "total_claims": total_claims,
        "per_standard": per_standard,
    }


def run_step2(registry: StandardsRegistry) -> dict:
    """Step 2: Lifecycle-phase mapping."""
    matrix = registry.compute_coverage_matrix()
    density = registry.compute_goal_density()
    counts = registry.count_standards_per_goal()

    return {
        "coverage_matrix": matrix,
        "goal_density": density,
        "standards_per_goal": counts,
    }


def run_step3() -> dict:
    """Step 3: GSN construction (extend Annex B)."""
    gsn = build_integrated_gsn()
    stats = gsn.compute_statistics()
    junction_points = [
        {
            "id": jp.element_id,
            "standards": jp.source_standards,
            "count": len(jp.source_standards),
        }
        for jp in gsn.get_junction_points()
    ]
    undeveloped = [
        {"id": ug.element_id, "text": ug.text}
        for ug in gsn.get_undeveloped_goals()
    ]

    return {
        "statistics": stats,
        "junction_points": junction_points,
        "undeveloped_goals": undeveloped,
    }


def run_step4() -> dict:
    """Step 4: Junction-point analysis (inconsistencies)."""
    catalogue = InconsistencyCatalogue()
    return {
        "summary": catalogue.summary_statistics(),
        "items": [
            {
                "id": i.inconsistency_id,
                "type": i.inconsistency_type.value,
                "description": i.description,
                "standards": i.standards_involved,
                "gsn_nodes": i.gsn_nodes,
            }
            for i in catalogue.inconsistencies
        ],
    }


def run_step5() -> dict:
    """Step 5: Gap identification and classification."""
    gaps = GapClassification()
    return {
        "summary": gaps.summary_statistics(),
        "items": [
            {
                "id": g.gap_id,
                "type": g.gap_type.value,
                "description": g.description,
                "phase": g.lifecycle_phase.display_name,
                "integration_induced": g.integration_induced,
            }
            for g in gaps.gaps
        ],
    }


def run_evidence_convergence() -> dict:
    """Evidence convergence analysis at G5."""
    analysis = EvidenceConvergenceAnalysis()
    return {
        "num_evidence_types": len(analysis.evidence_types),
        "num_analysis_paths": len(analysis.failure_event.analysis_paths),
        "evidence_types": [et.name for et in analysis.evidence_types],
    }


def generate_figures(registry, gsn, eval_result, output_dir):
    """Generate all visualization figures."""
    fig_dir = os.path.join(output_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)

    # GSN diagram
    from src.visualization.gsn_renderer import render_gsn_to_dot, save_gsn_diagram

    dot_source = render_gsn_to_dot(gsn)
    dot_path = os.path.join(fig_dir, "integrated_gsn.dot")
    with open(dot_path, "w") as f:
        f.write(dot_source)
    try:
        save_gsn_diagram(gsn, os.path.join(fig_dir, "integrated_gsn"), fmt="png")
        save_gsn_diagram(gsn, os.path.join(fig_dir, "integrated_gsn"), fmt="pdf")
    except Exception as e:
        print(f"  Warning: Graphviz rendering failed ({e}); DOT file saved.")

    # Coverage plots
    from src.visualization.coverage_plots import (
        plot_coverage_heatmap,
        plot_goal_density,
        plot_evidence_convergence,
        plot_weather_evaluation,
        plot_weather_heatmap,
        plot_inconsistency_distribution,
        plot_gap_lifecycle_distribution,
    )

    matrix = registry.compute_coverage_matrix()
    density = registry.compute_goal_density()
    eval_summary = eval_result.compute_summary()

    plot_coverage_heatmap(matrix, os.path.join(fig_dir, "coverage_heatmap.png"))
    plot_coverage_heatmap(matrix, os.path.join(fig_dir, "coverage_heatmap.pdf"))
    plot_goal_density(density, os.path.join(fig_dir, "goal_density.png"))
    plot_goal_density(density, os.path.join(fig_dir, "goal_density.pdf"))
    plot_evidence_convergence(os.path.join(fig_dir, "evidence_convergence.png"))
    plot_evidence_convergence(os.path.join(fig_dir, "evidence_convergence.pdf"))
    plot_weather_evaluation(eval_summary, os.path.join(fig_dir, "weather_evaluation.png"))
    plot_weather_evaluation(eval_summary, os.path.join(fig_dir, "weather_evaluation.pdf"))
    plot_weather_heatmap(
        eval_result.weather_results,
        os.path.join(fig_dir, "weather_heatmap.png"),
    )
    plot_weather_heatmap(
        eval_result.weather_results,
        os.path.join(fig_dir, "weather_heatmap.pdf"),
    )
    plot_inconsistency_distribution(
        os.path.join(fig_dir, "inconsistency_distribution.png"),
    )
    plot_inconsistency_distribution(
        os.path.join(fig_dir, "inconsistency_distribution.pdf"),
    )
    plot_gap_lifecycle_distribution(
        os.path.join(fig_dir, "gap_distribution.png"),
    )
    plot_gap_lifecycle_distribution(
        os.path.join(fig_dir, "gap_distribution.pdf"),
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate all results for the publication"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for deterministic evaluation (default: 42)",
    )
    parser.add_argument(
        "--scenes", type=int, default=50,
        help="Number of scenes per weather condition (default: 50)",
    )
    parser.add_argument(
        "--output", type=str, default="output",
        help="Output directory (default: output)",
    )
    args = parser.parse_args()

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 72)
    print("GENERATING ALL RESULTS")
    print("Assurance Gaps in an Integrated Safety and Cybersecurity Case")
    print("=" * 72)
    print(f"  Seed:              {args.seed}")
    print(f"  Scenes/weather:    {args.scenes}")
    print(f"  Output directory:  {output_dir}")
    print()

    t0 = time.time()

    # ── Step 1: Claim extraction ──────────────────────────────────────
    print("[Step 1] Extracting claims from standard clauses...")
    registry = StandardsRegistry()
    step1 = run_step1(registry)
    print(f"  {step1['total_claims']} claims from {step1['total_clauses']} clauses")

    # ── Step 2: Lifecycle mapping ─────────────────────────────────────
    print("[Step 2] Mapping claims to lifecycle phases...")
    step2 = run_step2(registry)
    print(f"  Coverage matrix: {len(step2['coverage_matrix'])} standards x 6 phases")

    # ── Step 3: GSN construction ──────────────────────────────────────
    print("[Step 3] Constructing integrated GSN...")
    gsn = build_integrated_gsn()
    step3 = run_step3()
    stats = step3["statistics"]
    print(f"  {stats['goals']} goals, {stats['solutions']} solutions, "
          f"{stats['junction_points']} junction points")

    # ── Step 4: Inconsistency analysis ────────────────────────────────
    print("[Step 4] Analysing junction-point inconsistencies...")
    step4 = run_step4()
    print(f"  {step4['summary']['total']} inconsistencies "
          f"({step4['summary']['structural']}S, "
          f"{step4['summary']['terminological']}T, "
          f"{step4['summary']['methodological']}M)")

    # ── Step 5: Gap identification ────────────────────────────────────
    print("[Step 5] Identifying assurance gaps...")
    step5 = run_step5()
    print(f"  {step5['summary']['total']} gaps "
          f"({step5['summary']['integration_induced']} integration-induced)")

    # ── Evidence convergence ──────────────────────────────────────────
    print("[Analysis] Evidence convergence at G5...")
    convergence = run_evidence_convergence()
    print(f"  {convergence['num_evidence_types']} evidence types, "
          f"{convergence['num_analysis_paths']} analysis paths")

    # ── Completeness check ─────────────────────────────────────────
    print("[Analysis] GSN completeness check...")
    completeness = check_gsn_completeness()
    print(f"  Complete: {completeness.is_complete}, "
          f"{completeness.mapped_claims}/{completeness.total_claims} claims mapped")

    # ── Counterfactual analysis ────────────────────────────────────
    print("[Analysis] Counterfactual analysis (per-standard perspective)...")
    counterfactual = CounterfactualAnalysis()
    gap_matrix = counterfactual.get_gap_visibility_matrix()
    integration_only = sum(
        1 for g in ["Gap-3", "Gap-4"]
        if all(not gap_matrix[s].get(g, False) for s in gap_matrix if s != "Integrated")
    )
    print(f"  {len(counterfactual.perspectives)} standard perspectives, "
          f"{integration_only} gaps visible only through integration")

    # ── CARLA evaluation ──────────────────────────────────────────────
    print(f"[Evaluation] Running synthetic CARLA evaluation "
          f"({args.scenes} scenes/weather)...")
    eval_result = generate_synthetic_evaluation(
        num_scenes_per_weather=args.scenes,
        seed=args.seed,
    )
    eval_summary = eval_result.compute_summary()
    print(f"  {eval_summary['total_weather_conditions']} conditions, "
          f"recall: {eval_summary['overall_mean_recall']:.4f}")

    # ── Sensitivity analysis ──────────────────────────────────────────
    print("[Analysis] Running sensitivity analysis (5 seeds)...")
    sensitivity = run_sensitivity_analysis(scenes_per_weather=args.scenes)
    sens_summary = sensitivity.summary()
    print(f"  Recall gap: {sens_summary['recall_gap_mean']:.4f} "
          f"+/- {sens_summary['recall_gap_std']:.4f} across {sens_summary['num_seeds']} seeds")

    # ── Export results ────────────────────────────────────────────────
    print()
    print("[Export] Generating output files...")

    # JSON
    json_path = export_json(registry, eval_result, output_dir)
    print(f"  JSON:    {json_path}")

    # CSV
    csv_files = export_csv_tables(registry, eval_result,
                                   os.path.join(output_dir, "csv"))
    for cf in csv_files:
        print(f"  CSV:     {cf}")

    # LaTeX tables
    tables = generate_all_tables(eval_summary,
                                  os.path.join(output_dir, "latex"))
    for name in tables:
        print(f"  LaTeX:   output/latex/{name}.tex")

    # Sensitivity results
    sens_path = os.path.join(output_dir, "csv", "sensitivity_analysis.csv")
    os.makedirs(os.path.join(output_dir, "csv"), exist_ok=True)
    import csv
    with open(sens_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Seed", "Overall Recall", "Triggering Recall",
                          "Non-Triggering Recall", "Triggering Divergence", "Recall Gap"])
        for i, seed in enumerate(sensitivity.seeds):
            writer.writerow([
                seed,
                f"{sensitivity.overall_recall[i]:.4f}",
                f"{sensitivity.triggering_recall[i]:.4f}",
                f"{sensitivity.non_triggering_recall[i]:.4f}",
                f"{sensitivity.triggering_divergence[i]:.4f}",
                f"{sensitivity.recall_gap[i]:.4f}",
            ])
        writer.writerow([])
        writer.writerow(["Mean", f"{sens_summary['overall_recall_mean']:.4f}",
                          f"{sens_summary['triggering_recall_mean']:.4f}",
                          f"{sens_summary['non_triggering_recall_mean']:.4f}",
                          f"{sens_summary['triggering_divergence_mean']:.4f}",
                          f"{sens_summary['recall_gap_mean']:.4f}"])
        writer.writerow(["Std", f"{sens_summary['overall_recall_std']:.4f}",
                          f"{sens_summary['triggering_recall_std']:.4f}",
                          f"{sens_summary['non_triggering_recall_std']:.4f}",
                          f"{sens_summary['triggering_divergence_std']:.4f}",
                          f"{sens_summary['recall_gap_std']:.4f}"])
    print(f"  CSV:     {sens_path}")

    # Summary report
    report_path = export_summary_report(registry, eval_result, output_dir)
    print(f"  Report:  {report_path}")

    # Figures
    print()
    print("[Figures] Generating visualizations...")
    generate_figures(registry, gsn, eval_result, output_dir)
    print("  Saved to output/figures/")

    elapsed = time.time() - t0
    print()
    print("=" * 72)
    print(f"ALL RESULTS GENERATED in {elapsed:.1f}s")
    print(f"Output directory: {output_dir}/")
    print("=" * 72)

    # Print key findings
    print()
    print("KEY FINDINGS:")
    print(f"  - {step4['summary']['total']} requirement inconsistencies "
          f"({step4['summary']['structural']} structural, "
          f"{step4['summary']['terminological']} terminological, "
          f"{step4['summary']['methodological']} methodological)")
    print(f"  - {step5['summary']['total']} assurance gaps "
          f"({step5['summary']['integration_induced']} integration-induced)")
    print(f"  - Central finding: evidence type asymmetry at G5 (I-2)")
    print(f"  - G5 is the only node where all 4 normative standards contribute")
    print(f"  - Triggering condition recall: {eval_summary['triggering_mean_recall']:.4f} "
          f"vs non-triggering: {eval_summary['non_triggering_mean_recall']:.4f}")
    print(f"  - Triggering divergence: {eval_summary['triggering_mean_divergence']:.4f} "
          f"(elevated uncertainty under adverse weather)")


if __name__ == "__main__":
    main()

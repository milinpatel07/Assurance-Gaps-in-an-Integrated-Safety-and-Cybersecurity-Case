"""Main analysis runner — executes the complete five-step methodology.

This script runs the full constructive integration process:
Step 1: Claim extraction from standard clauses
Step 2: Lifecycle-phase mapping
Step 3: GSN construction (extend Annex B)
Step 4: Junction-point analysis (inconsistencies)
Step 5: Gap identification and classification

It also runs the CARLA evaluation (synthetic) and generates visualizations.
"""

from __future__ import annotations

import os
import json

from src.standards.registry import StandardsRegistry
from src.gsn.integrated_pattern import build_integrated_gsn
from src.analysis.inconsistencies import InconsistencyCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis
from src.evaluation.carla_evaluator import generate_synthetic_illustration
from src.evaluation.weather_conditions import generate_weather_grid, compute_triggering_coverage


def run_step1_claim_extraction():
    """Step 1: Extract claims from all applicable standards."""
    print("\n" + "=" * 80)
    print("STEP 1: CLAIM EXTRACTION FROM STANDARD CLAUSES")
    print("=" * 80)

    registry = StandardsRegistry()
    total_claims = 0

    for std in registry.all_standards:
        claims = std.claims
        total_claims += len(claims)
        print(f"\n  {std.standard_id} ({std.year}):")
        print(f"    Clauses: {len(std.clauses)}")
        print(f"    Claims extracted: {len(claims)}")
        for c in claims:
            print(f"      [{c.claim_id}] -> {c.gsn_goal}: {c.text[:70]}...")

    print(f"\n  TOTAL CLAIMS EXTRACTED: {total_claims}")
    return registry


def run_step2_lifecycle_mapping(registry: StandardsRegistry):
    """Step 2: Map claims to lifecycle phases."""
    print("\n" + "=" * 80)
    print("STEP 2: LIFECYCLE-PHASE MAPPING")
    print("=" * 80)
    registry.print_coverage_summary()


def run_step3_gsn_construction():
    """Step 3: Construct the integrated GSN pattern."""
    print("\n" + "=" * 80)
    print("STEP 3: GSN CONSTRUCTION (Extend Annex B)")
    print("=" * 80)

    gsn = build_integrated_gsn()
    stats = gsn.compute_statistics()

    print(f"\n  Integrated GSN Statistics:")
    for key, value in stats.items():
        print(f"    {key}: {value}")

    print(f"\n  Junction Points (claims from 2+ standards):")
    for jp in gsn.get_junction_points():
        stds = ", ".join(jp.source_standards)
        print(f"    {jp.element_id}: [{stds}]")

    print(f"\n  Undeveloped Goals (gaps):")
    for ug in gsn.get_undeveloped_goals():
        print(f"    {ug.element_id}: {ug.text[:60]}...")

    print(f"\n  Argument Structure:")
    gsn.print_structure("G1")

    return gsn


def run_step4_inconsistency_analysis():
    """Step 4: Junction-point analysis for inconsistencies."""
    print("\n" + "=" * 80)
    print("STEP 4: JUNCTION-POINT ANALYSIS (Inconsistencies)")
    print("=" * 80)

    catalogue = InconsistencyCatalogue()
    catalogue.print_catalogue()

    stats = catalogue.summary_statistics()
    print(f"\n  Summary: {stats}")

    return catalogue


def run_step5_gap_identification():
    """Step 5: Gap identification and classification."""
    print("\n" + "=" * 80)
    print("STEP 5: GAP IDENTIFICATION AND CLASSIFICATION")
    print("=" * 80)

    gaps = GapClassification()
    gaps.print_classification()

    stats = gaps.summary_statistics()
    print(f"\n  Summary: {stats}")

    return gaps


def run_evidence_convergence_analysis():
    """Analyse the evidence convergence at G5."""
    print("\n" + "=" * 80)
    print("EVIDENCE CONVERGENCE ANALYSIS (Central Finding)")
    print("=" * 80)

    analysis = EvidenceConvergenceAnalysis()
    analysis.print_analysis()
    return analysis


def run_carla_evaluation():
    """Run the synthetic CARLA evaluation."""
    print("\n" + "=" * 80)
    print("CARLA EVALUATION (Synthetic Demonstration)")
    print("=" * 80)

    # Generate weather grid
    conditions = generate_weather_grid()
    trig_coverage = compute_triggering_coverage(conditions)
    print(f"\n  Weather grid: {len(conditions)} conditions")
    print(f"  Triggering condition coverage: {trig_coverage}")

    # Run synthetic evaluation
    result = generate_synthetic_illustration(num_scenes_per_weather=10)
    summary = result.compute_summary()

    print(f"\n  Evaluation Summary:")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"    {key}: {value:.4f}")
        else:
            print(f"    {key}: {value}")

    return result


def generate_visualizations(registry, gsn, eval_result):
    """Generate all visualization outputs."""
    print("\n" + "=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)

    os.makedirs("output", exist_ok=True)

    # GSN diagram
    from src.visualization.gsn_renderer import render_gsn_to_dot, save_gsn_diagram

    dot_source = render_gsn_to_dot(gsn)
    with open("output/integrated_gsn.dot", "w") as f:
        f.write(dot_source)
    print("  Saved: output/integrated_gsn.dot")

    save_gsn_diagram(gsn, "output/integrated_gsn", fmt="png")

    # Coverage plots
    from src.visualization.coverage_plots import (
        plot_coverage_heatmap,
        plot_goal_density,
        plot_evidence_convergence,
        plot_weather_evaluation,
    )

    matrix = registry.compute_coverage_matrix()
    plot_coverage_heatmap(matrix, "output/coverage_heatmap.png")

    density = registry.compute_goal_density()
    plot_goal_density(density, "output/goal_density.png")

    plot_evidence_convergence("output/evidence_convergence.png")

    eval_summary = eval_result.compute_summary()
    plot_weather_evaluation(eval_summary, "output/weather_evaluation.png")


def export_results(registry, gsn, catalogue, gaps, eval_result):
    """Export analysis results as JSON for reproducibility."""
    os.makedirs("output", exist_ok=True)

    results = {
        "methodology": "Constructive integration (5 steps)",
        "base_pattern": "ISO/PAS 8800 Annex B",
        "case_study": "LiDAR-based 3D object detection (SECOND + deep ensemble)",
        "gsn_statistics": gsn.compute_statistics(),
        "inconsistencies": {
            "summary": catalogue.summary_statistics(),
            "items": [
                {
                    "id": i.inconsistency_id,
                    "description": i.description,
                    "type": i.inconsistency_type.value,
                    "standards": i.standards_involved,
                    "gsn_nodes": i.gsn_nodes,
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
                    "integration_induced": g.integration_induced,
                }
                for g in gaps.gaps
            ],
        },
        "evaluation_summary": eval_result.compute_summary(),
        "goal_coverage": {
            goal: {std: active for std, active in stds.items()}
            for goal, stds in registry.compute_goal_density().items()
        },
    }

    # Convert numpy types for JSON serialization
    def convert(obj):
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    with open("output/analysis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=convert)
    print("  Saved: output/analysis_results.json")


def main():
    """Execute the complete analysis pipeline."""
    print("=" * 80)
    print("ASSURANCE GAPS IN AN INTEGRATED SAFETY AND CYBERSECURITY CASE")
    print("FOR AN AI-BASED PERCEPTION COMPONENT IN HIGHLY AUTOMATED DRIVING")
    print("=" * 80)
    print("Implementation of the five-step constructive integration methodology")
    print()

    # Steps 1-2: Standards framework
    registry = run_step1_claim_extraction()
    run_step2_lifecycle_mapping(registry)

    # Step 3: GSN construction
    gsn = run_step3_gsn_construction()

    # Steps 4-5: Analysis
    catalogue = run_step4_inconsistency_analysis()
    gaps = run_step5_gap_identification()

    # Evidence convergence (central finding)
    run_evidence_convergence_analysis()

    # CARLA evaluation
    eval_result = run_carla_evaluation()

    # Visualizations and export
    generate_visualizations(registry, gsn, eval_result)
    export_results(registry, gsn, catalogue, gaps, eval_result)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nKey findings:")
    print("  - 7 requirement inconsistencies (3 structural, 2 terminological, 2 methodological)")
    print("  - 5 assurance gaps (2 integration-induced)")
    print("  - Central finding: evidence type asymmetry at G5 (I-2)")
    print("  - G5 is the only node where ALL four standards contribute claims")
    print("\nOutput files in: output/")


if __name__ == "__main__":
    main()

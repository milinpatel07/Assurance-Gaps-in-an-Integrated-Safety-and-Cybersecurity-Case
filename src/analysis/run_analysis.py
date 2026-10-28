"""Main analysis runner: executes the five-step method of the WAISE paper.

Steps (WAISE paper, Section 3.2):
Step 1: Claim extraction from standard clauses
Step 2: Lifecycle-phase mapping
Step 3: GSN construction (extend ISO/PAS 8800 Annex B)
Step 4: Junction-point analysis, output the decision points (WAISE Table 4)
Step 5: Finding identification, output the findings in two categories
        (WAISE Table 5)

It also prints the synthetic weather-grid illustration (no detector, no CARLA)
and generates the figures. Graphviz is optional: without it the GSN diagram is
saved as DOT only.
"""

from __future__ import annotations

import os
import json

from src.standards.base import InconsistencyType, LifecyclePhase
from src.standards.registry import StandardsRegistry
from src.gsn.integrated_pattern import build_integrated_gsn
from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.findings import GapClassification
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

    # One row per phase and one column per document, so that the long phase
    # names stay readable instead of running into each other as column headers.
    matrix = registry.compute_coverage_matrix()
    std_ids = list(matrix.keys())
    phases = [p.display_name for p in LifecyclePhase]
    phase_width = max(len(p) for p in phases) + 2
    col_width = max(len(s) for s in std_ids) + 2

    print("\n  Clauses per lifecycle phase (--- = none)")
    header = f"  {'Lifecycle phase':<{phase_width}}" + "".join(
        f"{sid:>{col_width}}" for sid in std_ids
    )
    print(header)
    print("  " + "-" * (len(header) - 2))
    for phase in phases:
        row = f"  {phase:<{phase_width}}"
        for sid in std_ids:
            count = matrix[sid].get(phase, 0)
            row += f"{(count if count > 0 else '---'):>{col_width}}"
        print(row)

    density = registry.compute_goal_density()
    density_ids = list(registry.standards.keys())
    print("\n  Documents contributing claims per goal "
          "(repository analysis, not in either paper; Y = contributes)")
    header = f"  {'Goal':<8}" + "".join(f"{sid:>{col_width}}" for sid in density_ids)
    header += f"{'Count':>{col_width}}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for goal, stds in density.items():
        active = sum(1 for sid in density_ids if stds.get(sid, False))
        row = f"  {goal:<8}" + "".join(
            f"{('Y' if stds.get(sid, False) else '---'):>{col_width}}"
            for sid in density_ids
        )
        row += f"{active:>{col_width}}"
        print(row)


def run_step3_gsn_construction():
    """Step 3: Construct the integrated GSN pattern."""
    print("\n" + "=" * 80)
    print("STEP 3: GSN CONSTRUCTION (Extend Annex B)")
    print("=" * 80)

    gsn = build_integrated_gsn()
    stats = gsn.compute_statistics()

    print(f"\n  Integrated GSN statistics:")
    for key, value in stats.items():
        print(f"    {key}: {value}")

    print(f"\n  Junction points (goals where claims from two or more standards meet):")
    for jp in gsn.get_junction_points():
        stds = ", ".join(jp.source_standards)
        print(f"    {jp.element_id}: [{stds}]")

    print(f"\n  Undeveloped goals:")
    for ug in gsn.get_undeveloped_goals():
        print(f"    {ug.element_id}: {ug.text[:60]}...")

    print(f"\n  Argument structure:")
    gsn.print_structure("G1")

    return gsn


def _dp_id(inconsistency_id: str) -> str:
    """Paper id DP-n for the code id I-n."""
    return inconsistency_id.replace("I-", "DP-", 1)


def _finding_id(gap_id: str) -> str:
    """Paper id F-n for the code id Gap-n."""
    return gap_id.replace("Gap-", "F-", 1)


def run_step4_inconsistency_analysis():
    """Step 4: junction-point analysis, output the decision points."""
    print("\n" + "=" * 80)
    print("STEP 4: JUNCTION-POINT ANALYSIS (DECISION POINTS, WAISE TABLE 4)")
    print("=" * 80)
    print("T = terminological, M = methodological, S = structural")

    catalogue = DecisionPointCatalogue()
    type_labels = {
        InconsistencyType.TERMINOLOGICAL: "T",
        InconsistencyType.METHODOLOGICAL: "M",
        InconsistencyType.STRUCTURAL: "S",
    }
    for dp in catalogue.inconsistencies:
        tl = type_labels[dp.inconsistency_type]
        print(f"\n{_dp_id(dp.inconsistency_id)} ({dp.inconsistency_id}) [{tl}]: "
              f"{dp.description}")
        print(f"  Standards: {', '.join(dp.standards_involved)}")
        print(f"  GSN nodes: {', '.join(dp.gsn_nodes)}")
        print("  Clauses:")
        for ref in dp.clause_references:
            print(f"    - {ref}")
        print(f"  Consequence: {dp.consequence}")

    stats = catalogue.summary_statistics()
    print(f"\n  Decision points: {stats['total']} "
          f"({stats['structural']} structural, "
          f"{stats['terminological']} terminological, "
          f"{stats['methodological']} methodological)")

    return catalogue


def run_step5_gap_identification():
    """Step 5: finding identification, in the paper's two categories."""
    print("\n" + "=" * 80)
    print("STEP 5: FINDING IDENTIFICATION")
    print("=" * 80)

    gaps = GapClassification()
    gaps.print_classification()

    induced = [_finding_id(g.gap_id) for g in gaps.gaps if g.integration_induced]
    open_problems = [_finding_id(g.gap_id) for g in gaps.gaps if not g.integration_induced]
    print(f"\n  Findings: {len(gaps.gaps)}")
    print(f"  Integration-induced findings (II): {len(induced)} ({', '.join(induced)})")
    print(f"  Open methodological problems (OM): {len(open_problems)} "
          f"({', '.join(open_problems)})")

    return gaps


def run_evidence_convergence_analysis():
    """Print the evidence types (a) to (d) at G5 (decision point DP-2)."""
    print()
    analysis = EvidenceConvergenceAnalysis()
    analysis.print_analysis()
    return analysis


def run_carla_evaluation():
    """Print the synthetic weather-grid illustration (no detector, no CARLA)."""
    print("\n" + "=" * 80)
    print("SYNTHETIC WEATHER-GRID ILLUSTRATION (NO DETECTOR, NO CARLA)")
    print("=" * 80)
    print("  Seeded; not a measurement. See data/synthetic_illustrations/README.md.")

    # Generate weather grid
    conditions = generate_weather_grid()
    trig_coverage = compute_triggering_coverage(conditions)
    print(f"\n  Weather grid: {len(conditions)} conditions")
    print(f"  Triggering condition coverage: {trig_coverage}")

    result = generate_synthetic_illustration(num_scenes_per_weather=10)
    summary = result.compute_summary()

    print(f"\n  Illustration summary:")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"    {key}: {value:.4f}")
        else:
            print(f"    {key}: {value}")

    return result


def generate_visualizations(registry, gsn, eval_result):
    """Generate all figures."""
    print("\n" + "=" * 80)
    print("GENERATING FIGURES")
    print("=" * 80)

    os.makedirs("output", exist_ok=True)

    # GSN diagram
    from src.visualization.gsn_renderer import render_gsn_to_dot, save_gsn_diagram

    dot_source = render_gsn_to_dot(gsn)
    with open("output/integrated_gsn.dot", "w") as f:
        f.write(dot_source)
    print("  Saved: output/integrated_gsn.dot")

    # Graphviz is optional. Without the dot executable, keep the DOT file and
    # carry on, as generate_all does.
    try:
        save_gsn_diagram(gsn, "output/integrated_gsn", fmt="png")
    except Exception as e:
        print(f"  Warning: Graphviz rendering failed ({e}); DOT file saved.")

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
                    "category": (
                        "integration-induced finding"
                        if g.integration_induced
                        else "open methodological problem"
                    ),
                    "lifecycle_phase": g.lifecycle_phase.value,
                    # Every phase the paper lists, not only the primary one.
                    "lifecycle_phases": [p.value for p in g.lifecycle_phases],
                    "lifecycle_phase_label": g.lifecycle_phase_label,
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
    print("The five-step constructive integration method of the WAISE paper")
    print()

    # Steps 1-2: Standards framework
    registry = run_step1_claim_extraction()
    run_step2_lifecycle_mapping(registry)

    # Step 3: GSN construction
    gsn = run_step3_gsn_construction()

    # Steps 4-5: Analysis
    catalogue = run_step4_inconsistency_analysis()
    gaps = run_step5_gap_identification()

    # Evidence types at G5 (decision point DP-2)
    run_evidence_convergence_analysis()

    # Synthetic weather-grid illustration (no detector, no CARLA)
    eval_result = run_carla_evaluation()

    # Figures and export
    generate_visualizations(registry, gsn, eval_result)
    export_results(registry, gsn, catalogue, gaps, eval_result)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    dp_stats = catalogue.summary_statistics()
    induced = [_finding_id(g.gap_id) for g in gaps.gaps if g.integration_induced]
    open_problems = [_finding_id(g.gap_id) for g in gaps.gaps if not g.integration_induced]
    print("\nSummary:")
    print(f"  - {dp_stats['total']} decision points, WAISE Table 4 "
          f"({dp_stats['structural']} structural, "
          f"{dp_stats['terminological']} terminological, "
          f"{dp_stats['methodological']} methodological)")
    print(f"  - {len(gaps.gaps)} findings, WAISE Table 5: "
          f"{len(induced)} integration-induced ({', '.join(induced)}), "
          f"{len(open_problems)} open methodological problems "
          f"({', '.join(open_problems)})")
    print("  - DP-2 (I-2): at G5, the V&V goal, the evidence types are disjoint "
          "by design, each on its own measurement scale, and no standard "
          "prescribes how they combine into a single sufficiency claim")
    print("  - G5 is the goal where all four standards contribute claims")
    print("\nOutput files in: output/")


if __name__ == "__main__":
    main()

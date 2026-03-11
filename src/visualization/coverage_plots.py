"""Visualization of coverage matrices, evidence convergence, and evaluation results.

Generates the plots and tables that support the paper's analysis:
- Coverage matrix heatmap (Table 2)
- Goal density table (Table 4)
- Evidence convergence diagram (Figure 4)
- Weather evaluation results
"""

from __future__ import annotations

from typing import Optional

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MPL_AVAILABLE = True
except ImportError:
    MPL_AVAILABLE = False

from src.standards.base import LifecyclePhase


def plot_coverage_heatmap(
    matrix: dict[str, dict[str, int]],
    output_path: Optional[str] = None,
) -> None:
    """Plot the clause coverage matrix as a heatmap.

    Corresponds to Table 2 in the paper.
    """
    if not MPL_AVAILABLE:
        print("matplotlib not available; skipping heatmap")
        return

    standards = list(matrix.keys())
    phases = [p.display_name for p in LifecyclePhase]

    data = np.zeros((len(standards), len(phases)))
    for i, std in enumerate(standards):
        for j, phase in enumerate(phases):
            data[i, j] = matrix[std].get(phase, 0)

    fig, ax = plt.subplots(figsize=(12, 5))
    im = ax.imshow(data, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(range(len(phases)))
    ax.set_xticklabels(phases, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(standards)))
    ax.set_yticklabels(standards, fontsize=9)

    # Annotate cells
    for i in range(len(standards)):
        for j in range(len(phases)):
            val = int(data[i, j])
            text = str(val) if val > 0 else "---"
            color = "white" if val > 2 else "black"
            ax.text(j, i, text, ha="center", va="center", fontsize=9, color=color)

    ax.set_title("Clause Applicability per Lifecycle Phase (Table 2)", fontsize=11)
    fig.colorbar(im, ax=ax, label="Number of applicable clauses")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved coverage heatmap to {output_path}")
    plt.close()


def plot_goal_density(
    density: dict[str, dict[str, bool]],
    output_path: Optional[str] = None,
) -> None:
    """Plot the standard coverage density per goal as a grid.

    Corresponds to Table 4 in the paper.
    """
    if not MPL_AVAILABLE:
        print("matplotlib not available; skipping density plot")
        return

    goals = [g for g in density.keys() if g != "S1"]
    standards = list(next(iter(density.values())).keys())

    data = np.zeros((len(goals), len(standards)))
    for i, goal in enumerate(goals):
        for j, std in enumerate(standards):
            data[i, j] = 1.0 if density[goal].get(std, False) else 0.0

    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(data, cmap="Blues", aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(range(len(standards)))
    ax.set_xticklabels(standards, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(goals)))
    ax.set_yticklabels(goals, fontsize=9)

    for i in range(len(goals)):
        for j in range(len(standards)):
            text = "Y" if data[i, j] > 0 else "---"
            color = "white" if data[i, j] > 0 else "gray"
            ax.text(j, i, text, ha="center", va="center", fontsize=10, color=color)

    # Add active count on the right
    for i, goal in enumerate(goals):
        active = sum(1 for v in density[goal].values() if v)
        ax.text(
            len(standards) + 0.3, i, str(active),
            ha="center", va="center", fontsize=10, fontweight="bold",
        )
    ax.text(
        len(standards) + 0.3, -0.8, "Active",
        ha="center", fontsize=9, fontweight="bold",
    )

    ax.set_title("Standard Coverage Density per Goal Node (Table 4)", fontsize=11)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved goal density plot to {output_path}")
    plt.close()


def plot_evidence_convergence(
    output_path: Optional[str] = None,
) -> None:
    """Plot the evidence convergence diagram at G5 (Figure 4).

    Shows how a single failure event (missed pedestrian detection)
    enters the integrated argument through three analysis paths.
    """
    if not MPL_AVAILABLE:
        print("matplotlib not available; skipping convergence plot")
        return

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Event box
    event_box = mpatches.FancyBboxPatch(
        (5, 8.5), 4, 1, boxstyle="round,pad=0.2",
        facecolor="#E0E0E0", edgecolor="black", linewidth=1.5,
    )
    ax.add_patch(event_box)
    ax.text(7, 9, "LiDAR detector misses\na pedestrian",
            ha="center", va="center", fontsize=10, fontweight="bold")

    # Three analysis paths
    paths = [
        {
            "x": 2, "color": "#BBDEFB", "border": "#1565C0",
            "standard": "ISO 26262",
            "method": "HARA (Part 3, Cl.6)\n-> ASIL D",
            "evidence": "MC/DC coverage\n(deterministic, binary)",
        },
        {
            "x": 7, "color": "#FFE0B2", "border": "#E65100",
            "standard": "ISO 21448",
            "method": "Triggering condition\n(Cl.9-11)",
            "evidence": "Scenario coverage +\nensemble uncertainty\n(statistical)",
        },
        {
            "x": 12, "color": "#FFCDD2", "border": "#C62828",
            "standard": "ISO/SAE 21434",
            "method": "Threat scenario\n(Cl.15)",
            "evidence": "Penetration testing\n(attack success rate)",
        },
    ]

    for p in paths:
        # Analysis method box
        method_box = mpatches.FancyBboxPatch(
            (p["x"] - 1.5, 5.5), 3, 1.5, boxstyle="round,pad=0.15",
            facecolor=p["color"], edgecolor=p["border"], linewidth=1.2,
        )
        ax.add_patch(method_box)
        ax.text(p["x"], 6.8, p["standard"], ha="center", va="center",
                fontsize=8, fontweight="bold", color=p["border"])
        ax.text(p["x"], 6.1, p["method"], ha="center", va="center", fontsize=7)

        # Evidence box
        ev_box = mpatches.FancyBboxPatch(
            (p["x"] - 1.5, 3), 3, 1.5, boxstyle="round,pad=0.15",
            facecolor=p["color"], edgecolor=p["border"], linewidth=1.0,
            linestyle="dashed",
        )
        ax.add_patch(ev_box)
        ax.text(p["x"], 3.75, p["evidence"], ha="center", va="center", fontsize=7)

        # Arrows: event -> method -> evidence -> G5
        ax.annotate("", xy=(p["x"], 7.0), xytext=(7, 8.5),
                     arrowprops=dict(arrowstyle="->", lw=1.2, color="black"))
        ax.annotate("", xy=(p["x"], 4.5), xytext=(p["x"], 5.5),
                     arrowprops=dict(arrowstyle="->", lw=1.2, color="black"))
        ax.annotate("", xy=(7, 1.8), xytext=(p["x"], 3.0),
                     arrowprops=dict(arrowstyle="->", lw=1.2, color="black"))

    # G5 box
    g5_box = mpatches.FancyBboxPatch(
        (5, 0.8), 4, 1, boxstyle="round,pad=0.2",
        facecolor="#E8E8E8", edgecolor="black", linewidth=2.0,
    )
    ax.add_patch(g5_box)
    ax.text(7, 1.3, "G5: V&V sufficiency", ha="center", va="center",
            fontsize=11, fontweight="bold")

    # Key finding text
    ax.text(7, 0.2,
            "No standard defines how to combine these three evidence types.",
            ha="center", va="center", fontsize=9, fontstyle="italic",
            color="#C62828")

    ax.set_title("Evidence Convergence at G5 for a Single Failure Event (Figure 4)",
                 fontsize=12, fontweight="bold", pad=20)

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved convergence diagram to {output_path}")
    plt.close()


def plot_weather_evaluation(
    summary: dict,
    output_path: Optional[str] = None,
) -> None:
    """Plot weather evaluation summary comparing triggering vs non-triggering."""
    if not MPL_AVAILABLE:
        print("matplotlib not available; skipping weather plot")
        return

    categories = ["Non-triggering", "Triggering"]
    recall = [summary["non_triggering_mean_recall"], summary["triggering_mean_recall"]]
    divergence = [
        summary.get("non_triggering_mean_divergence", 0.15),
        summary["triggering_mean_divergence"],
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Recall comparison
    bars1 = ax1.bar(categories, recall, color=["#4CAF50", "#FF9800"], edgecolor="black")
    ax1.set_ylabel("Mean Recall")
    ax1.set_title("Detection Recall by Weather Category")
    ax1.set_ylim(0, 1.0)
    for bar, val in zip(bars1, recall):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                 f"{val:.3f}", ha="center", fontsize=10)

    # Divergence comparison
    bars2 = ax2.bar(categories, divergence, color=["#4CAF50", "#FF9800"], edgecolor="black")
    ax2.set_ylabel("Mean Geometric Divergence")
    ax2.set_title("Ensemble Uncertainty by Weather Category")
    ax2.set_ylim(0, 1.0)
    for bar, val in zip(bars2, divergence):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                 f"{val:.3f}", ha="center", fontsize=10)

    plt.suptitle("CARLA Evaluation: SOTIF Triggering vs Non-Triggering Conditions",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved weather evaluation plot to {output_path}")
    plt.close()

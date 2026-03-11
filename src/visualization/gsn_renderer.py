"""GSN diagram renderer using Graphviz.

Generates visual representations of the integrated GSN argument pattern
(Figure 3 in the paper) using the Graphviz DOT language.
"""

from __future__ import annotations

import os
from typing import Optional

from src.gsn.model import (
    GSNArgument,
    Goal,
    Strategy,
    Context,
    Assumption,
    Solution,
    GoalStatus,
)


# Color scheme matching the paper's figure
COLORS = {
    "goal_base": "#E8F0FE",       # Blue tint (ISO/PAS 8800)
    "goal_sotif": "#FFF3E0",      # Orange tint (ISO 21448)
    "goal_cyber": "#FFEBEE",      # Red tint (ISO/SAE 21434)
    "goal_gap": "#F5F5F5",        # Gray (undeveloped)
    "strategy": "#F3E5F5",        # Light purple
    "context": "#E8F5E9",         # Light green
    "assumption": "#FFF9C4",      # Light yellow
    "solution": "#E0F7FA",        # Light cyan
    "border_gap": "#9E9E9E",      # Gray dashed border
}


def _goal_color(goal: Goal) -> str:
    """Determine the fill color for a goal based on its origin."""
    if goal.status == GoalStatus.UNDEVELOPED:
        return COLORS["goal_gap"]
    if goal.element_id in ("G7",):
        return COLORS["goal_sotif"]
    if goal.element_id in ("G8",):
        return COLORS["goal_cyber"]
    return COLORS["goal_base"]


def _truncate(text: str, max_len: int = 60) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def render_gsn_to_dot(gsn: GSNArgument) -> str:
    """Render the GSN argument to Graphviz DOT format.

    Args:
        gsn: The integrated GSN argument.

    Returns:
        DOT language string representing the diagram.
    """
    lines = [
        'digraph GSN {',
        '  rankdir=TB;',
        '  node [fontname="Helvetica", fontsize=10];',
        '  edge [fontname="Helvetica", fontsize=8];',
        '  graph [ranksep=0.8, nodesep=0.5];',
        '',
    ]

    # Render each element type
    for elem in gsn.elements.values():
        if isinstance(elem, Goal):
            color = _goal_color(elem)
            style = "dashed" if elem.status == GoalStatus.UNDEVELOPED else "solid"
            stds = "\\n".join(elem.source_standards[:3]) if elem.source_standards else "Gap"
            label = f"{elem.element_id}\\n{_truncate(elem.text, 50)}\\n[{stds}]"
            lines.append(
                f'  {elem.element_id} [shape=box, style="{style},filled", '
                f'fillcolor="{color}", label="{label}"];'
            )

        elif isinstance(elem, Strategy):
            label = f"{elem.element_id}\\n{_truncate(elem.text, 50)}"
            lines.append(
                f'  {elem.element_id} [shape=trapezium, style="filled", '
                f'fillcolor="{COLORS["strategy"]}", label="{label}"];'
            )

        elif isinstance(elem, Context):
            label = f"{elem.element_id}\\n{_truncate(elem.text, 45)}"
            lines.append(
                f'  {elem.element_id} [shape=box, style="filled,rounded", '
                f'fillcolor="{COLORS["context"]}", label="{label}"];'
            )

        elif isinstance(elem, Assumption):
            label = f"{elem.element_id}\\n{_truncate(elem.text, 45)}"
            lines.append(
                f'  {elem.element_id} [shape=ellipse, style="filled", '
                f'fillcolor="{COLORS["assumption"]}", label="{label}"];'
            )

        elif isinstance(elem, Solution):
            label = f"{elem.element_id}\\n{_truncate(elem.text, 40)}"
            lines.append(
                f'  "{elem.element_id}" [shape=circle, style="filled", '
                f'fillcolor="{COLORS["solution"]}", label="{label}", '
                f'width=1.5, fixedsize=false];'
            )

    lines.append('')

    # Render relationships
    for elem in gsn.elements.values():
        if isinstance(elem, (Goal, Strategy)):
            # SupportedBy edges (solid arrows)
            for child_id in elem.supported_by:
                if child_id in gsn.elements:
                    lines.append(f'  {elem.element_id} -> "{child_id}";')

            # InContextOf edges (hollow arrows)
            for ctx_id in elem.in_context_of:
                if ctx_id in gsn.elements:
                    lines.append(
                        f'  {elem.element_id} -> {ctx_id} '
                        f'[arrowhead=onormal, style=dashed];'
                    )

    # Legend
    lines.append('')
    lines.append('  subgraph cluster_legend {')
    lines.append('    label="Legend";')
    lines.append('    style=dotted;')
    lines.append(
        f'    leg_base [shape=box, style="filled", fillcolor="{COLORS["goal_base"]}", '
        f'label="ISO/PAS 8800\\n(base pattern)"];'
    )
    lines.append(
        f'    leg_sotif [shape=box, style="filled", fillcolor="{COLORS["goal_sotif"]}", '
        f'label="ISO 21448\\n(SOTIF)"];'
    )
    lines.append(
        f'    leg_cyber [shape=box, style="filled", fillcolor="{COLORS["goal_cyber"]}", '
        f'label="ISO/SAE 21434\\n(Cybersecurity)"];'
    )
    lines.append(
        f'    leg_gap [shape=box, style="dashed,filled", fillcolor="{COLORS["goal_gap"]}", '
        f'label="Gap\\n(undeveloped)"];'
    )
    lines.append('  }')

    lines.append('}')
    return '\n'.join(lines)


def save_gsn_diagram(
    gsn: GSNArgument,
    output_path: str,
    fmt: str = "pdf",
) -> Optional[str]:
    """Save the GSN diagram as an image file.

    Requires graphviz to be installed (both the library and the system tool).

    Args:
        gsn: The integrated GSN argument.
        output_path: Path for the output file (without extension).
        fmt: Output format ('pdf', 'png', 'svg').

    Returns:
        Path to the generated file, or None if graphviz is not available.
    """
    dot_source = render_gsn_to_dot(gsn)

    try:
        import graphviz
        g = graphviz.Source(dot_source)
        rendered = g.render(output_path, format=fmt, cleanup=True)
        return rendered
    except ImportError:
        # Save DOT source as fallback
        dot_path = output_path + ".dot"
        with open(dot_path, "w") as f:
            f.write(dot_source)
        return dot_path


def main():
    """Generate the GSN diagram from the command line."""
    from src.gsn.integrated_pattern import build_integrated_gsn

    gsn = build_integrated_gsn()
    dot = render_gsn_to_dot(gsn)

    os.makedirs("output", exist_ok=True)
    dot_path = "output/integrated_gsn.dot"
    with open(dot_path, "w") as f:
        f.write(dot)
    print(f"GSN diagram saved to {dot_path}")

    result = save_gsn_diagram(gsn, "output/integrated_gsn", fmt="png")
    if result:
        print(f"Rendered diagram: {result}")

    # Also print the structure
    print("\n")
    gsn.print_structure("G1")


if __name__ == "__main__":
    main()

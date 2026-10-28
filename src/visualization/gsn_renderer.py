"""GSN diagram renderer using Graphviz.

Generates a repository rendering of the integrated GSN argument pattern in the
Graphviz DOT language. The WAISE paper draws its own Fig. 1 in TikZ; this
rendering is not that figure.

Every node ID is written as a quoted DOT ID. Graphviz does not read an unquoted
``A1.4`` as one ID, so without quotes the edge ``S1 -> A1.4`` lands on a
spurious node ``A1``.
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
from src.visualization.standard_colors import (
    GAP_GREY,
    STANDARD_COLORS,
    STANDARD_LABELS,
)


def _tint(hex_colour: str, keep: float = 0.18) -> str:
    """Return a light fill tint of a palette colour (blended towards white)."""
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    mix = [round(255 - (255 - c) * keep) for c in (r, g, b)]
    return "#{:02X}{:02X}{:02X}".format(*mix)


# Goals and solutions take a light tint of their standard's palette colour as
# fill and the palette colour itself as border, so nodes and legend agree.
COLORS = {
    "strategy": "#F3E5F5",        # Light purple
    "context": "#F5F5F5",         # Light grey
    "assumption": "#FFF9C4",      # Light yellow
    "goal_gap": "#F5F5F5",        # Undeveloped goal fill
    "border_gap": GAP_GREY,       # Undeveloped goal border
}

# Legend order: the four standards.
LEGEND_ORDER = ("ISO26262", "ISO21448", "ISOPAS8800", "ISO21434")


def _q(element_id: str) -> str:
    """Quote an element ID as a DOT ID."""
    return '"' + element_id.replace('"', '\\"') + '"'


def _esc(text: str) -> str:
    """Escape double quotes inside a DOT label."""
    return text.replace('"', '\\"')


def _goal_standard(goal: Goal) -> Optional[str]:
    """The standard whose colour a goal takes, or None for an undeveloped goal.

    G7 is added from ISO 21448 and G8 from ISO/SAE 21434; the other developed
    goals come from the ISO/PAS 8800 base pattern.
    """
    if goal.status == GoalStatus.UNDEVELOPED:
        return None
    if goal.element_id == "G7":
        return "ISO21448"
    if goal.element_id == "G8":
        return "ISO21434"
    return "ISOPAS8800"


def _solution_standard(sol: Solution) -> Optional[str]:
    """The standard whose colour a solution takes (its first source standard)."""
    for std in sol.source_standards or []:
        if std in STANDARD_COLORS:
            return std
    return None


def _wrap(text: str, width: int = 24) -> str:
    """Word-wrap into short lines so a node stays narrow.

    Graphviz sizes a node to its widest label line, so one long line makes the
    whole diagram wide. Wrapping keeps the rendered figure legible at the width
    a README or a slide gives it.
    """
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return "\\n".join(lines)


def render_gsn_to_dot(gsn: GSNArgument) -> str:
    """Render the GSN argument to Graphviz DOT format.

    Args:
        gsn: The integrated GSN argument.

    Returns:
        DOT language string representing the diagram. All node IDs are quoted.
    """
    lines = [
        'digraph GSN {',
        '  rankdir=TB;',
        '  node [fontname="Helvetica", fontsize=10];',
        '  edge [fontname="Helvetica", fontsize=8];',
        '  graph [ranksep=0.8, nodesep=0.5];',
        '',
    ]

    for elem in gsn.elements.values():
        eid = _q(elem.element_id)
        if isinstance(elem, Goal):
            std = _goal_standard(elem)
            if std is None:
                fill, border, style = COLORS["goal_gap"], COLORS["border_gap"], "dashed"
            else:
                fill = _tint(STANDARD_COLORS[std])
                border, style = STANDARD_COLORS[std], "solid"
            if elem.source_standards:
                stds = "\\n".join(
                    STANDARD_LABELS.get(s, s) for s in elem.source_standards
                )
            else:
                stds = "undeveloped"
            label = f"{elem.element_id}\\n{_esc(_wrap(elem.text, 24))}\\n[{stds}]"
            lines.append(
                f'  {eid} [shape=box, style="{style},filled", penwidth=1.5, '
                f'color="{border}", fillcolor="{fill}", label="{label}"];'
            )

        elif isinstance(elem, Strategy):
            label = f"{elem.element_id}\\n{_esc(_wrap(elem.text, 24))}"
            lines.append(
                f'  {eid} [shape=trapezium, style="filled", '
                f'fillcolor="{COLORS["strategy"]}", label="{label}"];'
            )

        elif isinstance(elem, Context):
            label = f"{elem.element_id}\\n{_esc(_wrap(elem.text, 24))}"
            lines.append(
                f'  {eid} [shape=box, style="filled,rounded", '
                f'fillcolor="{COLORS["context"]}", label="{label}"];'
            )

        elif isinstance(elem, Assumption):
            label = f"{elem.element_id}\\n{_esc(_wrap(elem.text, 24))}"
            lines.append(
                f'  {eid} [shape=ellipse, style="filled", '
                f'fillcolor="{COLORS["assumption"]}", label="{label}"];'
            )

        elif isinstance(elem, Solution):
            std = _solution_standard(elem)
            fill = _tint(STANDARD_COLORS[std]) if std else "#FFFFFF"
            border = STANDARD_COLORS[std] if std else "#000000"
            label = f"{elem.element_id}\\n{_esc(_wrap(elem.text, 16))}"
            lines.append(
                f'  {eid} [shape=circle, style="filled", penwidth=1.5, '
                f'color="{border}", fillcolor="{fill}", label="{label}", '
                f'width=1.5, fixedsize=false];'
            )

    lines.append('')

    # Relationships
    for elem in gsn.elements.values():
        if isinstance(elem, (Goal, Strategy)):
            # SupportedBy edges (solid arrows)
            for child_id in elem.supported_by:
                if child_id in gsn.elements:
                    lines.append(f'  {_q(elem.element_id)} -> {_q(child_id)};')

            # InContextOf edges (hollow arrows)
            for ctx_id in elem.in_context_of:
                if ctx_id in gsn.elements:
                    lines.append(
                        f'  {_q(elem.element_id)} -> {_q(ctx_id)} '
                        f'[arrowhead=onormal, style=dashed];'
                    )

    # Legend: the four standards in the shared palette, plus undeveloped.
    lines.append('')
    lines.append('  subgraph cluster_legend {')
    lines.append('    label="Legend: colour = source standard";')
    lines.append('    style=dotted;')
    for std in LEGEND_ORDER:
        lines.append(
            f'    "leg_{std}" [shape=box, style="filled", penwidth=1.5, '
            f'color="{STANDARD_COLORS[std]}", '
            f'fillcolor="{_tint(STANDARD_COLORS[std])}", '
            f'label="{STANDARD_LABELS[std]}"];'
        )
    lines.append(
        f'    "leg_undeveloped" [shape=box, style="dashed,filled", '
        f'color="{COLORS["border_gap"]}", fillcolor="{COLORS["goal_gap"]}", '
        f'label="Undeveloped goal"];'
    )
    # Invisible edges keep the legend entries in the order listed.
    order = [f'"leg_{std}"' for std in LEGEND_ORDER] + ['"leg_undeveloped"']
    lines.append('    {rank=same; ' + ' -> '.join(order) + ' [style=invis];}')
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

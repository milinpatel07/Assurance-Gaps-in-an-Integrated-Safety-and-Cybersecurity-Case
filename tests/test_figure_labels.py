"""Pin the wording of the repository's figures and the DOT output of the GSN.

The figures are repository renderings. Their titles must not carry paper
figure or table numbers, and the DOT source must quote node IDs so that
"A1.4" stays one node.
"""

import ast
import re
from pathlib import Path

from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis
from src.gsn.integrated_pattern import build_integrated_gsn
from src.visualization.gsn_renderer import render_gsn_to_dot
from src.visualization.standard_colors import STANDARD_COLORS, STANDARD_LABELS

ROOT = Path(__file__).resolve().parents[1]
PLOTS = ROOT / "src" / "visualization" / "coverage_plots.py"
PAPER_NUMBER = re.compile(r"\((?:Fig\.?|Figure|Table)\s*\d", re.IGNORECASE)


def _title_strings() -> list[str]:
    """Collect the string arguments of every title, suptitle and label call."""
    tree = ast.parse(PLOTS.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ("set_title", "suptitle", "set_xlabel", "set_ylabel"):
                for arg in node.args:
                    for sub in ast.walk(arg):
                        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                            found.append(sub.value)
    return found


def test_plot_titles_carry_no_paper_numbers():
    titles = _title_strings()
    assert titles
    for t in titles:
        assert not PAPER_NUMBER.search(t), t


def test_plot_source_names_no_paper_figure_or_table():
    text = PLOTS.read_text(encoding="utf-8")
    assert not PAPER_NUMBER.search(text)


def test_weather_title_says_synthetic_and_case_study_thresholds():
    joined = " ".join(_title_strings())
    assert "Synthetic illustration" in joined
    assert "no detector" in joined
    assert "rain > 20 mm/h or visibility < 200 m" in joined
    assert "not ISO 21448 values" in joined


def test_dot_quotes_node_ids():
    dot = render_gsn_to_dot(build_integrated_gsn())
    assert '"A1.4" [' in dot
    assert '"S1" -> "A1.4"' in dot
    # No unquoted ID at the start of a node or edge statement.
    statement = re.compile(r"^\s+(\S+)\s+(?:\[|->)")
    for line in dot.splitlines():
        m = statement.match(line)
        if m and m.group(1) not in ("node", "edge", "graph"):
            assert m.group(1).startswith('"'), line
        for target in re.findall(r"->\s*(\S+)", line):
            assert target.startswith('"'), line


def test_dot_legend_lists_four_standards_in_palette():
    dot = render_gsn_to_dot(build_integrated_gsn())
    for key, colour in STANDARD_COLORS.items():
        assert f'"leg_{key}"' in dot
        assert colour in dot
        assert f'label="{STANDARD_LABELS[key]}"' in dot


def test_triggering_condition_identification_is_cl7():
    paths = EvidenceConvergenceAnalysis().failure_event.analysis_paths
    methods = [p.analysis_method for p in paths if p.standard == "ISO 21448"]
    assert methods == ["Triggering condition identification (Cl.7)"]


def test_solution_sketch_is_labelled_and_plain():
    sketch = EvidenceConvergenceAnalysis().get_solution_sketch()
    assert sketch["label"] == "Repository analysis, not in either paper."
    text = repr(sketch)
    assert "justified from its source standard" not in text
    assert "Well-established" not in text
    assert "HIGH" not in text and "MEDIUM" not in text
    assert "illustrative" in sketch["approaches"][0]["description"]
    assert "—" not in text

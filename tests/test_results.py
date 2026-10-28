"""Tests for the results generation module."""

import json
import os
import tempfile

import pytest

from src.standards.registry import StandardsRegistry
from src.evaluation.carla_evaluator import generate_synthetic_illustration
from src.results.latex_tables import (
    generate_standards_overview_table,
    generate_coverage_matrix_table,
    generate_goals_table,
    generate_goal_density_table,
    generate_decision_points_table,
    generate_findings_table,
    generate_evidence_types_table,
    generate_weather_illustration_table,
    generate_all_tables,
)
from src.results.export import export_json, export_csv_tables, export_summary_report


@pytest.fixture
def registry():
    return StandardsRegistry()


@pytest.fixture
def eval_result():
    return generate_synthetic_illustration(num_scenes_per_weather=5, seed=42)


class TestLatexTables:
    def test_standards_overview_is_valid_latex(self):
        latex = generate_standards_overview_table()
        assert r"\begin{table}" in latex
        assert r"\end{table}" in latex
        assert r"\toprule" in latex
        assert "ISO" in latex

    def test_coverage_matrix_has_all_phases(self):
        latex = generate_coverage_matrix_table()
        assert "Concept" in latex
        assert "Design" in latex
        assert r"V\&V" in latex

    def test_goals_table_has_all_goals(self):
        latex = generate_goals_table()
        for g in ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]:
            assert g in latex

    def test_goal_density_has_checkmarks(self):
        latex = generate_goal_density_table()
        assert r"\checkmark" in latex

    def test_decision_points_table_has_all_decision_points(self):
        latex = generate_decision_points_table()
        for i in ["I-1", "I-2", "I-3", "I-4", "I-5", "I-6", "I-7"]:
            assert i in latex

    def test_decision_points_table_escapes_ampersand(self):
        latex = generate_decision_points_table()
        # V&V should be escaped to V\&V
        assert r"V\&V" in latex

    def test_findings_table_has_all_findings(self):
        latex = generate_findings_table()
        for g in ["Gap-1", "Gap-2", "Gap-3", "Gap-4", "Gap-5"]:
            assert g in latex

    def test_findings_table_uses_the_papers_categories(self):
        latex = generate_findings_table()
        assert " & II & " in latex
        assert " & OM & " in latex
        # The repository-only MC/ME/UI code is not presented as the paper's.
        for code in (" & MC & ", " & ME & ", " & UI & "):
            assert code not in latex

    def test_evidence_types_table_has_four_types(self):
        latex = generate_evidence_types_table()
        assert "MC/DC" in latex
        assert "Scenario" in latex or "scenario" in latex
        assert "uncertainty" in latex or "Uncertainty" in latex
        assert "penetration" in latex or "Penetration" in latex

    def test_weather_illustration_has_categories(self, eval_result):
        summary = eval_result.compute_summary()
        latex = generate_weather_illustration_table(summary)
        assert "Non-triggering" in latex
        assert "Triggering" in latex
        assert "Overall" in latex

    def test_generate_all_tables(self, eval_result):
        summary = eval_result.compute_summary()
        with tempfile.TemporaryDirectory() as tmpdir:
            tables = generate_all_tables(summary, tmpdir)
            assert len(tables) == 8
            for name in tables:
                path = os.path.join(tmpdir, f"{name}.tex")
                assert os.path.exists(path)
                # Named by content, never by a number that could be read as
                # a WAISE table number.
                assert not name.startswith("table")


class TestExport:
    def test_json_export(self, registry, eval_result):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = export_json(registry, eval_result, tmpdir)
            assert os.path.exists(path)
            with open(path) as f:
                data = json.load(f)
            assert "metadata" in data
            assert "standards" in data
            assert "inconsistencies" in data
            assert "gaps" in data
            assert "evaluation" in data
            assert data["metadata"]["random_seed"] == 42

    def test_json_has_correct_counts(self, registry, eval_result):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = export_json(registry, eval_result, tmpdir)
            with open(path) as f:
                data = json.load(f)
            assert data["inconsistencies"]["summary"]["total"] == 7
            assert data["gaps"]["summary"]["total"] == 5
            assert data["gsn_statistics"]["goals"] == 9

    def test_csv_export(self, registry, eval_result):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = export_csv_tables(registry, eval_result, tmpdir)
            assert len(files) == 6
            for f in files:
                assert os.path.exists(f)

    def test_summary_report(self, registry, eval_result):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = export_summary_report(registry, eval_result, tmpdir)
            assert os.path.exists(path)
            with open(path) as f:
                content = f.read()
            assert "ANALYSIS RESULTS SUMMARY" in content
            assert "7" in content  # inconsistencies
            assert "5" in content  # gaps

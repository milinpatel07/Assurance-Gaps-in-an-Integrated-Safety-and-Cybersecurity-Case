"""Tests for the results generation module."""

import json
import os
import tempfile

import pytest

from src.standards.registry import StandardsRegistry
from src.evaluation.carla_evaluator import generate_synthetic_evaluation
from src.results.latex_tables import (
    generate_table1_standards_overview,
    generate_table2_coverage_matrix,
    generate_table3_gsn_structure,
    generate_table4_goal_density,
    generate_table5_inconsistencies,
    generate_table6_gaps,
    generate_table7_evidence_types,
    generate_table8_weather_evaluation,
    generate_all_tables,
)
from src.results.export import export_json, export_csv_tables, export_summary_report


@pytest.fixture
def registry():
    return StandardsRegistry()


@pytest.fixture
def eval_result():
    return generate_synthetic_evaluation(num_scenes_per_weather=5, seed=42)


class TestLatexTables:
    def test_table1_is_valid_latex(self):
        latex = generate_table1_standards_overview()
        assert r"\begin{table}" in latex
        assert r"\end{table}" in latex
        assert r"\toprule" in latex
        assert "ISO" in latex

    def test_table2_has_all_phases(self):
        latex = generate_table2_coverage_matrix()
        assert "Concept" in latex
        assert "Design" in latex
        assert r"V\&V" in latex

    def test_table3_has_all_goals(self):
        latex = generate_table3_gsn_structure()
        for g in ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]:
            assert g in latex

    def test_table4_has_checkmarks(self):
        latex = generate_table4_goal_density()
        assert r"\checkmark" in latex

    def test_table5_has_all_inconsistencies(self):
        latex = generate_table5_inconsistencies()
        for i in ["I-1", "I-2", "I-3", "I-4", "I-5", "I-6", "I-7"]:
            assert i in latex

    def test_table5_escapes_ampersand(self):
        latex = generate_table5_inconsistencies()
        # V&V should be escaped to V\&V
        assert r"V\&V" in latex

    def test_table6_has_all_gaps(self):
        latex = generate_table6_gaps()
        for g in ["Gap-1", "Gap-2", "Gap-3", "Gap-4", "Gap-5", "Gap-6"]:
            assert g in latex

    def test_table6_marks_integration_induced(self):
        latex = generate_table6_gaps()
        assert r"$\dagger$" in latex

    def test_table7_has_four_evidence_types(self):
        latex = generate_table7_evidence_types()
        assert "MC/DC" in latex
        assert "Scenario" in latex or "scenario" in latex
        assert "uncertainty" in latex or "Uncertainty" in latex
        assert "penetration" in latex or "Penetration" in latex

    def test_table8_has_categories(self, eval_result):
        summary = eval_result.compute_summary()
        latex = generate_table8_weather_evaluation(summary)
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
            assert data["gaps"]["summary"]["total"] == 6
            assert data["gsn_statistics"]["goals"] == 9

    def test_csv_export(self, registry, eval_result):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = export_csv_tables(registry, eval_result, tmpdir)
            assert len(files) == 5
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
            assert "6" in content  # gaps

"""The G5 evidence-combination notebook, and the module it runs on.

The notebook restates DP-2 and F-4: the four V&V evidence scales at G5 do not
combine, so any single release verdict is one the assessor supplied. These tests
hold the module to that (each leg is one standard's, no standard spans two
scales, and a changed threshold flips the verdict), and rebuild the notebook,
check it is current, and execute it end to end.
"""

from __future__ import annotations

import json
import os

import pytest

from src.analysis.g5_evidence import (
    combine_all_must_pass,
    g5_legs,
    no_standard_combines_the_scales,
    scales,
)
from src.gsn.integrated_pattern import build_integrated_gsn
from src.visualization.g5_notebook import OUTPUT_PATH, build_notebook


class TestTheFourLegs:
    def test_there_are_four_legs_one_per_standard(self):
        legs = g5_legs()
        assert len(legs) == 4
        assert {leg.standard_id for leg in legs} == {
            "ISO26262",
            "ISO21448",
            "ISOPAS8800",
            "ISO21434",
        }

    def test_the_legs_are_read_from_the_argument(self):
        """Not retyped: the legs are the G5 solutions of the built pattern."""
        g5 = build_integrated_gsn().get_element("G5")
        assert len(g5_legs()) == len(g5.supported_by)

    def test_the_four_scales_share_no_common_unit(self):
        kinds = {scale for _, scale in scales()}
        assert kinds == {
            "deterministic coverage",
            "scenario coverage",
            "statistical metric",
            "attack success rate",
        }

    def test_only_one_leg_was_produced_in_the_case_study(self):
        produced = [leg for leg in g5_legs() if leg.instantiation.startswith("provided")]
        assert len(produced) == 1
        assert produced[0].standard_id == "ISOPAS8800"


class TestNoRuleIsAuthorised:
    def test_no_standard_spans_more_than_one_scale(self):
        result = no_standard_combines_the_scales()
        assert result["any_standard_combines"] is False
        assert result["standards_spanning_more_than_one_scale"] == []

    def test_a_changed_threshold_flips_the_verdict(self):
        """The lesson: the verdict is a property of the assessor's threshold,
        not the evidence."""
        values = {
            "ISO26262": 0.97,
            "ISO21448": 1200,
            "ISOPAS8800": 0.982,
            "ISO21434": 0.15,
        }
        lenient = {"ISO26262": 0.95, "ISO21448": 1000, "ISOPAS8800": 0.90, "ISO21434": 0.20}
        strict = dict(lenient, ISO26262=0.99)
        assert combine_all_must_pass(values, lenient)["verdict"] == "release"
        assert combine_all_must_pass(values, strict)["verdict"] == "hold"


class TestNotebook:
    def test_committed_notebook_is_current(self):
        assert os.path.exists(OUTPUT_PATH), "notebooks/g5_evidence_walk.ipynb missing"
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            assert handle.read() == build_notebook(), (
                "notebooks/g5_evidence_walk.ipynb is stale. "
                "Run: python -m src.visualization.g5_notebook"
            )

    def test_build_is_deterministic(self):
        assert build_notebook() == build_notebook()

    def test_prose_carries_the_argument(self):
        nb = json.loads(build_notebook())
        kinds = [c["cell_type"] for c in nb["cells"]]
        assert kinds[0] == "markdown" and kinds[-1] == "markdown"
        assert kinds.count("markdown") >= kinds.count("code")

    def test_no_outputs_are_stored(self):
        nb = json.loads(build_notebook())
        for cell in nb["cells"]:
            assert not cell.get("outputs")

    def test_it_claims_no_combination_rule(self):
        """A notebook that combined the scales would assert the rule F-4 says is
        missing. It must not."""
        text = json.dumps(json.loads(build_notebook()))
        assert "all publication results" not in text.lower()

    def test_notebook_executes_end_to_end(self):
        nbformat = pytest.importorskip("nbformat")
        nbclient = pytest.importorskip("nbclient")

        nb = nbformat.reads(build_notebook(), as_version=4)
        client = nbclient.NotebookClient(
            nb,
            timeout=180,
            kernel_name="python3",
            resources={"metadata": {"path": os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}},
        )
        client.execute()
        errors = [
            f"{output.ename}: {output.evalue}"
            for cell in nb.cells
            if cell.cell_type == "code"
            for output in cell.get("outputs", [])
            if output.output_type == "error"
        ]
        assert not errors, errors

        text = "".join(
            output.get("text", "")
            for cell in nb.cells
            if cell.cell_type == "code"
            for output in cell.get("outputs", [])
            if output.output_type == "stream"
        )
        assert "lenient ISO26262 threshold: release" in text
        assert "strict  ISO26262 threshold: hold" in text

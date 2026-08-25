"""The anomaly walk, and the notebook that presents it.

The walk restates the position paper's clause-level argument. These tests hold
it to that: every verdict cites a clause that exists in the registry, the walk
ends unassigned for any observation that does not indicate a hardware fault, and
the one case that does assign is the one the paper puts outside the ambiguity.

The notebook tests rebuild it, check the committed copy is current, and execute
it end to end. Execution needs nbclient; the tests skip without it and CI
installs it, so a broken notebook cannot reach a reader unnoticed.
"""

from __future__ import annotations

import json
import os

import pytest

from src.analysis.anomaly_walk import (
    SCENARIOS,
    AnomalyObservation,
    Cause,
    ClauseVerdict,
    Verdict,
    assignment,
    resolve_with_cause,
    walk,
    walk_result,
)
from src.standards.registry import StandardsRegistry
from src.visualization.anomaly_notebook import OUTPUT_PATH, build_notebook


class TestEveryVerdictCitesARealClause:
    def test_each_clause_exists_in_the_registry(self):
        registry = StandardsRegistry()
        for verdict in walk(SCENARIOS["detections_drop"]):
            standard = registry.get_standard(verdict.standard_id)
            references = {c.reference for c in standard.clauses}
            assert verdict.clause in references, (
                f"{verdict.standard_id} has no clause {verdict.clause}"
            )

    def test_each_verdict_gives_a_reason(self):
        for verdict in walk(SCENARIOS["detections_drop"]):
            assert len(verdict.reason) > 60, verdict

    def test_the_four_normative_standards_all_answer(self):
        ids = {v.standard_id for v in walk(SCENARIOS["detections_drop"])}
        assert ids == {"ISO26262", "ISO21448", "ISO21434", "ISOPAS8800"}


class TestTheWalkEndsUnassigned:
    @pytest.mark.parametrize(
        "name",
        [n for n in SCENARIOS if n != "hardware_fault"],
    )
    def test_perception_anomalies_are_never_assigned(self, name):
        assert walk_result(SCENARIOS[name])["assigned_to"] is None

    def test_a_correlated_report_does_not_assign_the_anomaly(self):
        """The paper's point: the same observation follows from either cause."""
        plain = walk_result(SCENARIOS["detections_drop"])["assigned_to"]
        rain = walk_result(SCENARIOS["drop_with_rain_reported"])["assigned_to"]
        attack = walk_result(SCENARIOS["drop_with_security_event"])["assigned_to"]
        assert plain == rain == attack is None

    def test_two_standards_wait_on_the_same_missing_fact(self):
        conditional = walk_result(SCENARIOS["detections_drop"])[
            "conditional_on_cause"
        ]
        assert {v.standard_id for v in conditional} == {"ISO21448", "ISO21434"}

    def test_iso21448_records_its_own_exclusion(self):
        verdicts = walk(SCENARIOS["detections_drop"])
        excludes = [v for v in verdicts if v.verdict is Verdict.EXCLUDES]
        assert len(excludes) == 1
        assert excludes[0].standard_id == "ISO21448"
        assert excludes[0].clause == "Cl.1"


class TestTheHardwareFaultException:
    def test_a_failing_diagnostic_assigns_to_iso26262(self):
        assert walk_result(SCENARIOS["hardware_fault"])["assigned_to"] == "ISO26262"

    def test_it_is_the_only_scenario_that_assigns(self):
        assigned = {
            name for name, obs in SCENARIOS.items()
            if walk_result(obs)["assigned_to"] is not None
        }
        assert assigned == {"hardware_fault"}


class TestKnowingTheCauseSettlesIt:
    """The cause is the only missing input, which is why it is a missing step."""

    @pytest.mark.parametrize(
        "cause,owner",
        [
            (Cause.PERFORMANCE_INSUFFICIENCY, "ISO21448"),
            (Cause.ATTACK, "ISO21434"),
            (Cause.HARDWARE_FAULT, "ISO26262"),
            (Cause.UNKNOWN, None),
        ],
    )
    def test_each_cause_maps_to_one_owner(self, cause, owner):
        assert resolve_with_cause(SCENARIOS["detections_drop"], cause) == owner


class TestDeterminism:
    def test_the_same_observation_gives_the_same_walk(self):
        first = walk(SCENARIOS["detections_drop"])
        second = walk(SCENARIOS["detections_drop"])
        assert first == second

    def test_observations_carry_no_cause_field(self):
        """If a cause field appeared, the walk would beg its own question."""
        fields = AnomalyObservation.__dataclass_fields__
        assert not any("cause" in name for name in fields)


class TestNotebook:
    def test_committed_notebook_is_current(self):
        assert os.path.exists(OUTPUT_PATH), "notebooks/anomaly_walk.ipynb missing"
        with open(OUTPUT_PATH, encoding="utf-8") as handle:
            assert handle.read() == build_notebook(), (
                "notebooks/anomaly_walk.ipynb is stale. "
                "Run: python -m src.visualization.anomaly_notebook"
            )

    def test_build_is_deterministic(self):
        assert build_notebook() == build_notebook()

    def test_prose_carries_the_argument(self):
        """More Markdown than code, and Markdown first and last."""
        nb = json.loads(build_notebook())
        kinds = [c["cell_type"] for c in nb["cells"]]
        assert kinds[0] == "markdown" and kinds[-1] == "markdown"
        assert kinds.count("markdown") >= kinds.count("code")

    def test_no_outputs_are_stored(self):
        """Stored outputs drift from the code that produced them."""
        nb = json.loads(build_notebook())
        for cell in nb["cells"]:
            assert not cell.get("outputs")

    def test_every_cell_has_a_stable_id(self):
        nb = json.loads(build_notebook())
        ids = [c["id"] for c in nb["cells"]]
        assert len(ids) == len(set(ids))
        assert ids == [f"cell-{i:02d}" for i in range(len(ids))]

    def test_notebook_executes_end_to_end(self):
        """The claim that it runs, verified by running it."""
        nbformat = pytest.importorskip("nbformat")
        nbclient = pytest.importorskip("nbclient")

        nb = nbformat.reads(build_notebook(), as_version=4)
        client = nbclient.NotebookClient(
            nb, timeout=180, kernel_name="python3",
            resources={"metadata": {"path": os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)))}},
        )
        client.execute()

        errors = [
            output
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
        assert "assigned to: None" in text
        assert "assigned to: ISO26262" in text

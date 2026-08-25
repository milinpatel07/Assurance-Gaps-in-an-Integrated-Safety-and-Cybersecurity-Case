"""Every committed notebook runs, and claims only what it does.

A notebook that no longer executes is worse than no notebook: it is the entry
point a reader is most likely to try first. These tests run each one end to end
under a clean kernel. Execution needs nbclient, so the tests skip without it and
CI installs it.
"""

from __future__ import annotations

import json
import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK_DIR = os.path.join(REPO_ROOT, "notebooks")

NOTEBOOKS = sorted(
    name for name in os.listdir(NOTEBOOK_DIR) if name.endswith(".ipynb")
)


def _source(notebook: dict) -> str:
    return "\n".join("".join(cell["source"]) for cell in notebook["cells"])


@pytest.fixture(scope="module", params=NOTEBOOKS)
def notebook(request) -> dict:
    path = os.path.join(NOTEBOOK_DIR, request.param)
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    data["_name"] = request.param
    return data


def test_every_notebook_is_covered():
    """Guard the list: a new notebook joins these tests automatically."""
    assert NOTEBOOKS, "no notebooks found"
    assert "anomaly_walk.ipynb" in NOTEBOOKS


class TestClaims:
    def test_no_notebook_claims_to_reproduce_everything(self, notebook):
        """`make reproduce` is the reproduction entry point, not a notebook."""
        text = _source(notebook).lower()
        assert "all publication results" not in text, notebook["_name"]

    def test_no_stored_outputs(self, notebook):
        """Stored outputs drift from the code that produced them."""
        for cell in notebook["cells"]:
            assert not cell.get("outputs"), notebook["_name"]


class TestExecution:
    def test_notebook_runs_end_to_end(self, notebook):
        nbformat = pytest.importorskip("nbformat")
        nbclient = pytest.importorskip("nbclient")

        path = os.path.join(NOTEBOOK_DIR, notebook["_name"])
        nb = nbformat.read(path, as_version=4)
        client = nbclient.NotebookClient(
            nb,
            timeout=600,
            kernel_name="python3",
            resources={"metadata": {"path": REPO_ROOT}},
        )
        client.execute()

        errors = [
            f"{output.ename}: {output.evalue}"
            for cell in nb.cells
            if cell.cell_type == "code"
            for output in cell.get("outputs", [])
            if output.output_type == "error"
        ]
        assert not errors, f"{notebook['_name']} failed: {errors[:3]}"

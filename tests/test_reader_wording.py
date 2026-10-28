"""Pins wording that was corrected against the WAISE paper.

Each test guards one correction so that it cannot quietly come back.
"""

from __future__ import annotations

import json
import os

import pytest

from src.analysis.completeness import get_related_work_comparison
from src.analysis.counterfactual import CounterfactualAnalysis
from src.results.traceability_index import build_index

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(*parts: str) -> str:
    with open(os.path.join(REPO_ROOT, *parts), encoding="utf-8") as handle:
        return handle.read()


def _notebook_text(name: str) -> str:
    notebook = json.loads(_read("notebooks", name))
    return "\n".join("".join(cell["source"]) for cell in notebook["cells"])


class TestCounterfactualScope:
    def test_only_iso_21448_explicitly_excludes_something(self):
        """A standard excludes something explicitly only where its scope clause
        says so. Of the four, that is ISO 21448 Cl.1 for cybersecurity."""
        perspectives = CounterfactualAnalysis().perspectives
        explicit = {p.standard_id: p.explicitly_excludes for p in perspectives if p.explicitly_excludes}
        assert list(explicit) == ["ISO 21448"]
        assert "Cl.1" in explicit["ISO 21448"][0]

    def test_iso_26262_is_not_said_to_exclude_ai(self):
        p = CounterfactualAnalysis().get_perspective("ISO 26262")
        assert not any("assumes deterministic" in e for e in p.excludes)


class TestRelatedWork:
    def test_friedberg_row_names_stpa_safesec_and_the_power_grid(self):
        rows = {a.name: a for a in get_related_work_comparison()}
        assert "STPA-SafeSec" in rows
        assert rows["STPA-SafeSec"].case_study_domain == "Power grid"
        assert not any("STPA-Sec " in name or name.endswith("STPA-Sec") for name in rows)

    def test_this_work_limitation_follows_section_6_3(self):
        this_work = [a for a in get_related_work_comparison() if a.name.startswith("This work")][0]
        limitation = this_work.key_limitation
        assert "single assessor" in limitation
        assert "inter-rater" in limitation
        assert "evidence type (c)" in limitation
        assert "CARLA" not in limitation


@pytest.fixture(scope="module")
def text() -> str:
    return _notebook_text("1_five_step_method.ipynb")


class TestNotebookOne:
    def test_verification_section_is_6_3(self, text):
        assert "Section 6.3, Verification and Limitations" in text
        assert "(Section 5, verification" not in text

    def test_goal_count_label(self, text):
        assert "G1 reformulated, G2 to G6 retained from Annex B, G7 to G9 added" in text
        assert "Annex B: G1 and G2 to G6" not in text

    def test_counterfactual_heading_is_does_not_address(self, text):
        assert "Does not address" in text


class TestProvenanceAndErrata:
    def test_traceability_uses_the_five_provenance_labels(self):
        index = build_index()
        section = index[index.index("## 7. Artefacts"):index.index("## 8. The position paper")]
        for label in ("| argued |", "| hand-written |", "| generated |", "| seeded |", "| measured |"):
            assert label in section, label

    def test_errata_entry_6_names_the_claim_mapped_to_g5(self):
        errata = _read("ERRATA.md")
        entry = errata[errata.index("## 6."):errata.index("## 7.")]
        assert "CLM-26262-SVAL-01" in entry
        assert "the repository does not" not in entry


@pytest.mark.parametrize(
    "path",
    [
        ("data", "empirical_results", "README.md"),
        ("data", "synthetic_illustrations", "README.md"),
        ("data", "case_study_parameters", "README.md"),
        ("data", "standards_reference", "README.md"),
        ("ERRATA.md",),
        ("REPRODUCING.md",),
        ("TRACEABILITY.md",),
    ],
)
def test_no_one_place_claims_and_no_em_dashes(path):
    text = _read(*path)
    assert "the one place" not in text
    assert "recorded in one place" not in text
    assert "—" not in text

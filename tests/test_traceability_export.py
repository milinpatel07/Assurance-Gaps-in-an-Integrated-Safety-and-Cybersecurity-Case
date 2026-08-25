"""The machine-readable traceability export stays current and complete.

``docs/traceability.json`` and ``docs/traceability.csv`` are tracked generated
files carrying the clause-to-node traceability the WAISE paper says exists in
machine-readable form. These tests rebuild both and fail if the committed copies
differ, and check that every claim in the registry reaches the export.
"""

from __future__ import annotations

import csv
import io
import json
import os

from src.results.traceability_export import (
    CSV_PATH,
    JSON_PATH,
    build_csv,
    build_json,
)
from src.standards.registry import StandardsRegistry


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class TestFilesAreCurrent:
    def test_committed_json_matches_a_rebuild(self):
        assert os.path.exists(JSON_PATH), "docs/traceability.json is missing"
        assert _read(JSON_PATH) == build_json(), (
            "docs/traceability.json is stale. "
            "Run: python -m src.results.traceability_export"
        )

    def test_committed_csv_matches_a_rebuild(self):
        assert os.path.exists(CSV_PATH), "docs/traceability.csv is missing"
        assert _read(CSV_PATH) == build_csv(), (
            "docs/traceability.csv is stale. "
            "Run: python -m src.results.traceability_export"
        )

    def test_build_is_deterministic(self):
        assert build_json() == build_json()
        assert build_csv() == build_csv()


class TestExportIsComplete:
    def test_json_carries_one_row_per_claim(self):
        claims = sum(len(s.claims) for s in StandardsRegistry().all_standards)
        document = json.loads(build_json())
        assert len(document["claims"]) == claims

    def test_every_claim_id_appears_in_both_files(self):
        json_ids = {row["claim_id"] for row in json.loads(build_json())["claims"]}
        csv_ids = {
            row["claim_id"] for row in csv.DictReader(io.StringIO(build_csv()))
        }
        for standard in StandardsRegistry().all_standards:
            for claim in standard.claims:
                assert claim.claim_id in json_ids, claim.claim_id
                assert claim.claim_id in csv_ids, claim.claim_id

    def test_every_row_carries_the_five_fields(self):
        for row in json.loads(build_json())["claims"]:
            for field in ("standard", "edition_as_cited", "clause", "claim_id", "node"):
                assert row.get(field), f"{row.get('claim_id')} missing {field}"

    def test_all_five_standards_are_listed_with_editions(self):
        document = json.loads(build_json())
        codes = {s["code"] for s in document["standards"]}
        assert codes == {"ISO26262", "ISO21448", "ISO21434", "ISOPAS8800", "TR5469"}
        for standard in document["standards"]:
            assert standard["edition_as_cited"]

    def test_the_edition_field_does_not_overclaim(self):
        """The edition is the one cited, not a claim of re-analysis against it."""
        note = json.loads(build_json())["note"]
        assert "cited under" in note
        assert "does not assert" in note

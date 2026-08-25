"""Export the clause-to-node traceability as machine-readable JSON and CSV.

The WAISE paper states that its clause-to-node traceability is available in
machine-readable form in the supplementary material (Section 4). ``TRACEABILITY.md``
carries it as a Markdown table for a human; this module emits the same data as
``docs/traceability.json`` and ``docs/traceability.csv`` for a machine, so the
paper's claim about its supplement is met in a form a reader can load and check.

The two files carry one row per extracted claim: the standard and the edition as
cited, the clause, the claim id, the GSN node it supports, and its lifecycle
phase. The rows are the same objects ``src/results/traceability_index.py`` writes
to Section 4 of ``TRACEABILITY.md``, read from ``StandardsRegistry``.

The ``edition_as_cited`` field records the edition each standard is cited under,
matching the standards table in ``TRACEABILITY.md``. It does not assert that the
analysis was re-run against any other edition.

Output is byte-deterministic: rows are sorted, and no timestamp is written, so
the committed copies diff cleanly. ``tests/test_traceability_export.py``
regenerates both files and fails if the committed copies differ.

Usage:
    python -m src.results.traceability_export          # write both files
    python -m src.results.traceability_export --check  # exit 1 if out of date
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

from src.standards.registry import StandardsRegistry

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON_PATH = os.path.join(REPO_ROOT, "docs", "traceability.json")
CSV_PATH = os.path.join(REPO_ROOT, "docs", "traceability.csv")

REBUILD_COMMAND = "python -m src.results.traceability_export"

EDITION_NOTE = (
    "edition_as_cited records the edition each standard is cited under, as in "
    "the standards table of TRACEABILITY.md. It does not assert the analysis was "
    "run against any other edition."
)

CSV_COLUMNS = [
    "standard",
    "edition_as_cited",
    "year",
    "clause",
    "claim_id",
    "node",
    "lifecycle_phase",
    "out_of_scope",
]


def _rows() -> list[dict]:
    registry = StandardsRegistry()
    normative_ids = {s.standard_id for s in registry.normative_standards}
    rows: list[dict] = []
    for standard in registry.all_standards:
        for claim in standard.claims:
            rows.append(
                {
                    "standard": standard.standard_id,
                    "edition_as_cited": standard.full_name,
                    "year": standard.year,
                    "normative": standard.standard_id in normative_ids,
                    "clause": claim.source_clause.reference,
                    "claim_id": claim.claim_id,
                    "node": claim.gsn_goal or "(out of scope)",
                    "lifecycle_phase": (
                        claim.lifecycle_phase.display_name if claim.lifecycle_phase else "(none)"
                    ),
                    "out_of_scope": claim.is_out_of_scope,
                    "text": " ".join(claim.text.split()),
                }
            )
    rows.sort(key=lambda r: (r["standard"], r["clause"], r["claim_id"]))
    return rows


def build_json() -> str:
    registry = StandardsRegistry()
    normative_ids = {s.standard_id for s in registry.normative_standards}
    standards = [
        {
            "code": s.standard_id,
            "edition_as_cited": s.full_name,
            "year": s.year,
            "normative": s.standard_id in normative_ids,
        }
        for s in sorted(registry.all_standards, key=lambda x: x.standard_id)
    ]
    document = {
        "generated_by": REBUILD_COMMAND,
        "note": EDITION_NOTE,
        "source_of_record": "TRACEABILITY.md Section 4",
        "standards": standards,
        "claims": _rows(),
    }
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def build_csv() -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer, fieldnames=CSV_COLUMNS, lineterminator="\n", extrasaction="ignore"
    )
    writer.writeheader()
    for row in _rows():
        writer.writerow(row)
    return buffer.getvalue()


def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export machine-readable traceability.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if the committed export files differ from a fresh build",
    )
    args = parser.parse_args(argv)

    targets = [(JSON_PATH, build_json()), (CSV_PATH, build_csv())]

    if args.check:
        for path, content in targets:
            if not os.path.exists(path):
                print(f"MISSING: {path}. Run: {REBUILD_COMMAND}")
                return 1
            with open(path, encoding="utf-8") as handle:
                if handle.read() != content:
                    print(f"STALE: {path}. Run: {REBUILD_COMMAND}")
                    return 1
        print("Machine-readable traceability is up to date.")
        return 0

    for path, content in targets:
        _write(path, content)
        print(f"Wrote {path} ({len(content)} bytes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

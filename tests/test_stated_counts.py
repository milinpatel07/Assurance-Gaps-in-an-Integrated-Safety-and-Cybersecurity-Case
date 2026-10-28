"""Numbers written in prose have to match the thing they count.

The test count in the README has gone stale twice: it said 192 after the suite
had grown, and 285 after it had grown again. Each time a reviewer found it, and
each time it was the first countable claim a sceptic checked. This test makes
the repository check it instead.

The same guard covers the counts the landing page states, though those are
already generated from the code rather than typed.
"""

from __future__ import annotations

import os
import re

import pytest

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.gsn.integrated_pattern import build_integrated_gsn

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(name: str) -> str:
    with open(os.path.join(REPO_ROOT, name), encoding="utf-8") as handle:
        return handle.read()


def test_the_readme_test_count_matches_the_suite(request):
    """Compare against what this very session collected.

    Skipped when only part of the suite is running, because the number would
    then be the size of the selection rather than of the suite.
    """
    collected = len(request.session.items)
    if collected < 100:
        pytest.skip("partial run; the collected count is not the suite size")

    readme = _read("README.md")
    match = re.search(r"tests/\s+(\d+) tests", readme)
    assert match, "README no longer states a test count in its map"
    stated = int(match.group(1))
    assert stated == collected, (
        f"README says {stated} tests; this run collected {collected}. "
        "Update the README, or drop the number rather than let it drift."
    )


def test_no_other_file_states_a_test_count():
    """One place to go stale is enough.

    REPRODUCING.md used to carry its own copy, which drifted separately.
    """
    reproducing = _read("REPRODUCING.md")
    assert not re.search(r"\b\d{3} tests\b", reproducing), (
        "REPRODUCING.md states a test count again. Keep the number in the "
        "README only, where one test checks it."
    )


def test_the_structural_counts_the_readme_states_match_the_code():
    readme = _read("README.md")
    goals = len(build_integrated_gsn().get_goals())
    decision_points = len(DecisionPointCatalogue().inconsistencies)
    findings = len(GapClassification().gaps)

    assert "nine-goal pattern" in readme and goals == 9
    assert f"{_word(decision_points)} decision points" in readme
    assert f"{_word(findings)} findings" in readme


def _word(number: int) -> str:
    words = {5: "five", 7: "seven", 9: "nine"}
    return words.get(number, str(number))


def test_the_readme_method_table_matches_the_code():
    """The README's five-step table states each step's output with its split.

    Those splits are the first thing a reader checks when asking why nine,
    seven or five, so they are held to the code like the totals above.
    """
    from collections import Counter

    from src.standards.registry import StandardsRegistry

    readme = _read("README.md")
    goals = build_integrated_gsn().get_goals()
    origin = Counter(goal.origin for goal in goals)
    dp_types = Counter(
        dp.inconsistency_type.value for dp in DecisionPointCatalogue().inconsistencies
    )
    gaps = GapClassification().gaps
    induced = sum(gap.integration_induced for gap in gaps)

    assert f"{len(StandardsRegistry().get_all_claims())} claims" in readme
    assert (
        f"{origin['retained']} kept, {origin['new']} added (G7, G8), "
        f"{origin['undeveloped']} left undeveloped (G9)"
    ) in readme
    assert (
        f"{dp_types['structural']} structural, {dp_types['terminological']} "
        f"terminological, {dp_types['methodological']} methodological"
    ) in readme
    assert (
        f"{induced} integration-induced, {len(gaps) - induced} open "
        "methodological problems"
    ) in readme

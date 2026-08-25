"""The ISO/PAS 8800 Annex B base pattern, and the 6-to-9 extension delta.

The WAISE paper's headline structural claim is that the integrated pattern
"extends ISO/PAS 8800 Annex B from six goals to nine". Everywhere else in this
repository that claim is narrated. This module makes it mechanical: it encodes
the six-goal base independently of the integrated builder, then computes the
delta between the two.

WHAT THE BASE IS, AND WHY IT IS ENCODED SEPARATELY

``build_annex_b_base()`` is this repository's rendering of Annex B's six-goal
structure in its pre-integration form: the AI-safety argument ISO/PAS 8800
Annex B publishes, before any claim from ISO 26262, ISO 21448 or ISO/SAE 21434
is added. Every base goal sources ISO/PAS 8800 alone, because Annex B is an
ISO/PAS 8800 artefact. The goal texts are the repository's paraphrase of each
Annex B goal's subject, not verbatim clause text; the augmented forms the paper
actually argues over live in ``integrated_pattern.py``.

The base is authored here rather than derived from the integrated pattern's own
``origin`` field on purpose. A delta computed against a base that was
back-formed from the integrated pattern would prove nothing: it would compare
the integrated pattern with itself. Encoding the six-goal base from Annex B and
then differencing it against ``build_integrated_gsn()`` is what makes "six to
nine" a checked fact rather than a stated one.

WHAT THE DELTA COMPUTES

``compute_extension_delta()`` compares the base against the integrated pattern
and reports, from the two independent encodings:

  * the goals added (G7 SOTIF, G8 cybersecurity, G9 the modification gap),
  * the goals retained (G1-G6),
  * for each retained goal, the standards its integrated form adds beyond the
    ISO/PAS 8800 base.

``tests/test_base_pattern.py`` cross-checks the computed per-goal augmentation
against the ``augmented_from`` field the integrated builder records for the four
goals that carry it, so the two representations of "what was added" must agree.
"""

from __future__ import annotations

from src.gsn.model import (
    Assumption,
    Goal,
    GSNArgument,
    Strategy,
)


def build_annex_b_base() -> GSNArgument:
    """Build the six-goal ISO/PAS 8800 Annex B base pattern.

    Six goals (G1-G6), the base strategy S1, and the assumption A1.4, all
    sourcing ISO/PAS 8800 alone. This is the AI-safety argument before the
    other three standards are integrated into it.
    """
    gsn = GSNArgument(
        name="ISO/PAS 8800 Annex B base pattern",
        description=(
            "The six-goal AI-safety assurance argument published in ISO/PAS "
            "8800 Annex B, in its pre-integration form. Every goal sources "
            "ISO/PAS 8800 alone. The integrated pattern extends this base; see "
            "src/gsn/integrated_pattern.py and src/gsn/annex_b_base.py."
        ),
    )

    a14 = Assumption(
        element_id="A1.4",
        element_type=None,
        text=(
            "Hardware random faults and systematic faults in non-AI elements "
            "are controlled by established processes."
        ),
        source_standards=["ISOPAS8800"],
        clause_references=["ISO/PAS 8800 Annex B A1.4"],
    )

    # G1's Annex B form, before the reformulation the paper describes: the AI
    # component satisfies its allocated safety requirements. The integrated
    # pattern reformulates this to add the cybersecurity concern.
    g1 = Goal(
        element_id="G1",
        element_type=None,
        text="The AI component satisfies the safety requirements allocated to it.",
        source_standards=["ISOPAS8800"],
        clause_references=["ISO/PAS 8800 Annex B G1"],
        origin="retained",
        supported_by=["S1"],
    )

    s1 = Strategy(
        element_id="S1",
        element_type=None,
        text=(
            "Argue that AI-specific insufficiencies are controlled "
            "(ISO/PAS 8800), decomposing over specification, data, design, "
            "verification and validation, and operational monitoring."
        ),
        source_standards=["ISOPAS8800"],
        clause_references=["ISO/PAS 8800 Annex B S1"],
        supported_by=["G2", "G3", "G4", "G5", "G6"],
        in_context_of=["A1.4"],
    )

    g2 = Goal(
        element_id="G2",
        element_type=None,
        text="The specification is sufficient for the AI component.",
        source_standards=["ISOPAS8800"],
        clause_references=["ISO/PAS 8800 Annex B G2 (Cl.5)"],
        origin="retained",
    )

    g3 = Goal(
        element_id="G3",
        element_type=None,
        text=(
            "Training and test data are sufficient in quantity, distribution "
            "coverage, annotation quality, and domain representativeness."
        ),
        source_standards=["ISOPAS8800"],
        clause_references=["ISO/PAS 8800 Annex B G3 (Cl.8.4)"],
        origin="retained",
    )

    g4 = Goal(
        element_id="G4",
        element_type=None,
        text="The AI design satisfies the safety requirements.",
        source_standards=["ISOPAS8800"],
        clause_references=["ISO/PAS 8800 Annex B G4 (Cl.7)"],
        origin="retained",
    )

    g5 = Goal(
        element_id="G5",
        element_type=None,
        text=(
            "Verification and validation evidence is sufficient for the AI "
            "component."
        ),
        source_standards=["ISOPAS8800"],
        clause_references=["ISO/PAS 8800 Annex B G5 (Cl.8-9)"],
        origin="retained",
    )

    g6 = Goal(
        element_id="G6",
        element_type=None,
        text=(
            "Operational monitoring covers the AI component (out-of-distribution "
            "detection, distributional drift)."
        ),
        source_standards=["ISOPAS8800"],
        clause_references=["ISO/PAS 8800 Annex B G6 (Cl.14)"],
        origin="retained",
    )

    for element in [a14, g1, s1, g2, g3, g4, g5, g6]:
        gsn.add_element(element)
    return gsn


def compute_extension_delta() -> dict:
    """Difference the integrated pattern against the Annex B base.

    Returns the goals added, the goals retained, and per retained goal the
    standards the integrated form adds beyond the ISO/PAS 8800 base. Computed
    from the two builders, not narrated.
    """
    from src.gsn.integrated_pattern import build_integrated_gsn

    base = build_annex_b_base()
    integrated = build_integrated_gsn()

    base_goal_ids = {g.element_id for g in base.get_goals()}
    integrated_goals = {g.element_id: g for g in integrated.get_goals()}

    added = sorted(set(integrated_goals) - base_goal_ids)
    retained = sorted(base_goal_ids & set(integrated_goals))

    base_sources = {g.element_id: set(g.source_standards or []) for g in base.get_goals()}

    augmentation: dict[str, list[str]] = {}
    for gid in retained:
        added_standards = set(integrated_goals[gid].source_standards or []) - base_sources[gid]
        augmentation[gid] = sorted(added_standards)

    return {
        "base_pattern": "ISO/PAS 8800 Annex B",
        "base_goal_ids": sorted(base_goal_ids),
        "base_goal_count": len(base_goal_ids),
        "integrated_goal_count": len(integrated_goals),
        "goals_retained": retained,
        "goals_added": added,
        "goals_added_count": len(added),
        "added_goal_standards": {
            gid: sorted(set(integrated_goals[gid].source_standards or []))
            for gid in added
        },
        "augmentation_of_retained_goals": augmentation,
    }


def print_extension_delta() -> None:
    """Print the 6-to-9 extension delta."""
    delta = compute_extension_delta()
    print("=" * 72)
    print("ISO/PAS 8800 ANNEX B BASE PATTERN -> INTEGRATED PATTERN")
    print("=" * 72)
    print(
        f"Base: {delta['base_pattern']}, {delta['base_goal_count']} goals "
        f"({', '.join(delta['base_goal_ids'])})."
    )
    print(
        f"Integrated: {delta['integrated_goal_count']} goals. "
        f"Added {delta['goals_added_count']}: {', '.join(delta['goals_added'])}."
    )
    print("\nGoals added:")
    for gid in delta["goals_added"]:
        stds = delta["added_goal_standards"][gid]
        print(f"  {gid}: {', '.join(stds) if stds else '(undeveloped, no source)'}")
    print("\nRetained goals, standards added beyond the ISO/PAS 8800 base:")
    for gid, stds in delta["augmentation_of_retained_goals"].items():
        print(f"  {gid}: {', '.join(stds) if stds else '(unchanged)'}")
    print("=" * 72)


if __name__ == "__main__":
    print_extension_delta()

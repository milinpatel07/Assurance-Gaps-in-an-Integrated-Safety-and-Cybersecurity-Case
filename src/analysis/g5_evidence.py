"""The four V&V evidence types at G5, and the missing rule for combining them.

This backs the G5 notebook and the G5 playground. At G5, the verification and
validation (V&V) goal, each of the four standards contributes one evidence
type on its own measurement scale. The WAISE paper's decision point DP-2 is that
the types are disjoint by design and no standard prescribes how they combine
into a single sufficiency claim at G5.

The functions here let a reader try two possible rules (all must pass; a
weighted score). Any result depends on the thresholds, weights and normalisation
the reader supplies, none of which a standard prescribes, and changing those
inputs can change the result.

The evidence types are read from ``build_integrated_gsn()`` so this module
cannot drift from the argument. Nothing here proposes a combination rule as the
standards' own; the WAISE paper leaves the method to future work and assigns the
choice to a project-level evidence admissibility policy.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.gsn.integrated_pattern import build_integrated_gsn

G5_LEG_LETTERS = ["(a)", "(b)", "(c)", "(d)"]


@dataclass(frozen=True)
class EvidenceLeg:
    """One V&V evidence type at G5, on its own measurement scale."""

    letter: str
    standard_id: str
    label: str
    scale: str
    instantiation: str
    # "higher" if a larger value is better on this scale, "lower" if smaller is
    # better. This direction is itself a reader's reading of the scale; no clause
    # fixes it. It is here so the "all must pass" attempt can run at all.
    better: str


# The reading direction of each scale, by the standard that owns the leg. These
# are the notebook reader's assumptions made explicit, not anything a clause
# states.
_BETTER = {
    "ISO26262": "higher",  # structural coverage fraction
    "ISO21448": "higher",  # triggering-condition coverage fraction
    "ISOPAS8800": "higher",  # AUROC
    "ISO21434": "lower",  # attack success rate
}


def g5_legs() -> list[EvidenceLeg]:
    """The four G5 evidence types, in the paper's Fig. 1(b) order (a) to (d)."""
    gsn = build_integrated_gsn()
    g5 = gsn.get_element("G5")
    legs = []
    for index, sid in enumerate(g5.supported_by):
        sol = gsn.get_element(sid)
        standard = next(iter(sol.source_standards or []), "")
        legs.append(
            EvidenceLeg(
                letter=G5_LEG_LETTERS[index],
                standard_id=standard,
                label=sol.text.split("(")[0].strip(),
                scale=sol.evidence_type.replace("_", " "),
                instantiation=sol.instantiation or "not stated",
                better=_BETTER.get(standard, "higher"),
            )
        )
    return legs


def scales(legs: list[EvidenceLeg] | None = None) -> list[tuple[str, str]]:
    """The four (evidence type, scale) pairs, to show they share no common unit."""
    legs = legs or g5_legs()
    return [(leg.letter, leg.scale) for leg in legs]


def combine_all_must_pass(
    values: dict[str, float], thresholds: dict[str, float]
) -> dict:
    """Attempt a verdict by requiring every leg to pass its own threshold.

    The reader supplies one value and one threshold per standard id, and the
    reading direction comes from the evidence type. The result is 'sufficient' only if every
    leg passes. Every threshold here is the reader's choice; no clause defines
    one, which is the point.
    """
    legs = {leg.standard_id: leg for leg in g5_legs()}
    per_leg = {}
    for sid, leg in legs.items():
        value = values[sid]
        threshold = thresholds[sid]
        passed = value >= threshold if leg.better == "higher" else value <= threshold
        per_leg[sid] = {
            "value": value,
            "threshold": threshold,
            "better": leg.better,
            "passed": passed,
        }
    return {
        "verdict": "sufficient" if all(p["passed"] for p in per_leg.values()) else "not sufficient",
        "per_leg": per_leg,
        "rule": "every evidence type must pass a threshold the engineer chose",
    }


def combine_weighted(
    normalised: dict[str, float], weights: dict[str, float]
) -> dict:
    """Attempt a verdict by a weighted sum of normalised leg values.

    This needs two things no clause supplies: a normalisation putting four
    different measurement scales onto one 0-to-1 axis, and a set of weights. Both
    are the reader's. Change either and the score changes.
    """
    total_weight = sum(weights.values())
    score = sum(normalised[sid] * weights[sid] for sid in normalised) / total_weight
    return {
        "score": score,
        "weights": dict(weights),
        "rule": (
            "weighted sum of normalised legs; the normalisation and the weights "
            "are the engineer's, not any standard's"
        ),
    }


def no_standard_combines_the_scales() -> dict:
    """Check that no single standard contributes more than one G5 scale.

    A repository check, consistent with decision point DP-2: in this encoding
    each evidence type at G5 is contributed by exactly one standard, so no
    standard covers two of the four scales. The paper's statement that no
    standard prescribes the combination is read from the clauses, not derived
    from this check.
    """
    legs = g5_legs()
    per_standard: dict[str, list[str]] = {}
    for leg in legs:
        per_standard.setdefault(leg.standard_id, []).append(leg.scale)
    spanning = {sid: sc for sid, sc in per_standard.items() if len(sc) > 1}
    return {
        "scales_per_standard": per_standard,
        "standards_spanning_more_than_one_scale": sorted(spanning),
        "any_standard_combines": bool(spanning),
        "derivation": (
            "Each G5 evidence type is contributed by exactly one standard, so no "
            "standard covers more than one of the four scales. This is "
            "consistent with decision point DP-2: no standard prescribes how "
            "the four combine."
        ),
    }

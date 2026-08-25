"""The four kinds of V&V evidence at G5, and why they do not combine.

This backs the G5 notebook. The point the WAISE paper makes at G5 (decision
point DP-2, finding F-4) is that four standards each require their own kind of
verification evidence there, on four measurement scales that do not convert into
one another, and no standard says how to combine them into one release verdict.

The functions here let a reader try the combination and watch it fail: any single
verdict they reach is a property of the thresholds, weights and normalisation
they themselves supplied, none of which any standard prescribes. Changing those
inputs flips the verdict, which is the lesson.

The four legs are read from ``build_integrated_gsn()`` so this module cannot
drift from the argument. Each leg is sourced by exactly one standard, which is
why ``no_standard_combines_the_scales()`` returns that no standard spans more
than one scale, so none of them combines the four.

Nothing here asserts a combination rule exists. That is the finding, and building
one would destroy it.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.gsn.integrated_pattern import build_integrated_gsn

G5_LEG_LETTERS = ["(a)", "(b)", "(c)", "(d)"]


@dataclass(frozen=True)
class EvidenceLeg:
    """One kind of V&V evidence required at G5, on its own measurement scale."""

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
    "ISO21448": "higher",  # scenario coverage count
    "ISOPAS8800": "higher",  # AUROC
    "ISO21434": "lower",  # attack success rate
}


def g5_legs() -> list[EvidenceLeg]:
    """The four G5 evidence legs, in the paper's Figure 2(b) order (a) to (d)."""
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
    """The four (leg, scale) pairs, to show they share no common unit."""
    legs = legs or g5_legs()
    return [(leg.letter, leg.scale) for leg in legs]


def combine_all_must_pass(
    values: dict[str, float], thresholds: dict[str, float]
) -> dict:
    """Attempt a verdict by requiring every leg to pass its own threshold.

    The reader supplies one value and one threshold per standard id, and the
    reading direction comes from the leg. The verdict is 'release' only if every
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
        "verdict": "release" if all(p["passed"] for p in per_leg.values()) else "hold",
        "per_leg": per_leg,
        "rule": "every leg must pass a threshold the assessor chose",
    }


def combine_weighted(
    normalised: dict[str, float], weights: dict[str, float]
) -> dict:
    """Attempt a verdict by a weighted sum of normalised leg values.

    This needs two things no clause supplies: a normalisation putting four
    incommensurable scales onto one 0-to-1 axis, and a set of weights. Both are
    the reader's. Change either and the score changes.
    """
    total_weight = sum(weights.values())
    score = sum(normalised[sid] * weights[sid] for sid in normalised) / total_weight
    return {
        "score": score,
        "weights": dict(weights),
        "rule": (
            "weighted sum of normalised legs; the normalisation and the weights "
            "are the assessor's, not any standard's"
        ),
    }


def no_standard_combines_the_scales() -> dict:
    """Derive that no single standard spans more than one G5 scale.

    Each leg is sourced by one standard, so no standard provides two of the four
    scales, so none of them defines how the four combine. This is F-4 (Gap-4)
    read off the argument rather than asserted.
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
            "Each G5 evidence leg is sourced by exactly one standard, so no "
            "standard provides more than one of the four scales, so none of them "
            "combines the four. The combining rule is missing (F-4)."
        ),
    }

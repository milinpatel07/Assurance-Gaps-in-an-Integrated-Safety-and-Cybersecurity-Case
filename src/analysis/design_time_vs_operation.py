"""Design time and operation: the two papers side by side.

Each paper reports, for its own lifecycle phase, that results from several
assurance domains (WAISE paper) or concerns (position paper) have to support a
single claim, are expressed on different measurement scales, and that no clause
in the standards examined says how to combine them. The WAISE paper reports
this at design time, at G5, the verification and validation (V&V) goal. The
position paper reports it in operation, at the re-evaluation of the assurance
argument that follows a runtime anomaly.

WHAT THIS MODULE ASSERTS, AND ON WHOSE AUTHORITY

Neither paper states the unification. This module draws it, from what both
papers state separately, and says so wherever it is displayed. It is a synthesis
made in this repository, in the same sense as the G5/G6 mapping in
``data/empirical_results/README.md``, and not a claim either paper makes.

What each paper does state, and what carries the synthesis:

  * WAISE, design time. The four evidence types at G5 are "disjoint by design"
    and "no standard defines how the disjoint evidence types combine to support
    a single sufficiency claim at G5" (DP-2).
  * Position, operation time: "the concern-specific results still meet at the
    top claim, where the evidence has different measurement scales, such as a
    calibrated probability, an ensemble disagreement value, a binary event
    indicator, or a risk rating, and no rule combines them."
  * The position paper contrasts the two settings itself: "Operation adds
    conditions that design-time analysis does not face". That sentence
    distinguishes operation from design-time analysis in general rather than
    from G5 in particular, so it supports the synthesis without
    establishing it. The position paper does cite the WAISE paper.

The design-time identifiers are read from the analysis catalogues rather than
repeated here, so they cannot drift. The operation-time entries are transcribed
from the position paper, which no code backs by design; each carries the paper
as its source.

A second, looser comparison is recorded below, on the assignment step rather
than the combination: the position paper's missing step 1 sits beside WAISE
finding F-3, the unowned adversarial-SOTIF boundary. It is looser because the
two cases differ. In F-3 the cause is known: the failure mode is both a threat
scenario and a triggering condition, and no standard allocates it to G7 or G8.
In missing step 1 the cause is not known at all. ``assignment_comparison()`` says
so, and the page repeats it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.findings import GapClassification
from src.gsn.integrated_pattern import build_integrated_gsn

PAPER_WAISE = "WAISE paper, SAFECOMP 2026 Workshops (LNCS), doi:10.1007/978-3-032-35506-5_55"
PAPER_POSITION = "Position paper, SAFECOMP 2026 (to appear)"


@dataclass(frozen=True)
class Scale:
    """One measurement scale among those that have to support the same claim."""

    label: str
    kind: str
    # None where the paper that lists the scale attributes it to no standard.
    standard: str | None


@dataclass(frozen=True)
class LifecyclePoint:
    """One of the two lifecycle phases compared."""

    point_id: str
    lifecycle: str
    where: str
    question: str
    paper: str
    paper_identifiers: list[str]
    scales: list[Scale]
    missing_rule: str
    source_note: str
    extra_conditions: list[str] = field(default_factory=list)


def _design_time_scales() -> list[Scale]:
    """The four evidence types at G5, read from the built argument."""
    gsn = build_integrated_gsn()
    g5 = gsn.get_element("G5")
    scales = []
    for sid in g5.supported_by:
        sol = gsn.get_element(sid)
        standard = next(iter(sol.source_standards or []), None)
        scales.append(
            Scale(
                label=sol.text.split("(")[0].strip(),
                kind=sol.evidence_type.replace("_", " "),
                standard=standard,
            )
        )
    return scales


# Transcribed from the position paper, which no code backs by design. The paper
# gives these four as examples ("such as") of the scales that meet at the top
# claim once an anomaly has been assigned to a concern.
#
# The paper attributes none of the four to a standard, so neither does this
# module. An earlier version assigned three of them by inference, which put a
# repository guess in the same slot as the paper-backed attributions on the
# design-time side, where a reader could not tell the two apart.
_OPERATION_SCALES = [
    Scale("Calibrated probability", "probability", None),
    Scale("Ensemble disagreement value", "disagreement value per detection", None),
    Scale("Binary event indicator", "binary indicator", None),
    Scale("Risk rating", "risk rating", None),
]


def design_time_point() -> LifecyclePoint:
    catalogue = DecisionPointCatalogue()
    gaps = GapClassification()
    dp2 = catalogue.get_by_id("I-2")
    f4 = gaps.get_by_id("Gap-4")
    return LifecyclePoint(
        point_id="design-time",
        lifecycle="Design time",
        where="G5, the verification and validation (V&V) goal",
        question=(
            "Suppose every prescribed verification activity is complete. Is "
            "the V&V evidence, taken together, sufficient?"
        ),
        paper=PAPER_WAISE,
        paper_identifiers=["DP-2"],
        scales=_design_time_scales(),
        missing_rule=(
            "No standard defines how the disjoint evidence types combine to "
            "support a single sufficiency claim at G5"
        ),
        source_note=(
            f"WAISE paper, decision point DP-2 ({dp2.description}), Table 4. "
            "A related finding concerns the release decision, F-4 (Table 5): "
            f"{' '.join(f4.description.split())}."
        ),
    )


def operation_time_point() -> LifecyclePoint:
    return LifecyclePoint(
        point_id="operation-time",
        lifecycle="Operation",
        where="Re-evaluation of the assurance argument after a runtime anomaly",
        question=(
            "A runtime monitor output is abnormal and each concern has "
            "re-evaluated. Does the assurance argument still hold?"
        ),
        paper=PAPER_POSITION,
        paper_identifiers=["Missing step 2, resolution"],
        scales=list(_OPERATION_SCALES),
        missing_rule=(
            "The concern-specific results meet at the top claim on different "
            "measurement scales, and no rule combines them"
        ),
        source_note=(
            "Position paper, missing step 2 (resolution): no clause resolves "
            "the concern-specific results into one judgement on the assurance "
            "argument. The four scales above are the paper's examples."
        ),
        extra_conditions=[
            "Evidence arrives asynchronously",
            "The component changes under updates",
            "The reporting duty requires a current judgement on demand",
        ],
    )


def shared_structure() -> list[str]:
    """What the two phases have in common. Each item holds in both."""
    return [
        "Each assurance domain or concern completes its own activity within "
        "its own scope",
        "The results are expressed on different measurement scales",
        "The results have to support a single claim",
        "No clause in the standards examined says how to combine them",
    ]


def what_differs() -> list[str]:
    """What differs. Recorded so the synthesis does not overstate."""
    return [
        "At design time the question arises before release and again after "
        "each modification (G9); in operation it recurs whenever a runtime "
        "monitor output is abnormal",
        "At design time the evidence is assembled deliberately; in operation it "
        "arrives asynchronously and the component may have changed under an update",
        "Operation carries a reporting duty that requires a current judgement on demand",
        "In operation the cause of an anomaly is unknown, so it must first be "
        "assigned to a concern; at design time the cause is known, although its "
        "allocation between G7 and G8 can still be open (DP-5)",
    ]


def assignment_comparison() -> dict[str, str]:
    """The second comparison, on the assignment step rather than the combination."""
    f3 = GapClassification().get_by_id("Gap-3")
    return {
        "design_time": " ".join(f3.description.split()),
        "design_time_identifier": "F-3",
        "operation_time": (
            "An anomaly in operational evidence carries no concern label and "
            "does not show whether the cause falls under SOTIF, AI safety or "
            "cybersecurity, and no clause performs the assignment"
        ),
        "operation_time_identifier": "Missing step 1, assignment",
        "note": (
            "This comparison is looser than the first, because the two cases "
            "differ. In the WAISE paper's F-3 the cause is known: an "
            "adversarial input that exploits a functional insufficiency is "
            "both a threat scenario and a triggering condition, yet belongs to "
            "neither G7 nor G8, because no standard allocates it. In the "
            "position paper's missing step 1 the cause is unknown: the anomaly "
            "carries no concern label at all. What they share is that a case "
            "falls between the standards' scopes and no clause assigns it."
        ),
    }


def comparison() -> dict:
    """The whole synthesis, as one object for the page and the figure."""
    return {
        "points": [design_time_point(), operation_time_point()],
        "shared": shared_structure(),
        "differs": what_differs(),
        "assignment_comparison": assignment_comparison(),
    }

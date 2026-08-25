"""The seam: one problem, two lifecycle points.

Both papers report that evidence from several concerns meets at a single point,
arrives on measurement scales that do not convert into one another, and that no
clause says how to combine it. The WAISE paper reports this at design time, at
the G5 release decision. The position paper reports it at operation time, at the
in-service re-evaluation that follows an anomaly.

WHAT THIS MODULE ASSERTS, AND ON WHOSE AUTHORITY

Neither paper states the unification. This module draws it, from what both
papers state separately, and says so wherever it is displayed. It is a synthesis
made in this repository, in the same sense as the G5/G6 mapping in
``data/empirical_results/README.md``, and not a claim either paper makes.

What each paper does state, and what carries the synthesis:

  * WAISE, design time. The four evidence types at G5 are "disjoint by design"
    and "no standard defines how the disjoint evidence types combine to support
    a single sufficiency claim at G5" (DP-2). Finding F-4 records the same
    absence at the release decision.
  * Position, operation time: "the concern-specific results still meet at the
    top claim, where the evidence has different measurement scales, such as a
    calibrated probability, an ensemble disagreement value, a binary event
    indicator, or a risk rating, and no rule combines them."
  * The position paper contrasts the two settings itself: "Operation adds
    conditions that design-time analysis does not face". That sentence
    distinguishes operation from design-time analysis in general rather than
    from the G5 junction in particular, so it supports the synthesis without
    establishing it. The position paper does cite the WAISE paper.

The design-time identifiers are read from the analysis catalogues rather than
repeated here, so they cannot drift. The operation-time entries are transcribed
from the position paper, which no code backs by design; each carries the paper
as its source.

A second, looser seam is recorded below, on the assignment step rather than the
combination: the position paper's missing step 1 sits beside WAISE finding F-3,
the unowned adversarial-SOTIF boundary. It is looser because the two cases
differ. F-3 is a boundary reached when the cause is known and belongs to two
concerns at once; missing step 1 is a boundary reached when the cause is not
known at all. ``assignment_seam()`` says so, and the page repeats it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.gsn.integrated_pattern import build_integrated_gsn

PAPER_WAISE = "paper/waise2026/camera-ready.tex"
PAPER_POSITION = "paper/safecomp2026-position/camera-ready.tex"


@dataclass(frozen=True)
class Scale:
    """One measurement scale that meets the others at the junction."""

    label: str
    kind: str
    # None where the paper that lists the scale attributes it to no standard.
    standard: str | None


@dataclass(frozen=True)
class LifecyclePoint:
    """One end of the seam."""

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
# lists these four as the scales that meet at the top claim once an anomaly has
# been assigned to a concern.
#
# The paper attributes none of the four to a standard, so neither does this
# module. An earlier version assigned three of them by inference, which put a
# repository guess in the same slot as the paper-backed attributions on the
# design-time side, where a reader could not tell the two apart.
_OPERATION_SCALES = [
    Scale("Calibrated probability", "probability", None),
    Scale("Ensemble disagreement value", "statistical metric", None),
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
        where="G5, the release decision",
        question=(
            "Every prescribed verification activity is complete. Is the "
            "evidence together enough to release?"
        ),
        paper=PAPER_WAISE,
        paper_identifiers=["DP-2", "F-4"],
        scales=_design_time_scales(),
        missing_rule=" ".join(f4.description.split()),
        source_note=(
            f"WAISE paper, decision point DP-2 ({dp2.description}) and finding "
            "F-4. The code calls them I-2 and Gap-4."
        ),
    )


def operation_time_point() -> LifecyclePoint:
    return LifecyclePoint(
        point_id="operation-time",
        lifecycle="Operation time",
        where="In-service re-evaluation, after an anomaly",
        question=(
            "A monitor output is abnormal and each concern has re-evaluated. "
            "Does the assurance argument still hold?"
        ),
        paper=PAPER_POSITION,
        paper_identifiers=["Missing step 2, resolution"],
        scales=list(_OPERATION_SCALES),
        missing_rule=(
            "Concern-specific results must meet the top claim on different "
            "measurement scales, and no rule combines them"
        ),
        source_note=(
            "Position paper, missing step 2 of two. Its figure labels this "
            "step resolution into one judgement, with no clause."
        ),
        extra_conditions=[
            "Evidence arrives asynchronously",
            "The component changes under updates",
            "The reporting duty requires a current judgement on demand",
        ],
    )


def shared_structure() -> list[str]:
    """What is the same at both ends. Each item holds at both points."""
    return [
        "Several concerns each complete their own activity within their own scope",
        "Their results land on measurement scales that do not convert into one another",
        "The results have to support a single claim at one junction",
        "No clause in any of the standards says how to combine them",
        "So the engineer can finish every prescribed activity and still not answer the question",
    ]


def what_differs() -> list[str]:
    """What is not the same. Recorded so the synthesis does not overstate."""
    return [
        "The design-time junction is reached once, before release; the "
        "operation-time one recurs whenever a monitor output is abnormal",
        "At design time the evidence is assembled deliberately; in operation it "
        "arrives asynchronously and the component may have changed under an update",
        "Operation carries a reporting duty that requires a current judgement on demand",
        "Operation needs an assignment step first, which design time does not: the "
        "anomaly carries no concern label",
    ]


def assignment_seam() -> dict[str, str]:
    """The parallel seam, on the assignment step rather than the combination."""
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
            "Setting these two beside each other is a second synthesis drawn "
            "here, and it is looser than the first. They are not the same "
            "case. The WAISE paper's F-3 is a boundary between two concerns "
            "when the cause is known: an adversarial input that exploits a "
            "functional insufficiency belongs to both, and no standard "
            "allocates it. The position paper's missing step 1 is a boundary "
            "when the cause is unknown: the anomaly carries no concern label "
            "at all. What they share is that a case falls between scopes and "
            "no clause claims it."
        ),
    }


def seam() -> dict:
    """The whole synthesis, as one object for the page and the figure."""
    return {
        "points": [design_time_point(), operation_time_point()],
        "shared": shared_structure(),
        "differs": what_differs(),
        "assignment_seam": assignment_seam(),
    }

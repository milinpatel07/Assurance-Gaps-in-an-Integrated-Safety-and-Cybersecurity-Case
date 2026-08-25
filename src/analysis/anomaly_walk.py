"""Follow a runtime anomaly clause by clause until no clause assigns it.

This is the position paper's argument, made executable. A monitor output goes
abnormal in service. Before any concern can act on it, the anomaly has to belong
to a concern. This module asks each applicable standard, at clause level,
whether it owns the anomaly, and records the answer with the clause that gives
it.

Three of the four standards answer the same way: each owns the anomaly if the
cause is of its kind. The cause is the one thing a runtime observation does not
carry. So the walk ends with no assignment, which is the position paper's
missing step 1.

WHAT THIS ASSERTS, AND ON WHOSE AUTHORITY

Each verdict restates a fact one of the papers argues, and names what it rests
on:

  * ISO 21448 Clause 1 (with Table 1) excludes cybersecurity threats and refers
    the attack case to ISO/SAE 21434. Position paper, and WAISE finding F-3.
  * ISO/SAE 21434 does not address performance insufficiency. Position paper.
  * Random hardware faults lie outside the ambiguity, because ISO 26262
    requires diagnostic mechanisms that identify them. The position paper makes
    this statement at the level of the standard and cites no clause, so neither
    does this module. An earlier version cited ISO 26262-5 Cl.9, which is the
    architectural-metrics evaluation and does not require diagnostics.
  * ISO/PAS 8800 owns the anomaly if the cause lies in the AI component itself.
    The position paper's figure puts AI-safety re-evaluation alongside the SOTIF
    and cybersecurity re-evaluations as one of three concerns.
  * ISO/PAS 8800 Clause 14 requires operational monitoring of the AI component,
    and prescribes no rule that assigns an anomaly to a concern.

WHAT THE WALK DOES NOT DO

It consults one observable, the hardware diagnostic. The other fields are
recorded because a monitor reports them, not because any clause turns them into
an assignment. A reported security event alongside the anomaly is a
co-occurrence, and no clause makes a co-occurrence a cause. The walk therefore
returns the same answer whatever those fields hold, and the notebook says so
rather than staging it as a discovery.

Knowing the cause does not always settle ownership either. Where a failure mode
is at once a triggering condition and a threat scenario, the WAISE paper finds
the boundary unowned (DP-5, finding F-3), so ``resolve_with_cause`` returns None
for that case rather than inventing an owner.

The walk is deterministic: the same observation always produces the same
verdicts in the same order.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.standards.registry import StandardsRegistry


# Used where a paper states something about a standard without citing a clause.
# Inventing a clause number to fill the column would be worse than saying so.
STANDARD_LEVEL = "(no clause cited)"


class Verdict(Enum):
    """What a standard's clauses say about owning this anomaly."""

    OWNS = "owns it"
    CONDITIONAL = "owns it only if the cause is of its kind"
    EXCLUDES = "excludes it and refers it elsewhere"
    SILENT = "prescribes no rule that assigns it"


class Cause(Enum):
    """The ground truth a runtime observation does not carry."""

    PERFORMANCE_INSUFFICIENCY = "performance insufficiency"
    ATTACK = "cybersecurity attack"
    AI_COMPONENT = "the AI component itself, for example distributional drift"
    HARDWARE_FAULT = "random hardware fault"
    # WAISE DP-5 and finding F-3: an adversarial input that exploits a
    # functional insufficiency is at once a threat scenario and a triggering
    # condition, and no standard assigns it to either goal.
    ATTACK_EXPLOITING_INSUFFICIENCY = (
        "an attack that exploits a performance insufficiency"
    )
    UNKNOWN = "not observable in service"


@dataclass(frozen=True)
class AnomalyObservation:
    """What a monitor can actually see when the alarm fires.

    Every field is something an in-service monitor reports. There is
    deliberately no field for the cause: that is the point of the walk.
    """

    description: str
    detections_dropped: bool = True
    ensemble_disagreement_high: bool = True
    hardware_diagnostic_passed: bool = True
    security_event_reported: bool = False
    adverse_weather_reported: bool = False

    # Only hardware_diagnostic_passed changes the walk. The other fields are
    # here because a monitor reports them, and because the position paper's
    # point is that the observation looks the same whatever caused it.
    def observable_summary(self) -> list[str]:
        return [
            f"Detections dropped: {self.detections_dropped}",
            f"Ensemble disagreement high: {self.ensemble_disagreement_high}",
            f"Hardware diagnostic passed: {self.hardware_diagnostic_passed}",
            f"Security event reported: {self.security_event_reported}",
            f"Adverse weather reported: {self.adverse_weather_reported}",
        ]


@dataclass(frozen=True)
class ClauseVerdict:
    """One standard's answer, and the clause that gives it."""

    standard_id: str
    standard_name: str
    clause: str
    clause_title: str
    verdict: Verdict
    reason: str

    def assigns(self) -> bool:
        return self.verdict is Verdict.OWNS


def _clause(registry: StandardsRegistry, standard_id: str, reference: str):
    standard = registry.get_standard(standard_id)
    for clause in standard.clauses:
        if clause.reference == reference:
            return standard, clause
    raise KeyError(f"{standard_id} has no clause {reference}")


def walk(observation: AnomalyObservation) -> list[ClauseVerdict]:
    """Ask each standard, in turn, whether it owns this anomaly."""
    registry = StandardsRegistry()
    verdicts: list[ClauseVerdict] = []

    # ISO 26262. Random hardware faults are outside the ambiguity because the
    # diagnostics identify them. The position paper states this at the level of
    # the standard and cites no clause, so this verdict cites none either.
    std = registry.get_standard("ISO26262")
    if observation.hardware_diagnostic_passed:
        verdicts.append(
            ClauseVerdict(
                std.standard_id, std.full_name, STANDARD_LEVEL,
                "Diagnostic mechanisms for random hardware faults",
                Verdict.SILENT,
                "The hardware diagnostic passed, so no random hardware fault is "
                "indicated. ISO 26262 identifies its own faults through "
                "diagnostic mechanisms and says nothing about an anomaly with "
                "no fault indication.",
            )
        )
    else:
        verdicts.append(
            ClauseVerdict(
                std.standard_id, std.full_name, STANDARD_LEVEL,
                "Diagnostic mechanisms for random hardware faults",
                Verdict.OWNS,
                "The hardware diagnostic failed, so a random hardware fault is "
                "indicated and ISO 26262 owns the anomaly. This is the one "
                "case the position paper puts outside the ambiguity.",
            )
        )

    # ISO 21448. Owns performance insufficiency; Clause 1 excludes attacks.
    std, clause = _clause(registry, "ISO21448", "Cl.7")
    verdicts.append(
        ClauseVerdict(
            std.standard_id, std.full_name, clause.reference, clause.title,
            Verdict.CONDITIONAL,
            "Triggering conditions and performance insufficiencies are in "
            "scope, so ISO 21448 owns the anomaly if the cause is a "
            "performance insufficiency. Nothing in the observation says "
            "whether it is.",
        )
    )
    std, clause = _clause(registry, "ISO21448", "Cl.1")
    verdicts.append(
        ClauseVerdict(
            std.standard_id, std.full_name, clause.reference, clause.title,
            Verdict.EXCLUDES,
            "Clause 1, with Table 1, excludes cybersecurity threats and refers "
            "the attack case to ISO/SAE 21434. So ISO 21448 cannot take the "
            "anomaly until something rules the attack case out.",
        )
    )

    # ISO/SAE 21434. Owns attacks; does not address performance insufficiency.
    std, clause = _clause(registry, "ISO21434", "Cl.15")
    verdicts.append(
        ClauseVerdict(
            std.standard_id, std.full_name, clause.reference, clause.title,
            Verdict.CONDITIONAL,
            "Threat analysis covers adversarial scenarios, so ISO/SAE 21434 "
            "owns the anomaly if the cause is an attack. It does not address "
            "performance insufficiency, and the observation does not say which "
            "this is.",
        )
    )

    # ISO/PAS 8800. One of the position paper's three concerns, and the source
    # of the monitoring that raised the anomaly in the first place.
    std, clause = _clause(registry, "ISOPAS8800", "Cl.14")
    verdicts.append(
        ClauseVerdict(
            std.standard_id, std.full_name, clause.reference, clause.title,
            Verdict.CONDITIONAL,
            "AI safety is one of the three concerns a re-evaluation can belong "
            "to, so ISO/PAS 8800 owns the anomaly if the cause lies in the AI "
            "component itself. Nothing in the observation says whether it does.",
        )
    )
    verdicts.append(
        ClauseVerdict(
            std.standard_id, std.full_name, clause.reference, clause.title,
            Verdict.SILENT,
            "The same clause requires the operational monitoring that produced "
            "this anomaly. It prescribes the monitoring, not a rule that "
            "assigns what the monitoring finds to a concern.",
        )
    )

    return verdicts


def assignment(verdicts: list[ClauseVerdict]) -> str | None:
    """The concern the walk assigns the anomaly to, or None."""
    owners = [v for v in verdicts if v.assigns()]
    if len(owners) == 1:
        return owners[0].standard_id
    return None


def walk_result(observation: AnomalyObservation) -> dict:
    """The walk and its outcome, as one object."""
    verdicts = walk(observation)
    assigned = assignment(verdicts)
    return {
        "observation": observation,
        "verdicts": verdicts,
        "assigned_to": assigned,
        "unassigned": assigned is None,
        "conditional_on_cause": [
            v for v in verdicts if v.verdict is Verdict.CONDITIONAL
        ],
    }


def resolve_with_cause(observation: AnomalyObservation, cause: Cause) -> str | None:
    """What the assignment would be if the cause were known.

    Operation cannot observe the cause. This function shows what knowing it
    would and would not settle.

    For a cause that falls inside one concern, it settles the assignment at
    once, which is why the position paper calls assignment a missing step
    rather than a hard problem. For a failure mode that belongs to two concerns
    at the same time, it settles nothing: the WAISE paper finds that boundary
    unowned at design time (DP-5, finding F-3), so this returns None rather
    than picking a side the standards do not.
    """
    single_owner = {
        Cause.HARDWARE_FAULT: "ISO26262",
        Cause.PERFORMANCE_INSUFFICIENCY: "ISO21448",
        Cause.ATTACK: "ISO21434",
        Cause.AI_COMPONENT: "ISOPAS8800",
    }
    return single_owner.get(cause)


# The anomaly the position paper opens with, plus variants a reader can try.
SCENARIOS: dict[str, AnomalyObservation] = {
    "detections_drop": AnomalyObservation(
        "Detections drop in one scene region while the vehicle is in service",
    ),
    "drop_with_rain_reported": AnomalyObservation(
        "The same drop, with adverse weather reported at the same time",
        adverse_weather_reported=True,
    ),
    "drop_with_security_event": AnomalyObservation(
        "The same drop, with a cybersecurity event reported at the same time",
        security_event_reported=True,
    ),
    "drop_with_both_reported": AnomalyObservation(
        "The same drop, with both adverse weather and a security event reported",
        adverse_weather_reported=True,
        security_event_reported=True,
    ),
    "hardware_fault": AnomalyObservation(
        "The same drop, with a failing hardware diagnostic",
        hardware_diagnostic_passed=False,
    ),
}

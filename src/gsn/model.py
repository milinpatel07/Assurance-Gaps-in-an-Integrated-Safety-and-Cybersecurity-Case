"""GSN data model following the GSN Community Standard v3.

GSN elements:
- Goal: a claim to be supported (rectangle)
- Strategy: reasoning connecting a goal to its sub-goals (trapezoid)
- Context: contextual information (rounded rectangle)
- Assumption: assumed to be true (ellipse)
- Solution: reference to evidence (circle)

Relationships:
- SupportedBy: goal/strategy -> sub-goals/strategies/solutions
- InContextOf: goal/strategy -> context/assumption
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GSNElementType(Enum):
    GOAL = "goal"
    STRATEGY = "strategy"
    CONTEXT = "context"
    ASSUMPTION = "assumption"
    SOLUTION = "solution"


class GoalStatus(Enum):
    """Development status of a GSN goal."""
    DEVELOPED = "developed"
    UNDEVELOPED = "undeveloped"


@dataclass
class GSNElement:
    """Base class for all GSN elements."""

    element_id: str
    element_type: GSNElementType
    text: str
    source_standards: list[str] = field(default_factory=list)
    clause_references: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class Goal(GSNElement):
    """A goal (claim) in the GSN argument.

    Attributes:
        status: Whether this goal is developed or undeveloped.
        origin: Whether this goal was retained from Annex B, added new,
                or identified as a gap.
        supported_by: IDs of sub-goals, strategies, or solutions supporting it.
        in_context_of: IDs of context or assumption elements.
        augmented_from: Standards that augment this goal beyond the base pattern.
    """

    status: GoalStatus = GoalStatus.DEVELOPED
    origin: str = "retained"  # "retained", "new", "undeveloped"
    supported_by: list[str] = field(default_factory=list)
    in_context_of: list[str] = field(default_factory=list)
    augmented_from: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.element_type = GSNElementType.GOAL


@dataclass
class Strategy(GSNElement):
    """A strategy connecting a goal to its sub-goals."""

    supported_by: list[str] = field(default_factory=list)
    in_context_of: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.element_type = GSNElementType.STRATEGY


@dataclass
class Context(GSNElement):
    """Contextual information for a goal or strategy."""

    def __post_init__(self):
        self.element_type = GSNElementType.CONTEXT


@dataclass
class Assumption(GSNElement):
    """An assumption in the argument."""

    def __post_init__(self):
        self.element_type = GSNElementType.ASSUMPTION


@dataclass
class Solution(GSNElement):
    """A reference to evidence supporting a goal.

    Attributes:
        instantiation: Whether the paper's case study produced this evidence.
            The WAISE paper's Figure 2(b) marks the G5 evidence legs: one
            "provided (simulated)", three "not produced". Empty string means
            the paper states no status for this solution.
    """

    evidence_type: str = ""
    evidence_description: str = ""
    instantiation: str = ""

    def __post_init__(self):
        self.element_type = GSNElementType.SOLUTION


@dataclass
class GSNArgument:
    """A complete GSN argument structure.

    Contains all elements and their relationships. Provides methods
    for querying the argument structure used in Steps 4 and 5.
    """

    name: str
    description: str
    elements: dict[str, GSNElement] = field(default_factory=dict)

    def add_element(self, element: GSNElement):
        self.elements[element.element_id] = element

    def get_element(self, element_id: str) -> Optional[GSNElement]:
        return self.elements.get(element_id)

    def get_goals(self) -> list[Goal]:
        return [e for e in self.elements.values() if isinstance(e, Goal)]

    def get_strategies(self) -> list[Strategy]:
        return [e for e in self.elements.values() if isinstance(e, Strategy)]

    def get_contexts(self) -> list[Context]:
        return [e for e in self.elements.values() if isinstance(e, Context)]

    def get_assumptions(self) -> list[Assumption]:
        return [e for e in self.elements.values() if isinstance(e, Assumption)]

    def get_solutions(self) -> list[Solution]:
        return [e for e in self.elements.values() if isinstance(e, Solution)]

    def get_junction_points(self) -> list[Goal]:
        """Return goals where claims from 2+ standards meet.

        These are the junction points analysed in Step 4.
        """
        return [
            g for g in self.get_goals()
            if len(g.source_standards) >= 2
        ]

    def get_undeveloped_goals(self) -> list[Goal]:
        """Return goals marked as undeveloped (gaps)."""
        return [
            g for g in self.get_goals()
            if g.status == GoalStatus.UNDEVELOPED
        ]

    def get_children(self, element_id: str) -> list[GSNElement]:
        """Return direct children of an element via SupportedBy."""
        element = self.elements.get(element_id)
        if element is None:
            return []
        child_ids = []
        if isinstance(element, (Goal, Strategy)):
            child_ids = element.supported_by
        return [self.elements[cid] for cid in child_ids if cid in self.elements]

    def get_context_elements(self, element_id: str) -> list[GSNElement]:
        """Return context/assumption elements for a goal or strategy."""
        element = self.elements.get(element_id)
        if element is None:
            return []
        ctx_ids = []
        if isinstance(element, (Goal, Strategy)):
            ctx_ids = element.in_context_of
        return [self.elements[cid] for cid in ctx_ids if cid in self.elements]

    def compute_statistics(self) -> dict:
        """Compute summary statistics of the argument structure."""
        goals = self.get_goals()
        return {
            "total_elements": len(self.elements),
            "goals": len(goals),
            "strategies": len(self.get_strategies()),
            "contexts": len(self.get_contexts()),
            "assumptions": len(self.get_assumptions()),
            "solutions": len(self.get_solutions()),
            "junction_points": len(self.get_junction_points()),
            "undeveloped_goals": len(self.get_undeveloped_goals()),
            "retained_goals": sum(1 for g in goals if g.origin == "retained"),
            "new_goals": sum(1 for g in goals if g.origin == "new"),
            "max_standards_per_goal": max(
                (len(g.source_standards) for g in goals), default=0
            ),
        }

    def print_structure(self, root_id: str = "G1", indent: int = 0):
        """Print the argument structure as an indented tree."""
        element = self.elements.get(root_id)
        if element is None:
            return

        prefix = "  " * indent
        type_label = element.element_type.value.upper()
        stds = ", ".join(element.source_standards) if element.source_standards else "---"

        # Truncate text for display
        text = element.text[:60] + "..." if len(element.text) > 60 else element.text
        print(f"{prefix}[{type_label}] {element.element_id}: {text}")
        print(f"{prefix}  Standards: {stds}")

        # Print context
        if isinstance(element, (Goal, Strategy)):
            for ctx in self.get_context_elements(element.element_id):
                ctx_text = ctx.text[:50] + "..." if len(ctx.text) > 50 else ctx.text
                print(f"{prefix}  ({ctx.element_type.value}) {ctx.element_id}: {ctx_text}")

        # Recurse into children
        if isinstance(element, (Goal, Strategy)):
            for child in self.get_children(element.element_id):
                self.print_structure(child.element_id, indent + 1)

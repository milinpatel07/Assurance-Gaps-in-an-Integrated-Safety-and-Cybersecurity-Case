"""Base classes for the standards traceability framework.

This module defines the core data model used throughout the analysis:
- Standard: represents an ISO/SAE standard with its claims and clauses
- Clause: a specific clause within a standard
- Claim: an assurance claim derived from a clause
- LifecyclePhase: enumeration of AI component lifecycle phases

The lifecycle phases follow the six-phase model defined in Section 3.2
of the paper (Table 2): Concept/Requirements, Design/Training, V&V,
Integration/Deployment, Operation/Monitoring, Modification/Re-assurance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LifecyclePhase(Enum):
    """AI component lifecycle phases as defined in Step 2 of the methodology.

    These six phases cover the complete lifecycle of an AI-based perception
    component, from initial concept through post-deployment modification.
    """

    CONCEPT = "concept_requirements"
    DESIGN = "design_training"
    VERIFICATION = "verification_validation"
    INTEGRATION = "integration_deployment"
    OPERATION = "operation_monitoring"
    MODIFICATION = "modification_reassurance"

    @property
    def display_name(self) -> str:
        names = {
            "concept_requirements": "Concept / Requirements",
            "design_training": "Design / Training",
            "verification_validation": "Verification & Validation",
            "integration_deployment": "Integration / Deployment",
            "operation_monitoring": "Operation / Monitoring",
            "modification_reassurance": "Modification / Re-assurance",
        }
        return names[self.value]


class ClaimType(Enum):
    """Classification of claim types extracted in Step 1."""

    NORMATIVE_REQUIREMENT = "shall_statement"
    WORK_PRODUCT = "work_product"
    LIFECYCLE_ACTIVITY = "lifecycle_activity"
    INFORMATIVE_GUIDANCE = "informative_guidance"


class InconsistencyType(Enum):
    """Inconsistency types as defined in Step 4 of the methodology."""

    TERMINOLOGICAL = "terminological"
    METHODOLOGICAL = "methodological"
    STRUCTURAL = "structural"


class GapType(Enum):
    """Gap types as defined in Step 5 of the methodology."""

    MISSING_CLAIM = "MC"
    MISSING_EVIDENCE = "ME"
    UNRESOLVED_INCONSISTENCY = "UI"


@dataclass
class Clause:
    """A specific clause within an ISO/SAE standard.

    Attributes:
        standard_id: Identifier of the parent standard (e.g., 'ISO26262').
        reference: Clause reference string (e.g., 'Part 3, Clause 6.4.3').
        title: Human-readable title of the clause.
        lifecycle_phases: Lifecycle phases where this clause applies.
        normative: Whether the clause is normative (True) or informative (False).
        ai_applicable: Whether the clause is applicable to AI components.
            None means applicability is not assessed.
        ai_applicability_note: Explanation of limited AI applicability.
    """

    standard_id: str
    reference: str
    title: str
    lifecycle_phases: list[LifecyclePhase] = field(default_factory=list)
    normative: bool = True
    ai_applicable: Optional[bool] = None
    ai_applicability_note: str = ""

    @property
    def full_reference(self) -> str:
        return f"{self.standard_id} {self.reference}"


@dataclass
class Claim:
    """An assurance claim derived from a standard clause.

    A claim is defined as a normative requirement ('shall' statement),
    a defined work product, or an explicitly required lifecycle activity
    that an assurance argument for the AI-based perception component
    must address (Step 1 of the methodology).

    Attributes:
        claim_id: Unique identifier (e.g., 'CLM-26262-HARA-01').
        text: The claim statement.
        source_clause: The clause from which this claim is derived.
        claim_type: Classification of the claim.
        gsn_goal: The GSN goal node this claim maps to (e.g., 'G5').
            None means the claim attaches to no node in this pattern. That is a
            defect unless out_of_scope_reason says why.
        lifecycle_phase: Primary lifecycle phase of this claim.
        evidence_types: Types of evidence required to support this claim.
        out_of_scope_reason: Why a claim with no gsn_goal is deliberately outside
            the AI-component argument rather than missing from it. The pattern is
            scoped to the AI component inside the encompassing system safety case
            (ISO 26262-2 Cl.6.4.8), so some obligations a standard imposes belong
            above that boundary. Recording the reason keeps the obligation visible
            while keeping it out of the argument, and lets the completeness check
            tell a deliberate exclusion apart from an unmapped claim.
    """

    claim_id: str
    text: str
    source_clause: Clause
    claim_type: ClaimType
    gsn_goal: Optional[str] = None
    lifecycle_phase: Optional[LifecyclePhase] = None
    evidence_types: list[str] = field(default_factory=list)
    out_of_scope_reason: str = ""

    @property
    def is_out_of_scope(self) -> bool:
        """True when the claim is deliberately outside the argument's scope."""
        return self.gsn_goal is None and bool(self.out_of_scope_reason)

    @property
    def standard_id(self) -> str:
        return self.source_clause.standard_id


@dataclass
class Inconsistency:
    """A requirement inconsistency at a junction point in the integrated GSN.

    Attributes:
        inconsistency_id: Identifier (e.g., 'I-1').
        description: Description of the inconsistency.
        inconsistency_type: Classification (terminological, methodological, structural).
        standards_involved: List of standard IDs involved.
        clause_references: Specific clause references.
        gsn_nodes: Affected GSN goal nodes.
        consequence: Description of the consequence for the integrated argument.
    """

    inconsistency_id: str
    description: str
    inconsistency_type: InconsistencyType
    standards_involved: list[str]
    clause_references: list[str]
    gsn_nodes: list[str]
    consequence: str


@dataclass
class AssuranceGap:
    """An assurance gap where no standard provides the required claim or evidence.

    Attributes:
        gap_id: Identifier (e.g., 'Gap-1').
        description: Description of the gap.
        gap_type: Classification (missing claim, missing evidence, unresolved inconsistency).
        lifecycle_phase: The lifecycle phase where the gap occurs.
        partial_coverage: Standards that provide partial coverage.
        integration_induced: Whether this gap only appears in the integrated argument.
    """

    gap_id: str
    description: str
    gap_type: GapType
    lifecycle_phase: LifecyclePhase
    partial_coverage: list[str]
    integration_induced: bool = False


@dataclass
class Standard:
    """Representation of an ISO/SAE standard with its claims and clauses.

    Attributes:
        standard_id: Short identifier (e.g., 'ISO26262').
        full_name: Full standard name.
        year: Publication year.
        scope: Brief scope description.
        clauses: List of relevant clauses.
        claims: Claims extracted from this standard (Step 1 output).
    """

    standard_id: str
    full_name: str
    year: int
    scope: str
    clauses: list[Clause] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)

    def get_claims_for_goal(self, goal_id: str) -> list[Claim]:
        """Return all claims mapped to a specific GSN goal."""
        return [c for c in self.claims if c.gsn_goal == goal_id]

    def get_claims_for_phase(self, phase: LifecyclePhase) -> list[Claim]:
        """Return all claims applicable to a specific lifecycle phase."""
        return [c for c in self.claims if c.lifecycle_phase == phase]

    def get_clauses_for_phase(self, phase: LifecyclePhase) -> list[Clause]:
        """Return all clauses applicable to a specific lifecycle phase."""
        return [c for c in self.clauses if phase in c.lifecycle_phases]

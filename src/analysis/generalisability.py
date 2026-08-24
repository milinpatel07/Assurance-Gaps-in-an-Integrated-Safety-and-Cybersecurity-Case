"""Generalisability analysis: which findings are component-specific vs. universal.

Addresses the question: How generalisable are the findings beyond the specific
LiDAR-based case study component?

The answer: the structural findings (inconsistencies I-1 through I-5, gaps
Gap-3 and Gap-4) are properties of the standards themselves, not of the
case study. They arise whenever the four standards are applied together.
The case-study-specific elements are the evidence instances, not the
structural gaps.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FindingGeneralisability:
    """Classification of a finding as universal or component-specific."""

    finding_id: str
    description: str
    scope: str  # "universal" or "component_specific"
    rationale: str
    would_apply_to: list[str] = field(default_factory=list)


def classify_finding_generalisability() -> list[FindingGeneralisability]:
    """Classify each inconsistency and gap by generalisability.

    Universal findings arise from the standards' structure and would
    appear for ANY AI-based perception component in HAD that falls
    within the scope of all four standards.

    Component-specific findings depend on the SECOND/deep ensemble
    architecture or the LiDAR modality.
    """
    return [
        # ── Inconsistencies ──────────────────────────────────────
        FindingGeneralisability(
            finding_id="I-1",
            description="Incompatible risk classification frameworks",
            scope="universal",
            rationale=(
                "ASIL, SOTIF acceptance criteria, and TARA risk values are "
                "defined by the standards themselves, not by the component. "
                "Any component under all three standards faces this."
            ),
            would_apply_to=[
                "Camera-based object detection",
                "Radar-based tracking",
                "Multi-modal fusion perception",
                "Planning and decision-making modules",
            ],
        ),
        FindingGeneralisability(
            finding_id="I-2",
            description="Evidence type asymmetry at V&V",
            scope="universal",
            rationale=(
                "The four evidence types (MC/DC, scenario coverage, AI metrics, "
                "penetration testing) are prescribed by the standards. The "
                "specific metrics differ per component, but the asymmetry "
                "(four incommensurable types at one node) is structural."
            ),
            would_apply_to=[
                "Any AI component at ASIL C or D",
                "Any perception component with cybersecurity exposure",
            ],
        ),
        FindingGeneralisability(
            finding_id="I-3",
            description="AI error terminology differs",
            scope="universal",
            rationale=(
                "Terminological differences between ISO 26262, ISO 21448, and "
                "TR 5469 exist regardless of the specific AI component."
            ),
            would_apply_to=["All AI-based automotive components"],
        ),
        FindingGeneralisability(
            finding_id="I-4",
            description="'Validation' defined differently",
            scope="universal",
            rationale=(
                "The three definitions of 'validation' are in the standards' "
                "normative sections. They do not depend on the component."
            ),
            would_apply_to=["All components under multiple standards"],
        ),
        FindingGeneralisability(
            finding_id="I-5",
            description="Cybersecurity-SOTIF boundary undefined",
            scope="universal",
            rationale=(
                "ISO 21448 Cl.1 excludes cybersecurity universally. Any component "
                "where adversarial inputs can exploit functional insufficiencies "
                "faces this boundary problem."
            ),
            would_apply_to=[
                "Camera-based detection (adversarial patches)",
                "Radar-based detection (jamming + weather)",
                "V2X communication (spoofing + functional impact)",
            ],
        ),
        FindingGeneralisability(
            finding_id="I-6",
            description="Monitoring scope overlap",
            scope="universal",
            rationale=(
                "Three monitoring regimes (AI, SOTIF, cybersecurity) operate on "
                "any deployed AI component. The overlap is structural."
            ),
            would_apply_to=["All deployed AI perception components"],
        ),
        FindingGeneralisability(
            finding_id="I-7",
            description="Data sufficiency undefined",
            scope="universal",
            rationale=(
                "No standard defines data sufficiency thresholds for any AI "
                "component, not just LiDAR detectors."
            ),
            would_apply_to=["All trained AI components"],
        ),
        # ── Gaps ─────────────────────────────────────────────────
        FindingGeneralisability(
            finding_id="Gap-1",
            description=(
                "Quantitative acceptance criteria for AI components undefined"
            ),
            scope="universal",
            rationale=(
                "Hardware metrics (SPFM, LFM, PMHF) exist at all ASIL levels. "
                "No equivalent AI metric exists at any ASIL level."
            ),
            would_apply_to=["All AI components at any ASIL"],
        ),
        FindingGeneralisability(
            finding_id="Gap-2",
            description="No OTA re-assurance workflow",
            scope="universal",
            rationale=(
                "Any retrained neural network changes its entire weight space. "
                "The re-assurance gap applies to all AI components, not just "
                "the SECOND detector."
            ),
            would_apply_to=["All AI components receiving OTA updates"],
        ),
        FindingGeneralisability(
            finding_id="Gap-3",
            description="Adversarial-SOTIF boundary unowned",
            scope="universal",
            rationale=(
                "Integration-induced. Arises from ISO 21448 Cl.1 scope exclusion "
                "combined with ISO/SAE 21434 scope inclusion. The specific attack "
                "vectors differ (LiDAR spoofing vs. adversarial patches vs. radar "
                "jamming) but the boundary problem is the same."
            ),
            would_apply_to=[
                "Camera: adversarial patches exploiting weather sensitivity",
                "Radar: jamming exploiting clutter sensitivity",
                "LiDAR: spoofing exploiting density sensitivity",
            ],
        ),
        FindingGeneralisability(
            finding_id="Gap-4",
            description="No cross-domain release criteria",
            scope="universal",
            rationale=(
                "Integration-induced. No standard defines a combined release "
                "decision for any component. This gap exists for every component "
                "that falls under multiple standards."
            ),
            would_apply_to=["All components under ISO 26262 + ISO 21448 + ISO/SAE 21434"],
        ),
        FindingGeneralisability(
            finding_id="Gap-5",
            description="Data acceptance threshold undefined",
            scope="universal",
            rationale=(
                "No domain-specific data sufficiency thresholds exist for any "
                "AI perception modality."
            ),
            would_apply_to=["All trained AI components"],
        ),
    ]


def get_generalisability_summary() -> dict:
    """Summarise how many findings are universal vs. component-specific."""
    findings = classify_finding_generalisability()
    universal = [f for f in findings if f.scope == "universal"]
    specific = [f for f in findings if f.scope == "component_specific"]
    return {
        "total_findings": len(findings),
        "universal": len(universal),
        "component_specific": len(specific),
        "universal_fraction": len(universal) / len(findings) if findings else 0,
        "universal_ids": [f.finding_id for f in universal],
        "specific_ids": [f.finding_id for f in specific],
    }


def print_generalisability_analysis():
    """Print the generalisability analysis."""
    findings = classify_finding_generalisability()
    summary = get_generalisability_summary()

    print("=" * 80)
    print("GENERALISABILITY ANALYSIS")
    print("=" * 80)
    print(f"\n  {summary['universal']}/{summary['total_findings']} findings are "
          f"universal (arise from standard structure, not component choice)")
    print(f"  {summary['component_specific']}/{summary['total_findings']} are "
          f"component-specific")
    print()

    for f in findings:
        marker = "U" if f.scope == "universal" else "C"
        print(f"  [{marker}] {f.finding_id}: {f.description}")
        print(f"      Rationale: {f.rationale[:80]}...")
        if f.would_apply_to:
            print(f"      Also applies to: {', '.join(f.would_apply_to[:3])}")
        print()

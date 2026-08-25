"""Base pattern sensitivity analysis.

Addresses the question: How would the findings change if a different base
pattern (e.g., AMLAS or SACE) were used instead of Annex B?

The answer: The structural findings (I-1, I-2, I-5, Gap-3, Gap-4) are
base-pattern-independent because they arise from the standards' scope
boundaries and evidence requirements, not from the organising principle
of the argument structure. The specific goal numbering and decomposition
would differ, but the same junction-point conflicts would surface.

The comparison in this module is qualitative: the ``would_detect_*`` flags are
hand-set judgments about four published frameworks. For the two
integration-induced findings (Gap-3, Gap-4) against the one alternative the
WAISE paper names, the Warg & Skoglund concern hierarchy, the answer is instead
*derived* from the standards' scope structure in
``src/analysis/topology_sensitivity.py``, so "not an artefact of the tree" is a
computed result there rather than an assertion here.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BasePatternComparison:
    """Comparison of how findings manifest under a different base pattern."""

    pattern_name: str
    organising_principle: str
    goals_structure: str
    would_detect_i1: bool
    would_detect_i2: bool
    would_detect_i5: bool
    would_detect_gap3: bool
    would_detect_gap4: bool
    limitations: list[str] = field(default_factory=list)
    advantages: list[str] = field(default_factory=list)


def compare_base_patterns() -> list[BasePatternComparison]:
    """Compare how key findings would manifest under alternative base patterns."""
    return [
        BasePatternComparison(
            pattern_name="ISO/PAS 8800 Annex B (this work)",
            organising_principle="Assurance activity (what was done)",
            goals_structure="G1-G6 by activity, extended to G7-G9",
            would_detect_i1=True,
            would_detect_i2=True,
            would_detect_i5=True,
            would_detect_gap3=True,
            would_detect_gap4=True,
            advantages=[
                "Designed specifically for AI components in road vehicles",
                "Direct clause-level traceability to ISO/PAS 8800",
                "Natural extension point for additional standards",
            ],
            limitations=[
                "Activity-based decomposition may obscure risk-based reasoning",
                "Not all reviewers familiar with ISO/PAS 8800",
            ],
        ),
        BasePatternComparison(
            pattern_name="ISO 21448 Annex A.1",
            organising_principle="Risk reduction (what was achieved)",
            goals_structure="Four-area model with risk reduction goals",
            would_detect_i1=True,
            would_detect_i2=True,
            would_detect_i5=True,
            would_detect_gap3=True,
            would_detect_gap4=True,
            advantages=[
                "Risk-based organising principle aligns with acceptance criteria",
                "Natural fit for SOTIF claims (ISO 21448 Cl.6.5)",
            ],
            limitations=[
                "No AI-specific goals (data quality, uncertainty quantification)",
                "Would require adding equivalent of G3 (data) from scratch",
                "Cybersecurity exclusion in ISO 21448 Cl.1 means G8 must still "
                "be created outside the base pattern",
            ],
        ),
        BasePatternComparison(
            pattern_name="AMLAS (Hawkins et al., 2021)",
            organising_principle="ML lifecycle stages",
            goals_structure="Six stages: requirements, data, model, V&V, deployment, operation",
            would_detect_i1=True,
            would_detect_i2=True,
            would_detect_i5=False,  # No cybersecurity in AMLAS
            would_detect_gap3=False,  # Only with cybersecurity integration
            would_detect_gap4=True,
            advantages=[
                "Mature framework with published guidance",
                "Strong data and model lifecycle coverage",
                "Used in practice (SMIRK case study by Borg et al.)",
            ],
            limitations=[
                "No cybersecurity claims — cannot detect I-5 or Gap-3 "
                "without extension",
                "Not automotive-specific (no ASIL, no SOTIF)",
                "Would require adding automotive standard claims",
            ],
        ),
        BasePatternComparison(
            pattern_name="SACE (Hawkins et al., 2022)",
            organising_principle="Operational context and system autonomy",
            goals_structure="Environment, system behaviour, safety constraints",
            would_detect_i1=True,
            would_detect_i2=True,
            would_detect_i5=False,  # No cybersecurity
            would_detect_gap3=False,
            would_detect_gap4=True,
            advantages=[
                "Context-aware: distinguishes operational environments",
                "Designed for autonomous systems in complex environments",
            ],
            limitations=[
                "Conceptual framework without clause-level traceability",
                "No cybersecurity or SOTIF coverage",
                "No AI-specific data or uncertainty goals",
            ],
        ),
    ]


def get_base_pattern_invariants() -> dict:
    """Identify which findings are base-pattern-invariant.

    A finding is base-pattern-invariant if it would be detected regardless
    of which base pattern is chosen, as long as all four standards are
    integrated.
    """
    patterns = compare_base_patterns()

    # A finding is invariant if ALL patterns that include the relevant
    # standards would detect it
    findings = {
        "I-1": "Incompatible risk classification",
        "I-2": "Evidence type asymmetry",
        "I-5": "Cybersecurity-SOTIF boundary",
        "Gap-3": "Adversarial-SOTIF boundary",
        "Gap-4": "Cross-domain release criteria",
    }

    invariants = {}
    for fid, desc in findings.items():
        attr = f"would_detect_{fid.lower().replace('-', '')}"
        # Check only patterns that include cybersecurity (for I-5, Gap-3)
        detected_by_all_complete = all(
            getattr(p, attr) for p in patterns
            if "cybersecurity" not in " ".join(p.limitations).lower()
            or attr not in ("would_detect_i5", "would_detect_gap3")
        )
        invariants[fid] = {
            "description": desc,
            "invariant": detected_by_all_complete,
            "detected_by": [
                p.pattern_name for p in patterns if getattr(p, attr)
            ],
            "missed_by": [
                p.pattern_name for p in patterns if not getattr(p, attr)
            ],
        }

    return invariants


def print_base_pattern_comparison():
    """Print the base pattern comparison."""
    patterns = compare_base_patterns()
    invariants = get_base_pattern_invariants()

    print("=" * 80)
    print("BASE PATTERN SENSITIVITY ANALYSIS")
    print("=" * 80)

    for p in patterns:
        print(f"\n{'─' * 80}")
        print(f"  {p.pattern_name}")
        print(f"  Organising principle: {p.organising_principle}")
        print(f"  Would detect: ", end="")
        detects = []
        if p.would_detect_i1:
            detects.append("I-1")
        if p.would_detect_i2:
            detects.append("I-2")
        if p.would_detect_i5:
            detects.append("I-5")
        if p.would_detect_gap3:
            detects.append("Gap-3")
        if p.would_detect_gap4:
            detects.append("Gap-4")
        print(", ".join(detects))

    print(f"\n{'=' * 80}")
    print("BASE-PATTERN-INVARIANT FINDINGS:")
    for fid, info in invariants.items():
        status = "INVARIANT" if info["invariant"] else "PATTERN-DEPENDENT"
        print(f"  [{status}] {fid}: {info['description']}")
        if info["missed_by"]:
            print(f"    Missed by: {', '.join(info['missed_by'])}")
    print("=" * 80)

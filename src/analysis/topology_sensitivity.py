"""Are the integration-induced findings an artefact of the argument tree?

The WAISE paper names one alternative to its flat, activity-based decomposition:
the concern hierarchy of Warg and Skoglund, in which functional safety and SOTIF
are sub-concerns of safety and cybersecurity is a co-concern. The paper retains
the flat structure and gives its reason (it keeps each leg traceable to one
standard's clauses), but it does not say whether its two integration-induced
findings, F-3 and F-4, would survive the alternative. A sceptical reader asks
exactly that: did these findings come out of the standards, or out of the way the
authors drew the tree?

This module answers it in the repository, by deriving the two findings under two
topologies rather than asserting the answer.

WHAT IS DERIVED, AND FROM WHAT

Both findings are read from the standards' scope structure, which no choice of
tree changes:

  * F-3 (adversarial-SOTIF boundary) arises where the SOTIF concern and the
    cybersecurity concern are owned by disjoint standards, so no single assessor
    holds both ends of the boundary. Whether that holds depends on which
    standards own SOTIF and cybersecurity, not on where the boundary is drawn.
  * F-4 (cross-domain release combination) arises where more than one standard's
    evidence must meet at one node and no single standard combines them. Whether
    that holds depends on how many standards contribute at the meeting point,
    not on which node it is.

Each topology assigns standards to nodes; the derivation then reads the two
findings off those assignments. The activity-based topology's assignments are
read from ``build_integrated_gsn()``. The concern-hierarchy topology's
assignments are encoded here from the paper's description of Warg and Skoglund,
grouping each standard by its subject (ISO 26262 functional safety, ISO 21448
SOTIF, ISO/PAS 8800 AI safety, ISO/SAE 21434 cybersecurity). The paper places
functional safety and SOTIF under safety and cybersecurity as a co-concern; it
does not place AI safety, so putting it under safety is this repository's
reading and is marked as such.

THE HONEST HAZARD

If a finding had come out present under one topology and absent under the other,
that would weaken the paper's retention argument, and this module would report
it. It does not tune the topologies to agree. The result below is what the
derivation returns.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Topology:
    """A top-level argument structure as an assignment of standards to nodes."""

    name: str
    organising_principle: str
    provenance: str
    node_standards: dict[str, frozenset[str]]
    # The two nodes whose boundary F-3 sits on: the SOTIF-scoped node and the
    # cybersecurity-scoped node.
    gap3_boundary: tuple[str, str]
    # The node where cross-domain evidence must combine (F-4).
    gap4_combination_node: str


def activity_based_topology() -> Topology:
    """This work: standards assigned to nodes by assurance activity.

    Read from the integrated builder, so it cannot drift from the pattern the
    repository actually holds.
    """
    from src.gsn.integrated_pattern import build_integrated_gsn

    goals = {g.element_id: frozenset(g.source_standards or []) for g in build_integrated_gsn().get_goals()}
    return Topology(
        name="Activity-based (this work)",
        organising_principle="Assurance activity: specification, data, design, V&V, monitoring",
        provenance="Node standards read from build_integrated_gsn().",
        node_standards={
            "G5 (V&V)": goals["G5"],
            "G7 (SOTIF residual risk)": goals["G7"],
            "G8 (cybersecurity treatment)": goals["G8"],
        },
        gap3_boundary=("G7 (SOTIF residual risk)", "G8 (cybersecurity treatment)"),
        gap4_combination_node="G5 (V&V)",
    )


def concern_hierarchy_topology() -> Topology:
    """Warg and Skoglund: standards assigned to nodes by concern.

    Encoded from the paper's description (line 233): functional safety and SOTIF
    as sub-concerns of safety, cybersecurity as a co-concern, meeting at the top
    claim. Each standard is grouped by its subject. AI safety (ISO/PAS 8800) is
    placed under safety here; the paper does not place it, so that is this
    repository's reading.
    """
    return Topology(
        name="Concern hierarchy (Warg & Skoglund)",
        organising_principle="Concern: safety (functional safety, SOTIF, AI safety) and cybersecurity",
        provenance=(
            "Encoded from the WAISE paper's description of Warg & Skoglund "
            "(concern hierarchy). AI-safety placement under safety is this "
            "repository's reading; the paper does not place it."
        ),
        node_standards={
            "Functional safety": frozenset({"ISO26262"}),
            "SOTIF": frozenset({"ISO21448"}),
            "AI safety": frozenset({"ISOPAS8800"}),
            "Cybersecurity": frozenset({"ISO21434"}),
            "Top claim (safety and cybersecurity)": frozenset(
                {"ISO26262", "ISO21448", "ISOPAS8800", "ISO21434"}
            ),
        },
        gap3_boundary=("SOTIF", "Cybersecurity"),
        gap4_combination_node="Top claim (safety and cybersecurity)",
    )


def topologies() -> list[Topology]:
    return [activity_based_topology(), concern_hierarchy_topology()]


def derive_gap3(topology: Topology) -> dict:
    """F-3 arises where the SOTIF and cybersecurity nodes share no standard."""
    sotif_node, cyber_node = topology.gap3_boundary
    sotif = topology.node_standards[sotif_node]
    cyber = topology.node_standards[cyber_node]
    spanning = sorted(sotif & cyber)
    return {
        "finding": "F-3 (adversarial-SOTIF boundary)",
        "sotif_node": sotif_node,
        "cybersecurity_node": cyber_node,
        "sotif_standards": sorted(sotif),
        "cybersecurity_standards": sorted(cyber),
        "standards_spanning_both": spanning,
        "arises": spanning == [],
        "derivation": (
            "The boundary belongs to no single assessor when no standard owns "
            "both the SOTIF node and the cybersecurity node."
        ),
    }


def derive_gap4(topology: Topology) -> dict:
    """F-4 arises where more than one standard must combine at one node."""
    node = topology.gap4_combination_node
    contributors = sorted(topology.node_standards[node])
    # Plurality premise (as in counterfactual.py): a cross-domain combining
    # question is posed only where more than one standard contributes at a node.
    # Restricted to any single standard, one standard contributes, so no
    # standard combines the scales by itself.
    return {
        "finding": "F-4 (cross-domain release combination)",
        "combination_node": node,
        "contributors": contributors,
        "contributor_count": len(contributors),
        "arises": len(contributors) > 1,
        "derivation": (
            f"{len(contributors)} standards meet at {node}, on scales that do "
            "not convert; no single standard combines them."
        ),
    }


def topology_report() -> dict:
    """Derive F-3 and F-4 under both topologies and answer the tree question."""
    results = []
    for topology in topologies():
        results.append(
            {
                "topology": topology.name,
                "organising_principle": topology.organising_principle,
                "provenance": topology.provenance,
                "gap3": derive_gap3(topology),
                "gap4": derive_gap4(topology),
            }
        )

    gap3_invariant = all(r["gap3"]["arises"] for r in results)
    gap4_invariant = all(r["gap4"]["arises"] for r in results)
    both_invariant = gap3_invariant and gap4_invariant

    return {
        "topologies": results,
        "gap3_arises_under_every_topology": gap3_invariant,
        "gap4_arises_under_every_topology": gap4_invariant,
        "findings_are_an_artefact_of_the_tree": not both_invariant,
        "answer": (
            "F-3 and F-4 arise under both the activity-based tree and the "
            "concern hierarchy, so they are not an artefact of the chosen "
            "topology; only the location of the junction moves."
            if both_invariant
            else "At least one finding is topology-dependent; see the per-topology "
            "results. This weakens the paper's retention argument and must be "
            "raised with the authors."
        ),
    }


def print_topology_report() -> None:
    """Print the derived topology-sensitivity result."""
    report = topology_report()
    print("=" * 72)
    print("ARE F-3 AND F-4 AN ARTEFACT OF THE ARGUMENT TREE?")
    print("=" * 72)
    for result in report["topologies"]:
        print(f"\n{result['topology']}")
        print(f"  Organising principle: {result['organising_principle']}")
        g3 = result["gap3"]
        g4 = result["gap4"]
        print(
            f"  F-3 arises: {g3['arises']} "
            f"(SOTIF {g3['sotif_standards']} vs cyber "
            f"{g3['cybersecurity_standards']}, shared {g3['standards_spanning_both'] or 'none'})"
        )
        print(
            f"  F-4 arises: {g4['arises']} "
            f"({g4['contributor_count']} standards meet at {g4['combination_node']})"
        )
    print(f"\n{'-' * 72}")
    print(f"F-3 invariant across topologies: {report['gap3_arises_under_every_topology']}")
    print(f"F-4 invariant across topologies: {report['gap4_arises_under_every_topology']}")
    print(f"\n{report['answer']}")
    print("=" * 72)


if __name__ == "__main__":
    print_topology_report()

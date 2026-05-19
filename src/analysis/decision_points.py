"""Decision point analysis (Step 4 of the methodology).

Implements junction-point analysis: examines each node in the integrated GSN
where claims from two or more standards meet, identifying decision points
where the standards defer to application context instead of prescribing a
single requirement on the AI component.

Three decision point types (Section 3.2, Step 4):
- Terminological: different terms for the same concept
- Methodological: different methods for the same assurance objective
- Structural: different risk classification or evidence frameworks
"""

from __future__ import annotations

from src.standards.base import Inconsistency, InconsistencyType


class DecisionPointCatalogue:
    """The seven decision points identified in the analysis.

    Each decision point corresponds to a row in Table 5 of the paper.
    """

    def __init__(self):
        self.inconsistencies = self._build_catalogue()

    def _build_catalogue(self) -> list[Inconsistency]:
        return [
            Inconsistency(
                inconsistency_id="I-1",
                description="Incompatible risk classification frameworks",
                inconsistency_type=InconsistencyType.STRUCTURAL,
                standards_involved=["ISO26262", "ISO21448", "ISO21434"],
                clause_references=[
                    "ISO 26262-3 Cl.6 (ASIL A-D: severity x exposure x controllability)",
                    "ISO 21448 Cl.6.5 (qualitative acceptance criteria, no severity scale)",
                    "ISO/SAE 21434 Cl.15.8 (risk value 1-5: impact x attack feasibility)",
                ],
                gsn_nodes=["G1"],
                consequence=(
                    "Three risk frameworks use different scales, different input "
                    "parameters, and different threshold definitions. The case study "
                    "component receives ASIL D (ISO 26262), a project-specific "
                    "residual risk threshold (ISO 21448), and a set of risk values "
                    "per threat scenario (ISO/SAE 21434). No standard defines how "
                    "to reconcile these into a single sufficiency judgement at G1."
                ),
            ),
            Inconsistency(
                inconsistency_id="I-2",
                description="Evidence type asymmetry at V&V",
                inconsistency_type=InconsistencyType.STRUCTURAL,
                standards_involved=["ISO26262", "ISO21448", "ISOPAS8800", "ISO21434"],
                clause_references=[
                    "ISO 26262-6 Cl.9 (MC/DC structural coverage at ASIL D)",
                    "ISO 21448 Cl.9-11 (scenario-based testing, triggering conditions)",
                    "ISO/PAS 8800 Cl.8-9 (AI metrics, uncertainty quantification)",
                    "ISO/SAE 21434 Cl.10 (vulnerability analysis, penetration testing)",
                ],
                gsn_nodes=["G5"],
                consequence=(
                    "Four evidence types differ in what they measure (code structure, "
                    "scenario space, model confidence, attacker capability), how they "
                    "are produced (static analysis, simulation, inference, red-teaming), "
                    "and what scale they use (binary, count, probability, rate). "
                    "No standard defines how they combine into a single sufficiency "
                    "claim at G5. THIS IS THE CENTRAL FINDING OF THE ANALYSIS."
                ),
            ),
            Inconsistency(
                inconsistency_id="I-3",
                description="AI error terminology differs across standards",
                inconsistency_type=InconsistencyType.TERMINOLOGICAL,
                standards_involved=["ISO26262", "ISO21448", "TR5469"],
                clause_references=[
                    "ISO 26262-1 Cl.1 (malfunction/fault scope — AI errors outside scope)",
                    "ISO 21448 Cl.3 (functional insufficiency)",
                    "ISO/IEC TR 5469 Cl.6.1 (systematic failure)",
                ],
                gsn_nodes=["G2", "G7"],
                consequence=(
                    "The same AI behavioural error (e.g., missed detection) is: "
                    "a systematic failure (TR 5469), a functional insufficiency "
                    "(ISO 21448), and falls outside scope (ISO 26262, which "
                    "addresses malfunctions only). This creates ambiguity about "
                    "which assurance domain owns the error."
                ),
            ),
            Inconsistency(
                inconsistency_id="I-4",
                description="'Validation' defined differently across standards",
                inconsistency_type=InconsistencyType.TERMINOLOGICAL,
                standards_involved=["ISO26262", "ISO21448", "ISOPAS8800"],
                clause_references=[
                    "ISO 26262-1 Cl.1.122 (confirmation of intended use)",
                    "ISO 21448 Cl.3.37 (verification of SOTIF activities)",
                    "ISO/PAS 8800 Cl.3 (AI validation definition)",
                ],
                gsn_nodes=["G5"],
                consequence=(
                    "The term 'validation' has different definitions. A single V&V "
                    "plan must clarify which definition applies at each point."
                ),
            ),
            Inconsistency(
                inconsistency_id="I-5",
                description="Cybersecurity-SOTIF boundary undefined for adversarial inputs",
                inconsistency_type=InconsistencyType.STRUCTURAL,
                standards_involved=["ISO21448", "ISO21434", "TR5469"],
                clause_references=[
                    "ISO 21448 Cl.1 (explicitly excludes cybersecurity threats)",
                    "ISO/SAE 21434 Cl.15 (includes adversarial threat scenarios)",
                    "ISO/IEC TR 5469 Cl.8.5.1 NOTE 2 (security contradicts safety)",
                ],
                gsn_nodes=["G7", "G8"],
                consequence=(
                    "Adversarial point cloud perturbations cause false negatives: "
                    "simultaneously a cybersecurity threat (ISO/SAE 21434) and a "
                    "triggering condition (ISO 21448). The boundary between G7 "
                    "and G8 is undefined. No standard provides guidance for this "
                    "ownership decision."
                ),
            ),
            Inconsistency(
                inconsistency_id="I-6",
                description="Monitoring scope overlap — three regimes on one component",
                inconsistency_type=InconsistencyType.METHODOLOGICAL,
                standards_involved=["ISO21448", "ISO21434", "ISOPAS8800"],
                clause_references=[
                    "ISO 21448 Cl.13 (SOTIF field monitoring)",
                    "ISO/SAE 21434 Cl.8 (continuous cybersecurity monitoring)",
                    "ISO/PAS 8800 Cl.14 (AI operational monitoring, OOD detection)",
                ],
                gsn_nodes=["G6"],
                consequence=(
                    "Three monitoring scopes operate on the same deployed component "
                    "without defined coordination. The same anomaly (e.g., sudden "
                    "increase in missed detections) could be classified as AI "
                    "distributional shift, a new SOTIF triggering condition, or an "
                    "adversarial attack. No standard defines interaction rules."
                ),
            ),
            Inconsistency(
                inconsistency_id="I-7",
                description="Data sufficiency threshold undefined",
                inconsistency_type=InconsistencyType.METHODOLOGICAL,
                standards_involved=["ISOPAS8800", "TR5469"],
                clause_references=[
                    "ISO/PAS 8800 Cl.8.4 (data quality requirements)",
                    "ISO/IEC TR 5469 Cl.9.3.2 (data distributions linked to HARA)",
                ],
                gsn_nodes=["G3"],
                consequence=(
                    "No operationalised threshold for when training data are "
                    "sufficient. ISO/PAS 8800 requires data quality but prescribes "
                    "no numerical threshold. TR 5469 links data to HARA risks but "
                    "without normative force."
                ),
            ),
        ]

    def get_by_id(self, inconsistency_id: str) -> Inconsistency | None:
        for i in self.inconsistencies:
            if i.inconsistency_id == inconsistency_id:
                return i
        return None

    def get_by_type(self, itype: InconsistencyType) -> list[Inconsistency]:
        return [i for i in self.inconsistencies if i.inconsistency_type == itype]

    def get_structural(self) -> list[Inconsistency]:
        return self.get_by_type(InconsistencyType.STRUCTURAL)

    def get_for_goal(self, goal_id: str) -> list[Inconsistency]:
        return [i for i in self.inconsistencies if goal_id in i.gsn_nodes]

    def print_catalogue(self):
        """Print the decision point catalogue (Table 5)."""
        print("=" * 80)
        print("REQUIREMENT INCONSISTENCIES (Step 4 Output — Table 5)")
        print("=" * 80)

        type_labels = {
            InconsistencyType.TERMINOLOGICAL: "T",
            InconsistencyType.METHODOLOGICAL: "M",
            InconsistencyType.STRUCTURAL: "S",
        }

        for inc in self.inconsistencies:
            tl = type_labels[inc.inconsistency_type]
            stds = ", ".join(inc.standards_involved)
            nodes = ", ".join(inc.gsn_nodes)
            print(f"\n{inc.inconsistency_id} [{tl}] — {inc.description}")
            print(f"  Standards: {stds}")
            print(f"  GSN nodes: {nodes}")
            print(f"  Clauses:")
            for ref in inc.clause_references:
                print(f"    - {ref}")
            print(f"  Consequence: {inc.consequence[:120]}...")

    def summary_statistics(self) -> dict:
        return {
            "total": len(self.inconsistencies),
            "terminological": len(self.get_by_type(InconsistencyType.TERMINOLOGICAL)),
            "methodological": len(self.get_by_type(InconsistencyType.METHODOLOGICAL)),
            "structural": len(self.get_by_type(InconsistencyType.STRUCTURAL)),
        }

"""Analysis engine for inconsistencies, gaps, and traceability (Steps 4-5)."""

from src.analysis.decision_points import DecisionPointCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis
from src.analysis.traceability import TraceabilityMatrix
from src.analysis.sensitivity import run_sensitivity_analysis
from src.analysis.completeness import check_gsn_completeness
from src.analysis.counterfactual import CounterfactualAnalysis
from src.analysis.generalisability import classify_finding_generalisability
from src.analysis.base_pattern_sensitivity import compare_base_patterns
from src.analysis.practitioner_guidance import build_practitioner_guidance

__all__ = [
    "DecisionPointCatalogue",
    "GapClassification",
    "EvidenceConvergenceAnalysis",
    "TraceabilityMatrix",
    "run_sensitivity_analysis",
    "check_gsn_completeness",
    "CounterfactualAnalysis",
    "classify_finding_generalisability",
    "compare_base_patterns",
    "build_practitioner_guidance",
]

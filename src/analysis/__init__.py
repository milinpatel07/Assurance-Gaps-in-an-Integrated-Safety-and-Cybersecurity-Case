"""Analysis engine for inconsistencies, gaps, and traceability (Steps 4-5)."""

from src.analysis.inconsistencies import InconsistencyCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis
from src.analysis.traceability import TraceabilityMatrix
from src.analysis.sensitivity import run_sensitivity_analysis

__all__ = [
    "InconsistencyCatalogue",
    "GapClassification",
    "EvidenceConvergenceAnalysis",
    "TraceabilityMatrix",
    "run_sensitivity_analysis",
]

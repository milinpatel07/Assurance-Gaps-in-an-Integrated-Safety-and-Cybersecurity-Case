"""Analysis engine for inconsistencies and gaps (Steps 4-5)."""

from src.analysis.inconsistencies import InconsistencyCatalogue
from src.analysis.gaps import GapClassification
from src.analysis.evidence_convergence import EvidenceConvergenceAnalysis

__all__ = [
    "InconsistencyCatalogue",
    "GapClassification",
    "EvidenceConvergenceAnalysis",
]

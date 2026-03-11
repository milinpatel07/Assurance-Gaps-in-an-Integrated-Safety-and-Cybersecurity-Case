"""Goal Structuring Notation (GSN) model and construction.

Provides data structures for GSN elements (goals, strategies, contexts,
assumptions, solutions) and the constructive integration process (Step 3).
"""

from src.gsn.model import (
    GSNElement,
    Goal,
    Strategy,
    Context,
    Assumption,
    Solution,
    GSNArgument,
)
from src.gsn.integrated_pattern import build_integrated_gsn

__all__ = [
    "GSNElement",
    "Goal",
    "Strategy",
    "Context",
    "Assumption",
    "Solution",
    "GSNArgument",
    "build_integrated_gsn",
]

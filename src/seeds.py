"""Every random seed in the repository, in one place.

The synthetic illustration pipeline and the sensitivity analysis are the only
consumers of randomness. Both read their seeds from here, and the run manifest
records these values, so a reproduction can state exactly what it ran.

Changing a value here changes the committed reference outputs under
``data/synthetic_illustrations/``; the drift check in the Makefile and CI will
fail until the references are regenerated, which is a decision, not a chore.
"""

from __future__ import annotations

# The seed behind every committed reference output (data/synthetic_illustrations/)
# and the default for generate_all, the evaluator, and the Makefile's SEED.
DEFAULT_SEED = 42

# Scenes per weather condition in the synthetic illustration.
DEFAULT_SCENES = 50

# The five seeds of the multi-seed sensitivity analysis (src/analysis/sensitivity.py).
SENSITIVITY_SEEDS = [42, 123, 256, 512, 1024]

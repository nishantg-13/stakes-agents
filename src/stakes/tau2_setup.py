"""Point tau2 at the pinned data checkout *before* tau2 is imported anywhere.

tau2 reads TAU2_DATA_DIR at import time (tau2/utils/utils.py), so import this module first.
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TAU2_DATA = REPO_ROOT / "vendor" / "tau2-bench" / "data"
TAU2_COMMIT = "033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f"

os.environ.setdefault("TAU2_DATA_DIR", str(TAU2_DATA))

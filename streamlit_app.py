"""Streamlit Community Cloud entry point.

Streamlit Cloud looks for `streamlit_app.py` at the repository root by default,
so keeping it here means the deploy form needs no editing.

The real application lives in prototypes/. This adds that directory to the
import path and hands over, so `app.py` runs identically whether launched from
the cloud, from the repo root, or from inside prototypes/.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent / "prototypes"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

runpy.run_path(str(APP_DIR / "app.py"), run_name="__main__")

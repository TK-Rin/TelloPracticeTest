"""
utils/common.py - shared helpers used by main.py and every mode module.

MEDIA_DIR / LOGS_DIR are resolved relative to THIS file's location, not the
current working directory and not a hardcoded drive letter. That is what
lets the project keep working after the portable disk is plugged into a
different PC (where it might show up as D:, E:, F:... instead of G:).
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
LOGS_DIR = BASE_DIR / "logs"


def ensure_dirs():
    MEDIA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)


def safe_land(tello, is_flying):
    """Land only if we actually took off, and never let a landing error escape."""
    if not is_flying:
        return
    try:
        tello.land()
    except Exception:
        pass

# utils/highscore.py
# Tiny JSON-backed high score store. One file, two modes ("space" and "car"),
# tolerant of missing/corrupt files (never crashes the game).

import json
import os
from settings import HIGHSCORE_FILE

# File lives next to main.py
_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), HIGHSCORE_FILE)


def _load_all() -> dict:
    """Return the full {mode: score} dict, or empty dict on any error."""
    if not os.path.isfile(_PATH):
        return {}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {k: int(v) for k, v in data.items() if isinstance(v, (int, float))}
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        # Corrupt file — silently start over
        pass
    return {}


def _save_all(data: dict):
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        # Read-only filesystem? Just skip — high score is non-critical.
        pass


def get(mode: str) -> int:
    """Return the high score for `mode` (0 if none yet)."""
    return _load_all().get(mode, 0)


def submit(mode: str, score: int) -> bool:
    """Save `score` if it beats the existing record. Returns True if new record."""
    data = _load_all()
    prev = data.get(mode, 0)
    if score > prev:
        data[mode] = int(score)
        _save_all(data)
        return True
    return False

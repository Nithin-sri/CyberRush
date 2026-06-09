# utils/prefs.py
# Tiny JSON-backed preferences store, separate from highscore.json so the
# schemas don't tangle. Tolerant of missing/corrupt files (returns defaults).

import json
import os

# File lives next to main.py
_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prefs.json")

_DEFAULTS = {
    "seen_tutorial": False,
}


def _load_all() -> dict:
    if not os.path.isfile(_PATH):
        return dict(_DEFAULTS)
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            # Merge over defaults so old prefs files still validate
            merged = dict(_DEFAULTS)
            merged.update(data)
            return merged
    except (json.JSONDecodeError, OSError):
        pass
    return dict(_DEFAULTS)


def _save_all(data: dict):
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass  # read-only filesystem — non-critical


def get(key: str):
    return _load_all().get(key, _DEFAULTS.get(key))


def set(key: str, value):
    data = _load_all()
    data[key] = value
    _save_all(data)

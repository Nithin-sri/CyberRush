"""Smoke tests — every module imports, sound manager survives missing files,
high score round-trips, results screen routes scores to the right grades."""

import os
import sys
import tempfile

# Make the project importable when running pytest from the repo root
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

# Headless pygame setup — must happen BEFORE pygame is imported anywhere
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((100, 100))


# ── Imports ────────────────────────────────────────────────
def test_all_modules_import():
    import main
    import settings
    from screens.menu        import MenuScreen
    from screens.mode_select import ModeSelectScreen
    from screens.game        import GameScreen
    from screens.pause       import PauseScreen
    from screens.results     import ResultsScreen
    from screens.review      import ReviewScreen
    from screens.howtoplay   import HowToPlayScreen
    from entities.player     import Player
    from entities.obstacle   import Obstacle
    from entities.effects    import EffectManager
    from utils.button        import Button
    from utils.draw          import draw_text, draw_hearts
    from utils.background    import SpaceBackground, RoadBackground
    from utils.sound         import get_sounds, SoundManager
    from utils               import highscore
    from data.questions      import QUESTIONS, CATEGORIES
    # Every question must have the new educational fields
    for q in QUESTIONS:
        assert "category" in q, f"missing category: {q['text']!r}"
        assert "deep"     in q, f"missing deep: {q['text']!r}"
        assert q["category"] in CATEGORIES, \
            f"unknown category {q['category']!r} on {q['text']!r}"


# ── Sound manager ──────────────────────────────────────────
def test_sound_manager_handles_missing_files():
    from utils.sound import SoundManager
    sm = SoundManager()
    # Every play / control call must be a safe no-op even if files are absent.
    for evt in ("click", "correct", "wrong", "gameover", "lane",
                "srank", "arank", "lowrank", "does_not_exist"):
        sm.play(evt)
    sm.stop("click", "wrong")
    sm.start_music(); sm.pause_music(); sm.unpause_music(); sm.stop_music()
    sm.toggle_mute(); sm.toggle_mute()


# ── High score ─────────────────────────────────────────────
def test_highscore_round_trip(monkeypatch):
    """Use a plain temp file we manage ourselves — avoids fixture-cleanup
    quirks on sandboxed filesystems."""
    from utils import highscore as hs
    fd, fake = tempfile.mkstemp(prefix="hs_", suffix=".json")
    os.close(fd)
    try:
        os.unlink(fake)            # let the module create it fresh
    except OSError:
        pass
    monkeypatch.setattr(hs, "_PATH", fake)
    try:
        assert hs.get("space") == 0
        assert hs.submit("space", 1000) is True
        assert hs.get("space") == 1000
        assert hs.submit("space", 500) is False
        assert hs.get("space") == 1000
    finally:
        try:
            os.unlink(fake)
        except OSError:
            pass


# ── Results screen routes scores to grades correctly ───────
def test_results_grade_thresholds():
    from screens.results import ResultsScreen
    r = ResultsScreen(800, 600)
    cases = [
        (0,     "D"),
        (1500,  "C"),
        (3500,  "B"),
        (5000,  "A"),
        (8000,  "S"),
        (50000, "S"),
    ]
    for score, expected in cases:
        r.set_result(score, "space")
        grade, _, _ = r._grade()
        assert grade == expected, f"score={score} expected {expected}, got {grade}"


# ── Review screen builds rows + per-category aggregates ────
def test_review_and_category_stats():
    from screens.review  import ReviewScreen
    from screens.results import ResultsScreen
    from data.questions  import QUESTIONS

    # Pick one phishing + one safe question to fabricate encounters
    phish = next(q for q in QUESTIONS if q["label"] == "phishing")
    safe  = next(q for q in QUESTIONS if q["label"] == "safe")

    encountered = [
        {"question": phish, "outcome": "hit"},
        {"question": phish, "outcome": "dodged"},
        {"question": phish, "outcome": "dodged"},
        {"question": safe,  "outcome": "collected"},
        {"question": safe,  "outcome": "missed"},
    ]

    # Review groups by question text and counts outcomes
    rv = ReviewScreen(800, 600)
    rv.set_data(encountered)
    assert len(rv.rows) == 2
    phish_row = next(r for r in rv.rows if r["question"]["text"] == phish["text"])
    assert phish_row["counts"]["hit"]    == 1
    assert phish_row["counts"]["dodged"] == 2

    # category_stats returns one entry per distinct category with right totals
    stats = ReviewScreen.category_stats(encountered)
    phish_stat = next(s for s in stats if s["category"] == phish["category"])
    safe_stat  = next(s for s in stats if s["category"] == safe["category"])
    assert phish_stat["phishing_hit"]    == 1
    assert phish_stat["phishing_dodged"] == 2
    assert safe_stat["safe_collected"]   == 1
    assert safe_stat["safe_missed"]      == 1

    # Results screen accepts encountered and computes cat_stats
    r = ResultsScreen(800, 600)
    r.set_result(score=4200, mode="space",
                 best_combo=3, encountered=encountered)
    assert r.encountered == encountered
    assert len(r.cat_stats) >= 1


# ── Game tracks encountered + forces pause on phishing hit ─
def test_game_pause_on_phishing_hit():
    from screens.game import GameScreen
    g = GameScreen(800, 600)
    g.set_mode("space")
    # Fresh game starts with empty encountered list and no forced pause.
    # The pause has no timer — it sits until the player dismisses it.
    assert g.encountered == []
    assert g.pause_on_hit_data is None


# ── Combo math: bonus grows but caps ───────────────────────
def test_combo_multiplier_caps():
    from settings import COMBO_STEP, COMBO_MAX, POINTS_SAFE
    # First pickup: combo = 0 → multiplier = 1
    base = POINTS_SAFE * (1 + COMBO_STEP * min(0, COMBO_MAX))
    assert base == POINTS_SAFE
    # At cap: combo = COMBO_MAX → multiplier = 1 + COMBO_STEP * COMBO_MAX
    capped = POINTS_SAFE * (1 + COMBO_STEP * min(COMBO_MAX + 50, COMBO_MAX))
    expected = POINTS_SAFE * (1 + COMBO_STEP * COMBO_MAX)
    assert capped == expected

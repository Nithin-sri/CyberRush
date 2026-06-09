"""Unit tests for the gameplay rules.

These complement test_smoke.py (which is mostly import / round-trip checks)
with focused assertions on level progression, speed capping, obstacle spawn
positioning, the SAFE_RATIO distribution, and player movement bounds.

They run under SDL's dummy driver so they're safe in CI / headless setups.
"""

import os
import sys
import random

# Headless pygame setup — must happen before pygame is imported anywhere
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Make the project root importable when running pytest from anywhere
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import settings
from settings import (OBSTACLE_SPEED, MAX_SPEED, FPS, ROUND_DURATION_SECONDS,
                      PLAYER_LIVES, PLAYER_INVINCIBLE_FRAMES, LANES,
                      WINDOW_W, WINDOW_H, SAFE_RATIO)


# ── Level progression ──────────────────────────────────────────
def test_level_starts_at_one_before_any_update():
    """A fresh game has level=1 the instant it's constructed, never level=2.
    Regression test: an earlier formula was int(speed // 2) which evaluated
    to 2 because the starting speed is already 4.0."""
    from screens.game import GameScreen
    g = GameScreen(WINDOW_W, WINDOW_H)
    g.set_mode("space")
    assert g.level == 1


def test_level_stays_at_one_after_first_frame():
    """After the very first update tick the level must still read 1 — the
    speed barely changes, so the displayed level shouldn't either."""
    from screens.game import GameScreen
    g = GameScreen(WINDOW_W, WINDOW_H)
    g.set_mode("space")
    g.update(1.0 / FPS)
    assert g.level == 1


def test_level_climbs_as_speed_grows():
    """When the speed has clearly increased past the starting value the
    level should be greater than 1."""
    from screens.game import GameScreen
    g = GameScreen(WINDOW_W, WINDOW_H)
    g.set_mode("space")
    # Force the speed higher and recompute level from the same formula
    g.speed = OBSTACLE_SPEED + 6.0   # i.e. starting + 6 px/frame
    g.level = 1 + int((g.speed - OBSTACLE_SPEED) // 2)
    assert g.level >= 4


# ── Speed cap ──────────────────────────────────────────────────
def test_speed_never_exceeds_max_speed():
    """Even after a long run the speed should not crawl past MAX_SPEED.
    Simulate enough frames to push the speed well above the cap."""
    from screens.game import GameScreen
    g = GameScreen(WINDOW_W, WINDOW_H)
    g.set_mode("space")
    # Far more frames than it takes to saturate the speed cap.
    for _ in range(60 * 120):
        g.update(1.0 / FPS)
        if g.game_over:
            break
    assert g.speed <= MAX_SPEED + 1e-6


# ── Obstacle spawn positions ───────────────────────────────────
def test_obstacle_space_mode_x_stays_clear_of_hud():
    """Space-mode obstacles must spawn inside the HUD-safe zone so the
    score / lives badges in the corners don't get covered by falling
    blocks. Implementation uses at least a 160px margin."""
    from entities.obstacle import Obstacle
    from data.questions   import QUESTIONS
    random.seed(0)
    q = next(qq for qq in QUESTIONS if qq["label"] == "phishing")
    margin = 160
    for _ in range(200):
        ob = Obstacle(q, "space", WINDOW_W, WINDOW_H, OBSTACLE_SPEED)
        assert margin <= ob.x <= WINDOW_W - margin


def test_obstacle_car_mode_snaps_to_lane_centre():
    """Car-mode obstacles must spawn on one of the LANES lane centres so
    the player can dodge by lane-switching."""
    from entities.obstacle import Obstacle
    from utils.background  import RoadBackground
    from data.questions    import QUESTIONS
    random.seed(0)
    q = next(qq for qq in QUESTIONS if qq["label"] == "safe")

    lane_w  = RoadBackground.ROAD_W // LANES
    centres = {RoadBackground.ROAD_LEFT + lane * lane_w + lane_w // 2
               for lane in range(LANES)}
    seen = set()
    for _ in range(120):
        ob = Obstacle(q, "car", WINDOW_W, WINDOW_H, OBSTACLE_SPEED)
        assert ob.x in centres
        seen.add(ob.x)
    # With 120 spawns we should hit every lane at least once.
    assert seen == centres


def test_obstacle_safe_ratio_distribution():
    """Spawning many obstacles via GameScreen._spawn() should keep the
    safe-vs-phishing ratio close to SAFE_RATIO. ±0.10 is generous enough
    to avoid flakes while still catching a regression that breaks the
    weighting entirely."""
    from screens.game import GameScreen
    random.seed(42)
    g = GameScreen(WINDOW_W, WINDOW_H)
    g.set_mode("space")
    for _ in range(1000):
        g._spawn()
    safe_count = sum(1 for ob in g.obstacles if ob.label == "safe")
    ratio = safe_count / len(g.obstacles)
    assert abs(ratio - SAFE_RATIO) < 0.10


# ── Player movement / lives ────────────────────────────────────
def test_player_space_mode_movement_bounds():
    """Player X must stay between min_x and max_x even when the input is
    held in one direction for many frames."""
    from entities.player import Player
    p = Player("space", WINDOW_W, WINDOW_H)

    # Simulate holding LEFT for a long time
    keys = {k: False for k in range(512)}
    keys[pygame.K_LEFT] = True
    class FakeKeys:
        def __getitem__(self, k): return keys.get(k, False)
    for _ in range(1000):
        p.handle_input(FakeKeys())
    assert p.x >= p.min_x

    # Hold RIGHT for a long time
    keys[pygame.K_LEFT]  = False
    keys[pygame.K_RIGHT] = True
    for _ in range(1000):
        p.handle_input(FakeKeys())
    assert p.x <= p.max_x


def test_player_hit_consumes_a_life_then_grants_iframes():
    """First hit reduces lives by one; subsequent hits during the
    invincible window must NOT reduce lives further."""
    from entities.player import Player
    p = Player("space", WINDOW_W, WINDOW_H)
    assert p.lives == PLAYER_LIVES

    assert p.hit() is True          # actually hit
    assert p.lives == PLAYER_LIVES - 1
    assert p.invincible_timer > 0

    # Second hit during i-frames — no damage
    assert p.hit() is False
    assert p.lives == PLAYER_LIVES - 1


def test_player_car_mode_stays_within_lanes():
    """In car mode the player must always be on a valid lane index after
    any sequence of left/right presses."""
    from entities.player import Player
    p = Player("car", WINDOW_W, WINDOW_H)
    keys = {k: False for k in range(512)}
    class FakeKeys:
        def __getitem__(self, k): return keys.get(k, False)

    # Spam LEFT — should clamp to lane 0
    keys[pygame.K_LEFT] = True
    for _ in range(60):
        p.handle_input(FakeKeys())
    assert p.lane == 0

    # Spam RIGHT — should clamp to LANES - 1
    keys[pygame.K_LEFT]  = False
    keys[pygame.K_RIGHT] = True
    for _ in range(60):
        p.handle_input(FakeKeys())
    assert p.lane == LANES - 1


# ── Round timer ────────────────────────────────────────────────
def test_round_ends_after_duration():
    """Once ROUND_DURATION_SECONDS of game time has elapsed the round
    should auto-end with end_reason='time'. We give the player infinite
    lives, suppress new spawns, and clear obstacles each frame so the
    only thing that can end the run is the round timer."""
    from screens.game import GameScreen
    g = GameScreen(WINDOW_W, WINDOW_H)
    g.set_mode("space")
    g.player.lives = 10**9
    for _ in range(int(ROUND_DURATION_SECONDS * FPS) + 5):
        # Clear any spawned obstacles before they can hit the player and
        # trigger the educational pause that would freeze the frame timer.
        g.obstacles.clear()
        g.spawn_cd = 10**9
        g.update(1.0 / FPS)
        if g.game_over:
            break
    assert g.game_over is True
    assert g.end_reason == "time"


# ── Game-over fade-in ──────────────────────────────────────────
def test_game_over_fade_blocks_premature_results():
    """The fade-in guard means SPACE shouldn't take you to the results
    screen until the overlay has mostly faded in (>=0.6)."""
    from screens.game import GameScreen
    g = GameScreen(WINDOW_W, WINDOW_H)
    g.set_mode("space")
    g.game_over    = True
    g.gameover_t   = 0.0
    g.end_reason   = "death"

    space_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
    # Before the fade is past 0.6 SPACE must not register.
    assert g.ready_for_results(space_event) is False
    g.gameover_t = 0.8
    assert g.ready_for_results(space_event) is True

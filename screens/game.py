# screens/game.py
# Core game loop screen — works for both space and car modes.

import pygame
import random
import textwrap
from settings import *
from utils.draw       import draw_text, draw_hearts, draw_bar, draw_card, get_font
from utils.background import SpaceBackground, RoadBackground
from entities.player   import Player
from entities.obstacle import Obstacle
from entities.effects  import EffectManager
from data.questions    import QUESTIONS, CATEGORIES
from utils.sound       import get_sounds


class GameScreen:
    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.mode      = "space"   # set before entering via set_mode()
        self._init()

    def set_mode(self, mode: str):
        self.mode = mode
        self._init()

    def _init(self):
        """Reset everything for a fresh game."""
        self.player    = Player(self.mode, self.W, self.H)
        self.speed     = OBSTACLE_SPEED
        self.score     = 0
        self.frame     = 0
        self.spawn_cd  = SPAWN_RATE
        self.obstacles: list[Obstacle] = []
        self.effects   = EffectManager()
        self.level     = 1
        self.q_pool    = QUESTIONS.copy()
        random.shuffle(self.q_pool)
        self.q_index   = 0
        self.game_over = False

        # Combo + screen shake state
        self.combo         = 0   # consecutive safe pickups, resets on a hit
        self.best_combo    = 0   # highest combo this run (shown on results)
        self.shake_frames  = 0   # remaining frames of screen shake
        self.end_reason    = None  # "death" or "time" once game_over flips
        # Game-over overlay fade-in progress (0 → 1 over ~0.5s)
        self.gameover_t    = 0.0

        # ── Educational additions ──
        # Encountered blocks for the review screen + stats breakdown.
        # Each entry: {"question": <dict>, "outcome": str}
        # outcome ∈ {"hit", "dodged", "collected", "missed"}
        self.encountered = []
        # Forced "Why?" pause after a phishing hit — freezes gameplay
        # entirely until the player dismisses it. There is no auto-resume
        # timer; the player must press SPACE / ENTER to continue.
        # pause_on_hit_data carries the question dict while the pause is
        # active, and is set back to None when the player dismisses it.
        self.pause_on_hit_data: dict | None = None

        if self.mode == "space":
            self.bg = SpaceBackground(self.W, self.H)
        else:
            self.bg = RoadBackground(self.W, self.H)

    # ── Pick next question (cycles through shuffled pool) ──
    def _next_question(self) -> dict:
        if self.q_index >= len(self.q_pool):
            self.q_pool  = QUESTIONS.copy()
            random.shuffle(self.q_pool)
            self.q_index = 0
        q = self.q_pool[self.q_index]
        self.q_index += 1
        return q

    # ── Obstacle spawning ──────────────────────────────────
    def _spawn(self):
        # Decide safe or phishing based on SAFE_RATIO
        pool = [q for q in self.q_pool
                if q["label"] == ("safe" if random.random() < SAFE_RATIO
                                  else "phishing")]
        if not pool:
            pool = self.q_pool
        q = random.choice(pool)
        self.obstacles.append(
            Obstacle(q, self.mode, self.W, self.H, self.speed)
        )

    # ── Update (called every frame) ───────────────────────
    def update(self, dt: float):
        if self.game_over:
            # Once the game is over, keep advancing the fade-in animation
            # so the overlay smoothly appears instead of popping in.
            if self.gameover_t < 1.0:
                self.gameover_t = min(1.0, self.gameover_t + dt / 0.5)
            return

        # Forced "Why?" pause after a phishing hit — gameplay frozen
        # entirely until the player dismisses the popup with SPACE/ENTER.
        # Only the shake-decay ticks during the pause so the screen settles.
        if self.pause_on_hit_data is not None:
            if self.shake_frames > 0:
                self.shake_frames -= 1
            return

        self.frame += 1
        self.speed  = min(MAX_SPEED,
                          OBSTACLE_SPEED + self.frame * SPEED_INCREMENT)
        self.score += SCORE_SURVIVAL
        # Level starts at 1 and climbs as speed grows past the starting value.
        # (Previously this was int(speed // 2) which gave level=2 at launch
        # because the starting speed is already 4.0.)
        self.level  = 1 + int((self.speed - OBSTACLE_SPEED) // 2)

        # Round timer — auto-end after ROUND_DURATION_SECONDS
        if self.frame / FPS >= ROUND_DURATION_SECONDS:
            self.game_over  = True
            self.end_reason = "time"
            get_sounds().play("gameover")
            return

        # Background
        if self.mode == "space":
            self.bg.update(speed_mult=self.speed / OBSTACLE_SPEED)
        else:
            self.bg.update(speed=self.speed)

        # Player
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update()

        # Spawn
        self.spawn_cd -= 1
        if self.spawn_cd <= 0:
            self._spawn()
            self.spawn_cd = max(30, SPAWN_RATE - self.level * 4)

        # Obstacles
        for obs in self.obstacles[:]:
            obs.update(self.speed)

            # Collision check — on contact the block VANISHES immediately
            # (player asked for this) instead of continuing to fall past.
            if self.player.rect.colliderect(obs.rect):
                if obs.label == "phishing":
                    # Player hit a phishing block — lose a life
                    if self.player.hit():
                        self.effects.explode(*obs.rect.center)
                        self.effects.show_tip(obs.tip, is_phishing=True)
                        get_sounds().play("wrong")
                        self.shake_frames = SHAKE_DURATION_FRAMES
                        self.combo = 0   # reset combo on any hit
                        # Record + force the "Why?" pause so the player
                        # actually reads the explanation. No timer — the
                        # player must press SPACE/ENTER to continue.
                        self.encountered.append(
                            {"question": obs.question, "outcome": "hit"})
                        self.pause_on_hit_data = obs.question
                    if not self.player.is_alive():
                        self.game_over  = True
                        self.end_reason = "death"
                        # Don't pop the why-pause on death; results screen
                        # handles the next step.
                        self.pause_on_hit_data = None
                        get_sounds().play("gameover")
                else:
                    # Player collected a safe block — score with combo bonus
                    multiplier  = 1 + COMBO_STEP * min(self.combo, COMBO_MAX)
                    awarded     = int(POINTS_SAFE * multiplier)
                    self.score += awarded
                    self.combo     += 1
                    self.best_combo = max(self.best_combo, self.combo)
                    self.effects.sparkle(*obs.rect.center)
                    self.effects.show_tip(obs.tip, is_phishing=False)
                    get_sounds().play("correct")
                    self.encountered.append(
                        {"question": obs.question, "outcome": "collected"})
                # Vanish immediately
                self.obstacles.remove(obs)
                continue

            # Remove when off-screen — track the "didn't-touch" outcome
            if obs.is_off_screen():
                outcome = "dodged" if obs.label == "phishing" else "missed"
                self.encountered.append(
                    {"question": obs.question, "outcome": outcome})
                self.obstacles.remove(obs)

        self.effects.update()

        # Tick down screen-shake timer
        if self.shake_frames > 0:
            self.shake_frames -= 1

    def handle_event(self, event) -> str | None:
        if event.type == pygame.KEYDOWN:
            # SPACE / ENTER dismisses the WHY pause (no timer — the player
            # explicitly confirms they've read the explanation).
            if (self.pause_on_hit_data is not None
                    and event.key in (pygame.K_SPACE,
                                      pygame.K_RETURN,
                                      pygame.K_KP_ENTER)):
                self.pause_on_hit_data = None
                return None
            # ESC pauses the game, but only when the WHY popup isn't open
            if event.key == pygame.K_ESCAPE and self.pause_on_hit_data is None:
                return "pause"
        return None

    # ── Draw ─────────────────────────────────────────────
    def draw(self, surface):
        if self.shake_frames > 0:
            # Render the world into an offscreen buffer, then blit it with a
            # random offset to produce screen shake. HUD draws on top without
            # shake so text stays readable.
            buf = pygame.Surface((self.W, self.H))
            self._draw_world(buf)
            mag = SHAKE_MAGNITUDE_PX * (self.shake_frames / SHAKE_DURATION_FRAMES)
            ox  = random.uniform(-mag, mag)
            oy  = random.uniform(-mag, mag)
            surface.fill(NAVY)
            surface.blit(buf, (int(ox), int(oy)))
        else:
            self._draw_world(surface)

        self._draw_hud(surface)

        # Forced "Why?" overlay sits on top of gameplay (and HUD)
        if self.pause_on_hit_data is not None:
            self._draw_why_overlay(surface)

        if self.game_over:
            self._draw_gameover(surface)

    # ── Educational "Why?" overlay ─────────────────────
    def _draw_why_overlay(self, surface):
        """Big centered card explaining the phishing concept that just hit."""
        q = self.pause_on_hit_data
        cat_key   = q.get("category", "social-engineering")
        cat_label = CATEGORIES.get(cat_key, cat_key).upper()

        # Dim the playfield
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((5, 13, 26, 215))
        surface.blit(ov, (0, 0))

        cx, cy = self.W // 2, self.H // 2
        cw, ch = 760, 360
        card   = pygame.Rect(cx - cw // 2, cy - ch // 2, cw, ch)
        draw_card(surface, card, colour=NAVY2, border_colour=RED, radius=20)

        # Category banner
        draw_text(surface, "WHY DID I LOSE A LIFE?",
                  FONT_XS, MUTED, cx, card.top + 30, bold=True)
        draw_text(surface, cat_label,
                  FONT_LG, RED, cx, card.top + 70, bold=True)

        # The block label that hit them
        block_text = q.get("text", "").replace("\n", "  ")
        draw_text(surface, f'"{block_text}"',
                  FONT_SM, AMBER, cx, card.top + 122)

        # Wrapped deep explanation
        deep = q.get("deep") or q.get("tip", "")
        font = get_font(FONT_SM, bold=False)
        # Pick a wrap width that comfortably fits inside the card
        wrap_chars = 62
        y = card.top + 170
        for line in textwrap.wrap(deep, width=wrap_chars):
            draw_text(surface, line, FONT_SM, WHITE, cx, y)
            y += 28

        # Dismiss hint — no timer, the player decides when to continue
        draw_text(surface,
                  "Press SPACE or ENTER to continue",
                  FONT_XS, MUTED, cx, card.bottom - 28)

    def _draw_world(self, surface):
        """Background + obstacles + player + effects — shake-eligible layer."""
        self.bg.draw(surface)
        for obs in self.obstacles:
            obs.draw(surface)
        self.player.draw(surface)
        self.effects.draw(surface, self.W)

    def _draw_hud(self, surface):
        cx = self.W // 2

        # Score
        draw_text(surface, f"SCORE  {self.score:06d}",
                  FONT_SM, CYAN, 20, 28, bold=True, anchor="left")

        # Combo (only shown once it actually means something)
        if self.combo >= 2:
            mult = 1 + COMBO_STEP * min(self.combo, COMBO_MAX)
            draw_text(surface, f"COMBO x{self.combo}  ({mult:.2f}×)",
                      FONT_XS, GREEN, 20, 56, bold=True, anchor="left")

        # Level
        draw_text(surface, f"LEVEL  {self.level}",
                  FONT_SM, AMBER, cx, 28, bold=True)

        # Lives (hearts)
        draw_hearts(surface, self.player.lives, PLAYER_LIVES,
                    self.W - 20, 32, size=18)

        # Time-remaining bar — replaces the old speed bar because remaining
        # time is the actionable info (speed is implicit from gameplay feel).
        time_left = max(0.0, ROUND_DURATION_SECONDS - self.frame / FPS)
        bar_col   = RED if time_left <= TIME_WARN_SECONDS else CYAN
        draw_bar(surface, cx, 58, 300, 7,
                 time_left, ROUND_DURATION_SECONDS,
                 colour=bar_col)
        draw_text(surface, f"TIME  {int(time_left):02d}s",
                  FONT_TINY, MUTED, cx, 70)

        # Mode badge — plain text (emojis don't render in the default font)
        mode_col  = CYAN if self.mode == "space" else PURPLE
        mode_text = "SPACE" if self.mode == "space" else "CAR"
        draw_text(surface, mode_text, FONT_XS, mode_col,
                  self.W - 20, 60, anchor="right", bold=True)

        # Controls reminder
        draw_text(surface, "Dodge RED  ·  Collect GREEN  ·  ESC pause",
                  FONT_TINY, MUTED, cx, self.H - 14)

    def _draw_gameover(self, surface):
        # Fade in: dim overlay alpha grows with gameover_t (0 → 1).
        # Ease-out so the fade decelerates into place.
        t    = self.gameover_t
        ease = 1 - (1 - t) * (1 - t)
        dim_alpha = int(190 * ease)

        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((5, 13, 26, dim_alpha))
        surface.blit(ov, (0, 0))
        cx, cy = self.W // 2, self.H // 2

        if self.end_reason == "time":
            title, col = "TIME UP!", AMBER
        else:
            title, col = "GAME OVER", RED

        # Title slides up slightly + fades in
        slide_y    = cy - 40 + int(20 * (1 - ease))
        title_font = get_font(FONT_XL, bold=True)
        img        = title_font.render(title, True, col)
        img.set_alpha(int(255 * ease))
        surface.blit(img, img.get_rect(center=(cx, slide_y)))

        # Score + prompt only appear after the title has mostly faded in
        if ease >= 0.6:
            score_alpha = int(255 * (ease - 0.6) / 0.4)
            font_md     = get_font(FONT_MD, bold=False)
            si          = font_md.render(f"Final Score:  {self.score}",
                                         True, WHITE)
            si.set_alpha(score_alpha)
            surface.blit(si, si.get_rect(center=(cx, cy + 20)))

            font_sm = get_font(FONT_SM, bold=False)
            pi      = font_sm.render("Press SPACE for results",
                                     True, MUTED)
            pi.set_alpha(score_alpha)
            surface.blit(pi, pi.get_rect(center=(cx, cy + 70)))

    def ready_for_results(self, event) -> bool:
        """Returns True when player presses SPACE on game-over screen.

        Guarded by the fade-in: SPACE only registers once the overlay has
        finished animating so the player doesn't accidentally skip past
        the moment of impact.
        """
        return (self.game_over
                and self.gameover_t >= 0.6
                and event.type == pygame.KEYDOWN
                and event.key  == pygame.K_SPACE)
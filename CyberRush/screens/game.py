# screens/game.py
# Core game loop screen — works for both space and car modes.

import pygame
import random
from settings import *
from utils.draw       import draw_text, draw_hearts, draw_bar
from utils.background import SpaceBackground, RoadBackground
from entities.player   import Player
from entities.obstacle import Obstacle
from entities.effects  import EffectManager
from data.questions    import QUESTIONS
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
            return

        self.frame += 1
        self.speed  = min(MAX_SPEED,
                          OBSTACLE_SPEED + self.frame * SPEED_INCREMENT)
        self.score += SCORE_SURVIVAL
        self.level  = max(1, int(self.speed // 2))

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

            # Collision check
            if not obs.collected and self.player.rect.colliderect(obs.rect):
                obs.collected = True
                obs.flash()
                if obs.label == "phishing":
                    # Player hit a phishing block — lose a life
                    if self.player.hit():
                        self.effects.explode(*obs.rect.center)
                        self.effects.show_tip(obs.tip, is_phishing=True)
                        get_sounds().play("wrong")
                    if not self.player.is_alive():
                        self.game_over = True
                        get_sounds().play("gameover")
                else:
                    # Player collected a safe block — score
                    self.score += POINTS_SAFE
                    self.effects.sparkle(*obs.rect.center)
                    self.effects.show_tip(obs.tip, is_phishing=False)
                    get_sounds().play("correct")

            # Remove when off-screen
            if obs.is_off_screen():
                self.obstacles.remove(obs)

        self.effects.update()

    def handle_event(self, event) -> str | None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "pause"
        return None

    # ── Draw ─────────────────────────────────────────────
    def draw(self, surface):
        self.bg.draw(surface)

        # Obstacles (draw before player so player is on top)
        for obs in self.obstacles:
            obs.draw(surface)

        self.player.draw(surface)
        self.effects.draw(surface, self.W)

        self._draw_hud(surface)

        if self.game_over:
            self._draw_gameover(surface)

    def _draw_hud(self, surface):
        cx = self.W // 2

        # Score
        draw_text(surface, f"SCORE  {self.score:06d}",
                  FONT_SM, CYAN, 20, 28, bold=True, anchor="left")

        # Level
        draw_text(surface, f"LEVEL  {self.level}",
                  FONT_SM, AMBER, cx, 28, bold=True)

        # Lives (hearts)
        draw_hearts(surface, self.player.lives, PLAYER_LIVES,
                    self.W - 20, 32, size=18)

        # Speed bar
        draw_bar(surface, cx, 58, 300, 7,
                 self.speed - OBSTACLE_SPEED,
                 MAX_SPEED  - OBSTACLE_SPEED,
                 colour=ORANGE)
        draw_text(surface, "SPEED", FONT_TINY, MUTED, cx, 70)

        # Mode badge
        mode_col  = CYAN if self.mode == "space" else PURPLE
        mode_text = "🚀 SPACE" if self.mode == "space" else "🚗 CAR"
        draw_text(surface, mode_text, FONT_XS, mode_col,
                  self.W - 20, 60, anchor="right")

        # Controls reminder
        draw_text(surface, "Dodge RED  ·  Collect GREEN  ·  ESC pause",
                  FONT_TINY, MUTED, cx, self.H - 14)

    def _draw_gameover(self, surface):
        # Dark overlay
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((5, 13, 26, 190))
        surface.blit(ov, (0, 0))
        cx, cy = self.W // 2, self.H // 2
        draw_text(surface, "GAME OVER", FONT_XL, RED,   cx, cy - 40, bold=True)
        draw_text(surface, f"Final Score:  {self.score}", FONT_MD, WHITE, cx, cy + 20)
        draw_text(surface, "Press SPACE for results",
                  FONT_SM, MUTED, cx, cy + 70)

    def ready_for_results(self, event) -> bool:
        """Returns True when player presses SPACE on game-over screen."""
        return (self.game_over
                and event.type == pygame.KEYDOWN
                and event.key  == pygame.K_SPACE)
# entities/player.py
# Player entity — works for BOTH space mode (spaceship) and car mode.
# Mode is passed as "space" or "car" at construction.

import pygame
import math
from settings import *
from utils.draw import draw_text


class Player:

    # How many pixels player moves per key-press frame
    MOVE_SPEED = 6

    def __init__(self, mode: str, window_w: int, window_h: int):
        self.mode    = mode          # "space" or "car"
        self.W, self.H = window_w, window_h
        self.lives   = PLAYER_LIVES
        self.invincible_timer = 0    # frames of invincibility after a hit
        self.INVINCIBLE_FRAMES = 90  # 1.5 seconds at 60fps

        # Starting position
        if mode == "space":
            self.x = window_w // 2
            self.y = window_h - 120
            self.w = 52
            self.h = 60
            # Movement: full 2D
            self.min_x = 40
            self.max_x = window_w - 40
            self.min_y = window_h // 3
            self.max_y = window_h - 60
        else:
            # Car mode: 3 lanes, snap horizontally
            self.lane  = 1               # 0, 1, 2
            self._set_lane_x()
            self.y = window_h - 140
            self.w = 50
            self.h = 80
            self.lane_cooldown = 0

        self.rect    = pygame.Rect(0, 0, self.w, self.h)
        self._update_rect()

        self._thrust_anim = 0  # animated thruster counter

    # ── Lane helpers (car mode) ────────────────────────
    def _set_lane_x(self):
        from utils.background import RoadBackground
        lane_w = RoadBackground.ROAD_W // LANES
        self.x = RoadBackground.ROAD_LEFT + self.lane * lane_w + lane_w // 2

    def _update_rect(self):
        self.rect.center = (int(self.x), int(self.y))

    # ── Input handling ─────────────────────────────────
    def handle_input(self, keys):
        if self.mode == "space":
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
                self.x = max(self.min_x, self.x - self.MOVE_SPEED)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.x = min(self.max_x, self.x + self.MOVE_SPEED)
            if keys[pygame.K_UP]    or keys[pygame.K_w]:
                self.y = max(self.min_y, self.y - self.MOVE_SPEED)
            if keys[pygame.K_DOWN]  or keys[pygame.K_s]:
                self.y = min(self.max_y, self.y + self.MOVE_SPEED)

        else:  # car mode — lane switching
            if self.lane_cooldown > 0:
                self.lane_cooldown -= 1
                return
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.lane > 0:
                self.lane -= 1
                self._set_lane_x()
                self.lane_cooldown = 18
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.lane < LANES - 1:
                self.lane += 1
                self._set_lane_x()
                self.lane_cooldown = 18

    def update(self):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        self._thrust_anim = (self._thrust_anim + 1) % 12
        self._update_rect()

    def hit(self):
        """Call when player collides with a phishing obstacle."""
        if self.invincible_timer > 0:
            return False   # still invincible — no damage
        self.lives -= 1
        self.invincible_timer = self.INVINCIBLE_FRAMES
        return True

    def is_alive(self) -> bool:
        return self.lives > 0

    # ── Drawing ────────────────────────────────────────
    def draw(self, surface):
        # Blink when invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 6) % 2 == 0:
            return

        if self.mode == "space":
            self._draw_spaceship(surface)
        else:
            self._draw_car(surface)

    def _draw_spaceship(self, surface):
        cx, cy = int(self.x), int(self.y)

        # Thruster flame (animated)
        flame_h = 14 + (self._thrust_anim % 6) * 2
        flame_pts = [
            (cx - 10, cy + self.h // 2),
            (cx,      cy + self.h // 2 + flame_h),
            (cx + 10, cy + self.h // 2),
        ]
        pygame.draw.polygon(surface, AMBER, flame_pts)
        inner = [
            (cx - 5,  cy + self.h // 2),
            (cx,      cy + self.h // 2 + flame_h - 6),
            (cx + 5,  cy + self.h // 2),
        ]
        pygame.draw.polygon(surface, WHITE, inner)

        # Hull — main body
        body = [
            (cx,           cy - self.h // 2),   # nose tip
            (cx + self.w // 2, cy + self.h // 2 - 10),   # right wing
            (cx + self.w // 4, cy + self.h // 2),
            (cx - self.w // 4, cy + self.h // 2),
            (cx - self.w // 2, cy + self.h // 2 - 10),   # left wing
        ]
        pygame.draw.polygon(surface, BLUE, body)
        pygame.draw.polygon(surface, CYAN, body, 2)

        # Cockpit
        pygame.draw.ellipse(surface, CYAN,
                            (cx - 10, cy - 14, 20, 18))
        pygame.draw.ellipse(surface, WHITE,
                            (cx - 6,  cy - 11, 12, 11))

    def _draw_car(self, surface):
        cx, cy = int(self.x), int(self.y)
        hw = self.w // 2
        hh = self.h // 2

        # Car body
        body = pygame.Rect(cx - hw, cy - hh, self.w, self.h)
        pygame.draw.rect(surface, BLUE, body, border_radius=10)
        pygame.draw.rect(surface, CYAN, body, 2, border_radius=10)

        # Windscreen
        ws = pygame.Rect(cx - hw + 8, cy - hh + 8, self.w - 16, 22)
        pygame.draw.rect(surface, CYAN_DIM, ws, border_radius=4)

        # Wheels
        for wx, wy in [(-hw - 4, -hh + 10), (hw - 2, -hh + 10),
                       (-hw - 4,  hh - 22), (hw - 2,  hh - 22)]:
            wheel = pygame.Rect(cx + wx, cy + wy, 10, 18)
            pygame.draw.rect(surface, DARK_MUTED, wheel, border_radius=4)
            pygame.draw.rect(surface, GREY, wheel, 1, border_radius=4)

        # Headlights
        for lx in [cx - hw + 6, cx + hw - 14]:
            pygame.draw.rect(surface, AMBER,
                             pygame.Rect(lx, cy - hh + 4, 8, 6),
                             border_radius=2)
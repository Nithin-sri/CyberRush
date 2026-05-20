# entities/obstacle.py
# Obstacles and collectibles that fly towards the player.
# label == "phishing"  → red block, dodge it
# label == "safe"      → green block, collect it

import pygame
import random
from settings import *
from utils.draw import get_font, draw_multiline
from utils.background import RoadBackground


class Obstacle:

    W = 140    # block width
    H = 90     # block height

    def __init__(self, question: dict, mode: str,
                 window_w: int, window_h: int, speed: float):
        self.question   = question
        self.label      = question["label"]
        self.tip        = question["tip"]
        self.mode       = mode
        self.W_win      = window_w
        self.H_win      = window_h
        self.speed      = speed
        self.collected  = False   # True once player touched it

        # Colour scheme by label
        if self.label == "phishing":
            self.fill_col   = RED_DIM
            self.border_col = RED
            self.text_col   = WHITE
            self.icon       = "⚠"
        else:
            self.fill_col   = GREEN_DIM
            self.border_col = GREEN
            self.text_col   = NAVY
            self.icon       = "✓"

        # Spawn position — random X within play area
        if mode == "space":
            self.x = random.uniform(80, window_w - 80)
            self.y = -self.H - 10
        else:
            # Snap to a random lane centre
            lane   = random.randint(0, LANES - 1)
            lane_w = RoadBackground.ROAD_W // LANES
            self.x = RoadBackground.ROAD_LEFT + lane * lane_w + lane_w // 2
            self.y = -self.H - 10

        self.rect = pygame.Rect(
            int(self.x) - self.W // 2,
            int(self.y) - self.H // 2,
            self.W, self.H
        )
        self._flash   = 0   # flash counter on collect/hit

    def update(self, speed: float):
        self.y    += speed
        self.rect.center = (int(self.x), int(self.y))
        if self._flash > 0:
            self._flash -= 1

    def is_off_screen(self) -> bool:
        return self.y > self.H_win + self.H + 20

    def flash(self):
        self._flash = 18

    def draw(self, surface):
        # Flash effect — alternate bright/dim
        if self._flash > 0 and (self._flash // 3) % 2 == 0:
            col = WHITE
        else:
            col = self.fill_col

        pygame.draw.rect(surface, col, self.rect, border_radius=12)
        pygame.draw.rect(surface, self.border_col, self.rect, 3, border_radius=12)

        # Icon (top centre)
        font_icon = get_font(FONT_SM, bold=True)
        icon_surf = font_icon.render(self.icon, True, self.border_col)
        icon_rect = icon_surf.get_rect(
            centerx=self.rect.centerx,
            top=self.rect.top + 6
        )
        surface.blit(icon_surf, icon_rect)

        # Question text (two lines)
        draw_multiline(surface, self.question["text"],
                       FONT_TINY, self.text_col,
                       self.rect.centerx,
                       self.rect.top + 30,
                       line_gap=2, anchor="center")
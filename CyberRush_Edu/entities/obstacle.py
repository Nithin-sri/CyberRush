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

    # Larger block so text fits clearly inside it.
    W = 170    # block width  (was 140)
    H = 110    # block height (was 90)

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

        # Colour scheme by label.
        # We render text on a dark inner panel for guaranteed contrast, so
        # the text colour is always near-white regardless of label.
        if self.label == "phishing":
            self.fill_col   = RED_DIM
            self.border_col = RED
            self.text_col   = WHITE
            self.icon       = "!"
            self.icon_col   = WHITE
        else:
            self.fill_col   = GREEN_DIM
            self.border_col = GREEN
            self.text_col   = WHITE
            self.icon       = "OK"
            self.icon_col   = WHITE

        # Spawn position — random X within play area
        if mode == "space":
            # Stay clear of the HUD corners (score on the left, lives + mode
            # badge on the right) so falling blocks don't pass behind the
            # text and turn into a visual smear.
            margin = max(160, self.W // 2)
            self.x = random.uniform(margin, window_w - margin)
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

        # Outer coloured block
        pygame.draw.rect(surface, col, self.rect, border_radius=12)
        pygame.draw.rect(surface, self.border_col, self.rect, 3, border_radius=12)

        # Color-blind mode: overlay a pattern so phishing vs safe is readable
        # without relying on red/green. Read flag lazily so toggling at runtime
        # picks up immediately.
        import settings as _S
        if getattr(_S, "COLORBLIND_MODE", False):
            self._draw_pattern(surface)

        # ── Top header band with icon + label ─────────────────
        header_h = 26
        header_rect = pygame.Rect(self.rect.left + 4, self.rect.top + 4,
                                  self.rect.width - 8, header_h)
        # Slightly lighter band, same hue family
        band_col = tuple(min(255, c + 30) for c in self.fill_col)
        pygame.draw.rect(surface, band_col, header_rect, border_radius=8)

        # Icon + tag text on header
        tag_text  = "PHISHING" if self.label == "phishing" else "SAFE"
        font_tag  = get_font(FONT_XS, bold=True)
        tag_surf  = font_tag.render(f"{self.icon}  {tag_text}", True, WHITE)
        tag_rect  = tag_surf.get_rect(center=header_rect.center)
        surface.blit(tag_surf, tag_rect)

        # ── Inner dark panel for the question text ─────────────
        # Guarantees high-contrast white text regardless of fill colour.
        inner = pygame.Rect(
            self.rect.left + 6,
            self.rect.top + header_h + 8,
            self.rect.width - 12,
            self.rect.height - header_h - 14
        )
        # Semi-transparent dark panel so the colour shows around the edge
        panel = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        panel.fill((5, 13, 26, 215))
        surface.blit(panel, inner.topleft)
        pygame.draw.rect(surface, self.border_col, inner, 1, border_radius=6)

        # Question text — bigger font, bold, white on dark
        draw_multiline(surface, self.question["text"],
                       FONT_XS, WHITE,
                       inner.centerx,
                       inner.top + 6,
                       line_gap=3, anchor="center", bold=True)

    def _draw_pattern(self, surface):
        """Color-blind helper: stripes on phishing, dots on safe."""
        clip = surface.get_clip()
        surface.set_clip(self.rect)
        if self.label == "phishing":
            # Diagonal stripes
            spacing = 10
            for i in range(-self.rect.height, self.rect.width, spacing):
                pygame.draw.line(
                    surface, self.border_col,
                    (self.rect.left + i,                 self.rect.top),
                    (self.rect.left + i + self.rect.height, self.rect.bottom),
                    2)
        else:
            # Dot grid
            for dy in range(8, self.rect.height, 14):
                for dx in range(8, self.rect.width, 14):
                    pygame.draw.circle(surface, self.border_col,
                                       (self.rect.left + dx,
                                        self.rect.top + dy), 2)
        surface.set_clip(clip)

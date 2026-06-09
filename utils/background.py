# utils/background.py
# Animated backgrounds shared across screens.
# SpaceBackground  — vaporwave-tinted sky + scrolling parallax stars
# RoadBackground   — scrolling highway road

import pygame
import random
from settings import *


# Pre-computed gradient cache, keyed by (w, h). Building the gradient surface
# is too expensive to do every frame, but the screens are usually one fixed
# size so this caches the result.
_GRADIENT_CACHE: dict[tuple[int, int], pygame.Surface] = {}


def _gradient_sky(w: int, h: int) -> pygame.Surface:
    """Vertical gradient that gives the menu a vaporwave feel without
    drifting so light that white text loses contrast.

    Stops (top → bottom): deep midnight indigo → magenta-violet bloom in
    the middle third → back to indigo at the floor. Three stops keep the
    overall image readable but add atmosphere.
    """
    key = (w, h)
    if key in _GRADIENT_CACHE:
        return _GRADIENT_CACHE[key]

    top    = (22, 14, 48)        # midnight indigo
    mid    = (62, 22, 88)        # magenta-violet bloom
    bottom = (16, 12, 38)        # deeper indigo floor

    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.5:
            # Top → middle
            k = t / 0.5
            r = int(top[0] + (mid[0] - top[0]) * k)
            g = int(top[1] + (mid[1] - top[1]) * k)
            b = int(top[2] + (mid[2] - top[2]) * k)
        else:
            # Middle → bottom
            k = (t - 0.5) / 0.5
            r = int(mid[0] + (bottom[0] - mid[0]) * k)
            g = int(mid[1] + (bottom[1] - mid[1]) * k)
            b = int(mid[2] + (bottom[2] - mid[2]) * k)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))

    # Soft horizon glow band — a faint warm streak across the middle, like
    # the sun is setting behind the magenta bloom. Pure cosmetic touch.
    glow_h = max(40, h // 8)
    glow_y = h // 2 - glow_h // 2
    for i in range(glow_h):
        a = int(35 * (1 - abs(i - glow_h / 2) / (glow_h / 2)))
        if a <= 0:
            continue
        line = pygame.Surface((w, 1), pygame.SRCALPHA)
        line.fill((255, 130, 200, a))    # warm pink horizon
        surf.blit(line, (0, glow_y + i))

    _GRADIENT_CACHE[key] = surf
    return surf


# Colour palette for the stars — multi-coloured so the sky reads as a
# stylised vaporwave scene rather than a default pygame starfield.
_STAR_TINTS = [
    (255, 255, 255),   # white
    (255, 255, 255),   # extra weight on white so they still dominate
    (255, 200, 240),   # soft pink
    (140, 230, 255),   # ice blue
    (255, 230, 160),   # warm gold
    (200, 180, 255),   # lavender
]


class SpaceBackground:
    """Vaporwave gradient sky with a scrolling parallax star field."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.layers = [
            self._make_layer(80,  speed=0.4, size_range=(1, 1), alpha_range=(60,  120)),
            self._make_layer(50,  speed=1.0, size_range=(1, 2), alpha_range=(100, 180)),
            self._make_layer(25,  speed=2.2, size_range=(2, 3), alpha_range=(160, 255)),
        ]

    def _make_layer(self, count, speed, size_range, alpha_range):
        stars = []
        for _ in range(count):
            stars.append({
                "x":     random.uniform(0, self.w),
                "y":     random.uniform(0, self.h),
                "size":  random.randint(*size_range),
                "alpha": random.randint(*alpha_range),
                "speed": speed,
                "tint":  random.choice(_STAR_TINTS),
            })
        return stars

    def update(self, speed_mult=1.0):
        for layer in self.layers:
            for star in layer:
                star["y"] += star["speed"] * speed_mult
                if star["y"] > self.h + 4:
                    star["y"] = -4
                    star["x"] = random.uniform(0, self.w)

    def draw(self, surface):
        # Vaporwave gradient instead of a flat dark fill
        surface.blit(_gradient_sky(self.w, self.h), (0, 0))

        for layer in self.layers:
            for s in layer:
                size = s["size"]
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*s["tint"], s["alpha"]),
                                   (size, size), size)
                surface.blit(surf, (s["x"] - size, s["y"] - size))


class RoadBackground:
    """Scrolling 3-lane highway with neon road markings."""

    ROAD_LEFT  = 250
    ROAD_RIGHT = 850
    ROAD_W     = 600

    def __init__(self, w: int, h: int):
        self.w, self.h    = w, h
        self.scroll       = 0.0
        self.line_gap     = 80    # pixels between dashes
        self.line_h       = 44    # dash height
        self.line_w       = 6     # dash width

    def update(self, speed: float):
        self.scroll = (self.scroll + speed) % self.line_gap

    def draw(self, surface):
        # Vaporwave sky behind the road too — gives car mode the same vibe
        surface.blit(_gradient_sky(self.w, self.h), (0, 0))

        # Side scenery (semi-transparent so the gradient still shows through)
        side = pygame.Surface((self.ROAD_LEFT, self.h), pygame.SRCALPHA)
        side.fill((*NAVY2, 180))
        surface.blit(side, (0, 0))
        right = pygame.Surface((self.w - self.ROAD_RIGHT, self.h),
                               pygame.SRCALPHA)
        right.fill((*NAVY2, 180))
        surface.blit(right, (self.ROAD_RIGHT, 0))

        # Road surface
        pygame.draw.rect(surface, (18, 14, 32),
                         (self.ROAD_LEFT, 0, self.ROAD_W, self.h))

        # Road edges — neon teal glow lines
        for x in [self.ROAD_LEFT, self.ROAD_RIGHT]:
            pygame.draw.line(surface, CYAN_DIM, (x, 0), (x, self.h), 3)

        # Lane dividers — dashed amber lines
        lane_w = self.ROAD_W // LANES
        for lane in range(1, LANES):
            lx = self.ROAD_LEFT + lane * lane_w
            y  = -self.line_gap + self.scroll
            while y < self.h + self.line_gap:
                rect = pygame.Rect(lx - self.line_w // 2,
                                   int(y), self.line_w, self.line_h)
                pygame.draw.rect(surface, AMBER_DIM, rect, border_radius=3)
                y += self.line_gap

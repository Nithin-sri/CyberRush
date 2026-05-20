# utils/background.py
# Animated backgrounds shared across screens.
# SpaceBackground  — scrolling stars
# RoadBackground   — scrolling highway road

import pygame
import random
from settings import *


class SpaceBackground:
    """Scrolling parallax star field."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.layers = [
            self._make_layer(80,  speed=0.4, size_range=(1, 1), alpha_range=(60, 120)),
            self._make_layer(50,  speed=1.0, size_range=(1, 2), alpha_range=(100, 180)),
            self._make_layer(25,  speed=2.2, size_range=(2, 3), alpha_range=(160, 255)),
        ]

    def _make_layer(self, count, speed, size_range, alpha_range):
        stars = []
        for _ in range(count):
            stars.append({
                "x": random.uniform(0, self.w),
                "y": random.uniform(0, self.h),
                "size":  random.randint(*size_range),
                "alpha": random.randint(*alpha_range),
                "speed": speed,
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
        surface.fill(NAVY)
        for layer in self.layers:
            for s in layer:
                surf = pygame.Surface((s["size"] * 2, s["size"] * 2),
                                      pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 255, 255, s["alpha"]),
                                   (s["size"], s["size"]), s["size"])
                surface.blit(surf, (s["x"] - s["size"], s["y"] - s["size"]))


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
        surface.fill(NAVY)

        # Side scenery (dark)
        pygame.draw.rect(surface, NAVY2,
                         (0, 0, self.ROAD_LEFT, self.h))
        pygame.draw.rect(surface, NAVY2,
                         (self.ROAD_RIGHT, 0,
                          self.w - self.ROAD_RIGHT, self.h))

        # Road surface
        pygame.draw.rect(surface, (18, 22, 32),
                         (self.ROAD_LEFT, 0, self.ROAD_W, self.h))

        # Road edges — neon cyan glow lines
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
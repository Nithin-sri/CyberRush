# entities/effects.py
# Visual particle effects: explosion on hit, sparkle on collect.

import pygame
import random
import math
from settings import *


class Particle:
    def __init__(self, x, y, colour, speed, angle, life, size):
        self.x, self.y = float(x), float(y)
        self.colour    = colour
        self.vx        = math.cos(angle) * speed
        self.vy        = math.sin(angle) * speed
        self.life      = life       # frames remaining
        self.max_life  = life
        self.size      = size

    def update(self):
        self.x    += self.vx
        self.y    += self.vy
        self.vy   += 0.12    # slight gravity
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        size  = max(1, int(self.size * (self.life / self.max_life)))
        s     = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.colour, alpha), (size, size), size)
        surface.blit(s, (int(self.x) - size, int(self.y) - size))


class EffectManager:
    """Holds and updates all active particle effects."""

    def __init__(self):
        self.particles: list[Particle] = []
        self.tip_messages: list[dict]  = []   # {"text", "colour", "timer"}

    def explode(self, x: int, y: int):
        """Red/orange explosion — player hit a phishing obstacle."""
        for _ in range(28):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.5, 5.5)
            life  = random.randint(25, 50)
            col   = random.choice([RED, ORANGE, AMBER, WHITE])
            size  = random.randint(2, 6)
            self.particles.append(Particle(x, y, col, speed, angle, life, size))

    def sparkle(self, x: int, y: int):
        """Green/cyan sparkle — player collected a safe item."""
        for _ in range(20):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.0, 4.0)
            life  = random.randint(20, 40)
            col   = random.choice([GREEN, CYAN, WHITE])
            size  = random.randint(2, 5)
            self.particles.append(Particle(x, y, col, speed, angle, life, size))

    def show_tip(self, text: str, is_phishing: bool):
        """Queue a tip message to display at the top of the screen."""
        self.tip_messages.append({
            "text":   text,
            "colour": RED if is_phishing else GREEN,
            "timer":  TIP_DURATION_FRAMES,   # configurable in settings.py
        })
        # Keep at most 2 tips at once
        if len(self.tip_messages) > 2:
            self.tip_messages.pop(0)

    def update(self):
        self.particles    = [p for p in self.particles if p.life > 0]
        self.tip_messages = [t for t in self.tip_messages if t["timer"] > 0]
        for p in self.particles:
            p.update()
        for t in self.tip_messages:
            t["timer"] -= 1

    def draw(self, surface, window_w: int):
        for p in self.particles:
            p.draw(surface)

        # Draw tip messages stacked at top-centre — start BELOW the HUD
        # (score / level / time bar live in the y=0..80 strip) so the pills
        # never overlap the HUD.
        from utils.draw import get_font
        y = 92
        for tip in self.tip_messages:
            alpha  = min(255, tip["timer"] * 3)
            font   = get_font(FONT_XS, bold=True)
            words  = tip["text"]
            img    = font.render(words, True, tip["colour"])
            # Pill background — slightly more opaque so text reads clearly
            # against the starfield/road.
            pad    = 10
            bg     = pygame.Surface((img.get_width() + pad * 2,
                                     img.get_height() + pad), pygame.SRCALPHA)
            pygame.draw.rect(bg, (*NAVY, min(alpha, 220)),
                             pygame.Rect(0, 0, bg.get_width(), bg.get_height()),
                             border_radius=8)
            # Thin coloured border so the tip's category colour is obvious
            pygame.draw.rect(bg, (*tip["colour"], min(alpha, 220)),
                             pygame.Rect(0, 0, bg.get_width(), bg.get_height()),
                             1, border_radius=8)
            surface.blit(bg,  (window_w // 2 - bg.get_width()  // 2, y))
            surface.blit(img, (window_w // 2 - img.get_width() // 2, y + pad // 2))
            y += bg.get_height() + 6
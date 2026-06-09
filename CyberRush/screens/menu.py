# screens/menu.py
# Animated main menu — title, buttons, scrolling star background.

import pygame
import math
from settings import *
from utils.draw   import draw_text
from utils.button import Button
from utils.background import SpaceBackground


class MenuScreen:
    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.bg        = SpaceBackground(W, H)
        self.time      = 0.0
        cx             = W // 2

        self.btn_play  = Button("PLAY",      cx, H // 2 + 20,  width=300, height=60, style="primary")
        self.btn_quit  = Button("QUIT",      cx, H // 2 + 100, width=300, height=54, style="danger")

    def update(self, dt: float):
        self.time += dt
        self.bg.update(speed_mult=0.6)

    def handle_event(self, event) -> str | None:
        if self.btn_play.clicked(event):  return "mode_select"
        if self.btn_quit.clicked(event):
            pygame.quit(); raise SystemExit
        return None

    def draw(self, surface):
        self.bg.draw(surface)

        cx = self.W // 2

        # Animated title size
        pulse = 1 + 0.018 * math.sin(self.time * 2.2)
        title_font = pygame.font.SysFont("arial", int(FONT_XL * pulse), bold=True)

        # Glow layer
        for offset, alpha in [(4, 40), (2, 80)]:
            glow = title_font.render("CYBERRUSH", True, CYAN)
            gs   = pygame.Surface(glow.get_size(), pygame.SRCALPHA)
            gs.blit(glow, (0, 0))
            gs.set_alpha(alpha)
            surface.blit(gs, (cx - glow.get_width() // 2 + offset,
                               self.H // 3 - 30))

        title = title_font.render("CYBERRUSH", True, CYAN)
        surface.blit(title, (cx - title.get_width() // 2, self.H // 3 - 30))

        draw_text(surface, "Dodge the threats. Collect the safe.",
                  FONT_SM, GREY, cx, self.H // 3 + 48)
        draw_text(surface, "3 lives  ·  increasing speed  ·  cyber education",
                  FONT_XS, MUTED, cx, self.H // 3 + 78)

        self.btn_play.draw(surface)
        self.btn_quit.draw(surface)

        draw_text(surface, "Arrow keys or WASD to move  ·  ESC to pause",
                  FONT_XS, MUTED, cx, self.H - 24)
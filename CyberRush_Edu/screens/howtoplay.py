# screens/howtoplay.py
# First-launch tutorial popup (also accessible from the main menu).
# 3 panels explain the core loop, plus a hotkey reference at the bottom.

import pygame
from settings import *
from utils.draw       import draw_text, draw_card
from utils.button     import Button
from utils.background import SpaceBackground


class HowToPlayScreen:
    PANELS = [
        ("DODGE  RED",
         "Phishing blocks cost a life.\nHit one and the game pauses\nso you can read WHY it's bad.",
         RED),
        ("COLLECT  GREEN",
         "Safe blocks score points and\nbuild a combo multiplier.",
         GREEN),
        ("REVIEW  &  LEARN",
         "After each run, see a breakdown\nby category and revisit every\nconcept you faced.",
         CYAN),
    ]

    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.bg        = SpaceBackground(W, H)
        cx             = W // 2
        # Centre the title + panels + controls block. Total ~440px tall.
        block_h        = 440
        self._title_y  = max(60, (H - block_h) // 2)
        self.btn_ok    = Button("GOT IT", cx, self._title_y + block_h + 40,
                                width=240, height=54, style="primary")

    def update(self, dt: float):
        self.bg.update(speed_mult=0.4)

    def handle_event(self, event) -> str | None:
        if self.btn_ok.clicked(event):
            return "dismiss"
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
            return "dismiss"
        return None

    def draw(self, surface):
        self.bg.draw(surface)
        cx = self.W // 2

        # Dim overlay so it reads as a popup, not a full screen
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((5, 13, 26, 200))
        surface.blit(ov, (0, 0))

        # Title
        draw_text(surface, "HOW TO PLAY", FONT_XL, CYAN,
                  cx, self._title_y, bold=True)
        draw_text(surface, "Three rules. That's it.",
                  FONT_SM, MUTED, cx, self._title_y + 50)

        # Three panels side by side
        panel_w = 280
        panel_h = 200
        gap     = 30
        total_w = panel_w * 3 + gap * 2
        start_x = cx - total_w // 2
        top_y   = self._title_y + 100

        for i, (heading, body, col) in enumerate(self.PANELS):
            x   = start_x + i * (panel_w + gap)
            r   = pygame.Rect(x, top_y, panel_w, panel_h)
            draw_card(surface, r, colour=NAVY2, border_colour=col, radius=18)

            draw_text(surface, heading, FONT_MD, col,
                      r.centerx, r.top + 38, bold=True)

            # body has \n — render line by line
            y = r.top + 90
            for line in body.split("\n"):
                draw_text(surface, line, FONT_XS, WHITE,
                          r.centerx, y)
                y += 24

        # Hotkey reference under the panels
        keys_y = top_y + panel_h + 36
        draw_text(surface, "CONTROLS",
                  FONT_SM, CYAN, cx, keys_y, bold=True)
        draw_text(surface,
                  "Arrow keys / WASD to move    ·    ESC to pause",
                  FONT_XS, GREY, cx, keys_y + 30)
        draw_text(surface,
                  "M  mute        F11  fullscreen        C  colour-blind mode",
                  FONT_XS, MUTED, cx, keys_y + 56)

        self.btn_ok.draw(surface)

# screens/results.py
# Final results screen with score, grade and replay option.

import pygame
from settings import *
from utils.draw   import draw_text, draw_card
from utils.button import Button
from utils.background import SpaceBackground


class ResultsScreen:
    def __init__(self, W: int, H: int):
        self.W, self.H  = W, H
        self.score      = 0
        self.mode       = "space"
        self.bg         = SpaceBackground(W, H)
        cx              = W // 2

        self.btn_again  = Button("PLAY AGAIN", cx - 155, H - 90,
                                 width=270, height=56, style="primary")
        self.btn_menu   = Button("MAIN MENU",  cx + 155, H - 90,
                                 width=270, height=56, style="ghost")

    def set_result(self, score: int, mode: str):
        self.score = score
        self.mode  = mode

    def _grade(self):
        if   self.score >= 8000: return "S", "Cyber Defender",    CYAN
        elif self.score >= 5000: return "A", "Security Expert",   GREEN
        elif self.score >= 3000: return "B", "Phish Spotter",     AMBER
        elif self.score >= 1000: return "C", "Getting There",     ORANGE
        else:                    return "D", "Keep Practising",   RED

    def update(self, dt: float):
        self.bg.update(speed_mult=0.3)

    def handle_event(self, event) -> str | None:
        if self.btn_again.clicked(event): return "play_again"
        if self.btn_menu.clicked(event):  return "menu"
        return None

    def draw(self, surface):
        self.bg.draw(surface)
        cx = self.W // 2

        draw_text(surface, "CYBERRUSH", FONT_LG, CYAN_DIM, cx, 42, bold=True)

        grade, title, col = self._grade()

        # Grade card
        gc = pygame.Rect(cx - 180, 80, 360, 180)
        draw_card(surface, gc, colour=NAVY2, border_colour=col, radius=20)
        draw_text(surface, grade, FONT_HUGE, col, cx, 148, bold=True)
        draw_text(surface, title, FONT_MD, WHITE, cx, 222, bold=True)

        draw_text(surface, f"Score:  {self.score:,}  pts",
                  FONT_LG, WHITE, cx, 290, bold=True)

        mode_label = "Space Mode" if self.mode == "space" else "Car Mode"
        draw_text(surface, f"Mode: {mode_label}",
                  FONT_XS, MUTED, cx, 330)

        # Cyber tip card
        tc = pygame.Rect(cx - 380, 358, 760, 110)
        draw_card(surface, tc, colour=NAVY3, border_colour=BORDER, radius=14)
        draw_text(surface, "Cyber Safety Tip", FONT_SM, CYAN,
                  tc.left + 20, tc.top + 28, bold=True, anchor="left")
        draw_text(surface,
                  "Always hover over links to preview the real URL before clicking.",
                  FONT_XS, WHITE, tc.left + 20, tc.top + 62, anchor="left")

        self.btn_again.draw(surface)
        self.btn_menu.draw(surface)
# screens/pause.py
# Pause overlay drawn on top of the game screen.

import pygame
from settings import *
from utils.draw   import draw_text, draw_card
from utils.button import Button


class PauseScreen:
    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        cx = W // 2
        cw, ch = 420, 300
        self.card = pygame.Rect(cx - cw // 2, H // 2 - ch // 2, cw, ch)

        self.btn_resume = Button("RESUME",     cx, H // 2 - 20, width=280, height=52, style="primary")
        self.btn_menu   = Button("MAIN MENU",  cx, H // 2 + 50, width=280, height=52, style="ghost")
        self.btn_quit   = Button("QUIT",       cx, H // 2 + 115, width=280, height=48, style="danger")

    def handle_event(self, event) -> str | None:
        if self.btn_resume.clicked(event): return "resume"
        if self.btn_menu.clicked(event):   return "menu"
        if self.btn_quit.clicked(event):
            pygame.quit(); raise SystemExit
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "resume"
        return None

    def draw(self, surface):
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((5, 13, 26, 185))
        surface.blit(ov, (0, 0))

        draw_card(surface, self.card, colour=NAVY2,
                  border_colour=CYAN, radius=20)

        cx = self.W // 2
        draw_text(surface, "PAUSED", FONT_LG, CYAN,
                  cx, self.card.top + 50, bold=True)
        pygame.draw.line(surface, BORDER,
                         (self.card.left + 28, self.card.top + 82),
                         (self.card.right - 28, self.card.top + 82), 1)
        draw_text(surface, "Timer stopped  ·  take your time",
                  FONT_XS, MUTED, cx, self.card.top + 102)

        self.btn_resume.draw(surface)
        self.btn_menu.draw(surface)
        self.btn_quit.draw(surface)
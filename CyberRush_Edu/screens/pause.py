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

        # Card with explicit content slots — title strip on top, then the
        # three buttons stacked underneath with comfortable padding so the
        # subtitle never overlaps the RESUME button.
        cw, ch = 420, 340
        cy_top = H // 2 - ch // 2
        self.card = pygame.Rect(cx - cw // 2, cy_top, cw, ch)

        btn_top = cy_top + 130
        self.btn_resume = Button("RESUME",    cx, btn_top,       width=280, height=52, style="primary")
        self.btn_menu   = Button("MAIN MENU", cx, btn_top + 64,  width=280, height=52, style="ghost")
        self.btn_quit   = Button("QUIT",      cx, btn_top + 128, width=280, height=48, style="danger")

        # Keyboard navigation
        self._nav = [self.btn_resume, self.btn_menu, self.btn_quit]
        self._focus_idx = 0
        self._nav[0].focused = True

    def _set_focus(self, idx: int):
        self._nav[self._focus_idx].focused = False
        self._focus_idx = idx % len(self._nav)
        self._nav[self._focus_idx].focused = True

    def handle_event(self, event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._set_focus(self._focus_idx - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._set_focus(self._focus_idx + 1)
            elif event.key == pygame.K_TAB:
                step = -1 if event.mod & pygame.KMOD_SHIFT else 1
                self._set_focus(self._focus_idx + step)
            elif event.key == pygame.K_ESCAPE:
                return "resume"

        if event.type == pygame.MOUSEMOTION:
            for i, b in enumerate(self._nav):
                if b.rect.collidepoint(event.pos) and i != self._focus_idx:
                    self._set_focus(i)
                    break

        if self.btn_resume.activated(event): return "resume"
        if self.btn_menu.activated(event):   return "menu"
        if self.btn_quit.activated(event):
            pygame.quit(); raise SystemExit
        return None

    def draw(self, surface):
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((5, 13, 26, 185))
        surface.blit(ov, (0, 0))

        draw_card(surface, self.card, colour=NAVY2,
                  border_colour=CYAN, radius=20)

        cx = self.W // 2
        draw_text(surface, "PAUSED", FONT_LG, CYAN,
                  cx, self.card.top + 42, bold=True)
        pygame.draw.line(surface, BORDER,
                         (self.card.left + 28, self.card.top + 76),
                         (self.card.right - 28, self.card.top + 76), 1)
        draw_text(surface, "Timer stopped  ·  take your time",
                  FONT_XS, MUTED, cx, self.card.top + 94)

        self.btn_resume.draw(surface)
        self.btn_menu.draw(surface)
        self.btn_quit.draw(surface)

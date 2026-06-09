# screens/mode_select.py
# Player picks the game mode: SPACE (arcade dodger) or QUIZ (QnA).

import pygame
from settings import *
from utils.draw   import draw_text, draw_card
from utils.button import Button
from utils.background import SpaceBackground


class ModeSelectScreen:
    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.bg        = SpaceBackground(W, H)
        cx             = W // 2

        # Centre the title + cards + buttons block vertically so the screen
        # looks balanced at both 700px and 1080px window heights.
        block_h = 480
        self._title_y = max(60, (H - block_h) // 2)
        self._top_y   = self._title_y + 80     # card top
        btn_y         = self._top_y + 280      # button row (just below cards)

        self.btn_space = Button("SPACE MODE", cx - 170, btn_y,
                                width=300, height=58, style="primary")
        self.btn_quiz  = Button("QUIZ MODE",  cx + 170, btn_y,
                                width=300, height=58, style="purple")
        self.btn_back  = Button("BACK",       cx,       btn_y + 80,
                                width=160, height=44, style="ghost")

        # Keyboard navigation: Space ↔ Quiz left/right, Down to BACK.
        self._nav = [self.btn_space, self.btn_quiz, self.btn_back]
        self._focus_idx = 0
        self._nav[0].focused = True

    def update(self, dt: float):
        self.bg.update(speed_mult=0.4)

    def _set_focus(self, idx: int):
        self._nav[self._focus_idx].focused = False
        self._focus_idx = idx % len(self._nav)
        self._nav[self._focus_idx].focused = True

    def handle_event(self, event) -> tuple | None:
        # Keyboard navigation. Layout: [Space] [Quiz]  /  [Back]
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                if self._focus_idx == 1: self._set_focus(0)
                elif self._focus_idx == 2: self._set_focus(0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self._focus_idx == 0: self._set_focus(1)
                elif self._focus_idx == 2: self._set_focus(1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._set_focus(2)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._set_focus(0)
            elif event.key == pygame.K_TAB:
                step = -1 if event.mod & pygame.KMOD_SHIFT else 1
                self._set_focus(self._focus_idx + step)
            elif event.key == pygame.K_ESCAPE:
                return ("back", None)

        if event.type == pygame.MOUSEMOTION:
            for i, b in enumerate(self._nav):
                if b.rect.collidepoint(event.pos):
                    if i != self._focus_idx:
                        self._set_focus(i)
                    break

        if self.btn_space.activated(event): return ("game", "space")
        if self.btn_quiz.activated(event):  return ("quiz", None)
        if self.btn_back.activated(event):  return ("back", None)
        return None

    # ── Icons drawn instead of emojis (default font can't render them) ──
    def _draw_ship_icon(self, surface, cx: int, cy: int, col):
        pts = [(cx, cy - 22), (cx + 18, cy + 14),
               (cx + 7, cy + 6), (cx - 7, cy + 6),
               (cx - 18, cy + 14)]
        pygame.draw.polygon(surface, col, pts)
        pygame.draw.polygon(surface, WHITE, pts, 2)
        pygame.draw.circle(surface, WHITE, (cx, cy - 4), 4)

    def _draw_quiz_icon(self, surface, cx: int, cy: int, col):
        """Stylised speech-bubble + question-mark icon for quiz mode."""
        # Speech bubble
        body = pygame.Rect(cx - 22, cy - 22, 44, 36)
        pygame.draw.rect(surface, col, body, border_radius=10)
        pygame.draw.rect(surface, WHITE, body, 2, border_radius=10)
        # Tail
        tail = [(cx - 6, cy + 12), (cx + 6, cy + 12), (cx - 2, cy + 22)]
        pygame.draw.polygon(surface, col, tail)
        pygame.draw.polygon(surface, WHITE, tail, 2)
        # Question mark inside
        font = pygame.font.SysFont("arial", 24, bold=True)
        q    = font.render("?", True, WHITE)
        surface.blit(q, q.get_rect(center=(cx, cy - 4)))

    def draw(self, surface):
        self.bg.draw(surface)
        cx = self.W // 2

        draw_text(surface, "CHOOSE YOUR MODE", FONT_LG, CYAN,
                  cx, self._title_y, bold=True)
        draw_text(surface, "Two ways to learn the same threats",
                  FONT_SM, MUTED, cx, self._title_y + 40)

        # ── Two big cards centred side by side ────────────────
        card_w = 320
        card_h = 240
        gap    = 40
        top_y  = self._top_y

        sc = pygame.Rect(cx - card_w - gap // 2, top_y, card_w, card_h)
        qc = pygame.Rect(cx + gap // 2,           top_y, card_w, card_h)

        # Space card
        draw_card(surface, sc, colour=NAVY2, border_colour=CYAN, radius=18)
        self._draw_ship_icon(surface, sc.centerx, sc.top + 56, CYAN)
        draw_text(surface, "SPACE", FONT_MD, CYAN,
                  sc.centerx, sc.top + 100, bold=True)
        draw_text(surface, "Arcade dodger",
                  FONT_XS, WHITE, sc.centerx, sc.top + 142)
        draw_text(surface, "Fly past threats, grab the safe ones",
                  FONT_XS, GREY, sc.centerx, sc.top + 168)
        draw_text(surface, "Reflex + recognition",
                  FONT_XS, MUTED, sc.centerx, sc.top + 200)

        # Quiz card
        draw_card(surface, qc, colour=NAVY2, border_colour=PURPLE, radius=18)
        self._draw_quiz_icon(surface, qc.centerx, qc.top + 56, PURPLE)
        draw_text(surface, "QUIZ", FONT_MD, PURPLE,
                  qc.centerx, qc.top + 100, bold=True)
        draw_text(surface, "Question & Answer",
                  FONT_XS, WHITE, qc.centerx, qc.top + 142)
        draw_text(surface, "Classify each scenario, learn the why",
                  FONT_XS, GREY, qc.centerx, qc.top + 168)
        draw_text(surface, "No timer, just thinking",
                  FONT_XS, MUTED, qc.centerx, qc.top + 200)

        self.btn_space.draw(surface)
        self.btn_quiz.draw(surface)
        self.btn_back.draw(surface)

# screens/quiz.py
# Quiz mode — show one cybersecurity scenario at a time, ask the player to
# classify it as PHISHING or SAFE, then reveal the deep explanation and
# either the correct/wrong outcome.
#
# Uses the same question pool as space mode (data/questions.py) so the two
# modes teach the same material in different formats.

import pygame
import random
import textwrap
from settings import *
from utils.draw       import draw_text, draw_card, draw_bar, get_font
from utils.button     import Button
from utils.background import SpaceBackground
from utils.sound      import get_sounds
from data.questions   import QUESTIONS, CATEGORIES


# Score awarded for a correct answer. Tuned so a perfect 10-question run
# lands in the same grade band as a strong space-mode run (8000+ → S).
POINTS_CORRECT = 1000
QUIZ_LENGTH    = 10


class QuizScreen:
    """A QnA-style cybersecurity quiz.

    Phases:
      "asking"   — question card visible, two answer buttons active
      "feedback" — after an answer, show whether they were right + the deep
                   explanation. Player presses SPACE/ENTER or clicks NEXT.
      "done"     — quiz finished; the state machine takes over and pushes
                   the results screen.
    """

    # ── Layout constants (anchored in the design grid so spacing is
    # predictable and never relies on H/2 maths that can put buttons
    # inside the question card on a short window).
    HEADER_TOP    = 70        # title baseline
    PROGRESS_Y    = 158       # progress bar
    CARD_TOP      = 196       # question card top
    CARD_H        = 200
    CARD_W        = 760
    ANSWER_GAP    = 36        # gap between card and answer buttons
    ANSWER_H      = 64
    FEEDBACK_GAP  = 26        # gap between card and feedback banner
    BANNER_H      = 62
    PANEL_GAP     = 24        # gap between banner+category and WHY panel
    PANEL_W       = 880
    PANEL_MIN_H   = 180
    NEXT_GAP      = 28        # gap between WHY panel and NEXT button
    NEXT_H        = 56

    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.bg        = SpaceBackground(W, H)

        cx = W // 2

        # ── Compute every Y-anchor up-front so nothing collides ─────
        card_bottom    = self.CARD_TOP + self.CARD_H
        # Answer buttons sit a fixed distance below the card, never under it
        answer_cy      = card_bottom + self.ANSWER_GAP + self.ANSWER_H // 2
        # Feedback band stack: banner → category → panel → NEXT
        banner_top     = card_bottom + self.FEEDBACK_GAP
        banner_bot     = banner_top + self.BANNER_H
        cat_y          = banner_bot + 20
        panel_top      = cat_y + 24
        # NEXT button anchored at the bottom. Panel height is whatever
        # space is left between the category line and the NEXT button —
        # never more, never less — so the panel can never grow past NEXT.
        next_cy        = H - 80
        next_top       = next_cy - self.NEXT_H // 2
        panel_h        = max(80, next_top - self.NEXT_GAP - panel_top)
        self._banner_top = banner_top
        self._cat_y      = cat_y
        self._panel_top  = panel_top
        self._panel_h    = panel_h

        # Answer buttons centred side-by-side, sitting below the card
        self.btn_phish = Button("PHISHING", cx - 170, answer_cy,
                                width=300, height=self.ANSWER_H, style="danger")
        self.btn_safe  = Button("SAFE",     cx + 170, answer_cy,
                                width=300, height=self.ANSWER_H, style="success")
        # NEXT button positioned below the WHY panel during feedback
        self.btn_next  = Button("NEXT", cx, next_cy,
                                width=240, height=self.NEXT_H, style="primary")

        # Keyboard navigation
        self._answer_nav = [self.btn_phish, self.btn_safe]
        self._focus_idx  = 0
        self._answer_nav[0].focused = True

        self.reset()

    # ── State ────────────────────────────────────────────
    def reset(self):
        """Start a fresh quiz round."""
        phishing = [q for q in QUESTIONS if q["label"] == "phishing"]
        safe     = [q for q in QUESTIONS if q["label"] == "safe"]
        random.shuffle(phishing)
        random.shuffle(safe)
        half          = QUIZ_LENGTH // 2
        chosen        = phishing[:half] + safe[:QUIZ_LENGTH - half]
        random.shuffle(chosen)
        self.questions: list[dict] = chosen

        self.idx           = 0
        self.score         = 0
        self.correct_count = 0
        self.phase         = "asking"
        self.last_correct  = False
        self.encountered: list[dict] = []
        self.best_combo    = 0
        self._combo        = 0
        for b in self._answer_nav:
            b.focused = False
        self._focus_idx = 0
        self._answer_nav[0].focused = True

    @property
    def current(self) -> dict | None:
        if 0 <= self.idx < len(self.questions):
            return self.questions[self.idx]
        return None

    def done(self) -> bool:
        return self.phase == "done"

    # ── Update ───────────────────────────────────────────
    def update(self, dt: float):
        self.bg.update(speed_mult=0.3)

    # ── Events ───────────────────────────────────────────
    def _set_focus(self, idx: int):
        self._answer_nav[self._focus_idx].focused = False
        self._focus_idx = idx % len(self._answer_nav)
        self._answer_nav[self._focus_idx].focused = True

    def handle_event(self, event) -> str | None:
        if self.phase == "asking":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self._set_focus(0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self._set_focus(1)
                elif event.key == pygame.K_TAB:
                    step = -1 if event.mod & pygame.KMOD_SHIFT else 1
                    self._set_focus(self._focus_idx + step)

            if event.type == pygame.MOUSEMOTION:
                for i, b in enumerate(self._answer_nav):
                    if b.rect.collidepoint(event.pos) and i != self._focus_idx:
                        self._set_focus(i)
                        break

            if self.btn_phish.activated(event):
                self._answer("phishing")
                return None
            if self.btn_safe.activated(event):
                self._answer("safe")
                return None

        elif self.phase == "feedback":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE,
                                 pygame.K_RETURN,
                                 pygame.K_KP_ENTER):
                    self._advance()
                    return None
                if event.key == pygame.K_ESCAPE:
                    self.phase = "done"
                    return None
            if self.btn_next.activated(event):
                self._advance()
                return None

        if (self.phase == "asking"
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE):
            self.phase = "done"

        return None

    def _answer(self, choice: str):
        q = self.current
        if q is None:
            return
        actual    = q["label"]
        correct   = (choice == actual)
        self.last_correct = correct

        if correct:
            self.correct_count += 1
            self._combo        += 1
            self.best_combo     = max(self.best_combo, self._combo)
            mult        = 1 + COMBO_STEP * min(self._combo - 1, COMBO_MAX)
            self.score += int(POINTS_CORRECT * mult)
            get_sounds().play("correct")
            outcome = "collected" if actual == "safe" else "dodged"
        else:
            self._combo = 0
            get_sounds().play("wrong")
            outcome = "missed" if actual == "safe" else "hit"

        self.encountered.append({"question": q, "outcome": outcome})
        self.phase = "feedback"

    def _advance(self):
        self.idx += 1
        if self.idx >= len(self.questions):
            self.phase = "done"
            get_sounds().play("gameover")
            return
        self.phase = "asking"
        for b in self._answer_nav:
            b.focused = False
        self._focus_idx = 0
        self._answer_nav[0].focused = True

    # ── Drawing ──────────────────────────────────────────
    def draw(self, surface):
        self.bg.draw(surface)
        cx = self.W // 2

        # Header — title + progress
        draw_text(surface, "CYBER QUIZ", FONT_XL, CYAN,
                  cx, self.HEADER_TOP, bold=True)
        draw_text(surface,
                  f"Question {min(self.idx + 1, QUIZ_LENGTH)} of {QUIZ_LENGTH}"
                  f"   ·   Score {self.score:,}",
                  FONT_SM, WHITE, cx, self.HEADER_TOP + 50, bold=True)

        progress = self.idx / max(1, QUIZ_LENGTH)
        if self.phase == "feedback":
            progress = (self.idx + 1) / max(1, QUIZ_LENGTH)
        draw_bar(surface, cx, self.PROGRESS_Y, 480, 6, progress, 1.0,
                 colour=CYAN, bg=NAVY3)

        q = self.current
        if q is None:
            return

        # Question card
        card = pygame.Rect(cx - self.CARD_W // 2, self.CARD_TOP,
                           self.CARD_W, self.CARD_H)
        draw_card(surface, card, colour=NAVY2,
                  border_colour=BORDER, radius=20)

        draw_text(surface, "IS THIS PHISHING OR SAFE?",
                  FONT_SM, WHITE, cx, card.top + 28, bold=True)

        font_big = get_font(FONT_LG, bold=True)
        lines    = q["text"].split("\n")
        # Centre the lines vertically inside the card so multi-line and
        # single-line scenarios both look balanced.
        total_h  = len(lines) * (font_big.get_height() + 4)
        line_y   = card.top + 70 + (self.CARD_H - 70 - total_h) // 2
        for line in lines:
            img = font_big.render(line, True, WHITE)
            surface.blit(img, img.get_rect(center=(cx, line_y)))
            line_y += font_big.get_height() + 4

        if self.phase == "asking":
            # Hint sits between the card bottom and the answer buttons —
            # explicitly placed in the gap so it's never covered.
            hint_y = card.bottom + self.ANSWER_GAP // 2 + 2
            draw_text(surface,
                      "← / →  to choose   ·   ENTER to confirm   ·   ESC to quit",
                      FONT_XS, WHITE, cx, hint_y, bold=True)
            self.btn_phish.draw(surface)
            self.btn_safe.draw(surface)

        elif self.phase == "feedback":
            self._draw_feedback(surface, cx, q)
            self.btn_next.draw(surface)

    def _draw_feedback(self, surface, cx: int, q: dict):
        """Result banner → category → WHY panel, stacked with explicit gaps
        so the NEXT button below never overlaps anything above."""
        # Result banner
        banner_col = GREEN if self.last_correct else RED
        banner_txt = "CORRECT" if self.last_correct else "INCORRECT"
        actual_lbl = "PHISHING" if q["label"] == "phishing" else "SAFE"

        banner_text = f"{banner_txt}   ·   This is {actual_lbl}"
        font_md     = get_font(FONT_MD, bold=True)
        img         = font_md.render(banner_text, True, banner_col)
        pad_x, pad_y = 28, 12
        bg_w = img.get_width()  + pad_x * 2
        bg_h = self.BANNER_H
        banner = pygame.Rect(cx - bg_w // 2, self._banner_top, bg_w, bg_h)
        draw_card(surface, banner, colour=NAVY2,
                  border_colour=banner_col, radius=14)
        surface.blit(img, img.get_rect(center=banner.center))

        # Category chip
        cat_key   = q.get("category", "")
        cat_label = CATEGORIES.get(cat_key, cat_key or "—")
        draw_text(surface, cat_label.upper(), FONT_XS, AMBER,
                  cx, self._cat_y, bold=True)

        # Deep explanation panel
        panel = pygame.Rect(cx - self.PANEL_W // 2,
                            self._panel_top,
                            self.PANEL_W, self._panel_h)
        draw_card(surface, panel, colour=NAVY3,
                  border_colour=BORDER, radius=14)

        draw_text(surface, "WHY", FONT_SM, CYAN,
                  panel.left + 24, panel.top + 22,
                  bold=True, anchor="left")

        deep = q.get("deep") or q.get("tip", "")
        wrapped = textwrap.wrap(deep, width=88)
        y = panel.top + 56
        for line in wrapped:
            draw_text(surface, line, FONT_SM, WHITE,
                      panel.left + 24, y, anchor="left")
            y += 30

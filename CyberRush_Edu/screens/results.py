# screens/results.py
# Final results screen with score, grade and replay option.

import pygame
from settings import *
from utils.draw       import draw_text, draw_card, get_font
from utils.button     import Button
from utils.background import SpaceBackground
from utils.sound      import get_sounds
from utils            import highscore
from screens.review   import ReviewScreen   # for category_stats helper


class ResultsScreen:
    def __init__(self, W: int, H: int):
        self.W, self.H  = W, H
        self.score      = 0
        self.mode       = "space"
        self.best_combo = 0
        self.bg         = SpaceBackground(W, H)
        self.high       = 0           # previous high score (before this run)
        self.new_record = False
        self.reveal_t   = 0.0         # 0 → ~1.0 over the reveal animation
        self.encountered: list[dict] = []
        self.cat_stats: list[dict]   = []
        cx              = W // 2

        # Three buttons across the bottom: PLAY AGAIN | REVIEW | MAIN MENU
        self.btn_again  = Button("PLAY AGAIN", cx - 230, H - 70,
                                 width=210, height=52, style="primary")
        self.btn_review = Button("REVIEW",     cx,       H - 70,
                                 width=200, height=52, style="warning")
        self.btn_menu   = Button("MAIN MENU",  cx + 230, H - 70,
                                 width=210, height=52, style="ghost")

        # Keyboard navigation across the horizontal button row.
        self._nav = [self.btn_again, self.btn_review, self.btn_menu]
        self._focus_idx = 0
        self._nav[0].focused = True

    def set_result(self, score: int, mode: str,
                   best_combo: int = 0,
                   encountered: list[dict] | None = None):
        self.score       = score
        self.mode        = mode
        self.best_combo  = best_combo
        self.reveal_t    = 0.0
        self.encountered = encountered or []
        # Compute per-category aggregates for the stats panel
        self.cat_stats   = ReviewScreen.category_stats(self.encountered)
        # High score handling — capture previous best, then save new record
        self.high       = highscore.get(mode)
        self.new_record = highscore.submit(mode, score)
        # Play a one-shot reaction matching the grade earned.
        if score >= 8000:
            get_sounds().play("srank")
        elif score >= 5000:
            get_sounds().play("arank")
        else:
            get_sounds().play("lowrank")

    def _grade(self):
        if   self.score >= 8000: return "S", "Cyber Defender",    CYAN
        elif self.score >= 5000: return "A", "Security Expert",   GREEN
        elif self.score >= 3000: return "B", "Phish Spotter",     AMBER
        elif self.score >= 1000: return "C", "Getting There",     ORANGE
        else:                    return "D", "Keep Practising",   RED

    def update(self, dt: float):
        self.bg.update(speed_mult=0.3)
        # Advance grade-reveal animation (caps at 1.0 after ~0.7 s)
        if self.reveal_t < 1.0:
            self.reveal_t = min(1.0, self.reveal_t + dt / 0.7)

    def _set_focus(self, idx: int):
        self._nav[self._focus_idx].focused = False
        self._focus_idx = idx % len(self._nav)
        self._nav[self._focus_idx].focused = True

    def handle_event(self, event) -> str | None:
        # Keyboard navigation across the horizontal button row.
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._set_focus(self._focus_idx - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._set_focus(self._focus_idx + 1)
            elif event.key == pygame.K_TAB:
                step = -1 if event.mod & pygame.KMOD_SHIFT else 1
                self._set_focus(self._focus_idx + step)

        if event.type == pygame.MOUSEMOTION:
            for i, b in enumerate(self._nav):
                if b.rect.collidepoint(event.pos) and i != self._focus_idx:
                    self._set_focus(i)
                    break

        if self.btn_again.activated(event):
            get_sounds().stop("srank", "arank", "lowrank")
            return "play_again"
        if self.btn_review.activated(event):
            get_sounds().stop("srank", "arank", "lowrank")
            return "review"
        if self.btn_menu.activated(event):
            get_sounds().stop("srank", "arank", "lowrank")
            return "menu"
        return None

    def draw(self, surface):
        self.bg.draw(surface)
        cx = self.W // 2

        draw_text(surface, "CYBERRUSH", FONT_LG, CYAN_DIM, cx, 42, bold=True)

        grade, title, col = self._grade()

        # Grade card
        gc = pygame.Rect(cx - 180, 80, 360, 180)
        draw_card(surface, gc, colour=NAVY2, border_colour=col, radius=20)

        # Animated grade reveal: scale up + fade in via reveal_t (0 → 1).
        # Eased so the letter "punches" in.
        t      = self.reveal_t
        ease   = 1 - (1 - t) * (1 - t)     # ease-out quadratic
        scale  = 0.4 + 0.6 * ease
        alpha  = int(255 * ease)
        font   = get_font(int(FONT_HUGE * scale), bold=True)
        img    = font.render(grade, True, col)
        img.set_alpha(alpha)
        rect   = img.get_rect(center=(cx, 148))
        surface.blit(img, rect)

        # Title appears once the grade has finished punching in
        if t >= 0.85:
            draw_text(surface, title, FONT_MD, WHITE, cx, 222, bold=True)

        draw_text(surface, f"Score:  {self.score:,}  pts",
                  FONT_LG, WHITE, cx, 290, bold=True)

        # High score line + NEW RECORD badge
        if self.new_record:
            draw_text(surface, "★ NEW HIGH SCORE ★",
                      FONT_SM, AMBER, cx, 326, bold=True)
        else:
            draw_text(surface, f"Best:  {self.high:,}",
                      FONT_XS, MUTED, cx, 326)

        mode_label = "Space Mode" if self.mode == "space" else "Car Mode"
        combo_label = (f"  ·  Best combo: x{self.best_combo}"
                       if self.best_combo >= 2 else "")
        draw_text(surface, f"Mode: {mode_label}{combo_label}",
                  FONT_XS, MUTED, cx, 348)

        # Per-category breakdown card — replaces the old static safety tip
        self._draw_stats_panel(surface, cx)

        self.btn_again.draw(surface)
        self.btn_review.draw(surface)
        self.btn_menu.draw(surface)

    def _draw_stats_panel(self, surface, cx: int):
        """Per-category hit/dodged/collected breakdown."""
        panel = pygame.Rect(cx - 380, 376, 760, 220)
        draw_card(surface, panel, colour=NAVY3,
                  border_colour=BORDER, radius=14)

        draw_text(surface, "BREAKDOWN BY CATEGORY",
                  FONT_SM, CYAN, panel.left + 20, panel.top + 22,
                  bold=True, anchor="left")

        if not self.cat_stats:
            draw_text(surface,
                      "No category data yet — play a round to see your "
                      "strengths and weak spots.",
                      FONT_XS, MUTED, panel.centerx, panel.centery)
            return

        # Top 5 categories by total encounters — rest accessible via REVIEW
        rows = self.cat_stats[:5]
        row_y = panel.top + 58
        for r in rows:
            self._draw_stat_row(surface, panel, row_y, r)
            row_y += 28

        if len(self.cat_stats) > 5:
            draw_text(surface,
                      f"+ {len(self.cat_stats) - 5} more — open REVIEW "
                      "for the full list.",
                      FONT_XS, MUTED, panel.centerx, panel.bottom - 22)

    @staticmethod
    def _draw_stat_row(surface, panel, y: int, stat: dict):
        # Category name (left)
        draw_text(surface, stat["label"], FONT_XS, WHITE,
                  panel.left + 28, y, anchor="left")

        # Phishing dodged / hit
        phish_total  = stat["phishing_hit"] + stat["phishing_dodged"]
        if phish_total > 0:
            dodged = stat["phishing_dodged"]
            hit    = stat["phishing_hit"]
            col    = GREEN if hit == 0 else (AMBER if dodged > 0 else RED)
            txt    = f"phishing  {dodged}/{phish_total} dodged"
            draw_text(surface, txt, FONT_XS, col,
                      panel.left + 320, y, anchor="left", bold=True)

        # Safe collected / missed
        safe_total = stat["safe_collected"] + stat["safe_missed"]
        if safe_total > 0:
            coll   = stat["safe_collected"]
            col    = GREEN if coll == safe_total else AMBER
            txt    = f"safe  {coll}/{safe_total} collected"
            draw_text(surface, txt, FONT_XS, col,
                      panel.right - 28, y, anchor="right", bold=True)
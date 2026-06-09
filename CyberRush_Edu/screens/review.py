# screens/review.py
# Post-game review of every cybersecurity concept the player encountered.
# Dedupes per question and shows hit/dodged/collected/missed counts plus the
# educational tip. Scrollable with mouse wheel or arrow keys.

import pygame
from collections import Counter, defaultdict
from settings import *
from utils.draw       import draw_text, draw_card, get_font
from utils.button     import Button
from utils.background import SpaceBackground
from data.questions   import CATEGORIES


# Outcome → (short label, colour)
_OUTCOME_STYLE = {
    "dodged":    ("DODGED",    GREEN),
    "hit":       ("HIT",       RED),
    "collected": ("COLLECTED", GREEN),
    "missed":    ("MISSED",    AMBER),
}


class ReviewScreen:
    ROW_HEIGHT      = 78
    HEADER_HEIGHT   = 170
    FOOTER_HEIGHT   = 90
    SCROLL_STEP_PX  = 36

    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.bg        = SpaceBackground(W, H)
        cx             = W // 2
        self.btn_back  = Button("BACK", cx, H - 50,
                                width=200, height=44, style="ghost")

        # Filled by set_data() before the screen becomes visible
        self.rows: list[dict] = []
        self.summary           = ""   # one-line counts across all encounters
        self.scroll_y          = 0
        self._content_height   = 0    # for clamping scroll

    # ── Build view from raw encounter list ─────────────
    def set_data(self, encountered: list[dict]):
        """Dedupe per question, count outcomes, build display rows."""
        self.scroll_y = 0
        if not encountered:
            self.rows    = []
            self.summary = "Nothing to review yet — play a round!"
            self._content_height = 0
            return

        # Group encounters by question text (stable identifier)
        groups: dict[str, dict] = {}
        for entry in encountered:
            q       = entry["question"]
            outcome = entry["outcome"]
            key     = q["text"]
            if key not in groups:
                groups[key] = {"question": q, "counts": Counter()}
            groups[key]["counts"][outcome] += 1

        # Sort: phishing first, then safe; within each, by category then text
        def sort_key(g):
            q   = g["question"]
            lbl = 0 if q["label"] == "phishing" else 1
            return (lbl, q.get("category", ""), q["text"])

        self.rows = sorted(groups.values(), key=sort_key)
        self._content_height = self.ROW_HEIGHT * len(self.rows) + 12

        # Top-line summary across the whole run
        totals = Counter()
        for entry in encountered:
            totals[entry["outcome"]] += 1
        self.summary = (
            f"Phishing: {totals['dodged']} dodged · {totals['hit']} hit     "
            f"Safe: {totals['collected']} collected · {totals['missed']} missed"
        )

    # ── Per-category stats helper (also used by results screen) ──
    @staticmethod
    def category_stats(encountered: list[dict]) -> list[dict]:
        """Returns per-category aggregates suitable for stats display.

        Each item: {category, label, phishing_hit, phishing_dodged,
                    safe_collected, safe_missed, total}
        """
        agg: dict[str, dict] = defaultdict(lambda: {
            "phishing_hit": 0, "phishing_dodged": 0,
            "safe_collected": 0, "safe_missed": 0,
        })
        for entry in encountered:
            q   = entry["question"]
            cat = q.get("category", "uncategorised")
            o   = entry["outcome"]
            label = q["label"]
            if label == "phishing":
                if o == "hit":    agg[cat]["phishing_hit"]    += 1
                elif o == "dodged": agg[cat]["phishing_dodged"] += 1
            else:
                if o == "collected": agg[cat]["safe_collected"] += 1
                elif o == "missed":  agg[cat]["safe_missed"]    += 1

        out = []
        for cat, counts in agg.items():
            total = sum(counts.values())
            out.append({
                "category": cat,
                "label":    CATEGORIES.get(cat, cat),
                "total":    total,
                **counts,
            })
        out.sort(key=lambda x: (-x["total"], x["label"]))
        return out

    # ── Events ─────────────────────────────────────────
    def handle_event(self, event) -> str | None:
        if self.btn_back.clicked(event):
            return "back"
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * self.SCROLL_STEP_PX
            self._clamp_scroll()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.scroll_y -= self.SCROLL_STEP_PX
                self._clamp_scroll()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll_y += self.SCROLL_STEP_PX
                self._clamp_scroll()
            elif event.key in (pygame.K_PAGEUP,):
                self.scroll_y -= self.SCROLL_STEP_PX * 5
                self._clamp_scroll()
            elif event.key in (pygame.K_PAGEDOWN,):
                self.scroll_y += self.SCROLL_STEP_PX * 5
                self._clamp_scroll()
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None

    def _clamp_scroll(self):
        max_scroll = max(0, self._content_height - self._list_height())
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

    def _list_height(self) -> int:
        return self.H - self.HEADER_HEIGHT - self.FOOTER_HEIGHT

    def update(self, dt: float):
        self.bg.update(speed_mult=0.3)

    # ── Draw ───────────────────────────────────────────
    def draw(self, surface):
        self.bg.draw(surface)

        # Dim overlay
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((5, 13, 26, 200))
        surface.blit(ov, (0, 0))

        cx = self.W // 2

        # Header
        draw_text(surface, "REVIEW", FONT_XL, CYAN, cx, 56, bold=True)
        draw_text(surface, "Every concept you saw this run",
                  FONT_SM, MUTED, cx, 96)
        draw_text(surface, self.summary, FONT_XS, AMBER,
                  cx, 130, bold=True)

        # Scrollable list area — clip so rows don't bleed into header/footer
        list_top    = self.HEADER_HEIGHT
        list_bottom = self.H - self.FOOTER_HEIGHT
        list_rect   = pygame.Rect(40, list_top, self.W - 80, list_bottom - list_top)
        prev_clip   = surface.get_clip()
        surface.set_clip(list_rect)

        y = list_top - self.scroll_y + 6
        for row in self.rows:
            if y + self.ROW_HEIGHT < list_top:
                y += self.ROW_HEIGHT
                continue
            if y > list_bottom:
                break
            self._draw_row(surface, row, list_rect.left, y, list_rect.width)
            y += self.ROW_HEIGHT

        surface.set_clip(prev_clip)

        # Scroll affordance hint
        if self._content_height > self._list_height():
            draw_text(surface, "↑ / ↓ / mouse wheel to scroll",
                      FONT_TINY, MUTED, cx, self.H - 98)

        # Empty-state fallback
        if not self.rows:
            draw_text(surface, "(No encounters recorded)",
                      FONT_SM, MUTED, cx, self.H // 2)

        self.btn_back.draw(surface)

    def _draw_row(self, surface, row, x, y, width):
        q       = row["question"]
        counts  = row["counts"]
        is_phish = q["label"] == "phishing"
        accent   = RED if is_phish else GREEN

        rect = pygame.Rect(x, y, width, self.ROW_HEIGHT - 8)
        draw_card(surface, rect, colour=NAVY3,
                  border_colour=accent, radius=10)

        # Category chip (top-left)
        cat_key   = q.get("category", "")
        cat_label = CATEGORIES.get(cat_key, cat_key or "—")
        chip_col  = AMBER if is_phish else CYAN
        draw_text(surface, cat_label.upper(),
                  FONT_TINY, chip_col,
                  rect.left + 16, rect.top + 14,
                  bold=True, anchor="left")

        # Block text (next to chip — replace \n with /)
        block_text = q["text"].replace("\n", "  ·  ")
        draw_text(surface, block_text, FONT_SM, WHITE,
                  rect.left + 16, rect.top + 36,
                  bold=True, anchor="left")

        # Tip (small, below)
        draw_text(surface, q["tip"], FONT_XS, GREY,
                  rect.left + 16, rect.top + 56, anchor="left")

        # Outcome badges (right side)
        bx = rect.right - 16
        for outcome in ("hit", "dodged", "collected", "missed"):
            n = counts.get(outcome, 0)
            if n == 0:
                continue
            label, col = _OUTCOME_STYLE[outcome]
            txt = f"{label} ×{n}" if n > 1 else label
            r = draw_text(surface, txt, FONT_XS, col,
                          bx, rect.centery, bold=True, anchor="right")
            bx = r.left - 14   # next badge sits to the left of this one

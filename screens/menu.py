# screens/menu.py
# Animated main menu — title, buttons, scrolling star background.

import pygame
import math
import random
from settings import *
from utils.draw       import draw_text, draw_card, get_font
from utils.button     import Button
from utils.background import SpaceBackground
from utils            import highscore


class MenuScreen:
    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.bg        = SpaceBackground(W, H)
        self.time      = 0.0
        cx             = W // 2

        # Layout: centre the whole title + chips + buttons block vertically.
        # Total stack height is roughly title (110) + tag (60) + chips (60)
        # + spacer (30) + buttons (200) = ~460. Anchor the title so the
        # stack sits centred in the window — looks right at both 700px and
        # 1080px window heights.
        block_h    = 460
        self._title_y = max(40, (H - block_h) // 2)
        button_top    = self._title_y + 260
        self.btn_play  = Button("PLAY",        cx, button_top,       width=300, height=58, style="primary")
        self.btn_howto = Button("HOW TO PLAY", cx, button_top + 72,  width=300, height=46, style="ghost")
        self.btn_quit  = Button("QUIT",        cx, button_top + 132, width=300, height=46, style="danger")

        # Keyboard navigation: ordered list of focusable buttons + the
        # current focus index. Up/Down moves focus, Enter/Space activates.
        self._nav = [self.btn_play, self.btn_howto, self.btn_quit]
        self._focus_idx = 0
        self._nav[0].focused = True

        # Floating particles behind the title — small extra polish
        self._particles = [
            {
                "x": random.uniform(0, W),
                "y": random.uniform(0, H),
                "r": random.uniform(1.5, 3.0),
                "vx": random.uniform(-0.15, 0.15),
                "vy": random.uniform(-0.4, -0.1),
                "hue": random.choice([CYAN, PURPLE, BLUE]),
                "alpha": random.randint(40, 120),
            }
            for _ in range(28)
        ]

    def update(self, dt: float):
        self.time += dt
        self.bg.update(speed_mult=0.6)

        # Float the particles upward; respawn at the bottom
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < -10:
                p["y"] = self.H + 10
                p["x"] = random.uniform(0, self.W)

    def handle_event(self, event) -> str | None:
        # Arrow keys move focus between buttons
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s,
                pygame.K_TAB):
            step = -1 if event.key in (pygame.K_UP, pygame.K_w) else 1
            if event.key == pygame.K_TAB:
                step = -1 if event.mod & pygame.KMOD_SHIFT else 1
            self._nav[self._focus_idx].focused = False
            self._focus_idx = (self._focus_idx + step) % len(self._nav)
            self._nav[self._focus_idx].focused = True
            return None

        # Mouse hover should also move the keyboard focus so the ring tracks
        # whichever button you're about to click.
        if event.type == pygame.MOUSEMOTION:
            for i, b in enumerate(self._nav):
                if b.rect.collidepoint(event.pos) and i != self._focus_idx:
                    self._nav[self._focus_idx].focused = False
                    self._focus_idx = i
                    self._nav[self._focus_idx].focused = True

        if self.btn_play.activated(event):   return "mode_select"
        if self.btn_howto.activated(event):  return "howtoplay"
        if self.btn_quit.activated(event):
            pygame.quit(); raise SystemExit
        return None

    # ── Helpers ─────────────────────────────────────────
    def _draw_particles(self, surface):
        for p in self._particles:
            s = pygame.Surface((int(p["r"]) * 4, int(p["r"]) * 4),
                               pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["hue"], p["alpha"]),
                               (int(p["r"]) * 2, int(p["r"]) * 2),
                               int(p["r"]))
            surface.blit(s, (p["x"], p["y"]))

    def _draw_title(self, surface, cx, base_y):
        # Animated pulse — the title gently breathes
        pulse = 1 + 0.025 * math.sin(self.time * 2.4)
        size  = int(FONT_HUGE * pulse * 0.85)
        font  = get_font(size, bold=True)

        # Multi-layer neon glow halo behind the title — bigger, softer, and
        # split across two hues so it reads as a gradient bloom rather than
        # a flat shadow. This is what makes the title look "aesthetic"
        # instead of just "cyan text".
        glow_layers = [
            (10, (255, 110, 200), 22),   # outer magenta haze
            (6,  (120, 200, 255), 38),   # mid teal-blue
            (3,  (180, 240, 255), 70),   # close ice-blue
        ]
        for offset, colour, alpha in glow_layers:
            glow = font.render("CYBERRUSH", True, colour)
            gs   = pygame.Surface((glow.get_width() + offset * 2,
                                   glow.get_height() + offset * 2),
                                  pygame.SRCALPHA)
            # Smear the glow in four directions so it looks omni-directional
            for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
                gs.blit(glow, (offset + dx, offset + dy))
            gs.set_alpha(alpha)
            surface.blit(gs, (cx - gs.get_width() // 2,
                              base_y - offset))

        # Vaporwave gradient title — render the text once, then paint a
        # vertical gradient over it through SRCALPHA blending. Top of each
        # letter is ice-cyan, bottom is hot magenta-pink.
        title       = font.render("CYBERRUSH", True, (255, 255, 255))
        tw, th      = title.get_size()
        gradient    = pygame.Surface((tw, th), pygame.SRCALPHA)
        top_col     = (140, 240, 255)    # ice cyan
        bot_col     = (255, 110, 200)    # hot pink
        for y in range(th):
            t = y / max(1, th - 1)
            r = int(top_col[0] + (bot_col[0] - top_col[0]) * t)
            g = int(top_col[1] + (bot_col[1] - top_col[1]) * t)
            b = int(top_col[2] + (bot_col[2] - top_col[2]) * t)
            pygame.draw.line(gradient, (r, g, b), (0, y), (tw, y))
        # Mask the gradient to the title's letter shape
        gradient.blit(title, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(gradient, (cx - tw // 2, base_y))

        # Underline accent — gradient bar that matches the title hues
        bar_w = int(tw * 0.6)
        bar_x = cx - bar_w // 2
        bar_y = base_y + th + 6
        for i in range(bar_w):
            k = i / max(1, bar_w - 1)
            r = int(top_col[0] + (bot_col[0] - top_col[0]) * k)
            g = int(top_col[1] + (bot_col[1] - top_col[1]) * k)
            b = int(top_col[2] + (bot_col[2] - top_col[2]) * k)
            pygame.draw.rect(surface, (r, g, b),
                             (bar_x + i, bar_y, 1, 3))

    # ── Draw ─────────────────────────────────────────────
    def draw(self, surface):
        self.bg.draw(surface)
        self._draw_particles(surface)

        cx = self.W // 2

        # Title sits at the anchor computed in __init__ so the whole stack
        # is vertically centred whether the window is 700px or 1080px tall.
        self._draw_title(surface, cx, self._title_y)

        # Tag-line + subtitle
        tag_y = self._title_y + 100
        draw_text(surface, "Dodge the threats.  Collect the safe.",
                  FONT_SM, WHITE, cx, tag_y, bold=True)
        draw_text(surface, "An arcade runner that teaches cyber awareness",
                  FONT_XS, GREY, cx, tag_y + 26)

        # Three feature tags pinned just above the buttons — purely cosmetic
        # but they sell the game faster than a paragraph of copy
        tags    = [("3 LIVES", AMBER), ("44 CONCEPTS", CYAN), ("7 CATEGORIES", GREEN)]
        chip_y  = tag_y + 60
        chip_w  = 130
        gap     = 14
        total_w = chip_w * len(tags) + gap * (len(tags) - 1)
        start_x = cx - total_w // 2
        for i, (txt, col) in enumerate(tags):
            r = pygame.Rect(start_x + i * (chip_w + gap), chip_y, chip_w, 28)
            draw_card(surface, r, colour=NAVY2, border_colour=col, radius=14)
            draw_text(surface, txt, FONT_XS, col, r.centerx, r.centery, bold=True)

        # Buttons
        self.btn_play.draw(surface)
        self.btn_howto.draw(surface)
        self.btn_quit.draw(surface)

        # High-score line — show whichever modes have a record
        hs_space = highscore.get("space")
        hs_quiz  = highscore.get("quiz")
        if hs_space or hs_quiz:
            parts = []
            if hs_space: parts.append(f"SPACE  {hs_space:,}")
            if hs_quiz:  parts.append(f"QUIZ  {hs_quiz:,}")
            draw_text(surface, "BEST   " + "    ".join(parts),
                      FONT_XS, AMBER, cx, self.H - 54, bold=True)

        draw_text(surface,
                  "Arrow keys / WASD  ·  ESC pause  ·  M mute  ·  F11 fullscreen  ·  C colour-blind",
                  FONT_XS, MUTED, cx, self.H - 22)

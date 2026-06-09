# utils/button.py
# Single reusable Button class for every screen.

import pygame
from settings import *
from utils.draw import get_font


class Button:
    STYLES = {
        "primary":  (CYAN,    NAVY,  CYAN_DIM),
        "danger":   (RED,     WHITE, RED_DIM),
        "success":  (GREEN,   NAVY,  GREEN_DIM),
        "ghost":    (NAVY3,   CYAN,  BORDER),
        "warning":  (AMBER,   NAVY,  AMBER_DIM),
        "purple":   (PURPLE,  WHITE, (80, 30, 180)),
    }

    def __init__(self, text: str, cx: int, cy: int,
                 width=260, height=54,
                 style="primary", font_size=FONT_SM):
        self.text     = text
        self.font_size = font_size
        self.rect     = pygame.Rect(0, 0, width, height)
        self.rect.center = (cx, cy)

        col, tcol, dim = self.STYLES.get(style, self.STYLES["primary"])
        self.colour     = col
        self.text_colour = tcol
        self.dim_colour  = dim
        # Whether the keyboard focus ring should be drawn around this button.
        # Set externally by screens that implement keyboard navigation.
        self.focused = False

    # ── Query ─────────────────────────────────────────
    def hovered(self) -> bool:
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def clicked(self, event) -> bool:
        hit = (event.type == pygame.MOUSEBUTTONDOWN
               and event.button == 1
               and self.rect.collidepoint(event.pos))
        if hit:
            # Play UI click sound. Imported lazily to avoid circular imports.
            from utils.sound import get_sounds
            get_sounds().play("click")
        return hit

    def activated(self, event) -> bool:
        """True if this button was clicked OR Enter/Space was pressed while
        it had the keyboard focus. Used by screens that support keyboard
        navigation alongside mouse input."""
        if self.clicked(event):
            return True
        if (self.focused
                and event.type == pygame.KEYDOWN
                and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                                  pygame.K_SPACE)):
            from utils.sound import get_sounds
            get_sounds().play("click")
            return True
        return False

    # ── Draw ──────────────────────────────────────────
    def draw(self, surface):
        h   = self.hovered() or self.focused
        col = self.colour if not h else tuple(min(255, c + 35) for c in self.colour)

        pygame.draw.rect(surface, col, self.rect, border_radius=12)
        pygame.draw.rect(surface, tuple(min(255, c + 70) for c in self.colour),
                         self.rect, 2, border_radius=12)

        # Keyboard-focus ring — an extra outer outline so it's clear which
        # button Enter would activate even when the mouse isn't on screen.
        if self.focused:
            ring = self.rect.inflate(10, 10)
            pygame.draw.rect(surface, WHITE, ring, 2, border_radius=14)

        font  = get_font(self.font_size, bold=True)
        label = font.render(self.text, True, self.text_colour)
        lr    = label.get_rect(center=(self.rect.centerx,
                                       self.rect.centery + (1 if h else 0)))
        surface.blit(label, lr)

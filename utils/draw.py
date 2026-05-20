# utils/draw.py
# Reusable drawing helper functions used across all screens.

import pygame
from settings import *

# Font cache — avoids re-creating font objects every frame
_font_cache: dict = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        name = pygame.font.match_font("segoeui,arial,helvetica")
        if name:
            _font_cache[key] = pygame.font.Font(name, size)
            _font_cache[key].set_bold(bold)
        else:
            _font_cache[key] = pygame.font.SysFont("arial", size, bold=bold)
    return _font_cache[key]


def draw_text(surface, text: str, size: int, colour,
              cx: int, cy: int, bold=False, anchor="center") -> pygame.Rect:
    """Render a single line of text at (cx, cy)."""
    font = get_font(size, bold)
    img  = font.render(text, True, colour)
    rect = img.get_rect()
    if   anchor == "center": rect.center   = (cx, cy)
    elif anchor == "left":   rect.midleft  = (cx, cy)
    elif anchor == "right":  rect.midright = (cx, cy)
    surface.blit(img, rect)
    return rect


def draw_multiline(surface, text: str, size: int, colour,
                   cx: int, top_y: int, line_gap=6, anchor="center") -> int:
    """Draw text with \\n newlines. Returns Y after last line."""
    font  = get_font(size)
    lines = text.split("\n")
    y     = top_y
    for line in lines:
        img  = font.render(line, True, colour)
        rect = img.get_rect()
        if   anchor == "center": rect.centerx = cx
        elif anchor == "left":   rect.left     = cx
        elif anchor == "right":  rect.right    = cx
        surface.blit(img, (rect.x, y))
        y += font.get_height() + line_gap
    return y


def draw_card(surface, rect: pygame.Rect, colour=None,
              border_colour=None, radius=14, alpha=255):
    """Draw a rounded rectangle card."""
    col = colour        or CARD
    bdr = border_colour or BORDER

    if alpha < 255:
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, alpha),
                         pygame.Rect(0, 0, rect.width, rect.height),
                         border_radius=radius)
        surface.blit(s, rect.topleft)
    else:
        pygame.draw.rect(surface, col, rect, border_radius=radius)

    pygame.draw.rect(surface, bdr, rect, 2, border_radius=radius)


def draw_bar(surface, cx: int, cy: int, width: int, height: int,
             value: float, max_value: float,
             colour=CYAN, bg=NAVY3, radius=-1):
    """Draw a horizontal progress / timer bar."""
    if radius < 0:
        radius = height // 2
    bg_rect   = pygame.Rect(cx - width // 2, cy - height // 2, width, height)
    fill_w    = int(width * max(0, min(1, value / max(max_value, 1))))
    fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, max(fill_w, radius * 2), height)

    pygame.draw.rect(surface, bg,     bg_rect,   border_radius=radius)
    if fill_w > 0:
        pygame.draw.rect(surface, colour, fill_rect, border_radius=radius)
    pygame.draw.rect(surface, BORDER, bg_rect,   2, border_radius=radius)


def draw_hearts(surface, lives: int, max_lives: int,
                right_x: int, cy: int, size=22):
    """Draw filled/empty heart icons for lives."""
    gap = size + 8
    for i in range(max_lives):
        x   = right_x - (max_lives - i) * gap
        col = RED if i < lives else DARK_MUTED
        # Simple heart shape using two circles + triangle
        r = size // 2
        pygame.draw.circle(surface, col, (x - r // 2, cy - 2), r // 2 + 2)
        pygame.draw.circle(surface, col, (x + r // 2, cy - 2), r // 2 + 2)
        points = [(x - r, cy + 1), (x + r, cy + 1), (x, cy + r + 4)]
        pygame.draw.polygon(surface, col, points)
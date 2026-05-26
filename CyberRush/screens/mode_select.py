# screens/mode_select.py
# Player picks Space mode or Car mode.

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

        self.btn_space = Button("🚀  SPACE MODE", cx - 170, H // 2 + 40,
                                width=300, height=64, style="primary")
        self.btn_car   = Button("🚗  CAR MODE",   cx + 170, H // 2 + 40,
                                width=300, height=64, style="purple")
        self.btn_back  = Button("BACK",           cx,       H - 70,
                                width=160, height=44, style="ghost")

    def update(self, dt: float):
        self.bg.update(speed_mult=0.4)

    def handle_event(self, event) -> tuple | None:
        if self.btn_space.clicked(event): return ("game", "space")
        if self.btn_car.clicked(event):   return ("game", "car")
        if self.btn_back.clicked(event):  return ("back", None)
        return None

    def draw(self, surface):
        self.bg.draw(surface)
        cx = self.W // 2

        draw_text(surface, "CHOOSE YOUR MODE", FONT_LG, CYAN,
                  cx, self.H // 2 - 80, bold=True)
        draw_text(surface, "Same cyber questions — different feel",
                  FONT_XS, MUTED, cx, self.H // 2 - 40)

        # Space card
        sc = pygame.Rect(cx - 330, self.H // 2 - 10, 290, 130)
        draw_card(surface, sc, colour=NAVY3, border_colour=CYAN, radius=16)
        draw_text(surface, "Navigate your spaceship",
                  FONT_XS, GREY, sc.centerx, sc.centery - 20)
        draw_text(surface, "Full 2D movement",
                  FONT_XS, MUTED, sc.centerx, sc.centery)

        # Car card
        cc = pygame.Rect(cx + 40, self.H // 2 - 10, 290, 130)
        draw_card(surface, cc, colour=NAVY3, border_colour=PURPLE, radius=16)
        draw_text(surface, "Race down the highway",
                  FONT_XS, GREY, cc.centerx, cc.centery - 20)
        draw_text(surface, "3-lane switching",
                  FONT_XS, MUTED, cc.centerx, cc.centery)

        self.btn_space.draw(surface)
        self.btn_car.draw(surface)
        self.btn_back.draw(surface)
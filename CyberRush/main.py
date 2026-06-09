# main.py
# Entry point — run this file to launch CyberRush.
# Manages the state machine that switches between all screens.

import pygame
import sys
from settings import *

from screens.menu        import MenuScreen
from screens.mode_select import ModeSelectScreen
from screens.game        import GameScreen
from screens.pause       import PauseScreen
from screens.results     import ResultsScreen
from utils.sound         import get_sounds


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    window = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock  = pygame.time.Clock()

    # Initialise the audio system *after* pygame.init() and start the BGM.
    # Safe if files are missing — see utils/sound.py.
    sounds = get_sounds()
    sounds.start_music()

    # Instantiate all screens once — reuse throughout
    menu        = MenuScreen(WINDOW_W, WINDOW_H)
    mode_select = ModeSelectScreen(WINDOW_W, WINDOW_H)
    game        = GameScreen(WINDOW_W, WINDOW_H)
    pause       = PauseScreen(WINDOW_W, WINDOW_H)
    results     = ResultsScreen(WINDOW_W, WINDOW_H)

    # State machine
    # States: "menu" | "mode_select" | "game" | "pause" | "results"
    state     = "menu"
    game_mode = "space"   # remembered so results screen knows

    while True:
        dt = clock.tick(FPS) / 1000.0   # seconds since last frame

        # ── EVENTS ──────────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Menu ──
            if state == "menu":
                action = menu.handle_event(event)
                if action == "mode_select":
                    state = "mode_select"

            # ── Mode select ──
            elif state == "mode_select":
                result = mode_select.handle_event(event)
                if result:
                    action, mode = result
                    if action == "game":
                        game_mode = mode
                        game.set_mode(mode)
                        state = "game"
                    elif action == "back":
                        state = "menu"

            # ── Game ──
            elif state == "game":
                action = game.handle_event(event)
                if action == "pause":
                    state = "pause"
                    sounds.pause_music()
                if game.ready_for_results(event):
                    results.set_result(game.score, game_mode)
                    state = "results"

            # ── Pause ──
            elif state == "pause":
                action = pause.handle_event(event)
                if action == "resume":
                    state = "game"
                    sounds.unpause_music()
                elif action == "menu":
                    state = "menu"
                    sounds.unpause_music()

            # ── Results ──
            elif state == "results":
                action = results.handle_event(event)
                if action == "play_again":
                    game.set_mode(game_mode)
                    state = "game"
                elif action == "menu":
                    state = "menu"

        # ── UPDATE ──────────────────────────────────────────
        if   state == "menu":        menu.update(dt)
        elif state == "mode_select": mode_select.update(dt)
        elif state == "game":        game.update(dt)
        elif state == "results":     results.update(dt)

        # ── DRAW ────────────────────────────────────────────
        if   state == "menu":        menu.draw(window)
        elif state == "mode_select": mode_select.draw(window)
        elif state == "game":
            game.draw(window)
        elif state == "pause":
            game.draw(window)       # game still visible behind pause
            pause.draw(window)
        elif state == "results":     results.draw(window)

        pygame.display.flip()


if __name__ == "__main__":
    main()
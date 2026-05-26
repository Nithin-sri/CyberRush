# main.py
# Entry point — run this file to launch CyberRush.
# Manages the state machine that switches between all screens.

import pygame
import sys
import settings
from settings import *

from screens.menu        import MenuScreen
from screens.mode_select import ModeSelectScreen
from screens.game        import GameScreen
from screens.pause       import PauseScreen
from screens.results     import ResultsScreen
from screens.howtoplay   import HowToPlayScreen
from screens.review      import ReviewScreen
from utils.sound         import get_sounds
from utils               import prefs


def _try_maximise():
    """Ask the OS to maximise the SDL window so it fills the desktop while
    keeping the title bar (close / minimise / restore buttons).

    Uses pygame's internal SDL2 bindings. Silently no-ops if they're not
    available — the window will still open at its initial size.
    """
    try:
        import pygame._sdl2.video as sdl2_video
        sdl2_video.Window.from_display_module().maximize()
    except Exception:
        pass


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    # ── Window sizing ──────────────────────────────────────
    # We deliberately do NOT use pygame.SCALED — it preserves the 1100:700
    # aspect ratio and pillarboxes the game with black bars on a 16:9 panel.
    # Instead we render the screens at the actual window size and rebuild
    # them whenever the window is resized. RESIZABLE gives a normal window
    # with the OS title bar (close / minimise / restore).
    try:
        info   = pygame.display.Info()
        disp_w = info.current_w
        disp_h = info.current_h
    except Exception:
        disp_w, disp_h = WINDOW_W, WINDOW_H

    # Open at a sensible initial size (close to fullscreen, but leaving room
    # for the OS title bar + taskbar), then ask SDL to maximise. The user
    # can drag the window or hit the maximise/restore button to change it.
    init_w = max(WINDOW_W, disp_w - 40)
    init_h = max(WINDOW_H, disp_h - 100)
    window = pygame.display.set_mode((init_w, init_h), pygame.RESIZABLE)
    _try_maximise()

    # Pygame doesn't always return the maximised size right away. Pump events
    # once so the resize is picked up before we instantiate screens.
    pygame.event.pump()
    cur_w, cur_h = window.get_size()

    clock        = pygame.time.Clock()
    fullscreen   = False
    last_win_size = (cur_w, cur_h)

    # Initialise the audio system *after* pygame.init() and start the BGM.
    # Safe if files are missing — see utils/sound.py.
    sounds = get_sounds()
    sounds.start_music()

    # Instantiate all screens at the current window size.
    def build_screens(w, h):
        return {
            "menu":        MenuScreen(w, h),
            "mode_select": ModeSelectScreen(w, h),
            "game":        GameScreen(w, h),
            "pause":       PauseScreen(w, h),
            "results":     ResultsScreen(w, h),
            "howto":       HowToPlayScreen(w, h),
            "review":      ReviewScreen(w, h),
        }

    screens = build_screens(cur_w, cur_h)
    menu        = screens["menu"]
    mode_select = screens["mode_select"]
    game        = screens["game"]
    pause       = screens["pause"]
    results     = screens["results"]
    howto       = screens["howto"]
    review      = screens["review"]

    # State machine
    # States: "menu" | "howtoplay" | "mode_select" | "game" | "pause" | "results" | "review"
    # First launch: show tutorial automatically, then mark it seen.
    state     = "howtoplay" if not prefs.get("seen_tutorial") else "menu"
    game_mode = "space"   # remembered so results screen knows

    while True:
        dt = clock.tick(FPS) / 1000.0   # seconds since last frame

        # ── EVENTS ──────────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Window resized — rebuild every screen at the new size so
            # layouts (buttons, cards, HUD) reflow to fill the new space.
            if event.type == pygame.VIDEORESIZE:
                new_w, new_h = max(800, event.w), max(560, event.h)
                window = pygame.display.set_mode(
                    (new_w, new_h), pygame.RESIZABLE)
                last_win_size = (new_w, new_h)
                screens = build_screens(new_w, new_h)
                menu, mode_select, game = (screens["menu"],
                                           screens["mode_select"],
                                           screens["game"])
                pause, results = screens["pause"], screens["results"]
                howto, review  = screens["howto"], screens["review"]

            # ── Global hotkeys (work from any screen) ──
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    sounds.toggle_mute()
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        # True fullscreen (no chrome). Use the desktop
                        # resolution so we still avoid black bars.
                        window = pygame.display.set_mode(
                            (disp_w, disp_h), pygame.FULLSCREEN)
                        new_size = window.get_size()
                    else:
                        window = pygame.display.set_mode(
                            last_win_size, pygame.RESIZABLE)
                        new_size = last_win_size
                    screens = build_screens(*new_size)
                    menu, mode_select, game = (screens["menu"],
                                               screens["mode_select"],
                                               screens["game"])
                    pause, results = screens["pause"], screens["results"]
                    howto, review  = screens["howto"], screens["review"]
                elif event.key == pygame.K_c:
                    settings.COLORBLIND_MODE = not settings.COLORBLIND_MODE

            # ── Menu ──
            if state == "menu":
                action = menu.handle_event(event)
                if action == "mode_select":
                    state = "mode_select"
                elif action == "howtoplay":
                    state = "howtoplay"

            # ── How-to-play popup ──
            elif state == "howtoplay":
                action = howto.handle_event(event)
                if action == "dismiss":
                    prefs.set("seen_tutorial", True)
                    state = "menu"

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
                    results.set_result(game.score, game_mode,
                                       game.best_combo, game.encountered)
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
                elif action == "review":
                    review.set_data(results.encountered)
                    state = "review"
                elif action == "menu":
                    state = "menu"

            # ── Review ──
            elif state == "review":
                action = review.handle_event(event)
                if action == "back":
                    state = "results"

        # ── UPDATE ──────────────────────────────────────────
        if   state == "menu":        menu.update(dt)
        elif state == "howtoplay":   howto.update(dt)
        elif state == "mode_select": mode_select.update(dt)
        elif state == "game":        game.update(dt)
        elif state == "results":     results.update(dt)
        elif state == "review":      review.update(dt)

        # ── DRAW ────────────────────────────────────────────
        if   state == "menu":        menu.draw(window)
        elif state == "howtoplay":   howto.draw(window)
        elif state == "mode_select": mode_select.draw(window)
        elif state == "game":
            game.draw(window)
        elif state == "pause":
            game.draw(window)       # game still visible behind pause
            pause.draw(window)
        elif state == "results":     results.draw(window)
        elif state == "review":      review.draw(window)

        pygame.display.flip()


if __name__ == "__main__":
    main()

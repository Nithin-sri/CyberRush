# utils/sound.py
# Tiny, safe wrapper around pygame.mixer.
#
# Design goals:
#   • If pygame.mixer can't init (no audio device, headless box), the game
#     still runs — every method becomes a no-op.
#   • If a sound file is missing, that one sound is just silent. No crash.
#   • One global instance: `from utils.sound import sounds` everywhere.

import os
import pygame

# Where the audio files live (relative to the project root)
SOUND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "assets", "sounds")

# Map of "event name" → filename inside SOUND_DIR
SFX_FILES = {
    "click":     "click.wav",
    "correct":   "correct.wav",
    "wrong":     "wrong.wav",
    "gameover":  "gameover.wav",
    "lane":      "lane.wav",    # short whoosh on lane change in car mode
    "srank":     "srank.wav",   # plays once when player earns an S rank
    "arank":     "arank.wav",   # plays once when player earns an A rank
    "lowrank":   "lowrank.wav", # plays once for grades below A (B, C, D)
}

# Background music — try .ogg first (smaller), fall back to .wav.
MUSIC_CANDIDATES = ("music.ogg", "music.wav")


class SoundManager:
    """Loads all SFX once, plays them on demand. Tolerant of missing files."""

    def __init__(self,
                 sfx_volume:   float = 0.7,
                 music_volume: float = 0.4,
                 enabled:      bool  = True):
        self.enabled      = enabled
        self.sfx_volume   = sfx_volume
        self.music_volume = music_volume
        self._sfx: dict[str, pygame.mixer.Sound] = {}
        self._ready          = False
        self._music_loaded   = False

        if not self.enabled:
            return

        # 1) Try to init the mixer. If this fails (no audio), give up gracefully.
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16,
                                  channels=2, buffer=512)
            pygame.mixer.init()
            self._ready = True
        except pygame.error as e:
            print(f"[sound] mixer init failed — running silently ({e})")
            self.enabled = False
            return

        # 2) Pre-load each SFX. Missing files are skipped, not fatal.
        for key, name in SFX_FILES.items():
            path = os.path.join(SOUND_DIR, name)
            if not os.path.isfile(path):
                print(f"[sound] missing: {name} — that event will be silent")
                continue
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(self.sfx_volume)
                self._sfx[key] = snd
            except pygame.error as e:
                print(f"[sound] could not load {name}: {e}")

        # 3) Find a usable music file (don't load it yet — start_music does)
        self._music_path: str | None = None
        for cand in MUSIC_CANDIDATES:
            p = os.path.join(SOUND_DIR, cand)
            if os.path.isfile(p):
                self._music_path = p
                break
        if self._music_path is None:
            print(f"[sound] no music file ({' or '.join(MUSIC_CANDIDATES)}) — "
                  "background music disabled")

    # ── SFX ───────────────────────────────────────────────────
    def play(self, key: str):
        """Play a one-shot sound by name ('click', 'correct', 'wrong', 'gameover')."""
        if not self.enabled or not self._ready:
            return
        snd = self._sfx.get(key)
        if snd is not None:
            snd.play()

    def stop(self, *keys: str):
        """Stop one or more named sounds immediately. Missing keys are ignored."""
        if not self._ready:
            return
        for k in keys:
            snd = self._sfx.get(k)
            if snd is not None:
                snd.stop()

    # ── Music ─────────────────────────────────────────────────
    def start_music(self):
        """Start looping the background music. Safe to call multiple times."""
        if not self.enabled or not self._ready or self._music_path is None:
            return
        if pygame.mixer.music.get_busy():
            return  # already playing
        try:
            pygame.mixer.music.load(self._music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=-1)   # -1 = loop forever
        except pygame.error as e:
            print(f"[sound] music failed to start: {e}")

    def pause_music(self):
        if self.enabled and self._ready:
            pygame.mixer.music.pause()

    def unpause_music(self):
        if self.enabled and self._ready:
            pygame.mixer.music.unpause()

    def stop_music(self):
        if self.enabled and self._ready:
            pygame.mixer.music.stop()

    # ── Volume / mute ─────────────────────────────────────────
    def set_sfx_volume(self, v: float):
        self.sfx_volume = max(0.0, min(1.0, v))
        for s in self._sfx.values():
            s.set_volume(self.sfx_volume)

    def set_music_volume(self, v: float):
        self.music_volume = max(0.0, min(1.0, v))
        if self._ready:
            pygame.mixer.music.set_volume(self.music_volume)

    def toggle_mute(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.unpause_music()
        else:
            self.pause_music()


# ── One shared instance for the whole game ───────────────────
# IMPORTANT: do NOT construct this at import time, because pygame.mixer needs
# pygame.init() to have run first. We create it lazily via get_sounds().
_instance: SoundManager | None = None


def get_sounds() -> SoundManager:
    """Return the global SoundManager, creating it on first call."""
    global _instance
    if _instance is None:
        _instance = SoundManager()
    return _instance

# CyberRush — Educational Edition

A fast-paced endless runner that **teaches** cybersecurity awareness — not just tests reflexes. This edition forces a learning beat on every mistake and gives you a full post-game review of every concept you faced.

## Screenshots

Drop in-game captures into `screenshots/` and uncomment the lines below.

<!--
![Main menu](screenshots/menu.png)
![How-to-play tutorial](screenshots/howtoplay.png)
![Mode select](screenshots/modesel.png)
![Gameplay — Space mode](screenshots/game.png)
![Results screen with category breakdown](screenshots/results.png)
-->

## Educational features (this edition)

- **Forced "Why?" pause** — hit a phishing block and the game freezes for 2.5 s with a deep explanation of the attack. SPACE skips early.
- **Categories** — every question is tagged (typosquatting, urgency-pressure, credential, malware-vector, social-engineering, system-hygiene, network-safety).
- **Post-game review** — a scrollable, deduped list of every concept you encountered this run with HIT / DODGED / COLLECTED / MISSED counts.
- **Per-category breakdown** — the results screen shows your weak spots and strengths at a glance.

## Game features

- **Two game modes** — Space (full 2D movement) and Car (3-lane switching)
- **Grade system** — D / C / B / A / S rankings with unique sound reactions
- **High score persistence** — tracks your best run per mode
- **Combo system** — chain safe pickups for score multipliers
- **Color-blind mode** — patterned obstacles for accessibility
- **Keyboard navigation** — every menu is fully usable without a mouse
- **Screen shake, particle effects, animated grade reveal, game-over fade-in**
- **Pause anytime with ESC**

## Controls

| Action            | Keys                                       |
| ----------------- | ------------------------------------------ |
| Move              | Arrow keys or WASD                         |
| Navigate menus    | Arrow keys / Tab — Enter or Space to confirm |
| Pause             | ESC                                        |
| Mute / unmute     | M                                          |
| Fullscreen toggle | F11  (game launches in a maximised window) |
| Color-blind mode  | C (in-game)                                |
| Confirm result    | SPACE (on game-over screen)                |

## Requirements

- Python 3.10+
- pygame 2.x

## Install & run

```bash
pip install pygame
python main.py
```

## Tests

The project has a focused test suite (19 tests) covering both smoke-level imports and core gameplay rules:

```bash
pip install pytest
python -m pytest tests/
```

Coverage highlights: level progression starts at 1 and respects the speed cap, obstacle spawn positions stay clear of the HUD, the SAFE_RATIO distribution is verified over 1000 spawns, player movement is clamped in both space and car modes, lives + invincibility frames behave correctly, and the round timer ends the run with the right reason.

## Project layout

```
CyberRush/
├── main.py                    # Entry point + state machine + window mgmt
├── settings.py                # All tunable constants
├── data/
│   └── questions.py           # Cybersecurity questions + tips + deep notes
├── entities/
│   ├── player.py              # Player ship / car
│   ├── obstacle.py            # Falling blocks (text + icon + dark inner panel)
│   └── effects.py             # Particle effects + tip popups
├── screens/
│   ├── menu.py                # Main menu (keyboard + mouse nav)
│   ├── mode_select.py         # Space vs Car
│   ├── howtoplay.py           # First-launch tutorial popup
│   ├── game.py                # Core game loop + forced WHY pause
│   ├── pause.py               # Pause overlay (keyboard + mouse nav)
│   ├── results.py             # End-of-run grade + category breakdown
│   └── review.py              # Post-game concept review (scrollable)
├── utils/
│   ├── background.py          # Animated backgrounds (stars / road)
│   ├── button.py              # Reusable button with focus ring
│   ├── draw.py                # Text + UI drawing helpers
│   ├── sound.py               # Audio manager (tolerant of missing files)
│   ├── highscore.py           # JSON-based high score store
│   └── prefs.py               # JSON-based preferences (tutorial flag, etc.)
├── assets/
│   └── sounds/                # SFX + background music
└── tests/
    ├── test_smoke.py          # Imports, sound, high-score, grades, review
    └── test_game_logic.py     # Level, spawn, distribution, movement, timer
```

## Sound assets

The game ships with synthesized placeholder sounds. To use your own, drop files into `assets/sounds/` with these exact names:

`click.wav`, `correct.wav`, `wrong.wav`, `gameover.wav`, `lane.wav`,
`srank.wav`, `arank.wav`, `lowrank.wav`, `music.wav` (or `music.ogg`).

Missing files are silently skipped — the game never crashes for a missing sound.

## Educational angle

The original CyberRush had a problem: a fast player could dodge by colour alone and learn nothing. This edition fixes that by making learning unavoidable:

1. **Hit a phishing block** → the game freezes for 2.5 s with the category name and a deep explanation of why it's dangerous. You can't skip past it without reading (SPACE forces an early exit, but you'll have seen the text).
2. **End of run** → a per-category breakdown shows your weakest categories and a REVIEW button opens a scrollable list of every concept you saw with HIT / DODGED / COLLECTED / MISSED counts.
3. **Categories** let you spot patterns — e.g. if you keep getting hit on `urgency-pressure` you know which kind of phishing fools you most.

44 questions across 7 categories, all with one-line tips and 2–3 line deep explanations.

## Design rationale

The unusual design decisions in this build were driven by three pieces of learning-science thinking. They're worth calling out because they explain why the game looks and feels different from a regular arcade runner.

### 1. Friction at the moment of failure (active recall)

Most arcade games punish failure with speed: lose a life and the game keeps moving so the player learns to react faster. CyberRush deliberately does the opposite when the player hits a phishing block — gameplay freezes for 2.5 seconds and a full-screen card appears explaining the attack category and *why* the choice was wrong. This is borrowed from spaced-repetition tutoring research: the moment of greatest learning is the moment immediately after an incorrect answer, when the brain is already engaged and looking for the right pattern. The pause is forced (SPACE can shorten it but not remove the message) so the player can't "muscle through" without absorbing the explanation. The same insight is why correct answers are *not* paused — they're rewarded with a quick green sparkle, because the loop we're reinforcing is "see threat → recognise it → dodge it," and pausing on correct play would interrupt that flow.

### 2. Patterned feedback over exam-style scoring (formative assessment)

The post-run results screen could have been a single score and a grade, but instead it shows a per-category breakdown (typosquatting, urgency-pressure, credential, social-engineering, etc.) with hit / dodged / collected / missed counts for each. This makes the feedback *diagnostic* rather than *summative*. A player who keeps hitting urgency-pressure phishing can see that as a labelled weakness and consciously slow down on those next round, instead of just seeing "C grade" and trying to play faster. The optional REVIEW screen goes further and exposes every individual concept they faced this run, deduplicated, with the educational tip. This is closer in spirit to a quiz-back tool than to an arcade leaderboard.

### 3. Accessible by default

Colour-blind players are particularly disadvantaged by a red/green threat-collect game, so the game ships with a colour-blind mode (toggle with `C`) that overlays diagonal stripes on phishing blocks and a dot grid on safe blocks. Every menu also supports full keyboard navigation (arrow keys + Enter or Space), so the game can be played mouse-free — important for users with motor difficulties and for keyboard-only environments like school computer labs. The default font is loaded via `pygame.font.match_font` so the game uses the OS's clearest sans-serif rather than pygame's pixel-sparse default, improving legibility for users with dyslexia.

These three principles — pause-on-failure for active recall, per-category diagnostic feedback, and accessibility by default — are what separate this build from a regular dodge-runner. They are the educational *features*, not just nice-to-haves.

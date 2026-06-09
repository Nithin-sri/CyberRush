# settings.py
# Every constant for the whole game lives here.
# Change a value here and it updates everywhere instantly.

# ── Window ──────────────────────────────────────────────
TITLE        = "CyberRush"
WINDOW_W     = 1100
WINDOW_H     = 700
FPS          = 60

# ── Gameplay rules ──────────────────────────────────────
PLAYER_LIVES      = 3
OBSTACLE_SPEED    = 4.0      # starting speed (pixels per frame)
SPEED_INCREMENT   = 0.0008   # how much speed increases every frame
MAX_SPEED         = 14.0
SPAWN_RATE        = 90       # frames between obstacle spawns (lower = harder)
SAFE_RATIO        = 0.45     # 45% of obstacles are "safe" collectibles
POINTS_SAFE       = 200      # points for collecting a safe item
SCORE_SURVIVAL    = 1        # points added every frame just for surviving

# Number of lanes (used in car mode)
LANES             = 3
LANE_WIDTH        = 200

# ── Player tuning ───────────────────────────────────────
PLAYER_MOVE_SPEED         = 6     # pixels per frame in space mode
PLAYER_INVINCIBLE_FRAMES  = 90    # 1.5 s of i-frames after taking a hit
LANE_COOLDOWN_FRAMES      = 18    # frames between lane changes in car mode

# ── Game feel ───────────────────────────────────────────
TIP_DURATION_FRAMES    = 360      # how long an educational tip stays on screen
SHAKE_DURATION_FRAMES  = 18       # frames of screen shake on a phishing hit
SHAKE_MAGNITUDE_PX     = 9        # max shake offset in pixels
ROUND_DURATION_SECONDS = 90       # how long each run lasts before auto-ending
TIME_WARN_SECONDS      = 10       # countdown bar turns red below this

# ── Educational pause ───────────────────────────────────
# (No timer any more — the player presses SPACE/ENTER to dismiss the WHY
# popup. The constant is kept for backward compatibility with anything that
# might still import it but is no longer consulted by the game loop.)
WHY_PAUSE_FRAMES = 0

# ── Combo system ────────────────────────────────────────
# Consecutive safe pickups multiply the next pickup's score.
# bonus = POINTS_SAFE * (1 + COMBO_STEP * min(combo, COMBO_MAX))
COMBO_STEP = 0.25
COMBO_MAX  = 8

# ── Accessibility ───────────────────────────────────────
COLORBLIND_MODE = False           # toggle in-game with 'C' key

# ── High score ──────────────────────────────────────────
HIGHSCORE_FILE = "highscore.json"  # stored in project root

# ── Colours ─────────────────────────────────────────────
# Palette: "synthwave-premium". Backgrounds are deep charcoal-purple rather
# than navy blue, so the accent colours read brighter without raising their
# saturation. Primary accent is a vibrant electric teal; secondary is a hot
# magenta-pink; warm gold carries highlights. Status colours (mint / coral)
# are tuned to feel like a modern security dashboard rather than a saturated
# pygame demo. Text is a warm champagne-white so it doesn't glare or pull
# the eye toward "another blue thing on a blue thing".

BLACK       = (0,    0,    0)
# Deep charcoal-purple background ramp — warm-leaning dark, not blue
NAVY        = (16,   12,   28)     # base
NAVY2       = (24,   18,   42)     # panel back
NAVY3       = (38,   28,   62)     # raised surface
# Card surfaces — warmer indigo, distinctly purple-leaning
CARD        = (32,   24,   56)
CARD2       = (50,   38,   84)
# Borders pick up a violet glow so cards delineate against the dark
BORDER      = (110,  85,   165)

# Signature accent — vibrant electric teal. High contrast on the purple
# background, "neon dashboard" feel without being garish.
CYAN        = (74,   232,  230)
CYAN_DIM    = (38,   150,  152)
# "BLUE" is repurposed as the secondary signature — hot magenta-pink. It's
# what the player ship and car bodies render in, so the gameplay sprite
# now reads as bright magenta against the deep purple void.
BLUE        = (240,  90,   188)
BLUE_DIM    = (158,  52,   122)
# Soft violet for car-mode chrome and accent panels
PURPLE      = (190,  130,  255)

# Status — mint for safe, coral-pink for danger, gold for highlights /
# best-scores / warnings. All three work together against the purple base.
GREEN       = (76,   240,  178)
GREEN_DIM   = (36,   150,  112)
RED         = (255,  98,   132)
RED_DIM     = (180,  55,   82)
AMBER       = (255,  208,  92)
AMBER_DIM   = (192,  148,  52)
ORANGE      = (255,  148,  92)

# Text ramp — warm champagne white at the top, soft lilac-white as it dims.
# The grey/muted bands are deliberately kept bright so small text (subtitles,
# hotkey strips, prompts like "Press SPACE to continue") is still readable
# against the deep purple gradient. Hierarchy is preserved by size and
# weight rather than by hue-darkness alone.
# All readable text colours collapse to the same warm off-white so the
# previously dim "gray" subtitle/hint text now reads as clearly as the
# score. Hierarchy is preserved by font size + bold weight instead of by
# colour dimming. DARK_MUTED stays low-contrast because it's reserved for
# decorative placeholder elements (empty hearts, car wheel outlines).
WHITE       = (248,  240,  232)   # primary text + headlines
GREY        = (248,  240,  232)   # was a dim purple-grey — now white
MUTED       = (248,  240,  232)   # was a dim purple-grey — now white
DARK_MUTED  = (130,  120,  170)   # empty-heart placeholders only

# ── Font sizes ───────────────────────────────────────────
FONT_HUGE   = 72
FONT_XL     = 52
FONT_LG     = 38
FONT_MD     = 26
FONT_SM     = 20
FONT_XS     = 15
FONT_TINY   = 12
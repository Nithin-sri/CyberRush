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
POINTS_SAFE       = 100      # points for collecting a safe item
SCORE_SURVIVAL    = 1        # points added every frame just for surviving

# Number of lanes (used in car mode)
LANES             = 3
LANE_WIDTH        = 200

# ── Colours ─────────────────────────────────────────────
BLACK       = (0,    0,    0)
NAVY        = (5,    13,   26)
NAVY2       = (8,    18,   36)
NAVY3       = (12,   24,   48)
CARD        = (13,   30,   58)
CARD2       = (18,   38,   70)
BORDER      = (28,   55,   95)

CYAN        = (0,    212,  255)
CYAN_DIM    = (0,    130,  160)
BLUE        = (30,   110,  255)
BLUE_DIM    = (15,   65,   160)
PURPLE      = (130,  60,   255)

GREEN       = (0,    230,  118)
GREEN_DIM   = (0,    155,  75)
RED         = (255,  55,   55)
RED_DIM     = (160,  25,   25)
AMBER       = (255,  175,  0)
AMBER_DIM   = (180,  115,  0)
ORANGE      = (255,  120,  30)

WHITE       = (240,  248,  255)
GREY        = (120,  160,  200)
MUTED       = (75,   115,  160)
DARK_MUTED  = (40,   65,   100)

# ── Font sizes ───────────────────────────────────────────
FONT_HUGE   = 72
FONT_XL     = 52
FONT_LG     = 38
FONT_MD     = 26
FONT_SM     = 20
FONT_XS     = 15
FONT_TINY   = 12
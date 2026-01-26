"""config.py

One More Block - 전역 설정 파일
"""

# =========================
# Game Loop / Window
# =========================
FPS = 60

WINDOW_W, WINDOW_H = 900, 600

WINDOW_MODE_WINDOWED = "windowed"
WINDOW_MODE_WINDOWED_MAX = "windowed_max"
WINDOW_MODE_BORDERLESS = "borderless"

# 요청: 풀스크린 X, 창모드 전체크기 기본
START_WINDOW_MODE = WINDOW_MODE_WINDOWED_MAX

# pygame key name (안전)
KEY_TOGGLE_WINDOW_MODE = "f11"
KEY_QUIT = "escape"
KEY_DROP = "space"

# =========================
# Layout
# =========================
FLOOR_MARGIN = 60
BLOCK_H = 34
HOVER_Y = 120

# =========================
# Movement / Physics
# =========================
FALL_SPEED = 520
HORIZONTAL_SPEED = 520
EDGE_PADDING = 12

MIN_OVERLAP_RATIO = 0.18

CAMERA_SMOOTH = 10.0
CAMERA_TOP_MARGIN = 220

# =========================
# PERFECT / COMBO
# =========================
PERFECT_RATIO = 0.95
COMBO_REWARD_EVERY = 3
COMBO_WIDTH_BONUS = 8
FLASH_TIME = 0.45

# =========================
# SHARD
# =========================
SHARD_GRAVITY = 1800
SHARD_FALL_SPEED = 200

# =========================
# BGM
# =========================
BGM_DEFAULT_ON = True
BGM_DEFAULT_VOLUME = 0.25
BGM_VOLUME_STEP = 0.05

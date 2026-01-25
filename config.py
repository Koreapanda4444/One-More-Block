# =========================
# FPS / 윈도우
# =========================
FPS = 60
WINDOW_W, WINDOW_H = 900, 600
START_BORDERLESS_MAX = True  # 풀스크린 X (테두리 없는 최대화)

# =========================
# 색상 (밝은 톤)
# =========================
BG_COLOR = (235, 245, 255)
FLOOR_COLOR = (180, 205, 230)
TEXT_COLOR = (40, 55, 75)

# =========================
# 레이아웃
# =========================
FLOOR_MARGIN = 60
BLOCK_H = 34
HOVER_Y = 120
EDGE_PADDING = 12

# =========================
# 기본 속도(난이도 계산 전 베이스)
# =========================
FALL_SPEED = 520
HORIZONTAL_SPEED = 520

# =========================
# 판정
# =========================
MIN_OVERLAP_RATIO = 0.18

# PERFECT / COMBO
PERFECT_RATIO = 0.95
COMBO_REWARD_EVERY = 3
COMBO_WIDTH_BONUS = 8
FLASH_TIME = 0.45

# =========================
# SHARD (잘린 조각 연출)
# =========================
SHARD_GRAVITY = 1800
SHARD_FALL_SPEED = 200

# =========================
# CAMERA
# =========================
CAMERA_SMOOTH = 10.0
CAMERA_TOP_MARGIN = 220

# =========================
# 착지 손맛 FX
# =========================
LAND_SQUASH_TIME = 0.10
LAND_SQUASH_PIXELS = 8
SHAKE_TIME = 0.12
SHAKE_INTENSITY = 6
PERFECT_SHAKE_MULT = 1.6

# =========================
# 난이도 곡선(점수 기반)
# =========================
DIFF_STEP_SCORE = 6
DIFF_HS_STEP = 0.07
DIFF_HS_MAX_MUL = 2.2
DIFF_FALL_STEP = 0.04
DIFF_FALL_MAX_MUL = 1.8
DIFF_JITTER_BASE = 18
DIFF_JITTER_STEP = 2
DIFF_JITTER_MAX = 52
DIFF_SPAWN_OFFSET_BASE = 120
DIFF_SPAWN_OFFSET_STEP = 6
DIFF_SPAWN_OFFSET_MAX = 220

# =========================
# 업적 UI
# =========================
TOAST_TIME = 2.2

# =========================
# SFX (Commit 10)
# =========================
DEFAULT_VOLUME = 0.70
VOLUME_STEP = 0.05

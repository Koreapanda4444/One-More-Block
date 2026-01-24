"""
config.py

게임 전체 설정(튜닝 값)을 모아두는 파일.
- 숫자만 만지면 게임 감각이 확 바뀌기 때문에, 로직 파일에 흩어지면 유지보수가 지옥됨.
- 여기만 보면 "게임이 어떤 느낌"인지 한 눈에 보이게 구성.
"""

# =========================
# FPS / 윈도우
# =========================
FPS = 60

# 창 모드 기본 크기 (F11로 테두리 없는 최대화 가능)
WINDOW_W, WINDOW_H = 900, 600

# 시작할 때 테두리 없는 최대화(풀스크린 X)
START_BORDERLESS_MAX = True

# =========================
# 색상 톤 (밝은 UI라고 했지만, 지금은 어두운 톤 기반)
# =========================
BG_COLOR = (28, 32, 38)        # 배경
FLOOR_COLOR = (38, 44, 54)     # 바닥(배경보다 약간 진하게)
TEXT_COLOR = (220, 220, 230)   # 텍스트(눈 아픈 흰색 대신 약간 회색)

# =========================
# 레이아웃
# =========================
FLOOR_MARGIN = 60              # 바닥이 화면 아래에서 떠 있는 정도
BLOCK_H = 34                   # 블록 높이
HOVER_Y = 120                  # current 블록이 move 상태일 때 y 위치
EDGE_PADDING = 12              # 좌우 화면 끝 여백(블록이 끝에 딱 붙지 않게)

# =========================
# 기본 속도
# =========================
FALL_SPEED = 520               # 낙하 속도
HORIZONTAL_SPEED = 520         # 좌우 이동 속도

# =========================
# 판정
# =========================
MIN_OVERLAP_RATIO = 0.18       # 겹침 비율이 이보다 작으면 게임오버(난이도 핵심)

# PERFECT / COMBO
PERFECT_RATIO = 0.90           # 겹침 비율이 이 이상이면 PERFECT
COMBO_REWARD_EVERY = 3         # PERFECT N회마다 보상
COMBO_WIDTH_BONUS = 8          # 다음 블록 폭 보너스(+N, 1회성)
FLASH_TIME = 0.45              # PERFECT 텍스트 표시 시간

# =========================
# SHARD(잘린 조각) 연출
# =========================
SHARD_GRAVITY = 1800           # 중력 가속도
SHARD_FALL_SPEED = 200         # 초기 낙하 속도

# =========================
# CAMERA (위로 올라가며 보이도록)
# =========================
CAMERA_SMOOTH = 10.0           # 값이 클수록 카메라가 목표로 빨리 따라감
CAMERA_TOP_MARGIN = 220        # 탑 블록이 화면 위쪽에 닿기 전에 카메라가 따라올라가게 하는 마진

# =========================
# 착지 손맛 FX
# =========================
LAND_SQUASH_TIME = 0.10        # 착지 눌림 지속 시간(초)
LAND_SQUASH_PIXELS = 8         # 눌림 정도(px)

# 화면 흔들림 FX
SHAKE_TIME = 0.12              # 흔들림 지속 시간(초)
SHAKE_INTENSITY = 6            # 기본 흔들림(px)
PERFECT_SHAKE_MULT = 1.6       # PERFECT면 흔들림 배율

# =========================
# 난이도 곡선(점수 기반)
# =========================
DIFF_STEP_SCORE = 6            # HEIGHT 6마다 난이도 레벨 +1

# 레벨당 속도 증가(상한 존재)
DIFF_HS_STEP = 0.07
DIFF_HS_MAX_MUL = 2.2

DIFF_FALL_STEP = 0.04
DIFF_FALL_MAX_MUL = 1.8

# 블록 폭 랜덤(±jitter)
DIFF_JITTER_BASE = 18
DIFF_JITTER_STEP = 2
DIFF_JITTER_MAX = 52

# 스폰 위치 랜덤 오프셋(±offset)
DIFF_SPAWN_OFFSET_BASE = 120
DIFF_SPAWN_OFFSET_STEP = 6
DIFF_SPAWN_OFFSET_MAX = 220

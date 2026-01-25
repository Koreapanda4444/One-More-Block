"""config.py

One More Block - 전역 설정 파일

원칙
- 숫자(속도/크기/판정) 같은 튜닝 값은 여기서만 관리
- 다른 파일은 config 값을 '읽기'만 한다
"""

# =========================
# Game Loop / Window
# =========================

FPS = 60

# 기본 창 크기(작은 창 모드)
WINDOW_W, WINDOW_H = 900, 600

# "풀스크린(FULLSCREEN)" 사용 X
# 대신 '창모드 전체크기(windowed_max)'를 기본으로 쓴다.
WINDOW_MODE_WINDOWED = "windowed"            # (WINDOW_W, WINDOW_H)
WINDOW_MODE_WINDOWED_MAX = "windowed_max"    # 데스크톱 해상도 크기(창 프레임 있음)
WINDOW_MODE_BORDERLESS = "borderless"        # 데스크톱 해상도 크기(프레임 없음)

# 시작 모드(요청: 풀스크린 X + 창모드 전체크기)
START_WINDOW_MODE = WINDOW_MODE_WINDOWED_MAX

# 키 설정: pygame.key.key_code()가 인식하는 이름으로 통일
# (중요) "ESC" 같은 축약어는 pygame이 모르는 경우가 있으니 "escape" 사용
KEY_TOGGLE_WINDOW_MODE = "f11"
KEY_QUIT = "escape"
KEY_DROP = "space"

# =========================
# Colors / Layout (밝은 톤)
# =========================

BG_COLOR = (235, 245, 255)
FLOOR_COLOR = (180, 205, 230)
TEXT_COLOR = (40, 55, 75)

FLOOR_MARGIN = 60

# 블록 기본 높이
BLOCK_H = 34

# 블록이 좌우로 움직이는 '공중 레일' y좌표
HOVER_Y = 120

# =========================
# Movement / Physics ("애매한 물리")
# =========================

FALL_SPEED = 520
HORIZONTAL_SPEED = 520

# 화면 가장자리 패딩(블록이 밖으로 나가지 않게)
EDGE_PADDING = 12

# 겹침이 이 비율보다 작으면 즉시 GAME OVER
MIN_OVERLAP_RATIO = 0.18

# 카메라 스무딩(값이 클수록 더 빠르게 따라감)
CAMERA_SMOOTH = 10.0

# "화면 상단에서 이 만큼 아래"로 탑이 올라오면 카메라를 위로 당김
CAMERA_TOP_MARGIN = 220

# =========================
# PERFECT / COMBO
# =========================

# 겹침 비율이 이 이상이면 PERFECT
PERFECT_RATIO = 0.95

# PERFECT가 N번 누적될 때마다 다음 블록 폭 보너스 지급
COMBO_REWARD_EVERY = 3
COMBO_WIDTH_BONUS = 8

# 화면 중앙에 텍스트가 남아있는 시간
FLASH_TIME = 0.45

# =========================
# SHARD (잘린 조각 연출)
# =========================

SHARD_GRAVITY = 1800
SHARD_FALL_SPEED = 200

# =========================
# BGM
# =========================

BGM_DEFAULT_ON = True
BGM_DEFAULT_VOLUME = 0.25
BGM_VOLUME_STEP = 0.05

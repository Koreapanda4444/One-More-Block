from __future__ import annotations

import random

from models import Block, GameState
from mechanics import get_top_block
from utils import pastel_color


def spawn_first_block(
    state: GameState,
    screen_w: int,
    floor_y: float,
    block_h: int,
    edge_padding: int,
) -> None:
    """
    런 시작 시 '바닥에 고정되는 시작 블록' 1개를 만들고,
    점수/콤보/이펙트/조각 등을 모두 초기화한다.

    - 이 시작 블록은 항상 "settled" 상태(이미 착지한 블록)
    - 이후 spawn_next_block()이 움직이는 블록(current)을 만든다.
    """
    # 시작 블록 폭: 너무 크면 화면을 넘을 수 있으니 clamp
    w = min(280, screen_w - edge_padding * 2)
    w = max(60, w)  # 너무 좁아지면 시작부터 빡세니까 최소 폭 유지

    # 시작 블록은 가운데 정렬
    x = (screen_w - w) / 2
    y = floor_y - block_h

    base = Block(
        x=float(x),
        y=float(y),
        w=float(w),
        h=float(block_h),
        color=pastel_color(),
        phase="settled",
    )

    # ===== 런 상태 초기화 =====
    # stack: 이미 쌓인 블록들(카메라/판정의 기준)
    state.stack = [base]

    # shards: 트림으로 잘려나간 조각(연출용)
    state.shards = []

    # current: 현재 조작(낙하) 중인 블록
    state.current = None

    state.score = 0
    state.game_over = False

    # ===== PERFECT / COMBO =====
    state.perfect_combo = 0
    state.width_bonus = 0           # 3연속 퍼펙트 보상 폭(+N) 1회성
    state.flash_text = ""
    state.flash_timer = 0.0

    # ===== 착지 손맛/흔들림 FX =====
    state.land_timer = 0.0
    state.land_total = 0.0
    state.last_settled = None       # 스쿼시(눌림) 적용 대상 블록

    state.shake_timer = 0.0
    state.shake_total = 0.0
    state.shake_amp = 0.0           # 흔들림 강도(px)


def spawn_next_block(
    state: GameState,
    screen_w: int,
    hover_y: int,
    block_h: int,
    edge_padding: int,
    horizontal_speed: float,
    width_jitter: int,
    spawn_offset: int,
) -> None:
    """
    다음 블록(current)을 생성한다.

    목표: '같은 게임' 느낌을 줄이기 위해 (난이도에 따라)
    - 폭 랜덤(width_jitter)
    - 스폰 위치 랜덤(spawn_offset)
    을 적용한다.

    동작 요약:
    1) 탑 블록(top) 기준 폭을 잡고 랜덤으로 흔들기
    2) 탑 블록 중심(center_x) 기준으로 좌우 오프셋을 줘서 스폰 위치 결정
    3) 좌/우 방향 랜덤으로 vx 설정하여 move 상태로 시작
    """
    top = get_top_block(state)
    if top is None:
        return  # 시작 블록이 없으면 생성 불가(정상 흐름에선 거의 없음)

    # ----- 1) 폭 결정 -----
    width_jitter = max(0, int(width_jitter))
    w = max(60, min(int(top.w), 360))  # 너무 커져도 단조로우니 상한 유지
    if width_jitter:
        w = max(60, w + random.randint(-width_jitter, width_jitter))

    # 퍼펙트 보상(1회성 폭 보너스): 적용 후 0으로 초기화
    if state.width_bonus:
        w = min(420, w + int(state.width_bonus))
        state.width_bonus = 0

    # ----- 2) 스폰 위치 결정 -----
    spawn_offset = max(0, int(spawn_offset))
    center_x = top.x + top.w / 2

    # 화면 밖으로 못 나가게 x 범위를 먼저 계산
    min_x = edge_padding
    max_x = max(edge_padding, screen_w - edge_padding - w)

    # center 기준 offset 적용 (너무 과하면 화면 밖으로 튀니까 max_offset도 clamp)
    max_offset = min(spawn_offset, int((max_x - min_x) / 2))
    offset = random.randint(-max_offset, max_offset) if max_offset > 0 else 0

    target_x = (center_x - w / 2) + offset
    x = int(max(min_x, min(target_x, max_x)))

    # ----- 3) 이동 방향 / 속도 -----
    direction = random.choice([-1, 1])
    vx = float(direction) * float(horizontal_speed)

    state.current = Block(
        x=float(x),
        y=float(hover_y),
        w=float(w),
        h=float(block_h),
        color=pastel_color(),
        phase="move",     # move 상태로 시작 → 클릭/스페이스 시 drop으로 전환
        vx=vx,
    )


def reset_run(
    state: GameState,
    screen_w: int,
    floor_y: float,
    hover_y: float,
    block_h: int,
    edge_padding: int,
    horizontal_speed: float,
    width_jitter: int,
    spawn_offset: int,
) -> None:
    """
    런(게임)을 완전히 리셋하고 즉시 첫 current 블록까지 생성한다.
    """
    spawn_first_block(state, screen_w, floor_y, block_h, edge_padding)
    spawn_next_block(
        state,
        screen_w,
        int(hover_y),
        block_h,
        edge_padding,
        horizontal_speed,
        width_jitter,
        spawn_offset,
    )

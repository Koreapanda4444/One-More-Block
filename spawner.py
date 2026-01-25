from __future__ import annotations

"""
spawner.py

Commit 9:
- 런 요약 통계(run_*) 초기화 항목 추가
"""

import random
from models import Block, GameState
from mechanics import get_top_block
from utils import pastel_color


def spawn_first_block(state: GameState, screen_w: int, floor_y: float, block_h: int, edge_padding: int) -> None:
    w = min(280, screen_w - edge_padding * 2)
    w = max(60, w)

    x = (screen_w - w) / 2
    y = floor_y - block_h

    base = Block(x=float(x), y=float(y), w=float(w), h=float(block_h), color=pastel_color(), phase="settled")

    state.stack = [base]
    state.shards = []
    state.current = None

    state.score = 0
    state.game_over = False
    state.fail_reason = ""

    state.perfect_combo = 0
    state.width_bonus = 0
    state.flash_text = ""
    state.flash_timer = 0.0

    state.land_timer = 0.0
    state.land_total = 0.0
    state.last_settled = None

    state.shake_timer = 0.0
    state.shake_total = 0.0
    state.shake_amp = 0.0

    # ===== 런 통계 초기화 =====
    state.run_time = 0.0
    state.run_perfects = 0
    state.run_shards_created = 0
    state.run_max_combo = 0
    state.run_min_width = float(w)
    state.run_narrow_streak = 0

    state.run_landings = 0
    state.run_overlap_sum = 0.0
    state.run_last_overlap_ratio = 0.0


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
    top = get_top_block(state)
    if top is None:
        return

    width_jitter = max(0, int(width_jitter))
    spawn_offset = max(0, int(spawn_offset))

    w = max(60, min(int(top.w), 360))
    if width_jitter:
        w = max(60, w + random.randint(-width_jitter, width_jitter))

    if state.width_bonus:
        w = min(420, w + int(state.width_bonus))
        state.width_bonus = 0

    center_x = top.x + top.w / 2

    min_x = edge_padding
    max_x = max(edge_padding, screen_w - edge_padding - w)

    max_offset = min(spawn_offset, int((max_x - min_x) / 2))
    offset = random.randint(-max_offset, max_offset) if max_offset > 0 else 0

    target_x = (center_x - w / 2) + offset
    x = float(max(min_x, min(target_x, max_x)))

    direction = random.choice([-1, 1])
    vx = float(direction) * float(horizontal_speed)

    state.current = Block(
        x=x, y=float(hover_y), w=float(w), h=float(block_h),
        color=pastel_color(), phase="move", vx=vx
    )


def reset_run(
    state: GameState,
    screen_w: int,
    floor_y: float,
    hover_y: int,
    block_h: int,
    edge_padding: int,
    horizontal_speed: float,
    width_jitter: int,
    spawn_offset: int,
) -> None:
    spawn_first_block(state, screen_w, floor_y, block_h, edge_padding)
    spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed, width_jitter, spawn_offset)

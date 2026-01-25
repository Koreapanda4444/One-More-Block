"""spawner.py

블록 생성(스폰) 관련.
"""

from __future__ import annotations

import random

from mechanics import get_top_block
from models import Block, GameState
from utils import pastel_color


def spawn_first_block(
    state: GameState,
    screen_w: int,
    floor_y: float,
    block_h: int,
    edge_padding: int,
) -> None:
    """런 시작 시 바닥에 기본 블록 1개를 생성."""
    w = min(280, screen_w - edge_padding * 2)
    x = (screen_w - w) / 2
    y = floor_y - block_h

    base = Block(x=x, y=y, w=w, h=block_h, color=pastel_color(), phase="settled")

    state.stack.clear()
    state.stack.append(base)

    state.score = 0
    state.current = None
    state.game_over = False

    state.perfect_combo = 0
    state.width_bonus = 0
    state.flash_text = ""
    state.flash_timer = 0.0
    state.shards.clear()


def spawn_next_block(
    state: GameState,
    screen_w: int,
    hover_y: int,
    block_h: int,
    edge_padding: int,
    horizontal_speed: float,
) -> None:
    """다음 블록 생성."""
    top = get_top_block(state)
    if top is None:
        return

    w = max(60, min(top.w, 360))
    w = max(60, w + random.randint(-18, 18))

    if state.width_bonus:
        w = min(420, w + state.width_bonus)
        state.width_bonus = 0

    center_x = top.x + top.w / 2

    max_offset = (screen_w - edge_padding * 2 - w) / 2
    max_offset = max(0, min(120, int(max_offset)))

    offset = random.randint(-max_offset, max_offset) if max_offset > 0 else 0
    x = center_x + offset - w / 2
    x = max(edge_padding, min(x, screen_w - edge_padding - w))

    vx = random.choice([-1, 1]) * horizontal_speed

    state.current = Block(
        x=float(x),
        y=float(hover_y),
        w=float(w),
        h=float(block_h),
        color=pastel_color(),
        phase="move",
        vx=float(vx),
    )


def reset_run(
    state: GameState,
    screen_w: int,
    floor_y: float,
    hover_y: int,
    block_h: int,
    edge_padding: int,
    horizontal_speed: float,
) -> None:
    """런을 완전히 초기화."""
    spawn_first_block(state, screen_w, floor_y, block_h, edge_padding)
    spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed)

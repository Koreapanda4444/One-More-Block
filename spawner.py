from __future__ import annotations

import random
from typing import Optional

from models import Block, GameState
from utils import pastel_color

def spawn_first_block(state: GameState, screen_w: int, floor_y: float, block_h: int, edge_padding: int) -> None:
    w = min(280, screen_w - edge_padding * 2)
    x = (screen_w - w) / 2
    y = floor_y - block_h
    base = Block(x=x, y=y, w=w, h=block_h, color=pastel_color(), phase="settled")
    state.stack = [base]
    state.score = 0
    state.current = None

def spawn_next_block(
    state: GameState,
    screen_w: int,
    hover_y: int,
    block_h: int,
    edge_padding: int,
    horizontal_speed: float,
) -> None:
    top = state.stack[0] if state.stack else None
    from mechanics import get_top_block
    top_block = get_top_block(state)
    if top_block is None:
        return

    w = max(60, min(top_block.w, 360))
    w = max(60, w + random.randint(-18, 18))

    # 기존 블록 x 좌표 근처에서만 랜덤하게 생성
    center_x = top_block.x + top_block.w / 2
    max_offset = min(120, (screen_w - edge_padding - w) // 2)  # 기존 블록 기준 최대 120px 이내
    offset = random.randint(-max_offset, max_offset)
    x = int(max(edge_padding, min(center_x + offset - w / 2, screen_w - edge_padding - w)))
    y = hover_y

    direction = random.choice([-1, 1])
    vx = direction * horizontal_speed

    state.current = Block(
        x=x, y=y, w=w, h=block_h,
        color=pastel_color(),
        phase="move",
        vx=vx,
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
    state.game_over = False
    spawn_first_block(state, screen_w, floor_y, block_h, edge_padding)
    spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed)

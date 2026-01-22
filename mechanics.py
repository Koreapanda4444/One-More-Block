from __future__ import annotations

from typing import Optional, Tuple

from models import Block, GameState

def top_surface_y(state: GameState, floor_y: float) -> float:
    if not state.stack:
        return float(floor_y)
    return float(min(b.y for b in state.stack))

def get_top_block(state: GameState) -> Optional[Block]:
    if not state.stack:
        return None
    top_y = min(b.y for b in state.stack)
    for b in state.stack:
        if abs(b.y - top_y) < 0.001:
            return b
    return None

def compute_overlap(a: Block, b: Block) -> Tuple[float, float, float]:
    a_left, a_right = a.x, a.x + a.w
    b_left, b_right = b.x, b.x + b.w

    left = max(a_left, b_left)
    right = min(a_right, b_right)
    overlap_w = max(0.0, right - left)
    ratio = overlap_w / max(a.w, 1.0)
    return overlap_w, left, ratio

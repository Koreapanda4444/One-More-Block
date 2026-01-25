"""mechanics.py

충돌/겹침/높이 같은 '순수 수학' 계산만 모아둔 파일.

여기는 pygame과 분리해두면,
- 테스트하기 쉽고
- 버그 원인도 빠르게 찾을 수 있다.
"""

from __future__ import annotations

from typing import Optional, Tuple

from models import Block, GameState


def top_surface_y(state: GameState, floor_y: float) -> float:
    """현재 스택의 맨 위 표면(y) 반환."""
    if not state.stack:
        return float(floor_y)
    return float(min(b.y for b in state.stack))


def get_top_block(state: GameState) -> Optional[Block]:
    """가장 위에 있는 블록을 1개 반환."""
    if not state.stack:
        return None
    top_y = min(b.y for b in state.stack)
    for b in state.stack:
        if abs(b.y - top_y) < 0.001:
            return b
    return None


def compute_overlap(a: Block, b: Block) -> Tuple[float, float, float]:
    """a(현재 블록)과 b(스택 최상단)의 x방향 겹침 계산."""
    a_left, a_right = a.x, a.x + a.w
    b_left, b_right = b.x, b.x + b.w

    left = max(a_left, b_left)
    right = min(a_right, b_right)
    overlap_w = max(0.0, right - left)

    ratio = overlap_w / max(a.w, 1.0)
    return overlap_w, left, ratio

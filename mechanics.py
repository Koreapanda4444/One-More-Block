from __future__ import annotations

"""
mechanics.py

"판정"과 관련된 순수 함수 모음.
- update.py가 너무 비대해지지 않게,
  겹침 계산 / 탑 블록 찾기 같은 기능은 여기서 담당한다.
"""

from typing import Optional, Tuple
from models import Block, GameState


def top_surface_y(state: GameState, floor_y: float) -> float:
    """
    현재 스택의 가장 위 표면 y를 반환한다.
    - 스택이 비었으면 floor_y를 표면이라고 가정(안전용)
    """
    if not state.stack:
        return float(floor_y)
    # y는 위로 갈수록 작아지는 좌표계이므로 min(y)가 가장 위
    return float(min(b.y for b in state.stack))


def get_top_block(state: GameState) -> Optional[Block]:
    """
    스택 중 "가장 위에 있는 블록"을 반환한다.
    (여러 개가 같은 높이일 가능성은 낮지만, 안전하게 첫 번째를 반환)
    """
    if not state.stack:
        return None

    top_y = min(b.y for b in state.stack)
    for b in state.stack:
        if abs(b.y - top_y) < 0.001:
            return b
    return None


def compute_overlap(a: Block, b: Block) -> Tuple[float, float, float]:
    """
    블록 a가 블록 b 위에 착지할 때 겹침(오버랩)을 계산한다.

    반환값:
    - overlap_w: 겹친 폭(0이면 겹침 없음)
    - left: 겹친 구간의 왼쪽 x
    - ratio: a의 폭 대비 겹침 비율 (overlap_w / a.w)

    ratio는:
    - MIN_OVERLAP_RATIO보다 작으면 게임오버
    - PERFECT_RATIO보다 크면 PERFECT
    """
    a_left, a_right = a.x, a.x + a.w
    b_left, b_right = b.x, b.x + b.w

    left = max(a_left, b_left)
    right = min(a_right, b_right)

    overlap_w = max(0.0, right - left)
    ratio = overlap_w / max(a.w, 1.0)
    return overlap_w, left, ratio

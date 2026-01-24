from __future__ import annotations

"""
models.py

게임 데이터 구조 정의.
"""

from dataclasses import dataclass, field
from collections import deque
from typing import Deque, List, Optional, Set, Tuple


Color = Tuple[int, int, int]


@dataclass
class BlockShard:
    """트림으로 잘려나간 조각(연출용)."""
    x: float
    y: float
    w: float
    h: float
    color: Color
    vy: float


@dataclass
class Block:
    """
    phase:
      - "move": 좌우 왕복
      - "drop": 낙하
      - "settled": 스택에 포함
    """
    x: float
    y: float
    w: float
    h: float
    color: Color
    phase: str = "move"
    vx: float = 0.0


@dataclass
class GameState:
    running: bool = True
    game_over: bool = False

    score: int = 0
    best: int = 0

    current: Optional[Block] = None
    stack: List[Block] = field(default_factory=list)
    shards: List[BlockShard] = field(default_factory=list)

    # PERFECT / COMBO
    perfect_combo: int = 0
    width_bonus: int = 0
    flash_text: str = ""
    flash_timer: float = 0.0

    # 착지/흔들림 FX
    land_timer: float = 0.0
    land_total: float = 0.0
    last_settled: Optional[Block] = None

    shake_timer: float = 0.0
    shake_total: float = 0.0
    shake_amp: float = 0.0

    # 업적
    unlocked_achievements: Set[str] = field(default_factory=set)
    show_achievements: bool = False

    toast_queue: Deque[str] = field(default_factory=deque)
    toast_text: str = ""
    toast_timer: float = 0.0
    toast_total: float = 0.0

    # 런 통계(업적 진행도용)
    run_perfects: int = 0
    run_shards_created: int = 0
    run_max_combo: int = 0
    run_min_width: float = 999999.0
    run_narrow_streak: int = 0

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple


Color = Tuple[int, int, int]

@dataclass
class BlockShard:
    x: float
    y: float
    w: float
    h: float
    color: Color
    vy: float  # 생성 시 반드시 값 할당

@dataclass
class Block:
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
    stack: List[Block] = None
    shards: list = None

    def __post_init__(self) -> None:
        if self.stack is None:
            self.stack = []
        if self.shards is None:
            self.shards = []

    # PERFECT / COMBO
    perfect_combo: int = 0
    width_bonus: int = 0   # 다음 블록 폭 보너스(1회성)

    # 화면 플래시 텍스트
    flash_text: str = ""
    flash_timer: float = 0.0

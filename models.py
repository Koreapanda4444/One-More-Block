from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

Color = Tuple[int, int, int]

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

    def __post_init__(self) -> None:
        if self.stack is None:
            self.stack = []

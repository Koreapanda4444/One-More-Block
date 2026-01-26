from __future__ import annotations

"""models.py

상태/데이터만 관리.
(2) 파티클/쉐이크
(1) 테마/해금
(3) 런 기록/누적 perfect
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

Color = Tuple[int, int, int]


@dataclass
class BlockShard:
    x: float
    y: float
    w: float
    h: float
    color: Color
    vy: float = 0.0


@dataclass
class Block:
    x: float
    y: float
    w: float
    h: float
    color: Color
    phase: str = "move"  # move | drop | settled
    vx: float = 0.0

    _orig_x: float = 0.0
    _orig_w: float = 0.0


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    size: int
    color: Color
    life: float
    age: float = 0.0


@dataclass
class GameState:
    running: bool = True

    current: Optional[Block] = None
    stack: List[Block] = field(default_factory=list)
    shards: List[BlockShard] = field(default_factory=list)

    score: int = 0
    best: int = 0
    game_over: bool = False
    game_over_recorded: bool = False

    perfect_combo: int = 0
    width_bonus: int = 0

    # 런 통계(3번)
    run_total_perfect: int = 0
    run_max_combo: int = 0

    flash_text: str = ""
    flash_timer: float = 0.0

    # 오디오
    bgm_on: bool = True
    bgm_volume: float = 0.25

    # (2) 손맛 효과
    particles: List[Particle] = field(default_factory=list)
    shake_timer: float = 0.0
    shake_duration: float = 0.12
    shake_strength: float = 10.0

    # (1) 테마/해금
    selected_theme: str = "sky"
    unlocked_themes: List[str] = field(default_factory=lambda: ["sky"])

    # (3) 누적/런 기록
    lifetime_perfect: int = 0
    runs: List[Dict[str, Any]] = field(default_factory=list)

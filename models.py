from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Deque, List, Optional, Set, Tuple


Color = Tuple[int, int, int]


@dataclass
class BlockShard:
    x: float
    y: float
    w: float
    h: float
    color: Color
    vy: float


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

    # 런 통계(Commit 9)
    run_time: float = 0.0
    run_perfects: int = 0
    run_shards_created: int = 0
    run_max_combo: int = 0
    run_min_width: float = 999999.0
    run_narrow_streak: int = 0
    run_landings: int = 0
    run_overlap_sum: float = 0.0
    run_last_overlap_ratio: float = 0.0
    fail_reason: str = ""

    # =========================
    # SFX / Audio (Commit 10)
    # =========================
    audio_volume: float = 0.70   # 0.0~1.0
    audio_muted: bool = False

    # update/input → 여기로 이벤트 쌓고 main에서 재생
    sfx_queue: Deque[str] = field(default_factory=deque)

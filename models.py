"""models.py

데이터(상태)만 담는 파일.

원칙
- 여기에는 '로직'을 넣지 않는다. (업데이트/스폰/렌더는 다른 파일)
- dataclass로 가볍게 상태를 들고 다닌다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


Color = Tuple[int, int, int]


@dataclass
class BlockShard:
    """블록이 잘렸을 때 떨어지는 조각."""
    x: float
    y: float
    w: float
    h: float
    color: Color
    vy: float = 0.0


@dataclass
class Block:
    """게임에 등장하는 단일 블록."""
    x: float
    y: float
    w: float
    h: float
    color: Color
    phase: str = "move"  # "move" | "drop" | "settled"
    vx: float = 0.0

    # drop 시작 시점의 원본 좌표/폭(트림 계산용)
    _orig_x: float = 0.0
    _orig_w: float = 0.0


@dataclass
class GameState:
    """런타임 게임 상태."""
    running: bool = True

    # 핵심 상태
    current: Optional[Block] = None
    stack: List[Block] = field(default_factory=list)
    shards: List[BlockShard] = field(default_factory=list)

    # 점수/기록
    score: int = 0
    best: int = 0
    game_over: bool = False

    # PERFECT/보너스
    perfect_combo: int = 0
    width_bonus: int = 0

    # UI 플래시 메시지(중앙 표시)
    flash_text: str = ""
    flash_timer: float = 0.0

    # 오디오 설정
    bgm_on: bool = True
    bgm_volume: float = 0.25

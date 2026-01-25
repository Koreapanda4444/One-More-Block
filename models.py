from __future__ import annotations

"""
models.py

게임 데이터 구조 정의.
Commit 9:
- 런 요약 통계를 위해 run_* 필드 확장
- fail_reason / overlap 평균 계산용 필드 추가
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

    # =========================
    # 런 통계 (업적 + 게임오버 요약에 사용)
    # =========================
    run_time: float = 0.0                 # 런 플레이 시간(초)
    run_perfects: int = 0                 # PERFECT 누적
    run_shards_created: int = 0           # 생성된 shard 개수
    run_max_combo: int = 0                # 런 최대 콤보
    run_min_width: float = 999999.0       # 런 최소 폭
    run_narrow_streak: int = 0            # 폭<=80 연속 성공 수(업적용)

    # 겹침(오버랩) 평균 계산용
    run_landings: int = 0                 # 성공 착지 횟수
    run_overlap_sum: float = 0.0          # 성공 착지들의 ratio 합
    run_last_overlap_ratio: float = 0.0   # 마지막 판정 ratio(죽을 때/마지막 착지 때)

    # 실패 사유(게임오버 요약용)
    fail_reason: str = ""                 # 예: "겹침 부족", "완전 빗나감"

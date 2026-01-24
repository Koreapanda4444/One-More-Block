from __future__ import annotations

"""
models.py

게임에서 쓰는 "데이터 구조"만 모아둔 파일.
- 로직(update)과 렌더(render)가 같은 데이터를 공유하므로
  dataclass로 형태를 고정해 두면 실수가 확 줄어든다.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

# pygame.Color 대신 튜플로 단순화
Color = Tuple[int, int, int]


@dataclass
class BlockShard:
    """
    트림으로 잘려나간 조각(연출용).
    - 물리 엔진을 쓰지 않고, 단순 중력/속도만 적용한다.
    """
    x: float
    y: float
    w: float
    h: float
    color: Color
    vy: float  # 생성 시 반드시 값 할당(초기 속도)


@dataclass
class Block:
    """
    실제 게임 플레이의 핵심 오브젝트(블록).
    phase:
      - "move": 좌우 왕복 중 (drop 입력 대기)
      - "drop": 아래로 떨어지는 중
      - "settled": 착지 완료(스택에 들어감)
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
    """
    게임 전체 상태(싱글턴처럼 main에서 1개만 만든다).
    - update / render / input이 이 state를 같이 만지며 게임이 진행됨.
    """

    # ===== 착지 FX(스쿼시) =====
    land_timer: float = 0.0
    land_total: float = 0.0
    last_settled: Optional[Block] = None  # 스쿼시 적용 대상(최근 착지 블록)

    # ===== 화면 흔들림 FX =====
    shake_timer: float = 0.0
    shake_total: float = 0.0
    shake_amp: float = 0.0

    # ===== 실행 상태 =====
    running: bool = True
    game_over: bool = False

    # ===== 점수 =====
    score: int = 0
    best: int = 0

    # ===== 현재 블록 / 스택 / 조각 =====
    current: Optional[Block] = None
    stack: List[Block] = None
    shards: list = None

    def __post_init__(self) -> None:
        """
        dataclass에서 mutable 기본값([])을 직접 넣으면 공유 버그가 생기므로,
        None으로 두고 여기서 새 리스트를 만든다.
        """
        if self.stack is None:
            self.stack = []
        if self.shards is None:
            self.shards = []

    # ===== PERFECT / COMBO =====
    perfect_combo: int = 0
    width_bonus: int = 0   # 다음 블록 폭 보너스(1회성)

    # ===== 화면 플래시 텍스트 =====
    flash_text: str = ""
    flash_timer: float = 0.0

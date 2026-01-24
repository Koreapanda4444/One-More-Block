from __future__ import annotations

"""
difficulty.py

점수(HEIGHT)에 따라 난이도 파라미터를 계산한다.

왜 이렇게?
- 초반은 안정적으로, 후반은 손이 바쁘게 만들기 위함.
- 무한히 빨라지면 불합리해지므로 상한(cap)을 둔다.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Difficulty:
    """
    update/spawn에서 사용할 난이도 값 묶음.
    frozen=True: 계산 결과를 실수로 변경하지 못하게 고정
    """
    level: int
    horizontal_speed: float
    fall_speed: float
    width_jitter: int
    spawn_offset: int


def compute_difficulty(
    score: int,
    base_hs: float,
    base_fs: float,
    base_jitter: int,
    base_offset: int,
    step_score: int,
    hs_step: float,
    hs_max_mul: float,
    fs_step: float,
    fs_max_mul: float,
    jitter_step: int,
    jitter_max: int,
    offset_step: int,
    offset_max: int,
) -> Difficulty:
    """
    score를 기반으로 난이도 레벨을 계산하고,
    레벨에 따라 각 파라미터를 증가시키되 최대치를 넘지 않게 제한한다.

    레벨:
      level = score // step_score

    속도:
      base * (1 + level * step), 단 최대 배율(hs_max_mul/fs_max_mul)

    랜덤:
      base + level * step, 단 최대값(jitter_max/offset_max)
    """
    score = max(0, int(score))
    step_score = max(1, int(step_score))

    level = score // step_score

    hs_mul = min(float(hs_max_mul), 1.0 + level * float(hs_step))
    fs_mul = min(float(fs_max_mul), 1.0 + level * float(fs_step))

    width_jitter = min(int(jitter_max), int(base_jitter) + level * int(jitter_step))
    spawn_offset = min(int(offset_max), int(base_offset) + level * int(offset_step))

    return Difficulty(
        level=level,
        horizontal_speed=base_hs * hs_mul,
        fall_speed=base_fs * fs_mul,
        width_jitter=width_jitter,
        spawn_offset=spawn_offset,
    )

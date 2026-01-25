"""difficulty.py

난이도(스케일링) 계산.

현재 버전에서는 아직 main에 연결하지 않은 상태다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Difficulty:
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
    """점수에 따라 Difficulty를 계산해서 반환한다."""
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

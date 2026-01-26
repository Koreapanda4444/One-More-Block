from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Difficulty:
    level: int
    horizontal_speed: float
    fall_speed: float

"""utils.py"""

from __future__ import annotations
import random
from typing import Tuple


def pastel_color() -> Tuple[int, int, int]:
    # 블록은 밝게 유지(배경만 딤 처리)
    base = 190
    return (
        base + random.randint(0, 50),
        base + random.randint(0, 50),
        base + random.randint(0, 50),
    )

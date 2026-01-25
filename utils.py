"""utils.py

작은 유틸 함수 모음.
"""

from __future__ import annotations

import random
from typing import Tuple


def pastel_color() -> Tuple[int, int, int]:
    """밝은 파스텔 톤 랜덤 색상을 만든다."""
    base = 190
    return (
        base + random.randint(0, 50),
        base + random.randint(0, 50),
        base + random.randint(0, 50),
    )

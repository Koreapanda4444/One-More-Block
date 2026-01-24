from __future__ import annotations

"""
잡다한 유틸 함수 모음.

현재는 "파스텔 컬러"만 제공하지만,
나중에 clamp(), lerp(), 텍스트 줄바꿈 등도 여기로 모으면
다른 파일이 깔끔해진다.
"""

import random
from typing import Tuple


def pastel_color() -> Tuple[int, int, int]:
    """
    랜덤 파스텔 색상을 만든다.

    왜 이렇게?
    - 너무 진한 색은 눈이 피곤하고, 밝은 톤 UI와도 어울리지 않는다.
    - base(기본 밝기)를 높게 잡고, 거기에 작은 랜덤 값을 더해 "부드러운 색"을 만든다.

    반환:
    - (R, G, B) 튜플, 각 값은 0~255 범위
    """
    base = 190
    return (
        base + random.randint(0, 50),
        base + random.randint(0, 50),
        base + random.randint(0, 50),
    )

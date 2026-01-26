from __future__ import annotations

"""themes.py

테마/스킨 정의.
눈부심 개선:
- sky/paper는 채도를 낮춘 색 + background-only 딤 오버레이 적용
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

Color = Tuple[int, int, int]


@dataclass(frozen=True)
class Theme:
    key: str
    display: str
    bg: Color
    floor: Color
    text: Color

    # 블록 스타일
    block_outline: bool = False
    outline_color: Color = (0, 0, 0)
    outline_width: int = 3

    # 배경/바닥만 살짝 어둡게(눈부심 감소)
    bg_dim_alpha: int = 0              # 0~255
    bg_dim_color: Color = (0, 0, 0)    # 검정 딤(가장 무난)


THEME_ORDER: List[str] = ["sky", "neon", "paper"]

THEMES: Dict[str, Theme] = {
    "sky": Theme(
        key="sky",
        display="Sky",
        # 🔻 기존보다 훨씬 '차분한' 하늘색 (눈부심 감소)
        bg=(205, 214, 228),
        floor=(168, 182, 202),
        text=(28, 35, 48),
        block_outline=False,
        # 배경/바닥만 살짝 딤
        bg_dim_alpha=28,
        bg_dim_color=(0, 0, 0),
    ),
    "neon": Theme(
        key="neon",
        display="Neon",
        bg=(10, 12, 18),
        floor=(20, 24, 36),
        text=(220, 235, 255),
        block_outline=True,
        outline_color=(80, 250, 210),
        outline_width=3,
        bg_dim_alpha=0,
    ),
    "paper": Theme(
        key="paper",
        display="Paper",
        # 🔻 종이 느낌 + 눈부심 덜한 톤
        bg=(232, 228, 220),
        floor=(216, 208, 196),
        text=(45, 42, 38),
        block_outline=True,
        outline_color=(120, 112, 102),
        outline_width=2,
        bg_dim_alpha=18,
        bg_dim_color=(0, 0, 0),
    ),
}


def get_theme(key: str) -> Theme:
    return THEMES.get(key, THEMES["sky"])


def next_theme_key(cur: str, direction: int) -> str:
    if cur not in THEME_ORDER:
        cur = "sky"
    i = THEME_ORDER.index(cur)
    ni = (i + direction) % len(THEME_ORDER)
    return THEME_ORDER[ni]

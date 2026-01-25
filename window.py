"""window.py

창 생성/모드 전환 로직.

요구사항
- '풀스크린(FULLSCREEN)'은 쓰지 않는다.
- 대신 '창모드 전체크기'(windowed_max)와 작은 창(windowed)을 토글한다.
- 선택적으로 borderless(프레임 없는 전체 화면 크기)도 지원.
"""

from __future__ import annotations

from typing import Tuple

import pygame


def get_desktop_size() -> Tuple[int, int]:
    """현재 모니터의 데스크톱 해상도 반환."""
    info = pygame.display.Info()
    return int(info.current_w), int(info.current_h)


def create_screen(window_mode: str, window_size: Tuple[int, int]) -> pygame.Surface:
    """window_mode에 따라 pygame 디스플레이를 생성한다.

    - windowed: 지정된 window_size
    - windowed_max: 데스크톱 해상도 크기(창 프레임 있음)
    - borderless: 데스크톱 해상도 크기(프레임 없음)

    주의:
    - FULLSCREEN 플래그는 사용하지 않는다.
    """
    dw, dh = get_desktop_size()

    if window_mode == "windowed_max":
        # 창 프레임이 있는 상태로 '큰 창'을 띄운다.
        # (OS에 따라 거의 전체를 덮지만, FULLSCREEN은 아님)
        return pygame.display.set_mode((dw, dh))

    if window_mode == "borderless":
        # 프레임 없는 전체 화면 크기(그래도 FULLSCREEN은 아님)
        return pygame.display.set_mode((dw, dh), pygame.NOFRAME)

    # 기본: 작은 창
    return pygame.display.set_mode(window_size)

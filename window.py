from __future__ import annotations

"""
윈도우/화면 생성 관련 모듈.

요구사항:
- "풀스크린"은 싫고,
- "창 모드지만 화면 전체처럼 보이게" (테두리 없는 최대화) 를 지원해야 함.

pygame에서 이것을 구현할 때 보통:
- pygame.NOFRAME + 디스플레이 해상도로 set_mode
를 사용한다.

주의:
- pygame.display.Info()는 display 초기화 이후에 정상값이 나오는 경우가 많다.
  (main.py에서 pygame.init() 이후 사용 권장)
"""

from typing import Tuple
import pygame


def get_desktop_size() -> Tuple[int, int]:
    """
    현재 모니터(데스크톱) 해상도를 가져온다.
    테두리 없는 최대화(NOFRAME)에 사용할 크기.
    """
    info = pygame.display.Info()
    return int(info.current_w), int(info.current_h)


def create_screen(borderless_max: bool, window_size: Tuple[int, int]) -> pygame.Surface:
    """
    화면 Surface 생성.

    - borderless_max=True:
        테두리 없는 최대화(풀스크린이 아님)
        → 알트탭, 작업표시줄 등 OS 사용성이 풀스크린보다 편함
    - borderless_max=False:
        일반 창 모드(window_size 크기)

    반환:
    - pygame Surface (렌더링 대상)
    """
    if borderless_max:
        dw, dh = get_desktop_size()
        return pygame.display.set_mode((dw, dh), pygame.NOFRAME)

    return pygame.display.set_mode(window_size)

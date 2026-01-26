"""window.py

풀스크린(FULLSCREEN) 없이 창 모드만으로 크기 토글
"""

from __future__ import annotations
from typing import Tuple
import pygame


def get_desktop_size() -> Tuple[int, int]:
    info = pygame.display.Info()
    return int(info.current_w), int(info.current_h)


def create_screen(window_mode: str, window_size: Tuple[int, int]) -> pygame.Surface:
    dw, dh = get_desktop_size()

    if window_mode == "windowed_max":
        return pygame.display.set_mode((dw, dh))
    if window_mode == "borderless":
        return pygame.display.set_mode((dw, dh), pygame.NOFRAME)

    return pygame.display.set_mode(window_size)

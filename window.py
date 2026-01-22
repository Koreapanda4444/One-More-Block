from __future__ import annotations

from typing import Tuple
import pygame

def get_desktop_size() -> Tuple[int, int]:
    info = pygame.display.Info()
    return int(info.current_w), int(info.current_h)

def create_screen(borderless_max: bool, window_size: Tuple[int, int]) -> pygame.Surface:
    if borderless_max:
        dw, dh = get_desktop_size()
        return pygame.display.set_mode((dw, dh), pygame.NOFRAME)
    return pygame.display.set_mode(window_size)

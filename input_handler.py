from __future__ import annotations

"""input_handler.py

- 드랍: 클릭/스페이스
- 게임오버: 스페이스/엔터로 재시작
- 게임오버: 좌/우로 테마 변경 시도
"""

from typing import Optional
import pygame
from models import GameState


def _begin_drop(state: GameState) -> None:
    if not state.current:
        return
    if state.current.phase != "move":
        return
    state.current._orig_x = state.current.x
    state.current._orig_w = state.current.w
    state.current.phase = "drop"


def handle_events(state: GameState, key_toggle_window_mode: int, key_drop: int, key_quit: int) -> Optional[str]:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == key_quit:
                state.running = False
                return None

            if event.key == key_toggle_window_mode:
                return "toggle_window_mode"

            if event.key == pygame.K_b:
                return "bgm_toggle"
            if event.key in (pygame.K_LEFTBRACKET, pygame.K_MINUS):
                return "bgm_down"
            if event.key in (pygame.K_RIGHTBRACKET, pygame.K_EQUALS):
                return "bgm_up"

            if state.game_over and event.key == pygame.K_LEFT:
                return "theme_prev"
            if state.game_over and event.key == pygame.K_RIGHT:
                return "theme_next"

            if state.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                return "restart"

            if (not state.game_over) and event.key == key_drop:
                _begin_drop(state)
                return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if state.game_over:
                    return "restart"
                _begin_drop(state)
                return None

    return None

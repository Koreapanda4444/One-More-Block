"""input_handler.py

입력(키/마우스) 처리.
"""

from __future__ import annotations

from typing import Optional

import pygame

from models import GameState


def _begin_drop(state: GameState) -> None:
    """현재 블록을 drop 상태로 전환(원본 좌표/폭 저장)."""
    if not state.current:
        return
    if state.current.phase != "move":
        return
    state.current._orig_x = state.current.x
    state.current._orig_w = state.current.w
    state.current.phase = "drop"


def handle_events(
    state: GameState,
    key_toggle_window_mode: int,
    key_drop: int,
    key_quit: int,
) -> Optional[str]:
    """pygame 이벤트를 읽고 명령 문자열을 반환."""
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

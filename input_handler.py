from __future__ import annotations

from typing import Optional
import pygame
from models import GameState


def _clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def handle_events(
    state: GameState,
    key_toggle_window_mode: int,
    key_drop: int,
    key_quit: int,
) -> Optional[str]:
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

            # 업적 패널 토글
            if event.key == pygame.K_a:
                state.show_achievements = not state.show_achievements
                return None

            # 뮤트 토글
            if event.key == pygame.K_m:
                state.audio_muted = not state.audio_muted
                pct = int(state.audio_volume * 100)
                state.toast_queue.append(f"VOLUME: {'MUTED' if state.audio_muted else str(pct)+'%'}")
                return None

            # 볼륨 다운: [ 또는 -
            if event.key in (pygame.K_LEFTBRACKET, pygame.K_MINUS):
                state.audio_volume = _clamp01(state.audio_volume - 0.05)
                state.audio_muted = False  # 볼륨 조절하면 자동 언뮤트
                state.toast_queue.append(f"VOLUME: {int(state.audio_volume * 100)}%")
                return None

            # 볼륨 업: ] 또는 =
            if event.key in (pygame.K_RIGHTBRACKET, pygame.K_EQUALS):
                state.audio_volume = _clamp01(state.audio_volume + 0.05)
                state.audio_muted = False
                state.toast_queue.append(f"VOLUME: {int(state.audio_volume * 100)}%")
                return None

            # 게임오버 상태에서 재시작
            if state.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                return "restart"

            # 업적 패널 열렸으면 drop 막기
            if state.show_achievements:
                return None

            # drop
            if (not state.game_over) and event.key == key_drop:
                if state.current and state.current.phase == "move":
                    state.current._orig_x = state.current.x
                    state.current._orig_w = state.current.w
                    state.current.phase = "drop"
                    state.sfx_queue.append("drop")
                return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state.game_over:
                return "restart"

            if state.show_achievements:
                return None

            if state.current and state.current.phase == "move":
                state.current._orig_x = state.current.x
                state.current._orig_w = state.current.w
                state.current.phase = "drop"
                state.sfx_queue.append("drop")
            return None

    return None

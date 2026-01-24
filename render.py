from __future__ import annotations

import random
from typing import Tuple

import pygame

from models import GameState


def draw_game(
    screen: pygame.Surface,
    font_main: pygame.font.Font,
    font_hint: pygame.font.Font,
    font_flash: pygame.font.Font,
    state: GameState,
    cam_y: float,
    screen_size: Tuple[int, int],
    floor_y: float,
    colors: dict,
    land_squash_px: float,
) -> None:
    """
    렌더링 전용 함수.

    좌표 개념:
    - 모든 블록/조각은 '월드 좌표'로 관리된다.
    - 화면에 그릴 때만 (y - cam_y)로 카메라 보정을 한다.
    - 화면 흔들림(shake)은 렌더 좌표에 (shake_x, shake_y)로 추가한다.
    """
    W, H = screen_size
    screen.fill(colors["bg"])

    # =========================
    # 1) 화면 흔들림(Shake) 오프셋 계산
    # =========================
    shake_x = 0
    shake_y = 0
    if state.shake_timer > 0.0 and state.shake_total > 0.0:
        # t: 1 → 0으로 줄어드는 비율 (시간이 지날수록 흔들림이 줄어듦)
        t = state.shake_timer / state.shake_total
        amp = state.shake_amp * t
        shake_x = int(random.uniform(-amp, amp))
        shake_y = int(random.uniform(-amp, amp))

    # =========================
    # 2) 바닥 렌더링
    # =========================
    floor_screen_y = int(floor_y - cam_y + shake_y)
    pygame.draw.rect(
        screen,
        colors["floor"],
        pygame.Rect(0 + shake_x, floor_screen_y, W, H - floor_screen_y),
    )

    # =========================
    # 3) 잘린 조각(shard) 렌더링
    # =========================
    for s in state.shards:
        x = s.x + shake_x
        y = (s.y - cam_y) + shake_y
        r = pygame.Rect(int(x), int(y), int(s.w), int(s.h))
        pygame.draw.rect(screen, s.color, r, border_radius=6)

    # =========================
    # 4) 스택 블록 렌더링 (+ 착지 스쿼시)
    # =========================
    for b in state.stack:
        x = b.x + shake_x
        y = (b.y - cam_y) + shake_y
        w = b.w
        h = b.h

        # 마지막으로 착지한 블록만 0.1초 정도 살짝 눌리는 연출
        if state.last_settled is b and state.land_timer > 0.0 and state.land_total > 0.0:
            t = state.land_timer / state.land_total   # 1 → 0
            squash = int(land_squash_px * t)
            h = max(1, h - squash)
            y += squash  # 아래쪽으로 눌린 느낌

        r = pygame.Rect(int(x), int(y), int(w), int(h))
        pygame.draw.rect(screen, b.color, r, border_radius=10)

    # =========================
    # 5) 현재 블록(current) 렌더링
    # =========================
    if state.current:
        c = state.current
        x = c.x + shake_x
        y = (c.y - cam_y) + shake_y
        r = pygame.Rect(int(x), int(y), int(c.w), int(c.h))
        pygame.draw.rect(screen, c.color, r, border_radius=10)

    # =========================
    # 6) UI 텍스트 렌더링
    # =========================
    ui = f"HEIGHT: {state.score}     BEST: {state.best}"
    screen.blit(font_main.render(ui, True, colors["text"]), (18, 16))

    hint = "CLICK / SPACE to DROP   |   F11: window mode"
    screen.blit(font_hint.render(hint, True, colors["text"]), (18, 46))

    # PERFECT/콤보 플래시
    if state.flash_timer > 0.0 and state.flash_text:
        flash = font_flash.render(state.flash_text, True, colors["text"])
        screen.blit(flash, (W // 2 - flash.get_width() // 2, 86))

    # =========================
    # 7) 게임오버 오버레이
    # =========================
    if state.game_over:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 185))
        screen.blit(overlay, (0, 0))

        t1 = font_main.render(f"HEIGHT: {state.score}", True, colors["text"])
        t2 = font_main.render("ONE MORE?  (click / space)", True, colors["text"])

        screen.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 40))
        screen.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 + 10))

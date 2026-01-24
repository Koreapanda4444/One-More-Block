
from __future__ import annotations
import pygame
import random
from models import GameState
from typing import Tuple

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
    W, H = screen_size
    screen.fill(colors["bg"])

    # SHAKE 오프셋 계산
    shake_x = 0
    shake_y = 0
    if state.shake_timer > 0.0 and state.shake_total > 0.0:
        t = state.shake_timer / state.shake_total
        amp = state.shake_amp * t
        shake_x = int(random.uniform(-amp, amp))
        shake_y = int(random.uniform(-amp, amp))

    floor_screen_y = int(floor_y - cam_y + shake_y)
    pygame.draw.rect(screen, colors["floor"], pygame.Rect(0 + shake_x, floor_screen_y, W, H - floor_screen_y))

    # 잘린 조각
    for s in state.shards:
        y = (s.y - cam_y) + shake_y
        x = s.x + shake_x
        r = pygame.Rect(int(x), int(y), int(s.w), int(s.h))
        pygame.draw.rect(screen, s.color, r, border_radius=6)

    # 스택
    for b in state.stack:
        y = (b.y - cam_y) + shake_y
        x = b.x + shake_x
        w = b.w
        h = b.h
        # 마지막 착지 블록 스쿼시
        if state.last_settled is b and state.land_timer > 0.0 and state.land_total > 0.0:
            t = state.land_timer / state.land_total
            squash = int(land_squash_px * t)
            h = max(1, h - squash)
            y += squash
        r = pygame.Rect(int(x), int(y), int(w), int(h))
        pygame.draw.rect(screen, b.color, r, border_radius=10)

    # 현재 블록
    if state.current:
        c = state.current
        y = (c.y - cam_y) + shake_y
        x = c.x + shake_x
        r = pygame.Rect(int(x), int(y), int(c.w), int(c.h))
        pygame.draw.rect(screen, c.color, r, border_radius=10)

    # UI
    ui = f"HEIGHT: {state.score}     BEST: {state.best}"
    img = font_main.render(ui, True, colors["text"])
    screen.blit(img, (18, 16))
    hint = "CLICK / SPACE to DROP   |   F11: window mode"
    img2 = font_hint.render(hint, True, colors["text"])
    screen.blit(img2, (18, 46))

    # 화면 중앙 플래시 텍스트
    if state.flash_timer > 0.0 and state.flash_text:
        t = font_flash.render(state.flash_text, True, colors["text"])
        screen.blit(t, (W // 2 - t.get_width() // 2, 86))

        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 185))
        screen.blit(overlay, (0, 0))

        t1 = font_main.render(f"HEIGHT: {state.score}", True, colors["text"])
        t2 = font_main.render("ONE MORE?  (click / space)", True, colors["text"])

        screen.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 40))
        screen.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 + 10))

from __future__ import annotations

import pygame
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
) -> None:
    W, H = screen_size
    screen.fill(colors["bg"])

    floor_screen_y = int(floor_y - cam_y)
    pygame.draw.rect(screen, colors["floor"], pygame.Rect(0, floor_screen_y, W, H - floor_screen_y))

    # 잘린 조각
    for s in state.shards:
        r = pygame.Rect(int(s.x), int(s.y - cam_y), int(s.w), int(s.h))
        pygame.draw.rect(screen, s.color, r, border_radius=6)

    # 스택
    for b in state.stack:
        r = pygame.Rect(int(b.x), int(b.y - cam_y), int(b.w), int(b.h))
        pygame.draw.rect(screen, b.color, r, border_radius=10)

    # 현재 블록
    if state.current:
        c = state.current
        r = pygame.Rect(int(c.x), int(c.y - cam_y), int(c.w), int(c.h))
        pygame.draw.rect(screen, c.color, r, border_radius=10)

    # UI
    ui = f"HEIGHT: {state.score}     BEST: {state.best}"
    img = font_main.render(ui, True, colors["text"])
    screen.blit(img, (18, 16))

    hint = "CLICK / SPACE to DROP   |   F11: window mode"
    img2 = font_hint.render(hint, True, colors["text"])
    screen.blit(img2, (18, 46))

    # 화면 중앙 플래시 텍스트
    if state.flash_text:
        t = font_flash.render(state.flash_text, True, colors["text"])
        screen.blit(t, (W // 2 - t.get_width() // 2, 86))

    if state.game_over:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 185))
        screen.blit(overlay, (0, 0))

        t1 = font_main.render(f"HEIGHT: {state.score}", True, colors["text"])
        t2 = font_main.render("ONE MORE?  (click / space)", True, colors["text"])

        screen.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 40))
        screen.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 + 10))

"""render.py

화면 그리기 전용.
"""

from __future__ import annotations

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
) -> None:
    """한 프레임 렌더."""
    W, H = screen_size

    screen.fill(colors["bg"])

    floor_screen_y = int(floor_y - cam_y)
    pygame.draw.rect(
        screen,
        colors["floor"],
        pygame.Rect(0, floor_screen_y, W, H - floor_screen_y),
    )

    for s in state.shards:
        r = pygame.Rect(int(s.x), int(s.y - cam_y), int(s.w), int(s.h))
        pygame.draw.rect(screen, s.color, r, border_radius=6)

    for b in state.stack:
        r = pygame.Rect(int(b.x), int(b.y - cam_y), int(b.w), int(b.h))
        pygame.draw.rect(screen, b.color, r, border_radius=10)

    if state.current:
        c = state.current
        r = pygame.Rect(int(c.x), int(c.y - cam_y), int(c.w), int(c.h))
        pygame.draw.rect(screen, c.color, r, border_radius=10)

    ui = f"HEIGHT: {state.score}     BEST: {state.best}"
    img = font_main.render(ui, True, colors["text"])
    screen.blit(img, (18, 16))

    hint = "CLICK/SPACE: DROP  |  F11: window size  |  B: BGM  |  [ ]: volume"
    img2 = font_hint.render(hint, True, colors["text"])
    screen.blit(img2, (18, 46))

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

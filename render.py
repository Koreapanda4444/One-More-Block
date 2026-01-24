from __future__ import annotations

"""
render.py

- 토스트(업적 언락 알림) 표시
- A 키 업적 패널 오버레이
- 착지 스쿼시 + 흔들림 FX
"""

import random
from typing import Tuple
import pygame

from models import GameState
import achievements


def _draw_toast(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    W: int,
    y: int,
    alpha: int,
    text_color: Tuple[int, int, int],
) -> None:
    label = font.render(text, True, text_color)

    pad_x, pad_y = 14, 10
    box_w = label.get_width() + pad_x * 2
    box_h = label.get_height() + pad_y * 2

    box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    box.fill((255, 255, 255, max(0, min(alpha, 240))))
    box.blit(label, (pad_x, pad_y))

    x = (W - box_w) // 2
    screen.blit(box, (x, y))


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

    # 흔들림
    shake_x = 0
    shake_y = 0
    if state.shake_timer > 0.0 and state.shake_total > 0.0:
        t = state.shake_timer / state.shake_total
        amp = state.shake_amp * t
        shake_x = int(random.uniform(-amp, amp))
        shake_y = int(random.uniform(-amp, amp))

    # 바닥
    floor_screen_y = int(floor_y - cam_y + shake_y)
    pygame.draw.rect(screen, colors["floor"], pygame.Rect(0 + shake_x, floor_screen_y, W, H - floor_screen_y))

    # 조각
    for s in state.shards:
        r = pygame.Rect(int(s.x + shake_x), int(s.y - cam_y + shake_y), int(s.w), int(s.h))
        pygame.draw.rect(screen, s.color, r, border_radius=6)

    # 스택(+ 스쿼시)
    for b in state.stack:
        x = b.x + shake_x
        y = b.y - cam_y + shake_y
        w = b.w
        h = b.h

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
        r = pygame.Rect(int(c.x + shake_x), int(c.y - cam_y + shake_y), int(c.w), int(c.h))
        pygame.draw.rect(screen, c.color, r, border_radius=10)

    # UI
    ui = f"HEIGHT: {state.score}     BEST: {state.best}"
    screen.blit(font_main.render(ui, True, colors["text"]), (18, 16))

    hint = "CLICK / SPACE to DROP   |   F11: window mode   |   A: achievements"
    screen.blit(font_hint.render(hint, True, colors["text"]), (18, 46))

    if state.flash_text:
        t = font_flash.render(state.flash_text, True, colors["text"])
        screen.blit(t, (W // 2 - t.get_width() // 2, 86))

    # 토스트
    if state.toast_text and state.toast_total > 0.0:
        t = 1.0 - (state.toast_timer / state.toast_total)
        fade_in = min(1.0, t / 0.12)
        fade_out = min(1.0, (1.0 - t) / 0.18)
        alpha = int(220 * fade_in * fade_out)

        _draw_toast(screen, font_hint, state.toast_text, W=W, y=78, alpha=alpha, text_color=colors["text"])

    # 게임오버
    if state.game_over:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 160))
        screen.blit(overlay, (0, 0))

        t1 = font_main.render(f"HEIGHT: {state.score}", True, colors["text"])
        t2 = font_main.render("ONE MORE?  (click / space)", True, colors["text"])
        screen.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 40))
        screen.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 + 10))

    # 업적 패널
    if state.show_achievements:
        panel = pygame.Surface((W, H), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 210))
        screen.blit(panel, (0, 0))

        title = font_flash.render("ACHIEVEMENTS", True, colors["text"])
        screen.blit(title, (W // 2 - title.get_width() // 2, 80))

        x0 = 80
        y0 = 140
        line_h = 28

        for i, a in enumerate(achievements.ALL):
            unlocked = (a.id in state.unlocked_achievements)

            mark = "✅" if unlocked else "🔒"
            prog = ""
            if a.progress is not None:
                cur, goal = a.progress(state)
                cur = max(0, int(cur))
                goal = max(1, int(goal))
                cur = min(cur, goal)
                prog = f"  [{cur}/{goal}]"

            line = f"{mark} {a.title}{prog}"
            screen.blit(font_hint.render(line, True, colors["text"]), (x0, y0 + i * line_h))

        foot = font_hint.render("Press A to close", True, colors["text"])
        screen.blit(foot, (W // 2 - foot.get_width() // 2, H - 70))

from __future__ import annotations

"""render.py

- 테마 적용
- 배경/바닥만 딤(눈부심 완화)
- 파티클/런기록 표시
"""

from typing import Tuple
import pygame
from models import GameState
from themes import get_theme


def _draw_block(screen: pygame.Surface, rect: pygame.Rect, color, theme) -> None:
    if theme.block_outline:
        pygame.draw.rect(screen, theme.outline_color, rect, border_radius=10)
        inner = rect.inflate(-theme.outline_width * 2, -theme.outline_width * 2)
        pygame.draw.rect(screen, color, inner, border_radius=9)
    else:
        pygame.draw.rect(screen, color, rect, border_radius=10)


def draw_game(
    screen: pygame.Surface,
    font_main: pygame.font.Font,
    font_hint: pygame.font.Font,
    font_flash: pygame.font.Font,
    state: GameState,
    cam_y: float,
    screen_size: Tuple[int, int],
    floor_y: float,
    theme_key: str,
) -> None:
    W, H = screen_size
    theme = get_theme(theme_key)

    # 배경/바닥
    screen.fill(theme.bg)
    floor_screen_y = int(floor_y - cam_y)
    pygame.draw.rect(screen, theme.floor, pygame.Rect(0, floor_screen_y, W, H - floor_screen_y))

    # ✅ 배경/바닥만 살짝 딤(블록은 안 딤 → 눈부심만 줄임)
    if theme.bg_dim_alpha > 0:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((*theme.bg_dim_color, int(theme.bg_dim_alpha)))
        screen.blit(overlay, (0, 0))

    # 파티클
    for p in state.particles:
        pr = pygame.Rect(int(p.x), int(p.y - cam_y), int(p.size), int(p.size))
        pygame.draw.rect(screen, p.color, pr, border_radius=2)

    # shards
    for s in state.shards:
        r = pygame.Rect(int(s.x), int(s.y - cam_y), int(s.w), int(s.h))
        pygame.draw.rect(screen, s.color, r, border_radius=6)

    # stack
    for b in state.stack:
        r = pygame.Rect(int(b.x), int(b.y - cam_y), int(b.w), int(b.h))
        _draw_block(screen, r, b.color, theme)

    # current
    if state.current:
        c = state.current
        r = pygame.Rect(int(c.x), int(c.y - cam_y), int(c.w), int(c.h))
        _draw_block(screen, r, c.color, theme)

    # HUD
    ui = f"HEIGHT: {state.score}     BEST: {state.best}"
    img = font_main.render(ui, True, theme.text)
    screen.blit(img, (18, 16))

    hint = "CLICK/SPACE: DROP | F11: window size | B: BGM | [ ]: volume"
    img2 = font_hint.render(hint, True, theme.text)
    screen.blit(img2, (18, 46))

    # Flash
    if state.flash_text:
        t = font_flash.render(state.flash_text, True, theme.text)
        screen.blit(t, (W // 2 - t.get_width() // 2, 86))

    # GameOver UI
    if state.game_over:
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((255, 255, 255, 190))
        screen.blit(ov, (0, 0))

        t1 = font_main.render(f"HEIGHT: {state.score}", True, (20, 20, 20))
        t2 = font_main.render("ONE MORE?  (click / space)", True, (20, 20, 20))
        screen.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 80))
        screen.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 - 30))

        locked = (theme_key not in state.unlocked_themes)
        s = f"Skin: {theme.display}   (LEFT/RIGHT)"
        if locked:
            s += "   [LOCKED]"
        ts = font_hint.render(s, True, (20, 20, 20))
        screen.blit(ts, (W // 2 - ts.get_width() // 2, H // 2 + 10))

        neon_ok = (state.best >= 25)
        paper_ok = (state.lifetime_perfect >= 10)
        p1 = f"Unlock Neon: BEST 25  ({'OK' if neon_ok else f'{state.best}/25'})"
        p2 = f"Unlock Paper: PERFECT 10 total  ({'OK' if paper_ok else f'{state.lifetime_perfect}/10'})"
        u1 = font_hint.render(p1, True, (35, 35, 35))
        u2 = font_hint.render(p2, True, (35, 35, 35))
        screen.blit(u1, (W // 2 - u1.get_width() // 2, H // 2 + 40))
        screen.blit(u2, (W // 2 - u2.get_width() // 2, H // 2 + 62))

        if state.runs:
            title = font_hint.render("Recent Runs:", True, (35, 35, 35))
            screen.blit(title, (18, H - 170))
            y = H - 145
            for r in state.runs[:5]:
                line = f"- {r.get('score', 0)}  | perfect:{r.get('perfect', 0)}  | maxCombo:{r.get('max_combo', 0)}"
                li = font_hint.render(line, True, (35, 35, 35))
                screen.blit(li, (18, y))
                y += 20

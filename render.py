from __future__ import annotations

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


def _fmt_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def _draw_run_summary(
    screen: pygame.Surface,
    font_title: pygame.font.Font,
    font_line: pygame.font.Font,
    state: GameState,
    W: int,
    H: int,
    text_color: Tuple[int, int, int],
) -> None:
    """
    게임오버 시 중앙에 런 요약 박스를 그린다.
    """
    # 평균 겹침 비율 계산(성공 착지 기준)
    if state.run_landings > 0:
        avg = state.run_overlap_sum / max(1, state.run_landings)
    else:
        avg = 0.0

    avg_pct = int(avg * 100)
    last_pct = int(max(0.0, min(1.0, state.run_last_overlap_ratio)) * 100)

    lines = [
        ("HEIGHT", str(state.score)),
        ("BEST", str(state.best)),
        ("MAX COMBO", str(state.run_max_combo)),
        ("PERFECTS", str(state.run_perfects)),
        ("SHARDS", str(state.run_shards_created)),
        ("MIN WIDTH", f"{int(state.run_min_width)} px" if state.run_min_width < 999998 else "-"),
        ("AVG OVERLAP", f"{avg_pct}%"),
        ("LAST OVERLAP", f"{last_pct}%"),
        ("TIME", _fmt_time(state.run_time)),
        ("FAIL", state.fail_reason or "-"),
    ]

    title = font_title.render("RUN SUMMARY", True, text_color)

    # 박스 크기 계산
    pad = 18
    line_h = 24
    box_w = 520
    box_h = pad * 2 + 32 + len(lines) * line_h + 18

    x = (W - box_w) // 2
    y = (H - box_h) // 2 - 10

    panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    panel.fill((255, 255, 255, 235))
    screen.blit(panel, (x, y))

    # 타이틀
    screen.blit(title, (x + (box_w - title.get_width()) // 2, y + pad))

    # 내용
    y_line = y + pad + 40
    key_x = x + 32
    val_x = x + box_w - 32

    for k, v in lines:
        key = font_line.render(k, True, text_color)
        val = font_line.render(v, True, text_color)

        screen.blit(key, (key_x, y_line))
        screen.blit(val, (val_x - val.get_width(), y_line))
        y_line += line_h


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

        # ✅ 런 요약 박스
        _draw_run_summary(
            screen,
            font_title=font_flash,
            font_line=font_hint,
            state=state,
            W=W,
            H=H,
            text_color=colors["text"],
        )

        # 재시작 안내
        t2 = font_main.render("ONE MORE?  (click / space)", True, colors["text"])
        screen.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 + 170))

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

from __future__ import annotations

"""main.py

(2) PERFECT 손맛: shake + particles + sfx
(1) 스킨/해금: Sky/Neon/Paper + 저장
(3) 런 기록 저장/표시
+ 눈부심 완화: themes에서 배경만 딤 처리
"""

import sys
from datetime import datetime
import pygame

import config
from audio import BgmPlayer
from audio_sfx import SfxPlayer
from camera import compute_target_cam_y
from effects import update_effects
from input_handler import handle_events
from models import GameState
from render import draw_game
from save_data import (
    load_best, save_best,
    load_bgm_settings, save_bgm_settings,
    load_theme_settings, save_theme_settings,
    load_lifetime_perfect, save_lifetime_perfect,
    load_runs, append_run,
)
from spawner import reset_run
from themes import next_theme_key, get_theme
from update import update_game
from window import create_screen


def _clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def _key_code_safe(name: str, fallback: int) -> int:
    aliases = {"ESC": "escape", "SPACE": "space", "F11": "f11", "ENTER": "return"}
    key_name = (name or "").strip()
    if not key_name:
        return fallback
    key_name = aliases.get(key_name.upper(), key_name).lower()
    try:
        return pygame.key.key_code(key_name)
    except Exception:
        return fallback


def _try_unlocks(state: GameState) -> bool:
    changed = False

    if state.best >= 25 and "neon" not in state.unlocked_themes:
        state.unlocked_themes.append("neon")
        state.flash_text = "UNLOCKED: Neon"
        state.flash_timer = 1.0
        changed = True

    if state.lifetime_perfect >= 10 and "paper" not in state.unlocked_themes:
        state.unlocked_themes.append("paper")
        state.flash_text = "UNLOCKED: Paper"
        state.flash_timer = 1.0
        changed = True

    if "sky" not in state.unlocked_themes:
        state.unlocked_themes.insert(0, "sky")
        changed = True

    return changed


def _cycle_theme(state: GameState, direction: int) -> None:
    nxt = next_theme_key(state.selected_theme, direction)
    if nxt in state.unlocked_themes:
        state.selected_theme = nxt
        th = get_theme(nxt)
        state.flash_text = f"SKIN: {th.display}"
        state.flash_timer = 0.8
    else:
        th = get_theme(nxt)
        state.flash_text = f"LOCKED: {th.display}"
        state.flash_timer = 0.8


def main() -> None:
    try:
        pygame.mixer.pre_init(44100, -16, 1, 512)
    except Exception:
        pass

    pygame.init()
    pygame.display.set_caption("ONE MORE BLOCK")

    key_toggle = _key_code_safe(config.KEY_TOGGLE_WINDOW_MODE, pygame.K_F11)
    key_quit = _key_code_safe(config.KEY_QUIT, pygame.K_ESCAPE)
    key_drop = _key_code_safe(config.KEY_DROP, pygame.K_SPACE)

    window_mode = config.START_WINDOW_MODE
    screen = create_screen(window_mode, (config.WINDOW_W, config.WINDOW_H))
    W, H = screen.get_size()
    floor_y = H - config.FLOOR_MARGIN

    font_main = pygame.font.SysFont("consolas", 24)
    font_hint = pygame.font.SysFont("consolas", 18)
    font_flash = pygame.font.SysFont("consolas", 30)
    clock = pygame.time.Clock()

    state = GameState()

    # 저장 로드
    state.best = load_best()
    saved_best = state.best

    on, vol = load_bgm_settings(config.BGM_DEFAULT_ON, config.BGM_DEFAULT_VOLUME)
    state.bgm_on = bool(on)
    state.bgm_volume = float(vol)
    saved_bgm_on = state.bgm_on
    saved_bgm_vol = state.bgm_volume

    state.selected_theme, state.unlocked_themes = load_theme_settings("sky")
    saved_theme = state.selected_theme
    saved_unlocked = list(state.unlocked_themes)

    state.lifetime_perfect = load_lifetime_perfect(0)
    saved_lifetime = state.lifetime_perfect

    state.runs = load_runs()

    # 오디오
    bgm = BgmPlayer(on=state.bgm_on, volume=state.bgm_volume)
    bgm.init()
    bgm.apply()

    sfx = SfxPlayer()
    sfx.init()

    # 시작
    reset_run(
        state,
        screen_w=W,
        floor_y=floor_y,
        hover_y=config.HOVER_Y,
        block_h=config.BLOCK_H,
        edge_padding=config.EDGE_PADDING,
        horizontal_speed=config.HORIZONTAL_SPEED,
    )

    cam_y = 0.0
    shake_offset = 0.0

    _try_unlocks(state)

    while state.running:
        dt = clock.tick(config.FPS) / 1000.0

        # (2) 손맛: 파티클/쉐이크 업데이트
        shake_offset = update_effects(state, dt)

        cmd = handle_events(state, key_toggle, key_drop, key_quit)

        # 창 모드 토글
        if cmd == "toggle_window_mode":
            if window_mode == config.WINDOW_MODE_WINDOWED_MAX:
                window_mode = config.WINDOW_MODE_WINDOWED
            else:
                window_mode = config.WINDOW_MODE_WINDOWED_MAX

            screen = create_screen(window_mode, (config.WINDOW_W, config.WINDOW_H))
            W, H = screen.get_size()
            floor_y = H - config.FLOOR_MARGIN

            reset_run(
                state,
                screen_w=W,
                floor_y=floor_y,
                hover_y=config.HOVER_Y,
                block_h=config.BLOCK_H,
                edge_padding=config.EDGE_PADDING,
                horizontal_speed=config.HORIZONTAL_SPEED,
            )
            cam_y = 0.0

        elif cmd == "restart":
            reset_run(
                state,
                screen_w=W,
                floor_y=floor_y,
                hover_y=config.HOVER_Y,
                block_h=config.BLOCK_H,
                edge_padding=config.EDGE_PADDING,
                horizontal_speed=config.HORIZONTAL_SPEED,
            )
            cam_y = 0.0

        # 테마 선택(게임 오버에서만)
        elif cmd == "theme_prev":
            _cycle_theme(state, -1)
        elif cmd == "theme_next":
            _cycle_theme(state, +1)

        # BGM
        elif cmd == "bgm_toggle":
            state.bgm_on = not state.bgm_on
            bgm.on = state.bgm_on
            bgm.apply()
            state.flash_text = "BGM ON" if state.bgm_on else "BGM OFF"
            state.flash_timer = 0.6

        elif cmd == "bgm_up":
            state.bgm_volume = _clamp01(state.bgm_volume + config.BGM_VOLUME_STEP)
            bgm.set_volume(state.bgm_volume)
            if not state.bgm_on:
                state.bgm_on = True
                bgm.on = True
                bgm.apply()
            state.flash_text = f"BGM {int(state.bgm_volume * 100)}%"
            state.flash_timer = 0.6

        elif cmd == "bgm_down":
            state.bgm_volume = _clamp01(state.bgm_volume - config.BGM_VOLUME_STEP)
            bgm.set_volume(state.bgm_volume)
            if state.bgm_volume <= 0.001:
                state.bgm_on = False
                bgm.on = False
                bgm.apply()
            state.flash_text = f"BGM {int(state.bgm_volume * 100)}%"
            state.flash_timer = 0.6

        # flash 타이머
        if state.flash_timer > 0.0:
            state.flash_timer = max(0.0, state.flash_timer - dt)
            if state.flash_timer == 0.0:
                state.flash_text = ""

        # update
        prev_perfect_total = state.run_total_perfect

        update_game(
            state,
            dt=dt,
            screen_w=W,
            floor_y=floor_y,
            hover_y=config.HOVER_Y,
            block_h=config.BLOCK_H,
            fall_speed=config.FALL_SPEED,
            horizontal_speed=config.HORIZONTAL_SPEED,
            edge_padding=config.EDGE_PADDING,
            min_overlap_ratio=config.MIN_OVERLAP_RATIO,
            perfect_ratio=config.PERFECT_RATIO,
            flash_time=config.FLASH_TIME,
            combo_every=config.COMBO_REWARD_EVERY,
            combo_bonus=config.COMBO_WIDTH_BONUS,
            shard_gravity=config.SHARD_GRAVITY,
            shard_fall_speed=config.SHARD_FALL_SPEED,
        )

        # PERFECT 발생 → lifetime 증가 + SFX
        if state.run_total_perfect > prev_perfect_total:
            delta = state.run_total_perfect - prev_perfect_total
            state.lifetime_perfect += delta
            sfx.play_click()

        # best 저장
        if state.best > saved_best:
            save_best(state.best)
            saved_best = state.best

        # 해금 체크
        if _try_unlocks(state):
            save_theme_settings(state.selected_theme, state.unlocked_themes)
            saved_theme = state.selected_theme
            saved_unlocked = list(state.unlocked_themes)

        # lifetime 저장
        if state.lifetime_perfect != saved_lifetime:
            save_lifetime_perfect(state.lifetime_perfect)
            saved_lifetime = state.lifetime_perfect

        # theme 저장
        if state.selected_theme != saved_theme or state.unlocked_themes != saved_unlocked:
            save_theme_settings(state.selected_theme, state.unlocked_themes)
            saved_theme = state.selected_theme
            saved_unlocked = list(state.unlocked_themes)

        # bgm 저장
        if state.bgm_on != saved_bgm_on or abs(state.bgm_volume - saved_bgm_vol) > 1e-6:
            save_bgm_settings(state.bgm_on, state.bgm_volume)
            saved_bgm_on = state.bgm_on
            saved_bgm_vol = state.bgm_volume

        # (3) 런 기록 저장 (1회만)
        if state.game_over and not state.game_over_recorded:
            record = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "score": state.score,
                "perfect": state.run_total_perfect,
                "max_combo": state.run_max_combo,
                "skin": state.selected_theme,
            }
            append_run(record, limit=30)
            state.runs.insert(0, record)
            state.runs = state.runs[:30]
            state.game_over_recorded = True

        # 카메라
        target_cam = compute_target_cam_y(state, config.CAMERA_TOP_MARGIN)
        cam_y += (target_cam - cam_y) * min(1.0, config.CAMERA_SMOOTH * dt)

        cam_draw = cam_y + shake_offset

        draw_game(
            screen,
            font_main=font_main,
            font_hint=font_hint,
            font_flash=font_flash,
            state=state,
            cam_y=cam_draw,
            screen_size=(W, H),
            floor_y=floor_y,
            theme_key=state.selected_theme,
        )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

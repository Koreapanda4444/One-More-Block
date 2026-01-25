"""main.py

One More Block - Pygame

- 풀스크린(FULLSCREEN) 사용 X
- 기본 모드는 "창모드 전체크기(windowed_max)"
- F11로 windowed_max ↔ windowed 토글
- B로 BGM on/off, [ ]로 볼륨 조절
"""

from __future__ import annotations

import sys
import pygame

import config
from audio import BgmPlayer
from camera import compute_target_cam_y
from input_handler import handle_events
from models import GameState
from render import draw_game
from save_data import load_best, load_bgm_settings, save_best, save_bgm_settings
from spawner import reset_run
from update import update_game
from window import create_screen


def _clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def _key_code_safe(name: str, fallback: int) -> int:
    """config에서 문자열 키를 받아 pygame 키코드로 변환.

    pygame이 모르는 축약어(ESC/SPACE 등)도 안전하게 처리한다.
    - 성공: pygame.key.key_code(...)
    - 실패: fallback 반환 (게임이 터지지 않음)
    """
    aliases = {
        "ESC": "escape",
        "ESCAPE": "escape",
        "SPACE": "space",
        "ENTER": "return",
        "RETURN": "return",
        "F11": "f11",
        "F10": "f10",
        "F12": "f12",
    }

    key_name = (name or "").strip()
    if not key_name:
        return fallback

    key_name = aliases.get(key_name.upper(), key_name).lower()

    try:
        return pygame.key.key_code(key_name)
    except Exception:
        return fallback


def main() -> None:
    # mixer 초기화 지연 줄이기(환경에 따라 실패할 수도 있으니 try)
    try:
        pygame.mixer.pre_init(44100, -16, 1, 512)
    except Exception:
        pass

    pygame.init()
    pygame.display.set_caption("ONE MORE BLOCK")

    # ✅ 여기서부터는 config 문자열이 어떤 값이 와도 최대한 안전하게 처리
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

    colors = {"bg": config.BG_COLOR, "floor": config.FLOOR_COLOR, "text": config.TEXT_COLOR}

    state = GameState()

    # ===== Save: BEST =====
    state.best = load_best()
    saved_best = state.best

    # ===== Save: BGM =====
    on, vol = load_bgm_settings(config.BGM_DEFAULT_ON, config.BGM_DEFAULT_VOLUME)
    state.bgm_on = bool(on)
    state.bgm_volume = float(vol)
    saved_bgm_on = state.bgm_on
    saved_bgm_vol = state.bgm_volume

    # ===== BGM =====
    bgm = BgmPlayer(on=state.bgm_on, volume=state.bgm_volume)
    bgm.init()   # 실패하면 enabled=False로 조용히 꺼짐
    bgm.apply()

    # ===== Start Run =====
    reset_run(
        state,
        screen_w=W,
        floor_y=floor_y,
        hover_y=config.HOVER_Y,
        block_h=config.BLOCK_H,
        edge_padding=config.EDGE_PADDING,
        horizontal_speed=config.HORIZONTAL_SPEED,
    )

    # 카메라는 항상 0에서 시작(바닥이 밑에 깔리게)
    cam_y = 0.0

    while state.running:
        dt = clock.tick(config.FPS) / 1000.0

        cmd = handle_events(state, key_toggle, key_drop, key_quit)

        # =========================
        # Window mode toggle (F11)
        # =========================
        if cmd == "toggle_window_mode":
            # windowed_max ↔ windowed
            if window_mode == config.WINDOW_MODE_WINDOWED_MAX:
                window_mode = config.WINDOW_MODE_WINDOWED
            else:
                window_mode = config.WINDOW_MODE_WINDOWED_MAX

            screen = create_screen(window_mode, (config.WINDOW_W, config.WINDOW_H))
            W, H = screen.get_size()
            floor_y = H - config.FLOOR_MARGIN

            # 화면 크기가 바뀌면 런을 깔끔하게 리셋
            reset_run(
                state,
                screen_w=W,
                floor_y=floor_y,
                hover_y=config.HOVER_Y,
                block_h=config.BLOCK_H,
                edge_padding=config.EDGE_PADDING,
                horizontal_speed=config.HORIZONTAL_SPEED,
            )

            # ✅ 카메라도 리셋 (중간에서 시작하는 문제 방지)
            cam_y = 0.0

        # =========================
        # Restart
        # =========================
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

        # =========================
        # BGM Control
        # =========================
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

            # 0%면 자동 OFF (원치 않으면 이 블록 지워도 됨)
            if state.bgm_volume <= 0.001:
                state.bgm_on = False
                bgm.on = False
                bgm.apply()

            state.flash_text = f"BGM {int(state.bgm_volume * 100)}%"
            state.flash_timer = 0.6

        # =========================
        # Flash timer
        # =========================
        if state.flash_timer > 0.0:
            state.flash_timer = max(0.0, state.flash_timer - dt)
            if state.flash_timer == 0.0:
                state.flash_text = ""

        # =========================
        # Update
        # =========================
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

        # =========================
        # Save
        # =========================
        if state.best > saved_best:
            save_best(state.best)
            saved_best = state.best

        if state.bgm_on != saved_bgm_on or abs(state.bgm_volume - saved_bgm_vol) > 1e-6:
            save_bgm_settings(state.bgm_on, state.bgm_volume)
            saved_bgm_on = state.bgm_on
            saved_bgm_vol = state.bgm_volume

        # =========================
        # Camera + Render
        # =========================
        target_cam = compute_target_cam_y(state, config.CAMERA_TOP_MARGIN)
        cam_y += (target_cam - cam_y) * min(1.0, config.CAMERA_SMOOTH * dt)

        draw_game(
            screen,
            font_main=font_main,
            font_hint=font_hint,
            font_flash=font_flash,
            state=state,
            cam_y=cam_y,
            screen_size=(W, H),
            floor_y=floor_y,
            colors=colors,
        )

        pygame.display.flip()

    # 종료 시 마지막 저장
    if state.best > saved_best:
        save_best(state.best)
    save_bgm_settings(state.bgm_on, state.bgm_volume)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

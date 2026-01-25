from __future__ import annotations

import sys

import pygame

import config
from audio import BgmPlayer
from camera import compute_target_cam_y
from input_handler import handle_events
from models import GameState
from render import draw_game
from save_data import load_best, save_best, load_bgm_settings, save_bgm_settings
from spawner import reset_run
from update import update_game
from window import create_screen


def _clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def main() -> None:
    # ✅ mixer 지연 줄이기(가능한 환경에서만)
    try:
        pygame.mixer.pre_init(44100, -16, 1, 512)
    except Exception:
        pass

    pygame.init()
    pygame.display.set_caption("ONE MORE BLOCK")

    key_toggle = pygame.K_F11
    key_quit = pygame.K_ESCAPE
    key_drop = pygame.K_SPACE

    borderless_max = config.START_BORDERLESS_MAX
    screen = create_screen(borderless_max, (config.WINDOW_W, config.WINDOW_H))

    W, H = screen.get_size()
    floor_y = H - config.FLOOR_MARGIN

    font_main = pygame.font.SysFont("consolas", 24)
    font_hint = pygame.font.SysFont("consolas", 18)
    font_flash = pygame.font.SysFont("consolas", 30)
    clock = pygame.time.Clock()

    colors = {"bg": config.BG_COLOR, "floor": config.FLOOR_COLOR, "text": config.TEXT_COLOR}

    # =========================
    # GameState + Save
    # =========================
    state = GameState()

    # BEST 불러오기
    state.best = load_best()
    saved_best = state.best

    # BGM 설정 불러오기
    on, vol = load_bgm_settings(config.BGM_DEFAULT_ON, config.BGM_DEFAULT_VOLUME)
    state.bgm_on = bool(on)
    state.bgm_volume = float(vol)
    saved_bgm_on = state.bgm_on
    saved_bgm_vol = state.bgm_volume

    bgm = BgmPlayer(on=state.bgm_on, volume=state.bgm_volume)
    bgm.init()   # 실패하면 enabled=False로 조용히 꺼짐
    bgm.apply()  # 재생 반영

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

    while state.running:
        dt = clock.tick(config.FPS) / 1000.0

        cmd = handle_events(state, key_toggle, key_drop, key_quit)

        # =========================
        # Command 처리
        # =========================
        if cmd == "toggle_window_mode":
            borderless_max = not borderless_max
            screen = create_screen(borderless_max, (config.WINDOW_W, config.WINDOW_H))
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

        elif cmd == "bgm_toggle":
            state.bgm_on = not state.bgm_on
            bgm.on = state.bgm_on
            bgm.apply()

            state.flash_text = "BGM ON" if state.bgm_on else "BGM OFF"
            state.flash_timer = 0.6

        elif cmd == "bgm_up":
            state.bgm_volume = _clamp01(state.bgm_volume + config.BGM_VOLUME_STEP)
            bgm.set_volume(state.bgm_volume)
            # 볼륨 올리면 자동으로 켜기
            if not state.bgm_on:
                state.bgm_on = True
                bgm.on = True
                bgm.apply()

            state.flash_text = f"BGM {int(state.bgm_volume * 100)}%"
            state.flash_timer = 0.6

        elif cmd == "bgm_down":
            state.bgm_volume = _clamp01(state.bgm_volume - config.BGM_VOLUME_STEP)
            bgm.set_volume(state.bgm_volume)
            # 0%면 자동 OFF 처리(원하면 지워도 됨)
            if state.bgm_volume <= 0.001:
                state.bgm_on = False
                bgm.on = False
                bgm.apply()

            state.flash_text = f"BGM {int(state.bgm_volume * 100)}%"
            state.flash_timer = 0.6

        # =========================
        # Flash timer (기존 PERFECT 텍스트도 자동으로 사라지게)
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
        # Save (best + bgm settings)
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

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

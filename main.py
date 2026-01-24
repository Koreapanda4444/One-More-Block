from __future__ import annotations

"""
main.py

Commit 8:
- save.json: BEST + achievements 저장/로드
- A 업적 패널 열려있을 땐 업데이트 멈춤(읽기 편하게)
"""

import sys
import pygame

import config
from models import GameState
from window import create_screen
from input_handler import handle_events
from update import update_game
from camera import compute_target_cam_y
from render import draw_game
from spawner import reset_run
from save_data import load_profile, save_profile
from difficulty import compute_difficulty


def main() -> None:
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

    state = GameState()

    best, unlocked = load_profile()
    state.best = best
    state.unlocked_achievements = set(unlocked)

    saved_best = state.best
    saved_unlocked = set(state.unlocked_achievements)

    reset_run(
        state,
        screen_w=W,
        floor_y=floor_y,
        hover_y=config.HOVER_Y,
        block_h=config.BLOCK_H,
        edge_padding=config.EDGE_PADDING,
        horizontal_speed=config.HORIZONTAL_SPEED,
        width_jitter=config.DIFF_JITTER_BASE,
        spawn_offset=config.DIFF_SPAWN_OFFSET_BASE,
    )

    cam_y = 0.0

    while state.running:
        dt = clock.tick(config.FPS) / 1000.0

        cmd = handle_events(state, key_toggle, key_drop, key_quit)

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
                width_jitter=config.DIFF_JITTER_BASE,
                spawn_offset=config.DIFF_SPAWN_OFFSET_BASE,
            )

        if cmd == "restart":
            reset_run(
                state,
                screen_w=W,
                floor_y=floor_y,
                hover_y=config.HOVER_Y,
                block_h=config.BLOCK_H,
                edge_padding=config.EDGE_PADDING,
                horizontal_speed=config.HORIZONTAL_SPEED,
                width_jitter=config.DIFF_JITTER_BASE,
                spawn_offset=config.DIFF_SPAWN_OFFSET_BASE,
            )

        # 업적 패널 열려 있으면 업데이트 멈춤
        if not state.show_achievements:
            diff = compute_difficulty(
                score=state.score,
                base_hs=config.HORIZONTAL_SPEED,
                base_fs=config.FALL_SPEED,
                base_jitter=config.DIFF_JITTER_BASE,
                base_offset=config.DIFF_SPAWN_OFFSET_BASE,
                step_score=config.DIFF_STEP_SCORE,
                hs_step=config.DIFF_HS_STEP,
                hs_max_mul=config.DIFF_HS_MAX_MUL,
                fs_step=config.DIFF_FALL_STEP,
                fs_max_mul=config.DIFF_FALL_MAX_MUL,
                jitter_step=config.DIFF_JITTER_STEP,
                jitter_max=config.DIFF_JITTER_MAX,
                offset_step=config.DIFF_SPAWN_OFFSET_STEP,
                offset_max=config.DIFF_SPAWN_OFFSET_MAX,
            )

            update_game(
                state,
                dt=dt,
                screen_w=W,
                floor_y=floor_y,
                hover_y=config.HOVER_Y,
                block_h=config.BLOCK_H,
                fall_speed=diff.fall_speed,
                horizontal_speed=diff.horizontal_speed,
                edge_padding=config.EDGE_PADDING,
                min_overlap_ratio=config.MIN_OVERLAP_RATIO,
                perfect_ratio=config.PERFECT_RATIO,
                flash_time=config.FLASH_TIME,
                combo_every=config.COMBO_REWARD_EVERY,
                combo_bonus=config.COMBO_WIDTH_BONUS,
                shard_gravity=config.SHARD_GRAVITY,
                shard_fall_speed=config.SHARD_FALL_SPEED,
                shard_initial_vy=config.SHARD_FALL_SPEED,
                land_time=config.LAND_SQUASH_TIME,
                shake_time=config.SHAKE_TIME,
                shake_intensity=config.SHAKE_INTENSITY,
                perfect_shake_mult=config.PERFECT_SHAKE_MULT,
                width_jitter=diff.width_jitter,
                spawn_offset=diff.spawn_offset,
                toast_time=config.TOAST_TIME,
            )

        # 저장(변경 시만)
        if state.best != saved_best or state.unlocked_achievements != saved_unlocked:
            save_profile(state.best, state.unlocked_achievements)
            saved_best = state.best
            saved_unlocked = set(state.unlocked_achievements)

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
            land_squash_px=config.LAND_SQUASH_PIXELS,
        )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

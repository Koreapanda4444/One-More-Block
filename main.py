from __future__ import annotations

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

        if cmd == "restart":
            reset_run(
                state,
                screen_w=W,
                floor_y=floor_y,
                hover_y=config.HOVER_Y,
                block_h=config.BLOCK_H,
                edge_padding=config.EDGE_PADDING,
                horizontal_speed=config.HORIZONTAL_SPEED,
            )

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
        )

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

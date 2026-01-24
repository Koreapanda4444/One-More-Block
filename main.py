from __future__ import annotations

"""
main.py

게임 실행 진입점.
- pygame 초기화
- 메인 루프(dt 기반 업데이트)
- 입력 처리 → 업데이트 → 카메라 → 렌더 순서

구조가 깔끔해야 디버깅/확장이 쉬움.
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
from save_data import load_best, save_best
from difficulty import compute_difficulty


def main() -> None:
    # =========================
    # pygame 초기화
    # =========================
    pygame.init()
    pygame.display.set_caption("ONE MORE BLOCK")

    # 키 매핑(지금은 코드 안에서만 사용)
    key_toggle = pygame.K_F11
    key_quit = pygame.K_ESCAPE
    key_drop = pygame.K_SPACE

    # =========================
    # 화면 생성 (테두리 없는 최대화 / 창 모드)
    # =========================
    borderless_max = config.START_BORDERLESS_MAX
    screen = create_screen(borderless_max, (config.WINDOW_W, config.WINDOW_H))

    W, H = screen.get_size()
    floor_y = H - config.FLOOR_MARGIN  # 바닥 y(월드 좌표 기준)

    # =========================
    # 폰트 / 프레임 타이머
    # =========================
    font_main = pygame.font.SysFont("consolas", 24)
    font_hint = pygame.font.SysFont("consolas", 18)
    font_flash = pygame.font.SysFont("consolas", 30)

    clock = pygame.time.Clock()

    colors = {
        "bg": config.BG_COLOR,
        "floor": config.FLOOR_COLOR,
        "text": config.TEXT_COLOR,
    }

    # =========================
    # 게임 상태 생성 + BEST 로드
    # =========================
    state = GameState()

    state.best = load_best()
    saved_best = state.best  # 변경 감지를 위한 값

    # 런 시작(첫 블록/첫 current 블록 생성)
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

    cam_y = 0.0  # 카메라 y(렌더에서만 사용)

    # =========================
    # 메인 루프
    # =========================
    while state.running:
        # dt: 프레임 시간(초). FPS가 떨어져도 게임 속도 유지 가능
        dt = clock.tick(config.FPS) / 1000.0

        # 1) 입력 처리(상태 변화/명령 반환)
        cmd = handle_events(state, key_toggle, key_drop, key_quit)

        # 2) 창 모드 토글
        if cmd == "toggle_window_mode":
            borderless_max = not borderless_max
            screen = create_screen(borderless_max, (config.WINDOW_W, config.WINDOW_H))

            # 화면 크기가 바뀌면 floor_y도 다시 계산해야 함
            W, H = screen.get_size()
            floor_y = H - config.FLOOR_MARGIN

            # 모드 바뀌면 스케일/좌표가 달라질 수 있으니 런 리셋
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

        # 3) 재시작(게임오버 후)
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

        # 4) 난이도 계산(점수 기반)
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

        # 5) 업데이트(물리/판정/스폰/이펙트 타이머)
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
            land_time=config.LAND_SQUASH_TIME,
            land_squash_px=config.LAND_SQUASH_PIXELS,
            shake_time=config.SHAKE_TIME,
            shake_intensity=config.SHAKE_INTENSITY,
            perfect_shake_mult=config.PERFECT_SHAKE_MULT,
            width_jitter=diff.width_jitter,
            spawn_offset=diff.spawn_offset,
        )

        # 6) BEST 저장(갱신될 때만)
        if state.best > saved_best:
            save_best(state.best)
            saved_best = state.best

        # 7) 카메라 목표값 계산 + 스무딩 적용
        target_cam = compute_target_cam_y(state, config.CAMERA_TOP_MARGIN)
        cam_y += (target_cam - cam_y) * min(1.0, config.CAMERA_SMOOTH * dt)

        # 8) 렌더
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

    # =========================
    # 종료 처리
    # =========================
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

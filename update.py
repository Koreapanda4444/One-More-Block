from __future__ import annotations

from models import GameState, BlockShard
from mechanics import top_surface_y, get_top_block, compute_overlap
from spawner import spawn_next_block

def update_game(
    state: GameState,
    dt: float,
    screen_w: int,
    floor_y: float,
    hover_y: int,
    block_h: int,
    fall_speed: float,
    horizontal_speed: float,
    edge_padding: int,
    min_overlap_ratio: float,
    perfect_ratio: float,
    flash_time: float,
    combo_every: int,
    combo_bonus: int,
    shard_gravity: float,
    shard_fall_speed: float,
) -> None:
    if state.game_over:
        return

    if state.current is None:
        spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed)
        return

    cur = state.current

    if cur.phase == "move":
        cur.x += cur.vx * dt

        # drop 시작 직전에 원본 폭 저장
        if not hasattr(cur, "_orig_w"):
            cur._orig_w = cur.w

        # 기존 블록 중심 기준 ±120px 범위 내에서만 이동
        top = get_top_block(state)
        if top:
            center_x = top.x + top.w / 2
            move_range = 500
            left_limit = max(center_x - move_range, edge_padding)
            right_limit = min(center_x + move_range - cur.w, screen_w - edge_padding - cur.w)
        else:
            left_limit = edge_padding
            right_limit = screen_w - edge_padding - cur.w

        if cur.x <= left_limit:
            cur.x = left_limit
            cur.vx *= -1
        elif cur.x >= right_limit:
            cur.x = right_limit
            cur.vx *= -1

        cur.y = hover_y
        return

    if cur.phase == "drop":
        cur.y += fall_speed * dt

        land_y = top_surface_y(state, floor_y) - cur.h
        if cur.y >= land_y:
            cur.y = land_y

            top = get_top_block(state)
            if top is None:
                state.game_over = True
                state.best = max(state.best, state.score)
                return

            overlap_w, overlap_left, ratio = compute_overlap(cur, top)

            if ratio < min_overlap_ratio or overlap_w <= 0.0:
                state.game_over = True
                state.best = max(state.best, state.score)
                return

            # 🔥 트림 직후에 조각 생성
            left = overlap_left
            original_width = getattr(cur, "_orig_w", cur.w)
            # 잘린 왼쪽 조각
            if cur.x > left:
                state.shards.append(
                    BlockShard(
                        x=cur.x,
                        y=cur.y,
                        w=left - cur.x,
                        h=cur.h,
                        color=cur.color,
                        vy=shard_fall_speed,
                    )
                )
            # 잘린 오른쪽 조각
            right_edge = left + overlap_w
            orig_right = cur.x + original_width
            if right_edge < orig_right:
                state.shards.append(
                    BlockShard(
                        x=right_edge,
                        y=cur.y,
                        w=orig_right - right_edge,
                        h=cur.h,
                        color=cur.color,
                        vy=shard_fall_speed,
                    )
                )

            cur.x = overlap_left
            cur.w = overlap_w
            cur.phase = "settled"
            state.stack.append(cur)
            state.score += 1

            # PERFECT / COMBO 판정
            if ratio >= perfect_ratio:
                state.perfect_combo += 1
                state.flash_text = f"PERFECT x{state.perfect_combo}"
                state.flash_timer = flash_time
                if state.perfect_combo % combo_every == 0:
                    state.width_bonus += combo_bonus
            else:
                state.perfect_combo = 0

            spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed)
        return

    # 🧩 SHARD 업데이트
    for s in state.shards[:]:
        s.vy += shard_gravity * dt
        s.y += s.vy * dt
        if s.y > floor_y + 300:
            state.shards.remove(s)

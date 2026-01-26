from __future__ import annotations

"""update.py

- shards는 game_over여도 계속 떨어지게 유지
- 실패 시 현재 블록 전체를 shard로 떨어뜨려 "안 떨어짐" 이슈 방지
- PERFECT 시 effects.trigger_perfect() 호출
"""

from mechanics import compute_overlap, get_top_block, top_surface_y
from models import BlockShard, GameState
from spawner import spawn_next_block
from effects import trigger_perfect


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
    # shards는 항상 업데이트
    for s in state.shards[:]:
        s.vy += shard_gravity * dt
        s.y += s.vy * dt
        if s.y > floor_y + 300:
            state.shards.remove(s)

    if state.game_over:
        return

    if state.current is None:
        spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed)
        return

    cur = state.current

    if cur.phase == "move":
        cur.x += cur.vx * dt

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
        if cur.y < land_y:
            return

        shard_y = land_y
        cur.y = land_y

        top = get_top_block(state)
        if top is None:
            state.game_over = True
            state.best = max(state.best, state.score)
            return

        overlap_w, overlap_left, ratio = compute_overlap(cur, top)

        # 실패: 현재 블록 전체를 shard로
        if ratio < min_overlap_ratio or overlap_w <= 0.0:
            state.shards.append(
                BlockShard(x=cur.x, y=shard_y, w=cur.w, h=cur.h, color=cur.color, vy=shard_fall_speed)
            )
            state.current = None
            state.game_over = True
            state.best = max(state.best, state.score)
            return

        # 성공: 트림
        orig_left = cur._orig_x if cur._orig_w else cur.x
        orig_w = cur._orig_w if cur._orig_w else cur.w
        orig_right = orig_left + orig_w

        new_left = overlap_left
        new_right = overlap_left + overlap_w

        if new_left > orig_left:
            state.shards.append(
                BlockShard(x=orig_left, y=shard_y, w=new_left - orig_left, h=cur.h, color=cur.color, vy=shard_fall_speed)
            )

        if new_right < orig_right:
            state.shards.append(
                BlockShard(x=new_right, y=shard_y, w=orig_right - new_right, h=cur.h, color=cur.color, vy=shard_fall_speed)
            )

        cur.x = new_left
        cur.w = overlap_w
        cur.phase = "settled"
        state.stack.append(cur)

        state.score += 1

        if ratio >= perfect_ratio:
            state.perfect_combo += 1
            state.run_total_perfect += 1
            state.run_max_combo = max(state.run_max_combo, state.perfect_combo)

            state.flash_text = f"PERFECT x{state.perfect_combo}"
            state.flash_timer = flash_time

            cx = cur.x + cur.w * 0.5
            trigger_perfect(state, cx, shard_y, cur.color)

            if state.perfect_combo % combo_every == 0:
                state.width_bonus += combo_bonus
        else:
            state.perfect_combo = 0

        spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed)
        return

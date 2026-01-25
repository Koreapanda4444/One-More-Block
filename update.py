from __future__ import annotations

from models import GameState, BlockShard
from mechanics import top_surface_y, get_top_block, compute_overlap
from spawner import spawn_next_block
import achievements


def _toast_tick(state: GameState, dt: float) -> None:
    if state.toast_timer > 0.0:
        state.toast_timer = max(0.0, state.toast_timer - dt)
        if state.toast_timer == 0.0:
            state.toast_text = ""

    if state.toast_timer == 0.0 and state.toast_queue:
        state.toast_text = state.toast_queue.popleft()
        state.toast_total = max(0.6, float(state.toast_total))
        state.toast_timer = state.toast_total


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
    shard_initial_vy: float,
    land_time: float,
    shake_time: float,
    shake_intensity: float,
    perfect_shake_mult: float,
    width_jitter: int,
    spawn_offset: int,
    toast_time: float,
) -> None:
    # 타이머
    if state.flash_timer > 0.0:
        state.flash_timer = max(0.0, state.flash_timer - dt)
        if state.flash_timer == 0.0:
            state.flash_text = ""

    if state.land_timer > 0.0:
        state.land_timer = max(0.0, state.land_timer - dt)
        if state.land_timer == 0.0:
            state.last_settled = None

    if state.shake_timer > 0.0:
        state.shake_timer = max(0.0, state.shake_timer - dt)

    state.toast_total = float(toast_time)
    _toast_tick(state, dt)

    # SHARD는 항상 업데이트
    for s in state.shards[:]:
        s.vy += shard_gravity * dt
        s.y += s.vy * dt
        if s.y > floor_y + 300:
            state.shards.remove(s)

    if state.game_over:
        return

    if state.current is None:
        spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed, width_jitter, spawn_offset)
        return

    cur = state.current

    # MOVE
    if cur.phase == "move":
        sign = 1.0 if cur.vx >= 0 else -1.0
        cur.vx = sign * float(horizontal_speed)

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

    # DROP
    if cur.phase == "drop":
        cur.y += float(fall_speed) * dt

        land_y = top_surface_y(state, floor_y) - cur.h
        if cur.y < land_y:
            return

        shard_y = land_y
        cur.y = land_y

        top = get_top_block(state)
        if top is None:
            state.game_over = True
            state.fail_reason = "기반 블록 없음"
            state.best = max(state.best, state.score)
            state.sfx_queue.append("gameover")
            return

        overlap_w, overlap_left, ratio = compute_overlap(cur, top)
        state.run_last_overlap_ratio = float(ratio)

        # 실패
        if overlap_w <= 0.0:
            state.game_over = True
            state.fail_reason = "완전 빗나감"
            state.best = max(state.best, state.score)
            state.sfx_queue.append("gameover")
            return

        if ratio < float(min_overlap_ratio):
            state.game_over = True
            state.fail_reason = "겹침 부족"
            state.best = max(state.best, state.score)
            state.sfx_queue.append("gameover")
            return

        # 조각 생성(원본 기준)
        orig_left = getattr(cur, "_orig_x", cur.x)
        orig_right = orig_left + getattr(cur, "_orig_w", cur.w)

        new_left = overlap_left
        new_right = overlap_left + overlap_w

        added_shards = 0

        left_w = new_left - orig_left
        if left_w > 0.0:
            state.shards.append(
                BlockShard(x=orig_left, y=shard_y, w=left_w, h=cur.h, color=cur.color, vy=float(shard_initial_vy))
            )
            added_shards += 1

        right_w = orig_right - new_right
        if right_w > 0.0:
            state.shards.append(
                BlockShard(x=new_right, y=shard_y, w=right_w, h=cur.h, color=cur.color, vy=float(shard_initial_vy))
            )
            added_shards += 1

        state.run_shards_created += added_shards

        # 트림 후 착지
        cur.x = overlap_left
        cur.w = overlap_w
        cur.phase = "settled"
        state.stack.append(cur)
        state.score += 1
        state.best = max(state.best, state.score)

        # 런 통계
        state.run_landings += 1
        state.run_overlap_sum += float(ratio)
        state.run_min_width = min(state.run_min_width, float(cur.w))
        if cur.w <= 80:
            state.run_narrow_streak += 1
        else:
            state.run_narrow_streak = 0

        # 착지 FX
        state.last_settled = cur
        state.land_total = float(land_time)
        state.land_timer = float(land_time)

        is_perfect = ratio >= float(perfect_ratio)

        state.shake_total = float(shake_time)
        state.shake_timer = float(shake_time)
        state.shake_amp = float(shake_intensity) * (float(perfect_shake_mult) if is_perfect else 1.0)

        # SFX: land + (perfect면 perfect 추가)
        state.sfx_queue.append("land")
        if is_perfect:
            state.sfx_queue.append("perfect")

        # PERFECT / COMBO
        if is_perfect:
            state.perfect_combo += 1
            state.run_perfects += 1
            state.flash_text = f"PERFECT x{state.perfect_combo}"
            state.flash_timer = float(flash_time)
        else:
            state.perfect_combo = 0

        state.run_max_combo = max(state.run_max_combo, state.perfect_combo)

        if is_perfect and combo_every > 0 and (state.perfect_combo % int(combo_every) == 0):
            state.width_bonus += int(combo_bonus)

        # 업적 체크
        newly = achievements.unlock_new(state)
        for a in newly:
            state.toast_queue.append(f"ACHIEVEMENT UNLOCKED: {a.title}")

        spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed, width_jitter, spawn_offset)
        return

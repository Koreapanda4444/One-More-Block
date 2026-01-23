from __future__ import annotations

from models import GameState, BlockShard
from mechanics import top_surface_y, get_top_block, compute_overlap
from spawner import spawn_next_block


def update_game(
    state: GameState,
    dt: float,
    screen_w: int,
    floor_y: float,
    hover_y: float,
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
    # =========================
    # 0) FLASH 타이머 (항상 감소)
    # =========================
    if state.flash_timer > 0.0:
        state.flash_timer = max(0.0, state.flash_timer - dt)
        if state.flash_timer == 0.0:
            state.flash_text = ""

    # =========================
    # 1) SHARD 업데이트는 "항상" 수행
    #    (move/drop에서 return 해도 위에서 이미 갱신됨)
    # =========================
    for s in state.shards[:]:
        s.vy += shard_gravity * dt
        s.y += s.vy * dt
        if s.y > floor_y + 300:
            state.shards.remove(s)

    # 게임오버여도 shard는 계속 떨어지고, flash는 꺼져야 하니까
    # shard/flash 처리 후에만 return
    if state.game_over:
        return

    # 현재 블록이 없으면 생성
    if state.current is None:
        spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed)
        return

    cur = state.current

    # =========================
    # 2) MOVE
    # =========================
    if cur.phase == "move":
        cur.x += cur.vx * dt

        # 기존 블록 중심 기준으로 제한된 범위에서만 왕복
        top = get_top_block(state)
        if top:
            center_x = top.x + top.w / 2
            move_range = 500  # 너 코드에서 쓰던 값 유지
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

    # =========================
    # 3) DROP
    # =========================
    if cur.phase == "drop":
        cur.y += fall_speed * dt

        land_y = top_surface_y(state, floor_y) - cur.h
        if cur.y >= land_y:
            # settle 직전 y를 shard 생성에 그대로 사용
            shard_y = land_y
            cur.y = land_y

            top = get_top_block(state)
            if top is None:
                state.game_over = True
                state.best = max(state.best, state.score)
                return

            overlap_w, overlap_left, ratio = compute_overlap(cur, top)

            # 실패(겹침 부족) -> 게임오버
            if ratio < min_overlap_ratio or overlap_w <= 0.0:
                state.game_over = True
                state.best = max(state.best, state.score)
                return

            # ✅ shard 생성(원본 기준) : input_handler에서 _orig_x/_orig_w 저장됨
            # 없으면(혹시라도) 현재 값으로 fallback
            orig_left = getattr(cur, "_orig_x", cur.x)
            orig_right = orig_left + getattr(cur, "_orig_w", cur.w)
            new_left = overlap_left
            new_right = overlap_left + overlap_w

            # 왼쪽 조각
            left_w = new_left - orig_left
            if left_w > 0.0:
                state.shards.append(
                    BlockShard(
                        x=orig_left,
                        y=shard_y,
                        w=left_w,
                        h=cur.h,
                        color=cur.color,
                        vy=shard_fall_speed,
                    )
                )

            # 오른쪽 조각
            right_w = orig_right - new_right
            if right_w > 0.0:
                state.shards.append(
                    BlockShard(
                        x=new_right,
                        y=shard_y,
                        w=right_w,
                        h=cur.h,
                        color=cur.color,
                        vy=shard_fall_speed,
                    )
                )

            # trim(겹친 부분만 남김)
            cur.x = overlap_left
            cur.w = overlap_w
            cur.phase = "settled"
            state.stack.append(cur)
            state.score += 1

            # PERFECT / COMBO
            if ratio >= perfect_ratio:
                state.perfect_combo += 1
                state.flash_text = f"PERFECT x{state.perfect_combo}"
                state.flash_timer = flash_time
                if combo_every > 0 and (state.perfect_combo % combo_every == 0):
                    state.width_bonus += combo_bonus
            else:
                state.perfect_combo = 0

            spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed)
        return

    # 혹시 cur.phase가 예상 밖이면(예: settled로 남아버림) 다음 블록 강제 생성
    spawn_next_block(state, screen_w, hover_y, block_h, edge_padding, horizontal_speed)

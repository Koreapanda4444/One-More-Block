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
    land_time: float,
    land_squash_px: float,   # render에서 스쿼시 양으로 사용(여기선 timer만 관리)
    shake_time: float,
    shake_intensity: float,
    perfect_shake_mult: float,
    width_jitter: int,
    spawn_offset: int,
) -> None:
    """
    게임 루프에서 매 프레임 호출되는 업데이트 함수.

    핵심 철학:
    - '조각(shards) 물리'는 **move/drop에서 return 하더라도** 항상 업데이트되어야 함
      (이게 안 되면 조각이 공중에서 멈춰 보이는 버그가 생김)

    흐름:
    0) FX 타이머 감소(착지 스쿼시/쉐이크/플래시)
    1) 조각(shard) 물리 업데이트(항상)
    2) 게임오버면 로직 중지(조각은 1)에서 이미 떨어지고 있음)
    3) current 없으면 스폰
    4) current.phase에 따라 move / drop 처리
    """
    # =========================
    # 0) FX 타이머 감소
    # =========================
    if state.land_timer > 0.0:
        state.land_timer = max(0.0, state.land_timer - dt)
        # 착지 눌림이 끝나면 대상 블록 해제
        if state.land_timer == 0.0:
            state.last_settled = None

    if state.shake_timer > 0.0:
        state.shake_timer = max(0.0, state.shake_timer - dt)

    if state.flash_timer > 0.0:
        state.flash_timer = max(0.0, state.flash_timer - dt)
        if state.flash_timer == 0.0:
            state.flash_text = ""

    # =========================
    # 1) SHARD 물리 업데이트(항상 실행)
    # =========================
    for s in state.shards[:]:
        s.vy += shard_gravity * dt
        s.y += s.vy * dt
        # 화면 아래로 충분히 내려가면 제거(메모리/성능 보호)
        if s.y > floor_y + 300:
            state.shards.remove(s)

    # =========================
    # 2) 게임오버면 현재 블록 로직은 중단
    # =========================
    if state.game_over:
        return

    # =========================
    # 3) current 없으면 바로 생성
    # =========================
    if state.current is None:
        spawn_next_block(
            state,
            screen_w,
            int(hover_y),
            block_h,
            edge_padding,
            horizontal_speed,
            width_jitter,
            spawn_offset,
        )
        return

    cur = state.current

    # =========================
    # 4) MOVE: 좌우 왕복 이동
    # =========================
    if cur.phase == "move":
        # 난이도가 올라가면 horizontal_speed가 바뀌므로,
        # 방향은 유지하고 속도 크기만 갱신한다.
        sign = 1.0 if cur.vx >= 0 else -1.0
        cur.vx = sign * float(horizontal_speed)

        cur.x += cur.vx * dt

        # 왕복 범위 제한: 탑 블록 중심을 기준으로 일정 범위 안에서만 움직이게
        top = get_top_block(state)
        if top:
            center_x = top.x + top.w / 2
            move_range = 500
            left_limit = max(center_x - move_range, edge_padding)
            right_limit = min(center_x + move_range - cur.w, screen_w - edge_padding - cur.w)
        else:
            left_limit = edge_padding
            right_limit = screen_w - edge_padding - cur.w

        # 벽에 닿으면 반사
        if cur.x <= left_limit:
            cur.x = left_limit
            cur.vx *= -1
        elif cur.x >= right_limit:
            cur.x = right_limit
            cur.vx *= -1

        # move 동안에는 y는 hover_y 고정
        cur.y = hover_y
        return

    # =========================
    # 5) DROP: 낙하 → 착지 → 트림/성공/실패 판정
    # =========================
    if cur.phase == "drop":
        cur.y += fall_speed * dt

        # 착지해야 하는 y(탑 표면 - 내 높이)
        land_y = top_surface_y(state, floor_y) - cur.h

        # 아직 착지 못 했으면 계속 낙하
        if cur.y < land_y:
            return

        # 착지 시점
        shard_y = land_y
        cur.y = land_y

        top = get_top_block(state)
        if top is None:
            # 안전 장치: 탑이 없으면 게임오버 처리
            state.game_over = True
            state.best = max(state.best, state.score)
            return

        overlap_w, overlap_left, ratio = compute_overlap(cur, top)

        # 겹침이 너무 적으면 실패(게임오버)
        if ratio < min_overlap_ratio or overlap_w <= 0.0:
            state.game_over = True
            state.best = max(state.best, state.score)
            return

        # ----- (A) 조각(shard) 생성: "원본 블록 기준"으로 잘린 좌/우를 만든다 -----
        # input_handler에서 drop 전환 시 cur._orig_x / cur._orig_w 저장해 둔 값을 사용.
        # 없으면 fallback으로 현재 값 사용(최악의 경우라도 크래시 방지)
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

        # ----- (B) 트림: 겹친 부분만 남기고, 스택에 넣는다 -----
        cur.x = overlap_left
        cur.w = overlap_w
        cur.phase = "settled"
        state.stack.append(cur)
        state.score += 1

        # ----- (C) 착지/흔들림 FX -----
        state.last_settled = cur
        state.land_timer = land_time
        state.land_total = land_time

        is_perfect = (ratio >= perfect_ratio)

        state.shake_timer = shake_time
        state.shake_total = shake_time
        state.shake_amp = shake_intensity * (perfect_shake_mult if is_perfect else 1.0)

        # ----- (D) PERFECT / COMBO -----
        if is_perfect:
            state.perfect_combo += 1
            state.flash_text = f"PERFECT x{state.perfect_combo}"
            state.flash_timer = flash_time

            # N연속마다 폭 보상(다음 블록에 1회성 적용)
            if combo_every > 0 and (state.perfect_combo % combo_every == 0):
                state.width_bonus += combo_bonus
        else:
            state.perfect_combo = 0

        # ----- (E) 다음 블록 생성 -----
        spawn_next_block(
            state,
            screen_w,
            int(hover_y),
            block_h,
            edge_padding,
            horizontal_speed,
            width_jitter,
            spawn_offset,
        )
        return

    # phase가 예상 밖이면(버그/예외) 다음 블록으로 복구
    spawn_next_block(
        state,
        screen_w,
        int(hover_y),
        block_h,
        edge_padding,
        horizontal_speed,
        width_jitter,
        spawn_offset,
    )

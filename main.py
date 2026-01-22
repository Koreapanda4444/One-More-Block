# main.py
from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

# ============================================================
# 0) 기본 설정
# ============================================================

FPS = 60

# 일반 창모드 크기(토글용)
WINDOW_W, WINDOW_H = 900, 600

# ✅ "풀스크린 금지" / 대신 보더리스 최대화 창 사용
START_BORDERLESS_MAX = True
TOGGLE_WINDOW_MODE_KEY = pygame.K_F11

# ✅ 밝은 UI 톤
BG_COLOR = (235, 245, 255)
FLOOR_COLOR = (180, 205, 230)
TEXT_COLOR = (40, 55, 75)

# 바닥: 화면 아래에서 몇 px 위
FLOOR_MARGIN = 60

# 블록
BLOCK_H = 34
FALL_SPEED = 380  # px/s

# 애매 물리 판정
STABLE_OVERLAP = 0.65
CRITICAL_OVERLAP = 0.45

# 카메라
CAMERA_SMOOTH = 8.0
CAMERA_TOP_MARGIN = 180

# 전역 화면 값(창모드/보더리스 토글 시 갱신)
W, H = WINDOW_W, WINDOW_H
FLOOR_Y = H - FLOOR_MARGIN


# ============================================================
# 1) 데이터 구조
# ============================================================

def pastel_color() -> Tuple[int, int, int]:
    base = 190
    return (
        base + random.randint(0, 50),
        base + random.randint(0, 50),
        base + random.randint(0, 50),
    )

@dataclass
class Block:
    x: float
    y: float
    w: float
    h: float
    color: Tuple[int, int, int]
    falling: bool = True
    settled: bool = False
    wobble_phase: float = 0.0

@dataclass
class GameState:
    running: bool = True
    game_over: bool = False

    height_score: int = 0
    best_score: int = 0

    current: Optional[Block] = None
    stack: List[Block] = None

    pending_collapse: bool = False
    collapse_timer: float = 0.0

    def __post_init__(self):
        if self.stack is None:
            self.stack = []


# ============================================================
# 2) 유틸
# ============================================================

def overlap_ratio(a: Block, b: Block) -> float:
    a_left, a_right = a.x, a.x + a.w
    b_left, b_right = b.x, b.x + b.w
    inter = max(0.0, min(a_right, b_right) - max(a_left, b_left))
    return inter / max(a.w, 1.0)

def top_surface_y(state: GameState) -> float:
    if not state.stack:
        return float(FLOOR_Y)
    return float(min(b.y for b in state.stack))

def spawn_block(state: GameState) -> None:
    base_w = 220
    shrink = min(state.height_score * 6, 140)
    w = max(80, base_w - shrink + random.randint(-30, 30))

    x = (W - w) / 2
    y = -BLOCK_H - 10

    state.current = Block(
        x=x,
        y=y,
        w=w,
        h=BLOCK_H,
        color=pastel_color(),
        falling=True,
        settled=False,
        wobble_phase=random.random() * 10.0,
    )

def reset_run(state: GameState) -> None:
    state.game_over = False
    state.pending_collapse = False
    state.collapse_timer = 0.0

    state.height_score = 0
    state.stack = []
    state.current = None
    spawn_block(state)


# ============================================================
# 3) 애매 물리 판정
# ============================================================

def judge_settle(state: GameState, landed_on: Optional[Block]) -> None:
    cur = state.current
    if cur is None:
        return

    ratio = 1.0 if landed_on is None else overlap_ratio(cur, landed_on)

    if ratio >= STABLE_OVERLAP:
        cur.settled = True
        cur.falling = False
        state.stack.append(cur)
        state.height_score += 1
        spawn_block(state)
        return

    if ratio < CRITICAL_OVERLAP:
        state.pending_collapse = True
        state.collapse_timer = random.uniform(0.30, 0.60)
        return

    t = (ratio - CRITICAL_OVERLAP) / (STABLE_OVERLAP - CRITICAL_OVERLAP)  # 0~1
    survive_prob = 0.25 + 0.65 * t  # 0.25 ~ 0.90

    if random.random() < survive_prob:
        if landed_on is not None:
            slip = (1.0 - t) * random.uniform(-18, 18)
            cur.x = max(0, min(W - cur.w, cur.x + slip))

        cur.settled = True
        cur.falling = False
        state.stack.append(cur)
        state.height_score += 1
        spawn_block(state)
    else:
        state.pending_collapse = True
        state.collapse_timer = random.uniform(0.30, 0.60)


# ============================================================
# 4) 입력 / 업데이트 / 렌더
# ============================================================

def handle_events(state: GameState) -> Optional[str]:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                state.running = False
                return None

            if event.key == TOGGLE_WINDOW_MODE_KEY:
                return "toggle_window_mode"

            if state.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                reset_run(state)
                return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if state.game_over:
                    reset_run(state)
                return None

    return None

def update_game(state: GameState, dt: float) -> None:
    if state.game_over:
        return

    if state.pending_collapse:
        state.collapse_timer -= dt
        if state.collapse_timer <= 0:
            state.pending_collapse = False
            state.game_over = True
            state.best_score = max(state.best_score, state.height_score)
        return

    cur = state.current
    if cur is None:
        spawn_block(state)
        return

    if cur.falling:
        cur.y += FALL_SPEED * dt

        cur.wobble_phase += dt * 4.0
        cur.x += math.sin(cur.wobble_phase) * 0.35
        cur.x = max(0, min(W - cur.w, cur.x))

        land_y = top_surface_y(state) - cur.h
        if cur.y >= land_y:
            cur.y = land_y

            landed_on = None
            if state.stack:
                top_y = top_surface_y(state)
                candidates = [b for b in state.stack if abs(b.y - top_y) < 0.1]
                if candidates:
                    cur_cx = cur.x + cur.w / 2
                    landed_on = min(candidates, key=lambda b: abs((b.x + b.w / 2) - cur_cx))

            judge_settle(state, landed_on)

def compute_target_cam_y(state: GameState) -> float:
    """
    cam_y는 '월드에서 화면으로 그릴 때 빼는 값'임.
    기본은 0(바닥이 아래에 있음).
    탑이 화면 위쪽(CAMERA_TOP_MARGIN)까지 올라왔을 때만
    cam_y를 '음수'로 내려서(= 화면에서 아래로 밀어서) 따라가게 한다.
    """
    # ✅ 스택이 없으면 카메라 움직이면 안 됨 (시작 화면 고정)
    if not state.stack:
        return 0.0

    # ✅ 탑(가장 위 블록)의 y
    top_y = min(b.y for b in state.stack)

    # ✅ 탑이 아직 충분히 낮으면 카메라 필요 없음
    # (cam_y=0이면 top_y가 그대로 화면 y가 됨)
    if top_y >= CAMERA_TOP_MARGIN:
        return 0.0

    # ✅ 탑이 위쪽으로 올라가면 cam_y를 '음수'로 만들어서
    # (world_y - cam_y)에서 -(-값) => 아래로 내려오게 함
    return float(top_y - CAMERA_TOP_MARGIN)


def draw_game(screen: pygame.Surface, font: pygame.font.Font, state: GameState, cam_y: float) -> None:
    screen.fill(BG_COLOR)

    floor_screen_y = FLOOR_Y - cam_y
    fy = int(floor_screen_y)
    pygame.draw.rect(screen, FLOOR_COLOR, pygame.Rect(0, fy, W, H - fy))

    for b in state.stack:
        r = pygame.Rect(int(b.x), int(b.y - cam_y), int(b.w), int(b.h))
        pygame.draw.rect(screen, b.color, r, border_radius=8)

    if state.current:
        c = state.current
        r = pygame.Rect(int(c.x), int(c.y - cam_y), int(c.w), int(c.h))
        pygame.draw.rect(screen, c.color, r, border_radius=8)

    ui_text = f"HEIGHT: {state.height_score}     BEST: {state.best_score}"
    img = font.render(ui_text, True, TEXT_COLOR)
    screen.blit(img, (18, 16))

    if state.pending_collapse:
        warn = font.render("...uh oh...", True, TEXT_COLOR)
        screen.blit(warn, (18, 46))

    if state.game_over:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        screen.blit(overlay, (0, 0))

        t1 = font.render(f"HEIGHT: {state.height_score}", True, TEXT_COLOR)
        t2 = font.render("ONE MORE?  (click / space)", True, TEXT_COLOR)

        screen.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 40))
        screen.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 + 10))


# ============================================================
# 5) 창 모드 생성: 보더리스 최대화 vs 일반 창
# ============================================================

def get_desktop_size() -> Tuple[int, int]:
    info = pygame.display.Info()
    return int(info.current_w), int(info.current_h)

def create_screen(borderless_max: bool) -> pygame.Surface:
    """
    ✅ borderless_max=True:
       - FULLSCREEN 아님
       - NOFRAME로 테두리 제거
       - 데스크탑 크기로 창을 만들어 '창모드 최대화처럼' 보이게 함
    """
    if borderless_max:
        dw, dh = get_desktop_size()
        return pygame.display.set_mode((dw, dh), pygame.NOFRAME)
    return pygame.display.set_mode((WINDOW_W, WINDOW_H))


# ============================================================
# 6) 엔트리
# ============================================================

def main() -> None:
    global W, H, FLOOR_Y

    pygame.init()
    pygame.display.set_caption("ONE MORE BLOCK")

    borderless_max = START_BORDERLESS_MAX
    screen = create_screen(borderless_max)

    W, H = screen.get_size()
    FLOOR_Y = H - FLOOR_MARGIN

    font = pygame.font.SysFont("consolas", 24)
    clock = pygame.time.Clock()

    state = GameState()
    reset_run(state)

    cam_y = 0.0

    while state.running:
        dt = clock.tick(FPS) / 1000.0

        cmd = handle_events(state)

        if cmd == "toggle_window_mode":
            borderless_max = not borderless_max
            screen = create_screen(borderless_max)
            W, H = screen.get_size()
            FLOOR_Y = H - FLOOR_MARGIN

        update_game(state, dt)

        target_cam = compute_target_cam_y(state)
        cam_y += (target_cam - cam_y) * min(1.0, CAMERA_SMOOTH * dt)

        draw_game(screen, font, state, cam_y)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

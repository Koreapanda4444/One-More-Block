from __future__ import annotations

"""
input_handler.py

입력 처리 전담.
- main.py에서 이벤트를 직접 처리하면 루프가 지저분해지므로 분리.
- 이 함수는 "상태 변경"과 "명령 문자열 반환"만 담당한다.

중요 포인트:
- drop 전환 순간에 current._orig_x / _orig_w 저장
  -> 트림 후 shard(잘린 조각) 위치를 정확히 만들기 위해 "원본"이 필요함
"""

from typing import Optional
import pygame
from models import GameState


def handle_events(
    state: GameState,
    key_toggle_window_mode: int,
    key_drop: int,
    key_quit: int,
) -> Optional[str]:
    """
    pygame 이벤트를 모두 소모하고, 필요하면 명령 문자열을 반환한다.

    반환 가능한 명령:
    - "toggle_window_mode": F11
    - "restart": 게임오버 상태에서 재시작
    - None: 아무 것도 없음
    """
    for event in pygame.event.get():
        # 창 닫기 버튼
        if event.type == pygame.QUIT:
            state.running = False
            return None

        # 키 입력
        if event.type == pygame.KEYDOWN:
            # 종료
            if event.key == key_quit:
                state.running = False
                return None

            # 창 모드 토글(F11)
            if event.key == key_toggle_window_mode:
                return "toggle_window_mode"

            # 게임오버 상태에서 재시작(스페이스/엔터)
            if state.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                return "restart"

            # 게임 진행 중: drop
            if (not state.game_over) and event.key == key_drop:
                if state.current and state.current.phase == "move":
                    # ✅ shard 생성에 필요한 원본 정보 저장
                    state.current._orig_x = state.current.x
                    state.current._orig_w = state.current.w
                    state.current.phase = "drop"
                return None

        # 마우스 입력
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 좌클릭만 사용
            if event.button == 1:
                if state.game_over:
                    return "restart"

                if state.current and state.current.phase == "move":
                    # ✅ shard 생성에 필요한 원본 정보 저장
                    state.current._orig_x = state.current.x
                    state.current._orig_w = state.current.w
                    state.current.phase = "drop"
                return None

    return None

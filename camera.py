from __future__ import annotations

"""
camera.py

카메라 목표 y를 계산하는 파일.
- 블록이 위로 쌓일수록 화면도 같이 위로 올라가야 한다.
- '렌더링에서만 cam_y를 빼서' 월드 좌표는 그대로 두는 방식.
"""

from models import GameState


def compute_target_cam_y(state: GameState, camera_top_margin: int) -> float:
    """
    카메라가 따라가야 하는 목표 cam_y를 계산한다.

    규칙:
    - 스택의 가장 위(top_y)가 화면 상단에서 camera_top_margin 이상 아래에 있으면 cam_y=0 유지
    - top_y가 더 위로 올라가면(cam_y를 증가시켜) 화면이 따라 올라가도록

    cam_y는 "월드 좌표를 화면 좌표로 변환"할 때
    y_screen = y_world - cam_y 로 쓰인다.
    """
    if not state.stack:
        return 0.0

    top_y = min(b.y for b in state.stack)

    # top_y가 충분히 아래면 카메라는 움직이지 않는다.
    if top_y >= camera_top_margin:
        return 0.0

    # top_y가 더 위로 올라갈수록 cam_y도 같이 올라간다.
    return float(top_y - camera_top_margin)

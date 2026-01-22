from __future__ import annotations

from models import GameState

def compute_target_cam_y(state: GameState, camera_top_margin: int) -> float:
    if not state.stack:
        return 0.0

    top_y = min(b.y for b in state.stack)

    if top_y >= camera_top_margin:
        return 0.0

    return float(top_y - camera_top_margin)

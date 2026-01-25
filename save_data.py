from __future__ import annotations
import json
from pathlib import Path
from typing import Set, Tuple


def _save_path() -> Path:
    return Path(__file__).resolve().parent / "save.json"


def load_profile() -> Tuple[int, Set[str], float, bool]:
    """
    반환:
    - best (int)
    - unlocked achievements (set[str])
    - volume (float 0~1)
    - muted (bool)
    """
    p = _save_path()
    try:
        if not p.exists():
            return 0, set(), 0.70, False

        data = json.loads(p.read_text(encoding="utf-8"))

        best = int(data.get("best", 0))

        ach_list = data.get("achievements", [])
        if not isinstance(ach_list, list):
            ach_list = []
        unlocked = {str(x) for x in ach_list}

        vol = float(data.get("volume", 0.70))
        vol = 0.0 if vol < 0.0 else 1.0 if vol > 1.0 else vol

        muted = bool(data.get("muted", False))

        return max(0, best), unlocked, vol, muted
    except Exception:
        return 0, set(), 0.70, False


def save_profile(best: int, unlocked: Set[str], volume: float, muted: bool) -> None:
    p = _save_path()
    try:
        vol = float(volume)
        vol = 0.0 if vol < 0.0 else 1.0 if vol > 1.0 else vol
        payload = {
            "best": int(best),
            "achievements": sorted(list(unlocked)),
            "volume": vol,
            "muted": bool(muted),
        }
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def load_best() -> int:
    best, _, _, _ = load_profile()
    return best


def save_best(best: int) -> None:
    _, unlocked, vol, muted = load_profile()
    save_profile(best, unlocked, vol, muted)

from __future__ import annotations

"""
save_data.py

save.json에 BEST + 업적 언락 상태 저장.
"""

import json
from pathlib import Path
from typing import Set, Tuple


def _save_path() -> Path:
    return Path(__file__).resolve().parent / "save.json"


def load_profile() -> Tuple[int, Set[str]]:
    p = _save_path()
    try:
        if not p.exists():
            return 0, set()

        data = json.loads(p.read_text(encoding="utf-8"))
        best = int(data.get("best", 0))
        ach_list = data.get("achievements", [])
        if not isinstance(ach_list, list):
            ach_list = []

        unlocked = {str(x) for x in ach_list}
        return max(0, best), unlocked
    except Exception:
        return 0, set()


def save_profile(best: int, unlocked: Set[str]) -> None:
    p = _save_path()
    try:
        payload = {
            "best": int(best),
            "achievements": sorted(list(unlocked)),
        }
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


# ---- (호환용) 기존 함수 이름 유지 ----
def load_best() -> int:
    best, _ = load_profile()
    return best


def save_best(best: int) -> None:
    _, unlocked = load_profile()
    save_profile(best, unlocked)

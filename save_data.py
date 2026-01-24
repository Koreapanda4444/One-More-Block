from __future__ import annotations

import json
from pathlib import Path


def _save_path() -> Path:
    return Path(__file__).resolve().parent / "save.json"


def load_best() -> int:
    p = _save_path()
    try:
        if not p.exists():
            return 0
        data = json.loads(p.read_text(encoding="utf-8"))
        best = int(data.get("best", 0))
        return max(0, best)
    except Exception:
        return 0


def save_best(best: int) -> None:
    p = _save_path()
    try:
        payload = {"best": int(best)}
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

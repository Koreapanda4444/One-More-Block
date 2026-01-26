from __future__ import annotations

"""save_data.py

save_data.json 하나에 통합 저장.

- best
- bgm_on, bgm_volume
- selected_theme, unlocked_themes
- lifetime_perfect
- runs (최근 30개)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

SAVE_PATH = Path("save_data.json")


def _safe_read() -> Dict[str, Any]:
    try:
        if not SAVE_PATH.exists():
            return {}
        data = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _safe_write(data: Dict[str, Any]) -> None:
    try:
        SAVE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def load_best(default: int = 0) -> int:
    data = _safe_read()
    try:
        return int(data.get("best", default))
    except Exception:
        return int(default)


def save_best(best: int) -> None:
    data = _safe_read()
    data["best"] = int(best)
    _safe_write(data)


def load_bgm_settings(default_on: bool, default_volume: float) -> Tuple[bool, float]:
    data = _safe_read()
    on = bool(data.get("bgm_on", default_on))
    try:
        vol = float(data.get("bgm_volume", default_volume))
    except Exception:
        vol = float(default_volume)
    vol = 0.0 if vol < 0.0 else 1.0 if vol > 1.0 else vol
    return on, vol


def save_bgm_settings(on: bool, volume: float) -> None:
    data = _safe_read()
    data["bgm_on"] = bool(on)
    v = float(volume)
    v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
    data["bgm_volume"] = v
    _safe_write(data)


def load_theme_settings(default_selected: str = "sky") -> Tuple[str, List[str]]:
    data = _safe_read()
    selected = str(data.get("selected_theme", default_selected))
    unlocked = data.get("unlocked_themes", ["sky"])
    if not isinstance(unlocked, list):
        unlocked = ["sky"]
    if "sky" not in unlocked:
        unlocked.insert(0, "sky")
    return selected, unlocked


def save_theme_settings(selected: str, unlocked: List[str]) -> None:
    data = _safe_read()
    data["selected_theme"] = str(selected)

    u: List[str] = []
    for k in unlocked:
        if k not in u:
            u.append(k)
    if "sky" not in u:
        u.insert(0, "sky")

    data["unlocked_themes"] = u
    _safe_write(data)


def load_lifetime_perfect(default: int = 0) -> int:
    data = _safe_read()
    try:
        return int(data.get("lifetime_perfect", default))
    except Exception:
        return int(default)


def save_lifetime_perfect(v: int) -> None:
    data = _safe_read()
    data["lifetime_perfect"] = int(max(0, v))
    _safe_write(data)


def load_runs() -> List[Dict[str, Any]]:
    data = _safe_read()
    runs = data.get("runs", [])
    return runs if isinstance(runs, list) else []


def append_run(record: Dict[str, Any], limit: int = 30) -> None:
    data = _safe_read()
    runs = data.get("runs", [])
    if not isinstance(runs, list):
        runs = []
    runs.insert(0, record)
    runs = runs[: max(1, int(limit))]
    data["runs"] = runs
    _safe_write(data)

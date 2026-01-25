"""save_data.py

간단한 저장/로드.

저장 대상
- BEST(최고 높이)
- BGM 설정(on/off, volume)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple


SAVE_PATH = Path("save_data.json")


def _safe_read_json() -> Dict[str, Any]:
    """저장 파일을 읽는다. 실패하면 빈 dict 반환."""
    try:
        if not SAVE_PATH.exists():
            return {}
        with SAVE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _safe_write_json(data: Dict[str, Any]) -> None:
    """저장 파일을 쓴다(실패해도 게임이 죽지 않게)."""
    try:
        with SAVE_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_best(default: int = 0) -> int:
    """BEST 로드."""
    data = _safe_read_json()
    try:
        return int(data.get("best", default))
    except Exception:
        return int(default)


def save_best(best: int) -> None:
    """BEST 저장."""
    data = _safe_read_json()
    data["best"] = int(best)
    _safe_write_json(data)


def load_bgm_settings(default_on: bool, default_volume: float) -> Tuple[bool, float]:
    """BGM 설정(on/off + volume) 로드."""
    data = _safe_read_json()

    on = bool(data.get("bgm_on", default_on))
    try:
        vol = float(data.get("bgm_volume", default_volume))
    except Exception:
        vol = float(default_volume)

    if vol < 0.0:
        vol = 0.0
    if vol > 1.0:
        vol = 1.0

    return on, vol


def save_bgm_settings(on: bool, volume: float) -> None:
    """BGM 설정 저장."""
    data = _safe_read_json()
    data["bgm_on"] = bool(on)
    data["bgm_volume"] = float(volume)
    _safe_write_json(data)

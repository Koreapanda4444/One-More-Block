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
        # ✅ 다른 설정 키(bgm 등)가 생겨도 덮어쓰면서 날리지 않도록
        payload = {}
        if p.exists():
            try:
                payload = json.loads(p.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    payload = {}
            except Exception:
                payload = {}

        payload["best"] = int(best)
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def load_bgm_settings(default_on: bool = True, default_volume: float = 0.25) -> tuple[bool, float]:
    """save.json에서 BGM 설정 로드.

    과거 버전(save.json에 best만 있던 버전)도 자연스럽게 호환.
    """
    p = _save_path()
    try:
        if not p.exists():
            return bool(default_on), float(default_volume)
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return bool(default_on), float(default_volume)

        on = bool(data.get("bgm_on", default_on))
        vol = float(data.get("bgm_volume", default_volume))
        vol = 0.0 if vol < 0.0 else 1.0 if vol > 1.0 else vol
        return on, vol
    except Exception:
        return bool(default_on), float(default_volume)


def save_bgm_settings(bgm_on: bool, bgm_volume: float) -> None:
    """save.json에 BGM 설정 저장(다른 키 유지)."""
    p = _save_path()
    try:
        payload = {}
        if p.exists():
            try:
                payload = json.loads(p.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    payload = {}
            except Exception:
                payload = {}

        payload["bgm_on"] = bool(bgm_on)
        v = float(bgm_volume)
        v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
        payload["bgm_volume"] = v
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

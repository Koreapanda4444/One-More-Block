from __future__ import annotations

"""audio_sfx.py

(2) PERFECT 클릭 SFX (외부 파일 없이 생성)
"""

import math
from array import array
from dataclasses import dataclass
from typing import Optional
import pygame


def _clamp(x: float, a: float, b: float) -> float:
    return a if x < a else b if x > b else x


def build_click_sfx(sr: int = 44100, dur: float = 0.06) -> bytes:
    n = max(1, int(sr * dur))
    out = array("h")

    for i in range(n):
        t = i / sr
        env = math.exp(-t * 45.0)
        s = math.sin(2.0 * math.pi * 1200.0 * t) * env
        s += math.sin(2.0 * math.pi * 2400.0 * t) * env * 0.35
        s += math.sin(2.0 * math.pi * 8000.0 * t) * env * 0.06
        out.append(int(_clamp(s, -1.0, 1.0) * 32767 * 0.55))

    return out.tobytes()


@dataclass
class SfxPlayer:
    enabled: bool = False
    volume: float = 0.45

    _sound_click: Optional[pygame.mixer.Sound] = None
    _ch: Optional[pygame.mixer.Channel] = None

    def init(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 1, 512)
            pygame.mixer.set_num_channels(8)
        except Exception:
            self.enabled = False
            return

        self.enabled = True
        self._ch = pygame.mixer.Channel(1)

        try:
            self._sound_click = pygame.mixer.Sound(buffer=build_click_sfx())
        except Exception:
            self._sound_click = None
            self.enabled = False
            return

        self.apply()

    def apply(self) -> None:
        if not self.enabled or self._ch is None:
            return
        try:
            self._ch.set_volume(_clamp(self.volume, 0.0, 1.0))
        except Exception:
            pass

    def play_click(self) -> None:
        if not self.enabled or self._ch is None or self._sound_click is None:
            return
        try:
            self._ch.play(self._sound_click)
        except Exception:
            pass

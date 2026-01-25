from __future__ import annotations

import math
from array import array
from dataclasses import dataclass
from typing import Dict, Optional

import pygame


def _clamp(x: float, a: float, b: float) -> float:
    return a if x < a else b if x > b else x


def _make_tone(
    freq: float,
    sec: float,
    volume: float,
    sr: int = 44100,
    fade: float = 0.015,
) -> bytes:
    """
    간단한 사인파 톤 생성(16-bit mono).
    - fade in/out을 넣어 '뚝' 끊기는 클릭 잡음 완화
    """
    sec = max(0.0, float(sec))
    n = max(1, int(sr * sec))
    vol = _clamp(float(volume), 0.0, 1.0)

    fade_n = int(sr * float(fade))
    if fade_n * 2 > n:
        fade_n = n // 2

    buf = array("h")
    amp = int(32767 * vol)

    for i in range(n):
        t = i / sr
        s = math.sin(2.0 * math.pi * float(freq) * t)

        # simple fade in/out
        if fade_n > 0:
            if i < fade_n:
                s *= (i / fade_n)
            elif i > n - fade_n:
                s *= ((n - i) / fade_n)

        buf.append(int(amp * s))

    return buf.tobytes()


def _concat(*chunks: bytes) -> bytes:
    return b"".join(chunks)


@dataclass
class AudioManager:
    """
    - enabled: mixer 초기화 성공 여부
    - master_volume: 0.0~1.0
    - muted: True면 완전 무음
    """
    enabled: bool = False
    master_volume: float = 0.7
    muted: bool = False
    sounds: Dict[str, pygame.mixer.Sound] = None

    def init(self) -> None:
        # mixer가 아직이면 최대한 지연 줄이려고 pre_init 느낌으로 맞춤
        try:
            if not pygame.mixer.get_init():
                # (freq=44100, size=-16, channels=1, buffer=512)
                pygame.mixer.init(44100, -16, 1, 512)
        except Exception:
            self.enabled = False
            self.sounds = {}
            return

        self.enabled = True
        self.sounds = {}

        # SFX 생성 (톤 조합)
        # drop: 짧은 저음 클릭 느낌
        drop = _concat(
            _make_tone(160, 0.025, 0.55),
            _make_tone(240, 0.020, 0.40),
        )
        # land: 좀 더 둔탁
        land = _concat(
            _make_tone(110, 0.060, 0.70),
            _make_tone(180, 0.040, 0.40),
        )
        # perfect: 밝은 2연타
        perfect = _concat(
            _make_tone(660, 0.050, 0.60),
            _make_tone(880, 0.060, 0.60),
        )
        # gameover: 내려가는 느낌
        gameover = _concat(
            _make_tone(220, 0.090, 0.60),
            _make_tone(140, 0.120, 0.60),
        )

        self.sounds["drop"] = pygame.mixer.Sound(buffer=drop)
        self.sounds["land"] = pygame.mixer.Sound(buffer=land)
        self.sounds["perfect"] = pygame.mixer.Sound(buffer=perfect)
        self.sounds["gameover"] = pygame.mixer.Sound(buffer=gameover)

        self.apply_volume()

    def apply_volume(self) -> None:
        if not self.enabled or not self.sounds:
            return
        v = 0.0 if self.muted else _clamp(self.master_volume, 0.0, 1.0)

        # 사운드별 밸런스(귀 아프지 않게)
        self.sounds["drop"].set_volume(v * 0.35)
        self.sounds["land"].set_volume(v * 0.55)
        self.sounds["perfect"].set_volume(v * 0.70)
        self.sounds["gameover"].set_volume(v * 0.65)

    def set_volume(self, v: float) -> None:
        self.master_volume = _clamp(float(v), 0.0, 1.0)
        self.apply_volume()

    def add_volume(self, delta: float) -> None:
        self.set_volume(self.master_volume + float(delta))

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        self.apply_volume()

    def play(self, name: str) -> None:
        if not self.enabled or self.muted:
            return
        s = self.sounds.get(name) if self.sounds else None
        if s is None:
            return
        try:
            s.play()
        except Exception:
            # 혹시라도 play 실패해도 게임은 계속
            pass

from __future__ import annotations

"""audio.py

Commit 11: BGM 루프(외부 파일 없이, 코드에서 톤으로 생성)

목표
- 배포할 때 wav/mp3 같은 외부 리소스 없이도 "배경음"이 돌아가게 만들기
- pygame.mixer가 실패하는 환경에서도(드라이버/권한 문제) 게임이 죽지 않게 안전 처리

구성
- BgmPlayer: init()로 mixer 초기화 + 루프 사운드 생성
- start()/stop()/toggle()로 재생 제어
- set_volume()로 0.0~1.0 볼륨 적용
"""

import math
from array import array
from dataclasses import dataclass
from typing import Optional

import pygame


def _clamp(x: float, a: float, b: float) -> float:
    return a if x < a else b if x > b else x


def _sine(freq: float, t: float) -> float:
    return math.sin(2.0 * math.pi * freq * t)


def _make_step(
    freqs: list[float],
    sec: float,
    sr: int,
    gain: float,
    fade: float = 0.020,
) -> list[int]:
    """한 스텝(짧은 구간) 샘플을 만든다."""
    n = max(1, int(sr * sec))
    fade_n = int(sr * fade)
    if fade_n * 2 > n:
        fade_n = n // 2

    mix_div = max(1, len(freqs))
    out: list[int] = []
    amp = int(32767 * _clamp(gain, 0.0, 1.0))

    for i in range(n):
        t = i / sr
        s = 0.0
        for f in freqs:
            s += _sine(f, t) * 0.75
            s += _sine(f * 2.0, t) * 0.25
        s /= mix_div

        if fade_n > 0:
            if i < fade_n:
                s *= (i / fade_n)
            elif i > n - fade_n:
                s *= ((n - i) / fade_n)

        out.append(int(amp * s))

    return out


def _hz(note: str) -> float:
    """간단한 음이름 -> 주파수 (A4=440 기준)"""
    note = note.strip().upper()
    names = {
        "C": 0, "C#": 1, "DB": 1,
        "D": 2, "D#": 3, "EB": 3,
        "E": 4,
        "F": 5, "F#": 6, "GB": 6,
        "G": 7, "G#": 8, "AB": 8,
        "A": 9, "A#": 10, "BB": 10,
        "B": 11,
    }
    if len(note) < 2:
        return 440.0
    if note[1] in ("#", "B"):
        pitch = note[:2]
        octv = note[2:]
    else:
        pitch = note[:1]
        octv = note[1:]

    sem = names.get(pitch, 9)
    try:
        octave = int(octv)
    except Exception:
        octave = 4

    midi = (octave + 1) * 12 + sem
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def build_bgm_loop(sr: int = 44100) -> bytes:
    """BGM 루프 버퍼(16-bit mono) 생성."""
    chords = [
        ["C4", "E4", "G4", "B4"],
        ["A3", "C4", "E4", "G4"],
        ["F3", "A3", "C4", "E4"],
        ["G3", "C4", "D4", "G4"],
    ]

    step_sec = 0.25
    arp = [0, 2, 1, 2, 3, 2, 1, 2]

    samples: list[int] = []
    for chord in chords:
        hz = [_hz(n) for n in chord]
        for idx in arp:
            root = hz[idx]
            freqs = [root, root / 2.0]
            step = _make_step(freqs=freqs, sec=step_sec, sr=sr, gain=0.22)
            samples.extend(step)

    buf = array("h", samples)
    return buf.tobytes()


@dataclass
class BgmPlayer:
    """게임 전체에서 계속 도는 BGM 플레이어."""
    enabled: bool = False
    on: bool = True
    volume: float = 0.25

    _sound: Optional[pygame.mixer.Sound] = None
    _channel: Optional[pygame.mixer.Channel] = None

    def init(self) -> None:
        """mixer 초기화 + 루프 사운드 생성."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 1, 512)
            pygame.mixer.set_num_channels(8)
            try:
                pygame.mixer.set_reserved(1)
            except Exception:
                pass
        except Exception:
            self.enabled = False
            self._sound = None
            self._channel = None
            return

        self.enabled = True
        self._channel = pygame.mixer.Channel(0)

        try:
            loop_bytes = build_bgm_loop(sr=44100)
            self._sound = pygame.mixer.Sound(buffer=loop_bytes)
        except Exception:
            self._sound = None
            self.enabled = False
            return

        self.apply()

    def apply(self) -> None:
        """현재 on/volume 상태를 실제 재생에 반영."""
        if not self.enabled or self._sound is None or self._channel is None:
            return

        v = _clamp(self.volume, 0.0, 1.0)
        if not self.on:
            v = 0.0

        try:
            self._channel.set_volume(v)
        except Exception:
            pass

        try:
            if self.on and (not self._channel.get_busy()):
                self._channel.play(self._sound, loops=-1)
        except Exception:
            pass

        if not self.on:
            try:
                self._channel.stop()
            except Exception:
                pass

    def start(self) -> None:
        self.on = True
        self.apply()

    def stop(self) -> None:
        self.on = False
        self.apply()

    def toggle(self) -> bool:
        self.on = not self.on
        self.apply()
        return self.on

    def set_volume(self, v: float) -> None:
        self.volume = _clamp(float(v), 0.0, 1.0)
        self.apply()

    def add_volume(self, delta: float) -> None:
        self.set_volume(self.volume + float(delta))

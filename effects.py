from __future__ import annotations

"""effects.py

(2) 손맛:
- PERFECT 순간 카메라 흔들림 + 파티클
"""

import random
from typing import Tuple
from models import GameState, Particle

SHAKE_DURATION = 0.12
SHAKE_STRENGTH = 10.0

PARTICLE_COUNT = (14, 22)
PARTICLE_LIFE = (0.18, 0.35)
PARTICLE_SIZE = (3, 6)
PARTICLE_SPEED_X = (-180, 180)
PARTICLE_SPEED_Y = (-420, -160)
PARTICLE_GRAVITY = 1100.0


def trigger_perfect(state: GameState, x: float, y: float, color: Tuple[int, int, int]) -> None:
    state.shake_timer = SHAKE_DURATION
    state.shake_duration = SHAKE_DURATION
    state.shake_strength = SHAKE_STRENGTH

    n = random.randint(PARTICLE_COUNT[0], PARTICLE_COUNT[1])
    for _ in range(n):
        size = random.randint(PARTICLE_SIZE[0], PARTICLE_SIZE[1])
        life = random.uniform(PARTICLE_LIFE[0], PARTICLE_LIFE[1])

        vx = random.uniform(PARTICLE_SPEED_X[0], PARTICLE_SPEED_X[1])
        vy = random.uniform(PARTICLE_SPEED_Y[0], PARTICLE_SPEED_Y[1])

        px = x + random.uniform(-18, 18)
        py = y + random.uniform(-8, 8)

        state.particles.append(
            Particle(x=px, y=py, vx=vx, vy=vy, size=size, color=color, life=life, age=0.0)
        )


def update_effects(state: GameState, dt: float) -> float:
    # 파티클 업데이트
    for p in state.particles[:]:
        p.age += dt
        if p.age >= p.life:
            state.particles.remove(p)
            continue

        p.vy += PARTICLE_GRAVITY * dt
        p.x += p.vx * dt
        p.y += p.vy * dt

    # 쉐이크 오프셋 반환
    if state.shake_timer > 0.0:
        state.shake_timer = max(0.0, state.shake_timer - dt)
        t = state.shake_timer / max(0.0001, state.shake_duration)
        amp = state.shake_strength * t
        return random.uniform(-amp, amp)

    return 0.0

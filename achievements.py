from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple, Any, List


# 진행도(progress) 표기용 타입: (현재값, 목표값)
Progress = Tuple[int, int]


@dataclass(frozen=True)
class Achievement:
    """
    - id: 저장용 고유 식별자 (절대 바꾸지 않는 것을 권장)
    - title/desc: 화면 표시용
    - condition(state): True가 되면 언락
    - progress(state): (current, goal)로 "진행도 표시"가 필요한 업적만 제공
    """
    id: str
    title: str
    desc: str
    condition: Callable[[Any], bool]
    progress: Optional[Callable[[Any], Progress]] = None


def _p_height(goal: int) -> Callable[[Any], Progress]:
    return lambda s: (int(getattr(s, "score", 0)), goal)


def _p_best(goal: int) -> Callable[[Any], Progress]:
    return lambda s: (int(getattr(s, "best", 0)), goal)


def _p_combo(goal: int) -> Callable[[Any], Progress]:
    return lambda s: (int(getattr(s, "run_max_combo", 0)), goal)


def _p_perfect(goal: int) -> Callable[[Any], Progress]:
    return lambda s: (int(getattr(s, "run_perfects", 0)), goal)


def _p_shards(goal: int) -> Callable[[Any], Progress]:
    return lambda s: (int(getattr(s, "run_shards_created", 0)), goal)


def _p_narrow_streak(goal: int) -> Callable[[Any], Progress]:
    return lambda s: (int(getattr(s, "run_narrow_streak", 0)), goal)


# =========================
# 업적 목록 (10개)
# =========================
ALL: List[Achievement] = [
    Achievement(
        id="height_5",
        title="Rookie Builder",
        desc="HEIGHT 5 달성",
        condition=lambda s: getattr(s, "score", 0) >= 5,
        progress=_p_height(5),
    ),
    Achievement(
        id="height_15",
        title="Getting Warm",
        desc="HEIGHT 15 달성",
        condition=lambda s: getattr(s, "score", 0) >= 15,
        progress=_p_height(15),
    ),
    Achievement(
        id="height_30",
        title="Skyline",
        desc="HEIGHT 30 달성",
        condition=lambda s: getattr(s, "score", 0) >= 30,
        progress=_p_height(30),
    ),
    Achievement(
        id="perfect_1",
        title="First Perfect!",
        desc="PERFECT 1회 성공",
        condition=lambda s: getattr(s, "run_perfects", 0) >= 1,
        progress=_p_perfect(1),
    ),
    Achievement(
        id="perfect_8",
        title="Precision Mode",
        desc="한 런에서 PERFECT 8회",
        condition=lambda s: getattr(s, "run_perfects", 0) >= 8,
        progress=_p_perfect(8),
    ),
    Achievement(
        id="combo_3",
        title="Combo Starter",
        desc="콤보 3 달성",
        condition=lambda s: getattr(s, "run_max_combo", 0) >= 3,
        progress=_p_combo(3),
    ),
    Achievement(
        id="combo_7",
        title="Combo Machine",
        desc="콤보 7 달성",
        condition=lambda s: getattr(s, "run_max_combo", 0) >= 7,
        progress=_p_combo(7),
    ),
    Achievement(
        id="shards_20",
        title="Carpenter",
        desc="한 런에서 조각 20개 생성",
        condition=lambda s: getattr(s, "run_shards_created", 0) >= 20,
        progress=_p_shards(20),
    ),
    Achievement(
        id="shards_60",
        title="Sawblade",
        desc="한 런에서 조각 60개 생성",
        condition=lambda s: getattr(s, "run_shards_created", 0) >= 60,
        progress=_p_shards(60),
    ),
    Achievement(
        id="narrow_3",
        title="Thread the Needle",
        desc="폭 80px 이하 블록을 3연속 성공",
        condition=lambda s: getattr(s, "run_narrow_streak", 0) >= 3,
        progress=_p_narrow_streak(3),
    ),
    # 10개 맞추려고 하나 더: BEST 기반(장기 목표)
    Achievement(
        id="best_50",
        title="Legend",
        desc="BEST 50 달성",
        condition=lambda s: getattr(s, "best", 0) >= 50,
        progress=_p_best(50),
    ),
]


def unlock_new(state: Any) -> List[Achievement]:
    """
    아직 언락되지 않은 업적들 중, 조건을 만족한 것들을 언락한다.

    반환:
    - 새로 언락된 Achievement 리스트 (토스트/사운드 등에 사용)
    """
    unlocked = getattr(state, "unlocked_achievements", None)
    if unlocked is None:
        # state에 set이 없다면 방어적으로 만들기
        unlocked = set()
        state.unlocked_achievements = unlocked

    newly: List[Achievement] = []
    for a in ALL:
        if a.id in unlocked:
            continue
        try:
            if a.condition(state):
                unlocked.add(a.id)
                newly.append(a)
        except Exception:
            # 조건 함수가 실수로 터져도 게임이 죽으면 안 됨
            continue
    return newly


def get_by_id(ach_id: str) -> Optional[Achievement]:
    for a in ALL:
        if a.id == ach_id:
            return a
    return None

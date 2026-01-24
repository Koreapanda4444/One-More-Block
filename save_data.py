from __future__ import annotations

"""
BEST 기록 저장/불러오기 모듈.

핵심 목표:
- 게임을 껐다 켜도 BEST가 유지되게 만들기
- 저장/읽기 실패해도 게임이 죽지 않게(최악의 경우 BEST=0으로 진행)

저장 파일:
- 이 파일(save_data.py)과 같은 폴더에 save.json 생성
  (실행 위치가 어디든 경로가 꼬이지 않게 "파일 기준 경로" 사용)
"""

import json
from pathlib import Path


def _save_path() -> Path:
    """
    save.json의 절대 경로를 반환한다.

    Path(__file__).resolve().parent:
    - "현재 파일이 위치한 폴더"를 기준으로 경로를 잡는다.
    - 따라서 터미널에서 어디서 실행하든 저장 파일 위치가 안정적이다.
    """
    return Path(__file__).resolve().parent / "save.json"


def load_best() -> int:
    """
    save.json에서 best 값을 불러온다.

    반환:
    - 정상: 0 이상 정수
    - 예외/파일 없음/파싱 실패: 0

    주의:
    - 저장 파일이 깨져있을 수도 있으니 try/except로 안전하게 처리한다.
    """
    p = _save_path()
    try:
        if not p.exists():
            return 0

        # JSON 읽기
        data = json.loads(p.read_text(encoding="utf-8"))

        # best 없으면 0, 타입이 이상해도 int로 강제 변환 시도
        best = int(data.get("best", 0))
        return max(0, best)
    except Exception:
        # 저장 파일이 깨져있거나 권한 문제 등이 있어도 게임이 죽지 않게 한다
        return 0


def save_best(best: int) -> None:
    """
    best 값을 save.json에 저장한다.

    - 실패해도 게임 진행에 지장이 없게 예외를 먹는다.
    - ensure_ascii=False: 한글/유니코드 깨짐 방지(굳이 필요 없지만 습관적으로)
    - indent=2: 사람이 열어봤을 때 보기 좋게
    """
    p = _save_path()
    try:
        payload = {"best": int(best)}
        p.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        # 디스크 권한/경로/백신 등으로 실패할 수 있으니 조용히 무시
        pass

# ONE MORE BLOCK

`Pygame`으로 만든 **원 버튼 스태킹(Stacking) 게임**.

- **클릭/스페이스**로 타이밍 맞춰 블록을 떨어뜨리고
- 착지 시 **겹친 부분만 남는(트림)** 방식으로
- 점점 좁아지는 스택을 얼마나 높게 쌓는지 겨루는 게임

## Controls

- **Left Click / SPACE**: Drop
- **SPACE / ENTER** (Game Over): Restart
- **F11**: Window size toggle
  - `창모드 전체크기(windowed_max)` ↔ `작은 창(windowed)`
- **B**: BGM ON/OFF
- **[ / ]**: BGM volume down/up

## Save

실행 폴더에 `save_data.json`을 생성해 아래를 저장합니다.

- `best`: 최고 기록
- `bgm_on`, `bgm_volume`: 배경음 설정

## Run

```bash
pip install pygame
python main.py

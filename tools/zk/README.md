# zk — 구역 편집 도구 (scratchpad/zk 의 사본 · 2026-10-16)
세션이 바뀌면 scratchpad 가 사라지므로 저장소에 둔다. 쓸 때는 `python3 tools/zk/u_zone.py …` 처럼 부른다.

| 파일 | 하는 일 |
|---|---|
| u_zone.py | crop(2배 바탕에서 구역 조각) · compose(Gemini 결과를 띠 정합 → 차지 사각형만 깃털 합성) |
| compose_sky.py | 담장 위(하늘·바다)만 붙이기 — 아래 경계를 벽돌 꼭대기 선을 따라 딱 자름 (s32u01 v7 E7b) |
| draw_drops.py | 바다 빛 물방울(잉크 테두리·하이라이트)을 그려 넣기 (s32u01 v7 C7) |
| zcrop.py | 임의 사각형 조각(1배 좌표) + 올릴 배율 — `zcrop.py base2x.png NAME x0,y0,x1,y1 UP --out DIR --gem PATH` (2026-10-17) |
| zdiff.py | Gemini 결과와 조각의 차이 덩어리를 1배 전역 own 사각형으로 찍는다(2026-10-24 — 조각의 y0 를 더하도록 고침) |
| orbfit.py | 틀이 달라진 결과를 ORB 유사변환으로 올린 조각에 정합 (2026-10-17) |
| affit.py | 결과의 가로세로 비가 달라진 것(비등방 리프레임)을 비등방 리사이즈 + ORB 전체 아핀으로 정합 — 3.1 Pro 가 조각을 1024×765 처럼 돌려줄 때 (2026-10-24) |
| refit.py | 비율이 달라진 결과를 높이로 맞추고 가로 어긋남만 찾아 조각 크기로 되돌린다(빈 자리는 조각 화소) |
| zone_kit.py | 옛 9:16 구역 도구(u_zone 의 전신) |
| wm_fill.py · spark_local.py | 워터마크·반짝이 지우기(로컬) |
| tile_stitch*.py | 조각 이어 붙이기 |
| gemini_capture.js | Gemini 그림 받기 도우미(옛판) — 지금은 tools/gemini_helpers_0928.js |

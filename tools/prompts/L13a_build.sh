#!/bin/bash
# L13a_build.sh <작업 폴더> — L13a 그림을 Gemini 원본(L13a_src/)에서 다시 만든다(같은 픽셀).
#  바탕 그림이 없다 — 하늘 · 회색 돌 성벽 · 무너진 틈은 L13a_pil.py 가 그린다.
#  (2026-11-14 Gemini 의 그림 올리기 동의 창을 그때는 누르지 않아 그림을 올려 고치게 할 수 없었다 → 물건을 글만으로 그리게 해 오려 세웠다.)
#  A1(파리채 경비) · A2(초록 알약 세균 둘 · 보라 망토 두른 이) · A3(세균을 통째로 입에 넣은 흰 덩이 · 털모자 · 장화) · B1(톨게이트 초소 · 창 난 삼베 자루)
#  · B2(인터폰 단 작은 집) · C1(주민 셋 · 보에 막힌 도랑) · E1(봉화 바구니 · 무너진 돌덩이) · F1(망보는 궁수 · 꼬리 전단) · P1(밧줄 전단 · 두루마리 전단)
#  · TW(발코니에 벌과 병정 둘 · 문간에 잠옷 병정이 앉은 내성 탑) = 크림빛 민 바탕에 물건만 그린 조각 그림(프롬프트 L13a_prompt_sprites.txt).
#  조끼 단추 · 붉은 리본 배지 · 게시판 · 잠옷 병정의 종이 속 세균 · 가로대 늘이기 · 빛깔 손질은 L13a_pil.py 가 한다.
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
for n in ('A1', 'A2', 'A3', 'B1', 'B2', 'C1', 'E1', 'F1', 'P1', 'TW'): Image.open(f'{D}/L13a_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
python3 "$D/L13a_pil.py" "$W/z" "$W/final.png"
echo "→ $W/final.png"

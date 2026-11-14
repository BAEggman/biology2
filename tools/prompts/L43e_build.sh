#!/bin/bash
# L43e_build.sh <작업 폴더> — L43e 그림을 Gemini 원본(L43e_src/)에서 다시 만든다(같은 픽셀).
#  s1.webp = 바탕(밑그림 L43e_sketch.py · 프롬프트 L43e_prompt_sketch.txt) — 조립에는 담 띠만 쓴다.
#  Z1(큰 상자 파리) · Z2(루페 든 흰 가운 + 머리가 파랑인 파리) · Z3(생선 뼈 물고기 + 눈알 여섯 개들이 팩) · Z4(어미 파리 + 코 붙은 알 둘)
#  · Z5(보통 파리 둘 — 오른쪽 것만 쓴다) · Z6(알 넷 — 성한 알 하나 + 깨진 알) = 또렷하게 다시 그린 구역(프롬프트 L43e_prompt_edits.txt) — 물건을 오려 세우는 조각의 원본.
#  끈 · 끈에 꿴 상자 셋 · 화살 · 모든 다리 · 발치의 상자 짝 · 덧눈은 L43e_pil.py 가 그린다.
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
Image.open(f'{D}/L43e_src/s1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base.png')
for n in ('Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6'): Image.open(f'{D}/L43e_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
python3 "$D/L43e_pil.py" "$W/base.png" "$W/z" "$W/final.png"
echo "→ $W/final.png"

#!/bin/bash
# L12f_build.sh <작업 폴더> — L12f 그림을 바탕과 구역 편집 결과(L12f_src/)에서 다시 만든다 → <작업 폴더>/final.png
# 차례: 바탕 s2(1024x572) → 2048x1144 → pil0(덤 넷 지움) → E2(수반 위 두 사람) → E1(쌍둥이) → E3(불룩 휜 통 벽) → pil1(세는 것 · 약속 물건)
set -e
W="$1"; TP="$(cd "$(dirname "$0")" && pwd)"; S="$TP/L12f_src"; mkdir -p "$W/z"
python3 -I -c "
from PIL import Image
import sys
w, s = sys.argv[1], sys.argv[2]
Image.open(s + '/s2.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(w + '/base.png')
for n in ('E1', 'E2', 'E3'): Image.open(s + '/' + n + '.webp').convert('RGB').save(w + '/z/gem_' + n + '.png')
" "$W" "$S"
python3 "$TP/L12f_pil0.py" "$W/base.png" "$W/p0.png"
python3 "$TP/zone3.py" crop "$W/p0.png" "$W/z" E2 1150 120 1510 360
python3 "$TP/zone3.py" paste "$W/p0.png" "$W/z" E2 "$W/z/gem_E2.png" "$W/p1.png" "1228,122,1325,292;1362,178,1456,358"
python3 "$TP/zone3.py" crop "$W/p1.png" "$W/z" E1 1640 610 2030 870
python3 "$TP/zone3.py" paste "$W/p1.png" "$W/z" E1 "$W/z/gem_E1.png" "$W/p2.png" "1700,622,1996,864" --ident --R=40
python3 "$TP/zone3.py" crop "$W/p2.png" "$W/z" E3 850 540 1110 930
python3 "$TP/zone3.py" paste "$W/p2.png" "$W/z" E3 "$W/z/gem_E3.png" "$W/p2b.png" "860,562,1106,905" --fit="860,640,1106,905"
python3 "$TP/L12f_pil1.py" "$W/p2b.png" "$W/final.png"
echo "→ $W/final.png"

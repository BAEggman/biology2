#!/usr/bin/env python3
# L43f_pil2.py <in.png> <out.png> — L43f 끝손질 둘째(2026-11-15 · 일치 검사 3회 뒤).
#  선 일꾼 손이 사슬을 쥔 자리의 검은 손가락 먹선이 「사슬의 검은 구슬」로 읽혀(2 · 3회 — 검은 구슬이 둘)
#  그 자리에 사슬의 다른 구슬과 같은 하늘빛 구슬 하나를 그린다 → 검은 구슬은 공 속 하나뿐.
import sys
from PIL import Image, ImageDraw

BEADS = [(1781, 1043, 6)]                 # 가운데 x · y · 반지름(2048 × 1144)
FILL = (78, 128, 162); HL = (128, 168, 198); INK = (22, 20, 18)

def main(src, out):
    img = Image.open(src).convert('RGB'); K = 6
    for x, y, r in BEADS:
        x0, y0 = x - r - 3, y - r - 3; S = 2 * r + 7
        big = img.crop((x0, y0, x0 + S, y0 + S)).resize((S * K, S * K), Image.LANCZOS); d = ImageDraw.Draw(big)
        c = (x - x0) * K; R = r * K
        d.ellipse([c - R - 1.6 * K, c - R - 1.6 * K, c + R + 1.6 * K, c + R + 1.6 * K], fill=INK)
        d.ellipse([c - R, c - R, c + R, c + R], fill=FILL)
        d.ellipse([c - R * 0.55, c - R * 0.65, c - R * 0.05, c - R * 0.15], fill=HL)
        img.paste(big.resize((S, S), Image.LANCZOS), (x0, y0))
    img.save(out); print('→', out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

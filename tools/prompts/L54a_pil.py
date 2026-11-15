#!/usr/bin/env python3
# L54a_pil.py <in.png> <out.png> — L54a 마무리 PIL(2026-11-15 · Opus 5.5)
#  ① 먼지 — 아래 주석.  ② 물속 위쪽의 붉은 조각 하나 → 잿빛.
import sys
from PIL import Image, ImageDraw

# 일치 검사 1회 ✕ 「목 안에 먼지가 안 보인다」 · 2회 △ 「선 위의 점선」 · 3회 △ 「겉무늬인지 안쪽인지」 → 구역 편집 ZN 으로 목 · 머리를 비치는 유리로
#  → 4회 ✕ 「비치는 머리 안의 고운 먼지가 이 크기에선 안 읽힌다」 → 만화식 먼지 알갱이(잿빛 · 검은 테 · 들쭉날쭉한 꼴)를 PIL 로:
#   ① 유리 머리 안의 먼지 덩이 ② 부리 앞 공기 속을 떠도는 알갱이 몇 ③ 부러진 플라스크의 열린 목으로 떨어져 드는 알갱이 몇 — 「먼지(미생물)는 어디로 가나」가 한 사건으로.
#   흰 · 둥근 것은 덱의 O₂(흰 방울)라 피한다 — 잿빛 · 모난 꼴.
import math

IN_HEAD = [(522, 783, 3.2), (528, 787, 3.6), (534, 783, 2.8), (526, 793, 3.0), (532, 794, 2.6), (537, 789, 2.2)]
AIR = [(560, 800, 2.6), (568, 789, 2.2), (576, 806, 2.6), (566, 818, 2.0), (584, 794, 2.2)]
FALL = [(664, 822, 2.6), (679, 812, 2.2), (690, 829, 2.6), (673, 838, 2.2), (686, 846, 2.4)]


def speck(d, x, y, r, k):
    pts = []
    for i in range(7):
        a = 2 * math.pi * i / 7 + k
        rr = r * (0.75 + 0.35 * ((i * 37 + k * 11) % 5) / 4)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=(124, 118, 112), outline=(38, 34, 30))


def dust(a):
    d = ImageDraw.Draw(a)
    for k, (x, y, r) in enumerate(IN_HEAD + AIR + FALL):
        speck(d, x, y, r, k * 0.7)


def flake_grey(a, box=(1940, 770, 1972, 805)):
    # ② 일치 검사 3 · 4회 △ 「위쪽에도 붉은 조각이 하나」 — 물속 오른쪽 위의 붉은 조각 하나를 잿빛(아직 녹슬지 않은 쇳조각)으로.
    x0, y0, x1, y1 = box; px = a.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if r > g + 30 and r > b + 30:
                L = int(0.3 * r + 0.59 * g + 0.11 * b) + 25
                px[x, y] = (min(255, L), min(255, L - 3), min(255, L - 6))


def main(src, out):
    a = Image.open(src).convert('RGB')
    dust(a)
    flake_grey(a)
    a.save(out)


if __name__ == '__main__':
    main(*sys.argv[1:3])

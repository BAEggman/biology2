#!/usr/bin/env python3
"""touch_h2.py — s45u02 v7 ② 행 4: 꼬투리 무더기 머리를 겹마다 셋씩 **세 세로줄에 맞춰**(폭의 0.2 · 0.5 · 0.8 — 흔들림 없음 · 6.0 px) 다시 박는다.
가운데 오른쪽 무더기(MR)는 touch_h1 로 두 겹(머리 여섯) — 같은 줄의 TR(여섯 겹 · 열여덟) · LR(일곱 겹 · 스물하나)와 견준다.
(v3 ~ v6 은 줄마다 비껴 박아 「흩뿌린 점」으로 읽혔고 겹 수 · 머리 수를 서로 다르게 셌다 — b137)
사용: touch_h2.py in.png out.png"""
import sys, numpy as np
from PIL import Image, ImageDraw
src, dst = sys.argv[1:3]
img = Image.open(src).convert('RGB'); W, H = img.size
SS = 4
S = lambda x, y: (x * SS, y * SS)
STK = {  # 이름: (왼 x, 오른 x, [겹 앞면 가운데 y …]) — touch_f 의 눈금 잼 · MR 는 난쟁이(grid_dwarf.png)
    'TL': (630.0, 728.0, [323.5, 332.5, 342.0, 351.5, 361.5, 372.0]),
    'TR': (740.0, 802.0, [394.0, 403.0, 411.0, 419.0, 427.5, 436.0]),
    'ML': (586.0, 678.0, [434.5, 444.5, 453.0, 461.0, 470.5, 481.5]),
    'MR': (742.0, 806.0, [503.0, 511.0]),
    'LL': (582.0, 674.0, [547.5, 555.5, 562.0, 569.0, 577.5, 588.5, 598.5]),
    'LR': (740.0, 798.0, [608.5, 617.0, 627.0, 638.0, 650.5, 661.5, 669.5]),
}
P2, P2D = (156, 108, 196, 255), (70, 44, 96, 255)
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); s = 6.0
def dot(x, y):
    d.rectangle([S(x - s / 2, y - s / 2), S(x + s / 2, y + s / 2)], fill=P2, outline=P2D, width=int(SS * 0.9))
    d.rectangle([S(x - s * 0.18, y - s * 0.18), S(x + s * 0.18, y + s * 0.18)], fill=(250, 250, 248, 255))
n = 0
for nm, (xl, xr, ys) in STK.items():
    for y in ys:
        for k in range(3):
            dot(xl + (xr - xl) * (0.2 + 0.3 * k), y); n += 1
small = lay.resize((W, H), Image.LANCZOS)
out = img.convert('RGBA'); out.alpha_composite(small); out.convert('RGB').save(dst)
print('heads', n, {k: 3 * len(v[2]) for k, v in STK.items()})

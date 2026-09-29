#!/usr/bin/env python3
"""s38p03 — 오른쪽 저울(G-C) 두 접시의 붉은 조각을 「장마다 갈고리 셋」으로 (개념 논리 M: 갈고리 수 = 수소결합 수 · A-T 2 · G-C 3).
바탕은 제미나이 v2(왼쪽 저울: 접시마다 초록 한 장 · 갈고리 둘 — 맞음 · 오른쪽 붉은 조각은 장마다 갈고리 둘 — 틀림).
v2·v3·v4 모두 붉은 조각 갈고리 셋을 못 셈 → 붉은 조각 둘만 글 → 그림으로 받아(s38p03_redtiles_*.png) 몸통으로 쓰고, 갈고리는 v2 의 갈고리 꼴(뒤집힌 J · 검은 겹선 철사)로 그려 장마다 셋을 얹는다.
① 옛 조각·갈고리 지움: 접시마다 조각 자리(x0..x1 × y 612..703)를 — y<646 은 바탕(접시 위 벽 y 596..606 의 중앙값 한 색 + 잔잡음), 그 아래는 새 조각이 덮는다
② 소품 조각(갈고리 뺀 몸통 · 소품 y ≥ 176)을 조각 자리 크기(100 × 70)로 맞춰 붙임 · 색은 v2 옛 조각 평균에 맞춤 · 윤곽 짙게
③ 갈고리: 8배로 그려 줄인 뒤(안티에일리어싱) 조각마다 셋 — 조각 윗변 위, 고르게
④ 앞 끈(왼·오른)은 두 끝점을 잇는 곧은 선(폭 ≈3px · 색은 접시 위 끈에서 뜸)으로 다시 그림 · 뒤 끈(가운데)은 조각 위로만 보임
사용: python3 tools/retouch/s38p03_red_tiles.py <v2.png> <소품.png> <출력.png>"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import binary_fill_holes
base_p, asset_p, out = sys.argv[1:4]
B = np.asarray(Image.open(base_p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
A = np.asarray(Image.open(asset_p).convert('RGB'), dtype=float)
bgA = np.median(A[5:60, 5:1000].reshape(-1, 3), axis=0)
PANS = [
    dict(x0=590, x1=690, ls=((612, 560), (580, 690)), rs=((668, 560), (705, 690)), mx=641),
    dict(x0=870, x1=970, ls=((893, 560), (858, 690)), rs=((948, 560), (985, 690)), mx=920),
]
YT, YB = 634, 703
def line_x(p, q, y):
    (x1, y1), (x2, y2) = p, q
    return x1 + (x2 - x1) * (y - y1) / (y2 - y1)
# --- asset tiles (no hooks)
d = np.sqrt(((A - bgA) ** 2).sum(axis=2))
ys, xs = np.where(d > 26)
ax0, ax1, ay1 = xs.min(), xs.max() + 1, ys.max() + 1
AY0 = 168  # tile top edge in asset (hooks above it are dropped)
crop = A[AY0:ay1, ax0:ax1]
m = binary_fill_holes(np.sqrt(((crop - bgA) ** 2).sum(axis=2)) > 26)
# drop hook stubs: keep only rows where the tile body spans (row coverage > 40%)
cov = m.mean(axis=1)
first = int(np.argmax(cov > 0.4))
crop = crop[first:]; m = m[first:]
W, H = 100, YB - YT
Ci = Image.fromarray(crop.round().astype(np.uint8)).resize((W, H), Image.LANCZOS)
Mi = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
C = np.asarray(Ci, dtype=float); Mk = np.asarray(Mi, dtype=float) / 255.0
lum = C.mean(axis=2)
body = (Mk > 0.9) & (lum > 90) & (C[..., 0] > C[..., 2] + 30)
old = B[650:700, 600:680].reshape(-1, 3)
oldbody = old[(old.mean(axis=1) > 80) & (old[:, 0] > old[:, 2] + 30)]
C = C * (oldbody.mean(axis=0) / C[body].mean(axis=0))
dark = lum < 75
C[dark] = C[dark] * 0.6
C = C.clip(0, 255)
# gap between the two tiles in the scaled asset (column with least coverage in the middle)
colcov = Mk.mean(axis=0)
mid = 30 + int(np.argmin(colcov[30:70]))
tiles = [(0, mid - 1), (mid + 2, W - 1)]
print('asset rows from', AY0 + first, 'gap col', mid, 'tiles', tiles)
# --- hook sprite (inverted J, dark wire with light core), drawn 8x then reduced
S = 8
hw, hh = 12, 20
big = Image.new('LA', (hw * S, hh * S), (0, 0))
dr = ImageDraw.Draw(big)
r = 3.5 * S; cx = 6.0 * S; cy = 5.0 * S
# question-mark shaped hook like the green tiles' hooks: top curl (left → over → right), bend back to the centre, straight stem down
pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(165, 361, 5)]
pts += [(cx + r * math.cos(math.radians(a)) * 0.9, cy + r * 0.9 * math.sin(math.radians(a))) for a in range(0, 91, 10)]
pts += [(cx, hh * S)]
for wdt, colr in ((3.0, 30), (1.1, 215)):
    dr.line(pts if colr == 30 else pts[:-1] + [(cx, hh * S - 2 * S)], fill=(colr, 255), width=int(wdt * S), joint='curve')
hook = big.resize((hw, hh), Image.LANCZOS)
hk = np.asarray(hook, dtype=float)
hv, ha = hk[..., 0], hk[..., 1] / 255.0
res = B.copy()
for P in PANS:
    x0, x1 = P['x0'], P['x1']
    # ① erase old tiles/hooks above the pan's back rim
    wall = np.median(B[596:607, x0 + 20:x1 - 20].reshape(-1, 3), axis=0)  # flat cream wall (strings are thin → median is wall)
    rng = np.random.default_rng(x0)
    for y in range(606, YT + 12):
        for x in range(x0 - 3, x1 + 4):
            res[y, x] = wall + rng.normal(0, 0.8, 3)
    # back (middle) string down to the new tile top
    for y in range(606, YT + 1):
        for x in range(P['mx'] - 2, P['mx'] + 3):
            if B[596:606, x].mean() < 150 or B[y, x].mean() < 110:
                res[y, x] = B[590, x] if B[590, x].mean() < 150 else res[y, x]
    # ② paste tiles
    reg = res[YT:YB, x0:x0 + W]
    res[YT:YB, x0:x0 + W] = reg * (1 - Mk[..., None]) + C * Mk[..., None]
    # ③ hooks: three per tile, evenly spaced
    for (ta, tb) in tiles:
        width = tb - ta
        for k in range(3):
            cxp = x0 + ta + width * (k + 0.5) / 3
            hx = int(round(cxp - hw / 2)); hy = YT + 3 - hh
            sub = res[hy:hy + hh, hx:hx + hw]
            res[hy:hy + hh, hx:hx + hw] = sub * (1 - ha[..., None]) + hv[..., None] * ha[..., None]
    # ④ front strings redrawn on top as straight anti-aliased wires (colour sampled from the string above the pan)
    for (p, q) in (P['ls'], P['rs']):
        ys_ = range(580, 591)
        samp = [B[y, int(round(line_x(p, q, y)))] for y in ys_]
        col = np.median(np.array(samp), axis=0)
        for y in range(600, YB + 1):
            xc = line_x(p, q, y)
            for x in range(int(xc) - 3, int(xc) + 4):
                wgt = max(0.0, min(1.0, 1.6 - abs(x - xc)))
                if wgt > 0:
                    res[y, x] = res[y, x] * (1 - wgt) + col * wgt
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)

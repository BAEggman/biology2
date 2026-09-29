#!/usr/bin/env python3
"""s48p01 — 제미나이 v1(셋째 칸: 두 막대가 세로 한 줄 · 막대마다 양쪽 벽 밧줄 / 넷째 칸: 짧은 밧줄이 막대를 벽으로 /
다섯째 칸: 실 뭉치가 천막 안) 손질.
① 셋째 칸 점선(x 511..514)이 막대(가운데 x 497) 오른쪽 곁에 그어져 「판 곁」으로 읽힘 → 옛 점선을 바닥 색으로 지우고
   막대 한가운데를 꿰뚫는 점선(x 497, 13px 주기 · 6px 대시)을 그 위에 새로 그림 — 밧줄 고리(y 147..159 · 233..247)는 비움
② 아래 천막 왼쪽 벽 밖으로 삐져나온 실 고리(벽 선 (886,259)–(896,283) 왼쪽) 지움 · 모서리 꼭지는 둠
③ 위 천막 문 밑 바닥으로 흘러내린 실 두어 가닥(x 843..880 · y 192..202) 지움
④ 앞 판자의 제미나이 반짝이 표식(x 930..962 · y 318..340)을 40px 왼쪽 판자 결로 덮음(가장자리 8px 섞음)
사용: python3 s48p01_plate_threads.py V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); W, H = im.size
assert (W, H) == (1024, 412), (W, H)
a = np.asarray(im).astype(np.float32)
lum = a.mean(2)
rng = np.random.default_rng(48)
out = a.copy()

# ① erase the old dashed line
ROPE_ROWS = [(153, 157), (237, 241)]      # where the two ropes cross the old dashed line
COLLARS = [(147, 159), (233, 247)]        # rope collars on the rods — no new dash over them
def in_rope(y):
    return any(r0 <= y <= r1 for r0, r1 in ROPE_ROWS)
for y in range(114, 312):
    if in_rope(y):
        continue
    cols = [509, 510] + list(range(516, 525))
    ref = a[y, cols]; ref = ref[ref.mean(1) > 185]
    if len(ref) < 3:
        continue
    bg = np.median(ref, axis=0)
    for x in range(510, 516):
        if lum[y, x] < bg.mean() - 12:
            out[y, x] = np.clip(bg + rng.normal(0, 1.5, 3), 0, 255)
# new dashed line through the rods' centre
SS = 8
L = Image.new('L', (W*SS, H*SS), 0); d = ImageDraw.Draw(L)
XC = 497.0
y = 119.0
while y < 306:
    y0, y1 = y, min(y + 6.0, 306)
    if not any((y0 <= r1 and y1 >= r0) for r0, r1 in COLLARS):
        d.line([(XC*SS, y0*SS), (XC*SS, y1*SS)], fill=255, width=int(2.4*SS))
    y += 13.0
al = np.asarray(L.resize((W, H), Image.LANCZOS)).astype(np.float32)[..., None] / 255.0 * 0.9
out = out*(1-al) + np.array([58, 54, 50], np.float32)*al

# ② lower tent: the thread loop outside its left wall — left of the wall line (886,259)–(896,283); the corner knob above stays
for y in range(260, 284):
    xl = 886 + (y - 259) * (10.0 / 24.0) - 1.5
    ref = a[y, 864:877]; bg = np.median(ref, axis=0)
    for x in range(878, int(np.floor(xl)) + 1):
        if lum[y, x] < bg.mean() - 10:
            out[y, x] = np.clip(bg + rng.normal(0, 1.5, 3), 0, 255)
# ③ upper tent: curls below the hem
box = (843, 192, 881, 203)
x0, y0, x1, y1 = box
for yy in range(y0, y1):
    ref = a[yy, 815:835]; ref = ref[ref.mean(1) > 200]
    bg = np.median(ref, axis=0) if len(ref) else np.array([236, 226, 205], np.float32)
    for xx in range(x0, x1):
        if lum[yy, xx] < bg.mean() - 14:
            out[yy, xx] = np.clip(bg + rng.normal(0, 1.5, 3), 0, 255)
# ④ sparkle mark on the front board
X0, X1, Y0, Y1, OFF, F = 924, 968, 317, 342, -40, 8
for x in range(X0, X1):
    wx = min(1.0, (x - X0 + 1) / F, (X1 - x) / F)
    for y in range(Y0, Y1):
        wy = min(1.0, (y - Y0 + 1) / 2.0, (Y1 - y) / 2.0)
        w = wx * wy
        out[y, x] = out[y, x] * (1 - w) + a[y, x + OFF] * w
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print('ok', dst)

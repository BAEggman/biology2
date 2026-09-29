#!/usr/bin/env python3
"""s19p01c — 개념 논리 M: M 쐐기(가장 얇은 칸)에 빵 하나 · G2 쐐기(돋보기 칸)에 빵 셋이던 것(S 뒤로는 계속 둘) →
G2 맨 위 빵(x 128..262 · y 296..402)을 떼어 M 쐐기의 왼쪽 벽(135° 바퀴살) 곁에 바퀴살과 나란히(45°) 눕힌다.
그러면 G2 는 돋보기 밑 빵 둘, M 은 두 벽에 붙은 빵 둘(가운데가 빔).
· 떼어 낸 자리: 바퀴살 좌표(s 따라 · t 가로)로 채움 — 같은 t 줄에서 s ±90px 안의 깨끗한 바닥·그늘 화소의 중앙값(바퀴살 그늘 띠가 끊기지 않게)
  + 테두리(원 중심 (414,483) · 바닥선 r≈318) 가까운 화소(r ≥ 311)는 같은 r · θ+20° 에서 옮김 + 잔잡음
· 옮긴 빵: 색 거리 + 채움으로 오린 알파 · 13° 시계 방향 · 바퀴살에서 t=+39(윗오른쪽) · s=62 · 연한 그림자(+6,+6)
사용: python3 s19p01c_move_bread.py SRC.png OUT.png"""
import sys, math
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); W, H = im.size
assert (W, H) == (1024, 1024), (W, H)
a = np.asarray(im).astype(np.float32)
lum = a.mean(2)
rng = np.random.default_rng(191)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
# spoke frame: origin on the 135° spoke centreline, d along it (down-right), n across it (up-right)
O = np.array([199.0, 276.0]); SQ = math.sqrt(2)
S = ((xx - O[0]) + (yy - O[1])) / SQ
T = ((xx - O[0]) - (yy - O[1])) / SQ
CX, CY = 414.0, 483.0
Rr = np.hypot(xx - CX, yy - CY)
TH = np.degrees(np.arctan2(-(yy - CY), xx - CX)) % 360

# --- the bread sprite ---
X0, Y0, X1, Y1 = 128, 296, 262, 402
sub = a[Y0:Y1, X0:X1]
R_, G_, B_ = sub[..., 0], sub[..., 1], sub[..., 2]
gold = (R_ - B_ > 45) & (R_ > 150)
dark = sub.mean(2) < 95
m = ndi.binary_closing(gold | dark, iterations=2)
lab, n = ndi.label(m)
sizes = ndi.sum(m, lab, range(1, n + 1))
bread = ndi.binary_fill_holes(lab == 1 + int(np.argmax(sizes)))
alpha = ndi.gaussian_filter(bread.astype(np.float32), 0.7)
spr = Image.fromarray(np.dstack([sub, alpha[..., None] * 255]).astype(np.uint8), 'RGBA')

# --- erase mask: bread + its drop shadow ---
E = np.zeros((H, W), bool)
bd = ndi.binary_dilation(bread, iterations=3)
sh = np.zeros_like(bd); sh[5:, 5:] = bd[:-5, :-5]
sh = ndi.binary_dilation(sh, iterations=4)
E[Y0:Y1, X0:X1] = bd | sh
E &= (Rr < 322)                     # never touch the rim beyond its floor line
out = a.copy()
# clean reference pixels: light, unsaturated, not erased, inside the floor
clean = (~E) & (lum > 160) & ((a[..., 0] - a[..., 2]) < 42) & (Rr < 309) & (T < -8.5)
# exclude other objects' neighbourhoods (other breads, magnifier): their dark outlines + gold
obj = (lum < 120) | ((a[..., 0] - a[..., 2]) > 45)
obj = ndi.binary_dilation(obj, iterations=4)
clean &= ~obj
ey, ex = np.nonzero(E)
tb = np.round(T[ey, ex]).astype(int); sb = S[ey, ex]
filled = 0
for (y, x, t, s) in zip(ey, ex, tb, sb):
    r = Rr[y, x]
    if r >= 311:
        th = math.radians(TH[y, x] + 20.0)
        sx = CX + r * math.cos(th); sy = CY - r * math.sin(th)
        out[y, x] = a[int(round(sy)), int(round(sx))]
        continue
    if t > -8:            # on/above the spoke edge: keep (bread never covered the spoke face)
        continue
    sel = (np.abs(T - t) < 0.75) & (np.abs(S - s) < 90) & clean
    vals = a[sel]
    if len(vals) < 8:
        sel = (np.abs(T - t) < 2.0) & (np.abs(S - s) < 140) & clean
        vals = a[sel]
    out[y, x] = np.median(vals, axis=0) + rng.normal(0, 1.3, 3)
    filled += 1
print('filled', filled, 'of', len(ey))
# soften the seam a touch
Eb = ndi.gaussian_filter(E.astype(np.float32), 1.0)
blur = ndi.gaussian_filter(out, sigma=(0.8, 0.8, 0))
ring = (Eb > 0.05) & (Eb < 0.95)
out[ring] = blur[ring]

# --- paste the bread along the spoke, up-right side ---
res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')
Sr = spr.rotate(-13.0, resample=Image.BICUBIC, expand=True)
s_c, t_c = 62.0, 39.0
cx = O[0] + (s_c + t_c) / SQ; cy = O[1] + (s_c - t_c) / SQ
px, py = int(round(cx - Sr.width / 2)), int(round(cy - Sr.height / 2))
sal = np.asarray(Sr)[..., 3].astype(np.float32) / 255.0
shadow = ndi.gaussian_filter(sal, 3.0) * 0.14
o2 = np.asarray(res).astype(np.float32)
shm = np.zeros((H, W), np.float32)
shm[py + 6:py + 6 + Sr.height, px + 6:px + 6 + Sr.width] = shadow
o2[..., :3] *= (1 - shm[..., None])
res = Image.fromarray(o2.astype(np.uint8), 'RGBA')
res.alpha_composite(Sr, (px, py))
res.convert('RGB').save(dst)
print('bread centre', round(cx, 1), round(cy, 1), 'box', px, py, Sr.size)

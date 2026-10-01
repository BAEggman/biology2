#!/usr/bin/env python3
"""s31p03 — 개념 논리 m 5: 벽 선반 위 사람의 **네모 양동이(FAD)가 비어** 있던 것 → 물이 가득 찬 네모 양동이(= FADH₂) · 바닥 셋의 둥근 양동이(NADH)도 또렷이 가득.
제미나이 v1 은 둥근 양동이 셋을 가득 채웠지만 **네모 양동이를 둥글게** 바꿔 버렸다(네모 = FAD · 둥근 = NAD 를 가르는 모양이 사라짐) →
  ① 둥근 양동이 셋 자리(상자 셋)만 v1 에서 옮김(σ2 밝기 차 > 10 · 닫기 3 · 메움 · 넓힘 3 · σ1.5 섞음).
  ② 네모 양동이는 원본 그대로 두고 **손으로 물을 채움**: 테 안쪽 마름모(왼 (652,182) · 뒤 (669,176) · 오른 (696,182) · 앞 (674,190))를
     v1 둥근 양동이의 물빛(183,205,203)으로, 뒤쪽 두 변을 따라 살짝 어둡게(그늘) · 가운데 밝은 물결 한 줄 · 4배 키운 마스크로 매끈하게.
  ③ 오른쪽 아래 벽돌 위 반짝이 표식(중심 ≈ (905,905))은 벽돌 결이 되풀이되는 것을 써서 둘레 고리가 가장 잘 맞는 어긋남의 벽돌을 옮겨 덮는다
     (흰 덧칠을 α 로 되돌리는 안은 별 가장자리가 고리처럼 남아 버림).
사용: python3 s31p03_buckets.py ORIG.png V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
H, W = O.shape[:2]
out = O.copy()
# ① 둥근 양동이 셋
d = ndi.gaussian_filter(np.abs(O - V).mean(axis=2), 2.0)
m = np.zeros((H, W), bool)
for (x0, y0, x1, y1) in [(100, 500, 200, 612), (380, 360, 472, 452), (820, 510, 922, 612)]:
    b = np.zeros((H, W), bool); b[y0:y1, x0:x1] = True
    mm = (d > 10) & b
    mm = ndi.binary_closing(mm, iterations=3)
    mm = ndi.binary_fill_holes(mm)
    mm = ndi.binary_dilation(mm, iterations=3) & b
    m |= mm
w = ndi.gaussian_filter(m.astype(float), 1.5)
out = out * (1 - w[..., None]) + V * w[..., None]
print('round buckets px', int(m.sum()))
# ② 네모 양동이 물
S = 4
poly = [(652, 182), (669, 176), (696, 182), (674, 190)]
mk = Image.new('L', (W * S, H * S), 0)
ImageDraw.Draw(mk).polygon([(x * S, y * S) for x, y in poly], fill=255)
mk = np.asarray(mk.resize((W, H), Image.LANCZOS)).astype(np.float64) / 255.0
water = np.array([183.0, 205.0, 203.0])
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
# 뒤쪽 두 변(왼→뒤 · 뒤→오른)에서 멀어질수록 밝게
def dist_line(p, q):
    (x1, y1), (x2, y2) = p, q
    return np.abs((y2 - y1) * xx - (x2 - x1) * yy + x2 * y1 - y2 * x1) / np.hypot(x2 - x1, y2 - y1)
dback = np.minimum(dist_line(poly[0], poly[1]), dist_line(poly[1], poly[2]))
shade = np.clip(dback / 6.0, 0, 1)
col = water[None, None, :] * (0.86 + 0.14 * shade[..., None])
# 밝은 물결 한 줄(앞-왼 변과 나란히, 가운데)
hl = Image.new('L', (W * S, H * S), 0)
ImageDraw.Draw(hl).line([(660 * S, 184.5 * S), (676 * S, 187.5 * S)], fill=255, width=int(1.2 * S))
ImageDraw.Draw(hl).line([(678 * S, 182.0 * S), (690 * S, 183.5 * S)], fill=255, width=int(1.0 * S))
hl = np.asarray(hl.resize((W, H), Image.LANCZOS)).astype(np.float64) / 255.0
col = col * (1 - 0.6 * hl[..., None]) + 245.0 * 0.6 * hl[..., None]
out = out * (1 - mk[..., None]) + col * mk[..., None]
print('water px', int((mk > 0.5).sum()))
# ③ 반짝이: 벽돌 결이 되풀이되므로 **같은 결의 다른 자리를 옮겨 덮는다**(방향 복제). 반짝이 모양 = 둘레 벽돌 면보다 밝은 덩어리(닫기 · 넓힘 3).
#    옮길 자리는 반짝이 둘레 고리(넓힘 3..12)가 가장 잘 맞는 어긋남(dx,dy ∈ ±90, 원본 반짝이와 겹치지 않는 것)으로 고른다.
X0, X1, Y0, Y1 = 860, 952, 858, 952
L = out.mean(axis=2)
ring = np.zeros((H, W), bool); ring[Y0 - 12:Y1 + 12, X0 - 12:X1 + 12] = True; ring[Y0:Y1, X0:X1] = False
face = ring & (L > 110)
bgL = np.median(L[face])
star = np.zeros((H, W), bool)
star[Y0:Y1, X0:X1] = ndi.grey_closing(L, size=(3, 3))[Y0:Y1, X0:X1] > bgL + 22
lab, n = ndi.label(star)
if n:
    sz = ndi.sum(star, lab, range(1, n + 1)); star = lab == (1 + int(np.argmax(sz)))
star = ndi.binary_fill_holes(ndi.binary_dilation(star, iterations=3))
ringm = ndi.binary_dilation(star, iterations=12) & ~ndi.binary_dilation(star, iterations=3)
ys, xs = np.nonzero(ringm)
best = None
for dy in range(-90, 91, 2):
    for dx in range(-90, 91, 2):
        if abs(dx) < 40 and abs(dy) < 40:
            continue
        sy, sx = ys + dy, xs + dx
        if sy.min() < 0 or sx.min() < 0 or sy.max() >= H or sx.max() >= W:
            continue
        e = np.abs(out[sy, sx] - out[ys, xs]).mean()
        if best is None or e < best[0]:
            best = (e, dx, dy)
e, dx, dy = best
# 2 단위 격자 주변을 1 단위로 다듬기
for ddy in (-1, 0, 1):
    for ddx in (-1, 0, 1):
        sy, sx = ys + dy + ddy, xs + dx + ddx
        e2 = np.abs(out[sy, sx] - out[ys, xs]).mean()
        if e2 < e:
            e, best = e2, (e2, dx + ddx, dy + ddy)
e, dx, dy = best
src = np.roll(np.roll(out, -dy, axis=0), -dx, axis=1)
wst = ndi.gaussian_filter(star.astype(float), 1.5)
wst = np.maximum(wst, star.astype(float) * 0.999)
out = out * (1 - wst[..., None]) + src * wst[..., None]
print('sparkle px', int(star.sum()), 'clone offset', (dx, dy), 'ring err %.1f' % e, 'bgL', round(float(bgL), 1))
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print('saved', dst)

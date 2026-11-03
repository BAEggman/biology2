#!/usr/bin/env python3
"""touch_h6.py — s45u02 v9 ⑥ 걸상 위
 ① 행 18 — 사상조류 실을 굵게(폭 7.5 px · 마디 9 px · 마디마다 그 자리 띠 빛깔 0.75 + 초록 0.25 · 양 가장자리 짙은 선)
    — b139 독자 둘 다 「걸상 뒤 모서리의 가는 연두 줄」을 1 · 2단계에서 못 봤다. 헤엄이 · 방울 화소는 위에 남긴다(실은 그 밑으로)
 ② 행 22 — 청록 · 주황 띠의 작은 무리를 헤엄이 다섯 → 여덟 · 방울 셋 → 넷(그래도 큰 무더기보다 작게)
사용: touch_h6.py in.png cur5c.png out.png   (cur5c = 실 · 헤엄이 전의 걸상 무지개 — 띠 빛깔 표본)"""
import sys, math, random, numpy as np
from PIL import Image, ImageDraw
src, c5c, dst = sys.argv[1:4]
img = Image.open(src).convert('RGB'); W, H = img.size
A = np.asarray(img).astype(float); C5c = np.asarray(Image.open(c5c).convert('RGB')).astype(float)
SS = 4; S = lambda x, y: (x * SS, y * SS)
ty = lambda x: 611 + (x - 1560) * 0.117
tyT = lambda x: ty(x) + 2.5
X0, X1, TW = 1568.0, 2004.0, 7.5
# 띠 빛깔(실 높이 10 px 위 걸상 무지개)
band = {}
for x in range(int(X0), int(X1) + 1):
    yb = int(ty(x) - 10)
    band[x] = C5c[yb - 1:yb + 2, x - 2:x + 3].reshape(-1, 3).mean(axis=0)
GREEN = np.array([96, 168, 70.0])
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
k = 0.117
nx, ny = -k / math.hypot(1, k), 1 / math.hypot(1, k)          # 실의 법선
seg = 9.0
x = X0
while x < X1:
    xb = min(x + seg, X1)
    col = tuple(int(v) for v in (0.75 * band[int((x + xb) / 2)] + 0.25 * GREEN))
    p = [S(x + nx * TW / 2, tyT(x) + ny * TW / 2 - TW), S(xb + nx * TW / 2, tyT(xb) + ny * TW / 2 - TW)]
    quad = [S(x, tyT(x) - TW / 2), S(xb, tyT(xb) - TW / 2), S(xb, tyT(xb) + TW / 2), S(x, tyT(x) + TW / 2)]
    d.polygon(quad, fill=col + (255,))
    # 마디 칸막이(짙은 초록 선)
    d.line([S(xb, tyT(xb) - TW / 2 + 0.6), S(xb, tyT(xb) + TW / 2 - 0.6)], fill=(40, 70, 30, 220), width=int(SS * 0.9))
    # 마디 속 밝은 결(세포 속)
    d.line([S(x + 2.0, tyT(x + 2.0) - 0.8), S(xb - 2.0, tyT(xb - 2.0) - 0.8)], fill=(255, 255, 240, 70), width=int(SS * 1.0))
    x = xb
d.line([S(X0, tyT(X0) - TW / 2), S(X1, tyT(X1) - TW / 2)], fill=(34, 60, 26, 255), width=int(SS * 1.1))
d.line([S(X0, tyT(X0) + TW / 2), S(X1, tyT(X1) + TW / 2)], fill=(34, 60, 26, 255), width=int(SS * 1.1))
d.ellipse([S(X0 - TW / 2, tyT(X0) - TW / 2), S(X0 + TW / 2, tyT(X0) + TW / 2)], fill=tuple(int(v) for v in (0.75 * band[int(X0)] + 0.25 * GREEN)) + (255,), outline=(34, 60, 26, 255), width=int(SS * 1.0))
L = np.asarray(lay.resize((W, H), Image.LANCZOS)).astype(float)
al = L[..., 3:4] / 255.0
# 헤엄이(올리브 · 짙은 테) · 방울(흰) 화소는 실 위에 남긴다
OL = np.array([128, 118, 52.0]); OLD = np.array([52, 46, 18.0])
dist_ol = np.minimum(np.linalg.norm(A - OL, axis=2), np.linalg.norm(A - OLD, axis=2))
keep = (dist_ol < 38) | (A.mean(axis=2) > 228)
al[keep] = 0
A = A * (1 - al) + L[..., :3] * al
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))

# ② 작은 무리 키우기
OLc, OLDc = (128, 118, 52, 255), (52, 46, 18, 255)
def bact(d, bx, by, ang, kk=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: S(bx + u * ca - v * sa, by + u * sa + v * ca)
    body = [P(4.4 * kk * math.cos(t), 1.9 * kk * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)]
    d.polygon(body, fill=OLc, outline=OLDc)
    d.line([P(-4.4 * kk - j * 0.9, 1.1 * math.sin(j * 1.1)) for j in range(9)], fill=OLDc, width=int(SS * 0.7))
def bub2(d, cx, cy, r):
    d.ellipse([S(cx - r, cy - r), S(cx + r, cy + r)], fill=(250, 251, 253, 255), outline=(116, 128, 146, 255), width=int(SS * 0.9))
    d.ellipse([S(cx - r * 0.5, cy - r * 0.55), S(cx - r * 0.05, cy - r * 0.1)], fill=(255, 255, 255, 255))
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
for (x, dy, ang) in [(1693.0, -6.0, 0.35), (1716.0, -7.0, -0.25), (1724.0, -3.5, 0.1)]:
    bact(d, x, tyT(x) + dy, ang)
for (x, dy, ang) in [(1876.0, -6.5, -0.3), (1893.0, -7.0, 0.3), (1899.0, -3.0, -0.1)]:
    bact(d, x, tyT(x) + dy, ang)
bub2(d, 1706.0, tyT(1706.0) - 50.0, 2.2)
bub2(d, 1888.0, tyT(1888.0) - 50.0, 2.2)
small = lay.resize((W, H), Image.LANCZOS)
im2 = img.convert('RGBA'); im2.alpha_composite(small); im2.convert('RGB').save(dst)
print('ok', dst)

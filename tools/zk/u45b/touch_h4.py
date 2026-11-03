#!/usr/bin/env python3
"""touch_h4.py — s45u02 v7 ④ 잔손질
 ① 행 9 — 놓친 공의 점선을 맞잡은 손(1233, 546)에서 시작해 사발 오른 테 위 ~12 px 를 넘어 쿠션의 타는 공으로(같은 손에서 난 공이 「받힘 / 비켜 타 버림」으로 갈린다)
    — v4 ~ v6 의 점선은 손에서 7.5 px 를 비우고 테 옆 팔뚝에서 시작해 「사발이 쏟은 공(전자의 주 경로)」으로 읽혔다(b137 A) · 사발 속 공 밑에 그늘 반달(안착)
 ② 행 10 · 19 — 생물학 고침: 초록 · 노랑 띠에도 헤엄이 한둘 · 노랑에 작은 방울 하나(녹색광에서도 광합성은 일어난다 — 가장 적을 뿐)
 ③ 행 21 — 앞판의 빈 a 머리 넷(청록 · 초록 · 노랑 · 주황) 흰 창을 그 띠 빛의 아주 옅은 빛으로(무대 액자의 안 든 칸과 같은 말 — 흰 창은 「흰빛」으로 읽혔다)
 ④ 행 22 — b 머리 · 당근 꼬리표에서 바로 위 작은 무리까지 빛기둥을 또렷이(폭 5 px · 짙기 0.55 · 위끝 빛무리)
사용: touch_h4.py in.png cur13.png out.png"""
import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, c13, dst = [a for a in sys.argv[1:] if not a.startswith('--')][:3]
img = Image.open(src).convert('RGB'); W, H = img.size
C13 = np.asarray(Image.open(c13).convert('RGB')).astype(float)
SS = 4; S = lambda x, y: (x * SS, y * SS)
def layer(): return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
def pm_blur(im, sig):
    """RGBA 흐림을 미리 곱한 알파로 — PIL 의 RGBA 흐림은 투명 화소의 검은 RGB 를 가장자리에 섞어 테를 어둡게 한다(v9 에서 찾음 · 흰 눈부심의 회색 테)."""
    import numpy as _np
    from scipy.ndimage import gaussian_filter as _gf
    a = _np.asarray(im).astype(float); al = a[..., 3:4] / 255.0
    pm = _gf(a[..., :3] * al, (sig, sig, 0)); ab = _gf(al, (sig, sig, 0))
    rgb = pm / _np.maximum(ab, 1e-6)
    return Image.fromarray(_np.clip(_np.concatenate([rgb, ab * 255.0], axis=2), 0, 255).astype('uint8'), 'RGBA')
def comp(img, lay, blur=0):
    small = lay.resize((W, H), Image.LANCZOS)
    if blur: small = pm_blur(small, blur)
    im2 = img.convert('RGBA'); im2.alpha_composite(small); return im2.convert('RGB')
yy, xx = np.mgrid[0:H, 0:W]
def bezpts(P0, C, P1, n=2000):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * np.array(P0) + 2 * (1 - t) * t * np.array(C) + t ** 2 * np.array(P1)

# ── ① 옛 점선 걷기(touch_e 의 호 · t ≤ 0.86 — 타는 공의 빛무리는 건드리지 않음) → 새 호
#    v7b: b138 에서 새 호가 「몸을 따라 곧장 내려가 이어짐」으로 읽혀 B 도 놓쳤다(v6 호는 B 가 읽었다) → 기본은 v6 호 그대로(--arc 일 때만)
ARC = '--arc' in sys.argv
A = np.asarray(img).astype(float)
old = bezpts((1238.0, 543.0), (1266.0, 512.0), (1272.0, 634.0)) if ARC else np.zeros((0, 2))
old = old[: int(len(old) * 0.86)]
M = np.zeros((H, W), bool)
for (x, y) in old[::4]:
    M[int(y) - 3:int(y) + 4, int(x) - 3:int(x) + 4] = True
M &= np.abs(A - C13).max(axis=2) > 10
A[M] = C13[M]
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
P0, C, P1 = (1233.0, 546.0), (1262.0, 508.0), (1272.0, 634.0)
pts = bezpts(P0, C, P1)
i = np.argmin(np.abs(pts[:, 0] - 1252)); print('호가 테(1252) 위를 지나는 높이 y =', round(float(pts[i, 1]), 1), '(테 윗변 ≈ 550)')
acc, last, dots = 0.0, pts[0], [tuple(pts[0])]
for p in pts[1:]:
    acc += math.hypot(p[0] - last[0], p[1] - last[1]); last = p
    if acc >= 3.1: dots.append(tuple(p)); acc = 0.0
lay = layer(); d = ImageDraw.Draw(lay)
for (x, y) in (dots if ARC else []):
    if math.hypot(x - P1[0], y - P1[1]) < 4.0: continue
    d.ellipse([S(x - 0.95, y - 0.95), S(x + 0.95, y + 0.95)], fill=(52, 44, 36, 240))
# 사발 속 공 밑 그늘 반달
if ARC: d.ellipse([S(1236.6, 556.4), S(1245.0, 559.0)], fill=(70, 46, 26, 120))
img = comp(img, lay)
print('점선', len(dots), '옛 점 걷음', int(M.sum()))

# ── ② 초록 · 노랑 띠의 헤엄이 한둘 · 방울 하나
ty = lambda x: 611 + (x - 1560) * 0.117
tyT = lambda x: ty(x) + 2.5
OL, OLD = (128, 118, 52, 255), (52, 46, 18, 255)
def bact(d, bx, by, ang, k=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: S(bx + u * ca - v * sa, by + u * sa + v * ca)
    body = [P(4.4 * k * math.cos(t), 1.9 * k * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)]
    d.polygon(body, fill=OL, outline=OLD)
    d.line([P(-4.4 * k - j * 0.9, 1.1 * math.sin(j * 1.1)) for j in range(9)], fill=OLD, width=int(SS * 0.7))
def bub2(d, cx, cy, r):
    d.ellipse([S(cx - r, cy - r), S(cx + r, cy + r)], fill=(250, 251, 253, 255), outline=(116, 128, 146, 255), width=int(SS * 0.9))
    d.ellipse([S(cx - r * 0.5, cy - r * 0.55), S(cx - r * 0.05, cy - r * 0.1)], fill=(255, 255, 255, 255))
lay = layer(); d = ImageDraw.Draw(lay)
bact(d, 1766.0, tyT(1766.0) - 3.0, 0.25)
bact(d, 1822.0, tyT(1822.0) - 2.5, -0.3)
bact(d, 1834.0, tyT(1834.0) - 4.5, 0.4)
bub2(d, 1829.0, tyT(1829.0) - 16.0, 2.0)
img = comp(img, lay)

# ── ③ 빈 a 머리 창을 그 띠 빛의 옅은 빛으로
A = np.asarray(img).astype(float)
TINT = {1705.5: (64, 170, 182), 1764.0: (86, 178, 80), 1828.0: (236, 206, 64), 1897.5: (240, 140, 40)}
for xc, col in TINT.items():
    top = ty(xc) + 22.6
    x0, x1, y0, y1 = xc - 4.6, xc + 4.6, top + 3.5, top + 12.5
    reg = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1) & ((xx - xc) ** 2 + (yy - (top + 8)) ** 2 > 3.4 ** 2)
    reg &= A.mean(axis=2) > 196
    A[reg] = 0.86 * 247 + 0.14 * np.array(col, float)
    print('창', xc, int(reg.sum()))
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))

# ── ④ 빛기둥(꼬리표 → 바로 위 작은 무리)
lay = layer(); d = ImageDraw.Draw(lay)
# v8: b 꼬리표는 touch_h5 가 걸상 아래 b 줄로 옮긴다 — 여기서는 당근 빛기둥만(--v7 이면 옛 셋)
V7 = '--v7' in sys.argv
COLS = [(1721.0, ty(1721.0) + 21.0, tyT(1721.0) - 5.0, (90, 196, 200))]
if V7:
    COLS = [(1689.5, ty(1689.5) + 22.5, tyT(1689.5) - 5.0, (70, 186, 196))] + COLS + [(1881.0, ty(1881.0) + 22.5, tyT(1881.0) - 5.0, (246, 150, 56))]
for (xc, ybot, ytop, col) in COLS:
    for k in range(24):
        ya = ytop + (ybot - ytop) * k / 24; yb_ = ytop + (ybot - ytop) * (k + 1) / 24
        al = int(150 - 40 * k / 24)
        d.rectangle([S(xc - 2.5, ya), S(xc + 2.5, yb_)], fill=col + (al,))
img = comp(img, lay, 0.8)
lay = layer(); d = ImageDraw.Draw(lay)
for (xc, col) in ([(1689.5, (70, 186, 196)), (1721.0, (90, 196, 200)), (1881.0, (246, 150, 56))] if V7 else [(1721.0, (90, 196, 200))]):
    yc = tyT(xc) - 6.0
    d.ellipse([S(xc - 7, yc - 4), S(xc + 7, yc + 4)], fill=col + (90,))
img = comp(img, lay, 2.0)
img.save(dst); print('ok', dst)

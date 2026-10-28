#!/usr/bin/env python3
"""touch_b.py — s45u02 PIL 손질 2: cur7 → cur8
 〔C 쿠션 무대〕 ① 액자 속 빛깔(왼 자매 맑은 파랑 · 오른 자매 초록빛 도는 파랑) ② 빛살 — 파랑 → 왼 자매 · 초록빛 파랑 → 오른 자매 ·
 초록 → 오른 자매 액자 윗변에서 V 로 되튐 · 보라~청록 → 당근빛 머리 · 흰 눈부심 → 망토 ③ 머리 사이 금빛 물결(→ 쌍둥이)
 ④ 가슴 브로치 — 왼 자매 세 갈래 잔가지 · 오른 자매 갈퀴 넷 포크 · 쌍둥이도 세 갈래 잔가지 ⑤ 쌍둥이 맞잡은 손 → 노란 공 → 빈 사발(옆으로 호)
 〔D 걸상〕 ⑥ 걸상 뒤 난간 + 자주빛 액자 머리 일곱(띠마다 하나 — 보라 · 파랑 · 빨강만 그 빛으로 가득 · 초록은 V 되튐 · 나머지 빔)
 (확대선은 그어 보니 잎 널 · 꼬투리가 맞붙어 있어 선이 외곽선을 겹치고 끈처럼 읽혀 뺐다 — 같은 초록 쿠션이 이음을 나른다)"""
import sys, os, math, colorsys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
img = Image.open('cur7.png').convert('RGB'); W, H = img.size
SS = 4
S = lambda x, y: (x * SS, y * SS)
def layer(): return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
def comp(img, lay, blur=0):
    small = lay.resize((W, H), Image.LANCZOS)
    if blur: small = small.filter(ImageFilter.GaussianBlur(blur))
    im2 = img.convert('RGBA'); im2.alpha_composite(small); return im2.convert('RGB')
A0 = np.asarray(img).astype(int)

# ── ① 액자 속 빛깔(은빛 구슬 · 테 남김)
def window_tint(img, box, ball, col, a=0.62):
    x0, y0, x1, y1 = box; A = np.asarray(img).astype(float)
    sub = A[y0:y1, x0:x1]; L = sub.mean(axis=2); sat = sub.max(axis=2) - sub.min(axis=2)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    white = (L > 200) & (sat < 40) & ((xx - ball[0]) ** 2 + (yy - ball[1]) ** 2 > (ball[2] + 2) ** 2)
    m = white.astype(float)[..., None] * a
    A[y0:y1, x0:x1] = sub * (1 - m) + np.array(col, float) * m
    return Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
img = window_tint(img, (960, 323, 1015, 388), (985, 353, 13), (96, 150, 232))
img = window_tint(img, (1332, 318, 1382, 388), (1355, 352, 14), (84, 176, 178))

# ── ② 빛살
def beam(lay, p0, p1, w0, w1, col, a0=40, a1=150, steps=24):
    d = ImageDraw.Draw(lay)
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    for k in range(steps):
        t0, t1 = k / steps, (k + 1) / steps
        wa, wb = w0 + (w1 - w0) * t0, w0 + (w1 - w0) * t1
        ca = (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0); cb = (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)
        alpha = int(a0 + (a1 - a0) * (t0 + t1) / 2)
        poly = [S(ca[0] + nx * wa / 2, ca[1] + ny * wa / 2), S(cb[0] + nx * wb / 2, cb[1] + ny * wb / 2),
                S(cb[0] - nx * wb / 2, cb[1] - ny * wb / 2), S(ca[0] - nx * wa / 2, ca[1] - ny * wa / 2)]
        d.polygon(poly, fill=col + (alpha,))
lay = layer()
beam(lay, (1050, 40), (994, 318), 14, 20, (92, 140, 228))                 # 파랑 → 왼 자매(a)
beam(lay, (1438, 40), (1380, 314), 14, 20, (70, 172, 176))                # 초록빛 파랑 → 오른 자매(b)
beam(lay, (1406, 40), (1349, 312), 10, 13, (86, 178, 80), 40, 170)        # 초록 들어옴
beam(lay, (1349, 312), (1288, 128), 13, 10, (86, 178, 80), 170, 30)       # 초록 되튐(위 왼쪽)
img = comp(img, lay, 1.2)
# 보라 ~ 청록(두 빛깔 반반) → 당근빛 머리
lay = layer()
beam(lay, (1163, 40), (1101, 414), 9, 10, (150, 96, 206), 40, 160)
beam(lay, (1173, 40), (1110, 414), 9, 10, (64, 170, 182), 40, 160)
img = comp(img, lay, 1.2)
# 흰 눈부심 → 망토(v2 — 자매 머리와 당근 잎 사이로 곧게 내려와 망토 바깥면에 부딪혀 그 자리가 하얗게 탄다)
lay = layer()
beam(lay, (1078, 40), (1031, 528), 16, 30, (255, 252, 236), 120, 245, 30)
d = ImageDraw.Draw(lay)
d.polygon([S(1004, 526), S(1022, 512), S(1046, 514), S(1062, 530), S(1050, 552), S(1020, 556)], fill=(255, 250, 232, 150))   # 망토 주름을 따라 번진 빛(공 꼴 아님)
img = comp(img, lay, 4.0)

# ── ③ 금빛 물결(머리 → 쌍둥이)
def wave(d, p0, p1, amp=3.0, lam=13.0, col=(214, 160, 30, 235), wdt=1.6, phase=0.0):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    pts = []
    for k in range(int(L) + 1):
        t = k; o = amp * math.sin(2 * math.pi * t / lam + phase)
        pts.append(S(x0 + ux * t + nx * o, y0 + uy * t + ny * o))
    d.line(pts, fill=col, width=int(SS * wdt), joint='curve')
def wave_curve(d, p0, c, p1, amp=3.0, lam=13.0, col=(214, 160, 30, 235), wdt=1.6, phase=0.0):
    pts, acc, prev = [], 0.0, None
    N = 400
    for k in range(N + 1):
        t = k / N
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t ** 2 * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t ** 2 * p1[1]
        dx = 2 * (1 - t) * (c[0] - p0[0]) + 2 * t * (p1[0] - c[0]); dy = 2 * (1 - t) * (c[1] - p0[1]) + 2 * t * (p1[1] - c[1])
        L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
        if prev is not None: acc += math.hypot(x - prev[0], y - prev[1])
        prev = (x, y); o = amp * math.sin(2 * math.pi * acc / lam + phase)
        pts.append(S(x + nx * o, y + ny * o))
    d.line(pts, fill=col, width=int(SS * wdt), joint='curve')
lay = layer(); d = ImageDraw.Draw(lay)
for ph, off in ((0.0, 0), (math.pi, 4)):
    wave_curve(d, (1030, 336 - off), (1112, 286 - off), (1176, 464 - off), phase=ph)      # 왼 자매 → 쌍둥이(당근 잎 위로 넘어감)
    wave(d, (1126, 448 - off), (1173, 488 - off), phase=ph)                                 # 당근빛 머리 → 쌍둥이
    wave(d, (1324, 364 - off), (1291, 474 - off), phase=ph)                                 # 오른 자매 → 쌍둥이
img = comp(img, lay)

# ── ④ 브로치
INK = (40, 32, 24, 255)
def twig(d, cx, top, h, spread):
    """세 갈래 잔가지 — 줄기(아래) · 갈래 셋(위)"""
    split = top + h * 0.42; bot = top + h
    BR, BRL = (104, 70, 36, 255), (150, 108, 62, 255)
    tips = [(cx - spread, top + h * 0.06), (cx, top), (cx + spread, top + h * 0.06)]
    for (tx, ty) in tips:
        d.line([S(cx, split), S(tx, ty)], fill=INK, width=int(SS * 3.6))
    d.line([S(cx, bot), S(cx, split)], fill=INK, width=int(SS * 4.2))
    for (tx, ty) in tips:
        d.line([S(cx, split), S(tx, ty)], fill=BR, width=int(SS * 2.0))
    d.line([S(cx, bot), S(cx, split)], fill=BR, width=int(SS * 2.5))
    d.line([S(cx - 0.4, bot - 1), S(cx - 0.4, split + 1)], fill=BRL, width=int(SS * 0.8))
    rH, rC = max(1.5, h * 0.075), max(1.3, h * 0.065)      # 갈래 끝마다 흰 알(H 셋) · 갈라지는 마디는 검은 알(C)
    for (tx, ty) in tips:
        d.ellipse([S(tx - rH, ty - rH), S(tx + rH, ty + rH)], fill=(252, 252, 250, 255), outline=INK, width=int(SS * 0.8))
    d.ellipse([S(cx - rC, split - rC), S(cx + rC, split + rC)], fill=(46, 40, 34, 255), outline=INK, width=int(SS * 0.6))
def fork(d, cx, top, h, wdt):
    """갈퀴 넷 포크 — 자루(아래) · 갈퀴 넷(위)"""
    base = top + h * 0.40; bot = top + h
    SIL, SIL2 = (186, 190, 198, 255), (232, 234, 238, 255)
    xs = [cx - wdt * 0.5 + wdt * k / 3 for k in range(4)]
    d.line([S(cx, bot), S(cx, base + 3)], fill=INK, width=int(SS * 4.4))
    d.rounded_rectangle([S(xs[0] - 1.6, base - 1), S(xs[-1] + 1.6, base + 4)], radius=2 * SS, fill=SIL, outline=INK, width=int(SS * 1.1))
    for x in xs:
        d.line([S(x, base), S(x, top)], fill=INK, width=int(SS * 2.6))
    d.line([S(cx, bot), S(cx, base + 3)], fill=SIL, width=int(SS * 2.6))
    for x in xs:
        d.line([S(x, base), S(x, top + 0.8)], fill=SIL, width=int(SS * 1.2))
    d.line([S(cx - 0.6, bot - 2), S(cx - 0.6, base + 5)], fill=SIL2, width=int(SS * 0.8))
lay = layer(); d = ImageDraw.Draw(lay)
twig(d, 985, 420, 34, 12)       # 왼 자매(a · 메틸기 — 갈래 셋)
fork(d, 1365, 418, 36, 15)      # 오른 자매(b · 포르밀기 — 갈퀴 넷)
twig(d, 1195, 513, 19, 6.5)     # 쌍둥이 왼(a)
twig(d, 1268, 515, 19, 6.5)     # 쌍둥이 오른(a)
img = comp(img, lay)

# ── ⑤ 노란 공(v2 — 쌍둥이가 사발을 맞잡은 손 바로 밑에 대고 있다 · 공이 손에서 곧장 사발로 떨어진다)
lay = layer(); d = ImageDraw.Draw(lay)
for (xa, ya, xb, yb) in [(1236.5, 545.5, 1238.5, 549.0), (1242.0, 545.0, 1243.5, 548.5)]:
    d.line([S(xa, ya), S(xb, yb)], fill=(90, 90, 90, 200), width=int(SS * 0.9))
cx, cy, r = 1240.5, 553.5, 4.4
d.ellipse([S(cx - r, cy - r), S(cx + r, cy + r)], fill=(246, 206, 56, 255), outline=INK, width=int(SS * 1.0))
d.ellipse([S(cx - r * 0.55, cy - r * 0.6), S(cx - r * 0.05, cy - r * 0.15)], fill=(255, 240, 170, 255))
img = comp(img, lay)

# ── ⑥ 걸상 뒤 난간 + 액자 머리 일곱
ty = lambda x: 611 + (x - 1560) * 0.117
rail_top = lambda x: ty(x) - 84
lay = layer(); d = ImageDraw.Draw(lay)
WOOD, WOODL = (138, 100, 62, 255), (170, 130, 86, 255)
for px in (1588, 1838):
    d.rectangle([S(px - 2.2, rail_top(px)), S(px + 2.2, ty(px) - 3)], fill=WOOD, outline=INK, width=int(SS * 0.9))
xa, xb = 1580, 1846
d.polygon([S(xa, rail_top(xa)), S(xb, rail_top(xb)), S(xb, rail_top(xb) + 5), S(xa, rail_top(xa) + 5)], fill=WOOD, outline=INK)
d.line([S(xa + 1, rail_top(xa) + 1.2), S(xb - 1, rail_top(xb) + 1.2)], fill=WOODL, width=int(SS * 1.0))
img = comp(img, lay)
# 띠 경계는 머리 높이에서 잰다
A = np.asarray(img).astype(float) / 255
def band_at(x):
    y = int(rail_top(x) - 11)
    r, g, b = A[y - 1:y + 2, x - 1:x + 2].reshape(-1, 3).mean(axis=0)
    h, s, v = colorsys.rgb_to_hsv(r, g, b); h *= 360
    if s < 0.18: return '.'
    return 'V' if 260 <= h <= 320 else 'B' if 200 <= h < 260 else 'T' if 160 <= h < 200 else 'G' if 80 <= h < 160 else 'Y' if 40 <= h < 80 else 'O' if 15 <= h < 40 else 'R'
import itertools
seq = ''.join(band_at(x) for x in range(1584, 1870))
runs, x = {}, 1584
for c, g in itertools.groupby(seq):
    n = len(list(g))
    if c != '.' and (c not in runs or n > runs[c][1] - runs[c][0] + 1): runs[c] = (x, x + n - 1)
    x += n
centers = {c: (v[0] + v[1]) / 2 for c, v in runs.items()}
print('bands at head line:', runs)
FILL = {'V': (150, 92, 206), 'B': (74, 122, 224), 'R': (214, 58, 48)}
PUR, PURD = (168, 128, 196, 255), (118, 82, 150, 255)
lay = layer(); d = ImageDraw.Draw(lay)
for c in ['V', 'B', 'T', 'G', 'Y', 'O', 'R']:
    if c not in centers: print('missing band', c); continue
    cx = centers[c]
    if c == 'R': cx = runs['R'][0] + 13
    base = rail_top(cx); s = 19.0; x0, y0 = cx - s / 2, base - s
    d.rectangle([S(x0, y0), S(x0 + s, y0 + s)], fill=PUR, outline=INK, width=int(SS * 1.2))
    t = 3.8
    win = FILL.get(c, (246, 246, 242))
    d.rectangle([S(x0 + t, y0 + t), S(x0 + s - t, y0 + s - t)], fill=win + (255,), outline=PURD, width=int(SS * 0.9))
    bx, by, br = cx, y0 + s / 2, 2.7
    d.ellipse([S(bx - br, by - br), S(bx + br, by + br)], fill=(200, 202, 208, 255), outline=INK, width=int(SS * 0.7))
    d.ellipse([S(bx - br * 0.5, by - br * 0.6), S(bx, by - br * 0.1)], fill=(250, 250, 252, 255))
    if c == 'G':   # 초록 V 되튐 — 프리즘 쪽(위 왼)에서 와서 윗변에 맞고 위 오른쪽으로
        GR = (70, 168, 64, 255)
        d.line([S(cx - 9, y0 - 12), S(cx - 1, y0 - 0.5)], fill=GR, width=int(SS * 2.0))
        d.line([S(cx - 1, y0 - 0.5), S(cx + 8, y0 - 12)], fill=GR, width=int(SS * 2.0))
img = comp(img, lay)

# 걸상(v2) — 실 높이 띠 한가운데: 청록 · 주황엔 헤엄이 셋과 작은 방울 둘씩 · 빨강 띠엔 무더기를 보태 보라 · 파랑 무더기만큼
import random
random.seed(45)
tyT = lambda x: 611 + (x - 1560) * 0.117 + 2.5
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
for xc in (1706, 1900):                                   # 청록 · 주황
    for (dx, dy, ang) in [(-8, -3.5, -0.4), (1, -4.5, 0.3), (9, -3.0, -0.1)]:
        bact(d, xc + dx, tyT(xc + dx) + dy, ang)
    bub2(d, xc - 2, tyT(xc) - 14, 3.0); bub2(d, xc + 3, tyT(xc) - 25, 2.4)
for k in range(30):                                        # 빨강 띠 무더기 보태기
    x = random.uniform(1938, 1986); y = tyT(x) + random.uniform(-9, 6)
    bact(d, x, y, random.uniform(-1.4, 1.4), random.uniform(0.85, 1.05))
for (x, dy, r) in [(1946, -16, 3.2), (1958, -27, 2.6), (1968, -15, 3.0), (1952, -38, 2.4), (1975, -30, 2.8), (1962, -48, 2.2)]:
    bub2(d, x, tyT(x) + dy, r)
img = comp(img, lay)
img.save('cur8.png')
for (b, nm, k) in [((880, 290, 1460, 640), 'v8_stage.png', 2), ((1560, 480, 1880, 680), 'v8_rail.png', 3), ((420, 160, 920, 760), 'v8_zoomlines.png', 1)]:
    img.crop(b).resize(((b[2] - b[0]) * k, (b[3] - b[1]) * k), Image.LANCZOS).save(nm)
print('cur8 saved')

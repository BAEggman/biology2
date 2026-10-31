#!/usr/bin/env python3
"""touch_g.py — s45u02 v6(b135 뒤): cur15 → cur16
 ① 행 22 — 주황 띠의 작은 무리(헤엄이 다섯 · 방울 셋)가 빨강 큰 무더기에 붙어 둘 다 「빨강 ≈11」로 합쳐 셌다:
    x 1872–1946 의 실 둘레를 cur5(헤엄이 · 방울 전)로 되돌리고, 빨강 무더기 왼끝(1946 칼자국)을 온전한 헤엄이로 덮어 1937 부터,
    주황 무리는 띠 왼쪽 한가운데(1886)로 옮겨 사이를 40 px 띄운다
 ② 행 17 · 22 — 앞판의 보조 색소 꼬리표: 청록 칸 = [청록 b 머리 · 빈 a 머리 · 당근] · 주황 칸 = [주황 b 머리 · 빈 a 머리]
    (b 머리를 무리 바로 밑으로 옮기고 청록 칸에도 하나 — b 는 a 의 바로 곁 칸(청록 · 주황)을 받는다) · 꼬리표에서 바로 위 무리까지 그 빛깔의 빛기둥
 ③ 행 18 — 실 마디를 그 자리 띠 빛깔로 짙게(0.42 → 0.72) — 실이 끝까지 초록으로 읽혔다
 ④ 행 4 — 무더기 · 낱장 머리를 4.6 → 5.4 px(같은 자리 · 같은 씨앗) — 「점처럼 작다」
 ⑤ 행 2 — 관다발 관 입구 다섯에 맑은 물(파란 물 · 물빛 반짝임) · 맨 아래 관 끝에 물방울 하나 — 「속 빈 금속관」으로 읽혔다
 ⑥ 행 9 — 놓친 공의 빛(형광)을 김보다 크게: 흰 빛무리 + 짧은 빛살 여섯
 ⑦ 행 14 — 꼬리 끝 입술 선 · 주름을 짙게"""
import sys, os, math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
img = Image.open('cur15.png').convert('RGB'); W, H = img.size
C5c = np.asarray(Image.open('cur5c.png').convert('RGB')).astype(float)
C5 = np.asarray(Image.open('cur5.png').convert('RGB')).astype(float)
C14 = np.asarray(Image.open('cur14.png').convert('RGB')).astype(float)
SS = 4
S = lambda x, y: (x * SS, y * SS)
INK = (40, 32, 24, 255)
def layer(): return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
def comp(img, lay, blur=0):
    small = lay.resize((W, H), Image.LANCZOS)
    if blur: small = small.filter(ImageFilter.GaussianBlur(blur))
    im2 = img.convert('RGBA'); im2.alpha_composite(small); return im2.convert('RGB')
ty = lambda x: 611 + (x - 1560) * 0.117
tyT = lambda x: ty(x) + 2.5
A = np.asarray(img).astype(float)
yy, xx = np.mgrid[0:H, 0:W]

# ── ③ 실 물들임(먼저 — ① 에서 되돌린 자리는 덮인 것이 없다)
thread = (np.abs(C5 - C5c).max(axis=2) > 12) & (xx >= 1566) & (xx <= 2000) & (np.abs(yy - (611 + (xx - 1560) * 0.117 + 2.5)) <= 5)
band = np.zeros_like(A)
for x in range(1566, 2001):
    yb = int(ty(x) - 10)
    band[:, x] = C5c[yb - 1:yb + 2, x - 2:x + 3].reshape(-1, 3).mean(axis=0)
T5 = C5 * 0.58 + band * 0.42                                        # touch_f ④ 가 칠한 값
rest = (xx >= 1872) & (xx < 1946) & (yy >= np.maximum(611 + (xx - 1560) * 0.117 + 2.5 - 50, 603)) & (yy <= 611 + (xx - 1560) * 0.117 + 2.5 + 12)
A[rest] = C5[rest]                                                  # ① 주황 · 칼자국 자리 되돌림
uncovered = thread & ((np.abs(A - T5).max(axis=2) < 12) | rest)
al = 0.72
A[uncovered] = C5[uncovered] * (1 - al) + band[uncovered] * al
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
print('thread px', int(uncovered.sum()), 'restored px', int(rest.sum()))

# ── ① 빨강 무더기 왼끝 덮기 · 주황 무리 옮기기
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
random.seed(135)
lay = layer(); d = ImageDraw.Draw(lay)
for k in range(18):
    x = random.uniform(1938.0, 1953.0); y = tyT(x) + random.uniform(-14.0, 7.0)
    bact(d, x, y, random.uniform(-1.5, 1.5), random.uniform(0.85, 1.05))
for (x, dy, r) in [(1941, -22, 2.8), (1949, -33, 2.4)]:
    bub2(d, x, tyT(x) + dy, r)
xo = 1886.0
for (dx, dy, ang) in [(-11, -3.0, -0.4), (-4, -5.0, 0.3), (3, -2.5, -0.1), (9, -5.5, 0.5), (14, -2.0, -0.3)]:
    bact(d, xo + dx, tyT(xo + dx) + dy, ang)
for (dx, dy, r) in [(-3, -16, 3.0), (4, -28, 2.6), (-1, -40, 2.3)]:
    bub2(d, xo + dx, tyT(xo) + dy, r)
img = comp(img, lay)

# ── ② 앞판 꼬리표: 주황 b 머리를 무리 바로 밑(빈 a 머리 왼쪽)으로 · 청록 칸에도 b 머리(빈 a 머리 왼쪽)
A = np.asarray(img).astype(float)
oldtag = (xx >= 1905) & (xx <= 1925) & (yy >= 611 + (xx - 1560) * 0.117 + 19) & (yy <= 611 + (xx - 1560) * 0.117 + 42)
A[oldtag] = C14[oldtag]                                             # touch_f 가 단 오른쪽 b 머리를 걷는다(앞판 나무로)
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
PUR, PURD = (168, 128, 196, 255), (118, 82, 150, 255)
def head(d, cx, top, s, win, bead=2.3):
    x0 = cx - s / 2
    d.rectangle([S(x0, top), S(x0 + s, top + s)], fill=PUR, outline=INK, width=int(SS * 1.1))
    t = s * 0.2
    d.rectangle([S(x0 + t, top + t), S(x0 + s - t, top + s - t)], fill=win + (255,), outline=PURD, width=int(SS * 0.8))
    d.ellipse([S(cx - bead, top + s / 2 - bead), S(cx + bead, top + s / 2 + bead)], fill=(200, 202, 208, 255), outline=INK, width=int(SS * 0.6))
    d.ellipse([S(cx - bead * 0.5, top + s / 2 - bead * 0.6), S(cx, top + s / 2 - bead * 0.1)], fill=(250, 250, 252, 255))
    d.ellipse([S(cx - 0.9, top - 1.6), S(cx + 0.9, top + 0.2)], fill=(70, 62, 54, 255))
def btag(d, xc, win, side):
    top = ty(xc) + 23.4
    head(d, xc, top, 13.0, win, bead=1.9)
    base = xc + (2.2 if side > 0 else -6.7)
    fx = [base + 1.5 * k for k in range(4)]
    for (col, wk) in ((INK, 1.0), ((214, 218, 224, 255), 0.0)):
        for x in fx:
            d.line([S(x, top + 7.6), S(x, top + 10.6)], fill=col, width=int(SS * (0.7 + wk)))
        d.line([S(fx[0], top + 10.6), S(fx[-1], top + 10.6)], fill=col, width=int(SS * (0.85 + wk)))
        d.line([S((fx[0] + fx[-1]) / 2, top + 10.6), S((fx[0] + fx[-1]) / 2, top + 15.0)], fill=col, width=int(SS * (1.0 + wk)))
# 빛기둥(꼬리표 → 바로 위 무리) — 앞판 윗변부터 실까지
lay = layer(); d = ImageDraw.Draw(lay)
for (x0, x1, col) in [(1683.0, 1727.0, (90, 200, 205)), (1872.0, 1900.0, (245, 150, 60))]:
    for k in range(10):
        a = int(70 * (1 - k / 10) + 25)
        ya = tyT((x0 + x1) / 2) - 8 + k * 3.2
        d.rectangle([S(x0 + 2, ya), S(x1 - 2, ya + 3.4)], fill=col + (a,))
img = comp(img, lay, 3.0)
lay = layer(); d = ImageDraw.Draw(lay)
btag(d, 1689.5, (84, 176, 178), -1)                                  # 청록 칸 b(포크는 왼 아래)
btag(d, 1881.0, (238, 136, 44), -1)                                  # 주황 칸 b(무리 바로 밑)
img = comp(img, lay)

# ── ④ 머리 키우기(touch_f ② 와 같은 씨앗 · 같은 자리)
STK = {
    'TL': (630.0, 728.0, [323.5, 332.5, 342.0, 351.5, 361.5, 372.0]),
    'TR': (740.0, 802.0, [394.0, 403.0, 411.0, 419.0, 427.5, 436.0]),
    'ML': (586.0, 678.0, [434.5, 444.5, 453.0, 461.0, 470.5, 481.5]),
    'MR': (742.0, 806.0, [502.0, 513.0, 523.0, 532.0, 542.0, 550.0]),
    'LL': (582.0, 674.0, [547.5, 555.5, 562.0, 569.0, 577.5, 588.5, 598.5]),
    'LR': (740.0, 798.0, [608.5, 617.0, 627.0, 638.0, 650.5, 661.5, 669.5]),
}
LONE = (697.0, 765.0, 695.4)
P2, P2D = (156, 108, 196, 255), (70, 44, 96, 255)
random.seed(45)
lay = layer(); d = ImageDraw.Draw(lay); s = 5.4
def dot(x, y):
    d.rectangle([S(x - s / 2, y - s / 2), S(x + s / 2, y + s / 2)], fill=P2, outline=P2D, width=int(SS * 0.85))
    d.rectangle([S(x - s * 0.18, y - s * 0.18), S(x + s * 0.18, y + s * 0.18)], fill=(250, 250, 248, 255))
for nm, (xl, xr, ys) in STK.items():
    for j, y in enumerate(ys):
        off = ((j % 3) - 1) * 0.07
        for k in range(3):
            x = xl + (xr - xl) * (0.2 + 0.3 * k + off) + random.uniform(-2.0, 2.0)
            dot(x, y + random.uniform(-0.4, 0.4))
xl, xr, yc = LONE
for k, jx in enumerate((-0.03, 0.02, -0.01)):
    dot(xl + (xr - xl) * (0.2 + 0.3 * k + jx), yc)
img = comp(img, lay)

# ── ⑤ 관 입구 다섯에 맑은 물 · 물방울
OPEN = [(180.0, 450.0), (148.8, 472.5), (207.5, 480.0), (156.3, 508.8), (188.8, 513.8)]
lay = layer(); d = ImageDraw.Draw(lay)
for (cx, cy) in OPEN:
    r = 8.0
    d.ellipse([S(cx - r, cy - r), S(cx + r, cy + r)], fill=(96, 164, 226, 165))
    d.chord([S(cx - r, cy - r), S(cx + r, cy + r)], 20, 160, fill=(60, 126, 206, 150))                       # 아래쪽 짙은 물
    d.arc([S(cx - r * 0.7, cy - r * 0.75), S(cx + r * 0.35, cy + r * 0.2)], 200, 290, fill=(250, 252, 255, 235), width=int(SS * 1.2))   # 물빛 반짝임
img = comp(img, lay)
lay = layer(); d = ImageDraw.Draw(lay)
dx_, dy_ = 151.0, 524.5                                              # 맨 아래 왼쪽 관 끝에서 떨어지는 물방울
T = np.linspace(0, 2 * math.pi, 60)
pts = [S(dx_ + 2.6 * math.sin(t) * abs(math.sin(t / 2)) ** 0.8 * 1.2, dy_ - 3.6 * math.cos(t)) for t in T]
d.polygon(pts, fill=(96, 164, 226, 255)); d.line(pts + [pts[0]], fill=(40, 70, 120, 255), width=int(SS * 0.8))
d.ellipse([S(dx_ - 1.2, dy_ - 0.2), S(dx_ - 0.1, dy_ + 1.6)], fill=(245, 250, 255, 255))
img = comp(img, lay)

# ── ⑥ 놓친 공의 빛(형광) — 흰 빛무리 + 짧은 빛살
bx, by = 1280.5, 646.0
lay = layer(); d = ImageDraw.Draw(lay)
for (rr, a) in [(17, 40), (12, 70), (8.5, 110)]:
    d.ellipse([S(bx - rr, by - rr * 0.85), S(bx + rr, by + rr * 0.85)], fill=(255, 250, 200, a))
img = comp(img, lay, 2.5)
lay = layer(); d = ImageDraw.Draw(lay)
for ang in (200, 235, 305, 340, 20, 160):
    t = math.radians(ang)
    d.line([S(bx + 9.5 * math.cos(t), by + 8.0 * math.sin(t)), S(bx + 15.5 * math.cos(t), by + 13.0 * math.sin(t))], fill=(255, 236, 120, 230), width=int(SS * 1.1))
img = comp(img, lay)

# ── ⑦ 꼬리 끝 입술 · 주름 짙게
TIPS = [(933.0, 657.6, 12.0), (1427.2, 657.6, 12.0), (1167.6, 590.8, 9.0), (1298.2, 598.6, 9.0)]
lay = layer(); d = ImageDraw.Draw(lay)
for (x, y, w) in TIPS:
    wl = w * 0.62; h = w * 0.36
    d.line([S(x + (wl / 2 + 0.8) * math.cos(t), y - 1.9 + h * 0.34 * math.sin(t)) for t in np.linspace(0.05, math.pi - 0.05, 30)], fill=(30, 58, 30, 230), width=int(SS * 1.1))
    for (ang, L) in ((205, 0.42), (335, 0.42), (165, 0.36), (15, 0.36)):
        t = math.radians(ang); ex, ey = x + (wl / 2 + 0.8) * math.cos(t), y - 1.4 + h * 0.6 * math.sin(t)
        d.line([S(ex, ey), S(ex + w * L * math.cos(t), ey + w * L * 0.45 * math.sin(t))], fill=(36, 70, 36, 170), width=int(SS * 0.8))
img = comp(img, lay)
img.save('cur16.png')
for (b, nm, k) in [((1560, 560, 2010, 720), 'v16_bench.png', 2), ((560, 290, 820, 710), 'v16_stacks.png', 2), ((120, 420, 300, 540), 'v16_tubes.png', 3), ((1240, 610, 1320, 680), 'v16_ball.png', 5)]:
    img.crop(b).resize(((b[2] - b[0]) * k, (b[3] - b[1]) * k), Image.LANCZOS).save(nm)
print('cur16 saved')

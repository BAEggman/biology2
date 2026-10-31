#!/usr/bin/env python3
"""touch_f.py — s45u02 v5(b134 뒤): cur14 → cur15
 ① 행 22 · 10 · 21 — 걸상 뒤 난간(머리 일곱 · 기둥 · 초록 V)을 걷고, 흡수 머리 일곱을 **걸상 앞판**에 띠마다 그 띠의 실 바로 밑에 붙인다
    (b134: 난간 머리 x 1590–1790 이 실 위 띠 자리 x 1575–2000 과 세로로 안 맞아 청록 무리 위에 노랑 머리가 섰다 — 머리 줄과 방울 줄을 위아래로 맞선다)
    빈 청록 머리 곁엔 작은 당근(청록 빛 무리) · 빈 주황 머리 곁엔 포크를 단 작은 b 머리(주황으로 참) · 초록 머리는 V 없이 비움(「✓」로 읽혔다)
 ② 행 4 — 무더기 여섯의 겹마다 머리 셋(왼 셋 · 오른 둘이 「3:2 의 뜻 모름」으로 걸렸다) · 바닥 낱장 쿠션도 셋
 ③ 행 17 — 자매마다 빛살 둘: a 파랑 + 빨강 · b 청록 + 주황(b 의 빛이 a 의 바로 곁 틈으로 든다) · 액자 속도 두 빛깔로 반씩
 ④ 행 18 — 사상조류 실의 마디를 그 자리 띠 빛으로 물들인다(한 오라기가 일곱 빛을 한꺼번에 받는다)
 ⑤ 빛살 여섯을 틀 윗변(y 19)까지 잇는다(b134 A 「빛줄기가 같은 높이에서 끊김」)"""
import sys, os, math, random, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import binary_dilation
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
img = Image.open('cur14.png').convert('RGB'); W, H = img.size
C5c = np.asarray(Image.open('cur5c.png').convert('RGB')).astype(float)
C5 = np.asarray(Image.open('cur5.png').convert('RGB')).astype(float)
C7 = np.asarray(Image.open('cur7.png').convert('RGB')).astype(float)
C8 = np.asarray(Image.open('cur8.png').convert('RGB')).astype(float)
SS = 4
S = lambda x, y: (x * SS, y * SS)
INK = (40, 32, 24, 255)
def layer(): return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
def comp(img, lay, blur=0):
    small = lay.resize((W, H), Image.LANCZOS)
    if blur: small = small.filter(ImageFilter.GaussianBlur(blur))
    im2 = img.convert('RGBA'); im2.alpha_composite(small); return im2.convert('RGB')
ty = lambda x: 611 + (x - 1560) * 0.117
rail_top = lambda x: ty(x) - 84

# ── ① 난간 걷기 — touch_b ⑥ 이 그린 화소(cur8 − cur7)만: 난간 판 · 머리 · V(난간 윗변 + 7 위) · 기둥 둘
A = np.asarray(img).astype(float)
yy, xx = np.mgrid[0:H, 0:W]
dif = np.abs(C8 - C7).max(axis=2) > 8
box = (xx >= 1572) & (xx <= 1876) & (yy >= 470) & (yy <= 650)
above = yy < (611 + (xx - 1560) * 0.117 - 84 + 7)
posts = ((np.abs(xx - 1588) <= 3.6) | (np.abs(xx - 1838) <= 3.6)) & (yy <= 611 + (xx - 1560) * 0.117)
M = binary_dilation(dif & box & (above | posts), iterations=1)
# G3(안개 속 둘을 앞모습으로) 조각이 바꾼 화소만 메우고(inpaint) 나머지는 cur7(난간을 긋기 전)로 되돌린다
G3 = np.abs(np.asarray(Image.open('cur13.png').convert('RGB')).astype(float) - np.asarray(Image.open('cur12.png').convert('RGB')).astype(float)).max(axis=2) > 6
G3 = binary_dilation(G3, iterations=2)
back = M & ~G3
A[back] = C7[back]
right = (M & G3).astype(np.uint8)
A8 = np.clip(A, 0, 255).astype(np.uint8)
A8 = cv2.inpaint(A8, right, 5, cv2.INPAINT_TELEA)
img = Image.fromarray(A8)
print('rail px removed', int(M.sum()))

# ── ① 걸상 앞판의 흡수 머리 일곱 — 띠 가운데(실 높이에서 잰 띠)의 바로 밑, 앞판(ty+21.5 ~ ty+39.5) 위에
BANDS = [('V', 1603.0), ('B', 1652.0), ('T', 1705.5), ('G', 1764.0), ('Y', 1828.0), ('O', 1897.5), ('R', 1964.5)]
FILL = {'V': (150, 92, 206), 'B': (74, 122, 224), 'R': (214, 58, 48)}
PUR, PURD = (168, 128, 196, 255), (118, 82, 150, 255)
def head(d, cx, top, s, win, bead=2.3):
    x0 = cx - s / 2
    d.rectangle([S(x0, top), S(x0 + s, top + s)], fill=PUR, outline=INK, width=int(SS * 1.1))
    t = s * 0.2
    d.rectangle([S(x0 + t, top + t), S(x0 + s - t, top + s - t)], fill=win + (255,), outline=PURD, width=int(SS * 0.8))
    d.ellipse([S(cx - bead, top + s / 2 - bead), S(cx + bead, top + s / 2 + bead)], fill=(200, 202, 208, 255), outline=INK, width=int(SS * 0.6))
    d.ellipse([S(cx - bead * 0.5, top + s / 2 - bead * 0.6), S(cx, top + s / 2 - bead * 0.1)], fill=(250, 250, 252, 255))
    d.ellipse([S(cx - 0.9, top - 1.6), S(cx + 0.9, top + 0.2)], fill=(70, 62, 54, 255))          # 앞판에 박은 못
s_h = 16.0
lay = layer(); d = ImageDraw.Draw(lay)
for (c, xc) in BANDS:
    top = ty(xc) + 22.6
    head(d, xc, top, s_h, FILL.get(c, (246, 246, 242)))
img = comp(img, lay)
# 청록 곁의 작은 당근(청록 빛 무리) · 주황 곁의 작은 b 머리(주황으로 참 · 포크 브로치)
xT = dict(BANDS)['T'] + 15.5; topT = ty(xT) + 22.0
lay = layer(); d = ImageDraw.Draw(lay)
d.ellipse([S(xT - 8, topT - 1), S(xT + 8, topT + 17)], fill=(80, 190, 196, 150))
img = comp(img, lay, 2.0)
lay = layer(); d = ImageDraw.Draw(lay)
car = [S(xT - 4.4, topT + 4.5), S(xT + 4.4, topT + 4.5), S(xT + 0.9, topT + 17.0), S(xT - 0.9, topT + 17.0)]
d.polygon(car, fill=(236, 126, 40, 255), outline=INK)
for k in range(3):
    y_ = topT + 7.0 + k * 3.2
    d.line([S(xT - 3.0 + k * 0.7, y_), S(xT - 0.8 + k * 0.5, y_ + 0.5)], fill=(170, 80, 20, 255), width=int(SS * 0.6))
for (dx, dy) in [(-3.0, -4.6), (0, -6.0), (3.0, -4.6)]:
    d.line([S(xT, topT + 4.5), S(xT + dx, topT + 4.5 + dy)], fill=(60, 140, 50, 255), width=int(SS * 1.4))
img = comp(img, lay)
xO = dict(BANDS)['O'] + 16.5; topO = ty(xO) + 23.4
lay = layer(); d = ImageDraw.Draw(lay)
head(d, xO, topO, 13.0, (238, 136, 44), bead=1.9)
fx = [xO + 2.2 + 1.5 * k for k in range(4)]                     # 포크(갈퀴 넷) — 액자 오른 아래 귀퉁이에 꽂힘
for (col, wk) in ((INK, 1.0), ((214, 218, 224, 255), 0.0)):
    for x in fx:
        d.line([S(x, topO + 7.6), S(x, topO + 10.6)], fill=col, width=int(SS * (0.7 + wk)))
    d.line([S(fx[0], topO + 10.6), S(fx[-1], topO + 10.6)], fill=col, width=int(SS * (0.85 + wk)))
    d.line([S((fx[0] + fx[-1]) / 2, topO + 10.6), S((fx[0] + fx[-1]) / 2, topO + 15.0)], fill=col, width=int(SS * (1.0 + wk)))
img = comp(img, lay)

# ── ② 무더기 겹마다 머리 셋 · 낱장 셋(touch_d ① · touch_e ② 는 --v5 에서 뺐다)
STK = {  # 이름: (왼 x, 오른 x, [겹 앞면 가운데 y …]) — 눈금 확대(grid_*.png)로 잰 윤곽 사이 가운데
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
lay = layer(); d = ImageDraw.Draw(lay); s = 4.6
def dot(x, y):
    d.rectangle([S(x - s / 2, y - s / 2), S(x + s / 2, y + s / 2)], fill=P2, outline=P2D, width=int(SS * 0.8))
    d.rectangle([S(x - s * 0.18, y - s * 0.18), S(x + s * 0.18, y + s * 0.18)], fill=(250, 250, 248, 255))
for nm, (xl, xr, ys) in STK.items():
    for j, y in enumerate(ys):
        off = ((j % 3) - 1) * 0.07                                  # 겹마다 비껴 놓아 단추 줄(누빔)로 서지 않게
        for k in range(3):
            x = xl + (xr - xl) * (0.2 + 0.3 * k + off) + random.uniform(-2.0, 2.0)
            dot(x, y + random.uniform(-0.4, 0.4))
xl, xr, yc = LONE
for k, jx in enumerate((-0.03, 0.02, -0.01)):
    dot(xl + (xr - xl) * (0.2 + 0.3 * k + jx), yc)
img = comp(img, lay)

# ── ③ 자매마다 빛살 둘 — a: + 빨강(파랑 왼쪽) · b: + 주황(초록과 청록 사이) · ⑤ 기존 빛살을 틀 윗변까지
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
def extend(lay, p0, p1, w0, w1, col, a0, top=19.0):
    """touch_b 의 빛살 (p0 → p1) 을 같은 기울기로 틀 윗변까지 — 짙기는 0 → a0"""
    (x0, y0), (x1, y1) = p0, p1
    k = (x1 - x0) / (y1 - y0); wk = (w1 - w0) / (y1 - y0)
    xt = x0 + k * (top - y0); wt = w0 + wk * (top - y0)
    beam(lay, (xt, top), (x0, y0), wt, w0, col, int(a0 * 0.35), a0, 8)
lay = layer()
for (p0, p1, w0, w1, col, a0) in [((1050, 40), (994, 318), 14, 20, (92, 140, 228), 40), ((1438, 40), (1380, 314), 14, 20, (70, 172, 176), 40),
                                  ((1406, 40), (1349, 312), 10, 13, (86, 178, 80), 40), ((1163, 40), (1101, 414), 9, 10, (150, 96, 206), 40),
                                  ((1173, 40), (1110, 414), 9, 10, (64, 170, 182), 40)]:
    extend(lay, p0, p1, w0, w1, col, a0)
beam(lay, (1031.0, 19.0), (972.0, 321.0), 11, 16, (214, 58, 48), 16, 150, 26)          # a 의 빨강
beam(lay, (1425.0, 19.0), (1364.0, 316.0), 9, 12, (240, 140, 40), 16, 160, 26)          # b 의 주황
img = comp(img, lay, 1.2)
lay = layer()
extend(lay, (1078, 40), (1031, 528), 16, 30, (255, 252, 236), 120)
img = comp(img, lay, 4.0)
# 액자 속을 두 빛깔로 반씩(a: 왼 빨강 · 오른 파랑 / b: 왼 주황 · 오른 청록) — 이미 물든 화소만 갈아 칠한다
A = np.asarray(img).astype(float)
def resplit(box, ball, col_old, col_new, xsplit):
    x0, y0, x1, y1 = box
    sub = A[y0:y1, x0:x1]
    tgt = 0.38 * 245 + 0.62 * np.array(col_old, float)
    m = (np.abs(sub - tgt).max(axis=2) < 34)
    ys_, xs_ = np.mgrid[y0:y1, x0:x1]
    m &= (xs_ < xsplit) & ((xs_ - ball[0]) ** 2 + (ys_ - ball[1]) ** 2 > (ball[2] + 1.5) ** 2)
    new = 0.38 * 245 + 0.62 * np.array(col_new, float)
    sub[m] = sub[m] - tgt + new
    A[y0:y1, x0:x1] = sub
    return int(m.sum())
print('split a', resplit((960, 323, 1015, 388), (985, 353, 13), (96, 150, 232), (214, 70, 58), 985.5))
print('split b', resplit((1332, 318, 1382, 388), (1355, 352, 14), (84, 176, 178), (238, 140, 48), 1355.5))
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))

# ── ④ 실 마디를 그 자리 띠 빛으로 — 실 화소(cur5 − cur5c) 가운데 뒤에 덮이지 않은 곳만(헤엄이 · 방울은 그대로)
A = np.asarray(img).astype(float)
thread = (np.abs(C5 - C5c).max(axis=2) > 12) & (np.abs(A - C5).max(axis=2) < 10)
thread &= (xx >= 1566) & (xx <= 2000) & (np.abs(yy - (611 + (xx - 1560) * 0.117 + 2.5)) <= 5)
band = np.zeros_like(A)
for x in range(1566, 2001):
    yb = int(ty(x) - 10)
    band[:, x] = C5c[yb - 1:yb + 2, x - 2:x + 3].reshape(-1, 3).mean(axis=0)
al = 0.42
A[thread] = A[thread] * (1 - al) + band[thread] * al
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
print('thread px tinted', int(thread.sum()))

img.save('cur15.png')
for (b, nm, k) in [((1560, 470, 2020, 720), 'v15_bench.png', 2), ((560, 290, 820, 710), 'v15_stacks.png', 2), ((930, 0, 1460, 400), 'v15_beams.png', 1)]:
    img.crop(b).resize(((b[2] - b[0]) * k, (b[3] - b[1]) * k), Image.LANCZOS).save(nm)
print('cur15 saved')

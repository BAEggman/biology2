#!/usr/bin/env python3
"""touch_h5.py — s45u02 v8 ⑤ 행 17 · 22: 걸상 앞판(a 줄) 바로 아래, 앞다리 사이에 **가로대(b 줄)**를 대고
b 의 흡수 칸 일곱을 a 줄과 같은 x 에 맞춰 박는다 — b 는 파랑 · 청록 · 주황이 참(a 의 찬 칸 보라 · 파랑 · 빨강에서 한 칸씩 안쪽)
· 줄 머리에 a = 세 갈래 잔가지 · b = 포크(약속 #165 · #166) · 옛 b 꼬리표 둘(빈 a 머리 곁)은 걷고(cur14 앞판으로)
· b 줄의 청록 · 주황 칸에서 바로 위 실의 작은 무리까지 빛기둥(빈 a 머리 뒤로 지나감).
(b138: 빛띠로 a · b 의 빛깔은 정확히 읽혔지만 「한 칸씩 = 조금」을 말하지 않았다 — 위아래로 맞선 두 줄이면 「바로 곁 칸」이 자리로 선다 · 독립 검토 2순위)
사용: touch_h5.py in.png cur14.png out.png [--v10]"""
import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
src, c14, dst = sys.argv[1:4]
img = Image.open(src).convert('RGB'); W, H = img.size
A = np.asarray(img).astype(float); C14 = np.asarray(Image.open(c14).convert('RGB')).astype(float)
SS = 4; S = lambda x, y: (x * SS, y * SS)
INK = (40, 32, 24, 255)
ty = lambda x: 611 + (x - 1560) * 0.117
tyT = lambda x: ty(x) + 2.5
abot = lambda x: 655 + (x - 1600) * 0.122            # 앞판 아랫선(잼: 1600 → 655 · 1800 → 680 · 1945 → 699)
rtop = lambda x: abot(x) + 9.0                      # 가로대 윗선
RH = 20.0                                           # b 칸을 a 칸과 같은 16 px 로(같은 자로 견준다 — v4 교훈)
XL, XR = 1574.0, 1982.0                             # 왼 앞다리 안쪽(1573) ~ 오른 앞다리 바깥(1987) — v9: 오른 다리 앞을 지나 빨강 칸까지(b139 「b 줄 일곱째가 다리 위에 떠 있다」)
if '--v10' in sys.argv:                              # v10(b140 닻대조 「가로대 왼끝이 왼 앞다리에 안 닿고 허공에서 끊김」): 왼 앞다리 바른 테(1567)까지
    XL = 1567.0
yy, xx = np.mgrid[0:H, 0:W]

def pm_blur(im, sig):
    """RGBA 흐림을 미리 곱한 알파로 — PIL 의 RGBA 흐림은 투명 화소의 검은 RGB 를 가장자리에 섞어 테를 어둡게 한다(v9 에서 찾음 · 흰 눈부심의 회색 테)."""
    import numpy as _np
    from scipy.ndimage import gaussian_filter as _gf
    a = _np.asarray(im).astype(float); al = a[..., 3:4] / 255.0
    pm = _gf(a[..., :3] * al, (sig, sig, 0)); ab = _gf(al, (sig, sig, 0))
    rgb = pm / _np.maximum(ab, 1e-6)
    return Image.fromarray(_np.clip(_np.concatenate([rgb, ab * 255.0], axis=2), 0, 255).astype('uint8'), 'RGBA')

# ── 1. 옛 b 꼬리표 둘 걷기(cur14 = 머리를 박기 전 앞판) — 가장자리 2 px 은 천천히
M = np.zeros((H, W))
for (x0, x1, y0, y1) in [(1679, 1697, 646, 669), (1871, 1889, 668, 691)]:
    m = np.zeros((H, W)); m[y0:y1, x0:x1] = 1.0
    M = np.maximum(M, np.clip(gaussian_filter(m, 1.0) * 1.6, 0, 1))
A = A * (1 - M[..., None]) + C14 * M[..., None]

# ── 2. 가로대: cur14 앞판의 나무 결(ty+22 ~ ty+38)을 그대로 떠서 아래로 · 그늘 0.86
for x in range(int(XL), int(XR) + 1):
    t0 = rtop(x)
    for k in range(int(RH)):
        ys = int(round(ty(x) + 25 + k * 12.0 / RH)); yd = int(round(t0 + k))
        A[yd, x] = C14[ys, x] * 0.86
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
d.line([S(XL, rtop(XL)), S(XR, rtop(XR))], fill=INK, width=int(SS * 1.6))
d.line([S(XL, rtop(XL) + RH), S(XR, rtop(XR) + RH)], fill=INK, width=int(SS * 1.6))
d.line([S(XL + 0.5, rtop(XL)), S(XL + 0.5, rtop(XL) + RH)], fill=INK, width=int(SS * 1.2))
d.line([S(XR - 0.5, rtop(XR)), S(XR - 0.5, rtop(XR) + RH)], fill=INK, width=int(SS * 1.2))
d.polygon([S(XL, rtop(XL) + RH), S(XR, rtop(XR) + RH), S(XR, rtop(XR) + RH + 4), S(XL, rtop(XL) + RH + 4)], fill=(30, 26, 22, 70))   # 가로대 밑 그늘
small = lay.resize((W, H), Image.LANCZOS)
im2 = img.convert('RGBA'); im2.alpha_composite(small); img = im2.convert('RGB')

# ── 3. b 줄 일곱 칸 + 줄 머리 표지
PUR, PURD = (168, 128, 196, 255), (118, 82, 150, 255)
COL = {1603.0: (150, 96, 206), 1652.0: (92, 140, 228), 1705.5: (64, 170, 182), 1764.0: (86, 178, 80),
       1828.0: (236, 206, 64), 1897.5: (240, 140, 40), 1964.5: (214, 58, 48)}
LIT_B = {1652.0, 1705.5, 1897.5}
def head(d, cx, top, s, win, bead=1.9):
    x0 = cx - s / 2
    d.rectangle([S(x0, top), S(x0 + s, top + s)], fill=PUR, outline=INK, width=int(SS * 1.0))
    t = s * 0.2
    d.rectangle([S(x0 + t, top + t), S(x0 + s - t, top + s - t)], fill=win + (255,), outline=PURD, width=int(SS * 0.7))
    d.ellipse([S(cx - bead, top + s / 2 - bead), S(cx + bead, top + s / 2 + bead)], fill=(200, 202, 208, 255), outline=INK, width=int(SS * 0.5))
    d.ellipse([S(cx - bead * 0.5, top + s / 2 - bead * 0.6), S(cx, top + s / 2 - bead * 0.1)], fill=(250, 250, 252, 255))
    d.ellipse([S(cx - 0.8, top - 1.4), S(cx + 0.8, top + 0.2)], fill=(70, 62, 54, 255))
# 빛기둥 먼저(머리 · 앞판 a 머리 뒤로 지나가게 — a 머리 자리는 가림)
colay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dc = ImageDraw.Draw(colay)
for xc in (1705.5, 1897.5):
    col = (70, 186, 196) if xc < 1800 else (246, 150, 56)
    ybot = rtop(xc) + 2.0; ytop = tyT(xc) - 5.0
    for k in range(30):
        ya = ytop + (ybot - ytop) * k / 30; yb = ytop + (ybot - ytop) * (k + 1) / 30
        dc.rectangle([S(xc - 2.5, ya), S(xc + 2.5, yb)], fill=col + (int(150 - 30 * k / 30),))
    dc.ellipse([S(xc - 7, ytop - 5), S(xc + 7, ytop + 3)], fill=col + (80,))
cs = pm_blur(colay.resize((W, H), Image.LANCZOS), 0.8)
ca = np.asarray(cs).astype(float)
for xc in (1705.5, 1897.5):                                    # 앞판 a 머리(16 px) 자리는 기둥을 지움 — 머리 뒤로 지나감
    top = ty(xc) + 22.6
    ca[int(top) - 1:int(top + 16) + 2, int(xc - 8) - 1:int(xc + 8) + 2, 3] = 0
cs = Image.fromarray(np.clip(ca, 0, 255).astype('uint8'), 'RGBA')
im2 = img.convert('RGBA'); im2.alpha_composite(cs); img = im2.convert('RGB')
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
FULL = {1652.0: (74, 122, 224), 1705.5: (64, 170, 182), 1897.5: (240, 140, 40)}   # a 줄의 찬 칸과 같은 짙기(touch_f FILL)
for xc, c in COL.items():
    win = FULL[xc] if xc in LIT_B else tuple(int(v) for v in (0.86 * 247 + 0.14 * np.array(c)))
    head(d, xc, rtop(xc) + 2.0, 16.0, win, bead=2.3)
# 줄 머리 — a 줄: 세 갈래 잔가지 · b 줄: 포크
def twig(d, cx, cy, k=1.35):
    d.line([S(cx, cy + 4.5 * k), S(cx, cy)], fill=INK, width=int(SS * 1.3))
    for ang in (-50, 0, 50):
        a = math.radians(ang); ex, ey = cx + 4.2 * k * math.sin(a), cy - 4.2 * k * math.cos(a)
        d.line([S(cx, cy), S(ex, ey)], fill=INK, width=int(SS * 1.2))
        d.ellipse([S(ex - 1.4, ey - 1.4), S(ex + 1.4, ey + 1.4)], fill=(252, 252, 250, 255), outline=INK, width=int(SS * 0.5))
    d.ellipse([S(cx - 1.6, cy - 1.6), S(cx + 1.6, cy + 1.6)], fill=(20, 16, 12, 255))
def fork(d, cx, cy, k=1.35):
    fx = [cx - 2.4 * k + 1.6 * k * j for j in range(4)]
    for (col, wk) in ((INK, 1.0), ((214, 218, 224, 255), 0.0)):
        for x in fx:
            d.line([S(x, cy - 4.5 * k), S(x, cy - 0.8)], fill=col, width=int(SS * (0.8 + wk)))
        d.line([S(fx[0], cy - 0.8), S(fx[-1], cy - 0.8)], fill=col, width=int(SS * (0.95 + wk)))
        d.line([S(cx, cy - 0.8), S(cx, cy + 4.5 * k)], fill=col, width=int(SS * (1.1 + wk)))
twig(d, 1585.0, ty(1585.0) + 31.0)
fork(d, 1585.0, rtop(1585.0) + RH / 2)
small = lay.resize((W, H), Image.LANCZOS)
im2 = img.convert('RGBA'); im2.alpha_composite(small); img = im2.convert('RGB')
# v9: a 줄 보라 칸 — 속이 액자 테(자주)와 같은 빛이라 찬 칸으로 안 읽혔다(b139) → 짙은 보라로 · 테와 사이에 흰 실선
A = np.asarray(img).astype(float)
xc = 1603.0; top = ty(xc) + 22.6; s_ = 16.0; t_ = s_ * 0.2
x0, x1, y0, y1 = xc - s_ / 2 + t_ + 0.6, xc + s_ / 2 - t_ - 0.6, top + t_ + 0.6, top + s_ - t_ - 0.6
reg = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1) & ((xx - xc) ** 2 + (yy - (top + s_ / 2)) ** 2 > 3.2 ** 2)
A[reg] = np.array([104, 44, 188], float)
rim = (xx >= x0 - 1) & (xx <= x1 + 1) & (yy >= y0 - 1) & (yy <= y1 + 1) & ~((xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1))
A[rim] = A[rim] * 0.4 + 255 * 0.6
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
img.save(dst); print('ok', dst)

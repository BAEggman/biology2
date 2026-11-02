#!/usr/bin/env python3
"""touch_h3.py — s45u02 v7 ③ 행 17 · 10: 두 자매에게 **같은 일곱 줄 빛띠**(왼 보라 → 오른 빨강 — 걸상 무지개와 같은 차례)가 내린다.
액자로 **드는 줄만** 창까지 이어지고(창도 일곱 칸 — 든 칸만 그 빛깔), 안 드는 줄은 액자 위에서 사라지며, 초록 줄은 두 자매 모두 액자 윗변에서 V 로 되튄다.
  a(잔가지 · 왼 자매): 보라 · 파랑 · 빨강 이 든다
  b(포크 · 오른 자매): 파랑 · 청록 · 주황 이 든다 — a 의 무늬를 한 칸씩 안쪽(가운데 쪽)으로 옮긴 꼴 = 「조금」 어긋남(약속 #126 — 같은 띠 둘 · 다른 것은 드는 칸)
옛 빛살(a 파랑 · 빨강 / b 청록 · 초록 V · 주황)은 cur7(빛살 전 하늘)로 걷는다. 흰 눈부심 · 당근 빛살 · 금빛 물결은 그대로.
(독립 검토 행 17 1순위 — 「조금」은 눈금 위의 자리로만 선다 · 행 10: V 가 b 에만 있어 「b 만 초록을 안 쓴다?」 → 둘 다)
사용: touch_h3.py in.png cur7.png out.png"""
import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, sky, dst = sys.argv[1:4]
img = Image.open(src).convert('RGB'); W, H = img.size
A = np.asarray(img).astype(float); C7 = np.asarray(Image.open(sky).convert('RGB')).astype(float)
yy, xx = np.mgrid[0:H, 0:W]

# ── 1. 옛 빛살 걷기(통로 안 · 액자 창 위까지)
def corridor(p0, p1, hw, ytop, ybot):
    (x0, y0), (x1, y1) = p0, p1
    k = (x1 - x0) / (y1 - y0)
    xc = x0 + k * (yy - y0)
    return (np.abs(xx - xc) <= hw) & (yy >= ytop) & (yy <= ybot)
OLD = [((1050, 40), (994, 318), 16, 322), ((1031, 19), (972, 321), 14, 322),          # a 파랑 · 빨강
       ((1438, 40), (1380, 314), 16, 318), ((1406, 40), (1349, 312), 13, 318),        # b 청록 · 초록
       ((1425, 19), (1364, 316), 12, 318)]                                          # b 주황
# v7b: 문턱 없이 통로 전체를 cur7 로 — 가장자리 8 px 은 천천히(b138 채점 「빛살 양옆의 희미한 윤곽선」 = 문턱 6 의 등고선이었다)
def cwt(p0, p1, hw, ytop, ybot, fe=8.0):
    (x0, y0), (x1, y1) = p0, p1
    k = (x1 - x0) / (y1 - y0)
    xc = x0 + k * (yy - y0)
    w = np.clip((hw + fe - np.abs(xx - xc)) / fe, 0, 1)
    w[(yy < ytop) | (yy > ybot)] = 0
    return w
Wt = np.zeros((H, W))
for (p0, p1, hw, yb) in OLD:
    Wt = np.maximum(Wt, cwt(p0, p1, hw - 3, 8, yb))
Wt = np.maximum(Wt, cwt((1288, 128), (1349, 312), 10, 110, 318))
# 흰 눈부심 · 당근 빛살 통로는 건드리지 않는다
keepw = corridor((1078, 40), (1031, 528), 20, 0, 600) | corridor((1163, 40), (1101, 414), 14, 0, 600) | corridor((1173, 40), (1110, 414), 14, 0, 600)
Wt[keepw] = 0
A = A * (1 - Wt[..., None]) + C7 * Wt[..., None]
print('옛 빛살 걷음(가중)', round(float(Wt.sum()), 1))
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))

# ── 2. 일곱 줄 빛띠
COL = [(150, 96, 206), (92, 140, 228), (64, 170, 182), (86, 178, 80), (236, 206, 64), (240, 140, 40), (214, 58, 48)]
SIS = {  # 창 x 범위 · 액자 바깥 윗변 y · 창 윗변 y · 창 아랫변 y · 구슬(가운데 · 반지름) · 드는 줄
    'a': dict(wx=(962.0, 1008.0), yft=313.0, ywt=326.0, ywb=384.5, bead=(987.0, 353.0, 15.8), lit={0, 1, 6}),
    'b': dict(wx=(1336.0, 1382.0), yft=309.0, ywt=325.0, ywb=382.5, bead=(1357.0, 352.0, 15.8), lit={1, 2, 5}),
}
SS = 4; S = lambda x, y: (x * SS, y * SS)
SLOPE = 0.2           # 위로 갈수록 오른쪽(옛 빛살 · 흰 눈부심과 같은 기울기)
TOPW = 32.0; YTOP = 19.0
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
def xb(sis, k, y):
    """줄 k 의 왼 경계(k=0..7) 의 y 에서의 x — 아래(액자 윗변)는 창 폭, 위(19)는 TOPW."""
    (x0, x1) = sis['wx']; yb = sis['yft']
    t = (y - YTOP) / (yb - YTOP)                      # 0(위) → 1(액자)
    w = TOPW + (x1 - x0 - TOPW) * t
    cx = (x0 + x1) / 2 + SLOPE * (yb - y)
    return cx - w / 2 + w * k / 7.0
def quad(sis, k, ya, yb_, al, col):
    d.polygon([S(xb(sis, k, ya), ya), S(xb(sis, k + 1, ya), ya), S(xb(sis, k + 1, yb_), yb_), S(xb(sis, k, yb_), yb_)], fill=col + (int(al),))
for nm, sis in SIS.items():
    yft, ywt = sis['yft'], sis['ywt']
    for k in range(7):
        col = COL[k]
        if k in sis['lit']:
            yend, fade = ywt + 1.5, 0
        elif k == 3:
            yend, fade = yft + 1.0, 0
        else:
            yend, fade = yft - 16.0, 30.0
        steps = 140
        for i in range(steps):
            ya = YTOP + (yend - YTOP) * i / steps; yb_ = YTOP + (yend - YTOP) * (i + 1) / steps
            t = (ya - YTOP) / (yft - YTOP)
            al = 45 + 120 * min(t, 1.0)
            if fade and yb_ > yend - fade: al *= max(0.0, (yend - (ya + yb_) / 2) / fade) ** 1.3
            if ya > yft: al = 150                                         # 액자 윗 테 위를 지나 창으로
            quad(sis, k, ya, yb_, al, col)
    # 초록 되튐 — 윗변에 맞은 자리에서 위 왼쪽으로(같은 기울기의 거울)
    xh0, xh1 = xb(sis, 3, yft), xb(sis, 4, yft); L = 150.0
    for i in range(30):
        s0, s1 = L * i / 30, L * (i + 1) / 30
        w0 = (xh1 - xh0) * (1 - 0.25 * i / 30); w1 = (xh1 - xh0) * (1 - 0.25 * (i + 1) / 30)
        c0 = ((xh0 + xh1) / 2 - SLOPE * s0, yft - s0); c1 = ((xh0 + xh1) / 2 - SLOPE * s1, yft - s1)
        al = int(160 * (1 - 0.85 * i / 30))
        d.polygon([S(c0[0] - w0 / 2, c0[1]), S(c0[0] + w0 / 2, c0[1]), S(c1[0] + w1 / 2, c1[1]), S(c1[0] - w1 / 2, c1[1])], fill=COL[3] + (al,))
small = lay.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
im2 = img.convert('RGBA'); im2.alpha_composite(small); img = im2.convert('RGB')

# ── 3. 창을 일곱 칸으로(든 칸 = 짙게 · 안 든 칸 = 아주 옅게) — 구슬 · 테두리는 그대로
A = np.asarray(img).astype(float)
for nm, sis in SIS.items():
    (x0, x1) = sis['wx']; bx, by, br = sis['bead']
    reg = (xx >= x0) & (xx < x1) & (yy >= sis['ywt']) & (yy <= sis['ywb'])
    rr2 = (xx - bx) ** 2 + (yy - by) ** 2
    reg &= rr2 > 11.5 ** 2                                              # 쇠구슬 몸 · 검은 테는 손대지 않음
    sub = A[reg]
    lum = sub.mean(axis=1); sat = sub.max(axis=1) - sub.min(axis=1)
    # v7b: 흰 테(구슬 둘레의 무채색 밝은 고리)는 남기되, 옛 반쪽 칠(채도 높음)이 남은 곳은 구슬 바로 곁까지 다 새 칸으로
    # (b138 「은구슬 둘레의 파란 테」 = 옛 칠이 흰 테 바깥 가장자리에 남은 것)
    win = (lum > 120) & ((rr2[reg] > br ** 2) | (sat > 28))
    k = np.clip(((xx[reg] - x0) / ((x1 - x0) / 7.0)).astype(int), 0, 6)
    new = np.zeros_like(sub)
    for j in range(7):
        c = np.array(COL[j], float)
        new[k == j] = 0.28 * 245 + 0.72 * c if j in sis['lit'] else 0.86 * 247 + 0.14 * c
    out = sub.copy(); out[win] = new[win]
    # 칸 사이 가는 금(옅게)
    fx = (xx[reg] - x0) / ((x1 - x0) / 7.0); edge = (np.abs(fx - np.round(fx)) * ((x1 - x0) / 7.0) < 0.55) & (np.round(fx) > 0) & (np.round(fx) < 7)
    out[win & edge] = out[win & edge] * 0.72 + np.array([70, 60, 80]) * 0.28
    A[reg] = out
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
img.save(dst); print('ok', dst)

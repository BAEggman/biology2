#!/usr/bin/env python3
"""touch_d.py — s45u02 v3(b132 뒤): cur9 → cur10 · 「까닭」을 나르는 장치 넷
 ① 행 4  — 꼬투리 쿠션 겹마다 앞면에 아주 작은 자주빛 액자 머리(엽록소 · 광계)를 줄지어 박는다 → 겹마다 광계가 박힌 막 · 쌓을수록 그 자리가 는다
 ② 행 9  — 사발을 비켜 쿠션에 떨어진 노란 공 하나가 희미한 빛무리로 사그라든다(받지 못한 들뜸은 빛 · 열로 샌다)
 ③ 행 22 · 17 — 걸상 뒤 난간: a 머리가 빈 청록 자리 위에 작은 당근(카로티노이드)이 청록 빛에 잠기고, 빈 주황 자리 위에 포크 브로치 단 작은 머리(b)가 주황으로 찼다
 ④ 행 17 — 진홍 안개 속 둘에 자매와 같은 꼬리 · 진홍 빛살이 액자로 든다"""
import sys, os, math, colorsys, itertools, numpy as np
from PIL import Image, ImageDraw, ImageFilter
V5 = '--v5' in sys.argv            # v5(b134 뒤): ① 무더기 머리 · ③ 난간 당근 · b 도 뺀다 — touch_f 가 겹마다 셋 · 걸상 앞판 머리 줄로 다시 그린다
V4 = '--v4' in sys.argv or V5      # v4(b133 뒤): ② 희미한 공 · ④ 진홍 빛살 둘을 뺀다(③ 은 크게) — 「에머슨의 두 빛」으로 읽혔다 · 공은 touch_e/G1 이 다시
args = [a for a in sys.argv[1:] if not a.startswith('--')]
os.chdir(args[0] if args else '.')
img = Image.open('cur9.png').convert('RGB'); W, H = img.size
SS = 4
S = lambda x, y: (x * SS, y * SS)
INK = (40, 32, 24, 255)
def layer(): return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
def comp(img, lay, blur=0):
    small = lay.resize((W, H), Image.LANCZOS)
    if blur: small = small.filter(ImageFilter.GaussianBlur(blur))
    im2 = img.convert('RGBA'); im2.alpha_composite(small); return im2.convert('RGB')
A = np.asarray(img).astype(int)
L = A.mean(axis=2); R_, G_, B_ = A[..., 0], A[..., 1], A[..., 2]
green = (G_ > R_ + 8) & (G_ > B_ + 15) & (L > 95)

# ── ① 쿠션 겹마다 작은 자주빛 머리
from scipy.ndimage import gaussian_filter1d
STACKS = [  # (가운데 x, 위 y, 아래 y, 앞면 왼끝 x, 오른끝 x, 한 겹에 머리 수) — 끝 x 는 그림에서 잰 무더기 폭
    (678, 318, 380, 624, 732, 3), (765, 385, 450, 734, 804, 2), (632, 420, 495, 579, 684, 3),
    (768, 495, 552, 734, 806, 2), (628, 535, 605, 573, 682, 3), (765, 600, 656, 734, 798, 2)]
faces = []
for (cx, y0, y1, xl, xr, n) in STACKS:
    prof = gaussian_filter1d(np.mean(L[y0:y1, cx - 12:cx + 13], axis=1), 0.8)
    mins = [y0 + i for i in range(1, len(prof) - 1) if prof[i] < prof[i - 1] and prof[i] <= prof[i + 1] and prof[i] < 85]
    merged = []
    for y in mins:
        if merged and y - merged[-1] < 4: merged[-1] = (merged[-1] + y) // 2
        else: merged.append(y)
    for a0, b0 in zip(merged, merged[1:]):
        gap = b0 - a0
        if gap < 4: continue
        k = max(1, int(round(gap / 9.0)))          # 윤곽선이 빠진 곳은 겹 수만큼 나눈다
        for j in range(k):
            yc = a0 + gap * (j + 0.5) / k
            faces.append((yc, xl + 4, xr - 4, n, gap / k))
lay = layer(); d = ImageDraw.Draw(lay)
PUR, PURD = (156, 108, 196, 255), (70, 44, 96, 255)
cnt = 0
import random
random.seed(7)
for j, (yc, xl, xr, n, gap) in enumerate([] if V5 else faces):
    s = min(5.0, max(3.6, gap * 0.62))
    off = ((j % 3) - 1) * 0.28 / (n + 1)          # 겹마다 자리를 비껴 놓아 단추 줄(누빔)처럼 서지 않게
    for k in range(n):
        x = xl + (xr - xl) * ((k + 1) / (n + 1) + off) + random.uniform(-3, 3)
        d.rectangle([S(x - s / 2, yc - s / 2), S(x + s / 2, yc + s / 2)], fill=PUR, outline=PURD, width=int(SS * 0.8))
        d.rectangle([S(x - s * 0.18, yc - s * 0.18), S(x + s * 0.18, yc + s * 0.18)], fill=(250, 250, 248, 255))
        cnt += 1
img = comp(img, lay)
print('faces', len(faces), 'heads', cnt)

# ── ② 사발을 비켜 떨어져 사그라드는 노란 공(v3 만 — v4 는 G1 조각)
if not V4:
    lay = layer(); d = ImageDraw.Draw(lay)
    cx, cy = 1230.0, 595.0
    for (rr, a) in [(12, 40), (9, 70), (6.5, 110)]:
        d.ellipse([S(cx - rr, cy - rr * 0.8), S(cx + rr, cy + rr * 0.8)], fill=(255, 244, 170, a))
    img = comp(img, lay, 2.2)
    lay = layer(); d = ImageDraw.Draw(lay)
    r = 3.6
    d.ellipse([S(cx - r, cy - r), S(cx + r, cy + r)], fill=(232, 214, 140, 255), outline=(120, 108, 70, 255), width=int(SS * 0.9))
    img = comp(img, lay)

# ── ③ 난간의 보조 색소(청록 = 당근 · 주황 = b 머리)
Af = np.asarray(img).astype(float) / 255
ty = lambda x: 611 + (x - 1560) * 0.117
rail_top = lambda x: ty(x) - 84
def band_at(x):
    y = int(rail_top(x) - 11)
    r_, g_, b_ = Af[y - 1:y + 2, x - 1:x + 2].reshape(-1, 3).mean(axis=0)
    h, s, v = colorsys.rgb_to_hsv(r_, g_, b_); h *= 360
    if s < 0.18: return '.'
    return 'V' if 260 <= h <= 320 else 'B' if 200 <= h < 260 else 'T' if 160 <= h < 200 else 'G' if 80 <= h < 160 else 'Y' if 40 <= h < 80 else 'O' if 15 <= h < 40 else 'R'
# 머리 줄 높이의 띠는 cur7(머리를 놓기 전)에서 잰다
A7 = np.asarray(Image.open('cur7.png').convert('RGB')).astype(float) / 255
def band7(x):
    y = int(rail_top(x) - 11)
    r_, g_, b_ = A7[y - 1:y + 2, x - 1:x + 2].reshape(-1, 3).mean(axis=0)
    h, s, v = colorsys.rgb_to_hsv(r_, g_, b_); h *= 360
    if s < 0.18: return '.'
    return 'V' if 260 <= h <= 320 else 'B' if 200 <= h < 260 else 'T' if 160 <= h < 200 else 'G' if 80 <= h < 160 else 'Y' if 40 <= h < 80 else 'O' if 15 <= h < 40 else 'R'
seq = ''.join(band7(x) for x in range(1584, 1870))
runs, x = {}, 1584
for c, g in itertools.groupby(seq):
    m = len(list(g))
    if c != '.' and (c not in runs or m > runs[c][1] - runs[c][0] + 1): runs[c] = (x, x + m - 1)
    x += m
cT = (runs['T'][0] + runs['T'][1]) / 2; cO = (runs['O'][0] + runs['O'][1]) / 2
print('teal head x', cT, 'orange head x', cO)
s = 19.0
K = 1.35 if V4 else 1.0                            # v4: 당근 · b 머리를 키운다(B 「작은 주황 상자의 쌓임 — 모름」)
lay = layer(); d = ImageDraw.Draw(lay)
# 청록: 빈 머리 위에 걸터앉은 작은 당근 + 청록 빛 무리
tb = rail_top(cT) - s                              # 머리 윗변
d.ellipse([S(cT - 11 * K, tb - 26 * K), S(cT + 11 * K, tb - 2)], fill=(80, 190, 196, 120))
if not V5: img = comp(img, lay, 2.5)
lay = layer(); d = ImageDraw.Draw(lay)
car = [S(cT - 5.0 * K, tb - 18 * K), S(cT + 5.0 * K, tb - 18 * K), S(cT + 1.0 * K, tb - 1.0), S(cT - 1.0 * K, tb - 1.0)]
d.polygon(car, fill=(236, 126, 40, 255), outline=INK)
for k in range(3):
    yy = tb - 15 * K + k * 4.0 * K
    d.line([S(cT - 3.6 * K + k * 0.9 * K, yy), S(cT - 1.0 * K + k * 0.6 * K, yy + 0.6)], fill=(170, 80, 20, 255), width=int(SS * 0.7))
for (dx, dy) in [(-3.5, -6), (0, -8), (3.5, -6)]:
    d.line([S(cT, tb - 18 * K), S(cT + dx * K, tb - 18 * K + dy * K)], fill=(60, 140, 50, 255), width=int(SS * 1.6))
if not V5: img = comp(img, lay)
# 주황: 빈 머리 위에 작은 b 머리(주황으로 찬 액자 · 포크 브로치)
lay = layer(); d = ImageDraw.Draw(lay)
ob = rail_top(cO) - s
def mini_b(d, cx, foot):
    """v4: 빈 주황 머리 위에 선 작은 b 사람 — 자주빛 액자 머리(주황으로 참 · 은빛 구슬) · 베이지 몸 · 가슴에 갈퀴 넷 포크(무대 오른 자매와 같은 사람)"""
    SKIN, SKIND = (222, 204, 178, 255), (120, 100, 78, 255)
    hip, sh = foot - 9.5, foot - 20.0
    for dx in (-1.9, 1.9):                                          # 다리
        d.line([S(cx + dx * 0.8, hip), S(cx + dx, foot)], fill=INK, width=int(SS * 2.6))
        d.line([S(cx + dx * 0.8, hip), S(cx + dx, foot - 0.4)], fill=SKIN, width=int(SS * 1.4))
    body = [S(cx - 4.6, sh), S(cx + 4.6, sh), S(cx + 3.6, hip + 1), S(cx - 3.6, hip + 1)]
    d.polygon(body, fill=SKIN, outline=INK)
    for dx in (-1, 1):                                              # 팔(몸 곁에 늘어뜨림)
        d.line([S(cx + dx * 4.6, sh + 0.6), S(cx + dx * 5.6, hip - 0.5)], fill=INK, width=int(SS * 2.2))
        d.line([S(cx + dx * 4.6, sh + 0.6), S(cx + dx * 5.6, hip - 0.8)], fill=SKIN, width=int(SS * 1.0))
    d.line([S(cx, sh - 2.4), S(cx, sh + 0.4)], fill=INK, width=int(SS * 2.4))      # 목
    hs = 15.0; hx0, hy0 = cx - hs / 2, sh - 2.2 - hs
    d.rectangle([S(hx0, hy0), S(hx0 + hs, hy0 + hs)], fill=(168, 128, 196, 255), outline=INK, width=int(SS * 1.0))
    t2 = 3.3
    d.rectangle([S(hx0 + t2, hy0 + t2), S(hx0 + hs - t2, hy0 + hs - t2)], fill=(238, 136, 44, 255), outline=(118, 82, 150, 255), width=int(SS * 0.7))
    d.ellipse([S(cx - 2.2, hy0 + hs / 2 - 2.2), S(cx + 2.2, hy0 + hs / 2 + 2.2)], fill=(200, 202, 208, 255), outline=INK, width=int(SS * 0.5))
    fx = [cx - 2.4 + 1.6 * k for k in range(4)]                      # 가슴 포크(갈퀴 넷 — 잉크 테 위에 은빛)
    for (col, wk) in ((INK, 1.0), ((214, 218, 224, 255), 0.0)):
        for x in fx:
            d.line([S(x, sh + 1.4), S(x, sh + 4.4)], fill=col, width=int(SS * (0.75 + wk)))
        d.line([S(fx[0], sh + 4.4), S(fx[-1], sh + 4.4)], fill=col, width=int(SS * (0.9 + wk)))
        d.line([S(cx, sh + 4.4), S(cx, sh + 8.2)], fill=col, width=int(SS * (1.0 + wk)))
if V4:
    mini_b(d, cO, ob - 0.6)
else:
    hs = 13.0; hx0, hy0 = cO - hs / 2, ob - hs - 9
    d.rectangle([S(hx0, hy0), S(hx0 + hs, hy0 + hs)], fill=(168, 128, 196, 255), outline=INK, width=int(SS * 1.0))
    d.rectangle([S(hx0 + 2.8, hy0 + 2.8), S(hx0 + hs - 2.8, hy0 + hs - 2.8)], fill=(238, 136, 44, 255), outline=(118, 82, 150, 255), width=int(SS * 0.7))
    bx, byy = cO, hy0 + hs / 2
    d.ellipse([S(bx - 1.8, byy - 1.8), S(bx + 1.8, byy + 1.8)], fill=(200, 202, 208, 255), outline=INK, width=int(SS * 0.5))
    # 목 + 포크 브로치(갈퀴 넷)
    d.line([S(cO, hy0 + hs), S(cO, ob - 0.5)], fill=(150, 120, 90, 255), width=int(SS * 2.2))
    fx = [cO - 3.0 + 2.0 * k for k in range(4)]
    for x in fx:
        d.line([S(x, hy0 + hs + 1.2), S(x, hy0 + hs + 4.6)], fill=(200, 204, 210, 255), width=int(SS * 0.8))
    d.line([S(fx[0], hy0 + hs + 4.6), S(fx[-1], hy0 + hs + 4.6)], fill=(200, 204, 210, 255), width=int(SS * 0.9))
    d.line([S(cO, hy0 + hs + 4.6), S(cO, hy0 + hs + 7.5)], fill=(200, 204, 210, 255), width=int(SS * 1.0))
if not V5: img = comp(img, lay)

# ── ④ 안개 속 둘: 진홍 빛살(v3 만 — v4 는 뺀다: 나란한 두 빛줄기가 「에머슨의 두 빛」으로 읽혔다)
if not V4:
    lay = layer(); d = ImageDraw.Draw(lay)
    for (hx, hy) in [(1828.0, 453.0), (1912.0, 467.0)]:
        d.polygon([S(hx - 6, 40), S(hx + 6, 40), S(hx + 9, hy - 32), S(hx - 9, hy - 32)], fill=(214, 24, 44, 120))
    img = comp(img, lay, 1.5)
img.save('cur10.png')
for (b, nm, k) in [((560, 280, 820, 660), 'v10_stacks.png', 2), ((1180, 520, 1290, 620), 'v10_bowl.png', 4), ((1580, 480, 1800, 600), 'v10_rail.png', 4), ((1790, 380, 1990, 620), 'v10_df.png', 2)]:
    img.crop(b).resize(((b[2] - b[0]) * k, (b[3] - b[1]) * k), Image.LANCZOS).save(nm)
print('cur10 saved')

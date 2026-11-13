#!/usr/bin/env python3
# L53b_pil3.py — 일치 검사 2 · 3회 뒤의 잔손질(pil2 다음):
#  ① 굴 · 틈의 위아래 끝을 물빛으로 풀어 줌(각진 「덧댄 조각」으로 읽힘)  ② 펌프 밑 동전 자리 정리(구슬과 뭉개짐) — 투입구에 반쯤 든 동전 + 아래서 오르는 동전 + ↑
#  ③ 포도 문 굴 끝의 포도를 굴 아래 물로 옮김(구슬과 겹침)  ④ 열쇠 문 아래 번진 소금 가루 → 또렷한 알갱이
import sys, math, cv2, numpy as np
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
a = np.array(Image.open(src).convert('RGB')).astype(np.float32)
LUM = np.array([187, 224, 244], np.float32); UPW = np.array([117, 187, 233], np.float32); BUT = np.array([248, 211, 75], np.float32)
DEEP, MID, TGT = np.array([40, 110, 187], np.float32), np.array([40, 86, 136], np.float32), np.array([33, 46, 94], np.float32)
def water(y):
    if y < 700: return UPW
    t = min(1.0, max(0.0, (y - 760) / (1144 - 760.0)))
    return DEEP + (MID - DEEP) * (t / 0.5) if t < 0.5 else MID + (TGT - MID) * ((t - 0.5) / 0.5)
# ③-가 옛 포도(굴 끝 · 구슬에 걸침) 지움: 굴 안쪽은 굴 빛 · 굴 밖은 물빛
yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
old = (xx - 1206.8) ** 2 + (yy - 871.3) ** 2 <= 23 ** 2
for y in range(846, 897):
    row = old[y]
    if not row.any(): continue
    xs = np.where(row)[0]
    for x in xs: a[y, x] = LUM if (y <= 880 and x <= 1217) else water(y)
# ① 끝 풀기
def fade(x0, x1, y_end, top, n=34):
    """굴 끝 n 줄: 물빛 ↔ 굴 빛 사이에 놓인 화소(가장자리의 섞인 빛 포함)만 물빛 쪽으로 푼다 — 칼 · 소금 · 구슬은 그대로."""
    for k in range(-6, n):
        y = y_end + k if top else y_end - k
        al = max(0.0, (k + 0.5) / n); row = a[y, x0:x1 + 1]; wat = water(y); v = LUM - wat; vv = float((v * v).sum())
        t = ((row - wat) * v).sum(axis=1) / vv; dist = np.sqrt((((row - wat) - t[:, None] * v) ** 2).sum(axis=1))
        m = (dist < 46) & (t > 0.04) & (t < 1.4)
        row[m] = wat + (np.minimum(t[m, None], 1.0) * al) * v
        if k < 6:                                          # 끝 바로 밖에 남는 옛 테두리 그림자(물보다 조금 어두운 푸른 줄)
            dk = (row[:, 2] > row[:, 0] + 40) & (np.abs(row - wat).sum(axis=1) < 110) & ~m
            row[dk] = wat
for x0, x1 in ((940, 980), (1158, 1221), (1409, 1471), (1623, 1657), (1773, 1807)):
    fade(x0, x1, 300, True); fade(x0, x1, 881, False)
# ④ 번진 소금 가루: 밝은 덩이의 자리만 적어 두고 물빛으로 지운 뒤 또렷한 알갱이로
reg = a[884:988, 1742:1848]; br = (reg.sum(axis=2) > 430).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(br, 8)
grains = [(cen[k][0] + 1742, cen[k][1] + 884, st[k, cv2.CC_STAT_AREA]) for k in range(1, n) if st[k, cv2.CC_STAT_AREA] >= 6]
soft = cv2.dilate((reg.sum(axis=2) > 360).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
for y in range(884, 988):
    a[y, 1742:1848][soft[y - 884]] = water(y)
# ② 펌프 밑
for y in range(624, 647): a[y, 1929:1968] = a[y, 1928]                       # 상자 밑의 옛 홈 → 놋쇠 · 아랫선(깨끗한 줄을 옮김)
for y in range(646, 714): a[y, 1914:1976] = a[y, 1910]                       # 상자 밑(버터 · 띠 아랫선 · 물) — 깨끗한 줄을 옮김
for y in range(646, 714): a[y, 1993:2022] = a[y, 2041]                       # 옛 흐린 화살
for y in range(716, 796): a[y, 1966:2038] = a[y, 2041]                       # 옛 동전(오른쪽 아래) → 물
pil = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); S = 4; INK = (22, 20, 18, 255)
def layer(x0, y0, W, H): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay, x0, y0, W, H): lay = lay.resize((W, H), Image.LANCZOS); pil.paste(lay, (x0, y0), lay)
def ball(cx, cy, r_out, r_in, col, hi=None):
    x0, y0 = int(cx - r_out - 3), int(cy - r_out - 3); W = H = int(2 * r_out + 6); lay = layer(x0, y0, W, H); d = ImageDraw.Draw(lay)
    ox, oy = (cx - x0) * S, (cy - y0) * S
    d.ellipse([ox - r_out * S, oy - r_out * S, ox + r_out * S, oy + r_out * S], fill=INK); d.ellipse([ox - r_in * S, oy - r_in * S, ox + r_in * S, oy + r_in * S], fill=col)
    if hi: d.ellipse([ox - r_in * 0.55 * S, oy - r_in * 0.62 * S, ox - r_in * 0.05 * S, oy - r_in * 0.2 * S], fill=hi)
    put(lay, x0, y0, W, H)
# 펌프 기둥의 구슬(상자 밑 빨강 · 파랑 · 노랑 윗부분)
ball(1950, 667, 16.2, 12.6, (226, 58, 48, 255)); ball(1950, 695, 16.2, 12.6, (62, 150, 226, 255)); ball(1950.2, 722.9, 16.2, 12.6, (247, 198, 44, 255))
# 투입구(상자 밑 오른쪽) + 반쯤 든 동전 + 아래서 오르는 동전 + ↑
def coin(cx, cy, rx, ry, clip_top=None):
    x0, y0 = int(cx - rx - 6), int(cy - ry - 6); W, H = int(2 * rx + 12), int(2 * ry + 12); lay = layer(x0, y0, W, H); d = ImageDraw.Draw(lay)
    ox, oy = (cx - x0) * S, (cy - y0) * S
    d.ellipse([ox - (rx + 3.2) * S, oy - (ry + 3.2) * S, ox + (rx + 3.2) * S, oy + (ry + 3.2) * S], fill=INK)
    d.ellipse([ox - rx * S, oy - ry * S, ox + rx * S, oy + ry * S], fill=(244, 190, 44, 255))
    d.ellipse([ox - (rx - 3.4) * S, oy - (ry - 3.4) * S, ox + (rx - 3.4) * S, oy + (ry - 3.4) * S], outline=(196, 138, 20, 255), width=int(2.2 * S))
    d.arc([ox - (rx - 1.5) * S, oy - (ry - 1.5) * S, ox + (rx - 1.5) * S, oy + (ry - 1.5) * S], 200, 255, fill=(254, 226, 130, 255), width=int(2.4 * S))
    if clip_top is not None: d.rectangle([0, 0, W * S, (clip_top - y0) * S], fill=(0, 0, 0, 0))
    put(lay, x0, y0, W, H)
bd = ImageDraw.Draw(pil)
bd.rectangle([1970, 636, 1988, 644], fill=(14, 10, 6))                        # 투입구(어두운 틈)
coin(1979, 655, 8.5, 13.5, clip_top=643)
coin(1981, 752, 13, 19)
def arrow_up(x, y0, y1, w=5.0):
    x0 = x - 15; W = 30; H = y0 - y1 + 8; yb = y1 - 4; lay = layer(x0, yb, W, H); d = ImageDraw.Draw(lay)
    def T(px, py): return ((px - x0) * S, (py - yb) * S)
    d.line([T(x, y0), T(x, y1 + 11)], fill=INK, width=int(w * S)); d.polygon([T(x, y1), T(x - 10, y1 + 14), T(x + 10, y1 + 14)], fill=INK)
    put(lay, x0, yb, W, H)
arrow_up(1981, 724, 678)
# ③-나 굴 끝 오른쪽 주황 구슬을 다시 긋고, 포도는 굴 아래 물에 또렷이
ball(1231.8, 861.1, 16.2, 12.6, (245, 140, 44, 255))
ball(1190, 917, 16.8, 13.2, (128, 62, 166, 255), hi=(176, 120, 206, 255))
# ④ 또렷한 소금 알갱이
for gx, gy, ar in grains:
    r = 2.8 + min(1.6, ar / 40.0)
    ball(gx, gy, r + 1.5, r, (255, 255, 255, 255))
pil.save(dst); print('ok grains', len(grains))

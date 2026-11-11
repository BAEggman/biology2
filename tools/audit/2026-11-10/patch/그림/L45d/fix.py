#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L45d (탄소 공방) 그림 고침 — 원본 final_v1.png 에서 final_new.png 를 다시 만든다 (PIL·numpy·cv2 만).
  항목 1 (정거장 4): 왼 토막의 선 금화(x1111..1149, y487..532)를 지우고, 오른 토막 윗줄(부러진 끝 바로 오른쪽,
         dx=+170, dy=-4)로 옮겨 '반쯤 박힌' 모양으로 붙인다 → 토막마다 금화 하나.
  항목 2 (정거장 8·9): 짐꾼(막대 셋 · 금화 셋 포함) · 속도선 · 발밑 그림자를 x=621 축으로 좌우 뒤집는다
         → 얼굴 · 발끝 · 금화 단 막대 앞끝이 왼쪽(스코프 쪽), 속도선은 오른쪽 뒤.
         짐꾼이 비운 자리는 배경 띠(벽 · 뒷가로대 · 앞가로대 · 바닥 · 깔개 · 작업대 앞판)를 선 위치에 맞춰
         가로로 이어 채우고(BHI), 다리 · 옆 가로대 끝 · 뒷가로대 끝 · 작업대 위 막대 마디는 따로 그린다.
  짐꾼 마스크(M)와 그 안쪽 밝은 칸(S)은 아래 base64 PNG(박스 x190..1070, y500..1100)로 함께 싣는다.
사용: python3 fix.py   → final_new.png, cmp_1.png, cmp_2.png (바뀐 자리 상자 출력)
"""
import io, base64
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = SP + '/L45d/r1/final_v1.png'
OUT = SP + '/picfix/L45d'
H, W = 1144, 2048

# 1-bit PNG masks (crop box x190..1070, y500..1100) of the carrier sprite (M) and its non-dark interior (S)
MASK_M = (
    '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'
)

MASK_S = (
    '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'
)


def decode_mask(b64parts):
    a = np.asarray(Image.open(io.BytesIO(base64.b64decode(''.join(b64parts)))).convert('L')) > 127
    m = np.zeros((H, W), bool)
    m[500:1100, 190:1070] = a
    return m


# =====================================================================  항목 1 : 금화 옮기기
SS = 8  # supersampling for polygon coverage


def poly_cov(poly, box):
    """coverage (0..1) of polygon given in pixel-centre coords over box=(x0,y0,x1,y1) (end exclusive)."""
    x0, y0, x1, y1 = box
    ww, hh = (x1 - x0) * SS, (y1 - y0) * SS
    im = Image.new('L', (ww, hh), 0)
    pts = [((px - x0 + 0.5) * SS, (py - y0 + 0.5) * SS) for px, py in poly]
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return np.asarray(im, np.float32).reshape(y1 - y0, SS, x1 - x0, SS).mean((1, 3)) / 255.0


def interp_rows(d, rows):
    ks = sorted(d)
    return np.interp(rows, ks, [d[k] for k in ks])


# ---- coin outer outline edge (AA midpoint, pixel-centre coords) measured on the original
LE = {488: 1122.37, 489: 1119.79, 490: 1117.45, 491: 1116.33, 492: 1115.24, 493: 1114.22, 494: 1113.30,
      495: 1112.49, 496: 1111.64, 497: 1111.36, 498: 1111.30, 499: 1111.22, 504: 1111.2, 505: 1111.32,
      506: 1111.41, 507: 1111.45, 508: 1111.48, 509: 1111.49, 510: 1111.6, 511: 1111.87, 512: 1112.44,
      513: 1112.98, 514: 1113.32, 515: 1113.8, 516: 1114.28, 517: 1114.82, 518: 1115.14, 519: 1115.55,
      520: 1116.28, 521: 1116.92, 522: 1117.21, 523: 1117.3}
RE = {488: 1127.24, 489: 1130.17, 490: 1132.55, 491: 1133.66, 492: 1134.72, 493: 1135.85, 494: 1136.84,
      495: 1138.04, 496: 1139.16, 497: 1139.82, 498: 1140.46, 499: 1141.1, 500: 1141.9, 501: 1142.7,
      502: 1143.5, 503: 1144.2, 504: 1144.8, 505: 1145.36, 506: 1145.57, 507: 1145.93, 508: 1146.37,
      509: 1146.74, 510: 1147.02, 511: 1147.35, 512: 1147.7, 513: 1148.0, 514: 1148.4, 515: 1148.55,
      516: 1148.7, 517: 1148.8, 518: 1148.9, 519: 1149.05, 520: 1149.2, 521: 1149.25, 522: 1149.3,
      523: 1149.25}
TOP = (1124.5, 487.6)
CUT = 523.5        # the pasted coin is cut here; the destination's rod top line stays in front of the rest
# lower part of the coin (only for erasing): left / right outer edge rows 523..532 and bottom
LOW_L = {523: 1117.3, 525: 1118.5, 527: 1121.5, 529: 1124.5, 530: 1126.5, 531: 1127.5}
LOW_R = {523: 1149.25, 524: 1148.5, 526: 1148.0, 528: 1147.2, 530: 1145.8, 531: 1144.0}
BOTTOM = 532.4
# knot outlines (outer edge on the bench side) — kept untouched
K1 = [(1080, 519.0), (1084, 517.42), (1086, 516.46), (1088, 515.37), (1090, 514.83), (1092, 514.04),
      (1094, 513.59), (1096, 513.62), (1098, 513.87), (1100, 514.53), (1102, 515.16), (1104, 515.64),
      (1106, 516.92), (1108, 518.06), (1110, 519.53), (1110.5, 520), (1111.4, 521), (1112.4, 522),
      (1113.4, 523), (1114.2, 524), (1114.8, 525), (1115.2, 526), (1115.4, 527), (1115.5, 528),
      (1115.9, 529), (1116.3, 530), (1116.8, 531), (1117.4, 532), (1117.7, 533), (1118.0, 534),
      (1118.3, 536), (1118.5, 545), (1080, 545)]
K2 = [(1172, 511.26), (1166, 509.87), (1164, 510.09), (1162, 510.66), (1160, 511.09), (1158, 511.38),
      (1157, 511.75), (1156, 512.16), (1155, 512.53), (1154, 512.93), (1153, 513.27), (1152.3, 513.6),
      (1151.5, 514), (1151.0, 515), (1150.5, 516), (1150.1, 517), (1149.8, 518), (1149.6, 519),
      (1149.5, 520), (1149.5, 521), (1149.6, 522), (1149.8, 523), (1150.1, 524), (1150.5, 525),
      (1151.3, 526), (1152.5, 527), (1153.3, 528), (1153.9, 529), (1154.4, 530), (1155.2, 532),
      (1155.7, 534), (1156.5, 545), (1172, 545)]
BX = (1092, 476, 1168, 542)          # working box around the source coin


def coin_poly(margin=0.0, cut=CUT):
    rows = np.arange(488, 524)
    le = interp_rows(LE, rows) - margin
    re = interp_rows(RE, rows) + margin
    pts = [(TOP[0], TOP[1] - margin)]
    pts += [(re[i], r) for i, r in enumerate(rows)]
    pts += [(re[-1], cut), (le[-1], cut)]
    pts += [(le[i], r) for i, r in reversed(list(enumerate(rows)))]
    return pts


def lower_poly(margin):
    rows = np.arange(523, 532)
    le = interp_rows(LOW_L, rows) - margin
    re = interp_rows(LOW_R, rows) + margin
    pts = [(le[i], r) for i, r in enumerate(rows)]
    pts += [(1130, BOTTOM + margin), (1140, BOTTOM + margin)]
    pts += [(re[i], r) for i, r in reversed(list(enumerate(rows)))]
    return pts


def erase_mask():
    # soft margin 4..8 px around the coin (removes the sharpening halo) ; knots and the apron fold excluded
    acc = 0
    ms = (5.0, 6.5, 8.0, 9.5, 11.0)
    for m in ms:
        acc = acc + np.maximum(poly_cov(coin_poly(m, cut=526.0), BX), poly_cov(lower_poly(min(m, 2.0)), BX))
    E = acc / len(ms)
    # bench strip between knot1 and the coin (light halo patch), rows 512..526
    patch = [(1100, 513.0), (1118, 513.0), (1121, 526.5), (1112, 526.5)]
    E = np.maximum(E, poly_cov(patch, BX))
    k1 = poly_cov(K1, BX); k2 = poly_cov(K2, BX)
    k3 = poly_cov([(1139, 470), (1170, 470), (1170, 489), (1145, 489), (1139, 484)], BX)   # apron fold line
    return E * (1 - k1) * (1 - k2) * (1 - k3)


def build_bg(O):
    """what lies behind the coin at its source: apron / bench edge line / bench top / rod top line / cream."""
    x0, y0, x1, y1 = BX
    bg = np.zeros((y1 - y0, x1 - x0, 3), np.float32)
    xs = np.arange(x0, x1)
    # apron + bench edge line (rows < 506): per-row linear interpolation between clean side strips
    for y in range(y0, 506):
        lc = O[y, 1097:1103].mean(0); rc = O[y, 1157:1163].mean(0) if y >= 495 else lc
        t = ((xs - 1100) / (1160 - 1100)).clip(0, 1)[:, None]
        bg[y - y0] = lc * (1 - t) + rc * t
    # bench top: per-row colour from clean strips (x1069..1078 between the lying coin and knot1, x1196..1204)
    for y in range(506, y1):
        if y <= 514:
            c = 0.5 * O[y, 1069:1079].mean(0) + 0.5 * O[y, 1196:1205].mean(0)
        else:
            c = O[min(y, 521), 1069:1079].mean(0)
        bg[y - y0] = c
    # rod top line between the knots: centre yl(x) ; profile (bench halo -> line -> cream) from x1188..1196
    yl = 524.6 + (xs - 1116) * (-0.6 / 34.0)
    pr = np.arange(510, 524)
    prof = O[510:524, 1188:1197].mean(1)          # line centre there = 518.0
    cr = np.arange(525, 542)
    cream = O[525:542, 1149:1152].mean(1)         # this segment's own cream (line centre ~524.3)
    def samp(rows, vals, q):
        return np.array([np.interp(q, rows, vals[:, c]) for c in range(3)])
    for j, x in enumerate(xs):
        for y in range(506, y1):
            d = y - yl[j]
            if d < -6.0:
                continue
            if d <= 1.6:
                v = samp(pr, prof, 518.0 + d)
                if d < -5.0:
                    t = d + 6.0
                    v = bg[y - y0, j] * (1 - t) + v * t
            else:
                v = samp(cr, cream, 524.3 + d)
                if d < 2.6:
                    t = d - 1.6
                    v = samp(pr, prof, 518.0 + d) * (1 - t) + v * t
            bg[y - y0, j] = v
    return bg


def item1(O, dx=170, dy=-4):
    """returns new image and the boxes changed"""
    P = O.copy()
    x0, y0, x1, y1 = BX
    bg = build_bg(O)
    E = erase_mask()
    src = O[y0:y1, x0:x1]
    P[y0:y1, x0:x1] = src * (1 - E[..., None]) + bg * E[..., None]
    # paste at the destination: background swap on the soft edge  new = src + (1-A)(dst - bg_src)
    A = poly_cov(coin_poly(0.0), BX)
    bgsrc = P[y0:y1, x0:x1]
    dst = O[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    new = src + (1 - A[..., None]) * (dst - bgsrc)
    region = P[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    m = A > 0
    region[m] = new[m]
    return P



# =====================================================================  항목 2 : 짐꾼 뒤집기
def ell(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def dil(m, r):
    return cv2.dilate(m.astype(np.uint8), ell(r)) > 0


def soft_masks(O, M):
    """speed lines (upper/lower), ground shadow (+hatch), rug dashes"""
    L = O.mean(2)
    Md = dil(M, 2)
    sp = np.zeros((H, W), bool)
    # upper speed lines on the floor (floor ~136, light strip ~182 below y 884)
    for (y0, y1, x0, x1) in ((820, 880, 270, 505), (808, 897, 430, 505)):
        sub = L[y0:y1, x0:x1]
        ref = np.median(L[y0:y1, 210:262], axis=1)[:, None]     # clean floor columns left of the lines
        sp[y0:y1, x0:x1] = sub < ref - 6
    # lower speed lines on the rug (rug ~157)
    y0, y1, x0, x1 = 945, 1032, 285, 490
    sp[y0:y1, x0:x1] |= L[y0:y1, x0:x1] < 147
    sp &= ~Md
    # drop specks
    n, l, st, _ = cv2.connectedComponentsWithStats(sp.astype(np.uint8), connectivity=8)
    keep = np.zeros_like(sp)
    for i in range(1, n):
        if st[i, 4] >= 8:
            keep |= l == i
    sp = keep
    # shadow ellipse + hatch (rug ~157)
    sh = np.zeros((H, W), bool)
    y0, y1, x0, x1 = 1036, 1096, 380, 845
    sh[y0:y1, x0:x1] = L[y0:y1, x0:x1] < 152
    sh &= ~Md
    # rug dashes (small dark marks) — excluded from sources only
    rug = np.zeros((H, W), bool)
    rug[912:1100, 300:1070] = L[912:1100, 300:1070] < 145
    rug &= ~(sp | sh | Md)
    return sp, sh, rug


def measure_line(O, bad, xs, yguess, half=5, thr=120, mass=60):
    Lm = O.max(2)
    out = []
    for x in xs:
        yc = int(round(yguess(x)))
        y0, y1 = yc - half, yc + half + 1
        if bad[y0:y1, x].any():
            continue
        col = Lm[y0:y1, x]
        dk = np.clip(thr - col, 0, None)
        if dk.sum() < mass or col.argmin() in (0, len(col) - 1):
            continue
        out.append((x, (dk * np.arange(y0, y1)).sum() / dk.sum()))
    return np.array(out)


def measure_step(O, bad, xs, ya, yb):
    """position where the column crosses the midpoint between rows ya (above) and yb (below)"""
    Lm = O.mean(2)
    out = []
    for x in xs:
        if bad[ya:yb + 1, x].any():
            continue
        col = Lm[ya:yb + 1, x]
        top, bot = col[:3].mean(), col[-3:].mean()
        mid = (top + bot) / 2
        s = np.nonzero((col[:-1] - mid) * (col[1:] - mid) <= 0)[0]
        if len(s) != 1:
            continue
        i = s[0]
        t = (mid - col[i]) / (col[i + 1] - col[i] + 1e-6)
        out.append((x, ya + i + t))
    return np.array(out)


def smooth_model(meas, xr, k=9, default=None):
    xs_all = np.arange(*xr)
    if len(meas) == 0:
        return np.full(len(xs_all), default, np.float32)
    x, y = meas[:, 0], meas[:, 1]
    # running median over neighbours (in sample index)
    ys = np.array([np.median(y[max(0, i - k // 2):i + k // 2 + 1]) for i in range(len(y))])
    return np.interp(xs_all, x, ys).astype(np.float32)


def bhi(O, hole, valid, xr, yr, guides, nav=12):
    """fill hole (within xr x yr) using band-coordinate row interpolation.
    guides: list of (gy array over xr, rigid half-width). returns filled float image (only hole pixels changed)."""
    xa, xb = xr; ya, yb = yr
    xs = np.arange(xa, xb)
    G = [float(np.median(g)) for g, r in guides]
    pad = 12
    cy = np.arange(ya - pad, yb + pad)                 # canonical rows
    nC = len(cy)
    C = np.zeros((nC, len(xs), 3), np.float32)
    V = np.zeros((nC, len(xs)), bool)
    Hc = np.zeros((nC, len(xs)), bool)
    knots_c, knots_a = [], []
    for j, x in enumerate(xs):
        kc, ka = [], []
        for (g, r), Gk in zip(guides, G):
            kc += [Gk - r, Gk + r]; ka += [g[j] - r, g[j] + r]
        kc = [cy[0] - 50] + kc + [cy[-1] + 50]
        ka = [cy[0] - 50 + (guides[0][0][j] - G[0])] + ka + [cy[-1] + 50 + (guides[-1][0][j] - G[-1])]
        knots_c.append(kc); knots_a.append(ka)
        Ya = np.interp(cy, kc, ka)
        f = np.floor(Ya).astype(int); t = (Ya - f)[:, None]
        f = np.clip(f, 0, H - 2)
        C[:, j] = O[f, x] * (1 - t) + O[f + 1, x] * t
        V[:, j] = valid[f, x] & valid[f + 1, x]
        Hc[:, j] = hole[f, x] | hole[f + 1, x]
    # row-wise fill
    Cf = C.copy()
    for i in range(nC):
        hrow = Hc[i]
        if not hrow.any():
            continue
        vidx = np.nonzero(V[i])[0]
        if len(vidx) == 0:
            continue
        hidx = np.nonzero(hrow)[0]
        pos = np.searchsorted(vidx, hidx)
        for hj, p in zip(hidx, pos):
            left = vidx[max(0, p - nav):p]
            right = vidx[p:p + nav]
            if len(left) and len(right):
                vl = np.median(C[i, left], 0); vr = np.median(C[i, right], 0)
                dl = hj - left.mean(); dr = right.mean() - hj
                Cf[i, hj] = (vl * dr + vr * dl) / (dl + dr)
            elif len(left):
                Cf[i, hj] = np.median(C[i, left], 0)
            else:
                Cf[i, hj] = np.median(C[i, right], 0)
    # rows with holes but no valid data: copy from nearest row (same band) that has data
    bands = np.zeros(nC, int)
    for (g, r), Gk in zip(guides, G):
        bands += (cy > Gk + r).astype(int) + (cy > Gk - r).astype(int)
    hasdata = V.any(1)
    for i in range(nC):
        if Hc[i].any() and not hasdata[i]:
            cand = [k for k in range(nC) if hasdata[k] and bands[k] == bands[i]]
            if not cand:
                continue
            rem = Hc[i].copy()
            for k in sorted(cand, key=lambda k: abs(k - i)):
                ok = rem & (Hc[k] | V[k])
                Cf[i, ok] = Cf[k, ok]
                rem &= ~ok
                if not rem.any():
                    break
    # map back
    out = O.copy()
    for j, x in enumerate(xs):
        ys = np.nonzero(hole[ya:yb, x])[0] + ya
        if len(ys) == 0:
            continue
        yc = np.interp(ys.astype(float), knots_a[j], knots_c[j]) - cy[0]
        f = np.clip(np.floor(yc).astype(int), 0, nC - 2); t = (yc - f)[:, None]
        out[ys, x] = Cf[f, j] * (1 - t) + Cf[f + 1, j] * t
    return out


def vfill(O, P, region, valid, yr, nav=3):
    """column-wise linear interpolation of region pixels from valid pixels above/below (rows within yr)."""
    out = P.copy()
    ya, yb = yr
    ys_, xs_ = np.nonzero(region)
    for x in np.unique(xs_):
        col_valid = np.nonzero(valid[ya:yb, x])[0] + ya
        if len(col_valid) == 0:
            continue
        ys = ys_[xs_ == x]
        pos = np.searchsorted(col_valid, ys)
        for y, p in zip(ys, pos):
            up = col_valid[max(0, p - nav):p]; dn = col_valid[p:p + nav]
            if len(up) and len(dn):
                vu = np.median(O[up, x], 0); vd = np.median(O[dn, x], 0)
                du = y - up.mean(); dd = dn.mean() - y
                out[y, x] = (vu * dd + vd * du) / (du + dd)
            elif len(up):
                out[y, x] = np.median(O[up, x], 0)
            else:
                out[y, x] = np.median(O[dn, x], 0)
    return out


def dirfill(O, P, region, valid, slope, maxlen=60):
    """fill region pixels by sampling the first valid pixel to the LEFT along direction (x-t, y - slope*t)."""
    out = P.copy()
    ys_, xs_ = np.nonzero(region)
    for y, x in zip(ys_, xs_):
        for t in range(1, maxlen):
            xx = x - t; yy = y - slope * t
            y0 = int(np.floor(yy)); f = yy - y0
            if valid[y0, xx] and valid[y0 + 1, xx]:
                out[y, x] = O[y0, xx] * (1 - f) + O[y0 + 1, xx] * f
                break
    return out


def draw_line_aa(P, pts, width, color, ss=8):
    """draw a polyline (pixel-centre coords) with given width onto P (float RGB) with AA coverage."""
    from PIL import ImageDraw
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0 = int(np.floor(min(xs) - width - 2)); y0 = int(np.floor(min(ys) - width - 2))
    x1 = int(np.ceil(max(xs) + width + 3)); y1 = int(np.ceil(max(ys) + width + 3))
    im = Image.new('L', ((x1 - x0) * ss, (y1 - y0) * ss), 0)
    d = ImageDraw.Draw(im)
    hp = [((px - x0 + 0.5) * ss, (py - y0 + 0.5) * ss) for px, py in pts]
    d.line(hp, fill=255, width=int(round(width * ss)), joint='curve')
    r = width * ss / 2
    for (hx, hy) in hp:
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=255)
    a = np.asarray(im, np.float32).reshape(y1 - y0, ss, x1 - x0, ss).mean((1, 3)) / 255.0
    sub = P[y0:y1, x0:x1]
    P[y0:y1, x0:x1] = sub * (1 - a[..., None]) + np.array(color, np.float32) * a[..., None]
    return a, (x0, y0, x1, y1)


A2 = 1242                       # x' = A2 - x  (mirror about x = 621)
INK = np.array([8.0, 5.0, 4.0], np.float32)


def mirror(a):
    out = np.zeros_like(a)
    x = np.arange(W); xm = A2 - x; ok = (xm >= 0) & (xm < W)
    out[:, x[ok]] = a[:, xm[ok]]
    return out


def compose(O, M, sp, sh, P, HOLE):
    # feather the plate into the original over the last 3 px of the hole
    dh = cv2.distanceTransform(HOLE.astype(np.uint8), cv2.DIST_L2, 5)
    w = np.clip(dh / 3.0, 0, 1)[..., None]
    P = O + w * (P - O)
    L = O.mean(2); LP = P.mean(2)
    # --- shadow ratio at the original place (inpaint where the old shoes touch it)
    Rsh = dil(sh, 4)
    r = np.ones((H, W, 3), np.float32)
    good = Rsh & ~dil(M, 2)
    r[good] = np.clip(O[good] / np.maximum(P[good], 1), 0, 1.08)
    holes = (Rsh & dil(M, 2)).astype(np.uint8)
    r8 = np.clip(r * 200, 0, 255).astype(np.uint8)
    r8 = cv2.inpaint(r8, holes, 3, cv2.INPAINT_TELEA)
    r = r8.astype(np.float32) / 200.0
    r[~Rsh] = 1.0
    # --- speed-line alpha at the original place
    Rsp = dil(sp, 2)
    s = np.zeros((H, W), np.float32)
    s[Rsp] = np.clip((LP[Rsp] - L[Rsp]) / np.maximum(LP[Rsp] - INK.mean(), 1), 0, 1)
    # --- background at the original place incl. its own soft elements (for the sprite's soft edge)
    Borig = P * r
    # --- new background: plate + mirrored soft elements
    Bnew = P * mirror(r)
    sm = mirror(s)[..., None]
    Bnew = Bnew * (1 - sm) + INK * sm
    # --- sprite alpha: 1 inside M, luminance coverage on a 2-px outer ring
    ring = dil(M, 3) & ~M
    ringa = dil(M, 2) & ~M
    a = np.zeros((H, W), np.float32)
    a[M] = 1.0
    LB = Borig.mean(2)
    a[ringa] = np.clip((LB[ringa] - L[ringa]) / np.maximum(LB[ringa] - INK.mean(), 1), 0, 1)
    a[ringa & (LB < 90)] = 0.0          # behind a dark background line the AA cannot be told apart
    # transferable residual (sharpening halo) of the ring, clamped; none where the plate is a drawn guess
    res = O - (a[..., None] * INK + (1 - a[..., None]) * Borig)
    res = np.clip(res, -8, 12)
    res[~ring] = 0
    guess = np.zeros((H, W), bool); guess[640:800, 236:312] = True; guess[640:862, 930:1002] = True
    res[guess] = 0
    res[LB < 90] = 0
    # composite at the mirrored place:  new = a*O(q) + (1-a)*Bnew(p) + (1-a)*halo(q)
    am = mirror(a)[..., None]
    Om = mirror(O); resm = mirror(res); ringm = mirror(ring); Mm = mirror(M)
    C = Bnew.copy()
    inner = Mm
    C[inner] = Om[inner]
    rr = ringm
    # ring: alpha-composite the ink part and carry the halo residual
    C[rr] = (am[rr] * INK + (1 - am[rr]) * Bnew[rr]) + resm[rr]
    U = dil(M | sp | sh, 8) | HOLE
    U = U | mirror(U)
    F = O.copy()
    F[U] = C[U]
    return np.clip(F, 0, 255), U, a




def item2(O):
    M = decode_mask(MASK_M)
    S = decode_mask(MASK_S)
    sp, sh, rug = soft_masks(O, M)
    FLAT = np.zeros((H, W), bool); FLAT[641:700] = True; FLAT[806:1100] = True     # flat bands: wider hole (halo)
    HOLE = dil(M, 6) | (dil(M, 9) & FLAT) | dil(sp, 4) | dil(sh, 4)
    bad = dil(M, 7) | (dil(M, 10) & FLAT) | dil(sp, 5) | dil(sh, 5) | dil(rug, 1)
    P = O.copy()
    # ---------------- zone B: under-bench + floor (fill x 305..973, rows 641..911)
    XR = (196, 974); XF = (305, 974)
    xs = np.arange(*XR)
    gL1 = smooth_model(measure_line(O, bad, xs, lambda x: 637, half=6), XR, default=636.5)
    gL2 = smooth_model(measure_line(O, bad, xs, lambda x: 701, half=5), XR, default=701.2)
    gL3 = smooth_model(measure_line(O, bad, xs, lambda x: 733, half=5), XR, default=732.7)
    mL4 = measure_line(O, bad, np.arange(196, 262), lambda x: 761.5, half=4)
    gL4 = np.full(len(xs), np.median(mL4[:, 1]), np.float32)
    mL5 = measure_line(O, bad, np.concatenate([np.arange(200, 262), np.arange(480, 560)]), lambda x: 771, half=4)
    gL5 = smooth_model(mL5, XR)
    gL6 = smooth_model(measure_line(O, bad, np.arange(207, 1000), lambda x: 804, half=5), XR)
    gF2 = smooth_model(measure_step(O, bad, np.arange(207, 1060), 876, 891), XR, k=15)
    gL7 = smooth_model(measure_line(O, bad, np.arange(290, 1060), lambda x: 905, half=6), XR)
    guidesB = [(gL1, 3), (gL2, 3), (gL3, 3), (gL4, 3), (gL5, 3), (gL6, 3), (gF2, 2), (gL7, 3)]
    reg = np.zeros((H, W), bool)
    reg[630:759, 305:974] = True
    reg[759:895, 207:974] = True
    reg[761:895, 974:987] = True
    reg[895:913, 300:974] = True
    fz = np.zeros((H, W), bool)          # where zone B may fill
    fz[641:757, 305:974] = True
    fz[699:738, 295:305] = True           # back rail left end
    fz[757:912, 207:987] = True
    fz[757:759, 207:305] = False
    hole = HOLE & fz
    XR = (196, 987)
    xs = np.arange(*XR)
    guidesB = [(np.concatenate([g, np.full(13, g[-1])]), r) for g, r in guidesB]
    PB = bhi(O, hole, ~bad & reg, XR, (641, 912), guidesB)
    P[hole] = PB[hole]

    # ---------------- zone C: rug (rows 912..1096, fill x 330..1065)
    XRc = (290, 1066)
    gL7c = smooth_model(measure_line(O, bad, np.arange(290, 1066), lambda x: 905, half=6), XRc)
    regc = np.zeros((H, W), bool); regc[900:960, 330:1066] = True; regc[960:1100, 290:1066] = True
    holec = HOLE.copy(); holec[:912] = False; holec[1097:] = False
    holec[:, :XRc[0]] = False; holec[:, XRc[1]:] = False
    PC = bhi(O, holec, ~bad & regc, XRc, (912, 1097), [(gL7c, 3)])
    P[holec] = PC[holec]

    # ---------------- zone A: bench face (rows 538..640, fill x 470..800)
    XRa = (470, 800)
    xsa = np.arange(*XRa)
    gB1 = smooth_model(measure_step(O, bad, xsa, 544, 556), XRa, k=9)
    gB2 = smooth_model(measure_step(O, bad, xsa, 556, 568), XRa, k=9)
    gL0 = smooth_model(measure_line(O, bad, xsa, lambda x: 589, half=5), XRa)
    gL1a = smooth_model(measure_line(O, bad, xsa, lambda x: 637, half=6), XRa)
    rega = np.zeros((H, W), bool); rega[536:646, 470:800] = True
    holea = HOLE.copy(); holea[:538] = False; holea[641:] = False
    holea[:, :XRa[0]] = False; holea[:, XRa[1]:] = False
    PA = bhi(O, holea, ~bad & rega, XRa, (538, 641), [(gB1, 2), (gB2, 2), (gL0, 3), (gL1a, 3)])
    P[holea] = PA[holea]


    INK_D = (14.0, 7.0, 5.0)
    # ---------------- right leg (vertical structure): outline x970-973, dark strip x974-986 (rows<=760), edge line x987-993
    R = np.zeros((H, W), bool)
    R[641:761, 968:987] = True
    R[641:881, 987:995] = True
    reg = R & HOLE
    P = vfill(O, P, reg, ~bad, (641, 881))

    # ---------------- left structure
    # (a) top rod end: far leg / edge / side strip / edge  (x 240..305, rows 641..699)
    R = np.zeros((H, W), bool); R[641:700, 236:306] = True
    P = vfill(O, P, R & HOLE, ~dil(M, 2), (641, 700))
    # (b) far leg / edge / side strip right of the side-rail end (x 270..294, rows 700..757)
    valid2 = ~dil(M, 2)
    R = np.zeros((H, W), bool); R[700:759, 270:295] = True
    P = vfill(O, P, R & HOLE, valid2, (690, 759))
    # (c) side rail end (x 250..270, rows 700..757): vector drawing
    LIGHT = np.median(O[757:759, 244:257].reshape(-1, 3), 0)
    FACE = np.array([111, 82, 56], np.float32); TOPF = np.array([117, 90, 67], np.float32); LEG = np.array([108, 80, 53], np.float32)
    xr0, xr1 = 250, 271
    reg_c = np.zeros((H, W), bool); reg_c[700:759, xr0:xr1] = True; reg_c &= HOLE
    SS = 8
    def yd2(x): return 706.0 + (268.5 - x) * 0.667          # second diagonal (top face / front face)
    def yd3(x): return 737.0 + (268.5 - x) * 0.60           # third diagonal (front face bottom)
    yy, xx = np.mgrid[700:759, xr0:xr1]
    acc = np.zeros(yy.shape + (3,), np.float32)
    for sy in range(SS):
        for sx in range(SS):
            fx = xx - 0.5 + (sx + 0.5) / SS; fy = yy - 0.5 + (sy + 0.5) / SS
            col = np.where(((fy < yd2(fx)) & (fx <= 268.5))[..., None], TOPF,
                  np.where(((fy < yd3(fx)) & (fx <= 268.5))[..., None], FACE,
                  np.where((fy > 756.5)[..., None], LIGHT, LEG)))
            acc += col
    acc /= SS * SS
    sub = P[700:759, xr0:xr1]; m = reg_c[700:759, xr0:xr1]
    sub[m] = acc[m]
    P[700:759, xr0:xr1] = sub
    # lines (only inside the region, so build on a copy and paste back the region)
    Q = P.copy()
    draw_line_aa(Q, [(xr0 - 6, 706.0), (268.5, 706.0)], 2.6, INK_D)                          # top edge
    draw_line_aa(Q, [(xr0 - 6, yd2(xr0 - 6)), (268.5, yd2(268.5))], 2.4, INK_D)              # 2nd diagonal
    draw_line_aa(Q, [(xr0 - 6, yd3(xr0 - 6)), (268.5, yd3(268.5))], 2.6, INK_D)              # 3rd diagonal
    draw_line_aa(Q, [(268.5, 706.0), (268.5, 737.0)], 2.6, INK_D)                           # end edge
    P[reg_c] = Q[reg_c]
    # (d) back rail left end (x 293..305, rows 699..738): rail band from zone B already filled for x>=295;
    #     left of the end edge: side strip (vertical fill from below), then draw the end edge with round corners
    R = np.zeros((H, W), bool); R[699:759, 286:306] = True
    side = vfill(O, P, R & HOLE, valid2, (738, 759))
    regd = np.zeros((H, W), bool); regd[699:739, 286:306] = True; regd &= HOLE
    # coverage of the rail (rounded rectangle from x=295.2, y 701.6..733.0, corner r=4)
    yy, xx = np.mgrid[699:739, 286:306]
    acc = np.zeros(yy.shape, np.float32)
    x_end, yt, yb, rr = 295.2, 701.6, 733.0, 4.0
    for sy in range(SS):
        for sx in range(SS):
            fx = xx - 0.5 + (sx + 0.5) / SS; fy = yy - 0.5 + (sy + 0.5) / SS
            cx = x_end + rr
            inside = (fx >= x_end) & (fy >= 699.0) & (fy <= np.where(fx < 305, 734.6, 736.5))
            tl = (fx < cx) & (fy < yt + rr)
            bl = (fx < cx) & (fy > yb - rr)
            dtl = (fx - cx) ** 2 + (fy - (yt + rr)) ** 2 <= rr ** 2
            dbl = (fx - cx) ** 2 + (fy - (yb - rr)) ** 2 <= rr ** 2
            inside = np.where(tl, dtl, np.where(bl, dbl, inside))
            acc += inside
    acc /= SS * SS
    sub = P[699:739, 286:306]; sd = side[699:739, 286:306]; m = regd[699:739, 286:306]
    blend = sub * acc[..., None] + sd * (1 - acc[..., None])
    sub[m] = blend[m]
    P[699:739, 286:306] = sub
    Q = P.copy()
    arc1 = [(x_end + rr - rr * np.sin(np.radians(t)), yt + rr - rr * np.cos(np.radians(t))) for t in range(0, 91, 10)]
    arc2 = [(x_end + rr - rr * np.cos(np.radians(t)), yb - rr + rr * np.sin(np.radians(t))) for t in range(0, 91, 10)]
    draw_line_aa(Q, [(x_end + rr + 3, yt)] + arc1 + arc2 + [(x_end + rr + 3, yb)], 2.6, INK_D)
    P[regd] = Q[regd]
    P[R & HOLE & ~regd] = side[R & HOLE & ~regd]


    # ---------------- rug edge line: the original line tapers out toward the old trouser leg (x 532..548);
    #                  after the flip the leg is gone there, so continue the line with the clean column x=528
    for x in range(529, 576):
        P[896:917, x] = O[896:917, 528]
    HOLE[896:917, 529:576] = True          # (so that the final feather keeps this continuation)

    # ---------------- tuft over the bench rod's cream knot (x 631..690, rows 515..548)
    AX2 = 1262
    clean1 = ~dil(M, 1)
    # left half of the knot bottom (x 600..631, rows 515..542): original pixels are clean but were inside the hole ring
    regl = np.zeros((H, W), bool); regl[515:543, 600:632] = True; regl &= HOLE & clean1
    P[regl] = O[regl]
    # right half (x 631..660): mirror of the left half about x = 631
    reg_t = np.zeros((H, W), bool); reg_t[515:543, 631:661] = True; reg_t &= HOLE
    ys, xs = np.nonzero(reg_t)
    src_ok = clean1[ys, AX2 - xs]
    ys, xs = ys[src_ok], xs[src_ok]
    P[ys, xs] = P[ys, AX2 - xs]

    # right of the knot: bench top under the segment's bottom line -> row-wise interpolation
    reg_r = np.zeros((H, W), bool); reg_r[515:541, 661:692] = True; reg_r &= HOLE
    okm = ~dil(M, 3)
    for y in range(515, 541):
        xs_h = np.nonzero(reg_r[y])[0]
        if len(xs_h) == 0: continue
        xl = xs_h.min() - 1
        xr = xs_h.max() + 1
        while not okm[y, xr]: xr += 1
        vl = P[y, xl]; vr = np.median(O[y, xr:xr + 4], 0)
        for x in xs_h:
            t = (x - xl) / (xr - xl)
            P[y, x] = vl * (1 - t) + vr * t
    # trim spurs where the rod ends touch background lines: keep only the outline band (<= 5 px) around the
    # non-dark sprite interior, near the rod ends
    zone = np.zeros_like(M); zone[640:800, 238:312] = True; zone[640:862, 930:1002] = True
    zone[512:548, 622:692] = True          # hair tuft where it touched the bench rod's knot
    n_, l_, st_, _ = cv2.connectedComponentsWithStats(S.astype(np.uint8), connectivity=4)
    small = np.isin(l_, [i for i in range(1, n_) if st_[i, 4] < 20])
    S = S & ~(small & zone)
    dS = cv2.distanceTransform((~S).astype(np.uint8), cv2.DIST_L2, 5)
    Lum = O.mean(2)
    cut = zone & M & ((dS > 5.0) | ((Lum >= 70) & (dS > 1.5) & ~S))
    M = M & ~cut
    Mo = cv2.morphologyEx(M.astype(np.uint8), cv2.MORPH_OPEN, ell(3)) > 0
    cut2 = zone & M & ~Mo
    M = M & ~cut2

    F, U, a = compose(O, M, sp, sh, P, HOLE)
    return F


# =====================================================================  출력
def bbox(mask):
    ys, xs = np.nonzero(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]


def mkcmp(before, after, box, out, maxlong=1400, gap=12, bar=34):
    b = before.crop(box); a = after.crop(box)
    w, h = b.size
    s = min((maxlong - gap) / 2 / w, (maxlong - bar) / h)
    rs = Image.LANCZOS if s < 1 else Image.BICUBIC
    Wd, Hd = max(1, int(w * s)), max(1, int(h * s))
    im = Image.new('RGB', (Wd * 2 + gap, Hd + bar), (255, 255, 255))
    im.paste(b.resize((Wd, Hd), rs), (0, bar)); im.paste(a.resize((Wd, Hd), rs), (Wd + gap, bar))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    except Exception:
        f = ImageFont.load_default()
    d.text((8, 5), 'BEFORE', fill=(0, 0, 0), font=f)
    d.text((Wd + gap + 8, 5), 'AFTER', fill=(0, 0, 0), font=f)
    im.save(out)


if __name__ == '__main__':
    O = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
    P1 = item1(O)
    F2 = item2(O)
    q = lambda a: np.clip(a + 0.5, 0, 255).astype(np.uint8)
    O8 = O.astype(np.uint8)
    N = O8.copy()
    c1 = (q(P1) != O8).any(2)
    N[c1] = q(P1)[c1]
    c2 = (q(F2) != O8).any(2)
    assert not (c1 & c2).any()
    N[c2] = q(F2)[c2]
    Image.fromarray(N).save(OUT + '/final_new.png')
    print('item1 changed box [x,y,w,h]:', bbox(c1), 'px', int(c1.sum()))
    print('item2 changed box [x,y,w,h]:', bbox(c2), 'px', int(c2.sum()))
    print('all changed box   [x,y,w,h]:', bbox(c1 | c2))
    before = Image.fromarray(O8); after = Image.fromarray(N)
    mkcmp(before, after, (990, 440, 1500, 600), OUT + '/cmp_1.png')
    mkcmp(before, after, (190, 500, 1070, 1100), OUT + '/cmp_2.png')

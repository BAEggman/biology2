#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L45b 그림 고침 (PIL · numpy · cv2 · scipy 만 씀 — 인터넷 · 그림 생성 AI 없음)

    python3 fix.py            # final_new.png · cmp_1.png · cmp_2.png 을 다시 만든다

원본(읽기만):  SP/L45b/r1/final_v1.png        (2048x1144 RGB)
결과:          SP/picfix/L45b/final_new.png   (2048x1144 RGB)

항목 2 — 빛띠 잇기
  두 무지개 띠는 「곧은 경계선 10줄(바탕|검정|보라|파랑|청록|초록|노랑|주황|빨강|검정|바탕)」이다.
  ① 그림에 남아 있는 띠에서 경계선마다 줄(x = a*y + b)을 재고(행마다 반 화소 이하로),
  ② 경계선 둘레의 색 단면(0.25 px 칸 · 가운데값)을 그림 픽셀에서 그대로 떠서,
  ③ 그 줄 · 그 단면을 위쪽(광원 쪽)으로 늘여 그린다 — 색 · 윤곽선 굵기 · 안티에일리어싱 · 흰 테가
     모두 원본 픽셀에서 온 것이라 이어 붙인 자리가 남지 않는다.
  왼 띠: x<160 의 옛 띠 조각(윤곽선 없는 겹 띠)을 바탕으로 지우고 새 띠를 그림 위 끝까지 늘인다.
  오른 띠: 왼 자매의 초록 되튐 줄 뒤를 지나 그림 위 끝까지 늘인다(초록 줄과 그 검은 윤곽선은 그대로).

항목 1 — 액자 윗변의 색 조각
  왼 액자: (있던 주황-빨강 조각의 주황 띠만 빨강으로) + 보라 조각 하나를 보라 줄 발치 아래에 새로
           (꼴은 오른 액자의 같은 자리 조각 — 옛 보라-파랑 조각 — 의 꼴을 뒤집지 않고 옮겨 씀).
  오른 액자: 보라-파랑 조각 → 파랑 한 빛깔 · 주황-빨강 조각 → 주황 한 빛깔.
  조각 색은 무지개 띠 줄의 가운데 색을 재어 쓴다.
"""
import os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = SP + '/L45b/r1/final_v1.png'
OUTDIR = SP + '/picfix/L45b'

BGREF = np.array([231., 242.5, 230.])      # 하늘 바탕(거의 평평하다)
K = np.zeros(3)
NB = 10                                    # 경계선 수


# ----------------------------------------------------------------------------
# 1. 띠 재기
# ----------------------------------------------------------------------------
def refcols(P, B, C, G, Y, O, R):
    return [BGREF, K] + [np.array(c, float) for c in (P, B, C, G, Y, O, R)] + [K, BGREF]


def cross_one(img, cols, y, i, xguess, win=6):
    """행 y 에서 i 번째 경계(색 cols[i] -> cols[i+1])가 반쯤 넘어가는 x(화소 이하 자리까지)."""
    c0, c1 = cols[i], cols[i + 1]
    d = c1 - c0
    x0 = int(round(xguess)) - win
    x1 = int(round(xguess)) + win + 1
    if x0 < 0 or x1 > img.shape[1] or y < 0 or y >= img.shape[0]:
        return np.nan
    row = img[y, x0:x1]
    t = ((row - c0) @ d) / (d @ d)
    proj = c0 + np.clip(t, 0, 1)[:, None] * d
    off = np.abs(row - proj).max(1)          # 두 색을 잇는 선에서 벗어난 만큼(딴 물건 거르기)
    best = None
    for j in range(len(row) - 1):
        if t[j] < 0.5 <= t[j + 1] and off[j] < 40 and off[j + 1] < 40:
            x = x0 + j + (0.5 - t[j]) / (t[j + 1] - t[j])
            if best is None or abs(x - xguess) < abs(best - xguess):
                best = x
    return np.nan if best is None else best


def track(img, cols, i, y0, x0, slope, ymin, ymax, tol=1.5):
    """씨앗 행 y0 에서 위아래로 경계를 따라간다(세 번 내리 놓치면 멈춤)."""
    pts = {}
    for direction in (-1, 1):
        ys, xs = [], []
        y, xg, miss = y0, x0, 0
        while ymin <= y <= ymax:
            x = cross_one(img, cols, y, i, xg)
            if not np.isnan(x) and abs(x - xg) < tol:
                pts[y] = x
                miss = 0
                ys.append(y)
                xs.append(x)
                if len(ys) >= 12:
                    p = np.polyfit(ys[-40:], xs[-40:], 1)
                    xg = np.polyval(p, y + direction)
                else:
                    xg = x + slope * direction
            else:
                miss += 1
                xg = xg + slope * direction
                if miss >= 3:
                    break
            y += direction
    ys = np.array(sorted(pts))
    xs = np.array([pts[y] for y in ys])
    return ys, xs


class Band:
    """경계선 10줄 + 경계선마다의 색 단면(가로 거리 d 의 함수)."""

    def __init__(self, img, cols, seeds, y0, slope, ymin, ymax, xmin=0, trim=8, hw=13.0, binw=0.25):
        self.cols = cols
        self.hw = hw
        self.binw = binw
        self.nb = int(round(2 * hw / binw)) + 1
        fits, rng = [], []
        for i, x0 in enumerate(seeds):
            ys, xs = track(img, cols, i, y0, x0, slope, ymin, ymax)
            fits.append(np.polyfit(ys, xs, 1))
            rng.append((int(ys.min()), int(ys.max())))
        self.A = np.array([p[0] for p in fits])
        self.Bc = np.array([p[1] for p in fits])
        self.rng = rng
        self._profiles(img, xmin, trim)

    def _profiles(self, img, xmin, trim):
        nb, binw, hw = self.nb, self.binw, self.hw
        samples = [[[] for _ in range(nb)] for _ in range(NB)]
        ylo = min(r[0] for r in self.rng)
        yhi = max(r[1] for r in self.rng)
        for y in range(ylo, yhi + 1):
            Xy = self.A * y + self.Bc
            for x in range(max(int(np.floor(Xy[0] - hw)), xmin), int(np.ceil(Xy[-1] + hw)) + 1):
                j = int(np.argmin(np.abs(x - Xy)))            # 가장 가까운 경계
                if not (self.rng[j][0] + trim <= y <= self.rng[j][1] - trim):
                    continue
                d = x - Xy[j]
                if abs(d) > hw:
                    continue
                c0, c1 = self.cols[j], self.cols[j + 1]
                v = img[y, x]
                dd = c1 - c0
                t = np.clip(((v - c0) @ dd) / (dd @ dd), 0, 1)
                if np.abs(v - (c0 + t * dd)).max() > 60:       # 딴 물건(초록 줄 · 액자)은 버린다
                    continue
                samples[j][int(round((d + hw) / binw))].append(v)
        T = np.full((NB, nb, 3), np.nan)
        for j in range(NB):
            for k in range(nb):
                s = samples[j][k]
                if len(s) >= 5:
                    T[j, k] = np.median(np.array(s), axis=0)
            valid = np.where(~np.isnan(T[j, :, 0]))[0]
            for c in range(3):
                T[j, :, c] = np.interp(np.arange(nb), valid, T[j, valid, c])
        Ts = T.copy()
        Ts[:, 1:-1] = (T[:, :-2] + 2 * T[:, 1:-1] + T[:, 2:]) / 4
        self.T = Ts

    def render(self, xs, ys):
        """화소 (xs, ys) 의 띠 색 · 띠의 손이 닿는 자리인가."""
        Xb = self.A[None, :] * ys[:, None] + self.Bc[None, :]
        d = xs[:, None] - Xb
        j = np.argmin(np.abs(d), axis=1)
        dj = d[np.arange(len(j)), j]
        inr = np.abs(dj) <= self.hw
        pos = np.clip((dj + self.hw) / self.binw, 0, self.nb - 1)
        k0 = np.floor(pos).astype(int)
        k1 = np.minimum(k0 + 1, self.nb - 1)
        f = (pos - k0)[:, None]
        col = self.T[j, k0] * (1 - f) + self.T[j, k1] * f
        inside = (xs >= Xb[:, 0]) & (xs <= Xb[:, 9])
        left = xs < Xb[:, 0]
        return col, inr | inside, inside, left

    def values(self, xs, ys, base):
        """base(밑에 깔린 바탕 화소) 위에 띠를 얹은 값.
        띠 안: 띠 색 x (바탕이 얼마나 어두운가 — 가로지르는 검은 윤곽선의 안티에일리어싱을 살린다)
        띠 밖: 바탕 x (단면 / 먼 바탕) — 띠 윤곽선의 바깥 번짐과 흰 테."""
        col, inr, inside, left = self.render(xs, ys)
        ratio_out = np.where(left[:, None], col / self.T[0, 0][None], col / self.T[9, -1][None])
        dev = np.abs(base - BGREF[None]).max(1)
        ratio_in = np.where((dev > 3)[:, None], np.clip(base / BGREF[None], 0, 1.08), 1.0)
        val = np.where(inside[:, None], col * ratio_in, base * ratio_out)
        return np.clip(val, 0, 255), inr

    def core(self, img, k, y0, y1, xmin=0):
        """k 번째 줄(0 보라 … 6 빨강)의 가운데 색(가운데값)."""
        j = k + 1
        v = []
        for y in range(y0, y1):
            xa = self.A[j] * y + self.Bc[j] + 5
            xb = self.A[j + 1] * y + self.Bc[j + 1] - 5
            for x in range(int(np.ceil(xa)), int(np.floor(xb)) + 1):
                if x >= xmin:
                    v.append(img[y, x])
        return np.median(np.array(v), axis=0)


def make_bands(src):
    colsL = refcols([155, 75, 221], [79, 88, 219], [38, 196, 220], [74, 194, 64], [251, 231, 1], [253, 133, 0], [235, 48, 36])
    # 씨앗: y=200 에서의 경계 x (왼 띠) · x>=166 만 믿는다(160 이 옛 이음매)
    L = Band(src, colsL, [182.90, 187.46, 203.46, 222.03, 240.90, 262.03, 281.96, 304.93, 324.79, 329.00],
             200, 0.59, 0, 268, xmin=166)
    colsR = refcols([154, 77, 220], [80, 88, 215], [38, 195, 222], [76, 194, 62], [250, 230, 2], [252, 132, 1], [234, 48, 34])
    # 씨앗: y=290 에서의 경계 x (오른 띠)
    R = Band(src, colsR, [433.73, 437.78, 449.90, 465.46, 480.52, 496.42, 511.52, 527.46, 541.54, 545.91],
             290, 0.69, 100, 340)
    return L, R


# ----------------------------------------------------------------------------
# 2. 항목 2 — 빛띠 잇기
# ----------------------------------------------------------------------------
def fix_left_band(src, out, L):
    X1, Y1 = 200, 250
    reg = src[:Y1, :X1]
    nonbg = (np.abs(reg - BGREF).max(2) > 4).astype(np.uint8)
    # 깨끗한 바탕 — 바탕 화소만의 가중 평균(이 둘레의 바탕은 1~2 단계밖에 안 흔들린다)
    valid = (cv2.dilate(nonbg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))) == 0).astype(np.float64)
    num = cv2.GaussianBlur(reg * valid[..., None], (0, 0), 14)
    den = cv2.GaussianBlur(valid, (0, 0), 14)
    med = np.median(reg[valid > 0], axis=0)
    Bg = np.where(den[..., None] > 1e-3, num / np.maximum(den[..., None], 1e-6), med[None, None])
    # 지울 곳: x<160 의 옛 띠 조각(가장자리 번짐까지) + 이음매 세 줄(160~162 — 붙인 자리의 물결)
    frag = cv2.dilate(nonbg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))).astype(bool)
    yy, xx = np.mgrid[0:Y1, 0:X1]
    erase = ((frag & (xx < 160)) | ((xx >= 160) & (xx <= 162))) & (yy < 240)
    o = out[:Y1, :X1]
    o[erase] = Bg[erase]
    # 새 띠: x<=162 는 온전히 모형, 163~166 은 원본과 섞어 넘긴다, 167 부터는 손대지 않는다
    XF0, XF1 = 162, 167
    sel = (xx < XF1)
    xs = xx[sel].astype(float)
    ys = yy[sel].astype(float)
    val, inr = L.values(xs, ys, Bg[sel])
    w = np.clip((xs - XF0) / (XF1 - XF0), 0, 1)[:, None]
    o[sel] = np.where(inr[:, None], w * src[:Y1, :X1][sel] + (1 - w) * val, o[sel])


def fix_right_band(src, out, R, ymax=246):
    mx = src.max(2)
    for y in range(0, ymax):
        Xy = R.A * y + R.Bc
        xs = np.arange(int(np.floor(Xy[0] - R.hw)), int(np.ceil(Xy[9] + R.hw)) + 1)
        dark = np.where(mx[y, xs] < 70)[0]          # 초록 되튐 줄의 바깥 검은 윤곽선 — 여기서 멈춘다
        if len(dark):
            xs = xs[:dark[0]]
        if len(xs) == 0:
            continue
        val, inr = R.values(xs.astype(float), np.full(xs.shape, float(y)), src[y, xs])
        out[y, xs] = np.where(inr[:, None], val, src[y, xs])


# ----------------------------------------------------------------------------
# 3. 항목 1 — 액자 윗변의 색 조각
# ----------------------------------------------------------------------------
def shift_profile(Pf, ys, s):
    out = np.empty_like(Pf)
    for c in range(3):
        out[:, c] = np.interp(ys - s, ys, Pf[:, c])
    return out


def bar_bg(img, xa, xb, ya, yb, colsL, colsR, pad=8):
    """조각 밑의 액자 윗변을 되살린다 — 조각 왼쪽 · 오른쪽 기둥의 세로 단면을 윗변의 기울기만큼
    밀어 가며 섞는다(윗변은 가로로 거의 한결같은 띠무늬다)."""
    ys = np.arange(ya - pad, yb + pad).astype(float)
    PL = img[ya - pad:yb + pad, colsL[0]:colsL[1] + 1].mean(1)
    PR = img[ya - pad:yb + pad, colsR[0]:colsR[1] + 1].mean(1)
    xLc = (colsL[0] + colsL[1]) / 2
    xRc = (colsR[0] + colsR[1]) / 2
    lum = lambda Pf: Pf @ np.array([0.3, 0.59, 0.11])
    best = None
    for s in np.arange(-5, 5.01, 0.05):
        e = ((lum(shift_profile(PL, ys, s)) - lum(PR))[pad:-pad] ** 2).mean()
        if best is None or e < best[0]:
            best = (e, s)
    tilt = best[1] / (xRc - xLc)
    bg = np.zeros((yb - ya, xb - xa, 3))
    for x in range(xa, xb):
        f = np.clip((x - xLc) / (xRc - xLc), 0, 1)
        a_ = shift_profile(PL, ys, tilt * (x - xLc))
        b_ = shift_profile(PR, ys, tilt * (x - xRc))
        bg[:, x - xa] = ((1 - f) * a_ + f * b_)[pad:-pad]
    return bg, tilt


def unmix(pix, bg, A, B):
    """pix = bg + u(A-bg) + v(B-bg) · u,v>=0 · u+v<=1 — 조각의 두 빛깔이 화소마다 얼마씩 덮였나."""
    sh = pix.shape[:-1]
    p = pix.reshape(-1, 3)
    b = bg.reshape(-1, 3)
    da = A[None] - b
    db = B[None] - b
    r = p - b
    aa = (da * da).sum(1)
    bb = (db * db).sum(1)
    ab = (da * db).sum(1)
    ra = (r * da).sum(1)
    rb = (r * db).sum(1)
    det = aa * bb - ab * ab + 1e-9
    u = (ra * bb - rb * ab) / det
    v = (rb * aa - ra * ab) / det
    un = u < 0
    vn = v < 0
    v1 = np.clip(rb / (bb + 1e-9), 0, 1)
    u1 = np.clip(ra / (aa + 1e-9), 0, 1)
    u, v = np.where(un, 0, u), np.where(un, v1, v)
    v, u = np.where(vn & ~un, 0, v), np.where(vn & ~un, u1, u)
    over = (u + v) > 1
    dab = A - B
    t = np.clip(((p - B[None]) @ dab) / (dab @ dab), 0, 1)
    u = np.where(over, t, u)
    v = np.where(over, 1 - t, v)
    return u.reshape(sh), v.reshape(sh)


SIG = 1.25          # 조각 가장자리의 부드러움(원본 조각의 번짐에 맞춤)


def clean_matte(alpha):
    """덮임 지도 -> 구멍 · 톱니 없는 볼록한 조각 꼴 + 부드러운 가장자리."""
    M = cv2.GaussianBlur(alpha, (0, 0), 0.8) > 0.5
    M = ndi.binary_fill_holes(M)
    lab, n = ndi.label(M)
    if n > 1:
        sizes = ndi.sum(M, lab, range(1, n + 1))
        M = lab == (1 + int(np.argmax(sizes)))
    pts = np.argwhere(M)[:, ::-1].astype(np.int32)
    hull = np.zeros(M.shape, np.uint8)
    cv2.fillConvexPoly(hull, cv2.convexHull(pts), 1)
    M = hull.astype(bool)
    return M, cv2.GaussianBlur(M.astype(np.float64), (0, 0), SIG)


def membrane(pix, bg, alpha, sig=4.0):
    """되살린 윗변(bg)을 조각 바깥의 실제 화소에 꼭 맞춘다(차이를 안쪽으로 번지게 메운다)."""
    known = (alpha < 0.02).astype(np.float64)
    res = (pix - bg) * known[..., None]
    num = cv2.GaussianBlur(res, (0, 0), sig)
    den = cv2.GaussianBlur(known, (0, 0), sig)
    fill = num / np.maximum(den[..., None], 1e-6)
    return bg + np.where(known[..., None] > 0, pix - bg, fill)


def redraw_tab(src, out, box, colsL, colsR, A, B, C):
    """두 빛깔(A·B) 조각을 지우고 같은 자리 · 같은 꼴로 한 빛깔(C) 조각을 다시 얹는다."""
    x, y, w, h = box
    bg, _ = bar_bg(src, x, x + w, y, y + h, colsL, colsR)
    pix = src[y:y + h, x:x + w]
    u, v = unmix(pix, bg, A, B)
    al = np.clip(u + v, 0, 1)
    M, am = clean_matte(al)
    bge = membrane(pix, bg, al)
    reg = ndi.binary_dilation(al >= 0.02, iterations=1) | (am > 0.004)
    new = bge * (1 - am[..., None]) + am[..., None] * C
    out[y:y + h, x:x + w] = np.where(reg[..., None], new, out[y:y + h, x:x + w])
    return M


def fix_tabs(src, out, L, R):
    # 조각 색 = 무지개 띠 줄의 가운데 색(그림에서 잰 값)
    P = L.core(src, 0, 60, 262, 168)      # 보라  (왼 띠)
    Rd = L.core(src, 6, 60, 262, 168)     # 빨강  (왼 띠)
    Ol = L.core(src, 5, 60, 262, 168)     # 주황  (왼 띠 — 왼 액자 조각의 주황 띠를 가려내는 데)
    Bl = R.core(src, 1, 256, 290)         # 파랑  (오른 띠)
    Or = R.core(src, 5, 256, 290)         # 주황  (오른 띠)

    # (가) 왼 액자의 주황-빨강 조각 -> 빨강: 주황이 덮인 만큼만 빨강 쪽으로 옮긴다(빨강 몸통은 그대로)
    box = (314, 342, 40, 36)
    x, y, w, h = box
    bg, _ = bar_bg(src, x, x + w, y, y + h, (309, 313), (350, 352))
    u, v = unmix(src[y:y + h, x:x + w], bg, Ol, Rd)
    ue = np.clip((u - 0.04) / 0.96, 0, 1)
    out[y:y + h, x:x + w] = src[y:y + h, x:x + w] + ue[..., None] * (Rd - Ol)[None, None]

    # (나) 오른 액자 왼 조각(보라-파랑) -> 파랑
    BOX_B = (466, 341, 36, 33)
    M_B = redraw_tab(src, out, BOX_B, (462, 466), (501, 505), P, Bl, Bl)
    # (다) 오른 액자 오른 조각(주황-빨강) -> 주황 · 이 조각의 빨강은 띠 빨강보다 주홍이라 따로 적는다
    redraw_tab(src, out, (524, 341, 38, 33), (519, 523), (561, 565), Or, np.array([236., 54., 20.]), Or)

    # (라) 왼 액자에 보라 조각 하나 — 오른 액자의 같은 자리 조각(보라-파랑 조각 = 줄 발치 왼쪽 조각)의 꼴을
    #      그대로(뒤집지 않고) 옮겨 왼 띠 보라 줄 발치(y=333 에서 x 266~283 · 가운데 275) 아래에 단다.
    #      두 액자 윗변의 세로 단면(검은 윗선 · 겉면 · 안쪽 턱 두 줄 · 창)을 맞춰 보면 x=275 에서 왼 액자가
    #      4.8 px 낮고, 왼 액자 윗변은 오른쪽으로 갈수록 올라간다(-0.046 px/px · 오른 액자는 수평).
    place_tab(out, M_B, BOX_B, xc_t=275.0, dy0=4.8, tilt=-0.046, C=P)
    return dict(P=P, Rd=Rd, Bl=Bl, Or=Or)


def place_tab(out, M, box_src, xc_t, dy0, tilt, C):
    """조각 꼴 M(원본 box_src 자리의 이진 꼴)을 가로 가운데가 xc_t 에 오게 옮겨(dy0 만큼 내리고, 윗변 기울기
    tilt 만큼 비스듬히) 부드러운 가장자리(SIG)로 빛깔 C 를 얹는다."""
    x, y, w, h = box_src
    ys_, xs_ = np.nonzero(M)
    xc_s = x + (xs_.min() + xs_.max()) / 2.0
    dx = xc_t - xc_s
    X0 = int(np.floor(x + xs_.min() + dx)) - 6
    X1 = int(np.ceil(x + xs_.max() + dx)) + 7
    Y0 = int(np.floor(y + ys_.min() + dy0 - abs(tilt) * (X1 - X0))) - 6
    Y1 = int(np.ceil(y + ys_.max() + dy0 + abs(tilt) * (X1 - X0))) + 7
    YY, XX = np.mgrid[Y0:Y1, X0:X1].astype(np.float64)
    sx = XX - dx - x
    sy = YY - dy0 - tilt * (XX - xc_t) - y
    Mt = ndi.map_coordinates(M.astype(np.float64), [sy, sx], order=1, mode='constant', cval=0.0)
    am = cv2.GaussianBlur(Mt, (0, 0), SIG)
    sl = (slice(Y0, Y1), slice(X0, X1))
    out[sl] = np.where((am > 0.004)[..., None], out[sl] * (1 - am[..., None]) + am[..., None] * C, out[sl])
    return (X0, Y0, X1, Y1)


# ----------------------------------------------------------------------------
# 4. 묶기 · 견줌 그림
# ----------------------------------------------------------------------------
def build():
    src8 = np.array(Image.open(SRC).convert('RGB'))
    src = src8.astype(np.float64)
    out = src.copy()
    L, R = make_bands(src)
    fix_left_band(src, out, L)
    fix_right_band(src, out, R)
    cols = fix_tabs(src, out, L, R)
    res = np.clip(np.rint(out), 0, 255).astype(np.uint8)
    # 두 단계 이하로만 달라진 화소는 원본으로 되돌린다(바탕을 쓸데없이 건드리지 않는다)
    small = np.abs(res.astype(int) - src8.astype(int)).max(2) <= 2
    res[small] = src8[small]
    return src8, res, cols


def _font(size):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
              '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def cmp_image(src8, res, box, name, panel_w=694):
    x, y, w, h = box
    s = panel_w / w
    size = (panel_w, int(round(h * s)))
    rs = Image.LANCZOS
    a = Image.fromarray(src8[y:y + h, x:x + w]).resize(size, rs)
    b = Image.fromarray(res[y:y + h, x:x + w]).resize(size, rs)
    bar, gap = 30, 10
    im = Image.new('RGB', (panel_w * 2 + gap, size[1] + bar), (255, 255, 255))
    im.paste(a, (0, bar))
    im.paste(b, (panel_w + gap, bar))
    d = ImageDraw.Draw(im)
    f = _font(20)
    d.text((6, 4), 'BEFORE', fill=(0, 0, 0), font=f)
    d.text((panel_w + gap + 6, 4), 'AFTER', fill=(0, 0, 0), font=f)
    im.save(os.path.join(OUTDIR, name))


def bbox(mask):
    ys, xs = np.nonzero(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]


if __name__ == '__main__':
    src8, res, cols = build()
    assert res.shape == (1144, 2048, 3)
    Image.fromarray(res, 'RGB').save(os.path.join(OUTDIR, 'final_new.png'))
    cmp_image(src8, res, (245, 300, 335, 82), 'cmp_1.png')      # 항목 1: 두 액자의 윗변
    cmp_image(src8, res, (0, 0, 560, 345), 'cmp_2.png')         # 항목 2: 두 빛띠
    ch = np.abs(res.astype(int) - src8.astype(int)).sum(2) > 0
    print('조각 색  보라 %s  빨강 %s  파랑 %s  주황 %s' % tuple(np.rint(cols[k]).astype(int).tolist() for k in ('P', 'Rd', 'Bl', 'Or')))
    print('달라진 화소 %d · 전체 상자 %s' % (ch.sum(), bbox(ch)))
    m1 = ch.copy(); m1[:300] = False
    m2 = ch.copy(); m2[300:] = False
    print('항목 1 (조각) 상자 %s · 화소 %d' % (bbox(m1), m1.sum()))
    print('항목 2 (빛띠) 상자 %s · 화소 %d' % (bbox(m2), m2.sum()))
    mL = m2.copy(); mL[:, 200:] = False
    mR = m2.copy(); mR[:, :200] = False
    print('  왼 띠 %s · 오른 띠 %s' % (bbox(mL), bbox(mR)))
    for nm, (xa, xb) in (('왼 액자 보라', (250, 300)), ('왼 액자 빨강', (300, 360)), ('오른 액자 파랑', (460, 510)), ('오른 액자 주황', (515, 570))):
        m = m1.copy(); m[:, :xa] = False; m[:, xb:] = False
        print('  %s %s · 화소 %d' % (nm, bbox(m) if m.any() else None, m.sum()))

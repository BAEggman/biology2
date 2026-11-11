#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L19b 그림 고침 — 원본(SP/L19b/r1/final_v1.png)에서 final_new.png 를 다시 만든다.
   1) 앞 덩치(멱살 잡은 쪽) 어깨의 붉은 겹동그라미 도장을 지운다 — 곁 살빛으로 메우고 어깨 윤곽선은 그대로
   2) 뒤 덩치(아치 밑 · 두 손 편 쪽) 어깨의 흐린 붉은 자국을 지우고, 같은 꼴의 또렷한 겹동그라미 도장을 찍는다
   3) 금고문 레버에 끼운 음반의 두꺼운 옆면(겹선 띠)을 걷어 내 얇은 한 장으로
   쓰는 것: PIL · numpy · cv2 뿐.  원본은 읽기만 한다.
   사용: python3 fix.py            -> 세 항목 모두
         python3 fix.py 13         -> 1·3 만 (점검용)
"""
import os
import sys
import numpy as np
import cv2
from PIL import Image

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = os.path.join(SP, 'L19b/r1/final_v1.png')
OUTDIR = os.path.join(SP, 'picfix/L19b')
OUT = os.path.join(OUTDIR, 'final_new.png')

STAMP_RED = np.array([200.0, 30.0, 40.0])      # 앞 도장의 붉은색(원본에서 잰 값)


def lum_of(a):
    return a.mean(axis=2)


def laplace_fill(sub, fill, fixed, iters=3000):
    """sub: HxWx3 float, fill: 메울 칸(bool), fixed: 값을 빌려 줄 칸(bool, Dirichlet).
    fill 도 fixed 도 아닌 칸은 경계에서 빠진다(Neumann — 윤곽선 쪽 색이 번져 들어오지 않게).
    네 이웃 평균을 되풀이(Jacobi)해 매끈하게 메운다."""
    H, W = fill.shape
    val = sub.copy()
    use = (fill | fixed).astype(np.float32)
    # 처음값: fixed 칸 평균
    init = sub[fixed].mean(axis=0)
    val[fill] = init
    for _ in range(iters):
        acc = np.zeros_like(val)
        cnt = np.zeros((H, W), np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            sh_v = np.roll(np.roll(val, dy, 0), dx, 1)
            sh_u = np.roll(np.roll(use, dy, 0), dx, 1)
            acc += sh_v * sh_u[..., None]
            cnt += sh_u
        new = np.where((cnt > 0)[..., None], acc / np.maximum(cnt, 1)[..., None], val)
        val[fill] = new[fill]
    return val


# ---------------------------------------------------------------- 1) 앞 덩치 도장 지우기
def fix1_erase_front_stamp(img):
    out = img.copy()
    cx, cy = 150.0, 744.0                 # 붉은 픽셀 테두리 상자(109..191, 702..786)의 가운데
    R_FILL = 49.0                          # 붉은 고리(r<=41.5) + 둘레의 분홍 번짐(r<=48) 까지
    x0, y0, x1, y1 = 80, 675, 225, 815
    sub = img[y0:y1, x0:x1].copy()
    lum = lum_of(sub)
    reddish = (sub[..., 0] - sub[..., 1]) > 80      # 도장 빨강은 「검은 심」이 아니다
    dark = ((lum < 120) & ~reddish).astype(np.uint8)  # 어깨 윤곽선 · 목걸이 줄의 검은 심
    dist = cv2.distanceTransform(1 - dark, cv2.DIST_L2, 5)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    r = np.hypot(xx - cx, yy - cy)
    line_zone = dist <= 3.0                         # 윤곽선과 그 가장자리 3px — 손대지 않는다
    fill = (r <= R_FILL) & ~line_zone
    skin = np.array([243.0, 185.0, 148.0])
    skinlike = np.abs(sub - skin).sum(axis=2) < 30
    fixed = (~fill) & (~line_zone) & skinlike & (r <= R_FILL + 6)
    val = laplace_fill(sub, fill, fixed)
    sub[fill] = val[fill]
    out[y0:y1, x0:x1] = sub
    return out


# ---------------------------------------------------------------- 2) 뒤 덩치 도장 또렷하게
OLD_CX, OLD_CY = 182.5, 372.5        # 흐린 옛 자국(x 171..195 · y 359..386)의 가운데
NEW_CX, NEW_CY = 189.0, 375.5        # 옛 자국을 지운 어깨에서 윤곽선(lum<120)과 가장 멀리 떨어진 점 — 그 거리 18.85
NEW_R = 16.0                         # 윤곽선 가장자리와 2px 남짓 띄운다 (20~24 는 어깨 밖으로 나간다)
RING_IN = 0.783                      # 앞 도장 비율: 고리 안쪽 32.5/41.5
DOT_R = 0.542                        # 앞 도장 비율: 가운데 점 22.5/41.5


def stamp_alpha(H, W, x0, y0, cx, cy, R, ss=8):
    """겹동그라미(바깥 고리 + 가운데 점)의 덮임 비율 — ss×ss 로 촘촘히 재서 평균(안티에일리어싱)."""
    off = (np.arange(ss) + 0.5) / ss - 0.5
    ys = (y0 + np.arange(H))[:, None] + off[None, :]
    xs = (x0 + np.arange(W))[:, None] + off[None, :]
    Y = ys.reshape(-1)[:, None]
    X = xs.reshape(-1)[None, :]
    r = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    ink = ((r <= R) & (r >= RING_IN * R)) | (r <= DOT_R * R)
    return ink.reshape(H, ss, W, ss).mean(axis=(1, 3)).astype(np.float32)


def fix2_back_stamp(img):
    out = img.copy()
    x0, y0, x1, y1 = 150, 340, 222, 408
    sub = img[y0:y1, x0:x1].copy()
    lum = lum_of(sub)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    r_old = np.hypot(xx - OLD_CX, yy - OLD_CY)
    core = lum < 60                                   # 윤곽선의 검은 심(옛 자국의 진한 빨강은 lum>=74 라 안 걸린다)
    d = cv2.distanceTransform((~core).astype(np.uint8), cv2.DIST_L2, 5)
    # 어깨 쪽만: 원 안에서 심으로 갈린 조각 가운데 옛 자국 가운데를 품은 것
    K = r_old <= 18.0
    n, lab = cv2.connectedComponents((K & ~core).astype(np.uint8), connectivity=4)
    shoulder = lab == lab[int(OLD_CY) - y0, int(OLD_CX) - x0]
    mod = shoulder & (r_old <= 16.0)                  # 옛 자국 + 번짐(r<=15.5)
    aa = mod & (d <= 3.0)                             # 윤곽선 안쪽 가장자리
    inner = mod & ~aa

    # (가) 윤곽선 안쪽 가장자리의 색 — 같은 윤곽선의 깨끗한 곳에서 거리별로 잰 값
    R_, G_, B_ = sub[..., 0], sub[..., 1], sub[..., 2]
    warm = (R_ - B_) > 30                              # 살 쪽(벽 쪽 가장자리는 잿빛)
    clean = warm & (r_old > 19.0) & (d <= 6.0) & (xx < 200) & ~core
    prof_d, prof_c = [], []
    for lo in np.arange(0.75, 6.0, 0.5):
        m = clean & (d >= lo) & (d < lo + 0.5)
        if m.sum() >= 5:
            prof_d.append(lo + 0.25)
            prof_c.append(np.median(sub[m], axis=0))
    prof_d = np.array(prof_d)
    prof_c = np.array(prof_c)
    for c in range(3):
        sub[..., c] = np.where(aa, np.interp(d, prof_d, prof_c[:, c]), sub[..., c])

    # (가') 옛 자국이 스며든 윤곽선 심 픽셀의 붉은 기만 뺀다(밝기는 그대로 · 같은 윤곽선의 심 빛깔 비율로)
    red_core = core & (r_old <= 16.0) & ((sub[..., 0] - sub[..., 1]) > 30)
    L = lum_of(sub)
    for c, k in enumerate((1.2, 0.95, 0.85)):
        sub[..., c] = np.where(red_core, np.clip(L * k, 0, 255), sub[..., c])

    # (나) 안쪽 — 둘레의 살빛으로 매끈하게
    skin = np.array([240.0, 183.0, 144.0])
    skinlike = (np.abs(sub - skin).sum(axis=2) < 40) & ((R_ - G_) < 70)
    fixed = shoulder & ~mod & (d > 3.0) & skinlike
    fixed |= aa                                        # 방금 칠한 가장자리도 경계값으로
    val = laplace_fill(sub, inner, fixed)
    sub[inner] = val[inner]

    # (다) 새 도장 — 앞 도장과 같은 비율 · 같은 빨강
    al = stamp_alpha(y1 - y0, x1 - x0, x0, y0, NEW_CX, NEW_CY, NEW_R)[..., None]
    sub = al * STAMP_RED + (1 - al) * sub
    out[y0:y1, x0:x1] = sub
    return out


# ---------------------------------------------------------------- 3) 레버의 음반을 얇은 한 장으로
# 앞면 타원(검은 테의 심 선): 원본에서 심 213점에 맞춘 값(잔차 대부분 1px 안)
F_CX, F_CY, F_A, F_B = 1837.82, 501.70, 28.82, 61.14
# 옛 뒷면(겹선 띠의 바깥 윤곽) = 앞면 타원을 (15.75, -1.90) 옮긴 것 (맞춤 오차 0.24px)
O_DX, O_DY = 15.75, -1.90
# 새 뒷면: 같은 방향으로 3px 만 — 앞면 테와 겹쳐 오른쪽이 조금 굵은 테 하나로 보인다(겹선 없음)
S_NEW = 3.0
N_DX, N_DY = S_NEW, O_DY * S_NEW / O_DX
ROD_T = (500.10, 0.2684)        # 레버 위 윤곽선 심  y = 500.10 + 0.2684 (x - 1870)
ROD_B = (516.05, 0.2559)        # 레버 아래 윤곽선 심 y = 516.05 + 0.2559 (x - 1870)
ROD_SRC_X = 1891                # 레버 단면을 빌려 올 깨끗한 세로줄(1890~1892 · 음반과 자물쇠 사이)
DOOR_ROW_TOP, DOOR_ROW_BOT = 420, 580   # 문 세로 이음선 단면을 빌려 올 가로줄(음반 위 · 아래)
BLACK = np.array([0.0, 0.0, 0.0])       # 옛 바깥 윤곽선 심의 색(중앙값)
BAND = np.array([38.0, 37.0, 39.0])     # 옛 옆면 띠의 바탕색(중앙값)


def ellipse_sdist(H, W, x0, y0, cx, cy, a, b, ss):
    """축이 곧은 타원(심 선)까지의 부호 있는 거리(px · 안쪽 음수) — ss 배 촘촘한 격자에서 잰다."""
    t = np.linspace(0, 2 * np.pi, 8000, endpoint=False)
    px = cx + a * np.cos(t)
    py = cy + b * np.sin(t)
    SHB = 4
    J = ((px - x0 + 0.5) * ss - 0.5) * (1 << SHB)
    I = ((py - y0 + 0.5) * ss - 0.5) * (1 << SHB)
    pts = np.stack([J, I], 1).round().astype(np.int32).reshape(-1, 1, 2)
    canvas = np.full((H * ss, W * ss), 255, np.uint8)
    cv2.polylines(canvas, [pts], True, 0, 1, cv2.LINE_8, SHB)
    dist = cv2.distanceTransform(canvas, cv2.DIST_L2, cv2.DIST_MASK_PRECISE) / ss
    jj = (np.arange(W * ss) + 0.5) / ss - 0.5 + x0
    ii = (np.arange(H * ss) + 0.5) / ss - 0.5 + y0
    X, Y = np.meshgrid(jj, ii)
    rho = np.sqrt(((X - cx) / a) ** 2 + ((Y - cy) / b) ** 2)
    return np.where(rho < 1, -dist, dist).astype(np.float32)


def fix3_thin_record(img):
    out = img.copy()
    x0, y0, x1, y1 = 1800, 426, 1898, 578
    H, W = y1 - y0, x1 - x0
    orig = img[y0:y1, x0:x1].copy()
    SS = 8
    sd_f = ellipse_sdist(H, W, x0, y0, F_CX, F_CY, F_A, F_B, SS)
    sd_n = ellipse_sdist(H, W, x0, y0, F_CX + N_DX, F_CY + N_DY, F_A, F_B, SS)
    sd_o = ellipse_sdist(H, W, x0, y0, F_CX + O_DX, F_CY + O_DY, F_A, F_B, SS)

    def down(A):
        return A.reshape(H, SS, W, SS).mean(axis=(1, 3))

    d_f, d_n, d_o = down(sd_f), down(sd_n), down(sd_o)
    ramp = lambda s: np.clip((3.2 - np.abs(s)) / 2.2, 0, 1)      # 윤곽선 짙기: 심±1px 까맣고 ±3.2px 에서 0
    a_line = down(np.maximum(ramp(sd_n), ramp(sd_f) * (sd_f >= 0)))  # 새 뒷면 테 ∪ 앞면 테 바깥쪽
    a_fill = down((sd_n < 0).astype(np.float32))                 # 새 뒷면 안쪽(얇은 옆면)

    # 바뀌는 자리 Z: 옛 띠·바깥 윤곽(+그 둘레 물결 번짐 5px) 가운데 새 음반 밖이 된 곳 + 새 테 자리
    Z1 = (d_o <= 3.5) & (d_n > 3.2) & (d_f > 3.2)
    Z1d = cv2.dilate(Z1.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))) > 0
    Z2 = (d_n <= 3.5) & (d_o <= 3.5)
    Z = (Z1d | Z2) & (d_f > 1.0)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    Z &= ~((xx >= 1886) & (yy >= 540))                # 자물쇠 몸통 테두리(밝은 테 x>=1887)는 건드리지 않는다
    Z &= ~((xx >= 1863) & (xx <= 1881) & (yy <= 438))  # 문 리벳 하나도 그대로

    # ---- 레버: 위·아래 심 직선(맞춘 값) — 단면은 자물쇠 앞 깨끗한 세 줄(1890~1892)을 기울기 따라 옮겨 평균
    def y_top(x):
        return ROD_T[0] + ROD_T[1] * (x - 1870)

    def y_bot(x):
        return ROD_B[0] + ROD_B[1] * (x - 1870)

    def y_mid(x):
        return 0.5 * (y_top(x) + y_bot(x))

    cols = [ROD_SRC_X - 1, ROD_SRC_X, ROD_SRC_X + 1]

    def rod_profile(x, yv):
        acc = 0
        for xs_ in cols:
            src = img[:, xs_].astype(np.float32)
            yf = yv + (y_mid(xs_) - y_mid(x))
            yi = np.floor(yf).astype(int)
            f = (yf - yi)[..., None]
            acc = acc + src[yi] * (1 - f) + src[yi + 1] * f
        return acc / len(cols)

    # 옮겨 온 단면을 쓰는 가로 범위: 1873~1886 은 온전히, 1870~1873 · 1886~1889 는 원본과 섞는다
    def w_copy(x):
        if x <= 1870 or x >= 1889:
            return 0.0
        if x < 1873:
            return (x - 1870) / 3.0
        if x > 1886:
            return (1889 - x) / 3.0
        return 1.0

    R_layer = orig.copy()                      # 레버 층(색): 몸통은 원본과 옮긴 단면을 가로로 섞음
    COPY = orig.copy()                         # 옮겨 온 단면 그대로(레버 둘레 문 바탕 · 밝은 테 포함)
    R_alpha = np.zeros((H, W), np.float32)     # 레버 실루엣(윤곽 심 포함)
    rod_band = np.zeros((H, W), bool)          # 레버 둘레 ±7.5px 띠
    for x in range(1862, 1896):
        j = x - x0
        cy_ = yy[:, j].astype(np.float32)
        band = (cy_ >= y_top(x) - 7.5) & (cy_ <= y_bot(x) + 7.5)
        rod_band[:, j] = band
        if x <= 1888:
            COPY[band, j] = rod_profile(x, cy_[band])
        wc = w_copy(x)
        R_layer[band, j] = wc * COPY[band, j] + (1 - wc) * orig[band, j]
        # 실루엣: 위 심 위 1px ~ 아래 심 아래 1px 까지 1, 바깥 1.5px 에 걸쳐 0 으로
        up = np.clip((cy_ - (y_top(x) - 2.5)) / 1.5, 0, 1)
        dn = np.clip(((y_bot(x) + 2.5) - cy_) / 1.5, 0, 1)
        R_alpha[:, j] = np.minimum(up, dn)

    # ---- 바탕 B: (1) 평평한 문 — 둘레 문 픽셀에서 매끈하게 이어 메움
    door = np.array([144.7, 158.8, 159.0])
    Lo = lum_of(orig)
    dark = (Lo < 110).astype(np.uint8)
    dd = cv2.distanceTransform(1 - dark, cv2.DIST_L2, 5)
    flat_door = (np.abs(Lo - 152) < 12) & ((orig[..., 2] - orig[..., 0]) > 4) & ((orig[..., 2] - orig[..., 0]) < 26) & (dd >= 2)
    ring = (cv2.dilate(Z.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & ~Z
    fixed = ring & flat_door
    Bimg = orig.copy()
    Bimg[Z] = door
    Bimg = laplace_fill(Bimg, Z, fixed, iters=2500)
    # (2) 문 세로 이음선 두 줄 — 음반 위·아래의 같은 세로줄 단면을 이어 그린다(평평한 문에서 벗어난 만큼만 더함)
    top_ref = img[DOOR_ROW_TOP, 1866:1891].mean(axis=0)
    bot_ref = img[DOOR_ROW_BOT, 1862:1879].mean(axis=0)
    for x in range(1834, 1867):
        j = x - x0
        det_t = img[DOOR_ROW_TOP, x] - top_ref
        det_b = img[DOOR_ROW_BOT, x] - bot_ref
        up = yy[:, j] < 500
        Bimg[up, j] += det_t
        Bimg[~up, j] += det_b
    # (3) 레버 둘레 띠(옮겨 온 단면 — 레버 위아래의 문 바탕 · 밝은 테까지, x>=1889 는 원본 그대로):
    #     띠 끝 2px 은 평평한 문과 섞는다
    for x in range(1866, 1896):
        j = x - x0
        cy_ = yy[:, j].astype(np.float32)
        b = rod_band[:, j]
        wv = np.minimum(np.clip((cy_ - (y_top(x) - 7.5)) / 2.0, 0, 1),
                        np.clip(((y_bot(x) + 7.5) - cy_) / 2.0, 0, 1))[b][:, None]
        Bimg[b, j] = wv * COPY[b, j] + (1 - wv) * Bimg[b, j]

    # ---- 새 음반 가장자리: 얇은 옆면(띠 색) 위에 검은 테
    N = Bimg * (1 - a_fill[..., None]) + BAND * a_fill[..., None]
    N = N * (1 - a_line[..., None]) + BLACK * a_line[..., None]
    # 레버는 음반 옆면 앞에 있다
    ra = R_alpha[..., None]
    N = ra * R_layer + (1 - ra) * N
    # 앞면은 원본 그대로(테 심 바깥 1px 부터 섞음)
    w_face = np.clip(2.0 - d_f, 0, 1)[..., None]
    N = w_face * orig + (1 - w_face) * N
    # Z 바깥은 원본, Z 가장자리 1.5px 은 안쪽으로 섞는다
    dz = cv2.distanceTransform(Z.astype(np.uint8), cv2.DIST_L2, 5)
    mz = np.clip(dz / 1.5, 0, 1)[..., None]
    res = orig * (1 - mz) + N * mz
    out[y0:y1, x0:x1] = res
    return out


def changed_bbox(a, b, box=None):
    d = np.abs(a.astype(int) - b.astype(int)).sum(axis=2) > 0
    if box is not None:
        m = np.zeros_like(d)
        x0, y0, x1, y1 = box
        m[y0:y1, x0:x1] = True
        d &= m
    ys, xs = np.nonzero(d)
    if len(xs) == 0:
        return None, 0
    return [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)], int(len(xs))


def main():
    src = Image.open(SRC).convert('RGB')
    assert src.size == (2048, 1144)
    orig = np.asarray(src).astype(np.float32)
    img = orig.copy()
    steps = sys.argv[1] if len(sys.argv) > 1 else '123'
    if '1' in steps:
        img = fix1_erase_front_stamp(img)
    if '2' in steps and 'fix2_back_stamp' in globals():
        img = globals()['fix2_back_stamp'](img)
    if '3' in steps and 'fix3_thin_record' in globals():
        img = globals()['fix3_thin_record'](img)
    res = np.clip(np.rint(img), 0, 255).astype(np.uint8)
    Image.fromarray(res, 'RGB').save(OUT)
    o8 = np.asarray(src)
    print('all   ', changed_bbox(o8, res))
    print('item1 ', changed_bbox(o8, res, (0, 600, 400, 900)))
    print('item2 ', changed_bbox(o8, res, (100, 300, 300, 450)))
    print('item3 ', changed_bbox(o8, res, (1750, 400, 1950, 620)))


if __name__ == '__main__':
    main()

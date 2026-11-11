# -*- coding: utf-8 -*-
"""L19e 그림 고침 — 원본(L19e/r1/final_v1.png, 읽기만)에서 picfix/L19e/final_new.png 를 다시 만든다.

  항목 1 (정거장 4) : 미토콘드리아 겉껍질의 둥근 구멍 둘 → 셋.
                      위 오른쪽 구멍(A)을 둥근 마스크로 오려 정수 칸만큼 옮겨(다시 표본 추출 없음)
                      A 왼쪽 · 가운데 구멍(B) 위의 빈 껍질에 붙인다. 절단창과 겹치지 않는다.
  항목 2 (정거장 11): 아스파라거스와 끊긴 자리 사이의 구슬 세 알 · 끊긴 끝 · 닫힌 채 매달린 캐스터네츠
                      (끈 · 뒷짝 · 그림자 포함)를 지우고 벽을 이어 깐다(곁의 깨끗한 벽 조각을 16px 격자에 맞춰 깔아
                      벽의 옅은 결까지 잇는다). 아스파라거스에서 나온 끈을 원래 끈 단면 그대로 오른쪽으로 짧게 늘이고,
                      바닥의 벌어진 캐스터네츠(정거장 6 과 같은 물건)를 오려 25° 돌리고 0.8 배로 줄여,
                      벌어진 입이 아스파라거스 바로 오른쪽에서 그 끈 끝을 물게 붙인다. 아스파라거스는 손대지 않는다.
                      (끈은 원래 끈처럼 위 · 아래 옅은 번짐 테까지, 캐스터네츠 바깥에는 곁 구슬에서 잰 만큼의
                      옅은 밝은 테를 벽 픽셀에만 얹어 이 그림의 가장자리 결에 맞춘다.)
쓰는 것: PIL · numpy · cv2 뿐.   실행: python3 fix.py
"""
import os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = SP + '/L19e/r1/final_v1.png'
OUT = SP + '/picfix/L19e'

WALL = np.array([150, 101, 65], np.float32)     # 정거장 11 벽 바탕(가장 흔한 값)
INK = np.array([16, 8, 5], np.float32)          # 윤곽선 색(곁에서 잰 가장 어두운 값 근처)


def lum(a):
    a = a.astype(np.float32)
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def over(dst, rgb, alpha, x0, y0):
    """dst(float32 HxWx3)의 [y0:,x0:] 위에 rgb 를 알파 alpha 로 얹는다."""
    h, w = alpha.shape
    roi = dst[y0:y0 + h, x0:x0 + w]
    a = alpha[..., None]
    roi[:] = rgb * a + roi * (1.0 - a)


# =============================================================== 항목 1 : 셋째 구멍
HOLE_SRC_C = (1505.8, 573.0)     # 위 오른쪽 구멍 A 의 가운데(검은 테 바깥선에 맞춘 원의 중심)
HOLE_SHIFT = (-51, 4)            # 정수 칸 이동 → 새 구멍 가운데 ≈ (1454.8, 577.0)
HOLE_R_IN, HOLE_R_OUT = 22.5, 25.0   # 검은 테(r≈18.5) + 바깥 밝은 테(r 20~24)까지 품고 그 밖 2.5px 에서 스며들게


def add_third_hole(canvas, im):
    cx, cy = HOLE_SRC_C
    R = int(np.ceil(HOLE_R_OUT)) + 1
    x0, y0 = int(np.floor(cx)) - R, int(np.floor(cy)) - R
    x1, y1 = int(np.ceil(cx)) + R + 1, int(np.ceil(cy)) + R + 1
    reg = im[y0:y1, x0:x1].astype(np.float32)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.hypot(xx - cx, yy - cy)
    alpha = np.clip((HOLE_R_OUT - d) / (HOLE_R_OUT - HOLE_R_IN), 0, 1)
    dx, dy = HOLE_SHIFT
    over(canvas, reg, alpha, x0 + dx, y0 + dy)


# =============================================================== 항목 2-a : 지우기
def _flood_keep(crit, seeds, box):
    """box 안에서 crit 픽셀을 따라 seeds 에 이어진 덩어리(속까지 메움)"""
    x0, y0, x1, y1 = box
    c = crit[y0:y1, x0:x1].astype(np.uint8)
    n, lab = cv2.connectedComponents(c, connectivity=8)
    sub = np.zeros(c.shape, np.uint8)
    for (sx, sy) in seeds:
        l = lab[sy - y0, sx - x0]
        assert l > 0, ('seed off', sx, sy)
        sub |= (lab == l).astype(np.uint8)
    ff = np.pad(1 - sub, 1, constant_values=1).astype(np.uint8)
    msk = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, msk, (0, 0), 2)
    out = np.zeros(crit.shape, bool)
    out[y0:y1, x0:x1] = (ff[1:-1, 1:-1] != 2)
    return out


# 아스파라거스 오른쪽 윤곽(잎 비늘 포함)의 바깥 끝 — 줄마다 원본을 재서 잡았다
_ASP_XCUT = {372: 1787, 373: 1787, 374: 1787, 375: 1788, 376: 1789, 377: 1789, 378: 1789, 379: 1790, 380: 1790}


def _asp_xcut(H, W):
    ys = np.arange(H)
    xc = np.where(ys <= 371, 1783, 1792)
    for y, x in _ASP_XCUT.items():
        xc[y] = x
    return xc[:, None]


def keep_masks(im, split=False):
    """지우면 안 되는 것: 아스파라거스 · 위 오른쪽 외톨이 구슬과 그 끈 · 세로로 드리운 구슬 줄(윗끈 포함)"""
    L = lum(im)
    f = im.astype(np.float32)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    dark = L < 75
    green = (G > R + 8) & (G > B + 40)
    bright = L > 138
    H, W = L.shape
    xs = np.arange(W)[None, :]
    asp = _flood_keep((green | dark) & (xs <= _asp_xcut(H, W)), [(1770, 340), (1785, 390)], (1735, 270, 1815, 480))
    tr = _flood_keep(dark | bright, [(1935, 333), (1916, 340)], (1905, 312, 1965, 366))
    vc = _flood_keep(dark | bright, [(1938, 425), (1930, 401)], (1912, 388, 1975, 760))
    if split:
        return asp, tr, vc
    return asp | tr | vc


def erase_mask(im, with_protect=False):
    H, W = im.shape[:2]
    P = np.zeros((H, W), np.uint8)
    pts = np.array([(1783, 333), (1907, 333), (1907, 366), (1934, 366), (1934, 512),
                    (1836, 512), (1814, 498), (1808, 470), (1808, 400), (1794, 386), (1786, 386), (1786, 372), (1783, 372)], np.int32)
    cv2.fillPoly(P, [pts], 1)
    asp, tr, vc = keep_masks(im, split=True)
    K = asp | tr | vc
    cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    Kd = cv2.dilate(K.astype(np.uint8), cross) > 0                           # 남길 것의 윤곽 바깥 1px(번짐)까지 지킨다
    # 끈보다 위(y<=362)에서는 구슬 1 이 멀어 아스파라거스의 밝은 번짐 테(바깥 2~3px)까지 그대로 둔다
    disk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    asp3 = cv2.dilate(asp.astype(np.uint8), disk) > 0
    asp3[363:, :] = False
    Kd |= asp3
    d = np.abs(im.astype(np.float32) - WALL).max(2)
    D = cv2.dilate((d > 4).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0  # 벽이 아닌 것과 그 번짐만 바꾼다
    E = (P > 0) & D & ~Kd
    if with_protect:
        return E, (asp, Kd)
    return E


# 벽 결 : 곁의 깨끗한 벽(구슬 위 · 96x32)을 16px 격자에 맞춰 바둑판으로 깐다
TILE = (1792, 288, 96, 32)


def wall_texture(im, H, W):
    tx, ty, tw, th = TILE
    tile = im[ty:ty + th, tx:tx + tw].astype(np.float32)
    ys = (np.arange(H) - ty) % th
    xs = (np.arange(W) - tx) % tw
    return tile[ys[:, None], xs[None, :]]


# =============================================================== 항목 2-b : 끈
STR_Y0 = 360                      # 끈 단면을 놓을 첫 줄(위 번짐 테 360~361 · 윤곽 363~365 · 속 366~369 · 윤곽 370~371)
STR_X0, STR_X1 = 1784, 1842       # 아스파라거스 윤곽 바로 다음부터 캐스터네츠 입속(가려지는 자리)까지
STR_CORE = (363, 372)             # 이 줄들은 아스파라거스 윤곽 바로 곁(1784)부터 그린다


def string_profile(im):
    """원본 끈 토막(x1785~1788)의 세로 단면 y360~371 그대로 + 그 밑 3줄(372~374)은
    같은 그림의 다른 끈(위 오른쪽 구슬에서 나간 끈 x1962)의 아래 가장자리(번짐 → 밝은 테 → 벽)를 따랐다."""
    top = im[360:372, 1785:1789].astype(np.float32).mean(1)                      # 360..371 (12줄)
    bot = np.array([[100, 76, 60], [150, 116, 92], [152, 110, 82]], np.float32)  # 372..374
    return np.vstack([top, bot])                                                   # 15 x 3


def draw_string(canvas, im, protect):
    """protect: 덮으면 안 되는 픽셀(아스파라거스와 그 번짐). 윤곽 · 속 줄은 아스파라거스 마스크만 피한다."""
    col = string_profile(im)
    n = len(col)
    w = STR_X1 - STR_X0
    rgb = np.repeat(col[:, None, :], w, axis=1)
    asp, Kd = protect
    ys = np.arange(STR_Y0, STR_Y0 + n)
    a = np.ones((n, w), np.float32)
    for i, y in enumerate(ys):
        m = asp[y, STR_X0:STR_X1] if STR_CORE[0] <= y < STR_CORE[1] else Kd[y, STR_X0:STR_X1]
        a[i, m] = 0.0
    over(canvas, rgb, a, STR_X0, STR_Y0)


# =============================================================== 항목 2-c : 벌어진 캐스터네츠
CLAM_BOX = (885, 915, 1040, 1075)                 # 바닥 왼쪽의 벌어진 캐스터네츠
CLAM_FLOOR_SEEDS = [(1025, 930), (960, 1070)]
CLAM_INSIDE_SEED = (960, 1000)
CLAM_APEX_SRC = (944.0, 992.0)                    # 뚜껑 가장자리와 접시 테가 만나는 입의 안쪽 꼭짓점
CLAM_ROT_DEG = 25.0                               # 화면에서 반시계 + : 입(이등분선)이 정확히 왼쪽을 보게
CLAM_SCALE = 0.8
CLAM_APEX_DST = (1828.0, 367.0)                   # 끈 가운데 줄 높이 · 아스파라거스 바로 오른쪽
CLAM_EDGE_RAMP = 2.0                              # 바깥 번짐 폭(작을수록 넓다) — 곁 구슬의 2px 번짐에 맞춤
CLAM_GLOW = ((3.0, 11.0, 16.0), 1.6, 0.9)         # 밝은 테: 더할 값(RGB) · 윤곽 바깥 거리(px) · 폭(px)


def clam_sprite(im, thr=90):
    x0, y0, x1, y1 = CLAM_BOX
    reg = im[y0:y1, x0:x1].astype(np.float32)
    dark = (lum(reg) < thr).astype(np.uint8)
    ff = (1 - dark).copy()
    msk = np.zeros((dark.shape[0] + 2, dark.shape[1] + 2), np.uint8)
    for sx, sy in CLAM_FLOOR_SEEDS:
        cv2.floodFill(ff, msk, (sx - x0, sy - y0), 2)
    sil = (ff != 2).astype(np.uint8)
    n, lab = cv2.connectedComponents(sil, connectivity=4)
    sil = (lab == lab[CLAM_INSIDE_SEED[1] - y0, CLAM_INSIDE_SEED[0] - x0]).astype(np.uint8)
    # 바닥색이 섞였을 수 있는 맨 바깥 1px 은 윤곽선 색 쪽으로 눌러 밝은 테를 막는다
    inner = cv2.erode(sil, np.ones((3, 3), np.uint8))
    ring = (sil == 1) & (inner == 0)
    rgb = reg.copy()
    rgb[ring] = np.minimum(rgb[ring], INK + 14)
    rgb[sil == 0] = INK
    return rgb, sil.astype(np.float32), (x0, y0)


def clam_affine():
    """원본 좌표 → 목적 좌표 : 꼭짓점을 축으로 반시계 θ · s 배"""
    th = np.deg2rad(CLAM_ROT_DEG)
    c, s_ = np.cos(th), np.sin(th)
    A = CLAM_SCALE * np.array([[c, s_], [-s_, c]], np.float64)
    t = np.array(CLAM_APEX_DST) - A @ np.array(CLAM_APEX_SRC)
    return A, t


def paste_clam(canvas, im, K=4):
    rgb, sil, (sx0, sy0) = clam_sprite(im)
    A, t = clam_affine()
    h, w = sil.shape
    corners = np.array([[sx0, sy0], [sx0 + w, sy0], [sx0, sy0 + h], [sx0 + w, sy0 + h]], np.float64)
    dc = corners @ A.T + t
    rx0, ry0 = int(np.floor(dc[:, 0].min())) - 2, int(np.floor(dc[:, 1].min())) - 2
    rx1, ry1 = int(np.ceil(dc[:, 0].max())) + 2, int(np.ceil(dc[:, 1].max())) + 2
    ow, oh = rx1 - rx0, ry1 - ry0
    # 조각 픽셀 (u,v) → 1배 목적 좌표 c = A(sx0+u, sy0+v) + t (픽셀 가운데 기준)
    # → 4배 캔버스 픽셀 X = K (c - rx0 + 0.5) - 0.5
    M = np.zeros((2, 3), np.float64)
    M[:, :2] = K * A
    M[:, 2] = K * (A @ np.array([sx0, sy0], np.float64) + t - np.array([rx0, ry0]) + 0.5) - 0.5
    big_rgb = cv2.warpAffine(rgb, M.astype(np.float32), (ow * K, oh * K), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=tuple(float(v) for v in INK))
    big_sil = cv2.warpAffine(sil, M.astype(np.float32), (ow * K, oh * K), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    big_sil = cv2.GaussianBlur(big_sil, (0, 0), K * 0.45)            # 계단진 실루엣 → 매끈한 바깥선
    big_a = np.clip((big_sil - 0.5) * CLAM_EDGE_RAMP + 0.5, 0, 1)
    a = np.clip(cv2.resize(big_a, (ow, oh), interpolation=cv2.INTER_AREA), 0, 1)
    srgb = np.clip(cv2.resize(big_rgb, (ow, oh), interpolation=cv2.INTER_AREA), 0, 255)
    over(canvas, srgb, a, rx0, ry0)
    if CLAM_GLOW is not None:
        # 이 그림의 물건들은 윤곽선 바깥 1~2px 에 옅게 밝은 테가 있다(곁 구슬 · 바닥의 원래 캐스터네츠에서 잼).
        # 붙인 캐스터네츠 바깥의 벽 픽셀에만 같은 세기로 얹는다.
        outside = (big_a < 0.5).astype(np.uint8)
        dist = cv2.distanceTransform(outside, cv2.DIST_L2, 5) / K       # 1배 픽셀 단위 거리
        peak, d0, w = CLAM_GLOW
        g_big = np.exp(-((dist - d0) / w) ** 2) * (outside > 0)
        g = cv2.resize(g_big.astype(np.float32), (ow, oh), interpolation=cv2.INTER_AREA)
        roi = canvas[ry0:ry1, rx0:rx1]
        wallish = (np.abs(roi - WALL).max(2) < 12).astype(np.float32)
        roi += (g * wallish)[..., None] * np.array(peak, np.float32)
    return (rx0, ry0, rx1, ry1), a


# =============================================================== 조립
def build(do1=True, do2=True):
    im = np.array(Image.open(SRC).convert('RGB'))
    canvas = im.astype(np.float32).copy()
    if do1:
        add_third_hole(canvas, im)
    if do2:
        E, protect = erase_mask(im, with_protect=True)
        tex = wall_texture(im, *im.shape[:2])
        canvas[E] = tex[E]
        draw_string(canvas, im, protect)  # 끈 먼저
        paste_clam(canvas, im)           # 그 위에 캐스터네츠(끈 끝이 입속으로 물려 가려진다)
    out = np.clip(np.rint(canvas), 0, 255).astype(np.uint8)
    return im, out


def diff_boxes(a, b, join=25):
    d = (a.astype(int) != b.astype(int)).any(2).astype(np.uint8)
    n, lab, st, ce = cv2.connectedComponentsWithStats(cv2.dilate(d, np.ones((join, join), np.uint8)), connectivity=8)
    boxes = []
    for i in range(1, n):
        ys, xs = np.nonzero((lab == i) & (d > 0))
        if len(xs):
            boxes.append((int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)))
    return boxes


def cmp_image(a, b, box, name, long_side=1400):
    ca = Image.fromarray(a).crop(box)
    cb = Image.fromarray(b).crop(box)
    gap, head = 12, 34
    z = min((long_side - gap) / 2.0 / ca.width, (long_side - head) / float(ca.height), 4.0)
    sz = (int(ca.width * z), int(ca.height * z))
    ca = ca.resize(sz, Image.LANCZOS)
    cb = cb.resize(sz, Image.LANCZOS)
    sheet = Image.new('RGB', (sz[0] * 2 + gap, sz[1] + head), (255, 255, 255))
    sheet.paste(ca, (0, head))
    sheet.paste(cb, (sz[0] + gap, head))
    dr = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    except Exception:
        f = ImageFont.load_default()
    dr.text((8, 5), 'BEFORE', fill=(0, 0, 0), font=f)
    dr.text((sz[0] + gap + 8, 5), 'AFTER', fill=(0, 0, 0), font=f)
    sheet.save(os.path.join(OUT, name))


if __name__ == '__main__':
    im, out = build()
    Image.fromarray(out, 'RGB').save(os.path.join(OUT, 'final_new.png'))
    cmp_image(im, out, (1370, 490, 1610, 710), 'cmp_1.png')
    cmp_image(im, out, (1700, 260, 2000, 540), 'cmp_2.png')
    print('diff boxes [x,y,w,h]:', diff_boxes(im, out))

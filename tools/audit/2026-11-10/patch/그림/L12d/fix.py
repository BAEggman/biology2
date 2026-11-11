# L12d 그림 고침 — 원본 final_v1.png 에서 final_new.png 를 다시 만든다 (PIL · numpy 만 사용).
#   1. 맨 오른쪽 벽에 기댄 판자 4 -> 5 : 맨 뒤 판자(D)를 옮겨 그려 D 뒤에 다섯째 판자(E)를 세운다(벽 그림자 포함).
#   2. 왼쪽 작업대 회색 벽돌 : 못 함 (note.md 참고) — 손대지 않는다.
#   3. 파란 공 곁 검은 줄표 둘을 지운다(벽 바탕 · 접시 안쪽 테 선 이어 그리기).
import sys
import numpy as np
from PIL import Image

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = SP + '/L12d/r1/final_v1.png'
OUT = SP + '/picfix/L12d/final_new.png'

src = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float64)
H, W, _ = src.shape
LUM = src.mean(2)


# ---------------------------------------------------------------- 공용
def cen_row(y, xa, xb, thr=110):
    seg = LUM[y, xa:xb]; w = (thr - seg).clip(0)
    return (np.arange(xa, xb) * w).sum() / w.sum() if w.sum() > 0 else None


def cen_col(x, ya, yb, thr=110):
    seg = LUM[ya:yb, x]; w = (thr - seg).clip(0)
    return (np.arange(ya, yb) * w).sum() / w.sum() if w.sum() > 0 else None


def track_row(y0, y1, xs, half=3):
    out = {}; xc = xs
    for y in range(y0, y1):
        c = cen_row(y, int(round(xc)) - half, int(round(xc)) + half + 1)
        if c is None: break
        out[y] = c; xc = c
    return out


def track_col(x0, x1, ys, half=3):
    out = {}; yc = ys
    for x in range(x0, x1):
        c = cen_col(x, int(round(yc)) - half, int(round(yc)) + half + 1)
        if c is None: break
        out[x] = c; yc = c
    return out


def linfit(d):
    k = np.array(sorted(d)); v = np.array([d[i] for i in k])
    b, a = np.polyfit(k, v, 1)
    return lambda t: a + b * np.asarray(t, dtype=np.float64)


def bilinear(img, xs, ys):
    xs = np.clip(xs, 0, img.shape[1] - 1.001); ys = np.clip(ys, 0, img.shape[0] - 1.001)
    x0 = np.floor(xs).astype(int); y0 = np.floor(ys).astype(int)
    fx = (xs - x0)[..., None]; fy = (ys - y0)[..., None]
    p00 = img[y0, x0]; p01 = img[y0, x0 + 1]; p10 = img[y0 + 1, x0]; p11 = img[y0 + 1, x0 + 1]
    return (p00 * (1 - fx) + p01 * fx) * (1 - fy) + (p10 * (1 - fx) + p11 * fx) * fy


# ---------------------------------------------------------------- 1. 다섯째 판자
def fix_planks(out):
    DX, DY = 35, 7          # E = D 를 오른쪽 35 · 위 7 로 옮긴 판자 (C->D 계단 간격과 같다)
    AX = 0.189              # D 판자 축의 기울기(아래로 1 내려가면 왼쪽으로 0.189)
    # 윤곽선 중심선 재기
    xD = linfit(track_row(504, 653, 1957.3))      # D 오른쪽 윤곽선
    xC = linfit(track_row(512, 653, 1923.1))      # C 오른쪽 윤곽선(원본에서 D 얼굴의 왼쪽 경계)
    xDf = linfit(track_row(504, 653, 1944.6))     # D 앞모서리 선
    dt = track_col(1906, 1957, 488.4)             # D 윗변
    dtx = np.array(sorted(dt)); dty = np.array([dt[x] for x in dtx])
    rm = track_col(1926, 2004, 653.6)             # 오른쪽 통 테두리 윗선
    rmx = np.array(sorted(rm)); rmy = np.array([rm[x] for x in rmx])
    yDt = lambda x: np.interp(x, dtx, dty)
    yR = lambda x: np.interp(x, rmx, rmy)

    x0, x1, y0, y1 = 1928, 2008, 468, 690
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float64)
    ys = yy + DY
    # 윗부분(D 윗변 위): 원본 C 윗변이 D 윗변에 꼭 겹치도록 E 윗변~D 윗변 사이 줄을 조금 늘이고 줄인다
    ct = track_col(1880, 1924, 498.0)             # C 윗변(원본)
    ctx = np.array(sorted(ct)); cty = np.array([ct[x] for x in ctx])
    xa = np.clip(xx, 1933, 1953)
    dlt = np.interp(xa - DX, ctx, cty) - yDt(xa) - DY        # 평행이동만 했을 때 어긋남(줄)
    yEt_a = np.interp(np.clip(xx, 1939, 1992) - DX, dtx, dty) - DY
    wv = np.clip((yy - yEt_a) / np.maximum(yDt(xa) - yEt_a, 1.0), 0, 1)
    ys = ys + np.where((xx <= 1958) & (yy < 501), dlt * wv, 0.0)

    # --- 원본(D)에서 가져올 자리: 오른쪽(앞모서리 · 옆면 · 윤곽선 · 벽 그림자)은 그대로 평행이동,
    #     얼굴(D 윤곽선 ~ E 앞모서리)은 C 윤곽선 ~ D 앞모서리를 줄 단위로 맞춰 늘이고 줄인다.
    L = xD(yy); Ls = xC(ys)
    R = xDf(ys) + DX - 3.0; Rs = xDf(ys) - 3.0
    xs_face = Ls + (xx - L) * (Rs - Ls) / (R - L)
    xs_tr = xx - DX
    xs = np.where(xx >= R, xs_tr, xs_face)
    # 윗부분(D 윗모서리 위)은 순수 평행이동, 499~512 줄에서 서서히 바꾼다
    w = np.clip((yy - 499) / 13.0, 0, 1)
    xs = xs_tr * (1 - w) + xs * w
    # 원본 통 테두리에 닿는 줄은 판자 축을 따라 위에서 가져온다
    cut = yR(np.clip(xs, rmx[0], rmx[-1])) - 10.0
    k = np.clip(ys - cut, 0, None)
    xs = xs + AX * k; ys = ys - k
    E = bilinear(src, xs, ys)

    # --- E 가 보이는 자리(앞의 D · 통 테두리는 지킨다)
    xDc = xD(yy); yDtc = yDt(xx); yRc = yR(xx)
    insideD = (yy >= yDtc) & (xx <= xDc)          # D 판자(앞) 자리 = 윗변 아래 · 오른쪽 윤곽선 왼쪽
    behindD = ~insideD
    aboveRim = yy < yRc
    region = behindD & aboveRim & (xx >= 1933)
    # 바깥 경계(맨 벽 안): E 오른쪽 그림자 + 여유, E 윗변 + 여유
    xE = xD(yy + DY) + DX
    yEt = np.interp(xx - DX, dtx, dty, left=dty[0], right=dty[-1]) - DY
    outer = np.clip((xE + 34 - xx) / 3.0, 0, 1) * np.clip((yy - (yEt - 9)) / 3.0, 0, 1)
    # 윗부분 오른쪽 위 구석(선반 그림자 쪽)은 건드리지 않는다
    outer *= (yy >= 470)

    # --- 앞의 윤곽선 가장자리 처리
    #  D 오른쪽 윤곽선 · D 윗변 : E 쪽에 옮겨 온 C 윤곽선이 같은 자리에 맞춰져 있으므로
    #     D 윤곽선 픽셀이 더 어두우면 그것을, 아니면 E 를 쓴다(어두운 쪽 고르기 = 원본 C|D 이음과 같은 모양).
    #  통 테두리 윗선 : E 쪽에는 선이 없으므로 테두리 선의 반투명 가장자리를 E 위에 다시 얹는다.
    K = np.array([6.0, 3.0, 2.0])
    dest = src[y0:y1, x0:x1]
    dl = LUM[y0:y1, x0:x1]
    El = E.mean(2)
    newE = E.copy()
    def bg_row(yv, xc):
        v = [LUM[int(yv), int(round(xc)) + d] for d in range(7, 11)]
        return float(np.median(v))
    def bg_col(xv, yc):
        v = [LUM[int(round(yc)) - d, int(xv)] for d in range(7, 11)]
        return float(np.median(v))
    hh, ww = dl.shape
    for j in range(hh):
        for i in range(ww):
            if not region[j, i]: continue
            X = x0 + i; Y = y0 + j
            if (Y >= 497 and 0 <= X - xD(Y) <= 6.5) or (X <= 1960 and 0 <= yDt(min(X, 1956)) - Y <= 6.5):
                if Y >= 497 and 0 <= X - xD(Y) <= 6.5: bg = bg_row(Y, xD(Y))
                else: bg = bg_col(X, yDt(min(X, 1956)))
                if dl[j, i] < El[j, i] and dl[j, i] < bg - 12:
                    newE[j, i] = dest[j, i]
            if 0 <= yR(X) - Y <= 6.5:
                bg = bg_col(X, yR(X))
                a = min(max((bg - dl[j, i] - 4) / (bg - 10), 0.0), 1.0)
                newE[j, i] = a * K + (1 - a) * newE[j, i]
    m = (region * outer)[..., None]
    blk = dest * (1 - m) + newE * m
    out[y0:y1, x0:x1] = blk
    return out


# ---------------------------------------------------------------- 3. 줄표 둘 지우기
def fix_dashes(out):
    # (가) 벽 위 줄표 x1158~1172 · y727~729 : 위아래 벽 줄로 채운다(벽은 한 빛깔)
    top = src[726, 1158:1173]; bot = src[730, 1158:1173]
    for k, y in enumerate(range(727, 730)):
        t = (k + 1) / 4.0
        out[y, 1158:1173] = top * (1 - t) + bot * t
    # (나) 접시 위 줄표 x1158~1172 · y763~765 : 접시 안쪽 테 선이 지나는 자리
    #      양옆 기준 열(1157 · 1173)의 세로 단면을 선 중심에 맞춰 섞어 이어 그린다
    xl, xr = 1157, 1173
    cl, cr = 766.2, 763.1             # 기준 열(1157 · 1173)의 선 중심 — 세로 밝기 단면에서 잰 값
    sl, sr = -0.25, -0.12             # 양끝 기울기
    span = xr - xl
    def yc(x):                         # 3차 에르미트 곡선
        t = (x - xl) / span
        h00 = 2*t**3 - 3*t**2 + 1; h10 = t**3 - 2*t**2 + t; h01 = -2*t**3 + 3*t**2; h11 = t**3 - t**2
        return h00*cl + h10*span*sl + h01*cr + h11*span*sr
    for x in range(1158, 1173):
        t = (x - xl) / span
        for y in range(763, 766):
            d = y - yc(x)
            pl = bilinear(src, np.array([float(xl)]), np.array([cl + d]))[0]
            pr = bilinear(src, np.array([float(xr)]), np.array([cr + d]))[0]
            out[y, x] = pl * (1 - t) + pr * t
    return out


if __name__ == '__main__':
    out = src.copy()
    out = fix_planks(out)
    out = fix_dashes(out)
    res = np.clip(np.round(out), 0, 255).astype(np.uint8)
    Image.fromarray(res, 'RGB').save(OUT)
    diff = np.abs(res.astype(int) - np.asarray(Image.open(SRC).convert('RGB')).astype(int)).max(2) > 0
    ys_, xs_ = np.nonzero(diff)
    print('changed px', diff.sum())
    # 달라진 자리 덩어리별 테두리 상자
    from collections import deque
    lab = np.zeros(diff.shape, int); n = 0
    for (y, x) in zip(ys_, xs_):
        if lab[y, x]: continue
        n += 1; q = deque([(y, x)]); lab[y, x] = n; bx = [x, y, x, y]
        while q:
            cy, cx = q.popleft()
            for ddy in range(-4, 5):
                for ddx in range(-4, 5):
                    ny, nx = cy + ddy, cx + ddx
                    if 0 <= ny < H and 0 <= nx < W and diff[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n; q.append((ny, nx))
                        bx = [min(bx[0], nx), min(bx[1], ny), max(bx[2], nx), max(bx[3], ny)]
        print('box [x,y,w,h] =', [bx[0], bx[1], bx[2] - bx[0] + 1, bx[3] - bx[1] + 1])

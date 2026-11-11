# fix.py — L38a 벽의 오각판 둘 고치기 (PIL·numpy·cv2 만)
# 원본 SP/L38a/r1/final_v3.png 에서 SP/picfix/L38a/final_new.png 를 다시 만든다.
import numpy as np, cv2
from PIL import Image

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = SP + '/L38a/r1/final_v3.png'
OUTDIR = SP + '/picfix/L38a'

O = np.array(Image.open(SRC).convert('RGB')).astype(np.float32)   # 원본 (읽기만)
H, W = O.shape[:2]

def lum(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]

# ---------------------------------------------------------------- 판 면 채우기
def wall_ok(p):
    r, g, b = p
    Y = 0.299 * r + 0.587 * g + 0.114 * b
    return 140 < Y < 185 and (r - b) > 95 and abs(r - 211) < 22 and abs(b - 89) < 22

def _side(im, mask, x, y, step, ok, nav):
    vals = []
    yy = y
    while 0 <= yy < im.shape[0] and len(vals) < nav:
        if mask[yy, x]:
            break
        if not ok(im[yy, x]):
            break
        vals.append(im[yy, x])
        yy += step
    return np.mean(vals, 0) if vals else None

def vfill(im, mask, ok, nav=3, horiz_after=True):
    """세로로 이어 채우기(판 · 벽의 결이 세로라 결이 이어진다). 위·아래 한쪽만 있으면 그 값으로."""
    out = im.copy()
    left = np.zeros_like(mask)
    for x in np.where(mask.any(0))[0]:
        ys = np.where(mask[:, x])[0]
        runs = np.split(ys, np.where(np.diff(ys) > 1)[0] + 1)
        for r in runs:
            a, b = r[0], r[-1]
            A = _side(im, mask, x, a - 1, -1, ok, nav)
            B = _side(im, mask, x, b + 1, +1, ok, nav)
            if A is not None and B is not None:
                t = (np.arange(a, b + 1) - (a - 1)) / float(b + 1 - (a - 1))
                out[a:b + 1, x] = A[None] * (1 - t[:, None]) + B[None] * t[:, None]
            elif A is not None:
                out[a:b + 1, x] = A
            elif B is not None:
                out[a:b + 1, x] = B
            else:
                left[a:b + 1, x] = True
    if horiz_after and left.any():
        T = np.transpose(out, (1, 0, 2)).copy()
        Tm = left.T.copy()
        T2 = vfill(T, Tm, ok, nav, horiz_after=False)
        out = np.transpose(T2, (1, 0, 2)).copy()
    return out

def circle_mask(cx, cy, r):
    yy, xx = np.mgrid[0:H, 0:W]
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r

def rect_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), bool); m[y0:y1 + 1, x0:x1 + 1] = True; return m

def not_face_mask(im, region):
    """region 안에서 판 면 색이 아닌 픽셀."""
    F = np.array([245, 210, 150], np.float32)
    d = np.abs(im - F).max(2)
    return region & (d > 16)

def dil(m, r):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    return cv2.dilate(m.astype(np.uint8), k) > 0

def fill_holes(m):
    m8 = m.astype(np.uint8)
    cnts, _ = cv2.findContours(m8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = np.zeros_like(m8)
    cv2.drawContours(out, cnts, -1, 1, -1)
    return out > 0

def face_valid_map(im):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    Y = lum(im)
    return (Y > 178) & ((r - b) > 70) & (b < 160) & ((r - g) < 55)

def grain_valid_map(im):
    """판 면 + 판의 세로 결(조금 어두운 줄)까지. 검은 선 · 흰 테 · 쇠 · 빨강은 뺀다."""
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    Y = lum(im)
    return (Y > 150) & ((r - b) > 62) & (b < 160) & ((r - g) < 60)

def harmonic_fill(im, mask, valid, iters=2500):
    """mask 픽셀을 둘레의 valid 픽셀에서 매끈하게 잇는다(라플라스). valid 아닌 이웃은 빼고 평균(=노이만)."""
    ys, xs = np.where(mask)
    y0, y1 = max(ys.min() - 2, 0), min(ys.max() + 3, H)
    x0, x1 = max(xs.min() - 2, 0), min(xs.max() + 3, W)
    sub = im[y0:y1, x0:x1].copy()
    M = mask[y0:y1, x0:x1]
    V = valid[y0:y1, x0:x1] & ~M
    Wt = (M | V).astype(np.float32)
    ring = dil(M, 1) & V
    sub[M] = sub[ring].mean(0)
    for _ in range(iters):
        P = np.pad(sub * Wt[..., None], ((1, 1), (1, 1), (0, 0)))
        Q = np.pad(Wt, 1)
        num = P[:-2, 1:-1] + P[2:, 1:-1] + P[1:-1, :-2] + P[1:-1, 2:]
        den = Q[:-2, 1:-1] + Q[2:, 1:-1] + Q[1:-1, :-2] + Q[1:-1, 2:]
        new = num / np.maximum(den, 1e-6)[..., None]
        sub[M] = new[M]
    out = im.copy(); out[y0:y1, x0:x1] = sub
    return out

def vgrain_fill(im, mask, valid, nav=4, skip=2):
    """세로 결 잇기: 칸마다 위 · 아래의 깨끗한 판 면(각 nav px 평균)을 곧게 잇는다.
    끝 바로 곁의 흰 테는 skip px 까지 건너뛴다. 한쪽이 막혔으면 다른 쪽 값으로,
    양쪽 다 막힌 칸은 마지막에 라플라스로 잇는다. 끝값은 이웃 칸과 1:2:1 로 고른다."""
    out = im.copy()
    runs = []
    def side(x, y, step):
        k = 0
        while 0 <= y < H and k < skip and not mask[y, x] and not valid[y, x]:
            y += step; k += 1
        v = []
        while 0 <= y < H and len(v) < nav and not mask[y, x] and valid[y, x]:
            v.append(im[y, x]); y += step
        return np.mean(v, 0) if len(v) >= 2 else None
    for x in np.where(mask.any(0))[0]:
        ys = np.where(mask[:, x])[0]
        for r in np.split(ys, np.where(np.diff(ys) > 1)[0] + 1):
            runs.append([x, r[0], r[-1], side(x, r[0] - 1, -1), side(x, r[-1] + 1, 1)])
    for key, yi in ((3, 1), (4, 2)):
        table = {(r[0], r[yi]): r[key] for r in runs if r[key] is not None}
        sm = []
        for r in runs:
            if r[key] is None:
                sm.append(None); continue
            acc = 2 * r[key]; n = 2
            for dx in (-1, 1):
                for dy in (0, -1, 1, -2, 2):
                    q = table.get((r[0] + dx, r[yi] + dy))
                    if q is not None:
                        acc = acc + q; n += 1; break
            sm.append(acc / n)
        for r, v in zip(runs, sm):
            r[key] = v
    left = np.zeros_like(mask)
    for x, a, b, A, B in runs:
        if A is None and B is None:
            left[a:b + 1, x] = True; continue
        if A is None: A = B
        if B is None: B = A
        t = (np.arange(a, b + 1) - (a - 1)) / float(b + 1 - (a - 1))
        out[a:b + 1, x] = A[None] * (1 - t[:, None]) + B[None] * t[:, None]
    if left.any():
        out = harmonic_fill(out, left, (valid | mask) & ~left)
    return out

# ---------------------------------------------------------------- 선을 따라 미끄러뜨려 옮기기
def line_dist(m, d):
    """점 m, 방향 d 인 직선까지의 부호 있는 거리(법선 n=(-dy,dx) 쪽이 +)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = np.array([-d[1], d[0]], np.float32)
    return (xx - m[0]) * n[0] + (yy - m[1]) * n[1]

def slide_copy(dst, src, region, shift, band_d, band_half, feather=1.5):
    """region 안, 선에서 band_half 이내인 픽셀을 src 의 (x-sx, y-sy) 에서 가져온다."""
    sx, sy = shift
    shifted = np.zeros_like(src)
    shifted[max(0, sy):H + min(0, sy), max(0, sx):W + min(0, sx)] = \
        src[max(0, -sy):H - max(0, sy), max(0, -sx):W - max(0, sx)]
    # shifted[y,x] = src[y-sy, x-sx]
    a = np.clip((band_half + feather - np.abs(band_d)) / (2 * feather), 0, 1) * region
    return dst * (1 - a[..., None]) + shifted * a[..., None], a

# ================================================================ 판 가장자리 직선(원본에서 잰 값: 점 · 방향)
L_TL = (np.array([1579.92, 506.93]), np.array([0.6931, -0.7209]))   # 왼판 왼위 변
L_L = (np.array([1558.80, 614.39]), np.array([0.2366, 0.9716]))     # 왼판 왼 변
R_TL = (np.array([1813.06, 494.79]), np.array([0.6978, -0.7163]))   # 오른판 왼위 변
R_L = (np.array([1784.82, 612.64]), np.array([0.2110, 0.9775]))     # 오른판 왼 변
R_B = (np.array([1862.11, 697.19]), np.array([0.9945, 0.1051]))     # 오른판 아래 변

def inter(l1, l2):
    (m1, d1), (m2, d2) = l1, l2
    A = np.array([d1, -d2]).T
    t = np.linalg.solve(A, m2 - m1)
    return m1 + d1 * t[0]

L_UL = inter(L_TL, L_L)      # 왼판 왼위 꼭짓점 (4′)
R_UL = inter(R_TL, R_L)      # 오른판 왼위 꼭짓점 (4′)

L_RI = (np.array([1707.51, 589.51]), np.array([-0.2423, 0.9702]))   # 왼판 오른 변(앞면 안쪽 선)
L_TRI = (np.array([1675.36, 501.57]), np.array([0.7372, 0.6756]))   # 왼판 오른위 변(앞면 안쪽 선)
R_RI = (np.array([1969.60, 581.14]), np.array([-0.2463, 0.9692]))
R_TRI = (np.array([1946.67, 504.79]), np.array([0.7123, 0.7019]))

def ring_mask(center, r, keep_away, grow=1):
    """center 둘레 r 안의 '판 면 아님' 픽셀(쇠고리 + 그 흰 테) — 판 가장자리 선에서 keep_away px 안은 빼다."""
    reg = circle_mask(center[0], center[1], r)
    for (line, sgn, dist) in keep_away:
        reg &= (line_dist(*line) * sgn) > dist
    inv = reg & ~face_valid_map(O)
    m = dil(fill_holes(inv), grow) & reg
    return m

def stage1(img):
    # 1a. 왼판 오른위 쇠고리 지우기
    m = ring_mask((1693, 555), 20, [(L_RI, 1, 4.5), (L_TRI, 1, 4.5)])
    img = harmonic_fill(img, m, face_valid_map(img) & ~m)
    # 1b. 오른판 왼위 소용돌이 고리 지우기
    m = ring_mask((1800, 549), 24, [(R_L, -1, 5.0), (R_TL, 1, 5.0)], grow=3)
    img = vgrain_fill(img, m, grain_valid_map(img) & ~m)
    return img

def remove_note_and_nail(img, line, shift, note_box, nail_box, extra_lines=()):
    """위 꼭짓점의 쪽지 + 못 지우기.
    ① 판 쪽(선에서 5px 넘게 안쪽): 쪽지 · 핀 · 못 머리의 판 쪽 반 → 판 면으로 세로 잇기
    ② 선 띠(±6px): 같은 변을 변 방향으로 미끄러뜨려 깨끗한 구간을 옮겨 온다
    ③ 벽 쪽(선에서 5.5px 넘게 바깥): 못 머리의 벽 쪽 반 → 벽으로 세로 잇기"""
    m, d = line
    dd = line_dist(m, d)                       # + = 판 안쪽
    reg = rect_mask(*note_box) | rect_mask(*nail_box)
    reg = reg & (dd > 5.0)
    for (ln, sgn) in extra_lines:
        reg &= (line_dist(*ln) * sgn) > 4.5
    mf = dil(fill_holes(reg & ~face_valid_map(O)), 2) & reg
    img = harmonic_fill(img, mf, face_valid_map(img) & ~mf)
    # ② 띠: 못 상자 안에서만, 변 방향 끝은 2px 깃털
    x0, y0, x1, y1 = nail_box
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (xx - m[0]) * d[0] + (yy - m[1]) * d[1]
    # 못 머리가 차지하는 변 방향 구간
    nm = not_face_mask(O, rect_mask(*nail_box)) & (np.abs(dd) < 9)
    tn = t[nm]
    ta, tb = tn.min() - 2, tn.max() + 2
    along = np.clip((t - ta) / 2.0, 0, 1) * np.clip((tb - t) / 2.0, 0, 1)
    img, a = slide_copy(img, img, along, shift, dd, 6.0, 1.0)
    # ③ 벽 쪽
    wreg = rect_mask(*nail_box) & (dd < -5.5)
    F = np.array([211, 153, 89], np.float32)
    nw = wreg & (np.abs(O - F).max(2) > 20)
    mw = dil(nw, 1) & rect_mask(*nail_box) & (dd < -5.0)
    img = vfill(img, mw, wall_ok)
    return img

def stage2(img):
    img = remove_note_and_nail(img, L_TL, (25, -26), (1604, 472, 1649, 523), (1596, 466, 1622, 494), [(L_TRI, 1)])
    img = remove_note_and_nail(img, R_TL, (38, -39), (1847, 449, 1895, 508), (1840, 445, 1866, 472), [(R_TRI, 1)])
    return img

def shifted(src, sx, sy):
    """out[y,x] = src[y-sy, x-sx]"""
    out = src.copy()
    out[max(0, sy):H + min(0, sy), max(0, sx):W + min(0, sx)] = \
        src[max(0, -sy):H - max(0, sy), max(0, -sx):W - max(0, sx)]
    return out

def line_edges(Yc, y0, y1, thr=100.0):
    """세로 한 칸의 밝기에서 검은 선의 위 · 아래 가장자리(밝기 thr 를 지나는 자리, 소수)."""
    c = Yc[y0:y1]; top = bot = None
    for i in range(1, len(c)):
        if top is None and c[i - 1] >= thr > c[i]:
            top = y0 + i - 1 + (c[i - 1] - thr) / (c[i - 1] - c[i])
        if top is not None and c[i - 1] < thr <= c[i]:
            bot = y0 + i - 1 + (thr - c[i - 1]) / (c[i] - c[i - 1]); break
    return top, bot

def stage3(img):
    """오른판 오른아래(2′) 쇠고리 지우기.
    아래 변을 변 방향(36,~4)으로 미끄러뜨려 왼쪽 깨끗한 구간(판 면 · 검은 선 · 그 아래 그림자 띠 · 벽)을 옮겨 오되,
    칸마다 세로로 조금씩 옮기고 늘려 검은 선의 위 · 아래 가장자리가 고리 왼쪽(x1902) · 오른쪽(x1934)의 원래 선과 맞물리게 한다.
    벽 이음 홈(x≈1904)은 남기고, 고리에 가려졌던 그림자 띠 안의 홈은 홈 자신의 어둡기로 이어 그린다."""
    Yo = lum(O)
    X0, X1, Y0, Y1 = 1898, 1940, 664, 726
    xs_list = range(X0, X1 + 1)
    # 목표 선 가장자리: 왼쪽 · 오른쪽 기준에서 곧게
    tL, bL = 698.95, 703.48     # x=1902
    tR, bR = 701.50, 706.82     # x=1934
    src_tb = {}
    for x in range(X0 - 36 - 2, X1 - 36 + 3):
        src_tb[x] = line_edges(Yo[:, x], 688, 712)
    mapx = np.zeros((Y1 - Y0, X1 - X0 + 1), np.float32)
    mapy = np.zeros_like(mapx)
    for i, x in enumerate(xs_list):
        u = np.clip((x - 1902) / 32.0, -0.2, 1.2)
        tt = tL + (tR - tL) * u; bt = bL + (bR - bL) * u
        xs = x - 36
        ts = np.mean([src_tb[xs + k][0] for k in (-1, 0, 1)])
        bs = np.mean([src_tb[xs + k][1] for k in (-1, 0, 1)])
        yv = np.arange(Y0, Y1, dtype=np.float32)
        ys = np.where(yv < tt, yv - tt + ts,
             np.where(yv > bt, yv - bt + bs, ts + (yv - tt) * (bs - ts) / (bt - tt)))
        mapx[:, i] = xs; mapy[:, i] = ys
    sub = cv2.remap(O, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    S = img.copy(); S[Y0:Y1, X0:X1 + 1] = np.clip(sub, 0, 255)
    yy, xx = np.mgrid[0:H, 0:W]
    box = (xx >= 1900) & (xx <= 1937) & (yy >= 668) & (yy <= 723)
    D = np.abs(O - S).max(2)
    hook = box & (((D > 28)) | ((yy < 698) & (D > 9)))
    hook = dil(fill_holes(dil(hook, 1)), 2) & box
    T = hook & (((yy <= 713) & (xx >= 1902)) | ((yy >= 714) & (xx >= 1907)))
    a = cv2.GaussianBlur(T.astype(np.float32), (5, 5), 0.8)
    a = np.clip(a * 1.6, 0, 1) * dil(T, 1)
    out = img * (1 - a[..., None]) + S * a[..., None]
    # 벽 이음 홈 이어 그리기
    wallref = np.median(O[719:728, 1890:1900].reshape(-1, 3), 0)
    shadowref = np.median(O[704:710, 1880:1898].reshape(-1, 3), 0)
    fw = O[719:728, 1901:1909].mean(0) / wallref            # x=1901..1908
    TT = dil(T, 1)
    for y in range(700, 718):
        for i, x in enumerate(range(1901, 1909)):
            if not TT[y, x]:
                continue
            base = out[y, x]
            sh = np.clip((lum(wallref) - lum(base)) / (lum(wallref) - lum(shadowref)), 0, 1)
            f = 1 - (1 - fw[i]) * (1 - 0.34 * sh)
            out[y, x] = base * f
    return out

# ================================================================ 선 모양(프로파일) 재기 · 그리기
SGRID = np.arange(-12.0, 12.0001, 0.1)

def measure_profile(line, face_sign, t0, t1, band=11.0):
    """곧은 변 하나에서 거리 s(+ = 판 쪽)별 평균 색을 재어, 검정 K 와 바탕(판/벽) 사이의 비율 k(s)로 바꾼다."""
    m, d = line
    n = np.array([-d[1], d[0]])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    s = face_sign * ((xx - m[0]) * n[0] + (yy - m[1]) * n[1])
    t = (xx - m[0]) * d[0] + (yy - m[1]) * d[1]
    sel = (np.abs(s) <= band) & (t >= t0) & (t <= t1)
    sv = s[sel]; cv = O[sel]
    bins = np.round(sv / 0.1).astype(int)
    P = np.zeros((len(SGRID), 3)); cnt = np.zeros(len(SGRID))
    idx = bins + 120
    ok = (idx >= 0) & (idx < len(SGRID))
    np.add.at(P, idx[ok], cv[ok]); np.add.at(cnt, idx[ok], 1)
    good = cnt > 0
    for c in range(3):
        P[:, c] = np.interp(SGRID, SGRID[good], P[good, c] / cnt[good])
    # 0.3px 정도로 고르기
    ker = np.exp(-0.5 * (np.arange(-4, 5) * 0.1 / 0.25) ** 2); ker /= ker.sum()
    P = np.stack([np.convolve(np.pad(P[:, c], 4, mode='edge'), ker, 'valid') for c in range(3)], 1)
    K = P[np.argmin(lum(P))]
    face = P[SGRID >= 9.5].mean(0); wall = P[SGRID <= -9.5].mean(0)
    k_in = (P - K) / (face - K)
    k_out = (P - K) / (wall - K)
    return dict(K=K, face=face, wall=wall, k_in=k_in, k_out=k_out, P=P)

PROF = {}
def get_profiles():
    if PROF:
        return PROF
    PROF['L_TL'] = measure_profile(L_TL, +1, -18, 18)        # 왼판 왼위 변 깨끗한 구간
    PROF['L_L'] = measure_profile(L_L, -1, -28, 30)          # 왼판 왼 변 (n 이 벽 쪽이라 -1)
    PROF['R_TL'] = measure_profile(R_TL, +1, -25, 30)
    PROF['R_L'] = measure_profile(R_L, -1, -35, 38)
    ks = [PROF[k] for k in ('L_TL', 'L_L', 'R_TL', 'R_L')]
    PROF['avg'] = dict(K=np.mean([p['K'] for p in ks], 0),
                       k_in=np.mean([p['k_in'] for p in ks], 0),
                       k_out=np.mean([p['k_out'] for p in ks], 0))
    return PROF

def kval(prof, which, dist):
    """선 가운데에서 dist(>=0) 떨어진 곳의 채널별 k. k_in 은 판 쪽(+s), k_out 은 벽 쪽(-s)에서 잰 값."""
    k = prof[which]
    d = np.clip(dist, 0, 12.0)
    s = d if which == 'k_in' else -d
    return np.stack([np.interp(s, SGRID, k[:, c]) for c in range(3)], -1)

# ================================================================ 4′ 팔 + 5′ 마디
THETA = np.deg2rad(55.0)                 # 왼쪽 위로 55° (두 판 같게)
U = np.array([-np.cos(THETA), -np.sin(THETA)])   # 팔 방향(꼭짓점 → 바깥)
STICK_HW = 6.0        # 막대 반폭(선 가운데까지)
STICK_LEN = 46.0      # 꼭짓점 → 마디 시작
KNOB = 20.0           # 마디 한 변(선 가운데까지)

def grid(bbox):
    x0, y0, x1, y1 = bbox
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float64)
    return xx, yy

def sd_half(line, sign, xx, yy):
    m, d = line
    return sign * ((xx - m[0]) * (-d[1]) + (yy - m[1]) * d[0])

def sd_box(center, u, half_len, half_w, xx, yy):
    """회전한 네모의 부호 있는 거리(+ = 안)."""
    px = xx - center[0]; py = yy - center[1]
    t = px * u[0] + py * u[1]; v = px * (-u[1]) + py * u[0]
    qx = np.abs(t) - half_len; qy = np.abs(v) - half_w
    out = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0)
    return -out

def shade(sd, BGin, BGout, prof_in, prof_out):
    """검은 윤곽선 그리기: sd>=0 은 안(바탕 BGin), sd<0 은 밖(바탕 BGout).
    색 = K + (바탕 - K) · k(거리) — 원본 판 가장자리에서 잰 k(흰 테 포함)를 채널별로 곱한다."""
    K = prof_in['K']
    kin = kval(prof_in, 'k_in', np.maximum(sd, 0))
    kout = kval(prof_out, 'k_out', np.maximum(-sd, 0))
    cin = K + (BGin - K) * kin
    cout = K + (BGout - K) * kout
    return np.where((sd >= 0)[..., None], cin, cout)

def wall_valid_map(im):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    Y = lum(im)
    return (Y > 140) & (Y < 186) & ((r - b) > 95) & (np.abs(r - 211) < 24) & (np.abs(b - 89) < 24)

def arm_patch(img, vtx, tl_line, l_line, prof_tl, prof_l, extra_clear=None, bbox=None):
    """꼭짓점 vtx 에서 U 방향으로 막대 + 네모 마디. 판의 두 변(tl_line, l_line)은 판 쪽이 +가 되게 sign 을 맞춘다."""
    P = get_profiles()
    x0, y0, x1, y1 = bbox
    xx, yy = grid(bbox)
    s_tl = sd_half(tl_line, +1, xx, yy)          # 왼위 변: n 이 판 쪽
    s_l = sd_half(l_line, -1, xx, yy)            # 왼 변: n 이 벽 쪽 → -1
    sd_board = np.minimum(s_tl, s_l)
    # 막대: 판 안 14px 에서 마디 가운데까지
    sd_stick = sd_box(vtx + U * ((STICK_LEN + KNOB / 2) - 14.0) / 2.0, U, (STICK_LEN + KNOB / 2 + 14.0) / 2.0, STICK_HW, xx, yy)
    c_knob = vtx + U * (STICK_LEN + KNOB / 2.0)
    sd_knob = sd_box(c_knob, U, KNOB / 2.0, KNOB / 2.0, xx, yy)
    sdU = np.maximum(sd_board, sd_stick)
    sub = img[y0:y1, x0:x1].copy()
    # --- 바탕 만들기: 판 면(BGF) · 벽(BGW). 옛 고리 · 판 가장자리 선(+흰 테)만 빼고 나머지(벽 결 · 이음 홈 · 판 결)는 그대로 쓴다
    clr = np.zeros((y1 - y0, x1 - x0), bool) if extra_clear is None else extra_clear[y0:y1, x0:x1]
    fv = (sd_board > 7.0) & ~clr
    wv = (sd_board < -7.0) & ~clr
    mF = np.zeros((H, W), bool); mF[y0:y1, x0:x1] = ~fv
    vF = np.zeros((H, W), bool); vF[y0:y1, x0:x1] = fv
    BGF_img = harmonic_fill(img, mF, vF, iters=1500)
    mW = np.zeros((H, W), bool); mW[y0:y1, x0:x1] = ~wv
    vW = np.zeros((H, W), bool); vW[y0:y1, x0:x1] = wv
    BGW_img = vgrain_fill(img, mW, vW)
    BGF = BGF_img[y0:y1, x0:x1]; BGW = BGW_img[y0:y1, x0:x1]
    # --- 1층: 판 ∪ 막대 실루엣 (가까운 변의 프로파일)
    use_stick = sd_stick > sd_board
    use_tl = (~use_stick) & (s_tl < s_l)
    lay = np.zeros_like(sub)
    for msk, pr in ((use_stick, P['avg']), (use_tl, prof_tl), ((~use_stick) & (~use_tl), prof_l)):
        r = shade(sdU, BGF, BGW, pr, pr)
        lay[msk] = r[msk]
    # --- 2층: 네모 마디(온 윤곽선), 안은 판 면 색
    knob_face = BGF
    r2a = shade(sd_knob, knob_face, lay, P['avg'], P['avg'])            # 바깥이 벽
    Pin_as_out = dict(K=P['avg']['K'], k_in=P['avg']['k_in'], k_out=P['avg']['k_in'][::-1].copy())
    r2b = shade(sd_knob, knob_face, lay, P['avg'], Pin_as_out)         # 바깥이 막대 면(판 쪽 프로파일)
    r2 = np.where((sdU > 0)[..., None], r2b, r2a)
    near_knob = sd_knob > -9.0
    lay2 = np.where(near_knob[..., None], r2, lay)
    # --- 바꿀 자리: 막대 · 마디 둘레 9px, 옛 고리 자리, 꼭짓점 둘레
    reg = (np.maximum(sd_stick, sd_knob) > -9.0) & ((sd_board < 6.0) | (sd_stick > -9.0))
    dv = np.hypot(xx - vtx[0], yy - vtx[1])
    reg |= dv < 14.0
    if extra_clear is not None:
        reg |= dil(extra_clear, 3)[y0:y1, x0:x1]
    a = cv2.GaussianBlur(reg.astype(np.float32), (7, 7), 1.2)
    a = np.clip(a * 1.5, 0, 1)
    out = img.copy()
    out[y0:y1, x0:x1] = sub * (1 - a[..., None]) + lay2 * a[..., None]
    info = dict(c_knob=c_knob, end=vtx + U * (STICK_LEN + KNOB), reg=reg, bbox=bbox)
    return out, info

ARM_INFO = {}
def stage4(img):
    # 왼판: 왼위 꼭짓점의 옛 쇠고리(+ 흰 테)를 바탕에서 빼고 다시 그린다
    reg = circle_mask(1546, 559, 21)
    ring = reg & ~face_valid_map(O) & ~wall_valid_map(O)
    # 판 가장자리 선 자체는 빼고(선은 다시 그려진다) 고리만 — 선 둘레 3px 은 어차피 다시 그림
    ring = dil(fill_holes(ring), 2) & reg
    img, ARM_INFO['L'] = arm_patch(img, L_UL, L_TL, L_L, get_profiles()['L_TL'], get_profiles()['L_L'],
                                   extra_clear=ring, bbox=(1470, 455, 1585, 600))
    img, ARM_INFO['R'] = arm_patch(img, R_UL, R_TL, R_L, get_profiles()['R_TL'], get_profiles()['R_L'],
                                   extra_clear=None, bbox=(1697, 445, 1800, 580))
    return img

# ================================================================ 쇠고리 오려 내기(매트)
def ring_cutout():
    """왼판 오른위 쇠고리를 원본에서 오려 낸다: 색(C) · 알파(α) · 그 뒤 판 면(Fbg).
    α: 검은 테 · 회색 몸통(+1px) = 1, 그 밖은 '검정과 판 면의 섞임' 비율."""
    x0, y0, x1, y1 = 1673, 532, 1712, 576
    C = O[y0:y1, x0:x1].copy()
    Fimg = stage1(O.copy())                        # 고리를 지운 판 면(같은 방법)
    Fbg = Fimg[y0:y1, x0:x1]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    inside = ((xx - 1693) ** 2 + (yy - 555) ** 2 <= 19.5 ** 2) & (xx <= 1710)
    Y = lum(C)
    D = (Y < 95) & inside
    G = (np.abs(C[..., 0] - C[..., 2]) < 45) & (Y > 95) & inside
    K = np.array([3.0, 0.4, 0.2])
    amix = 1 - np.mean((C - K) / np.maximum(Fbg - K, 1), axis=2)
    amix = np.clip(amix, 0, 1) * inside
    core = D | (dil(G, 1) & dil(D | G, 0))
    alpha = np.where(core, 1.0, amix)
    alpha[~dil(D | G, 2)] = 0.0
    return C, alpha.astype(np.float32), Fbg

def paste_cut(img, C, alpha, Fbg, x0, y0, k_rot=0):
    """오려 낸 조각을 (x0,y0)에 붙인다: out = C + (1-α)(새 바탕 - 옛 바탕)."""
    if k_rot:
        C = np.rot90(C, k_rot); alpha = np.rot90(alpha, k_rot); Fbg = np.rot90(Fbg, k_rot)
    h, w = alpha.shape
    bg = img[y0:y0 + h, x0:x0 + w]
    out = img.copy()
    out[y0:y0 + h, x0:x0 + w] = C + (1 - alpha[..., None]) * (bg - Fbg)
    return out

RING_BULB_ROT = np.array([30.2, 31.1])     # 90° 돌린 조각 안 나사 고리(bulb) 자리
def stage5(img):
    """마디 끝에 쇠고리(5′ 의 -OH): 왼판 오른위 고리를 오려 90° 돌려(나사 머리가 마디 쪽) 붙인다."""
    C, a, F = ring_cutout()
    for key in ('L', 'R'):
        E = ARM_INFO[key]['end']
        bulb = E - U * 2.5
        x0 = int(round(bulb[0] - RING_BULB_ROT[0])); y0 = int(round(bulb[1] - RING_BULB_ROT[1]))
        img = paste_cut(img, C, a, F, x0, y0, k_rot=-1)
        ARM_INFO[key]['ring_xy'] = (x0, y0)
    return img

# ================================================================ 쪽지 + 못 옮기기 (1′)
def note_cutout(bbox, rect, nail_seed, stage2_img, tl_line):
    """위 꼭짓점의 빨간 쪽지 + 못을 오려 낸다. rect = 쪽지 바깥 테두리 대략 [x0,y0,x1,y1].
    쪽지: 빨강 · 검은 테 · 핀 = 1, 테 바깥 2px 은 검정/판 면 섞임 비율, 4px 까지는 흰 테(차이)만 옮긴다.
    못 머리: 회색 덩이만 오려 내고 테는 새로 그린다(원래 테가 판 변의 검은 선과 붙어 있어서)."""
    x0, y0, x1, y1 = bbox
    C = O[y0:y1, x0:x1].copy()
    Fbg = stage2_img[y0:y1, x0:x1].copy()
    yy, xx = np.mgrid[y0:y1, x0:x1]
    Y = lum(C)
    rx0, ry0, rx1, ry1 = rect
    inrect = (xx >= rx0) & (xx <= rx1) & (yy >= ry0) & (yy <= ry1)
    D = Y < 95
    Rd = ((C[..., 0] - C[..., 1]) > 70) & (C[..., 0] > 150)
    G = (np.abs(C[..., 0] - C[..., 2]) < 45) & (Y > 110)
    # 못 머리: seed 에 이어진 회색 덩이(쪽지 네모 밖)
    sx, sy = nail_seed
    Gh = (np.abs(C[..., 0] - C[..., 2]) < 50) & (Y > 80)
    g8 = (Gh & ((xx - sx) ** 2 + (yy - sy) ** 2 <= 81)).astype(np.uint8)
    n, lab = cv2.connectedComponents(g8)
    L0 = lab[sy - y0, sx - x0]
    assert L0 != 0, 'nail seed not on head'
    head = lab == L0
    dist = cv2.distanceTransform((~head).astype(np.uint8), cv2.DIST_L2, 5)
    # 쪽지 네모
    core_rect = fill_holes((D | Rd | G) & inrect & (dist > 2.5))
    K = np.array([3.0, 0.4, 0.2])
    amix = np.clip(1 - np.mean((C - K) / np.maximum(Fbg - K, 1), axis=2), 0, 1)
    ring2 = dil(core_rect, 2) & ~core_rect
    a_rect = np.where(core_rect, 1.0, amix * ring2).astype(np.float32)
    dd = sd_half(tl_line, +1, xx.astype(np.float64), yy.astype(np.float64))
    support = (dil(core_rect, 4) & (dd > 6.0) & (dist > 6.0)) | core_rect
    return dict(C=C, a=a_rect, F=Fbg, support=support, head=head, dist=dist)

def paste_note(img, cut, x0, y0):
    C, a, F, sup, head, dist = cut['C'], cut['a'], cut['F'], cut['support'], cut['head'], cut['dist']
    h, w = a.shape
    bg = img[y0:y0 + h, x0:x0 + w].copy()
    P = get_profiles()['avg']
    # ① 못 머리: 회색 덩이는 그대로, 그 둘레는 검은 테(선 가운데 = 덩이에서 1px) + 흰 테
    k = kval(P, 'k_in', np.maximum(dist - 0.7, 0))
    nail = P['K'] + (bg - P['K']) * k
    nail = np.where(head[..., None], C, nail)
    near = (dist < 8.0)
    out = np.where(near[..., None], nail, bg)
    # ② 쪽지(못 머리 위에 겹쳐): out = C + (1-α)(바탕 - 옛 바탕), 지지 영역 밖은 바탕 그대로
    Cn = np.where(sup[..., None], C, F)
    a = a * sup
    out = Cn + (1 - a[..., None]) * (out - F)
    res = img.copy(); res[y0:y0 + h, x0:x0 + w] = out
    return res

def stage6(img, stage2_img):
    """쪽지 + 못을 위 꼭짓점에서 오른위 꼭짓점(1′)으로 옮긴다(평행 이동만)."""
    jobs = [  # (bbox, rect, nail_seed, tl_line, (dx,dy))
        ((1596, 469, 1647, 522), (1609, 475, 1642, 517), (1609, 480), L_TL, (62, 60)),
        ((1840, 446, 1892, 504), (1851, 454, 1888, 499), (1851, 459), R_TL, (76, 77)),
    ]
    for bbox, rect, seed, tl, (dx, dy) in jobs:
        cut = note_cutout(bbox, rect, seed, stage2_img, tl)
        img = paste_note(img, cut, bbox[0] + dx, bbox[1] + dy)
    return img

# ================================================================ 위 꼭짓점 = 고리 속 산소: 판을 뚫은 옹이구멍
HOLE_DARK = np.array([110.0, 66.0, 28.0])     # 구멍 너머 벽(그늘진 어두운 갈색 — 벽 이음 홈 색에 맞춤)
HOLE_WALL = np.array([172.0, 128.0, 80.0])    # 구멍 안쪽 벽(판 두께, 그늘) — 옆면 띠 색을 어둡게
HOLES = {  # 꼭짓점 이등분선을 따라 꼭짓점에서 d 만큼 안쪽, 선 가운데 반지름 rc
    'L': dict(apex=np.array([1627.85, 457.08]), bis=np.array([0.0241, 0.9997]), d=30.6, rc=12.3),
    'R': dict(apex=np.array([1871.69, 434.61]), bis=np.array([0.0264, 0.9997]), d=32.0, rc=13.3),
}
def draw_hole(img, apex, bis, d, rc, thin=1.0):
    P = get_profiles()['avg']
    c = apex + bis * d
    x0, y0 = int(c[0] - rc - 10), int(c[1] - rc - 10)
    x1, y1 = int(c[0] + rc + 11), int(c[1] + rc + 11)
    xx, yy = grid((x0, y0, x1, y1))
    r = np.hypot(xx - c[0], yy - c[1])
    sd = rc - r                                        # + = 구멍 안
    # 구멍 안: 오른위로 비낀 뒤쪽 구멍(지름 같음)과 겹치는 곳은 벽(어둠), 아니면 안쪽 벽(초승달)
    off = np.array([1.0, -1.0]) / np.sqrt(2) * (rc * 0.36)
    rb = np.hypot(xx - (c[0] + off[0]), yy - (c[1] + off[1]))
    t = np.clip((rc - 1.6 - rb) / 1.2 + 0.5, 0, 1)[..., None]   # 1 = 뒤 구멍 안(벽이 보임)
    inner = HOLE_DARK * t + HOLE_WALL * (1 - t)
    sub = img[y0:y1, x0:x1].copy()
    kin = kval(P, 'k_out', np.maximum(sd, 0) * thin)
    kout = kval(P, 'k_in', np.maximum(-sd, 0) * thin)
    cin = P['K'] + (inner - P['K']) * kin
    cout = P['K'] + (sub - P['K']) * kout
    lay = np.where((sd >= 0)[..., None], cin, cout)
    a = np.clip((rc + 9.0 - r) / 2.0, 0, 1)[..., None]
    out = img.copy()
    out[y0:y1, x0:x1] = sub * (1 - a) + lay * a
    return out, c

def stage7(img):
    for k in ('L', 'R'):
        h = HOLES[k]
        img, c = draw_hole(img, h['apex'], h['bis'], h['d'], h['rc'])
        h['c'] = c
    return img

def run():
    img = O.copy()
    img = stage1(img)                 # 왼판 오른위 고리 · 오른판 왼위 고리 지우기
    img = stage2(img)                 # 위 꼭짓점 쪽지 · 못 지우기(판 변 잇기)
    img_s2 = img.copy()
    img = stage3(img)                 # 오른판 오른아래(2′) 고리 지우기
    img = stage4(img)                 # 4′ 팔 + 5′ 마디 (왼판은 옛 왼위 고리도 함께 지움)
    img = stage5(img)                 # 마디 끝 쇠고리(5′ -OH)
    img = stage6(img, img_s2)         # 쪽지 + 못 → 오른위(1′)
    img = stage7(img)                 # 위 꼭짓점 옹이구멍(고리 속 O)
    return np.clip(img + 0.5, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    out = run()
    Image.fromarray(out).save(OUTDIR + '/final_new.png')
    d = np.abs(out.astype(int) - O.astype(int)).max(2) > 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(d.astype(np.uint8), np.ones((9, 9), np.uint8)))
    print('final_new.png saved', out.shape, 'changed px', int(d.sum()))
    for i in range(1, n):
        x, y, w, h, _a = st[i]
        sub = d[y:y + h, x:x + w]
        ys, xs = np.where(sub)
        print('  changed box [x,y,w,h] =', [int(x + xs.min()), int(y + ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)])

#!/usr/bin/env python3
"""spark_clone.py — 설치본 오른쪽 아래 **제미나이 반짝이 표식**(반투명 흰 네 꼭지 별, 중심 ≈ (903.5, 903.5))을
같은 그림의 **다른 자리 결을 옮겨** 덮는다(방향 복제). 바탕이 평평하거나(크림 · 판자 면) 결이 되풀이되는(벽돌 · 나뭇결 · 판자 줄) 판용.
(되돌림 식 I = (I′ − 255a)/(1 − a) 안은 버렸다 — a 가 판마다 0.25~0.76 으로 달라 별마다 재야 하고, a > 0.5 면 압축 잡음이 2~3배로 커져 얼룩 · 가장자리 테가 남았다.)

별 모양: 평평한 판 다섯 장에서 맞춘 해석식 (|x−cx|/R)^p + (|y−cy|/R)^p ≤ 1 · p 0.69 · R 25.4 — 판마다 R ±1 · 중심 ±1 을 다시 맞춤
   (고역 L − 중앙값31 에서 별 가장자리 안 2px 띠 − 밖 2px 띠 대비가 가장 큰 것).
덮을 곳: 별(M > 0.01)을 3px 넓힘(--dil · 별 가장자리 번짐까지). 고를 곳: 그 둘레 12px 고리가 가장 잘 맞는 어긋남(dx, dy ∈ ±SEARCH, 1 간격,
   덮을 곳+고리와 겹치지 않는 것, 그림 안) — 비용 = 고리 RGB 제곱평균근 차(cv2.matchTemplate 가면 TM_SQDIFF) + 0.5 × |옮겨 올 자리 안의 기울기 평균 − 고리 기울기 평균|
   (평평한 바탕에 물건 조각을 끌어오지 않게) + 0.7 × |옮겨 올 자리 안 평균 색 − 고리 평균 색|(그 자리만의 그늘을 끌어오지 않게).
붙이기: 고리 위 (원본 − 옮겨 온 것) 차를 σ3 로 고르게 해 덮을 곳 안을 라플라스 막으로 이어 더함(국소 그늘까지) · σ1.5 섞음(안은 다 바꿈).
사용: python3 spark_clone.py OUTDIR pid[:dx,dy][@cx,cy,R] ...   (입력 tools/blind/png/<pid>.png — 무손실 설치본; :dx,dy 로 어긋남을 박을 수 있다)
      --search N (기본 140) · --src DIR · --at CX,CY,R (기본 자리 말고 다른 자리 별 — 넓은 판 · 다른 출력 크기에서 온 별; ±2 · R ±1 다시 맞춤)
      --nofit: @cx,cy,R 를 다시 맞추지 않고 그대로(spark_inv 가 맞춘 자리를 넘길 때 — 맞추기가 판마다 20초 넘게 걸린다)"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

P0, R0, CX0, CY0 = 0.69, 25.4, 903.5, 903.5
S = 8
DIL = 3
AT = None
NOFIT = False


def star_mask_full(R, cx, cy, H=1024, W=1024, p=P0):
    n = int(R * 1.6) * 2 + 8
    x0, y0 = int(cx) - n // 2, int(cy) - n // 2
    ys = (np.arange(n * S) + 0.5) / S + y0 - 0.5
    xs = (np.arange(n * S) + 0.5) / S + x0 - 0.5
    XX, YY = np.meshgrid(xs, ys)
    m = ((np.abs(XX - cx) / R) ** p + (np.abs(YY - cy) / R) ** p <= 1).astype(float)
    m = m.reshape(n, S, n, S).mean(axis=(1, 3))
    M = np.zeros((H + 2 * n, W + 2 * n)); M[y0 + n:y0 + 2 * n, x0 + n:x0 + 2 * n] = m
    return M[n:n + H, n:n + W]


def fit_geometry(L, R0_=None, CX_=None, CY_=None, span=1.0):
    """별 가장자리 안 2px 띠 − 밖 2px 띠 대비(고역)가 가장 큰 R · 중심. 처음 값은 기본(903.5, 903.5, 25.4) 또는 --at."""
    R0_ = R0 if R0_ is None else R0_
    CX_ = CX0 if CX_ is None else CX_
    CY_ = CY0 if CY_ is None else CY_
    H, W = L.shape
    h = int(R0_ * 1.8) + 6
    y0, y1 = max(0, int(CY_) - h), min(H, int(CY_) + h)
    x0, x1 = max(0, int(CX_) - h), min(W, int(CX_) + h)
    hp = L - ndi.median_filter(L, size=31)
    best = None
    for R in np.arange(R0_ - 1.0, R0_ + 1.01, 0.25):
        for cx in np.arange(CX_ - span, CX_ + span + 0.01, 0.5):
            for cy in np.arange(CY_ - span, CY_ + span + 0.01, 0.5):
                M = star_mask_full(R, cx, cy, H, W)[y0:y1, x0:x1]
                din = ndi.distance_transform_edt(M > 0.5)
                dout = ndi.distance_transform_edt(M <= 0.5)
                c = hp[y0:y1, x0:x1][(M > 0.5) & (din <= 2)].mean() - hp[y0:y1, x0:x1][(M <= 0.5) & (dout <= 2)].mean()
                if best is None or c > best[0]:
                    best = (c, R, cx, cy)
    return best


def membrane(B, Om):
    """Om 안은 라플라스 막(4이웃 평균), Om 밖은 B 값 그대로 — 채널마다 희소 풀이."""
    from scipy.sparse import lil_matrix
    from scipy.sparse.linalg import spsolve
    H, W = Om.shape
    idx = -np.ones((H, W), int)
    ys, xs = np.nonzero(Om)
    idx[ys, xs] = np.arange(len(ys))
    n = len(ys)
    A = lil_matrix((n, n))
    b = np.zeros((n, 3))
    for k, (y, x) in enumerate(zip(ys, xs)):
        cnt = 0
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            yy, xx = y + dy, x + dx
            if not (0 <= yy < H and 0 <= xx < W):
                continue
            cnt += 1
            if Om[yy, xx]:
                A[k, idx[yy, xx]] = -1
            else:
                b[k] += B[yy, xx]
        A[k, k] = cnt
    A = A.tocsr()
    out = B.copy()
    for c in range(3):
        out[ys, xs, c] = spsolve(A, b[:, c])
    return out


def process(spec, outdir, srcdir, SEARCH):
    at = AT
    if '@' in spec:
        spec, a_ = spec.split('@')
        at = tuple(float(v) for v in a_.split(','))
    pid, fixed = (spec.split(':') + [None])[:2]
    full = np.asarray(Image.open(os.path.join(srcdir, pid + '.png')).convert('RGB')).astype(np.float64)
    H, W = full.shape[:2]
    L = full.mean(axis=2)
    if at and NOFIT:
        c, R, cx, cy = float('nan'), at[2], at[0], at[1]
    elif at:
        c, R, cx, cy = fit_geometry(L, at[2], at[0], at[1], span=2.0)
    else:
        assert (H, W) == (1024, 1024), (pid, full.shape)
        c, R, cx, cy = fit_geometry(L)
    M = star_mask_full(R, cx, cy, H, W)
    mask = ndi.binary_dilation(M > 0.01, iterations=DIL)
    ring = ndi.binary_dilation(mask, iterations=12) & ~mask
    G = ndi.gaussian_gradient_magnitude(L, 1.0)
    gring = G[ring].mean()
    ys, xs = np.nonzero(ring)
    my, mx = np.nonzero(mask)
    span = ndi.binary_dilation(mask, iterations=12)
    sy0, sy1 = np.nonzero(span.any(axis=1))[0][[0, -1]]
    sx0, sx1 = np.nonzero(span.any(axis=0))[0][[0, -1]]
    hh, ww = sy1 - sy0 + 1, sx1 - sx0 + 1

    # 빠른 찾기: 둘레 상자(span) 를 틀로, 고리만 가면(mask)으로 한 제곱차 합(cv2.matchTemplate TM_SQDIFF) +
    #   옮겨 올 자리 안 기울기 평균(덮을 곳 모양으로 상관) 벌점
    import cv2
    T = full[sy0:sy1 + 1, sx0:sx1 + 1].astype(np.float32)
    rm = ring[sy0:sy1 + 1, sx0:sx1 + 1].astype(np.float32)
    mm = mask[sy0:sy1 + 1, sx0:sx1 + 1].astype(np.float32)
    nr, nm = rm.sum(), mm.sum()
    ssd = cv2.matchTemplate(full.astype(np.float32), T, cv2.TM_SQDIFF, mask=np.dstack([rm] * 3))
    rmse = np.sqrt(np.maximum(ssd, 0) / (nr * 3))
    gin = cv2.matchTemplate(G.astype(np.float32), mm, cv2.TM_CCORR) / nm
    # 옮겨 올 자리 안 평균 밝기가 고리 평균과 다르면(그 자리만의 그늘) 벌점 — 막 보간은 둘레만 맞추고 안의 얼룩은 못 고친다
    ring_mean = full[ring].mean(axis=0)
    inm = np.stack([cv2.matchTemplate(full[..., k].astype(np.float32), mm, cv2.TM_CCORR) / nm for k in range(3)], axis=2)
    dmean = np.abs(inm - ring_mean[None, None, :]).mean(axis=2)
    score = rmse + 0.5 * np.abs(gin - gring) + 0.7 * dmean
    raw = score.copy()
    oy, ox = np.mgrid[0:score.shape[0], 0:score.shape[1]]
    ddy, ddx = oy - sy0, ox - sx0
    bad = ((np.abs(ddx) < ww) & (np.abs(ddy) < hh)) | (np.abs(ddx) > SEARCH) | (np.abs(ddy) > SEARCH)
    score[bad] = np.inf

    def cost(dx, dy):
        y, x = sy0 + dy, sx0 + dx
        if not (0 <= y < score.shape[0] and 0 <= x < score.shape[1]):
            return None
        return float(raw[y, x])

    if fixed:
        dx, dy = map(int, fixed.split(','))
        best = (cost(dx, dy), dx, dy)
    else:
        k = int(np.argmin(score))
        y, x = np.unravel_index(k, score.shape)
        best = (float(score[y, x]), int(x - sx0), int(y - sy0))
    e, dx, dy = best
    src = np.roll(np.roll(full, -dy, axis=0), -dx, axis=1)
    # 톤 맞춤(막 보간): 고리 위 (원본 − 옮겨 온 것) 차를 고리 안에서만 σ3 로 고르게 한 뒤(정규화 합성곱),
    #   덮을 곳 안은 그 둘레 값을 잇는 조화 함수(라플라스 막)로 채워 더한다 — 판자 줄마다 · 벽 위아래마다 다른 그늘도 따라간다.
    #   (평면 맞춤은 별이 두 바탕(크림 · 벽돌)에 걸치거나 그늘이 국소적일 때 다이아몬드 모양 얼룩을 남겼다.)
    D = full - src
    rb = ndi.binary_dilation(mask, iterations=4) & ~mask
    num = np.stack([ndi.gaussian_filter(D[..., k] * rb, 3.0) for k in range(3)], axis=2)
    den = ndi.gaussian_filter(rb.astype(float), 3.0)[..., None]
    Ds = num / np.maximum(den, 1e-6)
    y0b, y1b = my.min() - 6, my.max() + 7
    x0b, x1b = mx.min() - 6, mx.max() + 7
    sub_mask = mask[y0b:y1b, x0b:x1b]
    corr = membrane(Ds[y0b:y1b, x0b:x1b], sub_mask)
    src = src.copy()
    src[y0b:y1b, x0b:x1b][sub_mask] += corr[sub_mask]
    off = corr[sub_mask].mean(axis=0)
    w = ndi.gaussian_filter(mask.astype(float), 1.5)
    w = np.maximum(w, mask.astype(float))
    out = full * (1 - w[..., None]) + src * w[..., None]
    out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(outdir, pid + '.png'))
    hb = int(R * 2.6)
    bx = (int(cx) - hb, int(cy) - hb, int(cx) + hb, int(cy) + hb)
    a_img = Image.fromarray(full.astype(np.uint8)).crop(bx).resize((300, 300), Image.LANCZOS)
    b_img = Image.fromarray(out).crop(bx).resize((300, 300), Image.LANCZOS)
    cmp_ = Image.new('RGB', (610, 300), 'white'); cmp_.paste(a_img, (0, 0)); cmp_.paste(b_img, (310, 0))
    cmp_.save(os.path.join(outdir, pid + '_cmp.png'))
    print('%-8s R %.2f c (%.1f, %.1f) contrast %.1f  offset (%d, %d)  cost %.1f  tone %s' % (pid, R, cx, cy, c, dx, dy, e, off.round(1)))


if __name__ == '__main__':
    args = sys.argv[1:]
    srcdir, SEARCH = 'tools/blind/png', 140
    while args and args[0].startswith('--'):
        if args[0] == '--src':
            srcdir = args[1]; args = args[2:]
        elif args[0] == '--search':
            SEARCH = int(args[1]); args = args[2:]
        elif args[0] == '--dil':
            DIL = int(args[1]); args = args[2:]
        elif args[0] == '--at':
            AT = tuple(float(v) for v in args[1].split(',')); args = args[2:]
        elif args[0] == '--nofit':
            NOFIT = True; args = args[1:]
    outdir = args[0]
    os.makedirs(outdir, exist_ok=True)
    for spec in args[1:]:
        process(spec, outdir, srcdir, SEARCH)

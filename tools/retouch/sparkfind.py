#!/usr/bin/env python3
"""sparkfind.py — 설치본마다 **제미나이 반짝이 표식**(반투명 흰 네 꼭지 별 (|x|/R)^p + (|y|/R)^p ≤ 1 · p 0.69)이 남았는지 빠르게 잰다.
fit_geometry(spark_clone.py)는 자리 하나에 마스크 225개를 거리 변환까지 해 판마다 ~20초 — 192판을 다시 훑기엔 느렸다.
여기서는 R 마다(반 화소 위상 넷) 「별 가장자리 안 2px 띠 평균 − 밖 2px 띠 평균」을 낱알(kernel)로 만들어
고역 밝기(L − 중앙값31)에 cv2.filter2D 로 한 번에 상관 → 모든 자리의 대비가 한꺼번에 나온다.
  정사각 1024: 중심 903.5 ± 3 · R 23..28
  그 밖의 크기: 오른쪽·아래 모서리에서 40..200px 안 어디든 · R 11..27 (넓은 판은 별 자리가 판마다 다르다 — s42p01 (932, 487))
출력: pid 크기 대비 R cx cy — 대비 내림차순. 대비 ≳ 8 이면 별이 보인다(9/30 훑기 기준). 눈으로 확인할 모음판: --sheet OUT.png
사용: python3 sparkfind.py [--sheet OUT.png] [pid ...]   (없으면 tools/blind/png 전부)"""
import sys, os, glob
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import cv2

P = 0.69
S = 8


def star_mask(R, n, fx, fy):
    c = n / 2.0
    ys = (np.arange(n * S) + 0.5) / S - 0.5
    XX, YY = np.meshgrid(ys, ys)
    m = ((np.abs(XX - (c + fx)) / R) ** P + (np.abs(YY - (c + fy)) / R) ** P <= 1).astype(float)
    return m.reshape(n, S, n, S).mean(axis=(1, 3))


_KCACHE = {}


def kernel(R, fx, fy):
    key = (R, fx, fy)
    if key not in _KCACHE:
        n = int(R * 2.4) * 2 + 9
        M = star_mask(R, n, fx, fy)
        din = ndi.distance_transform_edt(M > 0.5)
        dout = ndi.distance_transform_edt(M <= 0.5)
        inn = (M > 0.5) & (din <= 2)
        out = (M <= 0.5) & (dout <= 2)
        K = inn / inn.sum() - out / out.sum()
        _KCACHE[key] = (K.astype(np.float32), n)
    return _KCACHE[key]


def scan(path):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    L = np.asarray(im).astype(np.float32).mean(axis=2)
    if (W, H) == (1024, 1024):
        cands = [(float(R), None) for R in np.arange(24.0, 27.01, 0.5)]
        box = (902, 902, 905, 905)            # 중심 903.5 ± 1.5 (9/30 맞춘 53판이 모두 이 안)
    else:
        # 제미나이는 별을 원 출력 크기에 맞춰 같은 꼴로 찍는다: 1024 정사각에서 여백 120.5 · R 25.4 → 여백/R ≈ 4.74.
        # 넓은 판(원 출력을 너비 1024 로 줄인 것)도 이 비가 지켜진다 — 1024×559 (936, 471) R 18.5 · ×572 (934, 482) R 19 · ×506 (940, 422) R 17.7.
        # 그래서 R 마다 중심을 (W − kR, H − kR), k 4.55..4.95 근처 ±1.5 화소로만 찾는다(구슬 · 가장자리 오탐을 막는다).
        cands = [(float(R), k) for R in np.arange(12.0, 26.01, 0.5) for k in (4.6, 4.74, 4.9)]
        box = (W - 26 * 4.95 - 2, H - 26 * 4.95 - 2, W - 12 * 4.55 + 2, H - 12 * 4.55 + 2)
    pad = 75
    x0, y0 = max(0, int(box[0]) - pad), max(0, int(box[1]) - pad)
    x1, y1 = min(W, int(box[2]) + pad), min(H, int(box[3]) + pad)
    sub = L[y0:y1, x0:x1]
    hp = sub - ndi.median_filter(sub, size=31)
    best = None
    maps = {}
    for R, k in cands:
        for fx in (0.0, 0.5):
            for fy in (0.0, 0.5):
                key = (R, fx, fy)
                K, n = kernel(R, fx, fy)
                if n >= min(hp.shape):
                    continue
                if key not in maps:
                    maps[key] = cv2.filter2D(hp, cv2.CV_32F, K, borderType=cv2.BORDER_CONSTANT)
                sc = maps[key]
                cy_map, cx_map = np.mgrid[0:sc.shape[0], 0:sc.shape[1]]
                cxs = cx_map + x0 - n // 2 + n / 2.0 + fx
                cys = cy_map + y0 - n // 2 + n / 2.0 + fy
                if k is None:
                    ok = (cxs >= box[0]) & (cxs <= box[2] + 1) & (cys >= box[1]) & (cys <= box[3] + 1)
                else:
                    tx, ty = W - k * R, H - k * R
                    ok = (np.abs(cxs - tx) <= 1.5) & (np.abs(cys - ty) <= 1.5)
                ok &= (cx_map >= n // 2) & (cx_map < sc.shape[1] - n // 2) & (cy_map >= n // 2) & (cy_map < sc.shape[0] - n // 2)
                if not ok.any():
                    continue
                v = np.where(ok, sc, -1e9)
                kk = int(np.argmax(v))
                yy, xx = np.unravel_index(kk, v.shape)
                c = float(v[yy, xx])
                if best is None or c > best[0]:
                    best = (c, R, float(cxs[yy, xx]), float(cys[yy, xx]))
    c, R, cx, cy = best
    # 정규 상관(별 알파 틀 ↔ 밝기 조각) — 평평한 바탕 위 별은 0.6 넘게, 결 위 가장자리 오탐은 낮게 나온다
    n = int(R * 2.4) * 2 + 9
    fx, fy = cx - int(cx), cy - int(cy)
    M = star_mask(R, n, 0.0, 0.0)
    xa, ya = int(round(cx - n / 2.0)), int(round(cy - n / 2.0))
    patch = L[max(0, ya):ya + n, max(0, xa):xa + n]
    ncc = float('nan')
    if patch.shape == M.shape:
        a = patch - patch.mean(); b = M - M.mean()
        ncc = float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-9))
    return (W, H, c, R, cx, cy, ncc)


def sheet(rows, out, per_row=8, S_=150):
    n = len(rows)
    nr = (n + per_row - 1) // per_row
    im = Image.new('RGB', (per_row * S_, nr * (S_ + 14)), 'white')
    d = ImageDraw.Draw(im)
    for k, (pid, W, H, c, R, cx, cy, ncc) in enumerate(rows):
        a = Image.open('tools/blind/png/%s.png' % pid).convert('RGB')
        hb = int(R * 2.4)
        cc = a.crop((int(cx) - hb, int(cy) - hb, int(cx) + hb, int(cy) + hb)).resize((S_ - 4, S_ - 4), Image.LANCZOS)
        X = (k % per_row) * S_; Y = (k // per_row) * (S_ + 14)
        im.paste(cc, (X + 2, Y + 14))
        d.text((X + 2, Y + 1), '%s %.0f' % (pid, c), fill=(200, 0, 0))
    im.save(out)


if __name__ == '__main__':
    args = sys.argv[1:]
    sh = None
    if args and args[0] == '--sheet':
        sh = args[1]; args = args[2:]
    pids = args or [os.path.basename(f)[:-4] for f in sorted(glob.glob('tools/blind/png/*.png'))]
    rows = []
    for p in pids:
        W, H, c, R, cx, cy, ncc = scan('tools/blind/png/%s.png' % p)
        rows.append((p, W, H, c, R, cx, cy, ncc))
    rows.sort(key=lambda r: -r[3])
    for r in rows:
        print('%-9s %4dx%-4d  c %5.1f  R %4.1f  (%6.1f, %6.1f)  ncc %5.2f' % r)
    if sh:
        sheet(rows, sh)

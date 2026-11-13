#!/usr/bin/env python3
"""zone3.py — Gemini 구역 편집 도우미(2026-11-13 · L12f) — crop 은 zone.py 그대로 · paste 는 zone2.py(닮음 변환)에 상자별 옮김 · --ident · --fit 을 더했다
  crop  <base.png> <dir> <name> x0 y0 x1 y1      → dir/crop_<name>.png · dir/up_<name>.png(긴 변 1024 — Gemini 에 올림) · dir/crop_<name>.json
  paste <base.png> <dir> <name> <gem_out.png> <out.png> "ax0,ay0,ax1,ay1[;…]" [thr] [--ident] [--R=14] [--fit="x0,y0,x1,y1[;…]"]
  · Gemini 가 세로로 더 그려 돌려준 경우(예: 1024x683 을 올렸는데 1024x765 가 옴) 크기를 억지로 맞추지 않고 같은 배율로 둔 채 정합한다.
  · --fit = 정합 때만 비워 둘 상자(붙일 상자가 커서 바깥 특징이 모자랄 때 더 작게 준다) · --ident = 정합 없이 같은 자리로 본다.
  · 전체 정합(닮음 변환) 뒤, 허용 상자마다 상자 바깥 띠(바뀌면 안 되는 곳)의 차이가 가장 작아지는 옮김(±R)을 따로 찾아 붙인다 — 상자 가장자리에서 선이 어긋나 보이는 것을 줄인다.
"""
import sys, json, cv2, numpy as np

def crop(base, d, name, x0, y0, x1, y1):
    im = cv2.imread(base); c = im[y0:y1, x0:x1]
    cv2.imwrite(f'{d}/crop_{name}.png', c)
    h, w = c.shape[:2]; s = 1024 / max(h, w)
    up = cv2.resize(c, (round(w * s), round(h * s)), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(f'{d}/up_{name}.png', up)
    json.dump({'box': [x0, y0, x1, y1], 'up': [up.shape[1], up.shape[0]]}, open(f'{d}/crop_{name}.json', 'w'))
    print('crop', c.shape[1], 'x', c.shape[0], '→ up', up.shape[1], 'x', up.shape[0])

def paste(base, d, name, gem, out, allow, thr=28, R=14, ident=False, fit=None):
    meta = json.load(open(f'{d}/crop_{name}.json')); x0, y0, x1, y1 = meta['box']
    im = cv2.imread(base); c = im[y0:y1, x0:x1].copy(); h, w = c.shape[:2]
    up = cv2.imread(f'{d}/up_{name}.png'); g = cv2.imread(gem)
    s = up.shape[1] / g.shape[1]                                  # 가로 배율만 맞춘다(세로로 더 그린 것은 그대로)
    g2 = cv2.resize(g, (up.shape[1], round(g.shape[0] * s)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4)
    sx = up.shape[1] / w; sy = up.shape[0] / h
    rects = [list(map(int, r.split(','))) for r in allow.split(';')]
    keep = np.full(up.shape[:2], 255, np.uint8)                   # 정합에 쓰는 곳 = fit 상자(없으면 허용 상자) 밖
    for ax0, ay0, ax1, ay1 in ([list(map(int, r.split(','))) for r in fit.split(';')] if fit else rects):
        keep[max(0, int((ay0 - y0) * sy) - 20):int((ay1 - y0) * sy) + 20, max(0, int((ax0 - x0) * sx) - 20):int((ax1 - x0) * sx) + 20] = 0
    orb = cv2.ORB_create(8000)
    k1, d1 = orb.detectAndCompute(cv2.cvtColor(up, cv2.COLOR_BGR2GRAY), keep)
    k2, d2 = orb.detectAndCompute(cv2.cvtColor(g2, cv2.COLOR_BGR2GRAY), None)
    M, inl, m = None, np.zeros(1), []
    if d1 is not None and d2 is not None and len(k1) >= 12:
        m = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d2, d1), key=lambda x: x.distance)[:800]
        src = np.float32([k2[x.queryIdx].pt for x in m]); dst = np.float32([k1[x.trainIdx].pt for x in m])
        if len(m) >= 8: M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=2)
    if ident or M is None: M = np.float32([[1, 0, 0], [0, 1, 0]]); inl = np.zeros(1)      # 정합할 바깥 특징이 거의 없을 때 — 같은 배율 · 같은 자리로 보고 상자별 옮김만 찾는다
    warp = cv2.warpAffine(g2, M, (up.shape[1], up.shape[0]), borderMode=cv2.BORDER_REFLECT)
    cv2.imwrite(f'{d}/warp_{name}.png', warp)
    res = c.copy(); tot = 0; mkall = np.zeros((h, w), np.uint8); offs = []
    upf = up.astype(np.float32)
    for ax0, ay0, ax1, ay1 in rects:
        rx0, ry0, rx1, ry1 = max(0, ax0 - x0), max(0, ay0 - y0), min(w, ax1 - x0), min(h, ay1 - y0)
        # 띠(업로드 배율) = 상자를 B 만큼 넓힌 것 − 상자
        B = 26; ux0, uy0, ux1, uy1 = int(rx0 * sx), int(ry0 * sy), int(rx1 * sx), int(ry1 * sy)
        band = np.zeros(up.shape[:2], bool); band[max(0, uy0 - B):uy1 + B, max(0, ux0 - B):ux1 + B] = True; band[uy0:uy1, ux0:ux1] = False
        best = None                                              # 반 배율에서 2픽셀 걸음으로 찾는다(빠르게)
        wh = cv2.resize(warp, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA).astype(np.float32); uh = cv2.resize(up, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA).astype(np.float32)
        bh = cv2.resize(band.astype(np.uint8), (uh.shape[1], uh.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
        ys, xs = np.where(bh); by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1; pad = R // 2 + 2
        whp = cv2.copyMakeBorder(wh, pad, pad, pad, pad, cv2.BORDER_REFLECT); ub = uh[by0:by1, bx0:bx1]; bb = bh[by0:by1, bx0:bx1]
        for dy in range(-(R // 2), R // 2 + 1):
            for dx in range(-(R // 2), R // 2 + 1):
                sh = whp[by0 + pad - dy:by1 + pad - dy, bx0 + pad - dx:bx1 + pad - dx]
                e = np.abs(sh - ub).max(axis=2)[bb].mean()
                if best is None or e < best[0]: best = (e, dx * 2, dy * 2)
        e, dx, dy = best; offs.append((dx, dy, round(float(e), 2)))
        sh = cv2.warpAffine(warp, np.float32([[1, 0, dx], [0, 1, dy]]), (up.shape[1], up.shape[0]), borderMode=cv2.BORDER_REFLECT)
        fit = cv2.resize(sh, (w, h), interpolation=cv2.INTER_AREA)
        diff = cv2.absdiff(fit, c).max(axis=2)
        al = np.zeros((h, w), np.uint8); al[ry0:ry1, rx0:rx1] = 255
        mk = ((diff > thr) & (al > 0)).astype(np.uint8) * 255
        mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)); mk = cv2.dilate(mk, np.ones((7, 7), np.uint8)); mk = cv2.bitwise_and(mk, al)
        a = cv2.GaussianBlur(mk.astype(np.float32) / 255, (0, 0), 2.0)[..., None]
        res = (fit.astype(np.float32) * a + res.astype(np.float32) * (1 - a)).astype(np.uint8)
        mkall |= mk; tot += int((mk > 0).sum())
    im[y0:y1, x0:x1] = res; cv2.imwrite(out, im); cv2.imwrite(f'{d}/mask_{name}.png', mkall)
    sc = 900 / w; both = np.hstack([cv2.resize(c, (900, round(h * sc)), interpolation=cv2.INTER_LANCZOS4), np.full((round(h * sc), 8, 3), 255, np.uint8), cv2.resize(res, (900, round(h * sc)), interpolation=cv2.INTER_LANCZOS4)])
    cv2.imwrite(f'{d}/cmp_{name}.png', both)
    print('M', np.round(M, 4).tolist(), 'inliers', int(inl.sum()), '/', len(m), '· 상자별 옮김', offs, '· 바뀐 픽셀', tot)

if __name__ == '__main__':
    a = sys.argv
    ident = '--ident' in a; a = [x for x in a if x != '--ident']
    R = 14; fit = None
    for x in list(a):
        if x.startswith('--R='): R = int(x[4:]); a.remove(x)
        if x.startswith('--fit='): fit = x[6:]; a.remove(x)
    if a[1] == 'crop': crop(a[2], a[3], a[4], *map(int, a[5:9]))
    elif a[1] == 'paste': paste(a[2], a[3], a[4], a[5], a[6], a[7], int(a[8]) if len(a) > 8 else 28, R=R, ident=ident, fit=fit)

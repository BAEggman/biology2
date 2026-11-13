#!/usr/bin/env python3
"""zalign.py — 구역 편집 결과를 「조각 전체가 다시 그려진」 경우에 맞춰 붙인다(2026-11-13 · L10b).
zone3.py 는 허용 상자 바깥의 특징으로 정합한다 — 조각 전체를 또렷하게 다시 그리게 하면(Gemini 가 틀을 조금 다르게 잡아 돌려준다) 바깥 특징이 없어 정합이 서지 않는다.
여기서는 조각 전체에서 특징을 찾아 닮음 변환(배율 + 옮김, 회전 없음)을 구하고, 허용 상자 안만 바꾼다(가장자리는 F 픽셀 번지게).
  python3 zalign.py <base.png> <dir> <name> <gem.png> <out.png> "ax0,ay0,ax1,ay1[;…]" [--F=6] [--M=s,tx,ty] [--key=x,y] [--tone=1]
  · dir/crop_<name>.json · dir/up_<name>.png 은 zone3.py crop 이 만든 것 · --M 은 손으로 잰 변환(올린 조각 좌표 = s × 돌려받은 그림 + (tx, ty)).
"""
import sys, json, cv2, numpy as np

def estimate(up, g):
    best = None
    dets = [cv2.ORB_create(12000)] + ([cv2.AKAZE_create()] if hasattr(cv2, 'AKAZE_create') else []) + ([cv2.SIFT_create()] if hasattr(cv2, 'SIFT_create') else [])
    for det in dets:
        k1, d1 = det.detectAndCompute(cv2.cvtColor(up, cv2.COLOR_BGR2GRAY), None)
        k2, d2 = det.detectAndCompute(cv2.cvtColor(g, cv2.COLOR_BGR2GRAY), None)
        if d1 is None or d2 is None: continue
        bf = cv2.BFMatcher(cv2.NORM_L2 if d1.dtype != np.uint8 else cv2.NORM_HAMMING)
        m = [a for a, b in bf.knnMatch(d2, d1, k=2) if a.distance < 0.8 * b.distance]
        if len(m) < 12: continue
        src = np.float32([k2[x.queryIdx].pt for x in m]); dst = np.float32([k1[x.trainIdx].pt for x in m])
        # 회전 없는 닮음 변환(s, tx, ty)을 RANSAC 으로
        rng = np.random.default_rng(0); bi = (0, None)
        for _ in range(4000):
            i, j = rng.choice(len(m), 2, replace=False)
            d2_ = np.linalg.norm(src[i] - src[j]); d1_ = np.linalg.norm(dst[i] - dst[j])
            if d2_ < 40: continue
            s = d1_ / d2_
            if not 0.6 < s < 1.6: continue
            t = dst[i] - s * src[i]
            err = np.linalg.norm(s * src + t - dst, axis=1); inl = err < 3.0
            if inl.sum() > bi[0]: bi = (int(inl.sum()), inl)
        if bi[1] is None: continue
        inl = bi[1]
        # 최소제곱으로 다듬기
        A = np.zeros((2 * inl.sum(), 3)); b = np.zeros(2 * inl.sum())
        A[0::2, 0] = src[inl, 0]; A[0::2, 1] = 1; b[0::2] = dst[inl, 0]
        A[1::2, 0] = src[inl, 1]; A[1::2, 2] = 1; b[1::2] = dst[inl, 1]
        s, tx, ty = np.linalg.lstsq(A, b, rcond=None)[0]
        if best is None or bi[0] > best[0]: best = (bi[0], len(m), float(s), float(tx), float(ty))
    return best

def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]; o = dict(x[2:].split('=') for x in sys.argv[1:] if x.startswith('--'))
    base, d, name, gem, out, allow = a
    F = int(o.get('F', 6))
    meta = json.load(open(f'{d}/crop_{name}.json')); x0, y0, x1, y1 = meta['box']
    im = cv2.imread(base); up = cv2.imread(f'{d}/up_{name}.png'); g = cv2.imread(gem)
    if 'M' in o: s, tx, ty = map(float, o['M'].split(',')); print('M(손)', s, tx, ty)
    else:
        e = estimate(up, g)
        if e is None: raise SystemExit('✕ 정합 실패')
        n, tot, s, tx, ty = e; print(f'M s={s:.4f} tx={tx:.1f} ty={ty:.1f} · 맞은 점 {n}/{tot}')
        if n < 25: raise SystemExit('✕ 맞은 점이 적다 — --M 으로 손으로 준다')
    k = (x1 - x0) / up.shape[1]                                    # 올린 조각 → 바탕 배율
    A = np.float32([[s * k, 0, x0 + tx * k], [0, s * k, y0 + ty * k]])
    H, W = im.shape[:2]
    warp = cv2.warpAffine(g, A, (W, H), flags=cv2.INTER_AREA)
    valid = cv2.warpAffine(np.full(g.shape[:2], 255, np.uint8), A, (W, H), flags=cv2.INTER_NEAREST) > 250
    valid = cv2.erode(valid.astype(np.uint8), np.ones((5, 5), np.uint8))
    mask = np.zeros((H, W), np.float32)
    for r in allow.split(';'):
        ax0, ay0, ax1, ay1 = map(int, r.split(',')); mask[ay0:ay1, ax0:ax1] = 1
    mask *= valid
    if F > 0:
        inner = cv2.erode(mask, np.ones((2 * F + 1, 2 * F + 1), np.uint8)); mask = cv2.GaussianBlur(inner, (0, 0), F / 2.0) * (mask > 0)
    if 'tone' in o:
        # --tone=1 : 평평한 바탕(하늘 · 땅)에서 바탕과 돌려받은 그림의 빛깔 차를 재어, 그 느린 차이만큼 돌려받은 그림을 고친다 — 네모 자국(2 ~ 6 단계 빛깔 차)을 없앤다.
        # 바탕이 두 빛(하늘 · 땅)이면 빛마다 따로 잰다(지평선 가까이에서 두 차이가 섞이면 땅 쪽에 옅은 네모가 남는다).
        wf = warp.astype(np.float32); bf_ = im.astype(np.float32)
        flat = lambda x: np.abs(x - cv2.GaussianBlur(x, (0, 0), 3)).max(axis=2) < 2.5
        bgm = flat(wf) & flat(bf_) & (bf_.min(axis=2) > 170) & (wf.min(axis=2) > 170) & (np.abs(bf_ - wf).max(axis=2) < 22) & (mask > 0)
        def field(m):
            m = m.astype(np.float32)
            num = cv2.GaussianBlur((bf_ - wf) * m[..., None], (0, 0), 30); den = cv2.GaussianBlur(m, (0, 0), 30)
            g0 = np.median((bf_ - wf)[m > 0].reshape(-1, 3), axis=0) if m.sum() > 50 else np.zeros(3, np.float32)      # 바탕이 드문 곳(큰 물건 속)은 전체 차이로 매끈하게 이어 간다
            return (num + g0[None, None, :] * 0.05) / (den + 0.05)[..., None], den
        corr, _ = field(bgm)
        Bv = bf_[..., 0][bgm]                                                    # 파랑 채널(BGR 의 0)로 하늘 · 땅을 가른다
        if Bv.size > 400 and np.percentile(Bv, 95) - np.percentile(Bv, 5) > 14:
            thr = (np.percentile(Bv, 95) + np.percentile(Bv, 5)) / 2
            hi = bgm & (bf_[..., 0] > thr); lo = bgm & (bf_[..., 0] <= thr)
            if hi.sum() > 200 and lo.sum() > 200:
                ch, _ = field(hi); cl, _ = field(lo)
                chi = np.median(wf[hi].reshape(-1, 3), axis=0); clo = np.median(wf[lo].reshape(-1, 3), axis=0)
                dh = np.abs(wf - chi[None, None, :]).max(axis=2); dl = np.abs(wf - clo[None, None, :]).max(axis=2)
                wh = np.clip((16 - dh) / 8.0, 0, 1)[..., None]; wl = np.clip((16 - dl) / 8.0, 0, 1)[..., None]      # 그 빛에 가까운 픽셀만 그 빛의 차이로
                corr = corr * (1 - np.maximum(wh, wl)) + ch * wh + cl * wl * (1 - wh)
                print('tone 두 빛: 하늘', np.round(np.median((bf_ - wf)[hi].reshape(-1, 3), axis=0)[::-1], 1), '· 땅', np.round(np.median((bf_ - wf)[lo].reshape(-1, 3), axis=0)[::-1], 1))
        warp = np.clip(wf + corr, 0, 255).astype(np.uint8)
        print('tone 고친 평균', np.round(corr[mask > 0].mean(axis=0)[::-1], 2), '· 평평한 바탕 픽셀', int(bgm.sum()))
    if 'key' in o:
        # --key=x,y : 돌려받은 그림의 (x, y) 둘레 빛(바탕색)과 같은 곳은 붙이지 않는다 — 바탕색이 조금 달라 네모 자국이 남을 때.
        # 그런 곳에 바탕의 옛(무른) 그림 자락이 남아 있으면 바탕색으로 덮는다.
        kx, ky = map(int, o['key'].split(',')); gb = np.median(g[ky - 6:ky + 7, kx - 6:kx + 7].reshape(-1, 3), axis=0)
        dist = np.abs(warp.astype(np.float32) - gb[None, None, :]).max(axis=2)
        # 바탕 = 상자 가장자리에서 바탕색으로 이어진 곳만(그림 속의 바탕색 닮은 빛 — 크림 벽 따위 — 은 그림으로 남긴다)
        nearbg = ((dist < 12) & (mask > 0)).astype(np.uint8)
        n_, lab_ = cv2.connectedComponents(nearbg, connectivity=4)
        rim = (cv2.dilate((mask > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & ~(cv2.erode((mask > 0).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
        ids = set(np.unique(lab_[rim & (nearbg > 0)])) - {0}
        outside_ = np.isin(lab_, list(ids))
        alpha = 1.0 - cv2.GaussianBlur(outside_.astype(np.float32), (0, 0), 1.2)
        alpha = np.clip((alpha - 0.15) / 0.7, 0, 1)
        ring = (cv2.dilate((mask > 0).astype(np.uint8), np.ones((25, 25), np.uint8)) > 0) & ~(mask > 0)
        bb = np.median(im[ring].reshape(-1, 3), axis=0)                      # 바탕의 바탕색(상자 둘레)
        far = np.abs(im.astype(np.float32) - bb[None, None, :]).max(axis=2) > 6
        far = cv2.dilate(far.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0                   # 옛 그림 가장자리의 번진 테까지
        im2 = im.copy(); im2[(mask > 0.5) & far] = bb.astype(np.uint8)          # 상자 안의 옛 그림은 모두 지운다(새 그림 테두리에 옛 빛이 비치지 않게)
        im = im2; mask = mask * alpha
        print('key 돌려받은 바탕색', gb.astype(int)[::-1], '· 바탕의 바탕색', bb.astype(int)[::-1])
    res = im.astype(np.float32) * (1 - mask[..., None]) + warp.astype(np.float32) * mask[..., None]
    cv2.imwrite(out, np.clip(res + 0.5, 0, 255).astype(np.uint8))
    print('ok', out, '바뀐 픽셀', int((mask > 0.5).sum()))
if __name__ == '__main__': main()

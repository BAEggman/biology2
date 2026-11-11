#!/usr/bin/env python3
"""zone2.py — zone.py paste 의 변형: Gemini 결과의 가로세로비가 올린 조각과 달라도(틀을 늘려 그림) 찌그러뜨리지 않고
닮음 변환(회전 · 크기 · 이동)으로 올린 조각 틀에 맞춘다. 쓰는 법은 zone.py paste 와 같다."""
import sys, json, cv2, numpy as np
def paste(base, d, name, gem, out, allow, thr=28):
    meta = json.load(open(f'{d}/crop_{name}.json')); x0, y0, x1, y1 = meta['box']
    im = cv2.imread(base); c = im[y0:y1, x0:x1].copy(); h, w = c.shape[:2]
    up = cv2.imread(f'{d}/up_{name}.png'); g = cv2.imread(gem)
    s0 = up.shape[1] / g.shape[1]
    g2 = cv2.resize(g, (round(g.shape[1] * s0), round(g.shape[0] * s0)), interpolation=cv2.INTER_AREA)
    sx = up.shape[1] / w; sy = up.shape[0] / h
    rects = [list(map(int, r.split(','))) for r in allow.split(';')]
    keep = np.full(up.shape[:2], 255, np.uint8)
    for ax0, ay0, ax1, ay1 in rects:
        keep[max(0, int((ay0 - y0) * sy) - 20):int((ay1 - y0) * sy) + 20, max(0, int((ax0 - x0) * sx) - 20):int((ax1 - x0) * sx) + 20] = 0
    orb = cv2.ORB_create(10000)
    k1, d1 = orb.detectAndCompute(cv2.cvtColor(up, cv2.COLOR_BGR2GRAY), keep)
    k2, d2 = orb.detectAndCompute(cv2.cvtColor(g2, cv2.COLOR_BGR2GRAY), None)
    m = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d2, d1), key=lambda x: x.distance)[:1000]
    src = np.float32([k2[x.queryIdx].pt for x in m]); dst = np.float32([k1[x.trainIdx].pt for x in m])
    M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=2)
    if inl is None or int(inl.sum()) < 30 or not (0.4 < abs(M[0, 0]) < 2.5) or abs(M[0, 1]) > 0.05:
        k1, d1 = orb.detectAndCompute(cv2.cvtColor(up, cv2.COLOR_BGR2GRAY), None)
        m = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d2, d1), key=lambda x: x.distance)[:1500]
        src = np.float32([k2[x.queryIdx].pt for x in m]); dst = np.float32([k1[x.trainIdx].pt for x in m])
        M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=2.5)
        print('· 다시 맞춤(가림 없이)')
    warp = cv2.warpAffine(g2, M, (up.shape[1], up.shape[0]), borderMode=cv2.BORDER_REFLECT)
    fit = cv2.resize(warp, (w, h), interpolation=cv2.INTER_AREA); cv2.imwrite(f'{d}/fit_{name}.png', fit)
    diff = cv2.absdiff(fit, c).max(axis=2)
    allowm = np.zeros((h, w), np.uint8)
    for ax0, ay0, ax1, ay1 in rects: allowm[max(0, ay0 - y0):max(0, ay1 - y0), max(0, ax0 - x0):max(0, ax1 - x0)] = 255
    mk = ((diff > thr) & (allowm > 0)).astype(np.uint8) * 255
    mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)); mk = cv2.dilate(mk, np.ones((7, 7), np.uint8))
    mk = cv2.bitwise_and(mk, allowm)
    a = cv2.GaussianBlur(mk.astype(np.float32) / 255, (0, 0), 2.0)[..., None]
    res = (fit.astype(np.float32) * a + c.astype(np.float32) * (1 - a)).astype(np.uint8)
    im[y0:y1, x0:x1] = res; cv2.imwrite(out, im); cv2.imwrite(f'{d}/mask_{name}.png', mk)
    s = 700 / w; both = np.hstack([cv2.resize(c, (700, round(h * s))), np.full((round(h * s), 8, 3), 255, np.uint8), cv2.resize(res, (700, round(h * s)))])
    cv2.imwrite(f'{d}/cmp_{name}.png', both)
    print('M', np.round(M, 4).tolist(), 'inliers', int(inl.sum()), '/', len(m), '· 바뀐 픽셀', int((mk > 0).sum()))
if __name__ == '__main__':
    a = sys.argv
    paste(a[2], a[3], a[4], a[5], a[6], a[7], int(a[8]) if len(a) > 8 else 28)

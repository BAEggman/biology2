#!/usr/bin/env python3
# deckfill.py <in.png> <out.png> "x,y;x,y;..." [feather] — polygon 안의 얼룩(그림자 · 잔상)을 지우고 바닥 빛깔(둘레 띠에서 평면 맞춤)로 채운다.
#   진한 선(널빤지 금)은 남긴다: 국소 밝기의 0.7 배보다 어두운 화소 = 선.
import sys, cv2, numpy as np
src, dst, poly = sys.argv[1:4]; fe = float(sys.argv[4]) if len(sys.argv) > 4 else 2.5
im = cv2.imread(src).astype(np.float32)
pts = np.array([[int(v) for v in p.split(',')] for p in poly.split(';')], np.int32)
bx, by, bw, bh = cv2.boundingRect(pts); P = 40
x0, y0, x1, y1 = max(0, bx - P), max(0, by - P), min(im.shape[1], bx + bw + P), min(im.shape[0], by + bh + P)
roi = im[y0:y1, x0:x1].copy(); H, W = roi.shape[:2]
m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [pts - [x0, y0]], 255)
ring = cv2.dilate(m, np.ones((41, 41), np.uint8)) & ~cv2.dilate(m, np.ones((9, 9), np.uint8))
lum = roi.mean(axis=2)
ref = np.median(roi[ring > 0], axis=0)
dist = np.abs(roi - ref[None, None, :]).max(axis=2)
good = (ring > 0) & (dist < 22)
yy, xx = np.nonzero(good)
A = np.c_[xx, yy, np.ones_like(xx)].astype(np.float64)
field = np.zeros_like(roi)
gx, gy = np.meshgrid(np.arange(W), np.arange(H))
for c in range(3):
    coef, *_ = np.linalg.lstsq(A, roi[yy, xx, c].astype(np.float64), rcond=None)
    field[..., c] = coef[0] * gx + coef[1] * gy + coef[2]
ill = cv2.GaussianBlur(cv2.medianBlur(roi.astype(np.uint8), 15).astype(np.float32), (0, 0), 2)
LT = float(sys.argv[5]) if len(sys.argv) > 5 else 0.72
line = lum < LT * ill.mean(axis=2)
rng = np.random.default_rng(7); noise = rng.normal(0, 1.6, (H, W, 1)).astype(np.float32)
out = field + noise
corr = np.clip(roi * (field / np.maximum(ill, 1)), 0, 255)
out[line] = corr[line]
a = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), fe)[..., None]
roi = np.clip(out, 0, 255) * a + roi * (1 - a)
im[y0:y1, x0:x1] = roi
cv2.imwrite(dst, im.astype(np.uint8))
print('ref', np.round(ref, 1), 'good px', int(good.sum()), 'line px in poly', int((line & (m > 0)).sum()))

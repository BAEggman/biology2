#!/usr/bin/env python3
# colormatch.py <up.png> <gem.png> <out.png> — Gemini 가 돌려준 그림의 전체 빛깔(채널별 a·x+b)을 올린 오림(up)에 맞춘다(2026-11-15 · L13f).
#  구역 편집에서 벽 · 창 안쪽 같은 넓은 맨바닥의 빛깔이 살짝 달라 붙인 상자 둘레에 네모 얼룩이 보일 때 — 바뀌지 않은 곳(둘이 비슷한 픽셀)만으로 맞춘다.
import sys, numpy as np, cv2
up, gem, out = sys.argv[1:4]
u = cv2.imread(up).astype(np.float32); g0 = cv2.imread(gem); g = cv2.resize(g0, (u.shape[1], u.shape[0]), interpolation=cv2.INTER_AREA).astype(np.float32)
m = np.abs(u - g).max(axis=2) < 40
m = cv2.erode(m.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
coef = []
for c in range(3):
    x, y = g[..., c][m], u[..., c][m]
    A = np.vstack([x, np.ones_like(x)]).T; a, b = np.linalg.lstsq(A, y, rcond=None)[0]; coef.append((a, b))
o = g0.astype(np.float32)
for c, (a, b) in enumerate(coef): o[..., c] = o[..., c] * a + b
cv2.imwrite(out, np.clip(o, 0, 255).astype(np.uint8))
print('coef', [(round(float(a), 3), round(float(b), 1)) for a, b in coef], 'px', int(m.sum()))

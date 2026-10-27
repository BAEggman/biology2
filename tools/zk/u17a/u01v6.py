# u01v6.py — s17u01 cur0 → cur1 (손질): ① 창 안 털 — 푸른 끝 · 흰 점 지우고 짧은 검은 벨벳 털 술 ② 호스 가로 이음선(y≈597) 세로 섞기 ③ (가시 공은 그대로)
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation, binary_fill_holes
A = np.asarray(Image.open('cur0.png').convert('RGB')).astype(float); C = A.copy(); H, W, _ = A.shape
rng = np.random.default_rng(31)
R, G, B = A[..., 0], A[..., 1], A[..., 2]; lum = A.mean(axis=2)
# ① 털 덩이 다각형(창 안 · 위 가장자리가 기운 띠)
poly = [(402, 302), (420, 286), (446, 270), (470, 266), (490, 267), (490, 300), (470, 316), (430, 338), (402, 350)]
pm = Image.new('L', (W, H), 0); ImageDraw.Draw(pm).polygon(poly, fill=255); pm = np.asarray(pm) > 0
satA = (A.max(axis=2) - A.min(axis=2)) / (A.max(axis=2) + 1e-6)
near = binary_dilation(lum < 80, iterations=3)
bad = pm & near & (((B - R > 12) & (lum > 85)) | ((lum > 150) & (satA < 0.16)))
bad = binary_dilation(bad, iterations=1) & pm & ~((R - B > 25) & (lum > 120))
velvet = np.array([38, 40, 46], float)
nz = gaussian_filter(rng.random((H, W)), 1.0)
for c in range(3): C[..., c][bad] = velvet[c] + (nz[bad] - 0.5) * 18
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img)
def top_y(x):
    pts = [(402, 302), (420, 286), (446, 270), (470, 266), (490, 267)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return 300
for x in np.arange(403, 489, 1.6):
    ty = top_y(x); L = 4 + rng.random() * 4; lean = rng.normal(0.6, 0.6)
    d.line([(x, ty + 5), (x + lean, ty - L * 0.6)], fill=(26, 28, 32), width=1)
for x in np.arange(404, 488, 4.5):
    ty = top_y(x); d.line([(x, ty + 1), (x + 0.4, ty - 2)], fill=(92, 96, 104), width=1)   # 끝의 옅은 광
C = np.asarray(img).astype(float)
# ② 호스 이음선(y≈593 의 계단 · x 236~392): 열마다 계단 높이를 재어 위쪽 22행을 0 → 계단만큼 선형으로 올린다
xa, xb = 236, 392
step = C[595:599, xa:xb].mean(axis=0) - C[588:592, xa:xb].mean(axis=0)          # (w,3)
step = np.stack([gaussian_filter(step[:, c], 6) for c in range(3)], axis=1)
edge = np.ones(xb - xa); edge[:12] = np.linspace(0, 1, 12); edge[-12:] = np.linspace(1, 0, 12)
for k, y in enumerate(range(571, 594)):
    t = (k + 1) / 23
    C[y, xa:xb] += step * t * edge[:, None]
# ③ 가시 공은 그대로(줄이면 가시가 빠지고 물결에 회색 테가 남는다 — 시도 후 되돌림)
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); img.save('cur1.png')
img.crop((380, 230, 560, 350)).resize((720, 480), Image.LANCZOS).save('v6_win.png')
img.crop((60, 520, 420, 820)).resize((720, 600), Image.LANCZOS).save('v6_hose.png')
img.crop((560, 560, 900, 820)).resize((680, 520), Image.LANCZOS).save('v6_balls.png'); print('cur1 saved')

#!/usr/bin/env python3
"""touch_h7.py — s45u02 v9 ⑦ 행 11: 흰 눈부심 빛살의 「회색 테」를 걷는다 — touch_b(v2)의 빛살 양옆이 하늘보다 20 남짓 어두워
독자들이 여러 판에 걸쳐 「이어 붙인 흰 기둥 · 반투명 관」으로 짚었다(b139 채점 확인). 통로 안 무채색 화소가 cur7 하늘보다 어두우면 하늘 값으로 올리고
(당근 잎 · 금빛 물결 · 빛띠 · 망토처럼 빛깔 있는 화소는 그대로), 가운데에 부드러운 흰 빛무리를 더한다.
사용: touch_h7.py in.png cur7.png out.png"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, sky, dst = sys.argv[1:4]
img = Image.open(src).convert('RGB'); W, H = img.size
A = np.asarray(img).astype(float); C7 = np.asarray(Image.open(sky).convert('RGB')).astype(float)
yy, xx = np.mgrid[0:H, 0:W]
(x0, y0), (x1, y1) = (1078.0, 40.0), (1031.0, 528.0)
k = (x1 - x0) / (y1 - y0)
xc = x0 + k * (yy - y0)
corr = (np.abs(xx - xc) <= 24) & (yy >= 12) & (yy <= 520)
sat = A.max(axis=2) - A.min(axis=2)
lum = A.mean(axis=2); lum7 = C7.mean(axis=2)
# cur7 에서 하늘이던 곳(무채색 · 밝음)이고 지금 화소가 빛깔 있는 물건(물결 · 빛띠 · 잎 · 망토 — 채도 45 넘음)이 아니면, 하늘보다 어두운 몫만 들어 올린다
sky7 = ((C7.max(axis=2) - C7.min(axis=2)) < 40) & (C7.mean(axis=2) > 200)   # 아래쪽 하늘은 크림빛(채도 24 남짓)
fix = corr & sky7 & (sat < 45) & (lum < lum7 - 0.5)
A[fix] = np.maximum(A[fix], C7[fix])
print('회색 테 걷음', int(fix.sum()))
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
# 부드러운 흰 빛무리(눈부심) — 빛깔은 한 가지라 짙기(알파)만 따로 그려 흐린다
#   (RGBA 를 줄이거나 흐리면 투명 화소의 검은 RGB 가 가장자리에 섞여 테가 어두워진다 — touch_b 의 회색 테가 바로 이것)
SS = 2
mask = Image.new('L', (W * SS, H * SS), 0); d = ImageDraw.Draw(mask)
for i in range(60):
    t0, t1 = i / 60, (i + 1) / 60
    ya, yb = 19 + (515 - 19) * t0, 19 + (515 - 19) * t1
    xa, xb = x0 + k * (ya - y0), x0 + k * (yb - y0)
    wa = 18 + 16 * t0; wb = 18 + 16 * t1
    al = int(70 + 60 * t1)
    d.polygon([((xa - wa / 2) * SS, ya * SS), ((xa + wa / 2) * SS, ya * SS), ((xb + wb / 2) * SS, yb * SS), ((xb - wb / 2) * SS, yb * SS)], fill=al)
ga = np.asarray(mask.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(5.0))).astype(float)[..., None] / 255.0
Ac = np.asarray(img).astype(float); satc = Ac.max(axis=2) - Ac.min(axis=2)
ga = ga * np.where(satc[..., None] > 30, 0.35, 1.0)
out = Ac * (1 - ga) + np.array([255, 253, 242.0]) * ga
Image.fromarray(np.clip(out, 0, 255).astype('uint8')).save(dst)
print('ok', dst)

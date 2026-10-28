#!/usr/bin/env python3
"""paste_d2.py — s45u02: Gemini D2(실 위 헤엄이 · 방울) 조각을 cur5 위에 「헤엄이 · 채찍 꼬리 · 흰 방울」 화소만 붙여 cur6.
 (diff 통째 붙이기는 Gemini 가 어둡게 다시 칠한 진홍 안개까지 끌고 와 네모 얼룩을 남겼다 — 그래서 빛깔로 고른다)"""
import sys, os, json, numpy as np, cv2
from PIL import Image
from scipy.ndimage import binary_dilation, gaussian_filter
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
cur = np.asarray(Image.open('cur5.png').convert('RGB')).astype(np.float32)
cj = json.load(open('crop_D2.json')); bx0, by0, bx1, by1 = [v * 2 for v in cj['box']]
C = cur[by0:by1, bx0:bx1]; H, W = C.shape[:2]
F = np.asarray(Image.open('fit_D2.png').convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
r, g, b = F[..., 0], F[..., 1], F[..., 2]
L = F.mean(axis=2); sat = F.max(axis=2) - F.min(axis=2)
diff = np.abs(F - C).mean(axis=2)
hsv = cv2.cvtColor(np.clip(F, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)   # H 0~180
hue = hsv[..., 0] * 2; sv = hsv[..., 1] / 255
olive = (hue >= 38) & (hue <= 75) & (sv > 0.3) & (L > 45) & (L < 175) & (diff > 18)
dark = (L < 75) & (diff > 25)
tails = dark & binary_dilation(olive, iterations=5)
white = (L > 212) & (sat < 45) & (diff > 25)
zone = np.zeros((H, W), bool); zone[0:205, 60:520] = True
# v2(b131 뒤): 무더기는 보라 · 파랑 띠(실 높이 x ≤ 1690)와 빨강 띠(x ≥ 1930)에만 — 주황 · 노랑에 번진 무더기를 뺀다
# (청록 · 주황의 몇 마리 · 작은 방울은 touch_b 가 띠 한가운데에 따로 그린다)
xs = np.arange(W)[None, :] + bx0
zone &= (xs <= 1690) | (xs >= 1930)
M = (binary_dilation(olive, iterations=1) | binary_dilation(tails, iterations=1) | binary_dilation(white, iterations=2)) & zone
Mf = np.clip(gaussian_filter(M.astype(float), 0.7) * 1.5, 0, 1)[..., None]
out = cur.copy(); out[by0:by1, bx0:bx1] = C * (1 - Mf) + F * Mf
Image.fromarray(np.clip(out, 0, 255).astype('uint8')).save('cur6.png')
print('cur6 px', int(M.sum()))

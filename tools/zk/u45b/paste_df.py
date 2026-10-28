#!/usr/bin/env python3
"""paste_df.py — s45u02 v2: Gemini D3(진홍 안개 속 둘 = 엽록소 d · f — 자매와 같은 몸 · 꼬리 · 액자 머리 속이 진홍) 를 cur5b 위로.
 Gemini 가 조각을 확대해 돌려줘 ORB 정합이 안 된다 → 두 은빛 구슬 중심으로 닮음 변환(배율 + 이동)을 잡아 옮기고,
 옛 둘 · 새 둘의 「안개가 아닌 화소」 합집합만 붙인다(무지개 띠 위로는 안 넘친다)."""
import sys, os, numpy as np, cv2
from PIL import Image
from scipy.ndimage import binary_dilation, binary_fill_holes, gaussian_filter
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
C = np.asarray(Image.open('cur5b.png').convert('RGB')).astype(np.float32); H, W, _ = C.shape
G = np.asarray(Image.open('out_D3.png').convert('RGB'))
g1, g2 = np.array([169.4, 297.5]), np.array([391.1, 337.8])      # Gemini 구슬
c1, c2 = np.array([1828.0, 453.0]), np.array([1912.0, 467.0])    # 캔버스 옛 구슬
s = np.linalg.norm(c2 - c1) / np.linalg.norm(g2 - g1)
t = c1 - s * g1
M = np.array([[s, 0, t[0]], [0, s, t[1]]], np.float32)
Wg = cv2.warpAffine(G, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0)).astype(np.float32)
valid = cv2.warpAffine(np.ones(G.shape[:2], np.uint8), M, (W, H), flags=cv2.INTER_NEAREST) > 0
def nonhaze(A):
    hsv = cv2.cvtColor(np.clip(A, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    h, sv, v = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
    crimson = ((h > 330) | (h < 12)) & (sv > 0.28)
    return ~crimson
R = np.zeros((H, W), bool); R[400:640, 1790:1975] = True
# 무지개 윗선(캔버스에서 붉은 띠의 윗모서리 — 열마다 처음으로 채도 높은 빨강 · 주황이 나오는 곳)
hsvC = cv2.cvtColor(np.clip(C, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
top = np.full(W, H, int)
for x in range(1790, 1975):
    col = hsvC[400:700, x]
    hh, ss, vv = col[:, 0] * 2, col[:, 1] / 255, col[:, 2] / 255
    idx = np.where((((hh < 30) | (hh > 345)) & (ss > 0.45) & (vv > 0.7)))[0]
    if len(idx): top[x] = 400 + idx[0]
yy = np.arange(H)[:, None]; above = yy < (top[None, :] - 2)
M_new = nonhaze(Wg) & valid & R & above
M_old = nonhaze(C) & R & above
heads = np.zeros((H, W), bool)
for (cx, cy) in (c1, c2):
    heads[int(cy - 32):int(cy + 32), int(cx - 33):int(cx + 33)] = True     # 액자 머리 통째(속의 진홍 빛까지)
Mk = (binary_fill_holes(binary_dilation(M_new | M_old, iterations=4)) | heads) & valid & R & above
Mf = np.clip(gaussian_filter(Mk.astype(float), 2.0) * 1.3, 0, 1)[..., None]
out = C * (1 - Mf) + Wg * Mf
Image.fromarray(np.clip(out, 0, 255).astype('uint8')).save('cur5c.png')
print('scale', round(float(s), 4), 'px', int(Mk.sum()))

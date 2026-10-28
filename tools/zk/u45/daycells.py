#!/usr/bin/env python3
"""daycells.py — cur19 → cur20: C₄ 바닥 흰 번짐 지움(행 밀기로 콩팥을 펴던 시도는 계단 윤곽이 나 버림 → 낮 공변세포는 Gemini G1)"""
import sys, os, numpy as np, cv2
from PIL import Image
from scipy.ndimage import binary_dilation, binary_fill_holes, label, binary_erosion
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
C = np.asarray(Image.open('cur19.png').convert('RGB')).astype(np.uint8).copy(); H, W, _ = C.shape
B0 = np.asarray(Image.open('cur18.png').convert('RGB')).astype(np.uint8)   # 위층 원본(밤 칸은 v2b 그대로)
def sprite(x0, y0, x1, y1):
    s = B0[y0:y1, x0:x1].astype(int); R, G, Bb = s[..., 0], s[..., 1], s[..., 2]; L = s.mean(axis=2)
    green = (G > R + 8) & (G > Bb + 12) & (L > 70)
    lab, n = label(green); big = max(range(1, n + 1), key=lambda i: (lab == i).sum()); body = lab == big
    body = binary_fill_holes(binary_dilation(body, iterations=1))
    ring = binary_dilation(body, iterations=3) & (L < 62)
    m = binary_fill_holes(body | ring)
    return s.astype(np.uint8), m
def straighten(spr, m, inner):   # inner = 'right' (왼 콩팥) / 'left'
    h, w = m.shape; out = np.zeros_like(spr); om = np.zeros_like(m)
    rows = [y for y in range(h) if m[y].any()]
    edge = {y: (np.where(m[y])[0].max() if inner == 'right' else np.where(m[y])[0].min()) for y in rows}
    X = max(edge.values()) if inner == 'right' else min(edge.values())
    for y in rows:
        sh = X - edge[y]
        xs = np.where(m[y])[0]
        for x in xs:
            nx = x + sh
            if 0 <= nx < w: out[y, nx] = spr[y, x]; om[y, nx] = True
    # 이동으로 생긴 바깥 빈틈(같은 행 안쪽) 채우기
    for y in rows:
        xs = np.where(om[y])[0]
        if len(xs): 
            a, b = xs.min(), xs.max()
            for x in range(a, b + 1):
                if not om[y, x]: out[y, x] = out[y, x - 1]; om[y, x] = True
    return out, om
def squeeze(spr, m, f):
    h, w = m.shape; nw = max(4, int(round(w * f)))
    s2 = cv2.resize(spr, (nw, h), interpolation=cv2.INTER_AREA); m2 = cv2.resize(m.astype(np.uint8) * 255, (nw, h), interpolation=cv2.INTER_AREA) > 127
    return s2, m2
# C₄ 바닥 오른쪽 흰 번짐(1506~1530 · 748~768) → 왼쪽 바닥 결로
s = C[746:770, 1504:1532].astype(int)
mw = np.zeros((H, W), np.uint8); mw[746:770, 1504:1532] = ((s.min(axis=2) > 196) | ((s.mean(axis=2) > 175) & (np.abs(s[..., 0] - s[..., 2]) < 18))).astype(np.uint8)
mw = binary_dilation(mw, iterations=2).astype(np.uint8)
C = cv2.inpaint(C, mw, 4, cv2.INPAINT_TELEA)
Image.fromarray(C).save('cur20.png')
Image.fromarray(C).crop((1880, 520, 1980, 670)).resize((400, 600), Image.LANCZOS).save('v20_day.png')
Image.fromarray(C).crop((1440, 730, 1540, 780)).resize((500, 250), Image.LANCZOS).save('v20_floor.png')
print('cur20 saved')

#!/usr/bin/env python3
"""zpaste.py — Gemini 조각(fit, crop 크기로 정합된 것)을 cur 위에 붙인다. 바뀐 화소만(diff) 또는 사각형 통째로(rect).
사용: zpaste.py cur.png crop_NAME.json fit_NAME.png out.png [--own x0,y0,x1,y1 (조각 2배 좌표 · 여럿은 ; 로)] [--mode diff|rect]
      [--thr 14] [--dil 3] [--feather 1.5] [--keep x0,y0,x1,y1;… (원본 그대로 둘 사각형)]
조각 좌표 = 2배 캔버스 좌표 - crop box*2. 출력: 붙인 화소 수."""
import sys, json, argparse, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation, binary_fill_holes
ap = argparse.ArgumentParser(); ap.add_argument('cur'); ap.add_argument('cj'); ap.add_argument('fit'); ap.add_argument('out')
ap.add_argument('--own', default=''); ap.add_argument('--mode', default='diff'); ap.add_argument('--thr', type=float, default=14)
ap.add_argument('--dil', type=int, default=3); ap.add_argument('--feather', type=float, default=1.5); ap.add_argument('--keep', default='')
a = ap.parse_args()
B = np.asarray(Image.open(a.cur).convert('RGB')).astype(float)
cj = json.load(open(a.cj)); S = cj['scale']; bx0, by0, bx1, by1 = [v * S for v in cj['box']]
F = np.asarray(Image.open(a.fit).convert('RGB').resize((bx1 - bx0, by1 - by0), Image.LANCZOS)).astype(float)
C0 = B[by0:by1, bx0:bx1]
h, w = F.shape[:2]
def rects(s):
    out = []
    for part in [p for p in s.split(';') if p.strip()]:
        out.append([int(round(float(v))) for v in part.split(',')])
    return out
own = rects(a.own) or [[0, 0, w, h]]
R = np.zeros((h, w), bool)
for (x0, y0, x1, y1) in own: R[max(0, y0):min(h, y1), max(0, x0):min(w, x1)] = True
if a.mode == 'rect':
    M = R.astype(float)
else:
    d = gaussian_filter(np.abs(C0 - F).mean(axis=2), 1.0)
    m = (d > a.thr) & R
    m = binary_dilation(m, iterations=a.dil); m = binary_fill_holes(m) & R
    M = m.astype(float)
for (x0, y0, x1, y1) in rects(a.keep): M[max(0, y0):min(h, y1), max(0, x0):min(w, x1)] = 0
M = gaussian_filter(M, a.feather); M = np.clip(M * 1.3, 0, 1)
out = B.copy(); out[by0:by1, bx0:bx1] = C0 * (1 - M[..., None]) + F * M[..., None]
Image.fromarray(np.clip(out, 0, 255).astype('uint8')).save(a.out)
print('pasted', cj['name'], 'px', int((M > 0.5).sum()), 'of', h * w)

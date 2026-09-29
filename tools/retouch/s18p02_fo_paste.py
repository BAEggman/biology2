#!/usr/bin/env python3
"""s18p02 — 개념 논리 m 1: 난원공 창에서 물이 **바닥으로** 쏟아지던 것 → 청록 탱크(RA · 가득) → 창 너머 물길 → 노란 탱크(LA · 반쯤).
조각(원본 x 20..500 · y 60..380)을 1200×800 으로 키워 제미나이에 주고 받은 1024×682 를 480×320 으로 줄여, 바뀐 곳만(σ2 밝기 차 > 12 · 닫기 3 · 메움 ·
넓힘 4 · σ2 섞음 · 조각 가장자리 10px 제외) 붙인다. 결과 오른쪽 아래 구석의 반짝이 표식(조각 x ≥ 420 · y ≥ 250)은 마스크에서 뺀다.
바뀌지 않은 둘레에서 잰 톤 차이를 σ20 으로 번져 맞춘다.
사용: python3 s18p02_fo_paste.py ORIG.png CROP_RESULT.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
op, cp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
X0, Y0, CW, CH = 20, 60, 480, 320
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(cp).convert('RGB').resize((CW, CH), Image.LANCZOS)).astype(np.float64)
Oc = O[Y0:Y0 + CH, X0:X0 + CW]
d = ndi.gaussian_filter(np.abs(V - Oc).mean(axis=2), 2.0)
m = d > 12
m = ndi.binary_closing(m, iterations=3)
m = ndi.binary_fill_holes(m)
m = ndi.binary_dilation(m, iterations=4)
m[:10, :] = m[-10:, :] = False; m[:, :10] = m[:, -10:] = False
m[250:, 420:] = False
w = ndi.gaussian_filter(m.astype(float), 2.0)
calm = (d < 6) & ~ndi.binary_dilation(m, iterations=4)
corr = np.zeros_like(V)
for k in range(3):
    num = ndi.gaussian_filter((Oc[..., k] - V[..., k]) * calm, 20)
    den = ndi.gaussian_filter(calm.astype(float), 20)
    corr[..., k] = np.where(den > 1e-3, num / np.maximum(den, 1e-6), 0)
out = O.copy()
out[Y0:Y0 + CH, X0:X0 + CW] = Oc * (1 - w[..., None]) + (V + corr) * w[..., None]
print('mask px', int(m.sum()), 'tone corr', corr[m].mean(axis=0).round(1))
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print('saved', dst)

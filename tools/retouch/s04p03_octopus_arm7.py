#!/usr/bin/env python3
"""s04p03 — 문어 팔 아홉 → 여덟. 오른쪽 아래, 다른 팔(6번) 뒤에서 나와 바닥에 누운 7번 팔을 지운다.
뿌리가 6번 팔 뒤에 숨어 있어 몸통 윤곽을 새로 그을 필요가 없다. 지운 자리는 열마다 위·아래 바닥 화소
(윤곽을 피해 2–4px 바깥의 중앙값)를 잇는 선형 보간 → 가면 안만 가로 가우스(σ1.2)로 세로 줄무늬를 누그러뜨리고
원래 바닥 결만큼 잡음. 세로 줄눈은 그대로 이어진다. 새 획 없음. (해부 감사 2026-09-28 batch_00)
사용: python3 tools/retouch/s04p03_octopus_arm7.py <src.png> <out.png>"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter1d
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.float64).copy()
poly = [(677,786),(684,790),(690,793),(700,794),(708,793),(711,790),(716,788),(719,786),(720,781),(721,776),
        (724,774),(729,775),(732,778),(733,784),(732,791),(730,796),(727,800),(723,803),(718,806),
        (712,808),(704,810),(690,811),(680,810),(677,808)]
m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon(poly, fill=255)
M = np.asarray(m) > 0
b = a.copy()
for x in range(M.shape[1]):
    ys = np.nonzero(M[:, x])[0]
    if len(ys) == 0: continue
    y0, y1 = ys.min(), ys.max()
    top = np.median(a[y0-4:y0-1, x], axis=0); bot = np.median(a[y1+2:y1+5, x], axis=0)
    for y in ys:
        t = (y - y0 + 1) / (y1 - y0 + 2)
        b[y, x] = (1 - t) * top + t * bot
sm = gaussian_filter1d(b, 1.2, axis=1)
b[M] = sm[M]
rng = np.random.default_rng(7)
b[M] += rng.normal(0, 1.8, (int(M.sum()), 3))
Image.fromarray(b.clip(0, 255).astype(np.uint8)).save(out)
print('erased px', int(M.sum()))

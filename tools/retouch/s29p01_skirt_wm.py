#!/usr/bin/env python3
"""s29p01 — 개념 논리 M(뒤의 여행자는 앞 장비 전부 — 포유류는 양막류·사지동물): 마지막(털옷) 여행자에 알 상자·사지 보호대가 없던 것 →
제미나이 같은 대화 v2(털옷에 더해 턱 보호대 · 무릎·정강이 보호대 · 왼손에 알 상자 · 문지기가 우유병을 내밂)를 쓰고,
설치본 때부터 있던 문지기 치마 위 반짝이 표식(x 893..936 · y 866..918)만 치마 빛깔로 덮음 —
줄마다 좌우 검은 윤곽(lum < 95) 사이를 치마 안쪽으로 보고, 위아래 ±7줄 띠의 치마 빛깔(밝기 90..125 · 붉은 기) 중앙값보다 12 이상 밝은 화소를 그 빛깔 + 잔잡음으로.
사용: python3 s29p01_skirt_wm.py V2.png OUT.png"""
import sys
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
assert a.shape == (1024, 1024, 3), a.shape
rng = np.random.default_rng(291)
out = a.copy()
lum = a.mean(2)
X0, X1, Y0, Y1 = 884, 944, 866, 919
for y in range(Y0, Y1):
    l = lum[y, X0:X1]
    dk = np.nonzero(l < 95)[0]
    if len(dk) < 2:
        continue
    # left outline = first dark run, right outline = last dark run
    L = dk[0]
    while L + 1 < len(l) and l[L + 1] < 95: L += 1
    R = dk[-1]
    while R - 1 >= 0 and l[R - 1] < 95: R -= 1
    if R - L < 6:
        continue
    a0, a1 = X0 + L + 2, X0 + R - 1
    # skirt colour from a ±7-row band (a single row can be mostly sparkle)
    band = a[max(Y0, y - 7):y + 8, a0:a1].reshape(-1, 3)
    lb = band.mean(1)
    ok = (lb > 90) & (lb < 125) & ((band[:, 0] - band[:, 2]) > 20)
    col = np.median(band[ok], axis=0) if ok.sum() > 10 else np.median(band, axis=0)
    for x in range(a0, a1):
        if lum[y, x] > col.mean() + 12:
            out[y, x] = np.clip(col + rng.normal(0, 2.0, 3), 0, 255)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst); print('ok', dst)

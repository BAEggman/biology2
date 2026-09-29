#!/usr/bin/env python3
"""s20p03 — 개념 논리 M(근적외광이 식물을 해치지 않는다 · 개화는 단일/장일로 반대): 적색 등 아래 꽃 핌 · 꺼진 등 아래 꽃 시듦이던 것 →
제미나이 v1(적색 등 아래 화분: 씨앗이 막 싹틈 — 떡잎 둘 · 갈라진 씨껍질 / 꺼진 등 아래 화분: 통통한 씨앗이 흙 위에 그대로 잠) — 상추 씨 발아 실험 —
을 쓰고 오른쪽 아래 반짝이 표식(x 920..955 · y 450..490)만 둘레 바탕(바닥 띠의 세로 그러데이션을 따라 줄마다 좌우 중앙값) + 잔잡음으로 덮음.
사용: python3 s20p03_wm.py V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
assert a.shape == (559, 1024, 3), a.shape
rng = np.random.default_rng(203)
X0, X1, Y0, Y1 = 916, 960, 446, 494
for y in range(Y0, Y1):
    ref = np.concatenate([a[y, X0-18:X0-4], a[y, X1+4:X1+18]])
    bg = np.median(ref, axis=0)
    a[y, X0:X1] = np.clip(bg + rng.normal(0, 1.2, (X1-X0, 3)), 0, 255)
Image.fromarray(a.astype(np.uint8)).save(dst); print('ok', dst)

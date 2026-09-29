#!/usr/bin/env python3
"""s22p02 — 개념 논리 M(카스파리대 = 내피세포 벽 속 띠): 검은 가스 파이프 고리가 두 집 고리 사이 골목에 놓여 골목을 막던 것 →
제미나이 같은 대화 v3(골목의 파이프 고리 없앰 · 가운데 관 다발을 바로 둘러싼 안쪽 고리 집들 사이 틈마다 검은 가스 파이프 토막을 끼워 막음 ·
토막 양끝 둥근 이음 테는 코르크 · 가운데·바깥 고리의 틈과 골목은 뚫림 · 막힌 틈 앞에서 손을 들고 멈춘 사람)을 쓰고,
오른쪽 아래 빈 바닥의 반짝이 표식(x 880..930 · y 880..930)만 바닥 한 색(둘레 중앙값) + 잔잡음으로 덮음 — 종이 결은 약하게 흐려 둘레와 맞춤.
사용: python3 s22p02_wm.py V3.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
assert a.shape == (1024, 1024, 3), a.shape
rng = np.random.default_rng(222)
X0, X1, Y0, Y1 = 876, 934, 876, 934
ring = np.concatenate([a[Y0 - 14:Y0, X0:X1].reshape(-1, 3), a[Y1:Y1 + 14, X0:X1].reshape(-1, 3),
                       a[Y0:Y1, X0 - 14:X0].reshape(-1, 3), a[Y0:Y1, X1:X1 + 14].reshape(-1, 3)])
bg = np.median(ring, axis=0)
fill = np.clip(bg + rng.normal(0, 2.2, (Y1 - Y0, X1 - X0, 3)), 0, 255)
fill = ndi.gaussian_filter(fill, sigma=(0.8, 0.8, 0))
w = np.ones((Y1 - Y0, X1 - X0), np.float32)
F = 8
for i in range(F):
    t = (i + 1) / (F + 1)
    w[i, :] *= t; w[-1 - i, :] *= t; w[:, i] *= t; w[:, -1 - i] *= t
a[Y0:Y1, X0:X1] = a[Y0:Y1, X0:X1] * (1 - w[..., None]) + fill * w[..., None]
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(dst); print('bg', bg.astype(int))

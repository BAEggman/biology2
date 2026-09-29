#!/usr/bin/env python3
"""s16p01c — 개념 논리 M(로돕신 = GPCR 자체 · 리간드는 빛) + m(G단백 토큰 = 짙은 회색 네모 칩): 제미나이 같은 대화 v3
(도르래·로프를 뒤틀린 벽돌 창구 틀 위 모서리에 박음 · 그 앞 사람은 불 켠 등불 · 주저앉은 주자는 무릎 위에서 짙은 회색 네모 칩을 뒤집고 바닥에 칩 하나)을 쓰고,
오른쪽 아래 빈 바닥의 반짝이 표식(x 884..922 · y 888..926)만 바닥 한 색 + 잔잡음으로 덮음.
사용: python3 s16p01c_wm.py V3.png OUT.png"""
import sys
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
assert a.shape == (1024, 1024, 3), a.shape
rng = np.random.default_rng(161)
X0, X1, Y0, Y1 = 878, 928, 882, 932
ring = np.concatenate([a[Y0-12:Y0, X0:X1].reshape(-1, 3), a[Y1:Y1+12, X0:X1].reshape(-1, 3)])
bg = np.median(ring, axis=0)
a[Y0:Y1, X0:X1] = np.clip(bg + rng.normal(0, 1.2, (Y1-Y0, X1-X0, 3)), 0, 255)
Image.fromarray(a.astype(np.uint8)).save(dst); print('bg', bg.astype(int))

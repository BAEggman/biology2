#!/usr/bin/env python3
"""fix_frame.py — s31u01 v2: 구역 붙이기가 건드린 틀 선(위 · 오른쪽)을 바탕(base_v1_2x)의 틀 선으로 되돌린다.
b144 B 가 「오른쪽 끝 틀에 흰 틈 · 어긋난 선」으로 짚음 — 하늘 조각(SK) · 집 조각(H)이 틀 선(x 2005~2008 · y 36~40)을 하늘 · 벽 빛으로 덮었다.
사용: fix_frame.py cur.png base2x.png out.png"""
import sys, numpy as np
from PIL import Image
cur, base, out = sys.argv[1:4]
C = np.asarray(Image.open(cur).convert('RGB')).astype(float)
B = np.asarray(Image.open(base).convert('RGB')).astype(float)
C[24:41, 1270:2048] = B[24:41, 1270:2048]          # 위 틀 선(안쪽 41 부터는 그대로)
C[24:842, 2005:2048] = B[24:842, 2005:2048]        # 오른쪽 틀 선과 바깥 여백
# 안쪽 한 줄(x 2004)은 바탕의 밝은 테와 지금 그림의 평균 — 이음이 안 보이게
C[41:842, 2004] = (C[41:842, 2004] + B[41:842, 2004]) / 2
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save(out); print('ok')

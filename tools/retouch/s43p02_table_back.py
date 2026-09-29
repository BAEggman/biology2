#!/usr/bin/env python3
"""s43p02 — 제미나이 v1(담장 구멍으로 나가는 띠 앞끝에 모자 · 뒤끝에 술)이 손대지 말라던 작업대 위 띠의 오른쪽 이음매 둘
(청록 조각 사이 밝은 틈 = 잘라 낸 뒤 이은 자리)을 지우고 조각 테두리를 바꿈 → 작업대 띠 구간(x 490..900 × y 312..358)을
설치본에서 되옮긴다. 가장자리 4px 섞음. 담장 · 구멍 · 모자 · 술(y < 300)은 v1 그대로.
사용: python3 tools/retouch/s43p02_table_back.py <설치본.png> <v1.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
old_p, new_p, out = sys.argv[1:4]
O = Image.open(old_p).convert('RGB'); N = Image.open(new_p).convert('RGB').resize(O.size, Image.LANCZOS)
O = np.asarray(O, dtype=float); N = np.asarray(N, dtype=float)
H, W = O.shape[:2]
X0, X1, Y0, Y1, F = 490, 900, 312, 358, 4
w = np.zeros((H, W))
for y in range(Y0, Y1):
    for x in range(X0, X1):
        w[y, x] = min(1.0, (x - X0 + 1) / F, (X1 - x) / F, (y - Y0 + 1) / F, (Y1 - y) / F)
w = w[..., None]
res = O * w + N * (1 - w)
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)

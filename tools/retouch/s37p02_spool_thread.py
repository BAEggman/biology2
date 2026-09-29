#!/usr/bin/env python3
"""s37p02 — 제미나이 v1(세균 맨 실을 끝 없는 닫힌 고리로)이 오른쪽 실패 줄의 **풀린 실 끝**(= 선형 · 진핵 염색체)을 지움
→ 그 실 끝 둘레 x 878..948 × y 468..494 를 설치본에서 되옮긴다(가장자리 3px 섞음). 옛 고리의 윗선(y ≥ 497)은 들어오지 않는다.
사용: python3 tools/retouch/s37p02_spool_thread.py <설치본.png> <v1.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
old_p, new_p, out = sys.argv[1:4]
O = np.asarray(Image.open(old_p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
N = np.asarray(Image.open(new_p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
X0, X1, Y0, Y1, F = 878, 948, 468, 494, 3
w = np.zeros((1024, 1024))
for y in range(Y0, Y1):
    for x in range(X0, X1):
        w[y, x] = min(1.0, (x - X0 + 1) / F, (X1 - x) / F, (y - Y0 + 1) / F, (Y1 - y) / F)
w = w[..., None]
res = O * w + N * (1 - w)
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)

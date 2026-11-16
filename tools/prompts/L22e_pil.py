#!/usr/bin/env python3
"""L22e_pil.py <in.png> <out.png> — L22e 의 PIL 손질(2026-11-16).
  ① 화단 유리 윗테의 턱(x=1700: 왼쪽 테가 4 픽셀 낮다 — ZAA4 상자 경계) — x 1684→1699 사이 열을 0→4 픽셀 위로 비스듬히 올려 오른쪽 테에 잇는다."""
import sys
import numpy as np
from PIL import Image
a = np.array(Image.open(sys.argv[1]).convert('RGB')); o = a.copy()
y0, y1 = 424, 452
for x in range(1684, 1700):
    k = (x - 1684) / 15 * 4.0                      # 위로 올릴 양(픽셀, 소수 — 두 줄 섞기)
    i, f = int(k), k - int(k)
    col = a[:, x].astype(np.float32)
    for y in range(y0, y1):
        o[y, x] = np.clip(col[min(y + i, a.shape[0] - 1)] * (1 - f) + col[min(y + i + 1, a.shape[0] - 1)] * f, 0, 255).astype(np.uint8)
Image.fromarray(o).save(sys.argv[2]); print('L22e_pil ok')

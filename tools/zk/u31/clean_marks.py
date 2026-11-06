#!/usr/bin/env python3
"""clean_marks.py — s31u01 v2: b143 B 가 「벽 밑 낙서」로 짚은 자국 둘을 지운다(2배 캔버스 좌표).
① 왼쪽 옆담 바깥 밑동(x 638–649 · y 778–828)의 구불구불한 겹선 → 왼쪽 풀밭 결(x 626–637)을 옮겨 채움
② 안뜰 뒷담 밑동 오른 모서리(x 1568–1598 · y 434–440 · 점 y 445–452)의 손글씨 같은 눈금 → 같은 줄 왼쪽(x 1530–1560) 결로
사용: clean_marks.py in.png out.png"""
import sys, numpy as np
from PIL import Image
src, dst = sys.argv[1:3]
A = np.asarray(Image.open(src).convert('RGB')).astype(float)
# ①
w = 12
A[778:829, 638:650] = A[778:829, 626:638]
# ②
A[434:441, 1568:1599] = A[434:441, 1530:1561]
A[445:453, 1570:1590] = A[445:453, 1540:1560]
# 경계 부드럽게(1px 가우시안 섞기)
from scipy.ndimage import gaussian_filter
B = A.copy()
for (y0, y1, x0, x1) in [(776, 831, 636, 652), (432, 455, 1566, 1601)]:
    reg = A[y0:y1, x0:x1]; sm = np.stack([gaussian_filter(reg[..., c], 0.6) for c in range(3)], -1)
    m = np.zeros(reg.shape[:2]); m[:, :2] = 1; m[:, -2:] = 1; m[:2, :] = 1; m[-2:, :] = 1
    B[y0:y1, x0:x1] = reg * (1 - m[..., None]) + sm * m[..., None]
Image.fromarray(np.clip(B, 0, 255).astype('uint8')).save(dst); print('ok')

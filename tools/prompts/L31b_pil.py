#!/usr/bin/env python3
# L31b_pil.py <in.png> <out.png> — L31b 덧붙임(2026-11-16 · 10장 · 지시서 차례 7)의 PIL 몫.
#  일치 검사 1회 「허리띠의 작은 파란 둥근 양동이 윗면이 연파랑이라 물이 찬 것(= NADH)으로 읽힌다」 → 테 안쪽 타원을 어두운 속(빈 양동이 = NAD⁺)으로.
#  안쪽 타원만 칠한다(테의 검은 선 · 손잡이 고리는 그대로) — 위쪽 1/3 은 안쪽 뒷벽 빛, 나머지는 그늘.
import sys
import numpy as np
from PIL import Image

CX, CY, RX, RY = 181.0, 726.6, 8.4, 2.6        # 둥근 양동이 테 안쪽(2304 × 1296)
BACK, SHADE = np.array([70, 98, 128.]), np.array([26, 40, 56.])

def main(src, out):
    a = np.array(Image.open(src).convert('RGB')).astype(float)
    K = 8; n = 0
    for y in range(int(CY - RY) - 1, int(CY + RY) + 2):
        for x in range(int(CX - RX) - 1, int(CX + RX) + 2):
            cov = 0.0; tsum = 0.0                        # 8 × 8 덧칠 표본으로 가장자리를 부드럽게
            for sy in range(K):
                for sx in range(K):
                    px, py = x + (sx + .5) / K, y + (sy + .5) / K
                    if ((px - CX) / RX) ** 2 + ((py - CY) / RY) ** 2 <= 1: cov += 1; tsum += (py - (CY - RY)) / (2 * RY)
            if cov == 0: continue
            c = cov / K / K; t = tsum / cov
            col = BACK if t < 0.34 else SHADE
            a[y, x] = a[y, x] * (1 - c) + col * c; n += 1
    Image.fromarray(np.clip(a + .5, 0, 255).astype(np.uint8)).save(out); print('→', out, '· 칠한 픽셀', n)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

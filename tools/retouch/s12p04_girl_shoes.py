#!/usr/bin/env python3
"""s12p04 — 제미나이 v2(노인 목 신발 둘 → 셋)가 노란 리본 소녀의 빨간 구두를 벗겨 맨발로 만들었다.
맨발은 이 판에서 B12 결핍 사람(압정을 밟고도 태연)만의 표지라 소녀가 맨발이면 흐려진다.
두 그림은 소녀 치마·다리 둘레에서 어긋남 0 → 설치돼 있던 그림에서 치마 밑단 아래(다리·구두) 직사각형을 옮겨 붙인다.
사용: python3 tools/retouch/s12p04_girl_shoes.py <현재_설치본.png> <제미나이_v2.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image

src, dst, out = sys.argv[1], sys.argv[2], sys.argv[3]
a = np.asarray(Image.open(src).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
b = np.asarray(Image.open(dst).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
X0, X1, Y0, Y1, F = 305, 415, 684, 797, 5
yy, xx = np.mgrid[0:1024, 0:1024]
wx = np.clip(np.minimum(xx - X0, X1 - xx) / F, 0, 1)
wy = np.clip(np.minimum(yy - Y0, Y1 - yy) / F, 0, 1)
w = (wx * wy)[..., None]
res = a * w + b * (1 - w)
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)

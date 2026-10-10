#!/usr/bin/env python3
"""s44p01_pole_shear.py SRC OUT — 제미나이가 조각(y≤330) 안에서 딸의 둘째 장대를 3px 왼쪽으로 옮겨 그려, 조각 아래 원본 장대와 y=330 에서 어긋난다.
아래 원본 장대 띠(x 664~702 · y 330~540)를 위에서 3px, 바닥에서 0px 로 비스듬히 밀어(선형 보간) 이음새를 없앤다."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
O = np.asarray(Image.open(src).convert('RGB')).astype(float)
X0, X1, Y0, Y1, S = 664, 702, 330, 540, 3.0
out = O.copy()
for y in range(Y0, Y1):
    s = S * (Y1 - y) / (Y1 - Y0)
    xs = np.arange(X0, X1) + s
    for k in range(3):
        out[y, X0:X1, k] = ndi.map_coordinates(O[y, :, k], [xs], order=1, mode='nearest')
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('sheared strip', (X0, Y0, X1, Y1), 'top shift', S)

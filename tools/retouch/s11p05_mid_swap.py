#!/usr/bin/env python3
"""s11p05 — 가운데 선로(분열 한계)에 남은 글자 판자 넷이 GGG·TTA·GGG·TTA 였다 = 위 선로의 **끝 쪽** 넷(4–7번째)이 남은 꼴.
닳는 것은 끝이므로 남아야 하는 것은 유전자 곁 쪽 넷(1–4번째) = TTA·GGG·TTA·GGG (logic_0929 s11p05 3–4 m).
→ 가운데 선로에서 6↔7, 8↔9 번째 판자의 속(테두리 선 안쪽 x 폭 41 · 두 레일 사이 y 452..573)을 맞바꾼다. 테두리와 레일은 그대로.
판자 속 x: 6번 442..482 · 7번 511..551 · 8번 580..620 · 9번 649..689 (간격 69).
사용: python3 tools/retouch/s11p05_mid_swap.py <입력.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
src, out = sys.argv[1:3]
a = np.asarray(Image.open(src).convert('RGB').resize((1024, 1024), Image.LANCZOS)).copy()
Y0, Y1 = 452, 574
X = {6: 442, 7: 511, 8: 580, 9: 649}
W = 41
b = a.copy()
for p, q in ((6, 7), (8, 9)):
    b[Y0:Y1, X[p]:X[p] + W] = a[Y0:Y1, X[q]:X[q] + W]
    b[Y0:Y1, X[q]:X[q] + W] = a[Y0:Y1, X[p]:X[p] + W]
Image.fromarray(b).save(out)
print('saved', out)

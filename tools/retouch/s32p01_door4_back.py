#!/usr/bin/env python3
"""s32p01 — 개념 논리 M(I/II → Q → III → cyt c → IV): 레일 위 Q 수레(둥근 덩이)가 I–II 사이 · cyt c 수레(네모 상자)가 II 앞이던 것 →
제미나이 v1(Q 수레와 미는 사람을 II 문 뒤 · III 문 앞으로 · cyt c 수레를 III 문 뒤 · IV 앞으로)을 쓰고,
v1 이 넷째 집 문간에 더 그려 넣은 궤짝 든 사람만 설치본에서 되옮김(x 752..828 · y 742..906 · 가장자리 흐림 2px) + 설치본 때부터 있던 오른쪽 아래 반짝이 표식과 작은 낙서를 벽돌 결을 따라 옮겨 메움(왼 면·오른 면·모서리·바닥 따로).
사용: python3 s32p01_door4_back.py V1.png ORIG.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
v1p, op, dst = sys.argv[1], sys.argv[2], sys.argv[3]
V = np.asarray(Image.open(v1p).convert('RGB')).astype(np.float32)
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float32)
assert V.shape == O.shape == (1024, 1024, 3)
M = np.zeros((1024, 1024), np.float32); M[742:906, 752:828] = 1.0
M = ndi.gaussian_filter(M, 2.0)[..., None]
out = V * (1 - M) + O * M
# sparkle (x 884..926 · y 878..932, on an inside wall corner and the ground) and a tiny scribble (x 921..946 · y 899..913) —
# both already in the installed picture. Filled by cloning ALONG the brick courses of each wall face (no smearing):
#   left face (x < 900): courses rise to the right (slope −0.5) → source (x − 36, y + 18)
#   right face (x > 904): courses fall to the right (slope +0.42) → source (x + 36, y + 15)
#   corner line (x 900..904): source (x, y − 32) · ground (below the base lines): the median of the unmasked ground in the same row (keeps the wall-shadow gradient)
lum = out.mean(2)
med = ndi.median_filter(lum, size=25)
box = np.zeros((1024, 1024), bool); box[876:934, 882:928] = True
mk = box & ((lum - med) > 6)
mk = ndi.binary_dilation(mk, iterations=2) & ndi.binary_dilation(box, iterations=2)
mk[898:914, 920:947] |= (lum[898:914, 920:947] < 110)
mk[896:916, 918:949] = ndi.binary_dilation(mk[896:916, 918:949], iterations=1)
src = out.copy()
ys, xs = np.nonzero(mk)
def base_y(x):
    return 930.0 - (x - 857) * 0.545 if x < 902 else 906.0 + (x - 902) * 0.42
GX = np.arange(850, 992)
rowcol = {}
for y in np.unique(ys):
    ok = [x for x in GX if (not mk[y, x]) and y > base_y(x) + 2]
    if len(ok) >= 4:
        rowcol[y] = np.median(src[y, ok], axis=0)
for y, x in zip(ys, xs):
    if y > base_y(x) + 1:
        if y in rowcol:
            out[y, x] = rowcol[y]
            continue
        sy, sx = y + 22, x
    elif x < 900:
        sy, sx = y + 18, x - 36
    elif x > 904:
        sy, sx = y + 15, x + 36
    else:
        sy, sx = y - 32, x
    k = 0
    while mk[sy, sx] and k < 4:            # step further along the same direction if the source is masked too
        sy, sx = sy + (sy - y), sx + (sx - x); k += 1
    out[y, x] = src[sy, sx]
blur = ndi.gaussian_filter(out, sigma=(0.6, 0.6, 0))
edge = ndi.binary_dilation(mk, iterations=1) & ~ndi.binary_erosion(mk, iterations=1)
out[edge] = blur[edge]
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst); print('ok', dst)

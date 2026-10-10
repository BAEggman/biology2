#!/usr/bin/env python3
"""s26p02_jar_empty.py SRC OUT — 작은 탑 사람의 병(산소)이 반쯤 차 보여 4행 「알갱이가 거의 바닥난 병」이 안 섬 →
병 속 알갱이를 병 안 빛(빈 윗부분 색)으로 지우고 맨 밑에 알갱이 둘만 남긴다(원본 알갱이 하나를 복사)."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
O = np.asarray(Image.open(src).convert('RGB')).astype(float)
X0, Y0, X1, Y1 = 215, 480, 300, 560
sub = O[Y0:Y1, X0:X1]; lum = sub.mean(2)
lab, n = ndi.label(lum > 60); reg = lab == lab[31, 37]          # 병 안(검은 윤곽 안쪽)
reg = ndi.binary_fill_holes(reg)                                 # 알갱이 윤곽(검은 구멍)까지 안으로
reg = ndi.binary_erosion(reg, iterations=1)
pale = reg & (lum > 195) & ((sub.max(2) - sub.min(2)) < 18)      # 빈 윗부분의 유리빛
fill = np.median(sub[pale], axis=0); print('interior color', fill, 'pale px', pale.sum())
grain = reg & ~pale                                             # 알갱이 + 그 윤곽 + 그늘
# 알갱이 하나를 복사해 둘 남길 자리(병 바닥 쪽) — 바닥은 병이 기울어 오른쪽 아래
ys, xs = np.nonzero(grain); print('grain bbox', xs.min(), ys.min(), xs.max(), ys.max())
out = O.copy()
sb = out[Y0:Y1, X0:X1]
a = ndi.gaussian_filter(grain.astype(float), 0.8)
for k in range(3): sb[..., k] = sb[..., k] * (1 - a) + fill[k] * a
# 복사할 알갱이: 가장 밝은 tan 덩어리 하나 — 색으로 찾기
tan = reg & (sub[..., 0] - sub[..., 2] > 30) & (lum > 150)
lab2, n2 = ndi.label(tan); sizes = ndi.sum(tan, lab2, range(1, n2 + 1)); gi = int(np.argmax(sizes)) + 1
cy, cx = ndi.center_of_mass(lab2 == gi); cy, cx = int(round(cy)), int(round(cx)); R = 5
print('grain copy center', cx, cy, 'size', sizes[gi - 1])
tile = O[Y0 + cy - R:Y0 + cy + R + 1, X0 + cx - R:X0 + cx + R + 1]
yy, xx = np.mgrid[-R:R + 1, -R:R + 1]; disk = (xx ** 2 + yy ** 2) <= (R - 0.5) ** 2
da = ndi.gaussian_filter(disk.astype(float), 0.6)
for (gx, gy) in [(int(sys.argv[3]), int(sys.argv[4])), (int(sys.argv[5]), int(sys.argv[6]))]:
    region = out[gy - R:gy + R + 1, gx - R:gx + R + 1]
    out[gy - R:gy + R + 1, gx - R:gx + R + 1] = region * (1 - da[..., None]) + tile * da[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)

#!/usr/bin/env python3
"""s16p01 — 캐비닛 왼쪽 아래 모서리에 겹친 흰 반짝이 표식(원본부터 있던 것, 중심 ≈ (905,905) · 반지름 ≈ 20) 지우기.
캐비닛이 곧은 선뿐이라 **다시 그려 넣는다**: 둘레의 멀쩡한 자리에서 면 색을 재어(옆판 x 898..905 · 서랍 앞 · 받침 · 바닥)
평면으로 칠하고, 끊긴 선 넷을 이어 그린다 — 바깥 왼쪽 선(x≈897, y 886→917) · 안쪽 선(x≈906, y 868→910) ·
맨 아래 서랍 밑선(y≈910, x 906→917) · 캐비닛 밑선(x 897→905, 멀쩡한 오른쪽 기울기 0.14 를 이어서).
원래 그림보다 **확실히 밝은 곳(국소 밝기 차 > 12)** 만 바꾸고 1px 섞는다.
사용: python3 s16p01_cabinet_spark.py IN.png OUT.png"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
I = np.asarray(Image.open(src).convert('RGB')).astype(np.float64)
H, W = I.shape[:2]
X0, X1, Y0, Y1 = 884, 938, 880, 924
def med(x0, x1, y0, y1):
    return np.median(I[y0:y1, x0:x1].reshape(-1, 3), axis=0)
side = med(900, 905, 845, 880)        # 옆판
front = med(936, 950, 888, 906)       # 서랍 앞
plinth = med(936, 950, 912, 917)      # 받침(서랍 밑선과 캐비닛 밑선 사이)
floor = med(860, 880, 900, 930)       # 바닥
ink = np.array([12.0, 12.0, 12.0])
print('side', side.astype(int), 'front', front.astype(int), 'plinth', plinth.astype(int), 'floor', floor.astype(int))
E = Image.new('RGB', (W, H))
E.paste(Image.fromarray(np.clip(I, 0, 255).astype(np.uint8)))
d = ImageDraw.Draw(E)
def bot(x): return 918.5 + (x - 912) * 0.14   # 캐비닛 밑선 중심(멀쩡한 x 905..950 에서 잰 것)
# 면
d.rectangle([X0, Y0, 896, Y1], fill=tuple(int(v) for v in floor))
d.polygon([(898, Y0), (905, Y0), (905, bot(905) - 1.5), (898, bot(898) - 1.5)], fill=tuple(int(v) for v in side))
d.rectangle([907, Y0, X1, 909], fill=tuple(int(v) for v in front))
d.polygon([(907, 911), (X1, 911), (X1, bot(X1) - 1.5), (907, bot(907) - 1.5)], fill=tuple(int(v) for v in plinth))
d.polygon([(896, bot(896) + 2), (X1, bot(X1) + 2), (X1, Y1), (896, Y1)], fill=tuple(int(v) for v in floor))
# 선
col = tuple(int(v) for v in ink)
d.line([(897, 884), (897, bot(897))], fill=col, width=3)
d.line([(906, 884), (906, 910)], fill=col, width=3)
d.line([(906, 910), (918, 910)], fill=col, width=3)
d.line([(896, bot(896)), (X1, bot(X1))], fill=col, width=3)
E = np.asarray(E).astype(np.float64)
E = ndi.gaussian_filter(E, sigma=(0.6, 0.6, 0))
lumI = I.mean(axis=2); lumE = E.mean(axis=2)
m = np.zeros((H, W), bool)
m[Y0:Y1, X0:X1] = (lumI - lumE)[Y0:Y1, X0:X1] > 12
m = ndi.binary_closing(m, iterations=1)
m = ndi.binary_dilation(m, iterations=1)
w = ndi.gaussian_filter(m.astype(float), 0.8)
w[:Y0 - 2, :] = 0; w[Y1 + 2:, :] = 0; w[:, :X0 - 2] = 0; w[:, X1 + 2:] = 0
out = I * (1 - w[..., None]) + E * w[..., None]
print('mask px', int(m.sum()))
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)

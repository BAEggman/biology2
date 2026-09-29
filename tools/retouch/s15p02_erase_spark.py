#!/usr/bin/env python3
"""s15p02 — v2(유리 통 · 통-관 한 몸) 결과에서 가위 곁에 새로 생긴 하얀 번개 모양 튐(전기로 읽힘)을 지운다.
같은 대화의 v1 결과는 가위·사람·벽이 v2 와 한 픽셀 단위로 겹치고(격자 차이 2–8) 튐이 없다 → 튐 둘레만 v1 에서 옮겨 온다.
범위: x 680..752 × y 197..308 안에서 v1·v2 차이가 15 넘는 곳 + 3px 부풀림, 가장자리 3px 섞음. 관(y<197)은 건드리지 않는다.
사용: python3 tools/retouch/s15p02_erase_spark.py <v1.png> <v2.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image, ImageFilter
v1p, v2p, out = sys.argv[1:4]
V1 = np.asarray(Image.open(v1p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
V2 = np.asarray(Image.open(v2p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
d = np.abs(V1 - V2).mean(axis=2)
m = np.zeros((1024, 1024), dtype=np.uint8)
X0, X1, Y0, Y1 = 680, 752, 197, 308
sub = (d[Y0:Y1, X0:X1] > 15).astype(np.uint8) * 255
m[Y0:Y1, X0:X1] = sub
M = Image.fromarray(m).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(1.5))
w = np.asarray(M, dtype=float)[..., None] / 255.0
# keep the pipe untouched
w[:Y0] = 0
res = V2 * (1 - w) + V1 * w
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out, 'mask px', int((w[..., 0] > 0.5).sum()))

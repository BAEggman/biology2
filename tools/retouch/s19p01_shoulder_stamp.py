#!/usr/bin/env python3
"""s19p01 — 제미나이 v3(자전거 B · 허리 도장 지움 · 지우개)가 아래 왼쪽 덩치 어깨의 붉은 도장 자국까지 지웠다.
「어깨의 붉은 도장 자국은 그대로」라고 적었는데도. 어깨 윤곽은 두 그림이 어긋남 0(가장자리 대조) →
설치돼 있던 그림(= 도장 자국 있음)에서 자국 둘레 원(중심 118,708 · 반지름 21)을 옮겨 붙인다. 가장자리 3px 는 섞는다.
사용: python3 tools/retouch/s19p01_shoulder_stamp.py <현재_설치본.png> <제미나이_v3.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image

src, dst, out = sys.argv[1], sys.argv[2], sys.argv[3]
a = np.asarray(Image.open(src).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
b = np.asarray(Image.open(dst).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
CY, CX, R, F = 708, 118, 21, 3
yy, xx = np.mgrid[0:1024, 0:1024]
dist = np.sqrt((yy - CY) ** 2 + (xx - CX) ** 2)
w = np.clip((R + F - dist) / F, 0, 1)[..., None]   # 1 안쪽 · 0 바깥 · 사이 3px 섞음
res = a * w + b * (1 - w)
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)

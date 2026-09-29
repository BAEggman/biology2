#!/usr/bin/env python3
"""s19p01c — 개념 논리 M(S 뒤로는 모두 둘): 제미나이 v1 이 G2(돋보기) 칸 맨 위 빵을 M(가장 얇은) 칸의 비스듬한 벽 곁으로 옮겨
G2 둘 · M 둘(두 벽에 하나씩)로 맞췄으나, 세로 벽 오른쪽 G1 칸 꼭대기에 빵 하나(x 418..468 · y 160..305)를 더 그려 넣음
→ 그 자리(x 416..482 · y 150..312, 세로 벽 오른쪽)만 설치본에서 되옮김(설치본엔 그 자리에 아무것도 없음 · 두 그림 어긋남 0px 확인) · 가장자리 3px 섞음.
사용: python3 s19p01c_drop_g1_loaf.py V1.png ORIG.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
v1p, op, dst = sys.argv[1], sys.argv[2], sys.argv[3]
V = np.asarray(Image.open(v1p).convert('RGB')).astype(np.float32)
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float32)
assert V.shape == O.shape == (1024, 1024, 3)
M = np.zeros((1024, 1024), np.float32)
M[150:312, 416:482] = 1.0
M = ndi.gaussian_filter(M, 1.5)[..., None]
out = V * (1 - M) + O * M
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst); print('ok', dst)

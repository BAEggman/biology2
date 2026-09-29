#!/usr/bin/env python3
"""s17p05 — 개념 논리 m 4 + m(s17 양동이): 가운데 요소 칸의 누런 요가 **개켜** 담겨(= 이 판 5행이 말하는 요산 쪽 「접어 쌓음」) 있던 것 →
통 위에 **펼쳐 깐** 요(마름모 누빔이 다 보이고 네 귀가 테 밖으로 늘어짐) · 가운데 칸 아래 금속 양동이(= NADH 예약) → 질그릇 물항아리.
제미나이 v1 에서 두 자리(통 x 440..700 · y 170..360 / 항아리 x 560..720 · y 390..545)만 옮겨 붙임(σ2 밝기 차 > 12 · 닫기 3 · 메움 · 넓힘 4 · σ2 섞음).
사용: python3 s17p05_quilt_jar_paste.py ORIG.png V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
H, W = O.shape[:2]
d = ndi.gaussian_filter(np.abs(O - V).mean(axis=2), 2.0)
m = np.zeros((H, W), bool)
for (x0, y0, x1, y1) in [(440, 170, 700, 360), (560, 390, 720, 545)]:
    b = np.zeros((H, W), bool); b[y0:y1, x0:x1] = True
    mm = (d > 12) & b
    mm = ndi.binary_closing(mm, iterations=3)
    mm = ndi.binary_fill_holes(mm)
    mm = ndi.binary_dilation(mm, iterations=4) & b
    m |= mm
w = ndi.gaussian_filter(m.astype(float), 2.0)
out = O * (1 - w[..., None]) + V * w[..., None]
print('paste px', int(m.sum()))
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print('saved', dst)

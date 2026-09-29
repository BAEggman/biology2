#!/usr/bin/env python3
"""s33p03 — 개념 논리 M 7·8·1(케톤체는 간을 나와 피를 타고 뇌로): 투구 지붕 건물(뇌)이 안뜰(미토콘드리아 기질) 안에 서 있던 것 →
제미나이 새 대화 v3(원본에 **연파랑 안내 띠**를 칠해 새 운하 자리를 박음: 위 운하 가까운 둑 → 오른쪽 아치 오른쪽 담 윗단) +
같은 대화 후속 v4(건너편 둑에 남은 궤도 토막 지움)를 쓰되, **바뀐 오른쪽만** 옮겨 붙이고 나머지는 원본(설치본) 그대로 둔다.
제미나이는 판 전체를 다시 그리며 왼쪽 2/3 도 살짝 흐려지게 한다(배·사슬·인부 — 국소 차이 10~40) → 그 흐림을 들이지 않으려는 것.
  ① 마스크: 원본↔v4 국소 차이(15px 평균) > 20 인 곳 가운데 x ≥ 600 에 닿는 덩어리들 → 16px 넓힘 → 구멍 메움 → 가우스 σ4 로 섞음.
  ② 왼쪽 아래 1/3(궤도·요·수레)은 마스크에서 뺀다(y > 700 이고 x < 700 — 원본 그대로).
  ③ 오른쪽 아래 반짝이 표식(원본부터 있던 것)을 별 화소만 둘레에서 메움(벽 그림자 결은 그대로).
사용: python3 s33p03_right_only.py ORIG.png V4.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
assert O.shape == V.shape == (1024, 1024, 3)
H, W = O.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]
d = ndi.uniform_filter(np.abs(O - V).mean(axis=2), 15)
m = d > 20
lab, n = ndi.label(m)
keep = np.zeros(n + 1, bool)
for i, sl in enumerate(ndi.find_objects(lab), start=1):
    if sl[1].stop > 600:
        keep[i] = True
m = keep[lab]
m = ndi.binary_dilation(m, iterations=16)
m = ndi.binary_fill_holes(m)
m[(yy > 700) & (xx < 700)] = False
w = ndi.gaussian_filter(m.astype(float), 4.0)
print('mask px', int(m.sum()), 'bbox', ndi.find_objects(m.astype(int))[0])
out = O * (1 - w[..., None]) + V * w[..., None]

# ③ 반짝이: 흰 별 화소(국소 밝기 − 중앙값21 > 3, 상자 x 878..935 · y 872..940)만 3px 넓혀 둘레에서 메움(Telea) — 벽 그림자 결은 그대로
import cv2
o8 = np.clip(out, 0, 255).astype(np.uint8)
L = o8.mean(axis=2).astype(np.float64)
loc = L - ndi.median_filter(L, 21)
star = np.zeros((H, W), bool)
star[872:940, 878:935] = loc[872:940, 878:935] > 3
star = ndi.binary_dilation(star, iterations=3)
print('spark px', int(star.sum()))
out = cv2.inpaint(o8, star.astype(np.uint8) * 255, 5, cv2.INPAINT_TELEA).astype(np.float64)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
Image.fromarray((w * 255).astype(np.uint8)).save(dst.replace('.png', '_mask.png'))
print('saved', dst)

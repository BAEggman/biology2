#!/usr/bin/env python3
"""s21p02 — 개념 논리 M 6(최대 절약 = 같은 종들의 나무 가운데 진화 사건이 가장 적게 드는 것): 작은 틀의 모빌 셋이 인물 수가 다르고 「관절(고리)이 가장 적은 것」을 고르던 것 →
틀 조각(원본 x 600..1000 · y 560..960)을 2.56배 키워 제미나이에 주고(판 전체에서는 이 조각이 너무 작아 v1 이 엉킴) 같은 대화 후속까지 두 번 →
모빌 **둘**, 둘 다 같은 셋(가슴에 노란 별 단 둘 · 안 단 하나) · 고리(갈림) 둘씩 같음 · 별이 생긴 자리를 끈에 묶은 작은 별로:
왼쪽 = 별 사람 둘이 한 고리에 모임 → 작은 별 **하나** · 오른쪽 = 별 사람이 갈림 → 작은 별 **둘** · 사람이 왼쪽 모빌을 들어 올림.
그 결과를 400×400 으로 줄여(어긋남 0px — 틀 기둥·바닥·위·오른쪽 가장자리에서 잼) 제자리에 붙인다:
  ① 바뀐 곳만: 원본↔결과 밝기 차이(가우스 σ2) > 12 → 닫기 3 · 구멍 메움 · 넓힘 6 → 가우스 σ3 로 섞음(조각 가장자리 12px 는 0 으로).
  ② 톤: 결과가 원본보다 살짝 덜 누렇다(V−O ≈ +2,+1,−3) → 바뀌지 않은 둘레(차이 < 6)에서 잰 O−V 를 σ25 로 번져 더한다.
  ③ 틀 오른쪽 아래 바닥 가로대 끝을 덮던 흰 번짐(원본부터 있던 것)은 결과 조각에서 온전히 그려져 있어 마스크로 함께 옮긴다.
사용: python3 s21p02_frame_paste.py ORIG.png CROP_RESULT_1024.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import cv2
op, cp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
X0, Y0, S = 600, 560, 400
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(cp).convert('RGB').resize((S, S), Image.LANCZOS)).astype(np.float64)
Oc = O[Y0:Y0 + S, X0:X0 + S]
d = ndi.gaussian_filter(np.abs(V - Oc).mean(axis=2), 2.0)
m = d > 12
m = ndi.binary_closing(m, iterations=3)
m = ndi.binary_fill_holes(m)
m[885 - Y0 - 6:912 - Y0 + 6, 880 - X0 - 6:925 - X0 + 6] = True   # ③ 흰 번짐 자리
m = ndi.binary_dilation(m, iterations=6)
m[:12, :] = False; m[-12:, :] = False; m[:, :12] = False; m[:, -12:] = False
w = ndi.gaussian_filter(m.astype(float), 3.0)
calm = (d < 6) & ~ndi.binary_dilation(m, iterations=4)
corr = np.zeros_like(V)
for k in range(3):
    num = ndi.gaussian_filter((Oc[..., k] - V[..., k]) * calm, 25)
    den = ndi.gaussian_filter(calm.astype(float), 25)
    corr[..., k] = np.where(den > 1e-3, num / np.maximum(den, 1e-6), 0)
Vt = V + corr
out = O.copy()
out[Y0:Y0 + S, X0:X0 + S] = Oc * (1 - w[..., None]) + Vt * w[..., None]
print('mask px', int(m.sum()), 'tone corr mean', corr[m].mean(axis=0).round(1))
# ③ 틀 오른쪽 아래 바닥 가로대 끝을 덮던 흰 번짐(원본부터 있던 것, x 880..925 · y 885..912)은 결과 조각에 없다 → 마스크에 들어오게 한다
out = np.clip(out, 0, 255).astype(np.uint8)
Image.fromarray(out).save(dst)
Image.fromarray((w * 255).astype(np.uint8)).save(dst.replace('.png', '_mask.png'))
print('saved', dst)

#!/usr/bin/env python3
"""s46p04 — 혈장 층 비율을 55% 로. 제미나이 v3 가 노란 층을 늘렸으나 51 % · 흰 띠 2 % · 적혈구 47 % 에 그침
(2행 「눈금으로 보면 절반이 넘는다」가 눈에 안 보임). 시험관 기둥(x 200..358)만 줄 단위로 옮긴다:
  y < 517 그대로 · 517..545 ← 488..516 (눈금 한 칸 = 29줄을 노란 층에 끼움 — 눈금 간격 그대로)
  546..578 ← 517..549 (노란 층 끝 · 경계선 · 흰 띠 위쪽 넉 줄) · 흰 띠 가운데 550..555 는 버림(띠를 머리카락 굵기로)
  579..589 ← 556..566 (적혈구 경계선과 윗부분) · 590 부터(받침 가로대) 그대로.
결과(가운데 기둥 색으로 잰 값): 노랑 ≈ 55.7 % · 흰 띠 ≈ 0.8 % · 빨강 ≈ 43.4 % — 실제 55 · <1 · 45 에 맞다.
사용: python3 tools/retouch/s46p04_plasma_55.py <제미나이_v3.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB').resize((1024, 1024), Image.LANCZOS)).copy()
b = a.copy()
X0, X1 = 200, 358
def put(dst0, src0, n):
    b[dst0:dst0 + n, X0:X1] = a[src0:src0 + n, X0:X1]
put(517, 488, 29)   # 517..545
put(546, 517, 33)   # 546..578
put(579, 556, 11)   # 579..589
Image.fromarray(b).save(out)
print('saved', out)

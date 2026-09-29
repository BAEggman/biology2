#!/usr/bin/env python3
"""s45p03 — 제미나이 v1(CAM 밤 칸: 방울을 막대 끝에 붙여 항아리에 꽂음)이 손대지 말라던 왼쪽 C₄ 집에 두 가지를 덧그림:
안쪽 방 벽의 초승달 표지(= 밤 — C₄ 는 시간이 아니라 공간 분리라 거짓) · 스코프 사람 발치의 막대 더미 · 바지 색 바뀜.
→ 왼쪽 집 전체(x 0..500, 두 집 사이 빈 바탕에서 자름)를 설치본에서 되옮긴다. 가장자리 x 492..500 에서 8px 섞음.
사용: python3 tools/retouch/s45p03_left_house_back.py <설치본.png> <v1.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
old_p, new_p, out = sys.argv[1:4]
O = np.asarray(Image.open(old_p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
N = np.asarray(Image.open(new_p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
X1, F = 500, 8
w = np.zeros(1024)
w[:X1 - F] = 1.0
w[X1 - F:X1] = np.linspace(1, 0, F)
w = w[None, :, None]
res = O * w + N * (1 - w)
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)

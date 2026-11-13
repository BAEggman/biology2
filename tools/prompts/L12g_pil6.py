#!/usr/bin/env python3
# L12g_pil6.py <in> <gem_Z6.png> <out> — 작업대의 일꾼(구역 편집 Z6)을 손으로 옮겨 붙인다.
#  Gemini 가 자른 조각(240x160 → 1024x683)을 같은 배율로 돌려주지 않고 일꾼을 작게(화면 가운데 아래) 다시 그렸다
#  — zone3.py 의 정합(같은 배율 가정)을 못 쓴다. 작업대 윗면을 맞춰 0.63 배로 줄여 붙이고 다리를 땅까지 늘인다.
import sys
import numpy as np
from PIL import Image, ImageFilter
im = Image.open(sys.argv[1]).convert('RGB'); g = Image.open(sys.argv[2]).convert('RGB')
a = np.asarray(im).astype(np.int32).copy()
SKY = np.array([198, 230, 247])
a[150:326, 1594:1772] = SKY                                    # 옛 일꾼 · 작업대 · 기름방울을 지운다(소 등선은 x < 1580 · 콩 탈 장수는 x ≥ 1780)
GX0, GY0, GX1, GY1 = 392, 400, 680, 683                        # Gemini 그림 속 일꾼 + 작업대
S = 145 / 230.0                                                # 작업대 너비 230 → 145
sub = g.crop((GX0, GY0, GX1, GY1)); w, h = round(sub.width * S), round(sub.height * S)
sub = np.asarray(sub.resize((w, h), Image.LANCZOS)).astype(np.int32)
gsky = np.median(np.asarray(g.crop((700, 100, 1000, 300))).reshape(-1, 3), axis=0)
m = np.abs(sub - gsky).sum(2) > 30
m = np.asarray(Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MaxFilter(3))) > 0
DX = 1600 - round((405 - GX0) * S); DY = 252 - round((592 - GY0) * S)   # 작업대 윗면 왼쪽 끝 (405,592) → (1600,252)
dst = a[DY:DY + h, DX:DX + w]; dst[m] = sub[m]
# 다리를 y=320 까지 늘인다(맨 아랫줄의 검은 다리 픽셀을 내려 복사)
yb = DY + h - 2
for y in range(DY + h - 1, 321):
    row = a[yb, DX:DX + w]; mm = row.sum(1) < 200
    a[y, DX:DX + w][mm] = row[mm]
Image.fromarray(a.clip(0, 255).astype('uint8')).save(sys.argv[3]); print('ok pil6', (DX, DY, w, h))

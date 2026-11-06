#!/usr/bin/env python3
"""paste_sky.py — s31u01 v2: 물레방아 지우기(fit_SK 첫 턴 · 안뜰 쪽 맑은 하늘) + 먹구름 아래 비 지우기(fit_SKb 둘째 턴 · 어둑한 하늘)를 한 조각에서 갈라 붙인다.
하늘(담 꼭대기 위): 왼쪽 원본 → 첫 턴(물레방아 자리) → 먹구름 밑으로 비스듬히 넓게(220px) 둘째 턴 / 담(꼭대기 아래): 원본 → x 360~430 에서 둘째 턴(비 없는 담).
사용: paste_sky.py cur.png crop_SK.json fit_SK.png fit_SKb.png out.png"""
import sys, json, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
cur, cj, f1, f2, out = sys.argv[1:6]
B = np.asarray(Image.open(cur).convert('RGB')).astype(float)
c = json.load(open(cj)); S = c['scale']; bx0, by0, bx1, by1 = [v * S for v in c['box']]
w, h = bx1 - bx0, by1 - by0
F1 = np.asarray(Image.open(f1).convert('RGB').resize((w, h), Image.LANCZOS)).astype(float)
F2 = np.asarray(Image.open(f2).convert('RGB').resize((w, h), Image.LANCZOS)).astype(float)
C0 = B[by0:by1, bx0:bx1].copy()
yy, xx = np.mgrid[0:h, 0:w].astype(float)
TOP = 186.0   # 담 꼭대기(조각 2배 좌표)
sky = (yy < TOP).astype(float); sky = gaussian_filter(sky, 1.5)
# 하늘: 원본 → 첫 턴 (x 60~100)
a1 = np.clip((xx - 60) / 40.0, 0, 1)
# 하늘: → 둘째 턴 — 시작이 위로 갈수록 왼쪽(먹구름 가장자리 따라)
x0 = 250 + 0.7 * yy
a2 = np.clip((xx - x0) / 220.0, 0, 1); a2 = a2 * a2 * (3 - 2 * a2)
SKY = C0 * (1 - a1[..., None]) + F1 * a1[..., None]
SKY = SKY * (1 - a2[..., None]) + F2 * a2[..., None]
# 담: 원본 → 둘째 턴(비 없음) x 360~430
a3 = np.clip((xx - 360) / 70.0, 0, 1)
WALL = C0 * (1 - a3[..., None]) + F2 * a3[..., None]
R = SKY * sky[..., None] + WALL * (1 - sky[..., None])
B[by0:by1, bx0:bx1] = R
Image.fromarray(np.clip(B, 0, 255).astype('uint8')).save(out); print('ok')

#!/usr/bin/env python3
"""arrow_turn.py — s31u01 문간: 회전문 앞 바닥에 「안쪽으로만」 한쪽 화살표를 그린다(회색 채움 + 먹선 · 4배로 그려 줄임).
Gemini 가 그린 화살표는 두 번 다 문 쪽(바깥)을 가리켰다 → 직접 그린다. 사용: arrow_turn.py in.png out.png"""
import sys, numpy as np
from PIL import Image, ImageDraw
src, dst = sys.argv[1:3]
im = Image.open(src).convert('RGB'); W, H = im.size
S = 4
# 2배 캔버스 좌표: 문지기 발 오른쪽 → 회전문 앞 바닥 → 오른쪽(안뜰 쪽)
P0, P1, P2 = np.array([792., 800.]), np.array([885., 832.]), np.array([988., 780.])
def bez(t): return (1-t)**2*P0 + 2*(1-t)*t*P1 + t*t*P2
def dbez(t): return 2*(1-t)*(P1-P0) + 2*t*(P2-P1)
ts = np.linspace(0, 0.86, 60)
half = 5.0
L, R = [], []
for t in ts:
    p = bez(t); d = dbez(t); d /= np.linalg.norm(d); n = np.array([-d[1], d[0]])
    L.append(p + n*half); R.append(p - n*half)
tip = bez(1.0); d = dbez(1.0); d /= np.linalg.norm(d); n = np.array([-d[1], d[0]])
base = bez(0.86)
hw = 14.0
head = [base + n*hw, tip + d*3, base - n*hw]
poly = L + [base + n*half, head[0], head[1], head[2], base - n*half] + R[::-1]
x0, y0 = int(min(p[0] for p in poly)) - 10, int(min(p[1] for p in poly)) - 10
x1, y1 = int(max(p[0] for p in poly)) + 10, int(max(p[1] for p in poly)) + 10
w, h = (x1 - x0) * S, (y1 - y0) * S
fill = Image.new('L', (w, h), 0); line = Image.new('L', (w, h), 0)
pp = [((p[0]-x0)*S, (p[1]-y0)*S) for p in poly]
ImageDraw.Draw(fill).polygon(pp, fill=255)
ImageDraw.Draw(line).line(pp + [pp[0]], fill=255, width=int(2.4*S), joint='curve')
fill = np.asarray(fill.resize((x1-x0, y1-y0), Image.LANCZOS)).astype(float)/255
line = np.asarray(line.resize((x1-x0, y1-y0), Image.LANCZOS)).astype(float)/255
A = np.asarray(im).astype(float)
reg = A[y0:y1, x0:x1]
# 채움: 연한 회색(아래쪽으로 조금 어둡게 — 물감 얼룩 느낌)
yy = np.linspace(0, 1, y1-y0)[:, None]
g = np.stack([186 - 10*yy, 190 - 10*yy, 194 - 10*yy], -1) * np.ones((1, x1-x0, 1))
rng = np.random.default_rng(31); g += rng.normal(0, 2.0, g.shape)
reg = reg*(1-fill[..., None]*0.92) + g*(fill[..., None]*0.92)
ink = np.array([52., 52., 56.])
reg = reg*(1-line[..., None]) + ink*line[..., None]
A[y0:y1, x0:x1] = reg
Image.fromarray(np.clip(A, 0, 255).astype('uint8')).save(dst)
print('arrow box', x0, y0, x1, y1)

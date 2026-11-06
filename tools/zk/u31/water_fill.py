#!/usr/bin/env python3
"""water_fill.py — 양동이 아가리(타원) 안을 물빛으로 채운다(가득 = NADH 가 한눈에 보이게 · s31u01 안뜰).
사용: water_fill.py in.png out.png "cx,cy,rx,ry;..." [--ref x0,y0,x1,y1 (물빛을 따올 칸)]
물빛 = ref 칸의 평균(없으면 연한 하늘빛) · 위쪽 가장자리에 흰 반짝임 한 줄 · 가장자리 0.8px 번짐(4배로 그려 줄임)."""
import sys, argparse, numpy as np
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst'); ap.add_argument('ells'); ap.add_argument('--ref', default='')
a = ap.parse_args()
im = Image.open(a.src).convert('RGB'); A = np.asarray(im).astype(float)
if a.ref:
    x0, y0, x1, y1 = [int(v) for v in a.ref.split(',')]; wc = A[y0:y1, x0:x1].reshape(-1, 3).mean(0)
else:
    wc = np.array([196., 222., 234.])
print('물빛', wc.round(1))
S = 4
for e in [p for p in a.ells.split(';') if p.strip()]:
    cx, cy, rx, ry = [float(v) for v in e.split(',')]
    bx0, by0, bx1, by1 = int(cx - rx - 3), int(cy - ry - 3), int(cx + rx + 4), int(cy + ry + 4)
    w, h = (bx1 - bx0) * S, (by1 - by0) * S
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    d.ellipse([((cx - rx) - bx0) * S, ((cy - ry) - by0) * S, ((cx + rx) - bx0) * S, ((cy + ry) - by0) * S], fill=255)
    hl = Image.new('L', (w, h), 0); dh = ImageDraw.Draw(hl)
    dh.arc([((cx - rx * 0.75) - bx0) * S, ((cy - ry * 0.6) - by0) * S, ((cx + rx * 0.55) - bx0) * S, ((cy + ry * 0.9) - by0) * S], 200, 300, fill=255, width=int(1.1 * S))
    M = np.asarray(m.resize((bx1 - bx0, by1 - by0), Image.LANCZOS)).astype(float) / 255
    H = np.asarray(hl.resize((bx1 - bx0, by1 - by0), Image.LANCZOS)).astype(float) / 255
    R = A[by0:by1, bx0:bx1]
    yy = np.linspace(-1, 1, by1 - by0)[:, None, None]
    col = wc[None, None, :] + yy * np.array([-10., -8., -4.])   # 아래쪽(가까운 쪽)이 조금 짙다
    R = R * (1 - M[..., None] * 0.9) + col * (M[..., None] * 0.9)
    R = R * (1 - H[..., None] * 0.7) + np.array([250., 252., 253.]) * (H[..., None] * 0.7)
    A[by0:by1, bx0:bx1] = R
Image.fromarray(np.clip(A, 0, 255).astype('uint8')).save(a.dst)

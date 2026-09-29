#!/usr/bin/env python3
"""s03p04 — 개념 논리 M: 진핵(오른쪽) 가게의 히스톤 실패가 곁방에(작은 70S 저울과 함께) · 가운데 방(핵)엔 주인만이던 것 →
제미나이 v2(오른쪽 가게 곁방의 작은 저울 뺌 · 실패를 옮기라 했더니 아예 지움 — 곁방엔 빈 선반만)를 바탕으로,
가운데(고세균) 가게 선반의 실패(x 583..607 · y 245..278)를 오려 1.25배로 키워 오른쪽 가게 가운데 방 계산대 위, 주인 앞(가운데 x 825 · 바닥 y 350)에 세운다.
+ 오른쪽 아래 반짝이 표식(x 938..952 · y 415..432)을 20px 왼쪽 결로 덮음.
사용: python3 s03p04_spool_to_nucleus.py V2.png OUT.png"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); W, H = im.size
assert (W, H) == (1024, 506), (W, H)
a = np.asarray(im).astype(np.float32)
# --- spool silhouette (hand polygon in source coords) ---
X0, Y0, X1, Y1 = 581, 243, 609, 280
sil = Image.new('L', ((X1-X0)*8, (Y1-Y0)*8), 0); d = ImageDraw.Draw(sil)
def E(x0, y0, x1, y1): d.ellipse([(x0-X0)*8, (y0-Y0)*8, (x1-X0)*8, (y1-Y0)*8], fill=255)
def Rc(x0, y0, x1, y1): d.rectangle([(x0-X0)*8, (y0-Y0)*8, (x1-X0)*8, (y1-Y0)*8], fill=255)
E(583.0, 245.0, 607.5, 257.5)      # top flange
Rc(586.5, 251.0, 604.5, 272.0)     # thread body
E(583.0, 266.5, 607.5, 279.0)      # bottom flange
sil = np.asarray(sil.resize((X1-X0, Y1-Y0), Image.LANCZOS)).astype(np.float32) / 255.0
spr = np.dstack([a[Y0:Y1, X0:X1], sil * 255]).astype(np.uint8)
S = Image.fromarray(spr, 'RGBA')
sc = 1.25
S = S.resize((round(S.width * sc), round(S.height * sc)), Image.LANCZOS)
rgb = S.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=2))
S = Image.merge('RGBA', (*rgb.split(), S.split()[3]))   # re-sharpen after the 1.25× upscale
# --- place on the counter in front of the shopkeeper ---
cx, base = 825, 351
px = int(round(cx - S.width / 2)); py = base - S.height
res = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
# soft contact shadow on the counter
o = np.asarray(res).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W]
sh = np.exp(-(((xx - cx - 3) / (S.width * 0.55)) ** 2 + ((yy - base + 1) / 3.2) ** 2)) * 0.22
o[..., :3] *= (1 - sh[..., None])
res = Image.fromarray(o.astype(np.uint8), 'RGBA')
res.alpha_composite(S, (px, py))
out = np.asarray(res.convert('RGB')).astype(np.float32)
# --- sparkle mark ---
X0w, X1w, Y0w, Y1w, OFF, F = 934, 956, 411, 436, -20, 5
src_ = out.copy()
for x in range(X0w, X1w):
    wx = min(1.0, (x - X0w + 1) / F, (X1w - x) / F)
    for y in range(Y0w, Y1w):
        wy = min(1.0, (y - Y0w + 1) / 3.0, (Y1w - y) / 3.0)
        w = wx * wy
        out[y, x] = out[y, x] * (1 - w) + src_[y, x + OFF] * w
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print('spool box', px, py, S.size)

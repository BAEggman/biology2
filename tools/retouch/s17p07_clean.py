#!/usr/bin/env python3
"""s17p07 — 개념 논리 M 둘: ① 근위(둥근 관) 문이 열려 인산 성냥갑이 밖으로 쏟아지던 것(= 인산 재흡수로 읽힘) ② NCC 문이 열려 있고 자물쇠는 옆 걸쇠 · 소금·염소가 관 밖 →
제미나이 v1(왼쪽 문을 PTH 줄이 묶어 닫음 · 둥근 창으로 관 안 성냥갑이 보임 / 네모 관 문 닫힘 · 금색 자물쇠 + 티백이 걸쇠를 잠금 · 쇠창살 창 너머 관 안에 소금 자루와 염소)을 쓰고 손질:
 a) 가운데 빈 둥근 창(중심 437,280 · 반지름 ~45) 지움 — 줄마다 좌우 관 몸 중앙값 + 세로 흐림 · 그 위를 지나던 PTH 줄은 위아래 줄 조각에서 잰 직선(x = 457 − 0.683(y − 212))으로 다시 그림(두 겹 가장자리 + 밝은 속)
 b) 자루 위 글자 「S L T」(x 803..837 · y 354..371, 창살 기둥 제외) → 자루 흰색
 c) 오른쪽 아래 반짝이 표식(x 922..954 · y 398..432) → 관 벽 · 윤곽선 · 바닥을 옆에서 이어 붙임
사용: python3 s17p07_clean.py V1.png OUT.png"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
assert a.shape == (506, 1024, 3), a.shape
H, W, _ = a.shape
rng = np.random.default_rng(177)
out = a.copy()
lum = a.mean(2)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
# ---- a) empty porthole ----
CX, CY, RX, RY = 437.5, 280.0, 48.0, 46.5
E = ((xx - CX) / RX) ** 2 + ((yy - CY) / RY) ** 2 <= 1.0
fill = out.copy()
for y in range(int(CY - RY) - 1, int(CY + RY) + 2):
    ref = np.concatenate([a[y, 345:388], a[y, 487:497]])
    ref = ref[ref.mean(1) > 150]
    if len(ref) < 5:
        continue
    fill[y, :] = np.median(ref, axis=0)
fill = ndi.gaussian_filter(fill, sigma=(2.0, 0, 0))
noise = rng.normal(0, 1.3, (E.sum(), 3))
out[E] = np.clip(fill[E] + noise, 0, 255)
# soft edge
Eb = ndi.gaussian_filter(E.astype(np.float32), 1.2)
edge = (Eb > 0.02) & (Eb < 0.98) & ~E
out[edge] = a[edge] * (1 - Eb[edge, None]) + fill[edge] * Eb[edge, None]
# redraw the rope across the filled porthole
SS = 8
L = Image.new('L', (W * SS, H * SS), 0); dL = ImageDraw.Draw(L)
C = Image.new('L', (W * SS, H * SS), 0); dC = ImageDraw.Draw(C)
y0r, y1r = CY - RY - 3, CY + RY + 3
def xr(y): return 457.0 - 0.683 * (y - 212.0)
dx, dy = -0.683, 1.0; nrm = math.hypot(dx, dy); ux, uy = dx / nrm, dy / nrm; px_, py_ = -uy, ux
for off in (-2.1, 2.1):
    dL.line([((xr(y0r) + px_ * off) * SS, (y0r + py_ * off) * SS), ((xr(y1r) + px_ * off) * SS, (y1r + py_ * off) * SS)], fill=255, width=int(1.25 * SS))
dC.line([(xr(y0r) * SS, y0r * SS), (xr(y1r) * SS, y1r * SS)], fill=255, width=int(3.2 * SS))
# twist hatches
t = y0r
while t < y1r:
    cxh, cyh = xr(t), t
    dL.line([((cxh - px_ * 2.0 - ux * 1.2) * SS, (cyh - py_ * 2.0 - uy * 1.2) * SS), ((cxh + px_ * 2.0 + ux * 1.2) * SS, (cyh + py_ * 2.0 + uy * 1.2) * SS)], fill=150, width=int(0.8 * SS))
    t += 5.5
Lm = np.asarray(L.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0
Cm = np.asarray(C.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0
reg = ndi.binary_dilation(E, iterations=3)
Lm *= reg; Cm *= reg
core = np.array([196, 188, 170], np.float32)
out = out * (1 - Cm[..., None] * 0.85) + core * (Cm[..., None] * 0.85)
out = out * (1 - Lm[..., None]) + np.array([72, 68, 62], np.float32) * Lm[..., None]
# ---- b) letters on the sack ----
bars = [(814, 824), (837, 847)]
for y in range(354, 372):
    xs = [x for x in range(803, 838) if not any(b0 <= x < b1 for b0, b1 in bars)]
    row = a[y, xs]
    bright = row[row.mean(1) > 185]
    if len(bright) < 4:
        continue
    sc = np.median(bright, axis=0)
    for x in xs:
        if lum[y, x] < sc.mean() - 16:
            out[y, x] = np.clip(sc + rng.normal(0, 1.2, 3), 0, 255)
# ---- c) sparkle ----
X0, X1 = 922, 955
for y in range(396, 434):
    if 422 <= y <= 432:
        out[y, X0:X1] = np.median(a[y, 895:919], axis=0) + rng.normal(0, 1.0, (X1 - X0, 3))   # horizontal outline: row median
    else:
        ref = np.concatenate([a[y, 900:920], a[y, 957:967]])
        out[y, X0:X1] = np.clip(np.median(ref, axis=0) + rng.normal(0, 1.2, (X1 - X0, 3)), 0, 255)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst); print('ok', dst)

#!/usr/bin/env python3
"""touch_h1.py — s45u02 v7 ① 행 4: 오른쪽 줄 가운데 무더기(MR)를 두 겹짜리 「난쟁이」로(윗면 · 첫 겹은 제자리 · 맨 아래 겹 테를 36 px 끌어올림)
· 그 아래와 왼 아래 무더기(LL)에서 MR 로 가던 다리 자리를 꼬투리 안벽으로 메움 · LL 오른 테를 닫음.
v7b(b138 채점 「꼬투리 속 회색 직사각 패치 · LL 테를 곧은 선으로 잘라 먹음」): 메움을 다시 짠다 —
  ① 구멍은 LL 테(x ≤ 688)와 꼬투리 벽선(x ≥ 814)을 건드리지 않는다
  ② 바탕 빛 = 둘레의 **벽 화소만** 경계로 삼은 조화 보간(무더기 · 선 · 벽선은 경계에서 뺌 — 자유 경계)
  ③ 결 = 둘레 벽의 잔결(원 − 흐림)을 12 px 조각으로 떠다 겹쳐 깖(붓 결 · 얼룩을 그대로 옮김)
사용: touch_h1.py in.png out.png"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, gaussian_filter
src, dst = sys.argv[1:3]
O = np.asarray(Image.open(src).convert('RGB')).astype(float)
H, W = O.shape[:2]
rng = np.random.default_rng(11)

hole = np.zeros((H, W), bool)
hole[505:559, 729:814] = True          # MR 아래쪽(난쟁이 아래)
hole[522:552, 689:729] = True          # LL → MR 다리(x 689 부터 — LL 테는 그대로)
# 벽 화소(경계로 쓸 수 있는 것): 초록 · 짙은 선이 아닌 밝은 회녹
gO = O[..., 1] - (O[..., 0] + O[..., 2]) / 2
wall = (gO < 12) & (O.mean(2) > 112) & ~hole
# ── ② 바탕 빛: 둘레 벽 화소만 쓴 정규화 합성곱(가우스 가중 평균 — 두 눈금) · 무더기 · 선은 가중치 0
y0, y1, x0, x1 = 470, 595, 660, 830
F = O[y0:y1, x0:x1].copy()
Hh = hole[y0:y1, x0:x1]; Wl = wall[y0:y1, x0:x1]
def nconv(sig):
    num = gaussian_filter(F * Wl[..., None], (sig, sig, 0)); den = gaussian_filter(Wl.astype(float), sig)
    return num / np.maximum(den, 1e-4)[..., None], den
s1, d1 = nconv(5.0); s2, d2 = nconv(14.0)
wgt = np.clip(d1 / 0.25, 0, 1)[..., None]           # 벽이 가까우면 잔 눈금, 멀면 큰 눈금
smooth = s1 * wgt + s2 * (1 - wgt)
# ── ③ 결: 둘레 벽의 잔결 조각
Rpool = []
for (ya, yb, xa, xb) in [(446, 463, 735, 812), (559, 577, 735, 812), (494, 521, 690, 726)]:
    P = O[ya:yb, xa:xb]; Ws = wall[ya:yb, xa:xb]
    Rr = P - gaussian_filter(P, (4, 4, 0))
    for _ in range(80):
        h = min(12, yb - ya); w = 12
        yy = rng.integers(0, P.shape[0] - h + 1); xx = rng.integers(0, P.shape[1] - w + 1)
        if Ws[yy:yy + h, xx:xx + w].mean() > 0.95: Rpool.append(Rr[yy:yy + h, xx:xx + w])
tex = np.zeros_like(F); wsum = np.zeros(F.shape[:2])
win = np.outer(np.hanning(14)[1:-1], np.hanning(14)[1:-1])
for yy in range(-6, F.shape[0], 6):
    for xx in range(-6, F.shape[1], 6):
        p = Rpool[rng.integers(0, len(Rpool))]
        h, w = p.shape[:2]; ww = win[:h, :w]
        ya, xa = max(0, yy), max(0, xx); yb, xb = min(F.shape[0], yy + h), min(F.shape[1], xx + w)
        if yb <= ya or xb <= xa: continue
        tex[ya:yb, xa:xb] += p[ya - yy:yb - yy, xa - xx:xb - xx] * ww[ya - yy:yb - yy, xa - xx:xb - xx, None]
        wsum[ya:yb, xa:xb] += ww[ya - yy:yb - yy, xa - xx:xb - xx]
tex /= np.maximum(wsum, 1e-6)[..., None]
fill = smooth + tex
M = gaussian_filter(Hh.astype(float), 0.8); M[Hh] = 1.0
F2 = F * (1 - M[..., None]) + fill * M[..., None]
A = O.copy(); A[y0:y1, x0:x1] = F2
print('wall px', int(Wl.sum()), 'hole px', int(Hh.sum()), 'patches', len(Rpool))

# 맨 아래 겹 테(541 ~ 558)를 36 px 올려 붙임(무더기 화소만 · 꼬투리 벽선 x ≥ 815 는 뺌 · LL 다리 끝을 끌고 오지 않게 x 734 부터)
L0, L1, SH, X0, X1 = 541, 559, 36, 734, 818
Q = O[L0:L1, X0:X1]
gq = Q[..., 1] - (Q[..., 0] + Q[..., 2]) / 2; lum = Q.mean(axis=2)
stack = (gq > 14) | (lum < 100)
stack[:, (815 - X0):] = False
stack = binary_dilation(stack, iterations=1)
Ms = gaussian_filter(stack.astype(float), 0.7)
reg = A[L0 - SH:L1 - SH, X0:X1]
A[L0 - SH:L1 - SH, X0:X1] = reg * (1 - Ms[..., None]) + Q * Ms[..., None]

im2 = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
d = ImageDraw.Draw(im2)
# LL 가운데 겹 끝 닫기 — 다리가 붙어 있던 겹(524 ~ 548)이 2 ~ 4 px 불룩한 쿠션 끝으로 끝나게
d.line([(684.0, 523.5), (687.0, 527.0), (688.6, 533.0), (688.8, 539.0), (687.8, 544.5), (685.0, 548.5)], fill=(40, 48, 30), width=2, joint='curve')
im2.save(dst)
print('ok', dst)

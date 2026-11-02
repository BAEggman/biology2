#!/usr/bin/env python3
"""touch_h1.py — s45u02 v7 ① 행 4: 오른쪽 줄 가운데 무더기(MR)를 두 겹짜리 「난쟁이」로(윗면 · 첫 겹은 제자리 · 맨 아래 겹 테를 36 px 끌어올림)
· 그 아래와 왼 아래 무더기(LL)에서 MR 로 가던 다리 자리를 꼬투리 안벽으로 메움(둘레 벽 표본에 맞춘 2차 곡면 + 고운 얼룩) · LL 오른 테를 닫음.
(독립 검토 1순위 — 같은 줄 · 같은 너비의 셋 가운데 하나만 낮다 = 약속 #126 · 낱장 쿠션은 c7a 에서 이미 걷음)
사용: touch_h1.py in.png out.png"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, gaussian_filter
src, dst = sys.argv[1:3]
O = np.asarray(Image.open(src).convert('RGB')).astype(float)
H, W = O.shape[:2]
rng = np.random.default_rng(7)

hole = np.zeros((H, W), bool)
hole[505:559, 719:816] = True          # MR 아래쪽
hole[523:551, 685:729] = True          # LL → MR 다리
hole[493:523, 686:728] = True          # 두 다리 사이 벽도 함께(밝은 결 경계가 남지 않게) — MR 왼 테(x ≥ 728)는 건드리지 않음
# 벽 표본(무더기 · 다리 · 벽선이 없는 곳)
S = np.zeros((H, W), bool)
S[560:574, 722:812] = True             # MR 와 LR 사이
S[497:521, 690:718] = True             # 두 다리 사이(채우기 전 원래 벽)
S[552:558, 690:718] = True
S[448:461, 745:810] = True             # TR 와 MR 사이
P = O[S]; g = P[:, 1] - (P[:, 0] + P[:, 2]) / 2
keep = (g < 14) & (P.mean(1) > 105)    # 초록 · 짙은 선 빼기
ys, xs = np.nonzero(S); ys, xs = ys[keep], xs[keep]; P = P[keep]
def feats(x, y):
    x = (x - 760) / 60.0; y = (y - 520) / 60.0
    return np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], 1)
F = feats(xs.astype(float), ys.astype(float))
coef, *_ = np.linalg.lstsq(F, P, rcond=None)
# 둘레 6 px 의 벽 화소까지 곡면으로 천천히 섞는다(경계 단차 없애기) — 무더기 · 다리 · 선은 건드리지 않음
gO = O[..., 1] - (O[..., 0] + O[..., 2]) / 2
wallish = (gO < 14) & (O.mean(2) > 105)
ring = binary_dilation(hole, iterations=6) & ~hole & wallish
zone = hole | ring
hy, hx = np.nonzero(zone)
fillv = feats(hx.astype(float), hy.astype(float)) @ coef
n = gaussian_filter(rng.normal(0, 1, (H, W)), (1.4, 2.2)); n = n / (n[hole].std() + 1e-6) * 3.0
A = O.copy()
A[hy, hx] = fillv + n[hy, hx][:, None] * np.array([1.0, 1.0, 0.85])
Hm = np.clip(gaussian_filter(hole.astype(float), 3.0) * 1.6, 0, 1)
Hm[hole] = 1.0; Hm[~zone] = 0.0
A = O * (1 - Hm[..., None]) + A * Hm[..., None]
print('wall samples', len(P), 'resid std', (P - F @ coef).std(0).round(1))

# 맨 아래 겹 테(541 ~ 558)를 36 px 올려 붙임(무더기 화소만 · 꼬투리 벽선 x ≥ 815 는 뺌)
L0, L1, SH, X0, X1 = 541, 559, 36, 734, 818   # x 734 부터 — LL 다리의 오른 끝(541 ~ 546)을 끌고 오지 않게
Q = O[L0:L1, X0:X1]
gq = Q[..., 1] - (Q[..., 0] + Q[..., 2]) / 2; lum = Q.mean(axis=2)
stack = (gq > 14) | (lum < 100)
stack[:, (815 - X0):] = False
stack = binary_dilation(stack, iterations=1)
M = gaussian_filter(stack.astype(float), 0.7)
reg = A[L0 - SH:L1 - SH, X0:X1]
A[L0 - SH:L1 - SH, X0:X1] = reg * (1 - M[..., None]) + Q * M[..., None]

im2 = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
d = ImageDraw.Draw(im2)
d.line([(683.5, 521), (685.0, 526), (686.0, 532), (686.2, 538), (685.6, 544), (684.0, 549)], fill=(38, 46, 30), width=2, joint='curve')
im2.save(dst)
print('ok', dst, 'hole px', int(hole.sum()))

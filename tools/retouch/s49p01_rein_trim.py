#!/usr/bin/env python3
"""s49p01 — 개념 논리 M(소마토스타틴은 인슐린·글루카곤을 둘 다 억제): δ(삼각 모자)가 두 손바닥으로 β 와 PP 를 누르고 α 는 멀던 것 →
제미나이 새 대화 v2 + 같은 대화 후속(v3): δ 가 셋째 창 안에서 두 주먹으로 끈 두 가닥을 고삐처럼 당김 — 한 가닥은 α 곤봉 머리의 매듭,
한 가닥은 β 국자 자루의 매듭. 창턱의 「아무도 들지 않은 배턴」은 그대로.
제미나이가 두 번 다 **곤봉 매듭 ↔ 국자 매듭을 잇는 셋째 끈**을 더 그렸고(후속으로 지우라 해도 가늘게만 함) 그것을 손으로 지운다:
  ① 포도 자루 둘레(x 355..421 · y 343..489): 원본(설치본)의 자루를 통째로 — 위 끈(δ→곤봉) 띠만 v3 그대로.
     (원본과 v3 는 자루 윤곽이 맞고 포도알 자리만 다르다 — 띠만 붙이면 포도알이 어긋난다.)
  ② 곤봉 매듭 곁 ~ 국자 매듭(x 309..637): 셋째 끈 띠(중심선 ±4.5, 가장자리 2px 섞음)에 원본을 붙임.
     토막별로 재 보니 원본↔v3 어긋남은 0px(창틀·창턱·벽 모서리·국자 자루·손끝이 제자리) — 옮기지 않는다.
     v3 가 원본보다 몇 단계 어둡고 누렇다(V−O ≈ −5..−15, 창 안쪽은 파랑이 −15) → 띠 둘레 고리 가운데 **두 그림 모두 평평한 화소**
     (기울기 < 5 — 선 곁 1px 어긋남은 빼고 톤 차이만 남김)의 V−O 를 가우스(σ5, 모자라면 σ12)로 번져 띠 안 원본에 더해
     **톤을 v3 에 맞춘다**(안 그러면 밝고 푸른 줄이 남는다).
     곤봉 매듭 바로 곁(x < 320)은 원본 곤봉이 v3 곤봉과 다른 자리라 원본 대신 v3 창 안쪽 회색 한 색 + 잔잡음.
     지우지 않는 것: 위 끈(중심 −4.5..+3.8 — 아래 윤곽 한가운데가 +3.3이고 매듭 곁에서 셋째 끈 윗 윤곽과 1px 붙어 있다) ·
     v3 곤봉(밝은 나무 + 2px) · 국자 매듭 고리(왼쪽 윤곽 x 636→633, y 503..512)와 매듭 몸통(x ≥ 637).
  ③ 오른쪽 아래 반짝이 표식 · 왼쪽 아래 흐린 낙서(원본에도 있던 것)를 둘레 바닥 한 색으로 덮음.
사용: python3 s49p01_rein_trim.py V3.png ORIG.png OUT.png [반짝이 x0,x1,y0,y1] [낙서 x0,x1,y0,y1]"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

v3p, origp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
V = np.asarray(Image.open(v3p).convert('RGB')).astype(np.float64)
O = np.asarray(Image.open(origp).convert('RGB')).astype(np.float64)
assert V.shape == O.shape == (1024, 1024, 3), (V.shape, O.shape)
H, W = V.shape[:2]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
rng = np.random.default_rng(4901)

# 중심선 — v3 에서 원본과의 차이 무게중심으로 잰 직선(잔차 평균 0.5px)
def cE(x): return 0.43588 * x + 228.222     # 셋째 끈(곤봉 매듭 → 국자 매듭)
def cU(x): return 0.15033 * x + 313.584     # 위 끈(δ → 곤봉 매듭)
UP_HALF = 4.5
# 위 끈 보호: 위로 4.5 · 아래로 3.8(아래 윤곽 한가운데가 중심+3.3 — 매듭 곁에서 셋째 끈 윗 윤곽과 1px 붙어 있다)
up_band = ((yy - cU(xx)) >= -UP_HALF) & ((yy - cU(xx)) <= 3.8)

Vl = V.mean(axis=2)
diff = np.abs(V - O).mean(axis=2)

# v3 곤봉(매듭 곁 밝은 나무) 보호
club = (xx >= 296) & (xx <= 332) & (yy >= 352) & (yy <= 392) & (Vl > 150) & (V[..., 0] - V[..., 2] > 18)
club = ndi.binary_dilation(club, iterations=2)

# ---- ② 셋째 끈 띠 ----
t = np.abs(yy - cE(xx))
wband = np.clip((6.5 - t) / 2.0, 0, 1)
wband[(xx < 309) | (xx > 637)] = 0
wband *= np.clip((xx - 309) / 3.0, 0, 1)
# 국자 매듭 고리(왼쪽 윤곽 x≈636→633, y 503..512)와 매듭 몸통은 v3 그대로
xloop = np.maximum(633.0, 636.0 - (yy - 503.0))
knot_l = ((yy >= 503) & (xx >= xloop - 0.5)) | ((yy >= 499) & (xx >= 637))
wband[knot_l] = 0
bag_rect = (xx >= 355) & (xx < 421) & (yy >= 343) & (yy < 489)
wband[bag_rect] = 0
wband[up_band | club] = 0

# 톤 맞춤 — 띠 둘레 고리 가운데 **두 그림 모두 평평한 화소**(기울기 < 5)만으로 V−O 를 번진다(선 곁 1px 어긋남은 빼고, 톤 차이는 살림)
gV = ndi.gaussian_gradient_magnitude(Vl, 1.0)
gO = ndi.gaussian_gradient_magnitude(O.mean(axis=2), 1.0)
ring = ndi.binary_dilation(wband > 0, iterations=7) & ~ndi.binary_dilation(wband > 0, iterations=1)
ring &= (np.abs(yy - cU(xx)) > UP_HALF + 1) & ~bag_rect & ~club & (gV < 5) & (gO < 5)
glob = np.median((V - O)[ring], axis=0)
D = np.zeros_like(V)
for k in range(3):
    acc = None
    for sig in (5.0, 12.0):
        num = ndi.gaussian_filter((V[..., k] - O[..., k]) * ring, sig)
        den = ndi.gaussian_filter(ring.astype(float), sig)
        est = np.where(den > 2e-3, num / np.maximum(den, 1e-6), np.nan)
        acc = est if acc is None else np.where(np.isnan(acc), est, acc)
    D[..., k] = np.where(np.isnan(acc), glob[k], acc)
print('band ring px', int(ring.sum()), 'global V-O', glob.round(1))
P = O + D
# 곤봉 매듭 바로 곁(x < 320)은 원본의 곤봉이 v3 와 다른 자리라 원본을 못 쓴다 → v3 창 안쪽 회색 한 색 + 잔잡음
ref = (xx >= 320) & (xx < 344) & (yy >= 349) & (yy < 356) & (Vl > 95) & (Vl < 170) & ((V.max(axis=2) - V.min(axis=2)) < 25)
g0 = V[ref].mean(axis=0)
flat = ndi.gaussian_filter(g0 + rng.normal(0, 3.0, V.shape), sigma=(0.8, 0.8, 0))
P = np.where((xx < 320)[..., None], flat, P)
print('window gray', g0.round(1))

# ---- ① 자루 ----
wbag = ndi.uniform_filter(bag_rect.astype(float), 3)
wbag[up_band] = 0
ring_b = ndi.binary_dilation(bag_rect, iterations=6) & ~bag_rect & ~up_band & (gV < 5) & (gO < 5)
off_b = np.median((V - O)[ring_b], axis=0)
print('bag ring px', int(ring_b.sum()), 'bag offset', off_b.round(1))
Pb = O + off_b

out = V * (1 - wband[..., None]) + P * wband[..., None]
out = out * (1 - wbag[..., None]) + Pb * wbag[..., None]

# ---- ③ 반짝이 · 흐린 낙서 ----
def flat_fill(a, x0, x1, y0, y1, feather=8, sigma=1.8):
    ringpx = np.concatenate([a[y0 - 12:y0, x0:x1].reshape(-1, 3), a[y1:y1 + 12, x0:x1].reshape(-1, 3),
                             a[y0:y1, x0 - 12:x0].reshape(-1, 3), a[y0:y1, x1:x1 + 12].reshape(-1, 3)])
    bg = np.median(ringpx, axis=0)
    f = ndi.gaussian_filter(np.clip(bg + rng.normal(0, sigma, (y1 - y0, x1 - x0, 3)), 0, 255), sigma=(0.8, 0.8, 0))
    w = np.ones((y1 - y0, x1 - x0))
    for i in range(feather):
        tt = (i + 1) / (feather + 1)
        w[i, :] *= tt; w[-1 - i, :] *= tt; w[:, i] *= tt; w[:, -1 - i] *= tt
    a[y0:y1, x0:x1] = a[y0:y1, x0:x1] * (1 - w[..., None]) + f * w[..., None]
    return bg
SPARK = tuple(int(v) for v in sys.argv[4].split(',')) if len(sys.argv) > 4 else (864, 938, 870, 944)
SCRIB = tuple(int(v) for v in sys.argv[5].split(',')) if len(sys.argv) > 5 else (26, 160, 896, 966)
print('spark bg', flat_fill(out, *SPARK).astype(int))
print('scribble bg', flat_fill(out, *SCRIB).astype(int))

Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print('saved', dst)

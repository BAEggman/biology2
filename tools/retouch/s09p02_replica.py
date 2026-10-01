#!/usr/bin/env python3
"""s09p02 — 개념 논리 m 3(복제 평판법: 대부분 다시 자라고 몇 자리만 빈다): 오른쪽 위 둘째 배지가 텅 비어 「옮겨 찍었더니 아무것도 안 자란다」로 읽히던 것 →
왼쪽 배지의 군락 **그림(고역)** 을 오른쪽 배지에 같은 배치로 옮겨 그리고 **세 자리만 비운다** — 빈 세 자리의 군락이 재조합체(삽입 불활성화로 내성 유전자가 망가짐).
  ① 두 배지의 한천 가장자리 타원을 맞춤(왼쪽: 바깥에서 셋째 테 · 오른쪽: 안에서 첫 테 — EllipseModel, 상위 75% 잔차만 다시 맞춤):
     왼쪽 (661.1, 159.7) 반축 98.5 × 49.9 · 오른쪽 (906.8, 203.0) 반축 102.3 × 56.7 (둘 다 θ ≈ 3.1 — 거의 가로).
  ② 군락 층 = 왼쪽 한천 안(타원 0.9) 밝기 − 중앙값 41(한천 바탕) — 윤곽선은 어둡게, 속은 조금 밝게. 바탕 색(왼쪽은 회록 · 오른쪽은 크림)은 옮기지 않는다.
  ③ 오른쪽 타원 좌표를 왼쪽 타원 좌표로 되돌려(반축 비로 늘임) 군락 층을 읽고 오른쪽 그림에 더함 · 가장자리 0.85→0.9 로 서서히 · 액자 선(x ≥ 952) 은 그대로.
  ④ 빼는 세 군락(왼쪽 좌표 — 오른쪽 배지가 액자 선에 잘려 보이는 왼쪽 60% 안에서 고름): 위 가운데 큰 것 (650, 122) · 왼쪽 가운데 고리 (607, 167) ·
     가운데 오른쪽 고리 (688, 141) — 각 고리 둘레 3·2px 까지 층을 0 으로.
  ⑤ 빈 세 자리에 옅은 연필 회색 점선 고리(14 토막 · 굵기 1.4 · 4배 덧그림) — 비교해 찾게.
사용: python3 s09p02_replica.py ORIG.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

op, dst = sys.argv[1], sys.argv[2]
A = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
H, W = A.shape[:2]
L1 = (661.1, 159.7, 98.5, 49.9)
R1 = (906.8, 203.0, 102.3, 56.7)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
bg = np.stack([ndi.median_filter(A[..., k], size=41) for k in range(3)], axis=2)
D = A - bg
uL = (xx - L1[0]) / L1[2]; vL = (yy - L1[1]) / L1[3]
rL = np.sqrt(uL ** 2 + vL ** 2)
D[rL > 0.9] = 0
# ④ 빼는 세 군락
OMIT = [(650, 122, 12.5, 8.5), (607, 167, 11.5, 7.5), (688, 141, 12.5, 7.5)]   # (cx, cy, rx, ry) 왼쪽 좌표 — 군락 고리 크기
for (cx, cy, rx, ry) in [(c[0], c[1], c[2] + 3, c[3] + 2) for c in OMIT]:
    e = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    D[e] = 0
# ③ 오른쪽 → 왼쪽 되돌림
uR = (xx - R1[0]) / R1[2]; vR = (yy - R1[1]) / R1[3]
rR = np.sqrt(uR ** 2 + vR ** 2)
sx = L1[0] + uR * L1[2]; sy = L1[1] + vR * L1[3]
Dw = np.stack([ndi.map_coordinates(D[..., k], [sy, sx], order=1, mode='constant') for k in range(3)], axis=2)
w = np.clip((0.9 - rR) / 0.05, 0, 1)
w[:, 951:] = 0
out = A + Dw * w[..., None]
# ⑤ 빈 세 자리에 옅은 점선 고리(연필 회색) — 「여기 있어야 할 군락이 안 자랐다」를 눈으로 찾게
from PIL import ImageDraw
S = 4
ov = Image.new('L', (W * S, H * S), 0)
d = ImageDraw.Draw(ov)
for (cx, cy, rx, ry) in OMIT:
    X = R1[0] + (cx - L1[0]) / L1[2] * R1[2]
    Y = R1[1] + (cy - L1[1]) / L1[3] * R1[3]
    RX = rx * R1[2] / L1[2]; RY = ry * R1[3] / L1[3]
    n = 14
    for k in range(n):
        a0 = 2 * np.pi * k / n; a1 = a0 + 2 * np.pi / n * 0.55
        ts = np.linspace(a0, a1, 6)
        pts = [((X + RX * np.cos(tt)) * S, (Y + RY * np.sin(tt)) * S) for tt in ts]
        d.line(pts, fill=255, width=int(1.4 * S))
    print('empty spot', (round(X, 1), round(Y, 1)), 'r', (round(RX, 1), round(RY, 1)))
ov = np.asarray(ov.resize((W, H), Image.LANCZOS)).astype(np.float64) / 255.0
ink = np.array([110.0, 100.0, 92.0])
a_ = 0.7 * ov[..., None]
out = out * (1 - a_) + ink * a_
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('done')

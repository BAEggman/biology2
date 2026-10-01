#!/usr/bin/env python3
"""s46p02 — 판째 다시 그리기 v4(문 둘 · 2|3 통벽 · 둘째 문이 넷째 방 안으로 열림 · 머리 있는 사람)의 넷째 방 손질.
v4 문짝은 아래 끝이 방 바닥 앞 모서리(y≈719)를 넘어 건물 앞 띠까지 내려왔고(y≈738), 받침대는 방 오른쪽 구석에 멀리 떨어져 있었다.
(후속 v5 는 문짝을 뒷벽에 닫힌 문처럼 정면으로 그렸고, v4 를 입력으로 한 새 대화 v6 은 문짝을 더 키워 더 내려보냄 — 둘 다 버림.)
v3(같은 대화 앞 판 — 넷째 방이 비어 있음 · 둘째 문이 셋째 방 안으로 열려 버린 판)과 v4 는 어긋남 0px 이라:
  ① 넷째 방 네모(636..802 × 450..742 — 왼 칸막이 선 · 방 안 · 앞 띠까지)를 v3 의 빈 방 화소로 되돌리고(둘레 4px 고리 차를 σ6 로 번져 톤 맞춤),
  ② v4 문짝(다각형 (642,543)(690,530)(698,535)(698,660)(696,662)(696,738)(688,738)(642,720) — 넓히지 않음: 넓히면 뒤 바닥선이 줄어 따라와 문짝 곁에 짧은 금이 남는다)을 위 끝(y 530)에 붙인 채 세로로 0.870 배 줄여
     바깥 끝 아래 ≈711 · 경첩 쪽 아래 ≈695 — 바닥 앞 모서리(719) 안에 서게 다시 얹고,
  ③ 받침대(다각형 (737,679)(757,678)(784,688)(784,710)(763,712)(737,701) — 위로 닿던 벽 모서리 선·그늘은 뺌)를 왼쪽으로 37px 옮겨 문짝 바깥 끝 아래에 닿게(먼저 깔고 문짝을 위에).
사용: python3 s46p02_door4.py V3.png V4.png OUT.png"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

p3, p4, dst = sys.argv[1:4]
A = np.asarray(Image.open(p3).convert('RGB')).astype(np.float64)
B = np.asarray(Image.open(p4).convert('RGB')).astype(np.float64)
H, W = B.shape[:2]
# ① 빈 방으로
hole = np.zeros((H, W), bool); hole[450:742, 636:802] = True
ring = ndi.binary_dilation(hole, iterations=4) & ~hole
D = B - A
num = np.stack([ndi.gaussian_filter(D[..., q] * ring, 6) for q in range(3)], axis=2)
den = ndi.gaussian_filter(ring.astype(float), 6)[..., None]
corr = num / np.maximum(den, 1e-6)
out = B.copy()
out[hole] = (A + corr)[hole]
# ③ 받침대
d = ndi.gaussian_filter(np.abs(A - B).mean(axis=2), 1.0)
rb = np.zeros((H, W), bool); rb[674:716, 733:788] = True
# 받침대 = 다각형(737,679)(757,678)(784,688)(784,710)(763,712)(737,701) — 그 위로 닿던 뒷벽·오른벽 모서리 선과 회색 그늘은 뺀다
pb = Image.new('L', (W, H), 0)
ImageDraw.Draw(pb).polygon([(737, 679), (757, 678), (784, 688), (784, 710), (763, 712), (737, 701)], fill=255)
mb = np.asarray(pb) > 0
mb = mb & rb
ys, xs = np.nonzero(mb)
by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
DX = -37
ba = ndi.gaussian_filter(mb[by0:by1, bx0:bx1].astype(float), 0.6)
seg = out[by0:by1, bx0 + DX:bx1 + DX]
out[by0:by1, bx0 + DX:bx1 + DX] = seg * (1 - ba[..., None]) + B[by0:by1, bx0:bx1] * ba[..., None]
# ② 문짝
poly = Image.new('L', (W, H), 0)
ImageDraw.Draw(poly).polygon([(642, 543), (690, 530), (698, 535), (698, 660), (696, 662), (696, 738), (688, 738), (642, 720)], fill=255)
ml = np.asarray(poly) > 0
ys, xs = np.nonzero(ml)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
f = 0.870
nh = int(round((y1 - y0) * f))
sp = np.asarray(Image.fromarray(B[y0:y1, x0:x1].astype(np.uint8)).resize((x1 - x0, nh), Image.LANCZOS)).astype(np.float64)
al = np.asarray(Image.fromarray((ml[y0:y1, x0:x1] * 255).astype(np.uint8)).resize((x1 - x0, nh), Image.LANCZOS)).astype(np.float64) / 255
al = ndi.gaussian_filter(al, 0.5)
seg = out[y0:y0 + nh, x0:x1]
out[y0:y0 + nh, x0:x1] = seg * (1 - al[..., None]) + sp * al[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('leaf', (x0, y0, x1, y1), '→ bottom', y0 + nh, '| block', (bx0, by0, bx1, by1), '→ x', bx0 + DX)

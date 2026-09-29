#!/usr/bin/env python3
"""s11p01 — 개념 논리 M(R9 · 두 번 실패): 지연가닥의 짧은 판자들이 띠를 **가로질러** 침목처럼 놓여(뾰족한 끝이 띠 밖) 「조각이 분기점에서
멀어지는 쪽으로 5′→3′ 로 자란다」가 안 읽히던 것 → 판자 다섯을 띠를 **따라** 한 줄로(틈을 두고 따로따로) · 판자마다 분기점 쪽 끝에 못 하나 ·
뾰족한 끝은 분기점 반대(왼쪽 아래).
두 걸음:
  ① 제미나이에게 **지우기만**(아래 갈래의 판자·못 전부 · 모래시계 인부 빈손 · 용접공과 불꽃 그대로) → CLEAN. 원본과 다른 곳(왼쪽 아래 4분의 1 안,
     σ2 밝기 차 > 14 → 닫기 3 · 메움 · 넓힘 5 · σ2 섞음)만 원본에 옮긴다 — 나머지는 원본 그대로.
  ② 판자는 **손으로**: 원본 위 갈래의 긴 판자(중심 (381.6,316.9) · 축 32.19° · 반폭 15 · 끝 뾰족 u 155→186)를 제 축으로 펴서 떼어 낸 뒤,
     짧은 판자 = 곧은 몸 + 뾰족한 끝(32px 를 18px 로 눌러) + 뭉툭한 끝 윤곽 3px · 폭은 0.8 배(짧은 판자에 긴 판자 폭·끝을 그대로 쓰면 당근처럼 뭉툭해진다). 아래 갈래 축 (−0.707, 0.707)에 맞춰 돌려 붙이되, 두께 면이 보는 쪽(오른쪽 아래)에
     오도록 뒤집는다. 못은 서 있어야 하므로 판자와 함께 돌리지 않고 곧게 그린다(회색 머리 + 짙은 자루).
     판자 자리(띠 가운데 줄 (496,640)에서 t · 옆으로 o): [52,128](새 판자 · o+30 · 인부 손끝) · [136,210] · [218,290] · [298,372] · [380,456].
     셋째·넷째 사이 틈(t≈294)이 용접 불꽃 자리 — CLEAN 의 불꽃을 판자 위에 다시 얹는다.
  ③ 오른쪽 아래 반짝이 표식(원본부터 있던 것)은 별 화소만 둘레에서 메움(Telea).
사용: python3 s11p01_okazaki_planks.py ORIG.png CLEAN.png OUT.png"""
import sys
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ndi
op, cp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
C = np.asarray(Image.open(cp).convert('RGB')).astype(np.float64)
H, W = O.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]
# ① CLEAN 의 바뀐 곳만
d = ndi.gaussian_filter(np.abs(O - C).mean(axis=2), 2.0)
m = (d > 14) & (xx < 700) & (yy > 560)
m = ndi.binary_closing(m, iterations=3)
m = ndi.binary_fill_holes(m)
m = ndi.binary_dilation(m, iterations=5) & (xx < 720) & (yy > 540)
w = ndi.gaussian_filter(m.astype(float), 2.0)
base = O * (1 - w[..., None]) + C * w[..., None]
print('clean mask px', int(m.sum()))
# ② 긴 판자 떼어 내기
c = np.array([381.6, 316.9]); ang = np.radians(32.19)
du = np.array([np.cos(ang), np.sin(ang)]); dv = np.array([-du[1], du[0]])
U0, U1, V = -180, 190, 24
us = np.arange(U0, U1); vs = np.arange(-V, V + 1)
UU, VV = np.meshgrid(us, vs)
mapx = (c[0] + du[0] * UU + dv[0] * VV).astype(np.float32)
mapy = (c[1] + du[1] * UU + dv[1] * VV).astype(np.float32)
long_rgb = cv2.remap(O.astype(np.float32), mapx, mapy, cv2.INTER_LINEAR)
def half(u):          # 판자(윤곽 포함) 반폭
    u = np.asarray(u, float)
    hw = np.where(u < 155, 18.5, 18.5 * np.clip((187 - u) / 32.0, 0, 1))
    return np.where(u < -177, 0, hw)
long_a = (np.abs(VV) <= half(UU)).astype(np.float32)
long_a = ndi.gaussian_filter(long_a, 0.7)
SW = 0.80   # 폭 줄임(긴 판자 반폭 18.5 → 14.8)
TIP = 18    # 뾰족한 끝 길이(긴 판자의 32px 를 눌러)
OUTL = np.array([58.0, 40.0, 26.0])
def short_plank(L):
    """짧은 판자 스프라이트(행 = v, 열 = u): 곧은 몸(긴 판자 u 10..) + 눌린 뾰족한 끝(u 155..187 → TIP px) · 뭉툭한 끝은 윤곽 3px 로 닫는다
    (긴 판자의 뭉툭한 끝을 그대로 쓰면 그 못이 같이 딸려 온다)."""
    x = np.arange(L, dtype=np.float64)
    u = np.where(x < L - TIP, 10 + x, 155 + (x - (L - TIP)) * (32.0 / TIP))
    v = np.arange(-V, V + 1, dtype=np.float64)
    XX, VV2 = np.meshgrid(u, v)
    src_v = VV2 / SW
    mx = (XX - U0).astype(np.float32); my = (src_v + V).astype(np.float32)
    rgb = cv2.remap(long_rgb, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    a = (np.abs(src_v) <= half(XX)).astype(np.float32)
    rgb[:, 0:3] = OUTL
    a = ndi.gaussian_filter(a, 0.6)
    return rgb, a
c0 = np.array([496.0, 640.0]); dlow = np.array([-0.7071, 0.7071]); nb = np.array([0.7071, 0.7071])
planks = [(52, 128, 30), (136, 210, 0), (218, 290, -8), (298, 372, -8), (380, 456, -4)]
out = base.copy()
nails = []
for (t0, t1, o) in planks:
    L = t1 - t0
    rgb, a = short_plank(L)
    rgb = rgb[::-1]; a = a[::-1]                     # 두께 면을 보는 쪽으로
    P0 = c0 + dlow * t0 + nb * o
    mvec = np.array([0.7071, 0.7071])                # 스프라이트 v(+) → 오른쪽 아래
    A = np.array([[dlow[0], mvec[0], P0[0] - V * mvec[0]],
                  [dlow[1], mvec[1], P0[1] - V * mvec[1]]], np.float32)
    warped = cv2.warpAffine(rgb.astype(np.float32), A, (W, H), flags=cv2.INTER_LINEAR)
    wa = cv2.warpAffine(a.astype(np.float32), A, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    out = out * (1 - wa) + warped * wa
    nails.append(c0 + dlow * (t0 + 9) + nb * o)
# 못 — 곧게 선 못(자루 13px · 머리 타원)
img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
from PIL import ImageDraw
dr = ImageDraw.Draw(img)
for (nx, ny) in nails:
    dr.line([(nx, ny), (nx + 1, ny - 13)], fill=(40, 40, 42), width=3)
    dr.line([(nx - 0.5, ny), (nx + 0.5, ny - 12)], fill=(120, 120, 125), width=1)
    dr.ellipse([nx - 5, ny - 17, nx + 7, ny - 11], fill=(150, 150, 156), outline=(25, 25, 25))
out = np.asarray(img).astype(np.float64)
# 불꽃을 판자 위에 다시
sp = np.zeros((H, W), bool)
sp[790:890, 230:340] = True
Cl = C.mean(axis=2)
spark = sp & (Cl > 200) & (C[..., 0] > 215) & (C[..., 2] < C[..., 0] - 10)
spark = ndi.binary_dilation(spark, iterations=1)
sw = ndi.gaussian_filter(spark.astype(float), 0.8)
out = out * (1 - sw[..., None]) + C * sw[..., None]
print('spark px', int(spark.sum()))
# ③ 반짝이
o8 = np.clip(out, 0, 255).astype(np.uint8)
L8 = o8.mean(axis=2).astype(np.float64)
loc = L8 - ndi.median_filter(L8, 21)
star = np.zeros((H, W), bool)
bx0, bx1, by0, by1 = 860, 960, 860, 960
ring = np.concatenate([L8[by0:by0 + 6, bx0:bx1].ravel(), L8[by1 - 6:by1, bx0:bx1].ravel(), L8[by0:by1, bx0:bx0 + 6].ravel(), L8[by0:by1, bx1 - 6:bx1].ravel()])
bg = np.median(ring)
star[by0:by1, bx0:bx1] = (L8[by0:by1, bx0:bx1] > bg + 3) | (loc[by0:by1, bx0:bx1] > 4)   # 별의 속(넓고 평평한 밝음)은 국소 대비로 안 잡혀 밝기로도 잡는다
star = ndi.binary_opening(star, iterations=1)
star = ndi.binary_dilation(star, iterations=4)
print('star px', int(star.sum()))
o8 = cv2.inpaint(o8, star.astype(np.uint8) * 255, 5, cv2.INPAINT_TELEA)
Image.fromarray(o8).save(dst)
print('saved', dst)

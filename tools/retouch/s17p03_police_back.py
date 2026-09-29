#!/usr/bin/env python3
"""s17p03 — 개념 논리 M(ENaC: Na⁺ 는 관강에서 나와야 = 재흡수): 짐꾼들이 운하에 소금을 쏟던 것 →
제미나이 같은 대화 v3(무릎 꿇은 짐꾼이 체로 운하에서 젖은 소금을 건져 자루에 담음 · 자루 진 짐꾼들은 운하를 등지고 왼쪽 자루 더미로 ·
로마 병정은 칼끝으로 벽의 배수구를 비틀어 알갱이를 운하로(K⁺ 분비) · β 사람은 운하 가장자리에서 흰 가루를 운하로)을 쓰고,
v1–v3 이 바꿔 버린 경관(한 손을 입에 대 물맛을 보는 몸짓이 사라지고 곁에 감긴 호스가 생김)만 설치본에서 되옮김:
 다각형 [(540,735),(645,735),(722,760),(722,988),(370,988),(370,816),(452,816),(452,797),(540,797)] — 감긴 호스까지 덮음 · 가장자리 흐림 3px
 · 따라 들어온 설치본의 흩어진 소금 알갱이(x 370..456 · y 812..852 — 쓸어 담던 통은 이제 없음)는 cv2 인페인트
 · 오른쪽 아래 반짝이 표식은 운하 물 결을 50px 왼쪽에서 옮겨 덮음(가장자리 8px 섞음)
사용: python3 s17p03_police_back.py V3.png ORIG.png OUT.png"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
v3p, op, dst = sys.argv[1], sys.argv[2], sys.argv[3]
V = np.asarray(Image.open(v3p).convert('RGB')).astype(np.float32)
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float32)
assert V.shape == O.shape == (1024, 1024, 3)
rng = np.random.default_rng(173)
out = V.copy()
import cv2
# policeman + hose from the original
M = Image.new('L', (1024, 1024), 0)
ImageDraw.Draw(M).polygon([(540, 735), (645, 735), (722, 760), (722, 988), (370, 988), (370, 816), (452, 816), (452, 797), (540, 797)], fill=255)
w = ndi.gaussian_filter(np.asarray(M).astype(np.float32) / 255.0, 3.0)[..., None]
out = out * (1 - w) + O * w
# the original's scattered salt grains that came along (x 370..456 · y 812..852) → inpaint (the tub they spilled from is gone)
lum = out.mean(2)
gm = np.zeros((1024, 1024), np.uint8)
g = (lum[812:852, 370:456] < 150)
g = ndi.binary_dilation(g, iterations=3)
gm[812:852, 370:456] = g.astype(np.uint8) * 255
# keep the long diagonal wall edge at the lower left (x < 392 below y 836) — it is not a grain
yy_, xx_ = np.mgrid[812:852, 370:456]
gm[812:852, 370:456][(xx_ < 395) & (yy_ > 834)] = 0
img8 = np.clip(out, 0, 255).astype(np.uint8)
out = cv2.cvtColor(cv2.inpaint(cv2.cvtColor(img8, cv2.COLOR_RGB2BGR), gm, 5, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB).astype(np.float32)
# sparkle in the lower-right water — feathered clone from 50 px to the left
SX0, SX1, SY0, SY1, F = 878, 934, 876, 934, 8
src_ = out.copy()
for y in range(SY0, SY1):
    wy = min(1.0, (y - SY0 + 1) / F, (SY1 - y) / F)
    for x in range(SX0, SX1):
        wx = min(1.0, (x - SX0 + 1) / F, (SX1 - x) / F)
        ww = wx * wy
        out[y, x] = src_[y, x] * (1 - ww) + src_[y, x - 50] * ww
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst); print('ok', dst)

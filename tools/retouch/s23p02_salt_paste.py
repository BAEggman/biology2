#!/usr/bin/env python3
"""s23p02 — 개념 논리 m 2·3·8: 니코틴 문(창살 문)으로 쏟아지던 회색 둥근 알갱이가 자갈(Ca²⁺ 예약)로 읽히던 것 → **흰 소금 결정**(Na⁺ — nAChR 탈분극의 주 이온,
덱 예약 소금 = Na) · 물자루를 쥐어짜는 손(M3)이 손가락 넷이던 것 → **셋**(「손가락 수 = 번호」: M2 둘 · M3 셋).
제미나이 v1 에서 바뀐 세 곳(위 창살 문 아래 소금 · 아래 창살 문 곁 소금 · 오른쪽 아래 손)만 원본에 옮겨 붙이고(σ2 밝기 차 > 12 · 닫기 3 · 메움 · 넓힘 4 · σ2 섞음),
제미나이가 소금 곁에 더 그린 **네 꼭지 반짝임 다섯**(워터마크 반짝이와 헷갈림)은 둥근 창 안에서 바탕보다 8 넘게 어두운 화소(굵은 검은 소금 윤곽 곁 3px 제외)를 Telea 로 지운다.
물방울 뒤에 원본부터 있던 흐린 반짝이 표식도 바탕보다 밝은 화소만 바탕색으로 덮는다(물방울 보호).
사용: python3 s23p02_salt_paste.py ORIG.png V1.png OUT.png"""
import sys
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ndi
op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
H, W = O.shape[:2]
d = ndi.gaussian_filter(np.abs(O - V).mean(axis=2), 2.0)
boxes = [(270, 280, 480, 510), (260, 740, 440, 995), (850, 730, 1005, 905)]
m = np.zeros((H, W), bool)
for (x0, y0, x1, y1) in boxes:
    b = np.zeros((H, W), bool); b[y0:y1, x0:x1] = True
    mm = (d > 12) & b
    mm = ndi.binary_closing(mm, iterations=3)
    mm = ndi.binary_fill_holes(mm)
    mm = ndi.binary_dilation(mm, iterations=4) & b
    m |= mm
w = ndi.gaussian_filter(m.astype(float), 2.0)
out = O * (1 - w[..., None]) + V * w[..., None]
print('paste px', int(m.sum()))
o8 = np.clip(out, 0, 255).astype(np.uint8)
L = o8.mean(axis=2)
glints = [(339, 332, 13), (373, 389, 18), (311, 418, 13), (345, 855, 17), (299, 892, 15)]
gm = np.zeros((H, W), bool)
for (cx, cy, r) in glints:
    x0, x1, y0, y1 = cx - r, cx + r + 1, cy - r, cy + r + 1
    sub = L[y0:y1, x0:x1]
    ring = np.concatenate([L[y0 - 4:y0, x0:x1].ravel(), L[y1:y1 + 4, x0:x1].ravel()])
    bg = np.percentile(ring, 70)
    off = sub < bg - 8                                  # 바탕보다 어두운 것(반짝임 선 · 그 그림자)
    blk = sub < 70
    lab_b, nb = ndi.label(blk)
    big = np.zeros_like(blk)
    for k in range(1, nb + 1):
        if (lab_b == k).sum() > 25:
            big |= lab_b == k
    cube = ndi.binary_dilation(big, iterations=3)       # 소금 결정의 굵은 윤곽 곁은 건드리지 않음
    yy, xx = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
    disc = np.hypot(xx - r, yy - r) <= r
    gm[y0:y1, x0:x1] |= off & ~cube & disc
gm = ndi.binary_dilation(gm, iterations=1)
print('glint px', int(gm.sum()))
o8 = cv2.inpaint(o8, gm.astype(np.uint8) * 255, 4, cv2.INPAINT_TELEA)
# 물방울 뒤의 옛 반짝이 표식(원본부터 있던 흐린 네 꼭지 별, x 870..940 · y 880..945): 바탕보다 밝은 화소만 바탕색으로 — 물방울(검은 윤곽 + 안)은 보호
X0, X1, Y0, Y1 = 862, 948, 878, 944
sub = o8[Y0:Y1, X0:X1].astype(np.float64)
Ls = sub.mean(axis=2)
ringpx = np.concatenate([o8[Y0:Y1, X0 - 6:X0].reshape(-1, 3), o8[Y0:Y1, X1:X1 + 6].reshape(-1, 3)]).astype(np.float64)
bgc = np.median(ringpx, axis=0); bgl = bgc.mean()
drop = ndi.binary_fill_holes(ndi.binary_dilation(Ls < 185, iterations=1))
drop = ndi.binary_dilation(drop, iterations=1)
bag = np.zeros_like(drop); bag[:12, 20:75] = True        # 자루 밑동
spark2 = (Ls > bgl + 4) & ~drop & ~bag
spark2 = ndi.binary_dilation(ndi.binary_opening(spark2, iterations=1), iterations=2) & ~drop & ~bag
sw = ndi.gaussian_filter(spark2.astype(float), 1.2)[..., None]
rng = np.random.default_rng(2302)
fill = bgc + rng.normal(0, 1.2, sub.shape)
sub = sub * (1 - sw) + fill * sw
o8[Y0:Y1, X0:X1] = np.clip(sub, 0, 255).astype(np.uint8)
print('old sparkle px', int(spark2.sum()), 'bg', bgc.astype(int))
Image.fromarray(o8).save(dst)
print('saved', dst)

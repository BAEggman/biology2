#!/usr/bin/env python3
"""s45p06_bubbles.py SRC OUT — 걸상 두 무더기 위의 방울 예닐곱(크기 제각각)을 지우고, 오른쪽 액자 굴뚝의 방울 무리(넷 · 같은 꼴)를 그대로 복사해 얹는다.
7행 「액자 방울과 걸상 방울이 똑같이 생겼다」가 눈으로 서게(같은 크기 · 같은 넷)."""
import sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
O = np.asarray(Image.open(src).convert('RGB'))
H, W = O.shape[:2]
# 1) 액자 방울 무리 복사 — 상자(775,192)-(835,258) · 크림 바탕과 다른 화소만
FX0, FY0, FX1, FY1 = 772, 197, 836, 260
grp = O[FY0:FY1, FX0:FX1].astype(float)
bg = np.median(grp.reshape(-1, 3), axis=0)
m = np.abs(grp - bg).max(axis=2) > 22
m = ndi.binary_closing(m, iterations=2); m = ndi.binary_fill_holes(m); m = ndi.binary_erosion(m, iterations=1)
a = ndi.gaussian_filter(m.astype(float), 0.6)
# 2) 걸상 위 방울 지우기 — 두 기둥 상자 안의 어두운 윤곽(방울 테두리)을 채워 마스크 → Telea
out = O.copy()
for (x0, y0, x1, y1, plain) in [(240, 500, 320, 662, False), (745, 490, 840, 662, True)]:
    sub = O[y0:y1, x0:x1]
    lum = sub.mean(axis=2)
    bgc = np.median(sub.reshape(-1, 3), axis=0)
    dark = (lum < 110) | (plain & (np.abs(sub.astype(float) - bgc).max(axis=2) > 30))
    dark = ndi.binary_closing(dark, iterations=2); dark = ndi.binary_fill_holes(dark)
    # 방울만: 덩어리의 상자가 40px 안인 것만(띠 가장자리 긴 선은 버린다)
    lab, n = ndi.label(dark); keep = np.zeros_like(dark)
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if hh <= 40 and ww <= 40: keep |= (lab == i)
    dark = ndi.binary_dilation(keep, iterations=4)
    if plain:  # 무더기 윤곽에 붙어 큰 덩어리가 된 맨 아래 방울(786,644)은 따로 원으로
        yy, xx = np.mgrid[y0:y1, x0:x1]; dark |= (xx - 786) ** 2 + (yy - 644) ** 2 <= 12 ** 2
    mk = np.zeros((H, W), np.uint8); mk[y0:y1, x0:x1] = dark.astype(np.uint8) * 255
    out = cv2.inpaint(np.ascontiguousarray(out[..., ::-1]), mk, 5, cv2.INPAINT_TELEA)[..., ::-1]
    print('erased px', int(dark.sum()), 'in', (x0, y0, x1, y1))
# 3) 무리 얹기 — 각 무더기 바로 위(무더기 꼭대기 y≈665)
out = out.astype(float)
for (px, py) in [(252, 588), (768, 588)]:
    reg = out[py:py + (FY1 - FY0), px:px + (FX1 - FX0)]
    out[py:py + (FY1 - FY0), px:px + (FX1 - FX0)] = reg * (1 - a[..., None]) + grp * a[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print('bubble px', int(m.sum()))

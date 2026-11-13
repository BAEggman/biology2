#!/usr/bin/env python3
# L53b_pil0.py — E1 바로 뒤 · pil1 앞: 버터 띠에 얹힌 반투명 흰 광택 줄 둘(위 · 아래)을 걷어 낸다
#  (일치 검사 독자가 두 번 「이음매 · 덧칠 자국」으로 읽음 · L53a 의 띠에는 광택이 없다).
#  흰 덧칠 p' = p(1 − a) + 255a 를 거꾸로 푼다: a 는 버터 화소(본디 빛을 아는 곳)에서 재고, 다리 화소에는 이웃 버터의 a 를 가로로 고르게 번져 준다.
import sys, cv2, numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
a = np.array(Image.open(src).convert('RGB')).astype(np.float32)
def dehi(y0, y1, x0, x1, skip=()):
    reg = a[y0:y1, x0:x1]; R, G, B = reg[..., 0], reg[..., 1], reg[..., 2]
    butterish = (R > 236) & (G > 198) & (R - B > 45)                         # 버터(광택이 얹혔든 아니든)
    obj = np.zeros(R.shape, bool)                                            # 물건(흰 방울 자취 · 파란 물방울)은 건드리지 않는다 — 그 가로 구간 안의 흰 · 파란 화소만
    for sx0, sx1 in skip:
        z = np.zeros(R.shape, bool); z[:, max(0, sx0 - x0):max(0, sx1 - x0)] = True
        thing = ((R > 232) & (G > 232) & (B > 225)) | (B > R + 25) | (R + G + B < 150)
        obj |= z & (cv2.dilate(thing.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
    oil = ((R > 200) & (G < 200) & (B < 125) & (R - G > 42)).astype(np.uint8)  # 기름방울(주황)
    oil = cv2.dilate(oil, np.ones((9, 9), np.uint8)) > 0
    al = np.clip((B - 75) / 180.0, 0, 1) * butterish
    w = butterish.astype(np.float32)
    A = cv2.GaussianBlur(al, (0, 0), sigmaX=9, sigmaY=1.6); W = cv2.GaussianBlur(w, (0, 0), sigmaX=9, sigmaY=1.6)
    am = np.where(W > 0.05, A / np.maximum(W, 1e-3), 0)
    am[am < 0.035] = 0
    h = y1 - y0; ramp = np.minimum(np.arange(h), np.arange(h)[::-1]).astype(np.float32); am = am * np.clip(ramp / 4.0, 0, 1)[:, None]
    out = (reg - 255.0 * am[..., None]) / np.maximum(1 - am[..., None], 0.25)
    out = np.clip(out, 0, 255)
    # 버터 화소는 버터빛을 넘어 어두워지지 않게, 다리 화소는 다리 먹빛보다 어둡지 않게
    BUT = np.array([248, 211, 75], np.float32)
    bm = butterish & (am > 0)
    out[bm] = np.maximum(out[bm], BUT - 6)
    apply = ~obj & ~oil & (am > 0)
    reg[apply] = out[apply]
    # 남은 밝은 부스러기 · 줄 윤곽: 광택이 있던 자리의 버터 화소는 버터빛 한 가지로
    zone = cv2.dilate((am > 0).astype(np.uint8), np.ones((7, 15), np.uint8)) > 0
    R, G, B = reg[..., 0], reg[..., 1], reg[..., 2]
    lightbits = zone & ~obj & ~oil & (((R > 222) & (G > 186) & ((R - B > 20) | (B > 150))) | ((B > 116) & (R > 150)))
    reg[lightbits] = BUT
dehi(447, 488, 20, 905, skip=[(78, 118)])
dehi(648, 692, 20, 905, skip=[(782, 830)])
Image.fromarray(a.astype(np.uint8)).save(dst); print('ok')

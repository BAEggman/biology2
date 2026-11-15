#!/usr/bin/env python3
# L37b_pil.py <in.png> <out.png> — L37b 덧붙임(2026-11-15 · 18장 · 일치 검사 1회 뒤)의 PIL 몫.
#  엄마 짚 뭉치의 분홍 물방울 머릿수건이 아빠 뭉치의 분홍 꽃 자국(= 메틸화)과 같은 빛이라 「엄마도 꽃이 찍혔다」로 읽힐 수 있다 →
#  머릿수건(과 매듭)만 하늘색으로(밝기는 그대로 · 흰 물방울은 흰 채로). 상자 밖 아빠 뭉치의 꽃은 건드리지 않는다.
import sys
import numpy as np
from PIL import Image

BOX = (1768, 170, 1840, 237)          # 엄마 뭉치 머릿수건 · 매듭(2048 × 1144) — 아빠 뭉치는 x ≥ 1845
SKY = np.array([118, 172, 226], float)

def main(src, out):
    a = np.array(Image.open(src).convert('RGB')).astype(float)
    x0, y0, x1, y1 = BOX; sub = a[y0:y1, x0:x1]
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    lumv = sub.mean(axis=2)
    dots = (lumv > 195) & (r - g > 8) & (b >= g - 6)                          # 옅은 분홍 물방울 → 흰 물방울(파란 바탕에서 분홍으로 남으면 꽃 자국처럼 보였다)
    pink = ~dots & (r > 110) & (r - g > 22) & (b > g - 12)                    # 분홍 · 그 테 번짐(빨강 > 초록 · 파랑 ≥ 초록) — 짚 노랑(b ≪ g)은 빠진다
    lum = lumv[..., None]; ref = np.array([226, 128, 172], float).mean()
    new = np.clip(SKY * (lum / ref), 0, 255)
    sub[pink] = new[pink]
    sub[dots] = np.array([246, 247, 250], float)
    a[y0:y1, x0:x1] = sub
    Image.fromarray(a.astype(np.uint8)).save(out); print('→', out, '· 바꾼 픽셀', int(pink.sum()), '· 물방울', int(dots.sum()))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
# L12b_pil.py <in.png> <out.png> — L12b 덧붙임(2026-11-16 · 42장 · 지시서 차례 7)의 PIL 몫.
#  일치 검사 2회 「종이띠 위의 빛깔 네모가 아주 옅어 잘 안 읽힌다」 → 뗏목 일꾼이 가위로 자르는 흰 종이띠와 물에 뜬 낱장 둘의 네모만 진하게.
#  흰 종이(밝고 무채)를 찾아 구멍을 메운 꼴 = 띠 · 낱장 → 그 안의 빛깔 픽셀만 채도 ↑ · 밝기 조금 ↓(빛깔은 그대로). 띠 밖 운하 물(베이지)은 손대지 않는다.
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import colorsys

BOXES = [(1218, 676, 1280, 720),       # 가위로 자르는 종이띠
         (1286, 684, 1310, 704),       # 물에 뜬 낱장(분홍)
         (1258, 714, 1286, 734)]       # 물에 뜬 낱장(초록)

def vivid(a, box):
    x0, y0, x1, y1 = box; sub = a[y0:y1, x0:x1].astype(float) / 255
    mx, mn = sub.max(axis=2), sub.min(axis=2); sat = (mx - mn) / np.maximum(mx, 1e-6)
    white = (mx > 0.80) & (sat < 0.14)
    paper = ndi.binary_fill_holes(ndi.binary_closing(white, iterations=2))
    paper = ndi.binary_erosion(paper, iterations=2)
    col = paper & ~white & (sat > 0.12) & (mx > 0.45)
    n = 0
    for y, x in zip(*np.nonzero(col)):
        h, s, v = colorsys.rgb_to_hsv(*sub[y, x])
        s2 = min(1.0, s * 2.3 + 0.18); v2 = v * 0.90
        sub[y, x] = colorsys.hsv_to_rgb(h, s2, v2); n += 1
    a[y0:y1, x0:x1] = np.clip(sub * 255 + 0.5, 0, 255).astype(np.uint8)
    return n

def main(src, out):
    a = np.array(Image.open(src).convert('RGB'))
    ns = [vivid(a, b) for b in BOXES]
    Image.fromarray(a).save(out); print('→', out, '· 진하게 한 픽셀', ns)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

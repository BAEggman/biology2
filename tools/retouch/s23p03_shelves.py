#!/usr/bin/env python3
"""s23p03 — 2×2 격자의 α/β 와 1/2 를 물건으로 나른다(F2 · 글자사전: 알 = α · 베 = β · 개수 = 번호).
제미나이가 이 그림 편집을 두 번 다 「hard time fulfilling」으로 거절 → 선반 넷만 따로 그려 받아(s23p03_shelves_*.png · 글 → 그림)
칸마다 빈 벽 높은 곳에 붙인다: 좌상 알 하나(α₁) · 좌하 알 둘(α₂) · 우상 개어 둔 베 하나(β₁) · 우하 베 둘(β₂).
오림: 소품 그림 바탕(251,249,237)에서 색 거리 > 28 인 곳 → 구멍 메움(흰 알·흰 베 속도 불투명) → 1px 부풀림 → 가장자리 1.2px 흐림.
붙임: 너비 136px 로 줄여(LANCZOS) 칸 벽의 빈 자리에 알파 합성.
사용: python3 tools/retouch/s23p03_shelves.py <설치본 s23p03.png> <소품.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import binary_fill_holes, binary_dilation
base_p, asset_p, out = sys.argv[1:4]
base = Image.open(base_p).convert('RGB').resize((1024, 1024), Image.LANCZOS)
A = Image.open(asset_p).convert('RGB')
a = np.asarray(A, dtype=float)
bg = np.array([251., 249., 237.])
dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
CROPS = {  # asset crop boxes (x0,y0,x1,y1) in the 1024×559 asset
    'a1': (85, 75, 450, 240),   # one egg
    'b1': (570, 90, 935, 240),  # one folded cloth
    'a2': (85, 325, 450, 495),  # two eggs
    'b2': (570, 345, 935, 495), # two folded cloths
}
PLACE = {  # top-left corner in s23p03 (1024²)
    'a1': (110, 56),   # top-left panel: α1 (strap round the pipe = vasoconstriction)
    'b1': (560, 60),   # top-right panel: β1 (pendulum = heart)
    'a2': (345, 556),  # bottom-left panel: α2 (own mouth covered = autoinhibition)
    'b2': (690, 540),  # bottom-right panel: β2 (spreading the tube = bronchodilation)
}
W = 136
res = base.copy()
for k, (x0, y0, x1, y1) in CROPS.items():
    m = dist[y0:y1, x0:x1] > 28
    m = binary_fill_holes(m)
    m = binary_dilation(m, iterations=1)
    M = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    crop = A.crop((x0, y0, x1, y1))
    h = round((y1 - y0) * W / (x1 - x0))
    crop = crop.resize((W, h), Image.LANCZOS); M = M.resize((W, h), Image.LANCZOS)
    res.paste(crop, PLACE[k], M)
    print(k, 'at', PLACE[k], 'size', (W, h))
res.save(out)
print('saved', out)

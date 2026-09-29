#!/usr/bin/env python3
"""s09p03 — 개념 논리 M 둘(logic_0929 s09p03 6 · 7).
① 노던·웨스턴 자리 배양기가 열려 「쓰는 중」 → 제미나이 v1 이 두 배양기를 흰 천으로 덮음 — 그 두 배양기 둘레(x 536..756 × y 203..488 · x 820..1020 × y 203..486)만 v1 에서 옮겨 온다(4px 섞음).
   (v1 은 아래 벽을 오히려 틈 오른쪽에 켜를 더 쌓아 버려서 벽은 쓰지 않는다)
② 아래 벽 — 틈 오른쪽에서 위 두 켜가 다시 이어짐(= ddNTP 뒤에 사슬이 다시 자람) → 설치본에서 틈 오른쪽(x ≥ 578)의 y 780..892(틈 윗선보다 위의 두 켜 R1 843..860 · R2 864..893)를 바탕으로 지운다.
   바탕은 벽 위 빈 곳(x 600..1000 × y 770..790) 중앙값 한 색 + 잔잡음. R3 윗선(y≈893..900)과 그 아래 두 켜(주형)는 끝까지 그대로.
사용: python3 tools/retouch/s09p03_cabinets_wall.py <설치본.png> <v1.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
old_p, new_p, out = sys.argv[1:4]
O = np.asarray(Image.open(old_p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
N = np.asarray(Image.open(new_p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
res = O.copy()
F = 4
for (x0, x1, y0, y1) in ((536, 757, 203, 489), (820, 1021, 203, 487)):
    for y in range(y0, y1):
        for x in range(x0, x1):
            w = min(1.0, (x - x0 + 1) / F, (x1 - x) / F, (y - y0 + 1) / F, (y1 - y) / F)
            res[y, x] = N[y, x] * w + O[y, x] * (1 - w)
XG, Y0, YTOP = 578, 780, 893   # R3 윗선(검은 줄 y≈893..900)은 남긴다
bg = np.median(O[770:790, 600:1000].reshape(-1, 3), axis=0)
rng = np.random.default_rng(9)
for x in range(XG, 1024):
    for y in range(Y0, YTOP):
        res[y, x] = bg + rng.normal(0, 0.8, 3)
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)

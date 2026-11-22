"""L07f-01 뒤처리(독자 ㄱ · ㄷ: 「자갈 둘이 바구니 안이 아니라 겉면에 붙어 보임 · 밖에 낱 자갈」) —
바구니 앞면의 자갈 둘을 바로 왼쪽 30 px 의 엮은 무늬로 덮고(가장자리 흐림), 바구니 입구 안쪽 바닥에 흰 자갈 둘을 그린다 ·
바구니 왼쪽 풀밭의 낱 자갈 하나는 바로 위 풀로 덮는다.
쓰는 법: python3 pil_pebbles.py <in.png> <out.png>"""
import sys
import cv2, numpy as np
im = cv2.imread(sys.argv[1]).astype(np.float32); src = im.copy()
def clone(cx, cy, rx, ry, dx, dy):
    m = np.zeros(im.shape[:2], np.float32); cv2.ellipse(m, (cx, cy), (rx, ry), 0, 0, 360, 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), 1.5)[..., None]
    sh = np.roll(np.roll(src, dy, axis=0), dx, axis=1)
    return im * (1 - m) + sh * m
im = clone(1430, 1028, 19, 14, 30, 0)      # 앞면 자갈 1 ← 왼쪽 30 px 무늬
src = im.copy(); im = clone(1463, 1024, 19, 14, 34, 0)   # 앞면 자갈 2 ← 자갈 1 자리(덮인 뒤) 쪽
src = im.copy(); im = clone(1303, 1074, 12, 9, 0, 22)    # 풀밭 낱 자갈 ← 위쪽 풀
im = im.clip(0, 255).astype(np.uint8)
for (cx, cy) in [(1420, 972), (1450, 974)]:
    cv2.ellipse(im, (cx, cy), (10, 6), 0, 0, 360, (250, 250, 250), -1, cv2.LINE_AA)
    cv2.ellipse(im, (cx, cy), (10, 6), 0, 0, 360, (25, 25, 25), 2, cv2.LINE_AA)
cv2.imwrite(sys.argv[2], im)

#!/usr/bin/env python3
# L12f_pil0.py <base_in.png> <out.png> — 바탕(s2 · 2048x1144)에서 덤으로 그려진 것 넷을 지운다(구역 편집 앞).
#   ① 수반 밖으로 떨어지는 베이지 물줄기  ② 곳간 오른쪽의 둘째 초록 관  ③ 통 가장자리의 둘째 우편함  ④ 목 방 위쪽의 둘째 빵 덩이
import sys, numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
a = np.array(Image.open(src).convert('RGB')).copy()
def fill_row(x0, x1, y0, y1, sx):
    """줄마다 (y, sx)의 색으로 x0 ~ x1 을 덮는다 — 바탕이 가로로 고른 곳에만."""
    for y in range(y0, y1):
        a[y, x0:x1] = a[y, sx]
# ① 베이지 물줄기(주전자 주둥이 아래 ~ 붉은 물길 위) — 곳간 오른쪽의 맨 바탕(같은 줄)에서
fill_row(1437, 1469, 309, 498, 1760); a[498:501, 1436:1464] = (30, 18, 16); fill_row(1436, 1464, 501, 514, 1428)      # 물길 윗선(검은 테)을 다시 긋고 그 아래는 왼쪽 이웃의 붉은 물빛으로
# ② 둘째 초록 관 — 곳간 오른쪽 벽 바깥
fill_row(1701, 1748, 256, 497, 1756)
# ③ 둘째 우편함 — 가지 관 상자와 초병 사이
fill_row(888, 974, 376, 434, 712); fill_row(888, 966, 434, 482, 712); fill_row(920, 942, 480, 493, 914)
# ④ 목 방 위쪽의 둘째 빵 덩이와 그 곁의 흔들림 줄 — 방 안쪽 색으로
col = np.median(a[690:716, 640:654].reshape(-1, 3), axis=0).astype(np.uint8)
yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
m = ((xx - 620) ** 2 + (yy - 532) ** 2 <= 31 ** 2) | ((xx >= 632) & (xx <= 656) & (yy >= 498) & (yy <= 570))
m &= (xx >= 596) & (xx <= 656)
a[m] = col
Image.fromarray(a).save(out)
print('pil0 ok', tuple(col))

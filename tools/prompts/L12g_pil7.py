#!/usr/bin/env python3
# L12g_pil7.py <in> <out> — 구역 편집 Z8(소 속의 작은 강철 통) 앞의 손질: 큰 통 → 강철 통으로 곧장 가던 초록 관을 지운다.
#  (차례가 통 → 입 → 책 → 강철 통이어야 한다. 관을 둔 채 Z8 을 시키면 Gemini 가 관을 통 속까지 이어 그린다.)
import sys, math
import numpy as np
from PIL import Image, ImageDraw
a = np.array(Image.open(sys.argv[1]).convert('RGB'))
COW = np.array([249, 250, 245])
yy, xx = np.mgrid[462:516, 1490:1540]
poly = Image.new('L', (50, 54), 0)
ImageDraw.Draw(poly).polygon([(x - 1490, y - 462) for x, y in [(1497, 485), (1510, 472), (1526, 482), (1534, 497), (1534, 511), (1509, 511), (1509, 497), (1502, 489)]], fill=255)
pm = np.asarray(poly) > 0
dline = np.abs((xx - 1499) * (471 - 481) - (yy - 481) * (1509 - 1499)) / math.hypot(10, 10)      # 통 띠의 아랫동(검은 빗금 (1499,481) – (1509,471))까지의 거리
along = ((xx - 1499) * 10 + (yy - 481) * (-10)) / (10 * 10 + 10 * 10)
keep = (dline < 3.2) & (along > -0.35) & (along < 1.35)
reg = a[462:516, 1490:1540]; reg[pm & ~keep] = COW
gk = pm & keep & (reg[..., 1].astype(int) > reg[..., 0].astype(int) + 18); reg[gk] = COW                # 빗금 곁에 남은 초록 부스러기
for x in range(1506, 1538): a[503:521, x] = a[503:521, 1546]                                            # 강철 상자 윗선(검은 띠)을 곧은 이웃 열에서 이어 온다
Image.fromarray(a).save(sys.argv[2]); print('ok pil7')

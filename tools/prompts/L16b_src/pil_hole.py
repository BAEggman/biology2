"""L16b-02(s10) — 날아가는 피자 조각 끝의 작은 넷째 구멍(1935, 204)을 치즈로 메워 구멍을 정확히 셋으로.
쓰는 법: python3 pil_hole.py <in.png> <out.png>"""
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
im = Image.open(sys.argv[1]).convert('RGB'); A = np.array(im).astype(float)
cx, cy = 1935, 204
yy, xx = np.mgrid[0:A.shape[0], 0:A.shape[1]]
r = np.hypot((xx - cx) / 1.0, (yy - cy) / 0.8)
ring = (r > 10) & (r < 14)
px = A[ring]; cheese = px[(px[:, 0] > 200) & (px[:, 1] > 160) & (px[:, 2] < 140)]
col = tuple(int(v) for v in np.median(cheese, 0))
m = Image.new('L', im.size, 0); ImageDraw.Draw(m).ellipse((cx - 10, cy - 9.5, cx + 10, cy + 8), fill=255)
m = m.filter(ImageFilter.GaussianBlur(1.2))
im = Image.composite(Image.new('RGB', im.size, col), im, m); im.save(sys.argv[2])
print('치즈 빛', col)

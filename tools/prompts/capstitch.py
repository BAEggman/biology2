#!/usr/bin/env python3
"""capstitch.py <out.png> <W> <H> <tile1.png> <y1> [<tile2.png> <y2> …]
Chrome 확대 갈무리(기기 픽셀 1:1) 조각들을 세로로 이어 W x H 원본을 되살린다. y = 갈무리 영역의 위쪽(스크린샷 좌표).
겹친 줄을 맞춰 정확한 어긋남을 찾는다(±5)."""
import sys, numpy as np
from PIL import Image
out, W, H = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); args = sys.argv[4:]
K = 2.200000047683716 * (1527 / 1419)        # 스크린샷 좌표 → 기기 픽셀
tiles = [(np.array(Image.open(args[i]).convert('RGB')).astype(np.int16), float(args[i + 1])) for i in range(0, len(args), 2)]
canvas = np.zeros((H + 80, max(W, max(t.shape[1] for t, _ in tiles)), 3), np.int16); filled = 0
for k, (t, y) in enumerate(tiles):
    if k == 0: off = 0
    else:
        approx = int(round(y * K)); best = None
        for dy in range(approx - 5, approx + 6):
            ov = filled - dy
            if ov < 20: continue
            a = canvas[dy:dy + min(ov, 200), :W]; b = t[:min(ov, 200), :W]
            e = np.abs(a - b).mean()
            if best is None or e < best[0]: best = (e, dy)
        off = best[1]; print('tile', k, 'approx', approx, '→ off', off, 'err', round(float(best[0]), 3))
    h = min(t.shape[0], canvas.shape[0] - off); canvas[off:off + h, :t.shape[1]] = t[:h]; filled = off + h
res = canvas[:H, :W].astype(np.uint8)
edge = canvas[:H, W:W + 3].max() if canvas.shape[1] > W else -1; bot = canvas[H:H + 3, :W].max()
print('size', res.shape[1], res.shape[0], '· 오른쪽 여백 max', int(edge), '· 아래 여백 max', int(bot), '· 마지막 줄 평균', round(float(res[-1].mean()), 1))
Image.fromarray(res).save(out)

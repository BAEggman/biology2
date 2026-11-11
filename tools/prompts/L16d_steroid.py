#!/usr/bin/env python3
# steroid.py <in.png> <out.png> cx_jar bottom_y r — 고리 넷(육각 셋 + 오각 하나)을 붙어 있는 한 덩이로 그린다(금빛 · 검은 테두리)
import sys, math
from PIL import Image, ImageDraw
src, dst, JX, BY, r = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
s3 = math.sqrt(3)
def hexv(cx, cy):  # 꼭짓점이 위아래(pointy-top)
    return [(cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))) for a in (90, 30, -30, -90, -150, 150)]
Ax = JX - 2.068 * r; Ay = BY - r
A = (Ax, Ay); B = (Ax + s3 * r, Ay); C = (Ax + 1.5 * s3 * r, Ay - 1.5 * r)
rings = [hexv(*A), hexv(*B), hexv(*C)]
# 오각: C 의 오른쪽 세로 변을 함께 쓴다
e0 = (C[0] + s3 / 2 * r, C[1] - r / 2); e1 = (C[0] + s3 / 2 * r, C[1] + r / 2)
ap = r / (2 * math.tan(math.radians(36))); R = r / (2 * math.sin(math.radians(36)))
D = (e0[0] + ap, C[1])
# 오각 꼭짓점: 중심에서 각도 — 공유 변의 두 끝이 각 180±36 이 되게
pv = [(D[0] + R * math.cos(math.radians(a)), D[1] - R * math.sin(math.radians(a))) for a in (144, 72, 0, -72, -144)]
rings.append(pv)
edges = set()
def key(p): return (round(p[0], 1), round(p[1], 1))
segs = []
for ring in rings:
    for i in range(len(ring)):
        p, q = ring[i], ring[(i + 1) % len(ring)]
        k = tuple(sorted([key(p), key(q)]))
        if k in edges: continue
        edges.add(k); segs.append((p, q))
im = Image.open(src).convert('RGB')
xs = [p[0] for g in rings for p in g]; ys = [p[1] for g in rings for p in g]
x0, y0, x1, y1 = int(min(xs)) - 12, int(min(ys)) - 12, int(max(xs)) + 12, int(max(ys)) + 12
S = 4; W, H = (x1 - x0) * S, (y1 - y0) * S
def T(p): return ((p[0] - x0) * S, (p[1] - y0) * S)
def layer(width, col):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for p, q in segs:
        d.line([T(p), T(q)], fill=255, width=int(width * S))
    for g in rings:
        for p in g:
            cx, cy = T(p); rr = width * S / 2
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)
    return m.resize((x1 - x0, y1 - y0), Image.LANCZOS), col
reg = im.crop((x0, y0, x1, y1))
for m, col in (layer(float(sys.argv[6]) if len(sys.argv) > 6 else 10.5, (28, 26, 24)), layer(float(sys.argv[7]) if len(sys.argv) > 7 else 6.4, (226, 186, 98)), layer(2.6, (246, 220, 150))):
    reg.paste(Image.new('RGB', m.size, col), (0, 0), m)
im.paste(reg, (x0, y0)); im.save(dst)
print('box', x0, y0, x1, y1, 'D', [round(v, 1) for v in D])

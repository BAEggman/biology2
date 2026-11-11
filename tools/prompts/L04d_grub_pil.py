#!/usr/bin/env python3
# grub_pil.py in out — 애벌레 갑옷: 투구 → 가슴 상자 검은 전선(PTTH) · 상자를 키워 금빛 고리 넷 문장(엑디스테로이드)
import sys, math
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
S = 4
im = Image.open(src).convert('RGB')
X0, Y0, X1, Y1 = 1290, 820, 1470, 1060
reg = im.crop((X0, Y0, X1, Y1)).resize(((X1 - X0) * S, (Y1 - Y0) * S), Image.LANCZOS)
d = ImageDraw.Draw(reg)
def T(p): return ((p[0] - X0) * S, (p[1] - Y0) * S)
def bez(pts, n=60):
    # Catmull-Rom 을 지나는 매끈한 선
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1]); return out
# 1) 상자(키움) — 짙은 밤색 · 검은 테 · 뚜껑 선
bx0, by0, bx1, by1 = 1331, 962, 1405, 1013
d.rounded_rectangle([T((bx0, by0)), T((bx1, by1))], radius=6 * S, fill=(120, 82, 50), outline=(24, 22, 20), width=int(3.2 * S))
d.line([T((bx0 + 2, by0 + 10)), T((bx1 - 2, by0 + 10))], fill=(24, 22, 20), width=int(2.4 * S))
d.rounded_rectangle([T((bx0 + 4, by0 + 2.5)), T((bx1 - 4, by0 + 8))], radius=2 * S, fill=(150, 106, 66))
# 2) 금빛 고리 넷 문장(육각 셋 + 오각 하나 · 한 덩이)
r = 8.4; s3 = math.sqrt(3)
JX, BY = 1368.5, 1007.5
Ax = JX - 2.068 * r; Ay = BY - r
def hexv(cx, cy): return [(cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))) for a in (90, 30, -30, -90, -150, 150)]
A = (Ax, Ay); B = (Ax + s3 * r, Ay); C = (Ax + 1.5 * s3 * r, Ay - 1.5 * r)
rings = [hexv(*A), hexv(*B), hexv(*C)]
e0 = (C[0] + s3 / 2 * r, C[1] - r / 2)
ap = r / (2 * math.tan(math.radians(36))); R = r / (2 * math.sin(math.radians(36)))
D = (e0[0] + ap, C[1])
rings.append([(D[0] + R * math.cos(math.radians(a)), D[1] - R * math.sin(math.radians(a))) for a in (144, 72, 0, -72, -144)])
segs = []; seen = set()
for g in rings:
    for i in range(len(g)):
        p, q = g[i], g[(i + 1) % len(g)]
        k = tuple(sorted([(round(p[0], 1), round(p[1], 1)), (round(q[0], 1), round(q[1], 1))]))
        if k in seen: continue
        seen.add(k); segs.append((p, q))
for w, col in ((4.4, (24, 22, 20)), (2.5, (232, 192, 96)), (1.0, (250, 228, 160))):
    for p, q in segs: d.line([T(p), T(q)], fill=col, width=max(1, int(w * S)))
    for g in rings:
        for p in g:
            cx, cy = T(p); rr = w * S / 2; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
print('ring box', round(min(p[0] for g in rings for p in g), 1), round(min(p[1] for g in rings for p in g), 1), round(max(p[0] for g in rings for p in g), 1), round(max(p[1] for g in rings for p in g), 1))
# 3) 검은 전선 — 투구 왼쪽 위 소켓에서 투구 바깥 왼쪽을 돌아 상자 왼쪽 옆구리로
path = bez([(1346, 866), (1334, 857), (1325, 872), (1323, 912), (1324, 945), (1326, 975), (1331, 984)])
d.line([T(p) for p in path], fill=(20, 18, 16), width=int(5.0 * S), joint='curve')
for p in (path[0], path[-1]):
    cx, cy = T(p); rr = 2.5 * S; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(20, 18, 16))
# 소켓(투구 위의 작은 검은 단자)
cx, cy = T((1346, 866)); rr = 5.2 * S; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(150, 156, 164), outline=(20, 18, 16), width=int(2.2 * S)); rr = 2.0 * S; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(20, 18, 16))
# 플러그(상자 옆구리)
d.rounded_rectangle([T((1327, 980)), T((1335, 992))], radius=S, fill=(150, 156, 164), outline=(20, 18, 16), width=int(1.8 * S))
reg = reg.resize((X1 - X0, Y1 - Y0), Image.LANCZOS)
im.paste(reg, (X0, Y0)); im.save(dst)

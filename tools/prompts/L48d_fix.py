#!/usr/bin/env python3
# L48d 손질: ① 기름 단지 금빛 라벨에 고리 넷(스테로이드) ② 안내인 사슬 앞 끝(구멍으로 드는 쪽) 구슬을 빨갛게 ③ 막대사탕에 빨간 도장 자국
import sys, math, colorsys
from PIL import Image, ImageDraw
import numpy as np
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
S = 6
INK = (24, 22, 20)
def work(box, fn):
    x0, y0, x1, y1 = box
    reg = im.crop(box).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS)
    d = ImageDraw.Draw(reg); T = lambda p: ((p[0] - x0) * S, (p[1] - y0) * S)
    fn(d, T)
    im.paste(reg.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))
# ① 고리 넷 — 라벨 가운데
def steroid(d, T, JX=697.5, BY=780.0, r=6.6):
    s3 = math.sqrt(3)
    Ax = JX - 2.068 * r; Ay = BY - r
    hexv = lambda cx, cy: [(cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))) for a in (90, 30, -30, -90, -150, 150)]
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
    for w, col in ((3.4, INK), (1.9, (222, 172, 60)), (0.7, (250, 226, 150))):
        for p, q in segs: d.line([T(p), T(q)], fill=col, width=max(1, int(w * S)))
        for g in rings:
            for p in g:
                cx, cy = T(p); rr = w * S / 2; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
work((672, 752, 724, 788), steroid)
# ② 사슬 앞 끝 구슬 빨갛게(HSV: 채도 높은 구슬 화소만 · 지붕 카키와 테두리는 그대로)
a = np.asarray(im).astype(np.float32) / 255
poly = [(612, 482), (624, 486), (640, 470), (652, 440), (660, 416), (648, 408), (636, 424), (624, 448), (614, 466)]
mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).polygon(poly, fill=255)
mk = np.asarray(mask) > 0
r, g, b = a[..., 0], a[..., 1], a[..., 2]
mx = a.max(axis=2); mn = a.min(axis=2); sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
bead = mk & (sat > 0.22) & (mx > 0.35)
# 카키 지붕(누런 회색) 빼기: 색상이 노랑~황토이고 채도 낮은 것
hsv = np.zeros_like(a)
import colorsys as cs
ys, xs = np.nonzero(bead)
out = np.asarray(im).copy()
for y, x in zip(ys, xs):
    h, s, v = cs.rgb_to_hsv(*a[y, x])
    if 0.10 < h < 0.20 and s < 0.45: continue      # 카키
    s2 = max(s, 0.62); v2 = min(1.0, max(v, 0.55))
    rr, gg, bb = cs.hsv_to_rgb(0.0, s2, v2 * 0.92)
    out[y, x] = (int(rr * 255), int(gg * 255), int(bb * 255))
im = Image.fromarray(out)
# ③ 막대사탕에 빨간 도장 자국(작은 네모 · 붉은 민 도장)
def stamp(d, T):
    cx, cy = 1579.5, 626.0
    d.rounded_rectangle([T((cx - 5.5, cy - 4.5)), T((cx + 5.5, cy + 4.5))], radius=1.2 * S, fill=(214, 40, 36), outline=(120, 20, 18), width=int(0.9 * S))
work((1568, 615, 1592, 638), stamp)
im.save(dst)

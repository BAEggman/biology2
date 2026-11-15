#!/usr/bin/env python3
# L46c_abo_pil.py — L46c 면역 덧붙임(ABO 응집 · 2026-11-15 · Opus 5.5).
#   ① 병 주인(이 병의 피)은 A 형 — 식탁의 붉은 원반 넷 · 모로 선 아령 · 당구 치는 원반의 테두리에 초록 알사탕 하나를 단 막대사탕(A 항원 — 알 하나 = A).
#   ② 벽의 피 주머니로 들어온 남의 피는 B 형 — 병 위에 엉긴 원반 덩어리 · 떨어지는 원반의 테두리에 주황 알사탕 둘을 붙인 막대사탕(B 항원 — 알 둘 = B · B 자의 두 배).
#   막대사탕 = 이 덱의 당 사슬(【막대사탕】 L48d · L53a — 「세포마다 사탕의 꼴이 달라 서로를 알아보는 표지」) — ABO 항원은 적혈구 겉 당 사슬의 꼴이다.
#   ③ 노란 층(혈장)의 하늘색 Y 집게(【하늘색 Y자 집게】 = 면역글로불린) = 항B — 두 팔 끝 집게발이 서로 다른 두 원반의 주황 혹을 물어 원반끼리 엮는다(응집) · 깃대는 덩어리 바깥(위)으로.
#   Gemini 는 집게를 한 원반에 두 팔을 다 대고 깃대를 옆 원반에 꽂았다(GC) → 집게 · 딱지는 모두 여기서.
#   첫 판(12 px 딱지 · 세모 집게와 혹 집게 둘 다)은 1 배에서 안 갈렸다 → 딱지를 빛깔로 가르고(초록 = A · 주황 = B) 집게는 한 가지(항B)만.
# 사용: python3 L46c_abo_pil.py <in.png> <out.png>
import sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw

S = 3
INK = (28, 22, 18, 255)
GREEN = (96, 186, 70, 255)           # A 딱지
ORANGE = (244, 146, 42, 255)         # B 딱지(보라는 포도로 읽힐 수 있어 주황)
BLUE = (150, 208, 234, 255)          # L46c s8 집게 몸 빛깔(바탕에서 뽑음)
BLUE_D = (96, 156, 198, 255)         # 손잡이
JAW = (214, 228, 238, 255)
RED = (206, 42, 44, 255); PINK = (236, 150, 160, 255)     # 식탁 원반의 빨강(바탕에서 뽑음)에 맞춤

# 남의 원반 덩어리(GB 를 붙인 바탕에서 잰 타원: 가운데 · 반지름 a · b) — 1 왼앞 · 2 왼뒤 · 3 오른뒤 · 4 가운데앞 · 5 오른앞
D = {1: (336, 293, 41, 25), 2: (393, 265, 40, 25), 3: (479, 265, 40, 25), 4: (440, 303, 40, 25), 5: (539, 290, 41, 25.5),
     # 병 주인의 원반(바탕 그대로): 식탁 넷 · 아령 위아래 혹 · 당구 치는 원반의 몸
     'T1': (774, 763, 96, 52), 'T2': (879, 815, 101, 53), 'T3': (780, 898, 115, 60), 'T4': (1080, 897, 115, 61),
     'DT': (1027, 668, 37, 30), 'DB': (1027, 803, 37, 32), 'CH': (1531, 724, 129, 134)}

def rim(k, deg):
    cx, cy, a, b = D[k]; t = math.radians(deg)
    p = (cx + a * math.cos(t), cy + b * math.sin(t))
    n = (math.cos(t) / a, math.sin(t) / b); l = math.hypot(*n)
    return p, (n[0] / l, n[1] / l)

def unit(v):
    l = math.hypot(*v); return (v[0] / l, v[1] / l)

def qb(p0, p1, p2, n=12):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]

class Pen:
    def __init__(self, img, box):
        self.x0, self.y0, self.x1, self.y1 = box
        self.lay = Image.new('RGBA', ((self.x1 - self.x0) * S, (self.y1 - self.y0) * S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.lay); self.img = img
    def P(self, p): return ((p[0] - self.x0) * S, (p[1] - self.y0) * S)
    def seg(self, p, q, w, col):
        self.d.line([self.P(p), self.P(q)], fill=col, width=max(1, int(round(w * S))))
        for x, y in (p, q):
            r = w * S / 2; X, Y = self.P((x, y)); self.d.ellipse([X - r, Y - r, X + r, Y + r], fill=col)
    def path(self, pts, w, col):
        self.d.line([self.P(p) for p in pts], fill=col, width=max(1, int(round(w * S))), joint='curve')
        for x, y in (pts[0], pts[-1]):
            r = w * S / 2; X, Y = self.P((x, y)); self.d.ellipse([X - r, Y - r, X + r, Y + r], fill=col)
    def poly(self, pts, fill, ow=1.8):
        self.d.polygon([self.P(p) for p in pts], fill=fill, outline=INK if ow else None, width=max(1, int(round(ow * S))) if ow else 0)
    def ell(self, c, a, b, ang, fill, ow=1.8):
        pts = []
        for k in range(0, 360, 8):
            t = math.radians(k); x, y = a * math.cos(t), b * math.sin(t)
            ca, sa = math.cos(ang), math.sin(ang); pts.append((c[0] + x * ca - y * sa, c[1] + x * sa + y * ca))
        self.poly(pts, fill, ow)
    def done(self):
        small = self.lay.resize((self.x1 - self.x0, self.y1 - self.y0), Image.LANCZOS)
        base = self.img.convert('RGBA'); base.alpha_composite(small, (self.x0, self.y0)); return base.convert('RGB')

STICK = (250, 248, 240, 255)

def stick(pen, p, dvec, L, w=3.0, ink=1.3):
    """막대사탕의 흰 막대(원반 테두리 p 에서 바깥 dvec 으로 L) — 【막대사탕】(당 사슬 · L48d · L53a) 그대로."""
    q0 = (p[0] - dvec[0] * 3, p[1] - dvec[1] * 3); q1 = (p[0] + dvec[0] * L, p[1] + dvec[1] * L)
    pen.seg(q0, q1, w + 2 * ink, INK); pen.seg(q0, q1, w, STICK)
    return q1

def tag_A(pen, p, dvec, L=13.0, r=7.6):
    """A 항원 — 초록 알사탕 하나를 단 막대사탕(알 하나 = A · 알 둘 = B). 원반 테두리 p · 바깥 dvec.
    ⚠ 세모 사탕은 막대에 꽂으면 「화살촉」이 되어(초판) 둥근 알로."""
    ux, uy = dvec
    q = stick(pen, p, dvec, L, w=3.6, ink=1.4)
    c = (q[0] + ux * r * 0.85, q[1] + uy * r * 0.85)
    X, Y = pen.P(c); R = r * S
    pen.d.ellipse([X - R, Y - R, X + R, Y + R], fill=GREEN, outline=INK, width=int(round(1.7 * S)))
    h = (c[0] - r * 0.35, c[1] - r * 0.38); Hx, Hy = pen.P(h); hr = r * 0.27 * S
    pen.d.ellipse([Hx - hr, Hy - hr, Hx + hr, Hy + hr], fill=(214, 244, 200, 255))

def tag_B(pen, p, dvec, r=6.2, L=9.0):
    """B 항원 — 주황 알사탕 둘을 나란히 붙인 사탕(B 자의 두 배)을 단 막대사탕. 사탕 바깥 끝까지의 거리를 돌려준다.
    ⚠ 보라로 칠하면 동글동글한 알이 【동글동글한 포도】(포도당)로 읽힐 수 있어 주황으로."""
    ux, uy = dvec; tx, ty = -uy, ux
    q = stick(pen, p, dvec, L, w=2.4 if r > 4 else 1.6, ink=1.1 if r > 4 else 0.9)
    for sg in (1, -1):
        c = (q[0] + tx * r * 0.85 * sg + ux * r * 0.8, q[1] + ty * r * 0.85 * sg + uy * r * 0.8)
        X, Y = pen.P(c); R = r * S
        pen.d.ellipse([X - R, Y - R, X + R, Y + R], fill=ORANGE, outline=INK, width=max(1, int(round((1.6 if r > 4 else 1.1) * S))))
        if r > 4:
            h = (c[0] - tx * r * 0.35 * sg - ux * r * 0.1 - r * 0.25, c[1] - ty * r * 0.35 * sg - uy * r * 0.1 - r * 0.3)
            Hx, Hy = pen.P(h); hr = r * 0.28 * S; pen.d.ellipse([Hx - hr, Hy - hr, Hx + hr, Hy + hr], fill=(255, 236, 200, 255))
    return L + r * 1.8

def claw(pen, p, dvec, ext, r=6.2, w=3.0, ink=1.4):
    """집게발 — 막대사탕 끝의 주황 알 둘(p 에서 바깥 dvec · 사탕 바깥 끝 ext)을 양옆에서 감싸 문 엷은 두 갈래(L46c s8 집게처럼 · 끝이 안으로 굽음). 팔이 닿을 점."""
    ux, uy = dvec; tx, ty = -uy, ux
    root = (p[0] + ux * (ext + 6), p[1] + uy * (ext + 6))
    prongs = []
    mid = ext - r * 1.0
    for sg in (1, -1):
        tip = (p[0] + tx * sg * (r * 1.2) + ux * (mid - r * 0.9), p[1] + ty * sg * (r * 1.2) + uy * (mid - r * 0.9))   # 알 밑 · 막대 곁으로 굽어 듦
        ctl = (p[0] + tx * sg * (r * 3.6) + ux * (ext + 3), p[1] + ty * sg * (r * 3.6) + uy * (ext + 3))
        prongs.append(qb(root, ctl, tip, 16))
    for col, ww in ((INK, w + 2 * ink), (JAW, w)):
        for pts in prongs: pen.path(pts, ww, col)
    return root

def clamp(pen, t1, t2, out, stem=34.0, fork_h=34.0, w=5.4, ink=1.8):
    """다리 놓는 Y 집게(항B) — t1 · t2 = (원반, 테두리 각) 두 주황 혹 자리 · out = 깃대 방향(덩어리 바깥)."""
    (p1, n1), (p2, n2) = rim(*t1), rim(*t2)
    mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    o = unit(out); fork = (mid[0] + o[0] * fork_h, mid[1] + o[1] * fork_h)
    roots = []
    for p, n in ((p1, n1), (p2, n2)):
        f = unit((fork[0] - p[0], fork[1] - p[1])); dv = unit((f[0] * 0.7 + n[0] * 0.3, f[1] * 0.7 + n[1] * 0.3))
        ext = tag_B(pen, p, dv)
        roots.append(claw(pen, p, dv, ext))
    en = (fork[0] + o[0] * stem, fork[1] + o[1] * stem)
    hd = (fork[0] + o[0] * stem * 0.5, fork[1] + o[1] * stem * 0.5)
    for col, ww in ((INK, w + 2 * ink), (BLUE, w)):
        for e in roots: pen.seg(fork, e, ww, col)
        pen.seg(fork, en, ww + 0.8, col)
    pen.seg(hd, en, w + 0.8 + 2 * ink, INK); pen.seg(hd, en, w + 0.8, BLUE_D)

def erase_falling(img):
    """GB 가 그린 바늘 밑 작은 원반 셋을 지운다(유리 안 바탕으로 메움) — 왼위 집게 자리를 비우고 원반은 바늘 바로 밑에 다시 그린다."""
    a = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    x0, y0, x1, y1 = 300, 212, 350, 264
    c = a[y0:y1, x0:x1].astype(int)
    bg = np.median(a[200:212, 330:350].reshape(-1, 3), axis=0)              # 유리 안 바탕 빛깔
    m = (np.abs(c - bg).max(axis=2) > 18).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    M = np.zeros(a.shape[:2], np.uint8); M[y0:y1, x0:x1] = m
    M[260:, :] = 0                                                         # 덩어리(왼앞 원반) 윗선은 남긴다
    a = cv2.inpaint(a, M, 7, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))

def brighten_donor(img):
    """GB 의 덩어리 원반은 자줏빛 빨강(195,72,85)이라 식탁 원반(205,35,35)과 「다른 것」으로 읽힐 수 있다(일치 검사 1회) — 빨강만 식탁 빛깔 쪽으로."""
    a = np.array(img).astype(np.float32); x0, y0, x1, y1 = 270, 225, 602, 336
    c = a[y0:y1, x0:x1]; r, g, b = c[..., 0], c[..., 1], c[..., 2]
    m = ((r - g) > 70) & (g < 112)
    c[..., 0] = np.where(m, np.clip(r * 1.06, 0, 255), r); c[..., 1] = np.where(m, g * 0.55, g); c[..., 2] = np.where(m, b * 0.45, b)
    a[y0:y1, x0:x1] = c
    return Image.fromarray(a.astype(np.uint8))

def falling(pen):
    """바늘 끝 바로 밑으로 떨어지는 남의 원반 둘(윗쪽 테두리에 주황 혹 하나씩 — 양 끝에 달면 「사탕 껍질」로 보인다)."""
    for c, a, b, ang in (((291, 224), 14, 8, 0.35), ((285, 250), 14.5, 8.5, -0.4)):
        ux, uy = math.cos(ang), math.sin(ang)
        q = (c[0] + uy * b * 0.95, c[1] - ux * b * 0.95); tag_B(pen, q, (uy, -ux), r=2.9, L=5.0)
        pen.ell(c, a, b, ang, RED, 1.6)
        pen.ell((c[0] - 0.6, c[1] - 0.6), a * 0.52, b * 0.45, ang, PINK, 0.0)

def bag_dots(pen, img):
    """벽의 피 주머니 속 원반(작다)마다 주황 점 하나 — 들어오는 남의 원반이 모두 B(주황 알사탕)라는 표. 원반 가운데의 옅은 분홍 무늬를 찾아 그 오른 위 테두리에."""
    a = np.array(img).astype(int); x0, y0, x1, y1 = 74, 92, 178, 184
    c = a[y0:y1, x0:x1]; r, g, b = c[..., 0], c[..., 1], c[..., 2]
    m = ((r > 185) & (g > 110) & (g < 175) & (b > 120) & (b < 190)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    pts = sorted([(cen[i][0] + x0, cen[i][1] + y0) for i in range(1, n) if st[i][4] >= 6], key=lambda q: (q[1], q[0]))
    used = []
    for q in pts:
        if any(math.hypot(q[0] - u[0], q[1] - u[1]) < 11 for u in used): continue
        used.append(q)
        d = (q[0] + 5.5, q[1] - 4.5); X, Y = pen.P(d); R = 2.7 * S
        pen.d.ellipse([X - R, Y - R, X + R, Y + R], fill=ORANGE, outline=INK, width=int(1.0 * S))
    return len(used)

def main(src, out):
    img = brighten_donor(erase_falling(Image.open(src).convert('RGB')))
    pen = Pen(img, (40, 20, 260, 220))
    nb = bag_dots(pen, img); img = pen.done()
    # ② · ③ 남의 원반 덩어리(B) + 항B 집게
    pen = Pen(img, (250, 140, 620, 410))
    falling(pen)
    for k, deg in ((1, 180), (5, 0)):     # 맨 밑에 달면 「발」로 보여 옆에만 · 나머지는 집게에 물린 것
        p, n = rim(k, deg); tag_B(pen, p, n)
    clamp(pen, (1, 30), (4, 165), (0, 1), stem=14, fork_h=24, w=4.8)          # 아래 왼쪽 — 1 · 4(앞가운데 원반도 엮는다 · 일치 검사 2회 「덩어리 느낌 약함」)
    clamp(pen, (4, 15), (5, 150), (0, 1), stem=14, fork_h=24, w=4.8)          # 아래 오른쪽 — 4 · 5
    clamp(pen, (1, -115), (2, -160), (-0.30, -0.95), stem=30, fork_h=30)     # 왼 위 — 1 · 2
    clamp(pen, (2, -60), (3, -120), (0, -1))                                # 위 — 2 · 3
    clamp(pen, (3, -25), (5, -75), (0.40, -0.92), stem=30, fork_h=32)        # 오른 위 — 3 · 5
    img = pen.done()
    # ① 병 주인의 원반(A) — 식탁 넷 · 아령 · 당구 치는 원반
    pen = Pen(img, (640, 560, 1700, 990))
    for k, deg in (('T1', -160), ('T1', -115), ('T1', 165), ('T2', -30), ('T2', 15), ('T3', 172), ('T3', 120), ('T3', 60), ('T3', -8),
                   ('T4', -25), ('T4', 75), ('T4', 125), ('T4', 168), ('DT', -160), ('DB', 20),
                   ('CH', -140), ('CH', -95), ('CH', -170), ('CH', -58)):
        p, n = rim(k, deg); tag_A(pen, p, n, L=10.0, r=10.5 if k != 'CH' else 11.5)
    pen.done().save(out)
    print('주머니 점', nb)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

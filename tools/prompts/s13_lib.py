#!/usr/bin/env python3
# s13_lib.py — 세계 s13 「성 방어전」의 공용 그리기 도구(L13b 부터 — L13a_pil.py 의 것을 그대로 옮겼다 · L13a 는 제 사본을 그대로 쓴다).
#  Canvas: 2048 x 1144 그림 한 장 + 3 배 PIL 겹(layer) · 성벽(castle_wall — L13a 와 같은 성) · 조각 오리기(comp_sprite) · 붙이기(place) · 붉은 리본 배지(badge) · 그림자.
import math, numpy as np, cv2
from PIL import Image, ImageDraw

W, H = 2048, 1144
INK = (24, 20, 18, 255)
GND = (239, 232, 202)
SKY = (128, 203, 242, 255)
WALL, WALL_D, WALL_L, WALL_IN = (165, 165, 165, 255), (118, 118, 118, 255), (180, 180, 180, 255), (106, 106, 106, 255)
SHADOW = (203, 196, 168, 255)
RED, RED_D, GOLD_C = (226, 46, 42, 255), (188, 34, 34, 255), (250, 208, 62, 255)
S = 3
# 성벽 · 틈(L13a 와 같은 좌표 — 같은 성)
TOP, FLOOR, LEDGE, WB = 46, 96, 178, 430
GAP_L = [(632, TOP), (632, 120), (648, 120), (648, 168), (636, 168), (636, 214), (658, 214), (658, 262), (646, 262), (646, 300), (668, 300), (668, 350), (658, 350), (658, 392), (678, 392), (678, WB)]
GAP_R = [(884, TOP), (884, 112), (868, 112), (868, 160), (880, 160), (880, 206), (858, 206), (858, 250), (870, 250), (870, 296), (848, 296), (848, 344), (860, 344), (860, 388), (838, 388), (838, WB)]
TH = 26

def T(pts): return [(x * S, y * S) for x, y in pts]
def poly(d, pts, fill, w=3.2, close=True):
    q = T(pts)
    if fill: d.polygon(q, fill=fill)
    if w:
        d.line(q + ([q[0]] if close else []), fill=INK, width=int(w * S), joint='curve')
        for x, y in q: r = w * S / 2; d.ellipse([x - r, y - r, x + r, y + r], fill=INK)
def line(d, pts, w=3.2, col=INK):
    q = T(pts); d.line(q, fill=col, width=int(w * S), joint='curve')
    for x, y in q: r = w * S / 2; d.ellipse([x - r, y - r, x + r, y + r], fill=col)
def disc(d, cx, cy, r, fill, w=2.4):
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=INK if w else fill)
    if w: d.ellipse([(cx - r + w) * S, (cy - r + w) * S, (cx + r - w) * S, (cy + r - w) * S], fill=fill)
def ellipse(d, cx, cy, rx, ry, fill): d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill)
def chaikin(pts, it=2, closed=True):
    for _ in range(it):
        q = []
        pairs = list(zip(pts, pts[1:] + pts[:1])) if closed else list(zip(pts, pts[1:]))
        for (x0, y0), (x1, y1) in pairs:
            q += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = q if closed else [pts[0]] + q + [pts[-1]]
    return pts
def edge_x(g, y):
    for (x0, y0), (x1, y1) in zip(g, g[1:]):
        if x0 == x1 and y0 <= y <= y1: return x0

class Canvas:
    def __init__(self, zdir):
        self.zdir = zdir; self.im = Image.new('RGB', (W, H), GND); self._cache = {}
    def layer(self): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    def put(self, lay):
        small = lay.resize((W, H), Image.LANCZOS)
        base = self.im.convert('RGBA'); base.alpha_composite(small); self.im = base.convert('RGB')
    def paste(self, sp, x0, y0):
        base = self.im.convert('RGBA'); base.alpha_composite(sp, (round(x0), round(y0))); self.im = base.convert('RGB')

    # ── 하늘 · 성벽 · 틈(L13a ① 그대로)
    def castle_wall(self, stones=((70, 222, 70, 30), (232, 282, 58, 26), (420, 232, 62, 28), (552, 286, 54, 26), (932, 226, 60, 28), (1128, 214, 58, 26), (1300, 286, 62, 28), (1392, 226, 56, 26), (1560, 300, 60, 26), (1700, 230, 58, 28), (1860, 292, 62, 26), (1980, 226, 54, 26))):
        lay = self.layer(); d = ImageDraw.Draw(lay)
        d.rectangle([0, 0, W * S, WB * S], fill=SKY)
        d.rectangle([0, WB * S, W * S, H * S], fill=GND + (255,))
        d.rectangle([600 * S, 396 * S, 960 * S, (WB + 4) * S], fill=GND + (255,)); line(d, [(600, 396), (960, 396)], 3.0)
        poly(d, GAP_L + [(x + TH, y) for x, y in reversed(GAP_L)], WALL_IN, 3.2)
        poly(d, GAP_R + [(x - TH, y) for x, y in reversed(GAP_R)], WALL_IN, 3.2)
        poly(d, [(-10, FLOOR), (GAP_L[0][0], FLOOR)] + GAP_L[1:] + [(-10, WB)], WALL, 3.4)
        poly(d, [(GAP_R[0][0], FLOOR), (W + 10, FLOOR), (W + 10, WB)] + list(reversed(GAP_R[1:])), WALL, 3.4)
        for xa, xb in ((-10, edge_x(GAP_L, LEDGE + 7)), (edge_x(GAP_R, LEDGE + 7), W + 10)):
            d.rectangle([xa * S, LEDGE * S, xb * S, (LEDGE + 14) * S], fill=WALL_L)
            line(d, [(xa, LEDGE), (xb, LEDGE)], 3.0); line(d, [(xa, LEDGE + 14), (xb, LEDGE + 14)], 3.0)
        MW, MS, PITCH = 62, 14, 124
        for k in range(-1, 18):
            x = 18 + k * PITCH
            if x + MW + MS > GAP_L[0][0] - 4 and x < GAP_R[0][0] + 4: continue
            poly(d, [(x + MW, TOP), (x + MW + MS, TOP + 6), (x + MW + MS, FLOOR), (x + MW, FLOOR)], WALL_D, 3.0)
            poly(d, [(x, TOP), (x + MW, TOP), (x + MW, FLOOR), (x, FLOOR)], WALL, 3.2)
            d.rectangle([(x + 2) * S, (FLOOR - 2) * S, (x + MW - 2) * S, (FLOOR + 3) * S], fill=WALL)
        poly(d, [(GAP_L[0][0] - 44, TOP), (GAP_L[0][0], TOP), (GAP_L[0][0], FLOOR), (GAP_L[0][0] - 44, FLOOR)], WALL, 3.2)
        d.rectangle([(GAP_L[0][0] - 42) * S, (FLOOR - 2) * S, (GAP_L[0][0] - 2) * S, (FLOOR + 3) * S], fill=WALL)
        poly(d, [(GAP_R[0][0], TOP), (GAP_R[0][0] + 50, TOP), (GAP_R[0][0] + 50, FLOOR), (GAP_R[0][0], FLOOR)], WALL, 3.2)
        d.rectangle([(GAP_R[0][0] + 2) * S, (FLOOR - 2) * S, (GAP_R[0][0] + 48) * S, (FLOOR + 3) * S], fill=WALL)
        for (sx, sy, sw, sh) in stones:
            d.rounded_rectangle([sx * S, sy * S, (sx + sw) * S, (sy + sh) * S], radius=7 * S, fill=INK)
            d.rounded_rectangle([(sx + 3) * S, (sy + 3) * S, (sx + sw - 3) * S, (sy + sh - 3) * S], radius=5 * S, fill=(146, 146, 142, 255))
        line(d, [(-10, WB), (GAP_L[-1][0], WB)], 3.6); line(d, [(GAP_R[-1][0], WB), (W + 10, WB)], 3.6)
        self.put(lay)

    # ── 조각 오리기(L13a 그대로): 조각 그림에서 hint 상자 안의 덩이(들)만 · 가장자리에서 이어진 바탕빛은 투명 · holes = 갇힌 바탕빛도(True 또는 상자 목록)
    def comp_sprite(self, name, hint, holes=False, tol=18, fix=None, min_area=150):
        if name not in self._cache:
            c = np.array(Image.open(f'{self.zdir}/gem_{name}.png').convert('RGB')).astype(int)
            bg = np.median(np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]]), axis=0)
            bgm = (np.abs(c - bg).max(axis=2) <= tol)
            n, lab = cv2.connectedComponents(bgm.astype(np.uint8), connectivity=4)
            border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); border = border[border != 0]
            fg = (~np.isin(lab, border)).astype(np.uint8)
            n2, lab2, st, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
            self._cache[name] = (c, lab2, st, bgm)
        c, lab2, st, bgm = self._cache[name]
        if fix is not None: c = fix(c.copy())
        x0, y0, x1, y1 = hint
        ids = [i for i in range(1, len(st)) if st[i][0] >= x0 and st[i][1] >= y0 and st[i][0] + st[i][2] <= x1 and st[i][1] + st[i][3] <= y1 and st[i][4] >= min_area]
        m = np.isin(lab2, ids); ys, xs = np.where(m); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        if holes is True: m = m & ~bgm
        elif holes:
            hb = np.zeros_like(bgm)
            for hx0, hy0, hx1, hy1 in holes: hb[hy0:hy1, hx0:hx1] = True
            m = m & ~(bgm & hb)
        al = (m[by0:by1, bx0:bx1] * 255).astype(np.uint8)
        al = cv2.erode(al, np.ones((3, 3), np.uint8)); al = cv2.GaussianBlur(al, (0, 0), 0.9)
        sp = Image.fromarray(np.dstack([c[by0:by1, bx0:bx1].astype(np.uint8), al]), 'RGBA')
        sp.origin = (bx0, by0)
        return sp
    def place(self, sp, scale, cx, bottom, flip=False):
        """조각을 scale 배로 아래 가운데가 (cx, bottom) 에 오게 붙이고, 조각 그림 좌표 → 그림 좌표 함수를 돌려준다."""
        w, h = max(1, round(sp.width * scale)), max(1, round(sp.height * scale))
        s2 = sp.resize((w, h), Image.LANCZOS)
        if flip: s2 = s2.transpose(Image.FLIP_LEFT_RIGHT)
        x0, y0 = round(cx - w / 2), round(bottom - h)
        self.paste(s2, x0, y0)
        ox, oy = sp.origin
        if flip: return lambda x, y: (x0 + w - (x - ox) * scale, y0 + (y - oy) * scale)
        return lambda x, y: (x0 + (x - ox) * scale, y0 + (y - oy) * scale)

def badge(d, cx, cy, r):
    """붉은 리본 배지(로제트) — 자기(self)의 표지(L13a 와 같은 꼴)."""
    w = max(1.5, r * 0.16)
    for sx in (-1, 1):
        poly(d, [(cx + sx * 0.10 * r, cy + 0.55 * r), (cx + sx * 0.62 * r, cy + 0.50 * r), (cx + sx * 0.98 * r, cy + 1.85 * r), (cx + sx * 0.58 * r, cy + 1.55 * r), (cx + sx * 0.30 * r, cy + 1.95 * r)], RED_D, w)
    for k in range(10):
        a = 2 * math.pi * k / 10; disc(d, cx + 0.80 * r * math.cos(a), cy + 0.80 * r * math.sin(a), 0.30 * r, RED, w)
    d.ellipse([(cx - 0.84 * r) * S, (cy - 0.84 * r) * S, (cx + 0.84 * r) * S, (cy + 0.84 * r) * S], fill=RED)
    disc(d, cx, cy, 0.38 * r, GOLD_C, w)

# ── 빛깔 손질(L13a 그대로)
def inpaint(c, boxes, dark=110):
    a = c.astype(np.uint8); m = np.zeros(a.shape[:2], np.uint8)
    for x0, y0, x1, y1 in boxes: m[y0:y1, x0:x1] = (a[y0:y1, x0:x1].max(axis=2) < dark) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    return cv2.inpaint(a, m, 4, cv2.INPAINT_TELEA).astype(int)
def unred(c, box):
    r = c[box[1]:box[3], box[0]:box[2]]; R_, G_, B_ = r[..., 0], r[..., 1], r[..., 2]
    m = (R_ - np.maximum(G_, B_) > 70)
    r[m] = np.stack([R_[m] * 0.62, R_[m] * 0.44, R_[m] * 0.27], axis=1).astype(int)
    return c
def whiten(c, box):
    r = c[box[1]:box[3], box[0]:box[2]]; m = (r.min(axis=2) > 200) & (r[..., 0] - r[..., 2] < 46)
    r[m] = 255
    return c

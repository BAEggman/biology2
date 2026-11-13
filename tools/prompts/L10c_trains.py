#!/usr/bin/env python3
# L10c_trains.py <in.png> <out.png> — L10c 「조차장의 오타 열차」의 PIL 손질.
# 세어야 하는 것 · 빛깔이 곧 뜻인 것은 Gemini 에게 맡기지 않고 여기서 그린다:
#  ⓪ 바탕의 빈 선로 여섯을 지우고 같은 꼴(겹줄 · 침목 없음 · 오른쪽 끝 빨간 차막이)로 조금 아래에 다시 긋는다 — 첫 열차의 구슬 사슬이 수리공의 발 · 망치와 겹치지 않게
#  ① 선로 여섯 위의 열차 여섯(원본 · 침묵 · 과오 · 정지 · 삽입 · 결실) — 객차 = 코돈 · 창 = 염기(초록 A · 파랑 U · 빨강 G · 노랑 C · L10b 와 같은 객차)
#  ② 열차마다 위에 걸린 구슬 사슬(객차 하나에 구슬 하나 · 종결 자리는 작은 나무판) — 실제 유전암호(L10c_seq.py)
#  ③ 빨간 색연필 동그라미 다섯(고친 자리)
#  ④ 사다리(DNA): 약병 방울을 맞은 칸 하나를 보라로 얼룩지게
import sys, math, os, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from L10c_seq import TRAINS, beads
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGBA')
INK = (24, 20, 18, 255)
BASE = {'A': (86, 176, 96, 255), 'U': (66, 128, 222, 255), 'G': (226, 74, 62, 255), 'C': (246, 206, 64, 255)}
BODY, ROOF, TYRE, HUB = (172, 187, 203, 255), (117, 131, 142, 255), (44, 46, 50, 255), (176, 177, 184, 255)
AACOL = {  # 구슬 빛깔 = 아미노산(창의 네 빛깔과 겹치지 않게) — 원본: 금 · 주황 · 분홍 · 청록 · 보라
    'M': (245, 196, 58, 255), 'E': (240, 140, 50, 255), 'Q': (242, 128, 176, 255), 'T': (64, 190, 180, 255), 'I': (150, 96, 196, 255),
    'V': (40, 40, 46, 255),                                                                                   # 과오: 검정(발린)
    'R': (156, 104, 58, 255), 'A': (172, 172, 178, 255), 'N': (250, 250, 250, 255), 'H': (34, 52, 124, 255), 'L': (132, 132, 56, 255),   # 삽입 뒤: 갈색 · 회색 · 흰색 · 남색 · 올리브
    'S': (176, 214, 84, 255), 'K': (124, 34, 48, 255), 'P': (92, 62, 40, 255), 'F': (92, 92, 102, 255),      # 결실 뒤: 연두 · 검붉은색 · 고동색 · 진회색
}
RT = [502, 614, 726, 838, 950, 1062]      # 선로 윗줄의 y(다시 그은 선로 여섯)
X0, PITCH = 272, 112
RX0, RX1 = 258, 1004                      # 선로의 왼끝 · 오른끝(차막이 앞)

class Patch:
    def __init__(s, x0, y0, x1, y1, S=4):
        s.b = (x0, y0, x1, y1); s.S = S; s.lay = Image.new('RGBA', ((x1 - x0) * S, (y1 - y0) * S), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.lay)
    def T(s, pts): return [((x - s.b[0]) * s.S, (y - s.b[1]) * s.S) for x, y in pts]
    def line(s, pts, fill, w, cap=True):
        W = max(1, int(round(w * s.S))); q = s.T(pts); s.d.line(q, fill=fill, width=W, joint='curve')
        if cap:
            for x, y in (q[0], q[-1]): s.d.ellipse([x - W / 2, y - W / 2, x + W / 2, y + W / 2], fill=fill)
    def poly(s, pts, fill, ink=INK, o=2.2):
        q = s.T(pts); s.d.polygon(q, fill=fill)
        if ink: s.d.line(q + [q[0]], fill=ink, width=int(round(o * s.S)), joint='curve')
    def ell(s, cx, cy, rx, ry, fill, ink=INK, o=2.2):
        (x0, y0), (x1, y1) = s.T([(cx - rx, cy - ry), (cx + rx, cy + ry)]); s.d.ellipse([x0, y0, x1, y1], fill=fill, outline=ink, width=int(round(o * s.S)) if ink else 0)
    def rrect(s, x0, y0, x1, y1, r, fill, ink=INK, o=2.2):
        (a, b), (c, e) = s.T([(x0, y0), (x1, y1)]); s.d.rounded_rectangle([a, b, c, e], radius=r * s.S, fill=fill, outline=ink, width=int(round(o * s.S)) if ink else 0)
    def done(s):
        x0, y0, x1, y1 = s.b; small = s.lay.convert('RGBa').resize((x1 - x0, y1 - y0), Image.LANCZOS).convert('RGBA'); im.alpha_composite(small, (x0, y0))
def rot(pts, cx, cy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg)); return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]
def bead(P, cx, cy, r, col, o=1.9):
    P.ell(cx, cy, r, r, col, INK, o); P.ell(cx - r * 0.32, cy - r * 0.36, r * 0.30, r * 0.24, (255, 255, 255, 235), None)
def miniplank(P, cx, cy, w=15, h=24, deg=-9):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    P.poly(rot([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], cx, cy, deg), (198, 146, 92, 255), INK, 1.8)
    for t, k in ((0.3, 0.04), (0.55, -0.05), (0.78, 0.03)):
        P.line(rot([(x0 + w * t, y0 + 3), (x0 + w * (t + k), cy), (x0 + w * t, y1 - 3)], cx, cy, deg), (150, 104, 62, 255), 0.9, cap=False)
WW, WH, WG, WM = 24, 22, 7, 10            # 창 너비 · 높이 · 사이 · 가장자리
def carw(n): return 2 * WM + n * WW + (n - 1) * WG
def car(P, x, rt, cod):
    """객차 한 대(창 1 ~ 3) — 왼쪽 위 x · 선로 윗줄 rt. 창의 한가운데 좌표를 돌려준다."""
    n = len(cod); w = carw(n); by0, by1 = rt - 64, rt - 12
    for cx in ((x + 26, x + w - 26) if n == 3 else (x + w / 2,)):
        P.ell(cx, rt - 7, 9.8, 9.8, TYRE, INK, 1.6); P.ell(cx, rt - 7, 4.0, 4.0, HUB, None)
    P.rrect(x, by0 - 4, x + w, by1, 8, BODY, INK, 2.4)
    P.poly([(x - 3, by0 - 7), (x + w + 3, by0 - 7), (x + w + 3, by0), (x - 3, by0)], ROOF, INK, 2.2)
    cs = []
    for k, b in enumerate(cod):
        wx = x + WM + k * (WW + WG); wy = by0 + 11
        P.poly([(wx, wy), (wx + WW, wy), (wx + WW, wy + WH), (wx, wy + WH)], BASE[b], INK, 2.0)
        cs.append((wx + WW / 2, wy + WH / 2))
    return cs
def circle(P, cx, cy, rx=18, ry=17):
    """빨간 색연필 동그라미(끝이 살짝 겹친 손 동그라미)."""
    pts = []
    for k in range(0, 41):
        a = math.radians(-100 + 396 * k / 40); r = 1 + 0.035 * math.sin(3 * a) + (0.05 * (k / 40 - 0.5) if k > 30 else 0)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    P.line(pts, (224, 44, 44, 255), 4.0)

# ── ⓪ 바탕의 빈 선로 여섯(x 180 ~ 1040 · y 462 ~ 1092)을 땅 빛으로 지운다 — 줄마다 왼쪽 · 오른쪽 가장자리의 빛을 이어서
a = np.array(im)
Y0, Y1, XA, XB = 442, 1100, 262, 1034
left = np.median(a[Y0:Y1, XA - 8:XA, :3], axis=1).astype(float); right = np.median(a[Y0:Y1, XB:XB + 8, :3], axis=1).astype(float)
t = np.linspace(0, 1, XB - XA)[None, :, None]
a[Y0:Y1, XA:XB, :3] = np.clip(left[:, None, :] * (1 - t) + right[:, None, :] * t + 0.5, 0, 255).astype(np.uint8)
# 원숭이를 좌우로 뒤집는다 — Gemini 가 오른쪽(열차 쪽)으로 걷게 그렸다 → 창을 빼 들고 열차에서 멀어지게(왼쪽으로)
import cv2
_r = a[950:1140, 30:250, :3]; _g = np.median(a[1120:1138, 232:250, :3].reshape(-1, 3), axis=0).astype(int)
_nb = (np.abs(_r.astype(int) - _g[None, None, :]).max(axis=2) > 14).astype(np.uint8)
_n, _lab, _st, _ = cv2.connectedComponentsWithStats(cv2.dilate(_nb, np.ones((3, 3), np.uint8)), 8)
_k = max((k for k in range(1, _n) if _st[k, 1] + _st[k, 3] > 150), key=lambda k: _st[k, 4])        # 바닥(y ≥ 1100)까지 닿는 가장 큰 덩이 = 원숭이
_m = cv2.dilate((_lab == _k).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
_xs = np.where(_m.any(axis=0))[0]; _x0, _x1 = int(_xs.min()), int(_xs.max())
_new = _r.copy(); _new[_m] = _g
_ys, _xx = np.where(_m); _new[_ys, _x0 + _x1 - _xx] = _r[_ys, _xx]
a[950:1140, 30:250, :3] = _new
# 왼쪽 두 구역(ZA · ZB)이 만나는 줄(y ≈ 803)에 남은 옅은 가로 자국을 땅 빛으로
sm = a[796:810, 24:246, :3].astype(int); g2 = np.median(a[820:840, 26:60, :3].reshape(-1, 3), axis=0).astype(int)
lightm = (sm.min(axis=2) > 186) & (np.abs(sm - g2[None, None, :]).max(axis=2) < 40)
sm[lightm] = g2; a[796:810, 24:246, :3] = sm.astype(np.uint8)
# ── ④-나 약병 방울을 맞은 사다리 칸(x ≈ 924) 하나를 보라로 얼룩지게
rg = a[160:212, 914:936, :3].astype(int); redm = (rg[..., 0] > 150) & (rg[..., 1] < 140) & (rg[..., 2] < 140)
lum = rg.mean(axis=2, keepdims=True) / 130.0
rg[redm] = np.clip(np.array((150, 96, 196))[None, None, :] * np.clip(lum, 0.8, 1.1), 0, 255)[redm]; a[160:212, 914:936, :3] = rg.astype(np.uint8)
# 바탕 그림의 잿빛 방울 둘(x 936 ~ 964 · y 118 ~ 149)을 하늘빛으로 지우고 보라 방울 셋을 그 칸 쪽으로 다시 그린다
sky = np.median(a[120:146, 968:990, :3].reshape(-1, 3), axis=0).astype(np.uint8)
a[117:150, 934:966, :3] = sky
im = Image.fromarray(a)
P = Patch(900, 108, 980, 170)
PUR = (150, 96, 196, 255)
def drop(cx, cy, r=5.2):
    pts = [(cx, cy - r * 2.1)] + [(cx + r * math.cos(math.radians(t)), cy + r * math.sin(math.radians(t))) for t in range(-35, 216, 10)]
    P.poly(pts, PUR, INK, 1.7); P.ell(cx - r * 0.3, cy - r * 0.1, r * 0.24, r * 0.3, (232, 214, 250, 255), None)
drop(944, 126); drop(937, 139); drop(930, 147, 4.6)
P.done()
# 휜 붉은 원반(겸상적혈구)의 손에 검은 구슬 — 과오 열차의 검은 구슬과 같은 것
P = Patch(1250, 770, 1320, 830)
bead(P, 1287, 803, 11.5, (40, 40, 46, 255))
P.done()
# ── ⓪ 선로 여섯을 다시 긋는다(겹줄 + 오른쪽 끝 빨간 차막이)
RAILC = (150, 152, 156, 255)
for rt in RT:
    P = Patch(RX0 - 6, rt - 26, RX1 + 26, rt + 34)
    for dy in (0, 12):
        P.poly([(RX0, rt + dy), (RX1, rt + dy), (RX1, rt + dy + 6.5), (RX0, rt + dy + 6.5)], RAILC, INK, 1.8)
    P.rrect(RX1 + 2, rt - 20, RX1 + 17, rt + 28, 2, (190, 62, 56, 255), INK, 2.2)
    P.done()

# ── ① ② ③ 열차 여섯
info = []
for ti, (name, seq, pos, kind) in enumerate(TRAINS):
    rt = RT[ti]
    P = Patch(X0 - 20, rt - 102, 1008, rt + 6)
    cods = [seq[i:i + 3] for i in range(0, len(seq), 3)]
    xs = []; x = X0; wins = []
    for cod in cods:
        cs = car(P, x, rt, cod); xs.append((x, carw(len(cod)))); wins += cs; x += carw(len(cod)) + (PITCH - carw(3))
    bs = beads(seq); cy = rt - 64 - 7 - 12
    pts = [(xs[i][0] + xs[i][1] / 2, cy) for i in range(len(bs))]
    if len(pts) > 1: P.line(pts, (96, 84, 72, 255), 2.2)
    for (bx, by), aa in zip(pts, bs):
        if aa == '*': miniplank(P, bx, by + 1)
        else: bead(P, bx, by, 10.0, AACOL[aa])
    if kind in ('sub', 'ins'): circle(P, *wins[pos])
    elif kind == 'del': circle(P, xs[1][0] - 3, wins[pos][1], 12, 19)                # 빠진 자리 = 둘째 객차 앞머리
    P.done()
    info.append((name, ''.join(bs), [(int(a_), int(b_)) for a_, b_ in xs]))
im.convert('RGB').save(dst)
for r in info: print(r)
print('ok', dst)

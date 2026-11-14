#!/usr/bin/env python3
# L13c_pil.py <base.png> <out.png> — L13c 「포위된 성, 내성 문 앞의 첩자 소동」의 PIL 마무리(2026-11-14).
#  바탕 = Gemini 가 통째로 그린 장면 S1(1024 → 2048 확대) + 구역 편집 Z1(흰 덩이 · 전령의 판) · Z2b(판 셋을 떼어 놓음) · Z3(셔츠 깃의 보라 망토).
#  여기서는 「개수 · 자리가 곧 뜻」인 것만 얹는다: 조끼 단추(한 줄 넷 = CD4 · 넷씩 두 줄 = CD8) · 붉은 리본 배지(MHC I — 모두) · 판의 초록 구슬 사슬(외부 항원)
#  · 쟁반의 보라 구슬 사슬(내부 항원) · 대장의 흰 쪽지 두 갈래(사이토카인 → 벌 · 두 줄 단추 병정) · 등불 빛과 한 줄 단추 곁의 작은 깃발(anti-CD4) · 여자의 빈 배지 자리.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s13_lib import S, INK, poly, line, disc, badge

W, H = 2048, 1144
src, dst = sys.argv[1:3]
im = Image.open(src).convert('RGB')
assert im.size == (W, H), im.size

def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay, blur=0):
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    if blur: small = small.filter(ImageFilter.GaussianBlur(blur))
    b = im.convert('RGBA'); b.alpha_composite(small); im = b.convert('RGB')

GOLD = (242, 190, 52, 255)
GREEN = [(118, 204, 84, 255), (74, 160, 58, 255)]
PURPLE = [(150, 96, 206, 255), (104, 60, 164, 255)]

# ── ① 등불 빛(문 위 등불 → 다리 위 앞 병정) — 한 줄로 지나는 병정을 빛이 비춘다(유세포분석)
lay = layer(); d = ImageDraw.Draw(lay)
d.polygon([(1458 * S, 330 * S), (1492 * S, 330 * S), (1452 * S, 712 * S), (1300 * S, 712 * S)], fill=(255, 236, 140, 46))
put(lay, blur=6)

# ── ② 구슬 사슬: 판(MHC II)의 칸마다 초록(밖에서 삼킨 세균의 조각) · 쟁반(MHC I)에 보라(집 안 망토 = 바이러스의 조각)
def chain(d, p0, p1, n, r, cols):
    (x0, y0), (x1, y1) = p0, p1
    pts = [(x0 + (x1 - x0) * k / (n - 1), y0 + (y1 - y0) * k / (n - 1) + (2.2 if k % 2 else -2.2)) for k in range(n)]
    line(d, pts, max(1.6, r * 0.32))
    for k, (x, y) in enumerate(pts): disc(d, x, y, r, cols[k % 2], max(1.5, r * 0.3))
lay = layer(); d = ImageDraw.Draw(lay)
for p0, p1, n, r in (((822, 514), (868, 578), 5, 7.0), ((934, 508), (968, 574), 5, 6.6),     # 벌의 판
                     ((626, 553), (661, 616), 5, 6.2), ((716, 528), (750, 590), 5, 6.2),     # 흰 덩이의 판(기울어짐)
                     ((488, 611), (517, 651), 4, 5.4), ((566, 619), (593, 659), 4, 5.4)):    # 나뭇가지 팔 전령의 판
    chain(d, p0, p1, n, r, GREEN)
chain(d, (1706, 948), (1782, 938), 5, 5.6, PURPLE)                                            # 주민의 쟁반
put(lay)

# ── ③ 조끼 단추: 한 줄 넷 = CD4(도움 T) · 넷씩 두 줄 = CD8(세포독성 T)
lay = layer(); d = ImageDraw.Draw(lay)
def badge_s(d, cx, cy, r):
    """작은 배지(r < 7): 꼬리를 테두리 없는 진홍 세모 둘로 — s13_lib.badge 의 꼬리 테두리선이 작게 줄면 「RR」 같은 글자로 읽혔다(일치 검사 1 · 2회)."""
    from s13_lib import RED, RED_D, GOLD_C
    for sx in (-1, 1):
        d.polygon([((cx + sx * 0.15 * r) * S, (cy + 0.5 * r) * S), ((cx + sx * 0.95 * r) * S, (cy + 0.55 * r) * S), ((cx + sx * 0.7 * r) * S, (cy + 1.75 * r) * S)], fill=RED_D)
    disc(d, cx, cy, r, RED, max(1.2, r * 0.2))
    d.ellipse([(cx - 0.4 * r) * S, (cy - 0.4 * r) * S, (cx + 0.4 * r) * S, (cy + 0.4 * r) * S], fill=GOLD_C)
def col(d, x0, y0, x1, y1, r, n=4):
    for k in range(n): disc(d, x0 + (x1 - x0) * k / (n - 1), y0 + (y1 - y0) * k / (n - 1), r, GOLD, max(1.4, r * 0.32))
col(d, 1080, 528, 1080, 574, 5.2)                                  # 상자 위 대장(CD4)
col(d, 1543, 915, 1543, 979, 6.6); col(d, 1569, 915, 1569, 979, 6.6)   # 쟁반을 낚아챈 병정(CD8)
col(d, 1372, 606, 1372, 651, 4.8)                                  # 다리 위 앞 병정(CD4 — 깃발)
col(d, 1484, 587, 1484, 621, 4.0); col(d, 1500, 587, 1500, 621, 4.0)   # 다리 위 뒤 병정(CD8)
col(d, 349, 960, 384, 988, 5.2)                                    # 부서진 대장(CD4) — 누운 몸의 축을 따라 · 금 간 자리 오른쪽
col(d, 568, 905, 600, 919, 4.8); col(d, 562, 922, 594, 936, 4.8)   # 조는 병정(CD8) — 누운 몸의 축을 따라 두 줄 · 가슴에 얹은 손을 피해 왼쪽으로
put(lay)

# ── ④ 붉은 리본 배지 = MHC I — 성 안의 모두(침입자 · 망토 · 배지를 뜯긴 여자만 없다)
lay = layer(); d = ImageDraw.Draw(lay)
for cx, cy, r in ((318, 395, 5), (551, 565, 8.5), (640, 705, 10), (880, 712, 8.5),             # 틈의 파리채 경비 · 전령 · 흰 덩이 · 벌
                  (1106, 519, 7.5), (1388, 603, 5.5), (1492, 572, 5), (1555, 893, 8),            # 대장 · 다리 위 둘 · 쟁반 병정(배지는 조끼 위 — 붉은 저고리 위에선 묻힌다)
                  (1790, 905, 9), (1912, 150, 6.5),                                               # 주민 · 탑 위 궁수
                  (282, 955, 7), (592, 892, 6.5), (455, 900, 6.5)):                             # 부서진 대장 · 조는 병정 · 조는 벌
    (badge if r >= 7 else badge_s)(d, cx, cy, r)
put(lay)

# ── ④' 굴러간 털모자의 금빛 턱끈(「검은 통 · 대포」가 아니라 병정 모자로 — 일치 검사 2회) · 점을 줄지어 찍으면 단추로 셌다(3회) → 이어진 띠
lay = layer(); d = ImageDraw.Draw(lay)
strap = [((1 - q) ** 2 * 170 + 2 * (1 - q) * q * 226 + q * q * 176, (1 - q) ** 2 * 1032 + 2 * (1 - q) * q * 1076 + q * q * 1118) for q in [k / 20 for k in range(21)]]
line(d, strap, 6.0)                                                  # 먹 테
line(d, strap, 3.4, (246, 196, 60, 255))                             # 금빛 띠
put(lay)

# ── ⑤ 여자의 빈 배지 자리(뜯긴 자국 — 점선 동그라미 + 끊긴 실) — NK 가 겨눈 까닭
lay = layer(); d = ImageDraw.Draw(lay)
disc(d, 1948, 628, 13.5, (176, 230, 220, 255), 0)
for k in range(10):                                               # 점선 테(빠진 것 자리)
    a0 = 2 * math.pi * k / 10; a1 = a0 + 2 * math.pi / 20
    pts = [(1948 + 13.5 * math.cos(a0 + (a1 - a0) * j / 4), 628 + 13.5 * math.sin(a0 + (a1 - a0) * j / 4)) for j in range(5)]
    line(d, pts, 3.0, (22, 52, 50, 255))
disc(d, 1948, 628, 2.2, (28, 66, 62, 255), 0)                     # 핀 구멍(붉은 실 끝은 「상처 · 얼룩」으로 읽혀 지움 — 일치 검사 4회)
put(lay)

# ── ⑥ 대장의 흰 쪽지 두 갈래 = 사이토카인 → 판 든 벌(B) · 쟁반을 낚아챈 두 줄 단추 병정(세포독성 T)
def bez(ps, t):
    if len(ps) == 3: (p0, c, p1) = ps; return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])
    p0, c0, c1, p1 = ps; u = 1 - t
    return tuple(u ** 3 * p0[i] + 3 * u * u * t * c0[i] + 3 * u * t * t * c1[i] + t ** 3 * p1[i] for i in (0, 1))
def note(d, cx, cy, ang, w=15, h=19):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    pts = [(cx + ca * x - sa * y, cy + sa * x + ca * y) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    poly(d, pts, (255, 255, 252, 255), 2.0)
STREAMS = ((((1100, 390), (760, 330), (700, 640), (872, 646)), (0.15, 0.32, 0.5, 0.68, 0.85, 1.0), (-20, 25, -35, 15, -10, 20)),   # 벌의 판을 왼쪽으로 돌아 벌의 머리에
           (((1240, 410), (1450, 330), (1700, 450), (1630, 840)), (0.14, 0.3, 0.46, 0.62, 0.78, 0.94), (30, -15, 40, -25, 10, -40)))   # 다리 위 병정들 머리 위 · 오른쪽으로 돌아 두 줄 단추 병정에게(다리 위 병정이 받는 것처럼 보이지 않게 — 일치 검사 3회)
lay = layer(); d = ImageDraw.Draw(lay)
for ps, ts, angs in STREAMS:                                      # 날아간 자취(점선) — 어디서 어디로 가는지
    n = 46
    for k in range(2, n - 1, 2): line(d, [bez(ps, k / n), bez(ps, (k + 1) / n)], 2.2, (120, 120, 128, 150))
put(lay)
lay = layer(); d = ImageDraw.Draw(lay)
for ps, ts, angs in STREAMS:
    for t_, ag in zip(ts, angs): note(d, *bez(ps, t_), ag)
note(d, 872, 646, 20, 19, 24)                                     # 벌 머리에 닿은 쪽지(크게)
for a_ in (-160, -120, -60, -20):                                 # 「톡」 하는 짧은 선
    tt = math.radians(a_); line(d, [(872 + 19 * math.cos(tt), 646 + 19 * math.sin(tt)), (872 + 30 * math.cos(tt), 646 + 30 * math.sin(tt))], 2.4)
put(lay)

# ── ⑦ 다리 위 앞 병정의 한 줄 단추 곁에 꽂힌 작은 깃발(항체 = anti-CD4) — 등불에 빛난다
lay = layer(); d = ImageDraw.Draw(lay)
gx, gy = 1388, 650
glow = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
for rr, al, cc in ((32, 60, (255, 230, 90)), (22, 110, (255, 238, 120)), (12, 190, (255, 252, 220))): gd.ellipse([(gx + 8 - rr) * S, (gy - 6 - rr) * S, (gx + 8 + rr) * S, (gy - 6 + rr) * S], fill=cc + (al,))
put(glow, blur=3)
lay = layer(); d = ImageDraw.Draw(lay)
line(d, [(gx, gy + 9), (gx, gy - 15)], 2.0)
poly(d, [(gx + 1, gy - 15), (gx + 19, gy - 10), (gx + 1, gy - 4)], (214, 166, 52, 255), 1.8)
for a in (-60, -30, 0, 30):
    t = math.radians(a); line(d, [(gx + 10 + 21 * math.cos(t), gy - 9 + 21 * math.sin(t)), (gx + 10 + 28 * math.cos(t), gy - 9 + 28 * math.sin(t))], 1.8, (250, 196, 40, 255))
put(lay)

im.save(dst)
print('ok', dst)

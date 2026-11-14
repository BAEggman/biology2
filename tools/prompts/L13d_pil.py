#!/usr/bin/env python3
# L13d_pil.py <base.png> <out.png> — L13d 「처형장과 옮겨 심은 집」의 PIL 마무리(2026-11-14).
#  바탕 = Gemini 가 통째로 그린 장면 S1(1024 → 2048 확대) + 구역 편집 Z1 ~ Z11(L13d_build.sh).
#  여기서는 「개수 · 자리 · 빛깔이 곧 뜻」인 것만 얹는다: 조끼 단추(넷씩 두 줄 = CD8 · 한 줄 넷 = CD4) · 붉은 리본 배지(자기 = MHC I — 성 안의 모두)
#  · 파란 리본 배지(옮겨 심은 집 사람 = 공여자의 MHC — 꼴은 같고 빛깔만 다름) · Gemini 가 몰래 찍은 조끼의 작은 검은 점 지우기 · 외눈 안경 병정의 볼.
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s13_lib import S, INK, line, disc, poly, badge, RED, RED_D, GOLD_C

W, H = 2048, 1144
src, dst = sys.argv[1:3]
im = Image.open(src).convert('RGB')
assert im.size == (W, H), im.size

def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay):
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    b = im.convert('RGBA'); b.alpha_composite(small); im = b.convert('RGB')

# ── ⓪ Gemini 가 「단추 없음」을 어기고 조끼에 찍은 작은 검은 점 — 지우고 나서 금빛 단추를 센다(점이 남으면 단추 수가 흐려진다)
a = np.array(im)[:, :, ::-1].copy(); m = np.zeros(a.shape[:2], np.uint8)
for x, y in ((1248, 820), (1250, 836), (1250, 852),            # 그라인더 병정
             (1020, 546), (1022, 557), (1024, 569)):           # 학교 문을 나서는 병정
    cv2.circle(m, (x, y), 5, 255, -1)
a = cv2.inpaint(a, m, 5, cv2.INPAINT_TELEA)
im = Image.fromarray(a[:, :, ::-1])

# ── ① 외눈 안경 병정의 볼(다른 장난감 병정과 같은 얼굴로 — Z11 에서 볼이 빠졌다)
lay = layer(); d = ImageDraw.Draw(lay)
d.ellipse([(1781) * S, (367.5) * S, (1791) * S, (374.5) * S], fill=(236, 128, 128, 120))
put(lay)

# ── ①-2 그라인더 입에서 배 구멍으로 쏟아지는 검은 알갱이(그랜자임 — 일치 검사 1 · 2회: 떨어지는 모습이 약하다) + 그라인더 머리를 비트는 호
import math
lay = layer(); d = ImageDraw.Draw(lay)
for x, y, r in ((1366, 813, 3.0), (1373, 816, 2.7), (1370, 822, 2.8), (1378, 821, 3.0), (1381, 828, 2.6),
                (1376, 830, 2.4), (1386, 826, 2.5), (1389, 833, 2.3), (1384, 836, 2.2)):
    disc(d, x, y, r, (28, 24, 22, 255), 0)
for x, y in ((1373, 816), (1381, 828), (1376, 830)):                 # 알갱이 뒤의 짧은 자국(그라인더 입 쪽으로)
    line(d, [(x - 3.5, y - 3.0), (x - 8.5, y - 7.2)], 1.3, (28, 24, 22, 200))
for cx, cy, a0, a1 in ((1282, 706, 150, 230), (1282, 706, -40, 40)):  # 그라인더 머리를 비트는 짧은 호 둘(돌린다)
    pts = [(cx + 27 * math.cos(math.radians(a)), cy + 14 * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 8)]
    line(d, pts, 2.2)
put(lay)

# ── ①-3 오려진 파란 동그라미를 공이 아니라 얇은 종이 원판으로(일치 검사 2회: 공으로도 읽힌다) — 둥근 공을 지우고 기울어진 납작한 원판
a = np.array(im)[:, :, ::-1].copy(); m = np.zeros(a.shape[:2], np.uint8)
cv2.circle(m, (941, 1045), 27, 255, -1)
a = cv2.inpaint(a, m, 7, cv2.INPAINT_TELEA)
im = Image.fromarray(a[:, :, ::-1])
lay = layer(); d = ImageDraw.Draw(lay)
def rell(cx, cy, rx, ry, ang, n=48):
    t = math.radians(ang)
    return [(cx + rx * math.cos(2 * math.pi * k / n) * math.cos(t) - ry * math.sin(2 * math.pi * k / n) * math.sin(t),
             cy + rx * math.cos(2 * math.pi * k / n) * math.sin(t) + ry * math.sin(2 * math.pi * k / n) * math.cos(t)) for k in range(n)]
poly(d, rell(941, 1050, 22, 8.5, -18), (44, 92, 170, 255), 2.6)            # 원판의 옆면(두께)
poly(d, rell(941, 1046, 22, 8.5, -18), (74, 132, 210, 255), 2.6)           # 원판의 윗면
put(lay)

# ── ①-4 뼈 속 골수에서 벌이 날아오른 자취(점선 — 일치 검사 2회: 뼈에서 나왔다가 간접적)
lay = layer(); d = ImageDraw.Draw(lay)
def bez3(p0, c0, c1, p1, t):
    u = 1 - t
    return tuple(u ** 3 * p0[i] + 3 * u * u * t * c0[i] + 3 * u * t * t * c1[i] + t ** 3 * p1[i] for i in (0, 1))
P = ((318, 622), (250, 600), (120, 600), (134, 505))
n = 40
for k in range(1, n - 1, 2): line(d, [bez3(*P, k / n), bez3(*P, (k + 1) / n)], 2.4, (70, 66, 72, 210))
put(lay)

# ── ①-5 외눈 안경에서 파란 배지로 가는 눈길(점선 — 일치 검사 2회: 배지까지 보는지 애매)
lay = layer(); d = ImageDraw.Draw(lay)
x0, y0, x1, y1 = 1779, 372, 1671, 387
n = 16
for k in range(0, n, 2):
    t0, t1 = k / n, (k + 1) / n
    line(d, [(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], 2.0, (40, 40, 48, 215))
put(lay)

# ── ② 조끼 단추: 넷씩 두 줄 = CD8(세포독성 T) · 한 줄 넷 = CD4(도움 T)
GOLD = (242, 190, 52, 255)
def col(d, x0, y0, x1, y1, r, n=4):
    for k in range(n): disc(d, x0 + (x1 - x0) * k / (n - 1), y0 + (y1 - y0) * k / (n - 1), r, GOLD, max(1.2, r * 0.32))
lay = layer(); d = ImageDraw.Draw(lay)
col(d, 850, 932, 850, 963, 3.9); col(d, 870, 932, 870, 963, 3.9)         # 펀치 병정(CD8)
col(d, 1237, 834, 1237, 865, 4.1); col(d, 1254, 834, 1254, 865, 4.1)     # 그라인더 병정(CD8)
col(d, 1801, 392, 1801, 421, 3.5); col(d, 1814, 392, 1814, 421, 3.5)     # 외눈 안경 병정(CD8)
col(d, 1641, 846, 1641, 888, 4.6)                                        # 인쇄기 곁 대장(CD4)
col(d, 1027, 543, 1027, 574, 3.7)                                        # 학교 문을 나서는 병정(CD4 — 두 갈래 모두 이 학교를 거친다)
put(lay)

# ── ③ 리본 배지 — 붉은 = 자기(MHC I · 성 안의 모두) · 파랑 = 옮겨 심은 집 사람(공여자 MHC — 받는 성에겐 비자기)
BLUE, BLUE_D = (52, 112, 222, 255), (32, 78, 170, 255)
def badge_c(d, cx, cy, r, c1, c2):
    """작은 배지(r < 7): 꼬리를 테두리 없는 세모 둘로 — 꼬리 테두리선이 작게 줄면 「RR」 글자로 읽혔다(L13c 일치 검사 1 · 2회)."""
    for sx in (-1, 1):
        d.polygon([((cx + sx * 0.15 * r) * S, (cy + 0.5 * r) * S), ((cx + sx * 0.95 * r) * S, (cy + 0.55 * r) * S), ((cx + sx * 0.7 * r) * S, (cy + 1.75 * r) * S)], fill=c2)
    disc(d, cx, cy, r, c1, max(1.2, r * 0.2))
    d.ellipse([(cx - 0.4 * r) * S, (cy - 0.4 * r) * S, (cx + 0.4 * r) * S, (cy + 0.4 * r) * S], fill=GOLD_C)
def badge_big(d, cx, cy, r, c1, c2):
    import s13_lib
    o1, o2 = s13_lib.RED, s13_lib.RED_D
    s13_lib.RED, s13_lib.RED_D = c1, c2
    try: s13_lib.badge(d, cx, cy, r)
    finally: s13_lib.RED, s13_lib.RED_D = o1, o2
def put_badge(d, cx, cy, r, c1=RED, c2=RED_D):
    (badge_big if r >= 7 else badge_c)(d, cx, cy, r, c1, c2)
lay = layer(); d = ImageDraw.Draw(lay)
for cx, cy, r in ((150, 176, 7.5), (343, 137, 7.5), (226, 497, 7),                 # 벌 셋(성벽 위 둘 · 뼈에서 날아오르는 하나)
                  (594, 570, 6.5), (686, 566, 6.5), (778, 562, 6.5),               # 학교로 가는 맨나무 인형 셋
                  (1112, 518, 6.5), (1232, 506, 6.5), (1488, 512, 6.5),            # 학교를 나와 비틀대는 둘 · 흙더미 곁의 하나
                  (1003, 557, 6.5), (828, 948, 7.5), (1208, 849, 8),                # 학교 문의 병정 · 펀치 병정 · 그라인더 병정(조끼 위 — 단추 줄과 떼어)
                  (1610, 894, 6.5), (1790, 340, 7.5),                               # 대장(조끼 아래쪽) · 외눈 안경 병정(털모자 앞 — 조끼가 작아 단추 곁을 피함)
                  (982, 880, 9), (1405, 770, 8.5)):                                # 망토 숨긴 주민 · 게 붙은 주민
    put_badge(d, cx, cy, r)
for cx, cy, r in ((1657, 388, 7.5), (1850, 371, 5.5)):                            # 옮겨 심은 집 — 여자 · 창가의 아이
    put_badge(d, cx, cy, r, BLUE, BLUE_D)
put(lay)

im.save(dst)
print('saved', dst)

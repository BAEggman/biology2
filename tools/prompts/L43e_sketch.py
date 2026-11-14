#!/usr/bin/env python3
# L43e_sketch.py — L43e 「상자 차례대로 짓는 초파리」 바탕용 배치 밑그림
# 2048x1144 로 그려 1024x572 로 줄인다(Gemini 에 올리는 것은 sketch.png).
# 이 그림의 초파리는 모두 「상자 파리」다 — 뚜껑 달린 상자 셋(머리 = 주황 · 가슴 = 파랑 · 배 = 분홍)을 이어 지었다.
# Gemini 가 그릴 것만 그린다: 담 띠 · 큰 상자 파리 · 루페 든 흰 가운과 머리가 파랑인 돌연변이 파리 · 등뼈만 남은 물고기와 눈알 여섯 개들이 팩과 받는 파리
#   · 코를 붙이는 어미 파리와 알 둘 · 부모 파리 둘과 알 넷(넷째는 깨진 알 속의 죽은 배아).
# ⚠ 끈 · 끈에 꿴 작은 상자 셋 · 화살 · 부모와 알 발치의 작은 상자 짝은 여기 그리지 않는다 — PIL(L43e_pil.py).
import math, sys
from PIL import Image, ImageDraw
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 2048, 1144; S = 2
GROUND, BRICK, MORTAR = (240, 233, 205), (186, 84, 62), (120, 50, 40)
SKIN = (250, 205, 170)
ORA, BLU, PNK = (244, 150, 50), (74, 134, 222), (240, 138, 176)
EYE = (170, 30, 44)
EGG = (246, 236, 208)
im = Image.new('RGB', (W * S, H * S), GROUND); d = ImageDraw.Draw(im)
def sc(pts): return [(x * S, y * S) for x, y in pts]
def R(x0, y0, x1, y1, fill, outline=(0, 0, 0), w=4): d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill, outline=outline, width=w * S if outline else 0)
def C(x, y, r, fill, outline=(0, 0, 0), w=4): d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=fill, outline=outline, width=w * S if outline else 0)
def E(x, y, rx, ry, fill, outline=(0, 0, 0), w=4): d.ellipse([(x - rx) * S, (y - ry) * S, (x + rx) * S, (y + ry) * S], fill=fill, outline=outline, width=w * S if outline else 0)
def L(pts, fill=(0, 0, 0), w=6): d.line(sc(pts), fill=fill, width=w * S, joint='curve')
def P(pts, fill, outline=(0, 0, 0), w=4):
    d.polygon(sc(pts), fill=fill)
    if outline: d.line(sc(pts + [pts[0]]), fill=outline, width=w * S)
def wall(y0, y1, x1=1410):
    R(0, y0, x1, y1, BRICK, None)
    n = (y1 - y0) // 30
    for r in range(n):
        y = y0 + r * 30; L([(0, y + 30), (x1, y + 30)], MORTAR, 3)
        for x in range(-60 + (r % 2) * 60, x1, 120): L([(x, y), (x, y + 30)], MORTAR, 3)
    L([(0, y1), (x1, y1)], (0, 0, 0), 6); L([(x1, y0), (x1, y1)], (0, 0, 0), 6)
def boxfly(x0, y0, bw, bh, cols=(ORA, BLU, PNK), face=-1, head_legs=False, lw=None):
    """상자 파리 — face=-1 이면 머리가 왼쪽. (x0, y0) = 왼쪽 위. cols = 머리 · 가슴 · 배 상자의 빛깔."""
    lw = lw or max(3, bw // 40)
    xs = [x0 + k * bw for k in range(3)]
    order = cols if face < 0 else cols[::-1]
    hx = xs[0] if face < 0 else xs[2]; tx = xs[1]
    # 날개(가슴 상자 위에서 뒤로)
    for dyw in (0, bh * 0.22):
        P([(tx + bw * 0.5, y0), (tx + bw * 0.5 - face * bw * 0.9, y0 - bh * 0.62 + dyw), (tx + bw * 0.5 - face * bw * 1.25, y0 - bh * 0.36 + dyw), (tx + bw * 0.5 - face * bw * 0.5, y0 + 4)], (226, 240, 250), (0, 0, 0), lw)
    # 다리 셋(가슴 상자 밑)
    for k, (dx, fx) in enumerate(((0.18, -0.55), (0.5, 0.05), (0.82, 0.62))):
        bx = tx + bw * dx; L([(bx, y0 + bh), (bx + bw * fx * 0.5 * (1 if face < 0 else -1), y0 + bh * 1.38), (bx + bw * fx * (1 if face < 0 else -1), y0 + bh * 1.78)], w=lw + 2)
    for k, c in enumerate(order):
        R(xs[k], y0, xs[k] + bw, y0 + bh, c, (0, 0, 0), lw); R(xs[k] - bw * 0.03, y0 - bh * 0.02, xs[k] + bw * 1.03, y0 + bh * 0.16, c, (0, 0, 0), lw)   # 상자 + 뚜껑
    ex = hx + bw * (0.34 if face < 0 else 0.66)
    C(ex, y0 + bh * 0.52, bh * 0.24, EYE, (0, 0, 0), lw); C(ex - bh * 0.07, y0 + bh * 0.45, bh * 0.06, (255, 255, 255), None)
    fx0 = hx if face < 0 else hx + bw
    if head_legs:                                                                    # 더듬이 자리에 다리 둘 + 머리 위 날개 한 쌍 더
        for k in (0, 1):
            L([(fx0 + face * -bw * 0.12 * (k + 0.4), y0), (fx0 + face * bw * (0.25 + 0.1 * k), y0 - bh * (0.45 + 0.3 * k)), (fx0 + face * bw * (0.55 + 0.1 * k), y0 - bh * (0.25 + 0.5 * k))], w=lw + 2)
        P([(hx + bw * 0.6, y0), (hx + bw * 0.6 - face * bw * 0.55, y0 - bh * 0.62), (hx + bw * 0.6 - face * bw * 0.8, y0 - bh * 0.3)], (226, 240, 250), (0, 0, 0), lw)
    else:                                                                            # 더듬이 둘
        for k in (0, 1):
            L([(fx0 - face * bw * (0.10 + 0.14 * k), y0), (fx0 + face * bw * (0.05 - 0.10 * k), y0 - bh * 0.36)], w=lw + 1); C(fx0 + face * bw * (0.05 - 0.10 * k), y0 - bh * 0.36, lw + 2, (40, 30, 30), None)
def egg(cx, cy, rx, ry, nose=0):
    E(cx, cy, rx, ry, EGG)
    for k in range(7): C(cx + rx * 0.6 * math.cos(k * 2.3), cy + ry * 0.6 * math.sin(k * 1.7), 3, (150, 110, 70), None)
    if nose: P([(cx + nose * rx * 0.86, cy - 16), (cx + nose * (rx + 34), cy + 10), (cx + nose * rx * 0.86, cy + 20)], (244, 170, 150))

wall(0, 90)
# ── 큰 상자 파리(위 왼쪽) — 그 밑 y 600 ~ 740 은 비워 둔다(끈과 작은 상자 셋이 들어온다)
boxfly(190, 240, 280, 180, lw=6)
# ── 아래 왼쪽: 루페 든 흰 가운 + 머리 상자가 파랑인 돌연변이 파리(더듬이 자리에 다리)
R(96, 870, 196, 1050, (250, 250, 250)); L([(118, 1050), (116, 1112)], w=10); L([(174, 1050), (176, 1112)], w=10)
C(150, 836, 36, SKIN); L([(190, 900), (262, 936)], (250, 250, 250), 18); L([(262, 936), (286, 912)], (120, 80, 40), 8); C(306, 890, 34, (210, 232, 246), (150, 110, 50), 7)
boxfly(366, 946, 104, 76, cols=(BLU, BLU, PNK), head_legs=True)
# ── 아래 가운데: 등뼈만 남은 물고기(꼬리로 섬) + 눈알 여섯 개들이 팩 + 받는 파리(다리에 붉은 겹눈 하나 더)
P([(770, 800), (850, 800), (836, 868), (784, 868)], (236, 236, 228)); C(796, 828, 10, (30, 30, 30), None)
L([(810, 868), (810, 1050)], (236, 236, 228), 12)
for k in range(5): L([(778, 896 + k * 30), (842, 896 + k * 30)], (236, 236, 228), 7)
P([(810, 1046), (770, 1106), (850, 1106)], (236, 236, 228))
L([(826, 930), (888, 950)], (236, 236, 228), 9)
R(884, 940, 1010, 1010, (196, 150, 96)); L([(916, 940), (916, 906), (978, 906), (978, 940)], (120, 80, 40), 7)
for k in range(3):
    C(908 + k * 39, 936, 17, (252, 252, 252), (0, 0, 0), 3); C(908 + k * 39, 936, 7, (70, 130, 220), None)
    C(914 + k * 39, 962, 17, (252, 252, 252), (0, 0, 0), 3); C(914 + k * 39, 962, 7, (70, 130, 220), None)
boxfly(1090, 940, 92, 70)
C(1062, 1042, 13, EYE, (0, 0, 0), 3)
# ── 오른쪽 위: 어미 파리(머릿수건)가 알의 앞(왼쪽) 끝에 코를 붙인다 + 코 붙은 알 하나
boxfly(1664, 196, 122, 92)
P([(1652, 190), (1796, 190), (1724, 130)], (230, 90, 110)); L([(1660, 196), (1640, 300)], (230, 90, 110), 8)
egg(1548, 306, 78, 54, nose=-1); L([(1664, 280), (1612, 290)], w=6); L([(1664, 320), (1470, 322)], w=5)
egg(1560, 452, 70, 48, nose=-1)
# ── 오른쪽 아래: 건강한 부모 둘(마주 봄) + 알 넷(넷째 = 깨진 알 속의 죽은 배아) — 부모 발치 · 알 발치는 비워 둔다(작은 상자 짝이 들어온다)
boxfly(1474, 640, 74, 56, face=1); boxfly(1786, 640, 74, 56)
for cx in (1520, 1650, 1780): egg(cx, 962, 44, 58)
P([(1872, 1016), (1866, 950), (1890, 968), (1908, 940), (1930, 966), (1954, 942), (1976, 968), (1996, 950), (1990, 1016)], EGG)
E(1931, 1004, 62, 28, EGG)
for k, c in enumerate((PNK, (60, 92, 160), ORA)): P([(1888 + k * 30, 960 - k * 6), (1916 + k * 30, 952 + k * 8), (1912 + k * 30, 986 + k * 4), (1886 + k * 30, 984 - k * 4)], c, (0, 0, 0), 3)
L([(1950, 950), (1962, 962)], w=3); L([(1962, 950), (1950, 962)], w=3)

im = im.resize((W, H), Image.LANCZOS); im.save(f'{OUT}/sketch_full.png'); im.resize((1024, 572), Image.LANCZOS).save(f'{OUT}/sketch.png')
print('ok', f'{OUT}/sketch.png')

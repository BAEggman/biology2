#!/usr/bin/env python3
# sketch.py — L53a 바탕용 배치 밑그림(2048x1144 → 1024x572). Gemini 가 이 배치를 따라 다시 그리게 한다.
import math, random
from PIL import Image, ImageDraw
W, H = 2048, 1144; S = 2
im = Image.new('RGB', (W * S, H * S), (120, 190, 235)); d = ImageDraw.Draw(im)
def R(x0, y0, x1, y1, fill, outline=(0, 0, 0), w=4): d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill, outline=outline, width=w * S if outline else 0)
def C(x, y, r, fill, outline=(0, 0, 0), w=4): d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=fill, outline=outline, width=w * S if outline else 0)
def L(pts, fill=(0, 0, 0), w=6): d.line([(x * S, y * S) for x, y in pts], fill=fill, width=w * S, joint='curve')
def P(pts, fill, outline=(0, 0, 0), w=4):
    d.polygon([(x * S, y * S) for x, y in pts], fill=fill)
    if outline: d.line([(x * S, y * S) for x, y in pts + [pts[0]]], fill=outline, width=w * S)
TOP, BOT = 440, 700            # 버터 띠
# 물: 위(밝음) · 아래(짙음)
R(0, 0, W, 70, (200, 232, 250), None); R(0, 70, W, TOP, (120, 190, 235), None); R(0, BOT, W, H, (40, 110, 190), None)
L([(0, 70), (W, 70)], (30, 80, 140), 5)
# 햇살(오른쪽 위)
for k in range(7): P([(2048, 0), (1500 + k * 80, 430), (1540 + k * 80, 430)], (175, 220, 245), None)
# 버터 띠: 왼쪽 언 곳(옅은 하늘빛) → 노랑 → 오른쪽 끝 녹아 흐름
R(0, TOP, W, BOT, (250, 214, 80), None)
for x in range(0, 520):
    t = max(0, min(1, (x - 380) / 140)); c = tuple(int(a * (1 - t) + b * t) for a, b in zip((205, 228, 248), (250, 214, 80)))
    d.line([(x * S, TOP * S), (x * S, BOT * S)], fill=c)
L([(0, TOP), (1960, TOP)], w=6); L([(0, BOT), (1930, BOT)], w=6)
# 오른쪽 끝 녹은 버터
P([(1930, TOP), (2048, TOP + 30), (2048, BOT + 60), (2010, BOT + 150), (1985, BOT + 40), (1960, BOT + 110), (1940, BOT)], (250, 214, 80))
for x, l in [(1975, 190), (2030, 230)]: C(x, BOT + l, 12, (250, 214, 80))
# 고드름(왼쪽 아래)
for x in range(20, 440, 60): P([(x, BOT), (x + 34, BOT), (x + 17, BOT + 90 + (x % 3) * 20)], (222, 238, 250))
# 얼음덩이 · 눈송이
for x, y, s in [(40, 110, 90), (190, 150, 70), (330, 100, 80), (60, 880, 100), (260, 960, 80)]: R(x, y, x + s, y + s, (222, 238, 250))
for x, y in [(160, 300), (300, 250), (120, 820), (400, 900), (30, 600), (430, 200)]:
    for a in range(0, 180, 60): L([(x - 22 * math.cos(math.radians(a)), y - 22 * math.sin(math.radians(a))), (x + 22 * math.cos(math.radians(a)), y + 22 * math.sin(math.radians(a)))], (255, 255, 255), 4)
RED, BLUE = (225, 45, 40), (40, 80, 200)
def buoy(x, top=True, kind='straight', col=None, leg=118, r=40, lean=0):
    col = col or (RED if top else BLUE)
    y0 = TOP if top else BOT; sgn = 1 if top else -1; hy = y0 - sgn * (r - 2)
    for dx in (-13, 13):
        if kind == 'straight': L([(x + dx, y0), (x + dx + lean, y0 + sgn * leg)], (60, 20, 20), 7)
        else: L([(x + dx, y0), (x + dx + 26, y0 + sgn * leg * 0.5), (x + dx - 4, y0 + sgn * leg)], (60, 20, 20), 7)
    C(x, hy, r, col); R(x - r + 5, hy - 8, x + r - 5, hy + 8, (255, 255, 255), (0, 0, 0), 2)
def animal(x, kind):
    y0 = TOP; hy = y0 - 42
    leg = 150 if kind == 'cow' else 118
    for dx in (-13, 13): L([(x + dx, y0), (x + dx, y0 + leg)], (60, 20, 20), 7)
    if kind == 'cow':
        C(x, hy, 44, (255, 255, 255)); C(x - 16, hy - 14, 14, (40, 40, 40), None); C(x, hy + 22, 22, (245, 190, 190))
        P([(x - 40, hy - 30), (x - 62, hy - 58), (x - 26, hy - 40)], (240, 230, 200)); P([(x + 40, hy - 30), (x + 62, hy - 58), (x + 26, hy - 40)], (240, 230, 200))
    else:
        C(x, hy, 42, (250, 170, 185)); C(x, hy + 10, 18, (240, 130, 150)); P([(x - 36, hy - 24), (x - 44, hy - 54), (x - 14, hy - 38)], (250, 170, 185)); P([(x + 36, hy - 24), (x + 44, hy - 54), (x + 14, hy - 38)], (250, 170, 185))
# A. 언 왼쪽: 곧은 다리 · 빽빽
R(20, 322, 140, 440, (222, 238, 250)); C(80, 372, 16, (250, 200, 160)); R(66, 388, 94, 432, (70, 110, 200))      # 얼음 속 일꾼
for x in (200, 262): buoy(x)
animal(326, 'cow'); animal(392, 'pig'); buoy(456)
for x in (60, 122, 184, 246, 308, 370, 432): buoy(x, top=False)
# B. 꺾인 다리 · 띄엄띄엄 · 옆으로 미끄러짐
for x in (560, 660, 760): buoy(x, kind='bent')
buoy(845, kind='bent', leg=70, r=30)
for x in (540, 640, 740, 840): buoy(x, top=False, kind='bent')
for x, y in [(515, 400), (715, 400), (595, 745), (795, 745)]: L([(x - 26, y), (x - 6, y)], w=4); L([(x - 26, y + 14), (x - 6, y + 14)], w=4)
# 금빛 덩이(콜레스테롤 자리): 다리 사이
for x, y in [(610, 500), (700, 640), (294, 500)]: R(x - 20, y - 34, x + 20, y + 34, (240, 180, 30))
# C. 오리발 잠수부가 부표 사람을 뒤집어 아랫줄로
DX = -85
R(985 + DX, 470, 1045 + DX, 640, (50, 60, 80)); C(1015 + DX, 455, 26, (250, 200, 160)); R(1000 + DX, 446, 1030 + DX, 462, (150, 220, 240), (0, 0, 0), 2)
P([(985 + DX, 640), (940 + DX, 760), (1000 + DX, 770), (1010 + DX, 640)], (245, 130, 30)); P([(1022 + DX, 640), (1040 + DX, 770), (1100 + DX, 755), (1045 + DX, 640)], (245, 130, 30))
L([(1045 + DX, 520), (1075 + DX, 560)], (50, 60, 80), 10)
C(1100 + DX, 590, 32, BLUE); R(1074 + DX, 583, 1126 + DX, 597, (255, 255, 255), (0, 0, 0), 2); L([(1112 + DX, 562), (1150 + DX, 500)], (60, 20, 20), 7); L([(1126 + DX, 572), (1172 + DX, 520)], (60, 20, 20), 7)
# D. 구슬 기둥 여섯
cols = [(230, 60, 60), (60, 160, 230), (250, 200, 50), (90, 190, 90), (170, 90, 200), (245, 140, 40)]
def pillar(x, y0, y1, r=17, skip=None):
    y = y0; i = 0
    while y <= y1:
        if not (skip and skip[0] <= y <= skip[1]): C(x, y, r, cols[i % 6], (0, 0, 0), 3)
        y += 2 * r - 2; i += 1
X1, X2, X3, X4, X5, X6 = 1110, 1255, 1400, 1545, 1690, 1835
# P1 나선 + 알
pillar(X1, 290, 1000, skip=(TOP, BOT))
for i in range(22):
    a = i * 0.9; C(X1 + 40 * math.cos(a), TOP + 14 + i * 11.3, 14, cols[i % 6], (0, 0, 0), 3)
d.ellipse([(X1 - 30) * S, 190 * S, (X1 + 30) * S, 272 * S], fill=(255, 255, 255), outline=(0, 0, 0), width=4 * S)
# P2 굴(가운데가 뚫린 기둥)
pillar(X2 - 30, 300, 880); pillar(X2 + 30, 300, 880); R(X2 - 13, 300, X2 + 13, 880, (150, 205, 240), None)
for y in (240, 380, 560, 760, 930): C(X2, y, 9, (240, 240, 240), (0, 0, 0), 2)
# P3 작업대
pillar(X3, 300, 900); R(X3 - 50, 915, X3 + 70, 935, (150, 100, 50)); L([(X3 - 40, 935), (X3 - 40, 1000)], (150, 100, 50), 8); L([(X3 + 60, 935), (X3 + 60, 1000)], (150, 100, 50), 8)
C(X3 + 90, 880, 16, (250, 200, 160)); R(X3 + 76, 896, X3 + 104, 940, (70, 110, 200)); R(X3 - 20, 895, X3 + 10, 913, (230, 60, 60), (0, 0, 0), 2); R(X3 + 12, 895, X3 + 42, 913, (60, 160, 230), (0, 0, 0), 2)
# P4 우편함 + 등
pillar(X4, 330, 860); R(X4 - 40, 250, X4 + 40, 312, (200, 40, 40)); P([(X4 + 45, 190), (X4 + 100, 190), (X4 + 100, 226), (X4 + 45, 226)], (255, 255, 255)); L([(X4 + 45, 190), (X4 + 72, 210), (X4 + 100, 190)], w=3)
C(X4, 905, 30, (255, 235, 90))
for a in range(0, 360, 45): L([(X4 + 40 * math.cos(math.radians(a)), 905 + 40 * math.sin(math.radians(a))), (X4 + 58 * math.cos(math.radians(a)), 905 + 58 * math.sin(math.radians(a)))], (255, 235, 90), 4)
# P5 막대사탕 다발
pillar(X5, 330, 880)
for dx, dy in [(-34, -70), (0, -90), (34, -70)]: L([(X5, 315), (X5 + dx, 315 + dy)], (255, 255, 255), 5); C(X5 + dx, 315 + dy, 20, (250, 130, 190))
# P6 밧줄 그물(위) + 살구색 구슬 줄(아래)
pillar(X6, 330, 860)
for i in range(12): C(X6 - i * 22, 890 + i * 21, 13, (250, 185, 140), (0, 0, 0), 2)
for i in range(5):
    L([(X6 - 10 + i * 40, 160), (X6 + i * 22, 330)], (190, 150, 90), 6); L([(X6 - 30, 180 + i * 34), (2040, 170 + i * 34)], (190, 150, 90), 6)
# 이웃 부교(오른쪽 위) + 매달린 빨간 머리
R(1400, 78, 2048, 150, (250, 214, 80))
for x in (1460, 1560):
    for dx in (-12, 12): L([(x + dx, 150), (x + dx, 200)], (60, 20, 20), 6)
    C(x, 232, 34, RED); R(x - 28, 226, x + 28, 238, (255, 255, 255), (0, 0, 0), 2)
# 기둥 사이 부표 사람(윗줄 · 아랫줄) + 머리의 막대사탕 + 실에 매인 작은 구슬 공
for x in (1182, 1327, 1472, 1617, 1762): buoy(x, kind='bent', r=34)
L([(1472, 370), (1500, 322)], (255, 255, 255), 5); C(1500, 316, 16, (250, 130, 190))
for x in (1182, 1327, 1472, 1617, 1762): buoy(x, top=False, kind='bent', r=34)
L([(1327, 780), (1327, 870)], (0, 0, 0), 3)
for dx, dy in [(-14, 0), (14, 0), (0, -16), (0, 16), (-12, 14), (12, -12)]: C(1327 + dx, 895 + dy, 13, cols[(dx + dy) % 6], (0, 0, 0), 2)
# E. 녹는 오른쪽 끝: 기우뚱한 작은 기둥 · 떠내려가는 부표 사람
for i in range(7): C(1955 + i * 9, 360 + i * 30, 15, cols[i % 6], (0, 0, 0), 3)
im = im.resize((W, H), Image.LANCZOS); im.save('/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad/L53a/r2/sketch_2048.png')
im.resize((1024, 572), Image.LANCZOS).save('/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad/L53a/r2/sketch.png')
print('ok')

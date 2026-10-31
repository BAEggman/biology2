#!/usr/bin/env python3
"""touch_e.py — s45u02 v4(b133 뒤): cur13(G1 · G2 · G3 조각을 붙인 뒤) → cur14
 ① 행 9  — 맞잡은 손에서 사발 오른 테를 비켜 쿠션으로 떨어진 공의 길(점선 호) — 공 · 빛무리 · 불티 · 열 아지랑이 · 그을음은 G1 조각
 ② 행 4  — 바닥 깔개 위 낱장 쿠션(G2 조각) 앞면에 작은 자주빛 머리 셋 — 곁의 일곱 장 무더기(겹마다 셋 남짓)와 견준다
 ③ 행 17 — 빨강 끝 너머 흐릿한 둘(G3 조각 — 앞모습)의 가슴에 글자 꼴 금빛 브로치 「d」 · 「f」(a = 세 갈래 잔가지 · b = 포크처럼 가슴의 꼴이 이름)
 ④ 이은 흔적 — 빨강 띠 헤엄이 무더기의 x≈1930 세로 칼자국(paste_d2 의 구역 경계) 위에 온전한 헤엄이를 얹어 덮고 반쪽 방울을 온전히
 ⑤ 행 22 — 청록 · 주황 띠 한가운데 헤엄이 셋 → 다섯 · 방울 둘 → 셋(머리는 비었는데 일은 했다)
 ⑥ 행 14 — 꼬리 넷이 쿠션 겉천 속으로 파고든 자리에 오목한 주름(구멍 없음 — 겉천이 꼬리를 덮는다)
 ⑦ 이은 흔적 — 흰 빔 오른쪽 하늘의 빛무리를 왼쪽과 같은 폭으로(A 「흰 빔 양옆 하늘빛이 갈림」)"""
import sys, os, math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
img = Image.open('cur13.png').convert('RGB'); W, H = img.size
P10 = np.asarray(Image.open('cur10.png').convert('RGB'))
SS = 4
S = lambda x, y: (x * SS, y * SS)
INK = (40, 32, 24, 255)
def layer(): return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
def comp(img, lay, blur=0):
    small = lay.resize((W, H), Image.LANCZOS)
    if blur: small = small.filter(ImageFilter.GaussianBlur(blur))
    im2 = img.convert('RGBA'); im2.alpha_composite(small); return im2.convert('RGB')

# ── ① 행 9: 공의 길(점선 호) — G1 이 남긴 짧은 점 토막은 걷어 내고(cur10 으로) 손 → 테 바깥 → 공 왼 위까지 한 줄로
A = np.asarray(img).copy()
A[600:619, 1275:1287] = P10[600:619, 1275:1287]
img = Image.fromarray(A)
P0, C, P1 = (1238.0, 543.0), (1266.0, 512.0), (1272.0, 634.0)      # 맞잡은 손 → 사발 오른 테 바로 바깥(1260, 550) → 공 왼 위
def bez(t):
    return ((1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * C[0] + t ** 2 * P1[0], (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * C[1] + t ** 2 * P1[1])
pts = [bez(t) for t in np.linspace(0, 1, 2000)]
acc, last, dots = 0.0, pts[0], []
for p in pts[1:]:
    acc += math.hypot(p[0] - last[0], p[1] - last[1]); last = p
    if acc >= 3.1: dots.append(p); acc = 0.0
lay = layer(); d = ImageDraw.Draw(lay)
for (x, y) in dots:
    if math.hypot(x - P0[0], y - P0[1]) < 7.5: continue              # 손 · 사발 속 공과 겹치지 않게
    d.ellipse([S(x - 0.95, y - 0.95), S(x + 0.95, y + 0.95)], fill=(52, 44, 36, 240))
img = comp(img, lay)

# ── ② 행 4: 낱장 쿠션 앞면의 작은 자주빛 머리 셋(touch_d ① 과 같은 꼴 · 같은 크기)
LONE = (697.0, 765.0, 695.4)    # (왼 x, 오른 x, 앞면 가운데 y) — G2 낱장 쿠션의 앞 띠(윤곽 676 · 윗면 678–692 · 앞 띠 693–698)
# 곁의 무더기(오른 아래)는 touch_d ① 이 겹 셋에만 머리를 박았다 — 견주려면 일곱 겹 모두에(겹마다 둘 · 아래로 갈수록 오른쪽으로 비낌)
STACK_FILL = [(752.5, 608.6), (774.0, 608.4), (759.5, 650.2), (782.0, 650.6), (756.0, 660.8), (779.5, 661.2), (761.5, 669.0), (783.5, 669.4)]
PUR, PURD = (156, 108, 196, 255), (70, 44, 96, 255)
lay = layer(); d = ImageDraw.Draw(lay); s = 4.4
for (x, yc) in STACK_FILL:
    d.rectangle([S(x - s / 2, yc - s / 2), S(x + s / 2, yc + s / 2)], fill=PUR, outline=PURD, width=int(SS * 0.8))
    d.rectangle([S(x - s * 0.18, yc - s * 0.18), S(x + s * 0.18, yc + s * 0.18)], fill=(250, 250, 248, 255))
img = comp(img, lay)
if LONE:
    xl, xr, yc = LONE
    lay = layer(); d = ImageDraw.Draw(lay); s = 4.6
    for k, j in enumerate((-0.04, 0.03, -0.02)):
        x = xl + (xr - xl) * ((k + 1) / 4 + j)
        d.rectangle([S(x - s / 2, yc - s / 2), S(x + s / 2, yc + s / 2)], fill=PUR, outline=PURD, width=int(SS * 0.8))
        d.rectangle([S(x - s * 0.18, yc - s * 0.18), S(x + s * 0.18, yc + s * 0.18)], fill=(250, 250, 248, 255))
    img = comp(img, lay)

# ── ③ 행 17: 글자 꼴 금빛 브로치 d · f
PINS = [(1830.0, 497.0, 24.0, 'd'), (1918.5, 511.5, 24.0, 'f')]    # G3(앞모습)를 붙인 뒤 잰 가슴 한가운데 — 자매 브로치(34 ~ 36 px)보다 조금 작게
GOLD, GOLDL = (206, 160, 52, 255), (246, 214, 120, 255)
def glyph(d, cx, top, h, ch):
    """금빛 글자 브로치 — 잉크 테 위에 금(굵기 h*0.17) · 소문자 d / f"""
    wv = max(1.2, h * 0.17)
    if ch == 'd':
        r = h * 0.27; bx, by = cx - h * 0.06, top + h - r - wv / 2      # 둥근 배(왼) + 곧은 기둥(오른 · 위로 길게)
        stem = [(cx + h * 0.22, top), (cx + h * 0.22, top + h)]
        strokes = [('ell', (bx - r, by - r, bx + r, by + r)), ('line', stem)]
    else:
        strokes = [('arc', (cx - h * 0.02, top, cx + h * 0.40, top + h * 0.40)),             # 위 갈고리
                   ('line', [(cx + h * 0.02, top + h * 0.2), (cx + h * 0.02, top + h)]),      # 기둥
                   ('line', [(cx - h * 0.20, top + h * 0.42), (cx + h * 0.26, top + h * 0.42)])]  # 가로대
    for (col, extra) in ((INK, 1.0), (GOLD, 0.0), (GOLDL, -0.55)):
        w = max(1, int(SS * (wv + extra)))
        for kind, g in strokes:
            if kind == 'ell':
                d.ellipse([S(g[0], g[1]), S(g[2], g[3])], outline=col, width=w)
            elif kind == 'arc':
                d.arc([S(g[0], g[1]), S(g[2], g[3])], 180, 330, fill=col, width=w)
            else:
                d.line([S(*g[0]), S(*g[1])], fill=col, width=w)
if PINS:
    lay = layer(); d = ImageDraw.Draw(lay)
    for (cx, top, h, ch) in PINS: glyph(d, cx, top, h, ch)
    img = comp(img, lay)

# ── ④ ⑤ 걸상: 칼자국 덮기 · 청록 · 주황 보태기
random.seed(133)
tyT = lambda x: 611 + (x - 1560) * 0.117 + 2.5
OL, OLD = (128, 118, 52, 255), (52, 46, 18, 255)
def bact(d, bx, by, ang, k=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: S(bx + u * ca - v * sa, by + u * sa + v * ca)
    body = [P(4.4 * k * math.cos(t), 1.9 * k * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)]
    d.polygon(body, fill=OL, outline=OLD)
    d.line([P(-4.4 * k - j * 0.9, 1.1 * math.sin(j * 1.1)) for j in range(9)], fill=OLD, width=int(SS * 0.7))
def bub2(d, cx, cy, r):
    d.ellipse([S(cx - r, cy - r), S(cx + r, cy + r)], fill=(250, 251, 253, 255), outline=(116, 128, 146, 255), width=int(SS * 0.9))
    d.ellipse([S(cx - r * 0.5, cy - r * 0.55), S(cx - r * 0.05, cy - r * 0.1)], fill=(255, 255, 255, 255))
lay = layer(); d = ImageDraw.Draw(lay)
for k in range(16):                                   # ④ 칼자국(x≈1930) 위에 온전한 헤엄이 — 끝이 들쭉날쭉하게
    x = random.uniform(1925.0, 1941.0); y = tyT(x) + random.uniform(-15.0, 7.0)
    bact(d, x, y, random.uniform(-1.5, 1.5), random.uniform(0.85, 1.05))
bub2(d, 1931.5, 589.0, 3.1)                           # 반쪽이던 방울을 온전히
bact(d, 1930.8, 615.5, 0.9)                           # 칼자국 위에 홀로 남은 꼬리 토막을 덮는다
for (xc, extra) in ((1706, [(-15, -2.0, 0.5), (15, -5.0, -0.6)]), (1900, [(-15, -4.5, 0.6), (15, -1.5, -0.3)])):   # ⑤
    for (dx, dy, ang) in extra:
        bact(d, xc + dx, tyT(xc + dx) + dy, ang)
    bub2(d, xc + 9, tyT(xc) - 36, 2.6)
img = comp(img, lay)

# ── ⑥ 행 14: 꼬리 끝 오목한 주름(구멍 없음)
A = np.asarray(img).astype(float)
def cushion_col(x, y):
    """꼬리 끝 바로 양옆(같은 높이)의 쿠션 빛깔 — 입술이 둘레와 한 빛깔이 되게"""
    sub = np.concatenate([A[int(y) - 1:int(y) + 3, int(x) - 10:int(x) - 5].reshape(-1, 3), A[int(y) - 1:int(y) + 3, int(x) + 6:int(x) + 11].reshape(-1, 3)])
    g = sub[(sub[:, 1] > sub[:, 0] + 8) & (sub[:, 1] > sub[:, 2] + 8) & (sub.mean(axis=1) > 90)]
    return tuple(int(v) for v in (np.median(g, axis=0) if len(g) else sub.mean(axis=0)))
TIPS = [(933.0, 657.6, 12.0), (1427.2, 657.6, 12.0), (1167.6, 590.8, 9.0), (1298.2, 598.6, 9.0)]
for (x, y, w) in TIPS:
    col = cushion_col(x, y); dark = tuple(int(c * 0.72) for c in col)
    h = w * 0.36
    # 안쪽 그늘(먼 쪽 반달) — 초록 화소에만
    lay = layer(); d = ImageDraw.Draw(lay)
    d.ellipse([S(x - w / 2, y - h * 0.9), S(x + w / 2, y + h * 0.6)], fill=dark + (120,))
    sh = np.asarray(lay.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.9))).astype(float)
    a = sh[..., 3:4] / 255
    Ag = A.copy()
    green = ((A[..., 1] > A[..., 0] + 6) & (A[..., 1] > A[..., 2] + 6))[..., None]
    A = np.where(green, A * (1 - a) + sh[..., :3] * a, A)
    img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
    # 가까운 쪽 입술 — 꼬리 끝을 겉천이 덮는다 · 입술 선 · 당겨진 주름
    lay = layer(); d = ImageDraw.Draw(lay)
    wl = w * 0.62
    lip = [S(x + (wl / 2) * math.cos(t), y - 1.4 + h * 0.62 * math.sin(t)) for t in np.linspace(0, math.pi, 40)]
    d.polygon(lip + [S(x - wl / 2, y - 1.4)], fill=col + (255,))
    d.line([S(x + (wl / 2 + 0.6) * math.cos(t), y - 1.9 + h * 0.30 * math.sin(t)) for t in np.linspace(0.05, math.pi - 0.05, 30)], fill=dark + (200,), width=int(SS * 0.8))
    for (ang, L) in ((200, 0.55), (228, 0.5), (312, 0.5), (340, 0.55), (18, 0.45), (162, 0.45)):
        t = math.radians(ang); ex, ey = x + (w / 2) * math.cos(t), y + h * 0.7 * math.sin(t)
        d.line([S(ex, ey), S(ex + w * L * math.cos(t), ey + w * L * 0.5 * math.sin(t))], fill=dark + (150,), width=int(SS * 0.8))
    img = comp(img, lay)
    A = np.asarray(img).astype(float)

# ── ⑦ 흰 빔 오른쪽 하늘 빛무리 — 왼쪽(빔 왼 끝 1545 에서 거리 d)의 빛깔을 오른쪽(빔 오른 끝 1584 에서 같은 거리)으로 옮긴다
A = np.asarray(img).astype(float)
L_ = A.mean(axis=2); sat = A.max(axis=2) - A.min(axis=2)
skym = (L_ > 214) & (sat < 26)
for y in range(18, 300):
    for dd in range(0, 110):
        xr, xl = 1584 + dd, 1543 - dd
        if skym[y, xr] and skym[y, xl]:
            w = 0.85 * max(0.0, 1 - dd / 110.0) ** 1.2
            A[y, xr] = A[y, xr] * (1 - w) + A[y, xl] * w
img = Image.fromarray(np.clip(A, 0, 255).astype('uint8'))
img.save('cur14.png')
for (b, nm, k) in [((1200, 520, 1330, 680), 'v14_ball.png', 4), ((1860, 560, 2010, 690), 'v14_seam.png', 4), ((1480, 20, 1720, 360), 'v14_sky.png', 2)]:
    img.crop(b).resize(((b[2] - b[0]) * k, (b[3] - b[1]) * k), Image.LANCZOS).save(nm)
print('cur14 saved')

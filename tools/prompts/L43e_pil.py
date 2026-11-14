#!/usr/bin/env python3
# L43e_pil.py <base.png> <구역 폴더(gem_Z1 ~ gem_Z6.png)> <out.png> — L43e 「상자 차례대로 짓는 초파리」 조립.
# 이 그림의 뼈대는 「끈에 꿴 상자의 차례 = 파리 몸 상자의 차례」다 — 그 뼈대(끈 · 상자 셋 · 화살)와 셈이 뜻인 것(부모 · 알 발치의 상자 짝)을 Gemini 에게 맡기지 않는다.
#  ① 바탕에서는 담 띠만 쓴다. 나머지 바닥은 비우고, 또렷하게 다시 그린 구역(Z1 ~ Z6)에서 물건을 오려(가장자리에서 이어진 바탕빛 · 그림자빛을 투명하게) 제자리에 세운다.
#  ② 금빛 짚끈(L43c · d 의 그 끈)과 끈에 꿴 작은 상자 셋(주황 · 파랑 · 분홍) · 상자에서 몸 상자로 가는 같은 빛깔 화살 셋.
#  ③ 보통 파리 한 마리(Z5 오른쪽)에 큰 파리의 붉은 눈을 줄여 붙여 조각 하나를 만들고, 부모 둘(하나는 뒤집어) · 눈알 팩을 받는 파리에 똑같이 쓴다.
#  ④ 부모 · 알 발치의 파랑 상자 짝(성한 것 / 찌그러진 것) · 부모 → 알 화살 · 받은 파리 다리의 붉은 눈 하나.
import sys, math, numpy as np, cv2
from PIL import Image, ImageDraw
src, zdir, dst = sys.argv[1:4]
im = Image.open(src).convert('RGB'); W, H = im.size
INK = (24, 20, 18, 255)
GND = (239, 232, 202)
a = np.array(im).astype(int)
a[96:, :] = GND; a[:, 1416:] = GND                                                # 바탕에서는 담 띠(x 0 ~ 1414 · y 0 ~ 94)만 남긴다
reg = a[0:100, 1404:1416]; reg[(reg > np.array(GND) + 3).all(axis=2)] = GND       # 담 띠 오른쪽 끝의 흰 테
im = Image.fromarray(a.astype(np.uint8))

S = 3
def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay, rows=None):
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    if rows:
        al = np.asarray(small.split()[3]).copy(); al[:rows[0]] = 0; al[rows[1]:] = 0; small.putalpha(Image.fromarray(al))
    base = im.convert('RGBA'); base.alpha_composite(small); im = base.convert('RGB')
def T(pts): return [(x * S, y * S) for x, y in pts]
def spline(pts, n=24):
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = [np.array(p, float) for p in P[i - 1:i + 3]]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(P[-2])); return out
def resample(q, step=1.0):
    u = [q[0]]; acc = 0.0
    for (x0, y0), (x1, y1) in zip(q, q[1:]):
        seg = math.hypot(x1 - x0, y1 - y0); t = step - acc
        while t <= seg:
            u.append((x0 + (x1 - x0) * t / seg, y0 + (y1 - y0) * t / seg)); t += step
        acc = (acc + seg) % step
    return u
ROPE, ROPE_D = (236, 196, 96, 255), (176, 128, 44, 255)
RW, RO = 13, 2.4
def rope(d, pts, smooth=True):
    """금빛 짚끈(L43c · L43d 와 같은 함수) — 1 px 걸음으로 원을 찍는다."""
    u = resample(spline(pts) if smooth else pts)
    for r, col in (((RW + 2 * RO) / 2, INK), (RW / 2, ROPE)):
        for x, y in u: d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=col)
    for k in range(5, len(u) - 1, 9):
        (x0, y0), (x1, y1) = u[k - 1], u[k + 1]; seg = math.hypot(x1 - x0, y1 - y0) or 1
        tx, ty = (x1 - x0) / seg, (y1 - y0) / seg; nx, ny = -ty, tx; x, y = u[k]; h = RW * 0.44
        d.line([((x - nx * h - tx * 3.2) * S, (y - ny * h - ty * 3.2) * S), ((x + nx * h + tx * 3.2) * S, (y + ny * h + ty * 3.2) * S)], fill=ROPE_D, width=int(1.7 * S))
def poly(d, pts, fill, w=3.2):
    q = T(pts)
    if fill: d.polygon(q, fill=fill)
    d.line(q + [q[0]], fill=INK, width=int(w * S), joint='curve')
    for x, y in q: r = w * S / 2; d.ellipse([x - r, y - r, x + r, y + r], fill=INK)
def arrow(d, pts, col, w=9, head=24):
    q = resample(spline(pts)); (x0, y0), (x1, y1) = q[-8], q[-1]; an = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + head * 0.55 * math.cos(an), y1 + head * 0.55 * math.sin(an))
    hp = [tip, (x1 - head * 0.5 * math.cos(an) + head * 0.62 * math.sin(an), y1 - head * 0.5 * math.sin(an) - head * 0.62 * math.cos(an)), (x1 - head * 0.5 * math.cos(an) - head * 0.62 * math.sin(an), y1 - head * 0.5 * math.sin(an) + head * 0.62 * math.cos(an))]
    for r, c in (((w + 5) / 2, INK), (w / 2, col)):
        for x, y in q[:-6]: d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    poly(d, hp, col, 2.6)

# ── 조각 오리기: 구역 그림에서 hint 상자 안에 든 덩이(들)만 — 가장자리에서 이어진 바탕빛 · 그림자빛은 투명
_cache = {}
def comp_sprite(name, hint, tol=18):
    if name not in _cache:
        c = np.array(Image.open(f'{zdir}/gem_{name}.png').convert('RGB')).astype(int)
        bg = np.median(np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]]), axis=0)
        R_, G_, B_ = c[..., 0], c[..., 1], c[..., 2]
        bgm = (np.abs(c - bg).max(axis=2) <= tol) | ((R_ >= 150) & (R_ <= 234) & (np.abs(R_ - G_) <= 18) & (R_ - B_ >= 8) & (R_ - B_ <= 60))
        n, lab = cv2.connectedComponents(bgm.astype(np.uint8), connectivity=4)
        border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); border = border[border != 0]
        fg = (~np.isin(lab, border)).astype(np.uint8)
        n2, lab2, st, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
        _cache[name] = (c, lab2, st)
    c, lab2, st = _cache[name]
    x0, y0, x1, y1 = hint
    ids = [i for i in range(1, len(st)) if st[i][0] >= x0 and st[i][1] >= y0 and st[i][0] + st[i][2] <= x1 and st[i][1] + st[i][3] <= y1 and st[i][4] >= 150]   # 150 px 보다 작은 덩이 = 그림자 가장자리 부스러기
    m = np.isin(lab2, ids); ys, xs = np.where(m); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    al = (m[by0:by1, bx0:bx1] * 255).astype(np.uint8)
    al = cv2.erode(al, np.ones((3, 3), np.uint8)); al = cv2.GaussianBlur(al, (0, 0), 0.9)
    sp = Image.fromarray(np.dstack([c[by0:by1, bx0:bx1].astype(np.uint8), al]), 'RGBA')
    sp.origin = (bx0, by0)                                                           # 구역 그림에서의 왼쪽 위
    return sp
def stick(sp, scale, cx, bottom, flip=False):
    """조각을 scale 배로 줄여 아래 가운데가 (cx, bottom) 에 오게 붙인다. 돌려주는 값 = 붙인 자리의 왼쪽 위."""
    global im
    w, h = max(1, round(sp.width * scale)), max(1, round(sp.height * scale))
    s2 = sp.resize((w, h), Image.LANCZOS)
    if flip: s2 = s2.transpose(Image.FLIP_LEFT_RIGHT)
    x0, y0 = round(cx - w / 2), round(bottom - h)
    base = im.convert('RGBA'); base.alpha_composite(s2, (x0, y0)); im = base.convert('RGB')
    return x0, y0

def cut(sp, fn):
    """조각에서 fn(x, y)(구역 그림 좌표)가 참인 곳을 투명하게 — Gemini 가 그린 곧은 막대 다리를 떼어 낸다."""
    arr = np.array(sp); ox, oy = sp.origin
    ys, xs = np.mgrid[0:sp.height, 0:sp.width]; arr[..., 3][fn(xs + ox, ys + oy)] = 0
    out = Image.fromarray(arr, 'RGBA'); out.origin = sp.origin; return out
def legs(tf, specs, w):
    """관절 다리 — 이 그림의 모든 초파리 다리를 같은 꼴로(엉덩이 → 무릎 → 발목 → 발끝). 머리에 돋은 다리도 이 함수가 그린다.
    tf = 구역 좌표 → 그림 좌표 · specs = [(엉덩이, 발목, 무릎이 불거지는 쪽 ±1, 발끝 방향 ±1)] · 돌려주는 값 = 무릎들의 그림 좌표."""
    global im
    lay = layer(); d = ImageDraw.Draw(lay); knees = []
    for H, F, kn, toe in specs:
        vx, vy = F[0] - H[0], F[1] - H[1]; L = math.hypot(vx, vy); nx, ny = -vy / L, vx / L
        K = (H[0] + vx * 0.46 + nx * kn * 0.21 * L, H[1] + vy * 0.46 + ny * kn * 0.21 * L)
        TT = (F[0] + toe * max(0.15 * L, 9), F[1] + (0.02 * L if vy > 0 else -0.02 * L))
        q = [tf(*P) for P in (H, K, F, TT)]; knees.append(q[1])
        d.line(T(q), fill=INK, width=int(w * S), joint='curve')
        for x, y in q: d.ellipse([(x - w / 2) * S, (y - w / 2) * S, (x + w / 2) * S, (y + w / 2) * S], fill=INK)
    put(lay); return knees
def place(sp, scale, cx, bottom, flip=False):
    """조각을 붙이고, 구역 좌표 → 그림 좌표 함수를 돌려준다."""
    x0, y0 = stick(sp, scale, cx, bottom, flip)
    ox, oy = sp.origin; w = round(sp.width * scale)
    if flip: return lambda x, y: (x0 + w - (x - ox) * scale, y0 + (y - oy) * scale)
    return lambda x, y: (x0 + (x - ox) * scale, y0 + (y - oy) * scale)

ORA, BLU, PNK = (239, 143, 36, 255), (75, 133, 213, 255), (240, 128, 171, 255)
# 다리 자리(구역 그림 좌표) — (엉덩이, 발목, 무릎 쪽, 발끝 쪽). 머리가 왼쪽인 파리: 앞다리 · 가운뎃다리의 발끝은 왼쪽, 뒷다리는 오른쪽.
LEG_BIG = [((430, 366), (302, 520), +1, -1), ((520, 366), (537, 520), -1, -1), ((615, 366), (768, 520), -1, +1)]   # 앞 · 뒷다리의 발끝이 주황 · 분홍 화살에 닿지 않게 안쪽으로
LEG_N = [((735, 204), (665, 275), +1, -1), ((772, 204), (778, 275), -1, -1), ((810, 204), (888, 275), -1, +1)]
LEG_MUT = [((680, 419), (600, 497), +1, -1), ((725, 419), (730, 497), -1, -1), ((768, 419), (858, 497), -1, +1)]
LEG_MUT_HEAD = [((566, 318), (540, 204), -1, -1), ((600, 318), (648, 214), -1, +1)]          # 더듬이 자리에 돋아 허공을 차는 다리 둘
LEG_MOM = [((625, 303), (517, 420), +1, -1), ((690, 303), (700, 420), -1, -1), ((752, 303), (878, 420), -1, +1)]
SHADOW = (203, 196, 168, 255)

# ── 자리(모두 2048 x 1144 좌표)
BIG_S, BIG_CX, BIG_BOT = 0.86, 600, 548                                            # 큰 상자 파리(Z1) — 발끝 y
SP_BIG = cut(comp_sprite('Z1', (30, 10, 1000, 545)), lambda x, y: y > 369)
bx0 = BIG_CX - SP_BIG.width * BIG_S / 2; by0 = BIG_BOT - SP_BIG.height * BIG_S
def big(x, y): return (bx0 + (x - SP_BIG.origin[0]) * BIG_S, by0 + (y - SP_BIG.origin[1]) * BIG_S)   # Z1 좌표 → 그림 좌표
BODY = [(78, 368), (373, 667), (672, 968)]                                         # Z1 에서 몸 상자 셋의 x 범위(주황 · 파랑 · 분홍)
BOX_BOT = big(0, 365)[1]                                                           # 몸 상자의 아랫변 y
CXS = [big((u + v) / 2, 0)[0] for u, v in BODY]                                    # 몸 상자 셋의 가운데 x → 끈의 작은 상자도 그 바로 밑
YR = 676                                                                           # 끈의 높이
BW, BH, LIDH = 150, 80, 18                                                         # 끈에 꿴 작은 상자(몸통 80 + 뚜껑 18)

# ── ① 그림자(조각을 세울 자리마다) → 끈 → 끈에 꿴 상자 셋 → 화살 셋 (조각보다 먼저 그려 다리 뒤로 지나가게)
lay = layer(); d = ImageDraw.Draw(lay)
def shadow(cx, cy, rx, ry): d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=SHADOW)
shadow(BIG_CX + 10, BIG_BOT - 2, 372, 22)
put(lay)
lay = layer(); d = ImageDraw.Draw(lay)
rope(d, [(-20, YR), (400, YR), (800, YR), (1180, YR), (1262, YR - 4), (1310, YR - 26), (1334, YR - 70), (1338, YR - 170), (1336, YR - 370), (1332, YR - 520), (1328, YR - 600)])
put(lay, rows=(95, H))                                                             # 담 띠 위로는 그리지 않는다(끈이 뒤 담 밑으로 든다)
lay = layer(); d = ImageDraw.Draw(lay)
for cx, col in zip(CXS, (ORA, BLU, PNK)):
    poly(d, [(cx - BW / 2, YR - BH / 2), (cx + BW / 2, YR - BH / 2), (cx + BW / 2, YR + BH / 2), (cx - BW / 2, YR + BH / 2)], col, 3.6)
    poly(d, [(cx - BW / 2 - 7, YR - BH / 2 - LIDH), (cx + BW / 2 + 7, YR - BH / 2 - LIDH), (cx + BW / 2 + 7, YR - BH / 2), (cx - BW / 2 - 7, YR - BH / 2)], col, 3.6)
    for sx in (-1, 1):                                                             # 끈이 드나드는 구멍(옆면의 검은 반달)
        hx = cx + sx * BW / 2
        d.pieslice([(hx - 9) * S, (YR - 12) * S, (hx + 9) * S, (YR + 12) * S], 90 if sx > 0 else 270, 270 if sx > 0 else 90, fill=INK)
AX = [CXS[0], big(476, 0)[0], CXS[2] + 24]                                              # 파랑 화살은 앞다리와 가운뎃다리 사이로(가운데는 다리가 지난다) · 분홍 화살은 뒷다리 발끝을 비켜 조금 오른쪽
for ax, col in zip(AX, (ORA, BLU, PNK)):
    arrow(d, [(ax, YR - BH / 2 - LIDH - 10), (ax, (YR + BOX_BOT) / 2), (ax, BOX_BOT + 20)], col, w=11, head=28)   # 화살촉 끝이 몸 상자 아랫변 바로 밑(틈 5 px)
put(lay)
tf = place(SP_BIG, BIG_S, BIG_CX, BIG_BOT)
legs(tf, LEG_BIG, 10)

# ── ② 아래 왼쪽: 루페 든 흰 가운 + 머리 상자가 파랑인 돌연변이 파리(Z2 — 서로의 자리는 구역 그림 그대로)
Z2S, Z2X, Z2B = 0.72, -28, 1122                                                    # Z2 (x, y) → (Z2X + 0.72 x, Z2B − (538 − y) · 0.72)
SP_SCI = comp_sprite('Z2', (100, 14, 520, 548)); SP_MUT = comp_sprite('Z2', (496, 170, 960, 512))
_m = np.array(SP_MUT); _ox, _oy = SP_MUT.origin
_m[300 - _oy:342 - _oy, 582 - _ox:616 - _ox] = _m[300 - _oy:342 - _oy, 578 - _ox:579 - _ox]                          # 머리 상자 윗변에 박힌 다리 밑동 — 깨끗한 이웃 세로줄(x = 578)로 메운다
_m[328 - _oy:333 - _oy, 506 - _ox:652 - _ox, :3] = INK[:3]                                                               # 머리 상자에도 뚜껑 테(둘째 상자의 뚜껑 아랫줄을 이어 긋는다 — 민짜면 다른 상자와 달라 보였다 · 일치 검사 2회)
SP_MUT = Image.fromarray(_m, 'RGBA'); SP_MUT.origin = (_ox, _oy)
SP_MUT = cut(SP_MUT, lambda x, y: (y > 422) | ((y < 236) & (x < 672)) | ((y >= 236) & (y < 313) & (x < 606 + (316 - y) * 0.70 - 9)))
lay = layer(); d = ImageDraw.Draw(lay)
shadow(Z2X + 212 * Z2S, Z2B - 6, 84, 13); shadow(Z2X + 728 * Z2S, Z2B - 36 * Z2S, 138, 14)
put(lay)
for sp in (SP_SCI, SP_MUT):
    ox, oy = sp.origin
    tf = place(sp, Z2S, Z2X + (ox + sp.width / 2) * Z2S, Z2B - (538 - (oy + sp.height)) * Z2S)
legs(tf, LEG_MUT + LEG_MUT_HEAD, 5)

# ── ③ 보통 파리 조각 하나(Z5 오른쪽 파리 + 큰 파리의 붉은 눈) — 부모 둘 · 받는 파리가 함께 쓴다
SP_N = cut(comp_sprite('Z5', (560, 40, 975, 290)), lambda x, y: y > 206)
z1 = np.array(Image.open(f'{zdir}/gem_Z1.png').convert('RGB'))
EX, EY, ER = 177, 268, 49                                                          # Z1 의 붉은 눈(가운데 · 테 포함 반지름)
eye = Image.fromarray(z1[EY - ER:EY + ER, EX - ER:EX + ER]).convert('RGBA')
m = Image.new('L', (ER * 2 * 4, ER * 2 * 4), 0); ImageDraw.Draw(m).ellipse([6, 6, ER * 8 - 6, ER * 8 - 6], fill=255); eye.putalpha(m.resize((ER * 2, ER * 2), Image.LANCZOS))
def with_eye(sp, lx, ly, r):
    """조각의 (lx, ly)(조각 좌표)에 반지름 r 인 붉은 눈을 붙인 새 조각."""
    out = sp.copy(); e = eye.resize((2 * r, 2 * r), Image.LANCZOS); out.alpha_composite(e, (round(lx - r), round(ly - r))); out.origin = sp.origin; return out
nx, ny = SP_N.origin
SP_N = with_eye(SP_N, 628 - nx, 154 - ny, 23)                                      # 감은 눈 자리에 붉은 눈(큰 파리와 같은 눈)

# ── ④ 아래 가운데: 등뼈만 남은 물고기 + 눈알 여섯 개들이 팩(Z3) → 받는 파리
SP_FISH = comp_sprite('Z3', (60, 40, 800, 960))
lay = layer(); d = ImageDraw.Draw(lay)
shadow(852, 1116, 62, 11); shadow(1222, 1108, 150, 13)
put(lay)
stick(SP_FISH, 0.40, 880, 1124)
SP_REC = with_eye(SP_N, 900 - nx, 166 - ny, 23)                                    # 받는 파리: 맨 뒤 분홍 상자의 옆면에 머리의 눈과 똑같은 붉은 눈 하나 더
legs(place(SP_REC, 0.86, 1215, 1114), LEG_N, 4.8)                                  #   (다리 무릎에 달았더니 눈이 아니라 「붉은 공 · 열매」로 읽혔다 — 일치 검사 1회. 상자 옆면에 달아야 머리의 눈과 같은 것으로 읽힌다)

# ── ⑤ 오른쪽 위: 어미 파리가 알의 앞(왼쪽) 끝에 코를 붙인다(Z4 — 자리는 구역 그림 그대로)
Z4S, Z4X, Z4Y = 0.6035, 1430, 104
SP_MOM = cut(comp_sprite('Z4', (5, 40, 1015, 445)), lambda x, y: (y > 307) & (x > 625 - (y - 302) * 0.9 - 16)); SP_EGGB = comp_sprite('Z4', (25, 485, 345, 672))
_m = np.array(SP_MOM); _ox, _oy = SP_MOM.origin                                    # 머릿수건 안쪽의 회색 덩이 → 수건 바탕빛(「회색 모자 같은 덩어리」로 읽혔다 — 일치 검사 1회)
_r = _m[58 - _oy:156 - _oy, 380 - _ox:504 - _ox]; _g = (np.abs(_r[..., :3].astype(int) - np.array([147, 137, 126])).max(axis=2) <= 26)
_r[_g, 0], _r[_g, 1], _r[_g, 2] = 232, 235, 202
for _y in range(334, 367):                                                         # 아래 앞다리의 끝이 알 테두리 안쪽으로 들어와 「알을 뚫은 것」처럼 보였다(일치 검사 1 ~ 3회) → 알 안쪽 토막을 알 빛깔로 지워 테두리에 닿게
    _m[_y - _oy, 278 - _ox:int(314 - max(0, _y - 350) * 0.7) - _ox, :3] = (243, 234, 203)
SP_MOM = Image.fromarray(_m, 'RGBA'); SP_MOM.origin = (_ox, _oy)
lay = layer(); d = ImageDraw.Draw(lay)
shadow(Z4X + 560 * Z4S, Z4Y + 418 * Z4S, 250, 15); shadow(Z4X + 190 * Z4S, Z4Y + 652 * Z4S, 86, 9)
put(lay)
for sp in (SP_EGGB, SP_MOM):
    ox, oy = sp.origin
    tf = place(sp, Z4S, Z4X + (ox + sp.width / 2) * Z4S, Z4Y + (oy + sp.height) * Z4S)
legs(tf, LEG_MOM, 4.6)

# ── ⑥ 오른쪽 아래: 부모 둘(같은 조각 — 왼쪽은 뒤집어 마주 봄) → 알 넷(성한 알 하나를 세 번 · 넷째는 깨진 알 속의 죽은 배아)
PX = (1585, 1895); PBOT = 762
EGX = (1500, 1650, 1800); EBOT = 1022; DX, DBOT = 1952, 1026                     # 알 사이 150 px — 발치의 상자 짝이 알마다 따로 떨어져 보이게(131 px 일 때는 이웃 짝과 붙어 어느 알의 것인지 모호했다 · 일치 검사 6회)
SP_EGG = comp_sprite('Z6', (50, 38, 222, 256)); SP_DEAD = comp_sprite('Z6', (700, 60, 960, 290))
lay = layer(); d = ImageDraw.Draw(lay)
for x in PX: shadow(x, PBOT - 3, 104, 10)
for x in EGX: shadow(x, EBOT - 2, 42, 8)
shadow(DX, DBOT - 4, 80, 10)
put(lay)
legs(place(SP_N, 0.60, PX[0], PBOT, flip=True), LEG_N, 3.8); legs(place(SP_N, 0.60, PX[1], PBOT), LEG_N, 3.8)
for x in EGX: stick(SP_EGG, 0.60, x, EBOT)
stick(SP_DEAD, 0.78, DX, DBOT)

# 발치의 파랑 상자 짝 — 성한 것(뚜껑 달린 작은 상자) / 찌그러진 것(납작하게 구겨진 것)
def mini(d, cx, top, ok=True):
    w, h, lh = 48, 28, 10                                                          # 몸통 48 x 28 + 뚜껑 10
    y1 = top + lh + h
    if ok:
        poly(d, [(cx - w / 2, top + lh), (cx + w / 2, top + lh), (cx + w / 2, y1), (cx - w / 2, y1)], BLU, 2.8)
        poly(d, [(cx - w / 2 - 4, top), (cx + w / 2 + 4, top), (cx + w / 2 + 4, top + lh), (cx - w / 2 - 4, top + lh)], BLU, 2.8)
    else:                                                                          # 밟혀 주저앉은 같은 상자 — 옆으로 벌어진 낮은 몸통 + 가운데가 꺾여 내려앉은 뚜껑(양 끝은 들림). 구겨진 덩이로만 그리면 「구긴 종이 · 쓰레기」로 읽혔다(일치 검사 1 ~ 3회)
        poly(d, [(cx - 29, y1), (cx - 26, y1 - 15), (cx - 8, y1 - 13), (cx, y1 - 7), (cx + 9, y1 - 13), (cx + 26, y1 - 16), (cx + 30, y1)], BLU, 2.8)
        poly(d, [(cx - 31, y1 - 24), (cx - 27, y1 - 15), (cx, y1 - 5), (cx + 28, y1 - 16), (cx + 31, y1 - 26), (cx + 24, y1 - 27), (cx, y1 - 14), (cx - 24, y1 - 26)], BLU, 2.8)
        for p, q in (((cx - 17, y1 - 9), (cx - 20, y1 - 2)), ((cx + 16, y1 - 10), (cx + 20, y1 - 2)), ((cx - 3, y1 - 3), (cx + 3, y1 - 3))): d.line(T([p, q]), fill=INK, width=int(1.7 * S))
MT = PBOT + 16; ET = EBOT + 16
lay = layer(); d = ImageDraw.Draw(lay)                                             # 짝마다 그림자 하나를 함께 깔아 「이 둘이 한 짝」임을 보인다(짝 사이가 붙어 어느 알의 것인지 헷갈렸다 · 일치 검사 6 · 7회)
for x in PX: shadow(x, MT + 38, 70, 7)
for x in EGX + (DX,): shadow(x, ET + 38, 66, 7)
put(lay)
lay = layer(); d = ImageDraw.Draw(lay)
for x in PX: mini(d, x - 32, MT, True); mini(d, x + 32, MT, False)
for x, pair in zip(EGX + (DX,), ((True, True), (True, False), (False, True), (False, False))):
    mini(d, x - 30, ET, pair[0]); mini(d, x + 30, ET, pair[1])
arrow(d, [(1740, PBOT + 6), (1740, PBOT + 60), (1740, 876)], (120, 112, 100, 255), w=8, head=24)   # 부모 → 알
put(lay)
im.save(dst)
print('ok', dst, 'CXS', [round(x) for x in CXS], 'AX', [round(x) for x in AX], 'BOX_BOT', round(BOX_BOT))

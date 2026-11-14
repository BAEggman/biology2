#!/usr/bin/env python3
# L13b_pil2.py <base.png> <out.png> — L13b 다시 짓기 「가시 하나에서 번진 안뜰의 난리」의 PIL 마무리(2026-11-14 · 사건 장면).
#  바탕 = Gemini 가 통째로 그린 장면 S1(1024 → 2048) + 구역 편집 B1 · B2 · B3b · B4 · B7(L13b_build2.sh) — 이 PIL 뒤에 B8s(밑동 물보라 · 돌벽 틈) · B9 · B10 을 붙인다.
#  여기서는: 뚱보 경비의 무릎을 치는 가는 물줄기의 「출발점」을 저수지로 고쳐 그림(Gemini 는 그 줄기를 세균 머리에서 끝냈다 — 구역 편집 B5 도 실패)
#  · 여자의 빨간 원피스 → 청록(붉은 배지가 묻힌다) · 두루마리 끈 빨강 → 갈색 · 붉은 리본 배지(자기 — 성 안의 사람 · 흰 덩이 · 경비 모두).
import sys, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s13_lib import S, INK, poly, line, disc, badge, RED, RED_D, GOLD_C

W, H = 2048, 1144
src, dst = sys.argv[1:3]
im = Image.open(src).convert('RGB')
assert im.size == (W, H), im.size

def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay):
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    b = im.convert('RGBA'); b.alpha_composite(small); im = b.convert('RGB')
def catmull(pts, n=12):
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1]); return out

# ── ① 가는 물줄기(보체 → 염증 증폭 · 뚱보 경비의 무릎)를 저수지에서 나오게 — Gemini 는 이 줄기의 오른쪽 끝을 세균 머리에 내렸다(구역 편집 B5 · B6 둘 다 실패)
#      → 꼭대기(x 1092) 오른쪽의 옛 줄기를 열마다 찾아 지우고(굵은 줄기와 엇갈리는 x 1362 ~ 1402 는 남김), 같은 꼴의 줄기를 저수지 물에서 솟게 다시 그린다
a = np.array(im)[:, :, ::-1].copy(); m = np.zeros(a.shape[:2], np.uint8)
PRED = [(1092, 737), (1150, 748), (1200, 761), (1250, 779), (1300, 800), (1340, 822), (1362, 836), (1402, 865), (1425, 882), (1452, 902)]
def pred_y(x):
    for (x0, y0), (x1, y1) in zip(PRED, PRED[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None
rgb = a[:, :, ::-1].astype(int)
for x in range(1092, 1458):
    if 1360 <= x <= 1404: continue
    py = pred_y(x)
    if py is None: continue
    ys = [y for y in range(int(py) - 26, int(py) + 27) if rgb[y, x, 2] - rgb[y, x, 0] > 22 and rgb[y, x, 2] > 150]
    if not ys: continue
    cy = (min(ys) + max(ys)) / 2; hw = (max(ys) - min(ys)) / 2 + 6
    m[int(cy - hw):int(cy + hw) + 1, x] = 255
m = cv2.dilate(m, np.ones((3, 3), np.uint8))
TJ = np.zeros_like(m); cv2.fillPoly(TJ, [np.array([(1345, 880), (1372, 849), (1400, 825), (1415, 812), (1450, 826), (1431, 843), (1418, 859), (1404, 876), (1392, 895), (1350, 895)], np.int32)], 255)
m_in = cv2.bitwise_and(m, TJ); m = cv2.bitwise_and(m, cv2.bitwise_not(TJ))   # 굵은 줄기 안은 물빛으로 메우고(TELEA) · 밖은 모래로
a = cv2.inpaint(a, m_in, 5, cv2.INPAINT_TELEA)
rgb = a[:, :, ::-1].astype(int)                                             # 지운 자리는 그 열의 모래 빛(가운데값)으로 채운다 — TELEA 는 테의 검정을 끌어와 얼룩을 남겼다
sandlike = (rgb[..., 0] > 200) & (rgb[..., 1] > 180) & (rgb[..., 2] > 120) & (rgb[..., 2] < 210) & (rgb[..., 0] - rgb[..., 2] > 40)
ys_, xs_ = np.where(m > 0)
for x in np.unique(xs_):
    yy = ys_[xs_ == x]; y0, y1 = max(0, yy.min() - 40), min(H, yy.max() + 41)
    colm = rgb[y0:y1, x]; ok = sandlike[y0:y1, x] & (m[y0:y1, x] == 0)
    if ok.sum() < 5: continue
    med = np.median(colm[ok], axis=0)
    for y in yy: rgb[y, x] = med
rgb = np.clip(rgb + np.random.RandomState(7).randint(-2, 3, rgb.shape) * (m[..., None] > 0), 0, 255)
im = Image.fromarray(rgb.astype(np.uint8))
# 옛 줄기가 굵은 줄기와 엇갈리던 자리(x 1350 ~ 1430)의 토막을 메운다 — 왼위 토막은 모래로 · 굵은 줄기의 오른 테가 끊긴 데는 테를 잇고 안을 물빛으로
c_ = np.array(im).astype(int)
SAND = (238, 217, 165)
pm = Image.new('L', (W, H), 0); ImageDraw.Draw(pm).polygon([(1342, 810), (1403, 813), (1397, 821), (1389, 828), (1381, 835), (1374, 841), (1367, 847), (1352, 852), (1342, 852)], fill=255)
mk = np.array(pm) > 0; c_[mk] = SAND
jet_in = np.median(c_[855:868, 1395:1405].reshape(-1, 3), axis=0).astype(int)
pm2 = Image.new('L', (W, H), 0); ImageDraw.Draw(pm2).polygon([(1408, 851), (1424, 851), (1420, 856), (1413, 864), (1406, 872), (1400, 872)], fill=255)
mk2 = (np.array(pm2) > 0) & ~((c_.mean(axis=2) < 90)); c_[mk2] = jet_in
pm3 = Image.new('L', (W, H), 0); d3 = ImageDraw.Draw(pm3)
d3.polygon([(1431, 846), (1446, 846), (1446, 884), (1408, 884), (1407, 876), (1414, 868), (1421, 860), (1427, 852)], fill=255)
d3.polygon([(1402, 873), (1428, 868), (1462, 902), (1455, 911), (1447, 916), (1440, 915), (1402, 885)], fill=255)   # 세균 머리 위까지 남은 옛 줄기 끝
mk3 = np.array(pm3) > 0; c_[mk3] = SAND
im = Image.fromarray(c_.astype(np.uint8))
lay = layer(); d = ImageDraw.Draw(lay)
line(d, catmull([(1431, 843), (1425, 851), (1418, 859), (1411, 867), (1404, 876)], 6), 3.2)
put(lay)
# 새 줄기의 길: 저수지에서 솟는 굵은 줄기의 허리(y ≈ 860)에서 갈라져 → 굵은 줄기 바깥(위 · 오른쪽)으로 더 높이 · 더 멀리 휘어 → 뚱보 경비의 무릎(옛 줄기 x 1086 에 이음)
#   (따로 물길 폭포 곁에서 솟게 그렸더니 「위에서 떨어지는 물」 · 굵은 줄기에 붙여 그리면 「얹힌 줄」 · 굵은 줄기 곁으로 물까지 내리면 줄기 둘의 밑동이 첫 물길의 폭포와 맞붙어
#    「도랑 물이 튀어 오른 것」으로 읽혔다(일치 검사 2 ~ 4회) → 굵은 줄기와 Y 자로 합쳐 물기둥 하나로 저수지 물에 닿게 — 폭포와의 사이에 돌벽이 보인다)
PATH = [(1086, 740.6), (1200, 745), (1320, 752), (1420, 757.5), (1500, 760), (1560, 767), (1597, 781), (1620, 803), (1633, 828), (1636, 848), (1632, 866), (1626, 880)]
NEW = catmull(PATH, 14)
WATER, WATER_L, WATER_HI = (150, 206, 228, 255), (196, 238, 252, 255), (236, 252, 255, 255)
lay = layer(); d = ImageDraw.Draw(lay)
def offs(pts, w, ph=0.0):
    out = []
    for i, (x, y) in enumerate(pts):
        (xa, ya) = pts[max(0, i - 1)]; (xb, yb) = pts[min(len(pts) - 1, i + 1)]
        tx, ty = xb - xa, yb - ya; L_ = math.hypot(tx, ty) or 1; nx, ny = -ty / L_, tx / L_
        t = i / (len(pts) - 1); ww = w(t) * (1 + 0.14 * math.sin(2 * math.pi * 11 * t + ph) * math.sin(math.pi * t)); out.append((x + nx * ww, y + ny * ww))
    return out
def _sm(a, b, t): u = min(1.0, max(0.0, (t - a) / (b - a))); return u * u * (3 - 2 * u)
wf = lambda t: (9.9 - 2.4 * math.sin(math.pi * t) - 1.2 * t) * (1 - 0.5 * _sm(0.86, 1.0, t))   # 옛 줄기(x 1086 · 반폭 9.9)에 꼭 맞춰 잇고 · 끝은 굵은 줄기 몸 안으로 가늘게 스민다
Lp, Rp = offs(NEW, wf, 0.0), offs(NEW, lambda t: -wf(t), 1.7)                   # 두 테가 따로 출렁인다(고른 테 = 「관 · 리본」 — L13b ㉕)
d.polygon([(x * S, y * S) for x, y in Lp + Rp[::-1]], fill=WATER)              # 채움은 테 없이(시작 마구리에 세로 테가 그어지면 「여기서 시작」으로 읽혔다 — 일치 검사 1회)
ramp = lambda t: min(1.0, t / 0.06)                                           # 밝은 띠는 옛 줄기에서 서서히(갑자기 시작하면 이음매)
inner = offs(NEW, lambda t: wf(t) * 0.45 * ramp(t), 0.6); inner2 = offs(NEW, lambda t: -wf(t) * 0.15 * ramp(t), 2.1)
d.polygon([(x * S, y * S) for x, y in inner + inner2[::-1]], fill=WATER_L)
put(lay); lay = layer(); d = ImageDraw.Draw(lay)                               # 두 테는 굵은 줄기 몸(테 포함) 밖에만 — Y 자로 갈라지는 가랑이가 생긴다
line(d, Lp, 3.0); line(d, Rp, 3.0)
c0 = np.array(im).astype(int); dk = c0.mean(axis=2) < 90; wt = ((c0[..., 2] - c0[..., 0] > 25) & (c0[..., 2] > 150)) | (c0.mean(axis=2) > 225)
TAB = {812: 1564, 818: 1578, 824: 1587, 830: 1593, 836: 1600, 842: 1605, 848: 1610, 854: 1614, 860: 1618, 866: 1623, 872: 1625, 878: 1628, 884: 1630, 890: 1636, 896: 1637, 902: 1638, 908: 1642, 914: 1643}
body = Image.new('L', (W, H), 0); bd = ImageDraw.Draw(body); _ys = sorted(TAB)
for y in range(806, 925):
    cx = int(np.interp(y, _ys, [TAB[k] for k in _ys]))
    for dx in (0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5):
        if wt[y, cx + dx]: cx += dx; break
    l_ = cx; r_ = cx
    while l_ > 1500 and wt[y, l_ - 1]: l_ -= 1
    while r_ < 1700 and wt[y, r_ + 1]: r_ += 1
    while l_ > 1500 and dk[y, l_ - 1]: l_ -= 1
    while r_ < 1700 and dk[y, r_ + 1]: r_ += 1
    bd.line([(l_ - 1, y), (r_ + 1, y)], fill=255)
bm = np.array(body.resize((W * S, H * S), Image.NEAREST)) > 0
la = np.array(lay); la[..., 3] = np.where(bm, 0, la[..., 3]); lay = Image.fromarray(la)
put(lay); lay = layer(); d = ImageDraw.Draw(lay)
hl = offs(NEW, lambda t: wf(t) * 0.25, 0.3)
for k0, k1 in ((8, 26), (34, 56), (64, 88), (96, 120), (128, 150)):
    seg = hl[k0:min(k1, len(hl))]
    if len(seg) > 1: line(d, seg, 1.8, WATER_HI)
# (솟는 자리의 물보라는 이 PIL 뒤의 구역 편집 B8s 가 그린다 — 여기 찍던 작은 물방울 여섯은 「떨어지는 물의 튐」으로 읽혔다 · 일치 검사 2회)
put(lay)

# ── ①'' 첫 물길 폭포의 아랫부분을 오른쪽으로 비껴 세운다(전단 · 바닥에서 24 px) — 물기둥 밑동과 폭포 사이에 돌벽 틈을 낸다
#      (Gemini 장면은 두 줄기의 밑동을 첫 폭포 바로 곁에 그렸다 — 일치 검사 2 ~ 4회 「도랑 물이 부딪혀 튀어 오른 것」) · 틈의 지저분한 자리는 뒤의 구역 편집 B8s 가 깨끗이 다시 그린다
c_ = np.array(im).astype(np.float32); dk_ = c_.mean(axis=2) < 90
wt_ = ((c_[..., 2] - c_[..., 0] > 25) & (c_[..., 2] > 150)) | (c_.mean(axis=2) > 225)
X0, X1, SH = 1646, 1750, 24
stone_ = np.median(c_[846:900, 1646:1652].reshape(-1, 3), axis=0); wat_ = np.median(c_[920:932, 1700:1720].reshape(-1, 3), axis=0)
o_ = c_.copy()
for y in range(846, 937):
    sh = SH * _sm(0, 1, (y - 846) / (905 - 846)) if y < 905 else SH
    if sh < 0.5: continue
    k = 0
    while k < X1 - X0 and not wt_[y, X0 + k]: k += 1
    j = k
    while j > 0 and dk_[y, X0 + j - 1]: j -= 1
    wl = X0 + j if y < 905 else X0
    seg = c_[y, wl:X1].copy(); n = X1 - wl; xs = np.arange(n) - sh
    for ch in range(3): o_[y, wl:X1, ch] = np.interp(xs, np.arange(n), seg[:, ch], left=np.nan)
    gw_old = wl - X0; gw_new = int(round(wl + sh)) - X0
    if y < 905 and gw_old >= 4:
        sx = np.linspace(0, gw_old - 1, gw_new)
        for ch in range(3): o_[y, X0:X0 + gw_new, ch] = np.interp(sx, np.arange(gw_old), c_[y, X0:X0 + gw_old, ch])
    o_[y] = np.where(np.isnan(o_[y]), stone_ if y < 912 else wat_, o_[y])
im = Image.fromarray(np.clip(o_, 0, 255).astype(np.uint8))

# (①' 집낙지의 찢긴 금 · 날리는 조각은 PIL 지그재그로 그렸다가 「찢는지 확실치 않다」(일치 검사 2회) → 구역 편집 B7 로 찢는 사건 자체를 그렸다)

# ── ② 빛깔 손질 — 여자의 빨간 원피스 → 청록(붉은 배지가 묻힌다 · L13c ㉚) · 두루마리 끈 빨강 → 갈색(빨간 리본 = 건넴 예약)
c = np.array(im).astype(int)
def recolor(box, cond, fn):
    x0, y0, x1, y1 = box; r_ = c[y0:y1, x0:x1]; mk = cond(r_)
    r_[mk] = fn(r_[mk])
redish = lambda r_: (r_[..., 0] > 150) & (r_[..., 1] < 110) & (r_[..., 2] < 120) & (r_[..., 0] - r_[..., 1] > 80)   # 진한 빨강만(살빛 · 입은 그대로)
def to_teal(p):
    lum = p.mean(axis=1, keepdims=True) / 255.0
    base = np.array([38, 170, 160]); return np.clip(base * (0.55 + 0.9 * lum), 0, 255).astype(int)
def to_brown(p):
    lum = p.mean(axis=1) / 255.0
    return np.stack([150 * (0.5 + lum), 100 * (0.5 + lum), 56 * (0.5 + lum)], axis=1).clip(0, 255).astype(int)
recolor((1780, 360, 1890, 560), redish, to_teal)
recolor((1290, 270, 1430, 370), lambda r_: (r_[..., 0] - np.maximum(r_[..., 1], r_[..., 2]) > 30) & (r_[..., 0] > 70), to_brown)
im = Image.fromarray(c.astype(np.uint8))

# ── ②' 세균을 샌드위치처럼 베어 문 경비 — 초록 덩이에 얼굴(겁먹은 눈 · 떨리는 입)을 그린다(일치 검사 4회: 「초록 샌드위치로는 읽히지만 세균으로 알아보이지 않는다」)
lay = layer(); d = ImageDraw.Draw(lay)
for ex, ey in ((1044.5, 875.5), (1056.5, 873.5)):
    disc(d, ex, ey, 3.6, (255, 255, 255, 255), 1.3)
    disc(d, ex + 0.6, ey + 0.7, 1.5, INK, 0)
line(d, [(1041.5, 869.5), (1047.5, 870.5)], 1.3); line(d, [(1054, 868), (1060, 867.5)], 1.3)          # 치켜 올라간 눈썹(겁)
line(d, [(1045, 886.5), (1048, 884.8), (1051, 886.5), (1054, 884.8), (1057, 886.2)], 1.4)          # 떨리는 입
put(lay)

# ── ③ 붉은 리본 배지 = 자기 — 성 안의 사람 · 경비 · 흰 덩이 모두(배지 없는 것 = 세균 · 보라 망토 · 주황 문어(효소) · 달팽이 · 튤립(성 밖의 다른 생물))
def badge_c(d, cx, cy, r):
    for sx in (-1, 1):
        d.polygon([((cx + sx * 0.15 * r) * S, (cy + 0.5 * r) * S), ((cx + sx * 0.95 * r) * S, (cy + 0.55 * r) * S), ((cx + sx * 0.7 * r) * S, (cy + 1.75 * r) * S)], fill=RED_D)
    disc(d, cx, cy, r, RED, max(1.2, r * 0.2))
    d.ellipse([(cx - 0.4 * r) * S, (cy - 0.4 * r) * S, (cx + 0.4 * r) * S, (cy + 0.4 * r) * S], fill=GOLD_C)
BADGES = [(300, 335, 8),                                   # 가시 박힌 주민
          (418, 683, 8), (827, 633, 10),                   # 호스에서 비집고 나오는 경비(가슴 — 모자에 달면 「모자 장식」) · 뚱보 경비(가슴의 회색 원판 위)
          (575, 893, 7.5), (790, 952, 7.5),                # 고름 웅덩이에 뻗은 경비 둘
          (1094, 941, 8),                                  # 세균을 베어 문 경비
          (975, 570, 8.5), (1176, 570, 8.5), (1420, 570, 8.5), (1226, 1020, 7),   # 큰 흰 덩이 셋(몸 왼쪽 위 — 발치에 달면 「땅에 떠 있다」 · 일치 검사 3 ~ 7회) · 작은 흰 덩이
          (1840, 418, 7.5), (1958, 356, 6.5)]              # 인터폰에 외치는 여자 · 창에 판자를 대는 이웃(등을 보인다 — 어깨께)
lay = layer(); d = ImageDraw.Draw(lay)
for cx, cy, r in BADGES: (badge if r >= 7 else badge_c)(d, cx, cy, r)
put(lay)

im.save(dst)
print('saved', dst)

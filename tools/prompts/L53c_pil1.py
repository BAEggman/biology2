#!/usr/bin/env python3
# L53c_pil1.py — 바탕(s1) 뒤의 PIL 손질. Gemini 에게는 창을 「비워」 그리게 하고, 세어야 하는 것 · 자리가 뜻인 것은 여기서 그린다.
#  ① 염소 곁의 덤 부호(+ · −) 지움  ② 펌프 오른쪽 아래의 누운 도장 머리 지움(왼쪽 아래 모서리를 거울로 옮김) + 떨어지는 붉은 도장 자국
#  ③ 심장 집 문 → 노란 반달 문  ④ 흰 덩어리 26 → 목을 묶은 흰 소금 자루(L53b 의 자루를 스프라이트로) · 갈색 덩어리 5 → 갈색 자루
#  ⑤ 큰 펌프 창: 유리 문짝 + 왼쪽 칸 소금 자루 셋 ↑ + 오른쪽 칸 칼 둘 ↓  ⑥ 회전문 넷: 놋쇠 굽은 벽 · 문짝 · 탄 손님 · 굴 속의 손님과 화살
#  ⑦ 아래 물을 깊을수록 짙게  ⑧ 굴의 위아래 끝을 물빛으로 풀기  ⑨ 펌프 위에 선 칼 · 달걀 같은 동전을 다시 · 아래 물의 칼을 더 빽빽이
# 차례: (E1 염소) → 이 파일.
import sys, math, cv2, numpy as np
from PIL import Image, ImageDraw
import os
src, dst = sys.argv[1], sys.argv[2]
SPR = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'L53c_spr')      # 스프라이트(L53c_sprites.py 로 떼어 냄)
im = cv2.imread(src)                                           # BGR
UP, DEEP, LUM = (231, 187, 117), (187, 111, 40), (243, 224, 188)      # BGR
INK = (22, 20, 18, 255)
# ① 염소 곁의 덤 부호
im[755:787, 830:860] = DEEP; im[762:784, 890:920] = DEEP
# ② 누운 도장 머리: 왼쪽 아래 모서리(108..174)를 거울로 옮겨 오른쪽 아래 모서리(556..622)를 되살림
im[745:815, 556:643] = im[745:815, 88:175][:, ::-1]
im[730:745, 580:643] = im[730:745, 88:151][:, ::-1]
# ③ 심장 집 문: 문 자리(1924..1974)를 왼쪽 통나무 벽 기둥으로 덮고 → 노란 반달 문은 아래에서 그림
for y in range(1040, 1120): im[y, 1922:1977] = np.median(im[y, 1896:1920].reshape(-1, 3), axis=0)      # 통나무 줄은 가로로 곧다 — 줄마다 왼쪽 벽 빛으로
# ⑨-가 펌프 윗면에 발을 딛고 선 칼(「반쯤 잘려 나온 칼」로 읽힘) · 민짜 타원 동전(「달걀」로 읽힘) 지움 — 아래에서 다시 그림
im[276:360, 429:457] = UP; im[826:879, 517:559] = DEEP
# ④ 덩어리 지우기(둘레에서 메움) — 흰 덩어리 · 갈색 덩어리
rgb = im[..., ::-1].astype(int); R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
white = ((R > 236) & (G > 236) & (B > 236)).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(white, 8)
lumps = [k for k in range(1, n) if 800 <= st[k, cv2.CC_STAT_AREA] <= 1200 and 28 <= st[k, cv2.CC_STAT_HEIGHT] <= 37 and 30 <= st[k, cv2.CC_STAT_WIDTH] <= 41]
brown = ((np.abs(R - 160) < 24) & (np.abs(G - 114) < 22) & (np.abs(B - 72) < 22)).astype(np.uint8); brown[:, :1100] = 0; brown[:, 1360:] = 0
nb, labb, stb, cenb = cv2.connectedComponentsWithStats(brown, 8)
blumps = [k for k in range(1, nb) if 500 <= stb[k, cv2.CC_STAT_AREA] <= 1000]
assert len(lumps) == 26 and len(blumps) == 5, (len(lumps), len(blumps))
place = []; ring_k = np.ones((13, 13), np.uint8)
def erase(core, up):
    """덩어리 하나를 물빛으로 메운다. 둘레가 온통 물이면 넉넉히(번진 테까지), 다른 물건에 걸쳤으면 바짝 — 걸친 구슬 · 굴은 아래에서 다시 그린다."""
    ys, xs = np.where(core > 0); cy = ys.mean(); wat = np.array(UP if cy < 446 else DEEP)
    def grown(k): return cv2.dilate(core, np.ones((k, k), np.uint8)) | np.roll(cv2.dilate(core, np.ones((k - 4, k - 4), np.uint8)), -up, axis=0)
    big = grown(27); big[:80] = 0                       # 수면선(y ≈ 70)은 아래에서 깨끗한 기둥(x = 300)을 옮겨 되살린다
    ring = (cv2.dilate(big, ring_k) > 0) & (big == 0); ring[:80] = False
    if ys.min() < 92:
        for y in range(58, 80): im[y, xs.min() - 16:xs.max() + 17] = im[y, 300]
    ok = (np.abs(im[ring].astype(int) - wat).sum(axis=1) < 26).mean()
    if ok > 0.985: im[big > 0] = wat
    else:
        g = grown(17); g[:80] = 0; im[g > 0] = wat; print('  걸친 덩어리', int(xs.mean()), int(cy), round(float(ok), 3))
for k in lumps:
    x, y, w, h = st[k, :4]; erase((lab == k).astype(np.uint8), 10); place.append(('sack', x + w / 2.0, y + h + 4))
for k in blumps:
    x, y, w, h = stb[k, :4]; erase(cv2.dilate((labb == k).astype(np.uint8), np.ones((3, 3), np.uint8)), 8); place.append(('bsack', x + w / 2.0, y + h + 5))
im[776:881, 1217:1270] = LUM                               # 둘째 문 아래 굴(갈색 덩어리가 걸쳤던 곳)을 굴 빛으로 되살림
# ⑦ 아래 물: 깊을수록 짙게(물빛 화소만 — 물건은 그대로)
a = im[..., ::-1].astype(np.float32); H0, W0 = a.shape[:2]
deep = np.array([40, 111, 187], np.float32); upw = np.array([117, 187, 231], np.float32); lumc = np.array([188, 224, 243], np.float32)
mid, tgt = np.array([40, 86, 136], np.float32), np.array([33, 46, 94], np.float32)
def water(y):
    if y < 700: return upw
    t = min(1.0, max(0.0, (y - 760) / (1144 - 760.0)))
    return deep + (mid - deep) * (t / 0.5) if t < 0.5 else mid + (tgt - mid) * ((t - 0.5) / 0.5)
dist = np.abs(a - deep).sum(axis=2); m = np.clip((70 - dist) / 40.0, 0, 1); m[:700] = 0
m = cv2.GaussianBlur(m, (0, 0), 1.2)
col = np.stack([water(y) for y in range(H0)])[:, None, :]
a = a * (1 - m[..., None]) + (a - deep + col) * m[..., None]
# ⑧ 굴의 위아래 끝을 물빛으로 풀기(각진 「덧댄 조각」으로 읽힘 — L53b 와 같은 손질)
def fade(x0, x1, y_end, top, n=46):
    for k in range(-6, n):
        y = y_end + k if top else y_end - k
        al = max(0.0, (k + 0.5) / n); row = a[y, x0:x1 + 1]; wat = water(y); v = lumc - wat; vv = float((v * v).sum())
        t = ((row - wat) * v).sum(axis=1) / vv; dd = np.sqrt((((row - wat) - t[:, None] * v) ** 2).sum(axis=1))
        mm = (dd < 46) & (t > 0.04) & (t < 1.4)
        tt = np.where(t > 0.6, 1.0, np.clip(t / 0.6, 0, 1))                 # 굴 안쪽은 줄마다 한 빛으로(가로 띠 무늬가 안 생기게)
        row[mm] = wat + (tt[mm, None] * al * al * (3 - 2 * al)) * v
        if k < 6:
            dk = (row[:, 2] > row[:, 0] + 40) & (np.abs(row - wat).sum(axis=1) < 110) & ~mm
            row[dk] = wat
for x0, x1 in ((1005, 1064), (1213, 1273), (1421, 1482), (1629, 1688)):
    fade(x0, x1, 300, True); fade(x0, x1, 880, False)
# 큰 펌프의 위 · 아래 트인 곳이 놋쇠 상자 밖으로 10 px 쯤 삐져나온 것(「덧댄 조각」으로 읽힘)을 상자 모서리에서 끊는다
a[340:362, 294:436] = upw
for y in range(780, 796): a[y, 294:436] = water(y)
pil = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); S = 4
# 덩어리가 걸쳤던 구슬을 다시 그림(구슬 자리 · 빛깔은 밑그림 공식 그대로 — Gemini 가 1 px 안으로 지켰다)
BEAD = [(228, 56, 56), (60, 158, 231), (250, 196, 40), (94, 190, 90), (169, 81, 198), (246, 134, 36)]
def ball(cx, cy, r_out, r_in, col):
    x0, y0 = int(cx - r_out - 3), int(cy - r_out - 3); W = H = int(2 * r_out + 6); lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ox, oy = (cx - x0) * S, (cy - y0) * S
    d.ellipse([ox - r_out * S, oy - r_out * S, ox + r_out * S, oy + r_out * S], fill=INK); d.ellipse([ox - r_in * S, oy - r_in * S, ox + r_in * S, oy + r_in * S], fill=col + (255,))
    lay = lay.resize((W, H), Image.LANCZOS); pil.paste(lay, (x0, y0), lay)
def poff(y): return 40 + 38 * math.exp(-((y - 570) / 120.0) ** 2)
for k in (15, 16, 17, 18): ball(1856, 330 + 28 * k, 15.8, 12.3, BEAD[k % 6])                    # 자물쇠 펌프 기둥(소금 자루 더미 뒤)
for i in (0, 17, 18, 19): ball(1243 - poff(300 + 28 * i), 300 + 28 * i, 15.8, 12.3, BEAD[i % 6])  # 둘째 문 왼쪽 줄(꼭대기 구슬 · 아래 셋)
for i in (18, 19, 20): ball(1243 + poff(300 + 28 * i), 300 + 28 * i, 15.8, 12.3, BEAD[(i + 3) % 6])   # 둘째 문 오른쪽 줄
# 스프라이트
def load(nm): return Image.open(f'{SPR}/{nm}.png').convert('RGBA')
sack, knife, lemon, pebble, grape_s = load('sack'), load('knife'), load('lemon'), load('pebble'), load('grape')
def tint_brown(sp):
    a = np.array(sp).astype(np.float32); rgbv = a[..., :3]; lum = rgbv.sum(axis=2)
    out = rgbv.copy(); bright = lum > 520; cord = (~bright) & (lum > 180)
    out[bright] = rgbv[bright] / 255.0 * np.array([176, 124, 74], np.float32)
    out[cord] = np.array([92, 60, 34], np.float32)
    a[..., :3] = out; return Image.fromarray(a.astype(np.uint8), 'RGBA')
bsack = tint_brown(sack)
SP = {'sack': sack, 'bsack': bsack, 'knife': knife, 'lemon': lemon, 'pebble': pebble, 'grape': grape_s}
def put(nm, cx, cy, scale=1.0, anchor='c', flip=False, rot=0):
    """anchor 'c' = 가운데 · 'b' = (cx, cy)가 물건의 아랫변 가운데."""
    sp = SP[nm]
    if flip: sp = sp.transpose(Image.FLIP_TOP_BOTTOM)
    w, h = max(2, round(sp.width * scale)), max(2, round(sp.height * scale)); sp = sp.resize((w, h), Image.LANCZOS)
    if rot: sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True); w, h = sp.size
    pad = 4 * scale
    x0 = round(cx - w / 2.0); y0 = round(cy - h + pad) if anchor == 'b' else round(cy - h / 2.0)
    pil.paste(sp, (x0, y0), sp)
for nm, cx, by in place:
    if nm == 'sack' and cx < 400 and by > 780: cx += 34; by -= 10            # 펌프 밑의 자루 셋: 트인 곳 바로 밑으로 다가서게
    if nm == 'sack' and by < 126: by += 16                                   # 수면선에 걸친 자루를 물속으로
    put(nm, cx, by, 1.12, 'b')
gb = ImageDraw.Draw(pil); gcol = pil.getpixel((985, 100))                      # 경구수액 컵 속의 작은 덩어리 → 작은 소금 자루
gb.rectangle([961, 112, 1000, 149], fill=gcol); put('sack', 983, 131, 0.6)
# 그리기 도우미
def paste_layer(lay, x0, y0, W, H):
    lay = lay.resize((W, H), Image.LANCZOS); pil.paste(lay, (x0, y0), lay)
def arrow(x, y0, y1, w=5.5, head=10):
    up = y1 < y0; top, bot = min(y0, y1), max(y0, y1); x0 = int(x - head - 5); W = int(2 * head + 10); H = int(bot - top + 8); yb = int(top - 4)
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def T(px, py): return ((px - x0) * S, (py - yb) * S)
    if up:
        d.line([T(x, bot), T(x, top + head)], fill=INK, width=int(w * S)); d.polygon([T(x, top), T(x - head, top + head * 1.4), T(x + head, top + head * 1.4)], fill=INK)
    else:
        d.line([T(x, top), T(x, bot - head)], fill=INK, width=int(w * S)); d.polygon([T(x, bot), T(x - head, bot - head * 1.4), T(x + head, bot - head * 1.4)], fill=INK)
    paste_layer(lay, x0, yb, W, H)
GLASS, GEDGE, GHI = (128, 190, 236, 255), (40, 70, 110, 255), (205, 232, 250, 255)
def panel(cx, cy, ang, r, w):
    R0 = int(r + 12); x0, y0 = int(cx - R0), int(cy - R0); W = H = 2 * R0
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def P(rr, a): return ((cx - x0 + rr * math.cos(math.radians(a))) * S, (cy - y0 + rr * math.sin(math.radians(a))) * S)
    for a in (ang, ang + 180):
        d.line([P(0, a), P(r, a)], fill=GEDGE, width=int((w + 4.4) * S)); d.line([P(0, a), P(r - 1.2, a)], fill=GLASS, width=int(w * S)); d.line([P(r * 0.2, a), P(r * 0.82, a)], fill=GHI, width=int(max(1.6, w * 0.22) * S))
    hub = max(6.0, w * 1.05); x, y = P(0, 0)
    d.ellipse([x - (hub + 3) * S, y - (hub + 3) * S, x + (hub + 3) * S, y + (hub + 3) * S], fill=INK); d.ellipse([x - hub * S, y - hub * S, x + hub * S, y + hub * S], fill=(214, 164, 52, 255))
    paste_layer(lay, x0, y0, W, H)
# ⑤ 큰 펌프 창(가운데 368, 569 · 반지름 159)
PX, PY = 368, 569
def door(cx, cy, hh, hw):
    """세로로 선 유리 문짝(위아래 놋쇠 마구리 · 가운데 축)."""
    x0, y0 = int(cx - hw - 12), int(cy - hh - 12); W, H = int(2 * hw + 24), int(2 * hh + 24)
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def T(px, py): return ((px - x0) * S, (py - y0) * S)
    d.rectangle([T(cx - hw - 3.2, cy - hh), T(cx + hw + 3.2, cy + hh)], fill=GEDGE); d.rectangle([T(cx - hw, cy - hh + 3.2), T(cx + hw, cy + hh - 3.2)], fill=GLASS)
    d.line([T(cx - hw * 0.45, cy - hh + 14), T(cx - hw * 0.45, cy - 22)], fill=GHI, width=int(3 * S)); d.line([T(cx - hw * 0.45, cy + 22), T(cx - hw * 0.45, cy + hh - 40)], fill=GHI, width=int(3 * S))
    for yy in (cy - hh, cy + hh):
        d.rectangle([T(cx - hw - 6, yy - 7), T(cx + hw + 6, yy + 7)], fill=INK); d.rectangle([T(cx - hw - 3, yy - 4), T(cx + hw + 3, yy + 4)], fill=(214, 164, 52, 255))
    x, y = T(cx, cy); r = 16 * S; d.ellipse([x - r, y - r, x + r, y + r], fill=INK); r = 12.5 * S; d.ellipse([x - r, y - r, x + r, y + r], fill=(214, 164, 52, 255))
    r = 4 * S; d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 104, 24, 255))
    paste_layer(lay, x0, y0, W, H)
bd0 = ImageDraw.Draw(pil)
for xx in (300, 428):
    bd0.line([(xx, 362), (xx, 432)], fill=(22, 20, 18), width=4); bd0.line([(xx, 706), (xx, 778)], fill=(22, 20, 18), width=4)
door(PX, PY, 146, 12)                                                         # 세로로 선 유리 문짝
for cx, cy in [(290, 476), (262, 572), (290, 668)]: put('sack', cx, cy, 1.28)          # 왼쪽 칸: 흰 소금 자루 셋
arrow(332, 660, 486, 7, 13)                                                   # ↑ 밖으로
for cx, cy in [(462, 506), (462, 634)]: put('knife', cx, cy, 1.2, flip=True)           # 오른쪽 칸: 칼 둘(날을 아래로)
arrow(408, 486, 660, 7, 13)                                                   # ↓ 안으로
# ⑨-나 펌프 위 물의 칼(다시) · 아래 물의 칼 넷 더 · 금 동전(테 있는 동전으로)
put('knife', 443, 312, 1.0, flip=True)
for cx, cy, rot in [(662, 938, -12), (352, 1012, 10), (566, 1076, -8), (704, 1046, 6)]: put('knife', cx, cy, 1.0, rot=rot)
def coin(cx, cy, rx, ry):
    x0, y0 = int(cx - rx - 6), int(cy - ry - 6); W, H = int(2 * rx + 12), int(2 * ry + 12); lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ox, oy = (cx - x0) * S, (cy - y0) * S
    d.ellipse([ox - (rx + 3.2) * S, oy - (ry + 3.2) * S, ox + (rx + 3.2) * S, oy + (ry + 3.2) * S], fill=INK)
    d.ellipse([ox - rx * S, oy - ry * S, ox + rx * S, oy + ry * S], fill=(244, 190, 44, 255))
    d.ellipse([ox - (rx - 3.6) * S, oy - (ry - 3.6) * S, ox + (rx - 3.6) * S, oy + (ry - 3.6) * S], outline=(196, 138, 20, 255), width=int(2.4 * S))
    d.arc([ox - (rx - 1.5) * S, oy - (ry - 1.5) * S, ox + (rx - 1.5) * S, oy + (ry - 1.5) * S], 200, 255, fill=(254, 226, 130, 255), width=int(2.6 * S))
    paste_layer(lay, x0, y0, W, H)
coin(538, 852, 15, 21)
# ② 떨어지는 붉은 도장 자국(펌프 오른쪽 아래 모서리 밖)
lay = Image.new('RGBA', (90 * S, 110 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); ox, oy = 596, 752
for ax, ay, bx, by in [(606, 762, 614, 786), (622, 758, 628, 780), (640, 764, 642, 782)]: d.line([((ax - ox) * S, (ay - oy) * S), ((bx - ox) * S, (by - oy) * S)], fill=INK, width=int(3 * S))
mk = Image.new('RGBA', (60 * S, 46 * S), (0, 0, 0, 0)); md = ImageDraw.Draw(mk)
md.ellipse([8 * S, 9 * S, 52 * S, 37 * S], fill=(214, 50, 42, 255))
for k in range(18):                                                            # 번진 점선 테(벗겨진 자국 — 놋쇠 면의 흐린 자국과 같은 꼴)
    an = math.radians(k * 20); px, py = 30 + 25.5 * math.cos(an), 23 + 17.5 * math.sin(an)
    md.ellipse([(px - 3.2) * S, (py - 2.4) * S, (px + 3.2) * S, (py + 2.4) * S], fill=(238, 120, 84, 255))
mk = mk.rotate(24, resample=Image.BICUBIC, expand=True)
lay.paste(mk, (int((630 - ox) * S - mk.width / 2), int((820 - oy) * S - mk.height / 2)), mk)
paste_layer(lay, ox, oy, 90, 110)
# ③ 노란 반달 문(심장 집 — L46 의 나무집)
lay = Image.new('RGBA', (80 * S, 50 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); ox, oy = 1909, 1070
d.pieslice([(8) * S, (6) * S, (72) * S, (70) * S], 180, 360, fill=INK); d.pieslice([(12) * S, (10) * S, (68) * S, (66) * S], 180, 360, fill=(250, 208, 52, 255))
d.rectangle([8 * S, 38 * S, 72 * S, 42 * S], fill=INK)
paste_layer(lay, ox, oy + 2, 80, 50)
# ⑥ 회전문 넷(가운데 y = 570)
def walls(cx, cy, k=0.84, G=19):
    bd = ImageDraw.Draw(pil); shaft = (188, 224, 243)
    bd.ellipse([cx - 60 * k, cy - 60 * k, cx + 60 * k, cy + 60 * k], fill=shaft)           # 옛 괄호 · 창 속을 굴 빛으로
    R0 = int(76 * k) + 4; x0, y0 = cx - R0, cy - R0; W = H = 2 * R0
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def band(r1, r0, a0, a1, col): d.arc([(R0 - r1) * S, (R0 - r1) * S, (R0 + r1) * S, (R0 + r1) * S], a0, a1, fill=col, width=int((r1 - r0) * S))
    for a0, a1 in ((270 + G, 90 - G), (90 + G, 270 - G)):
        band(73 * k, 56.5 * k, a0, a1, INK); band(70.2 * k, 59.3 * k, a0 + 2.6, a1 - 2.6, (214, 164, 52, 255)); band(67.2 * k, 63.4 * k, a0 + 2.6, a1 - 2.6, (240, 200, 96, 255))
    paste_layer(lay, x0, y0, W, H)
def purple(cx, cy, r):
    x0, y0 = int(cx - r - 5), int(cy - r - 5); W = H = int(2 * r + 10); lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); ox, oy = (cx - x0) * S, (cy - y0) * S
    d.ellipse([ox - (r + 2.8) * S, oy - (r + 2.8) * S, ox + (r + 2.8) * S, oy + (r + 2.8) * S], fill=INK); d.ellipse([ox - r * S, oy - r * S, ox + r * S, oy + r * S], fill=(128, 62, 166, 255))
    d.ellipse([ox - r * 0.55 * S, oy - r * 0.62 * S, ox - r * 0.1 * S, oy - r * 0.22 * S], fill=(176, 120, 206, 255))
    paste_layer(lay, x0, y0, W, H)
D1, D2, D3, D4 = 1035, 1243, 1451, 1659; CY = 570
for cx in (D1, D2, D3, D4): walls(cx, CY)
# D1 짝 손님(흰 소금 자루 + 포도): 굴 위쪽에 나란히 · 문짝 위에 나란히 타고 · 아래로 ↓↓
put('sack', D1 - 20, 468, 0.74); purple(D1 + 20, 470, 15)
panel(D1, CY, -38, 45, 8); put('sack', D1 + 27, CY + 5, 0.6); purple(D1 - 1, CY + 28, 12.5)
arrow(D1 - 18, 644, 694, 5.5, 9.5); arrow(D1 + 18, 644, 694, 5.5, 9.5)
for gx, gy in [(1122, 868), (1104, 986)]: put('grape', gx, gy, 1.0)                    # 첫 문 아래 물의 포도를 또렷이 둘 더(구슬 줄에 걸친 둘은 구슬로 읽힌다)
# D2 짝 손님(레몬 + 갈색 자루)
put('lemon', D2 - 20, 470, 0.62); put('bsack', D2 + 20, 468, 0.74)
panel(D2, CY, -38, 45, 8); put('bsack', D2 + 27, CY + 5, 0.6); put('lemon', D2 - 2, CY + 29, 0.52)
arrow(D2 - 18, 644, 694, 5.5, 9.5); arrow(D2 + 18, 644, 694, 5.5, 9.5)
# D3 혼자(포도)
purple(D3, 470, 16)
panel(D3, CY, -38, 45, 8); purple(D3 + 18, CY + 19, 14.5)
arrow(D3, 644, 694, 5.5, 9.5)
# D4 맞바꿈(왼쪽 줄 흰 소금 자루 ↓ · 오른쪽 줄 자갈 ↑)
put('sack', D4 - 20, 468, 0.74); put('pebble', D4 + 20, 472, 0.86)
panel(D4, CY, 90, 45, 8); put('sack', D4 - 25, CY, 0.6); put('pebble', D4 + 25, CY, 0.74)
arrow(D4 - 18, 644, 694, 5.5, 9.5); arrow(D4 + 18, 694, 644, 5.5, 9.5)
pil.save(dst); print('ok', len(lumps), len(blumps))

#!/usr/bin/env python3
# L13b_pil.py <조각 폴더(gem_*.png)> <out.png> — L13b 「안뜰의 싸움」 조립(세계 s13 의 b · 같은 성).
#  ① 하늘 · 회색 돌 성벽 · 틈 = s13_lib.castle_wall()(L13a 와 같은 성벽 · 같은 틈).
#  ② 물건은 조각 그림에서 오려 세운다 — L13a 의 인물(흰 덩이 · 파리채 경비 · 주민 · 집 · 망토 침입자 · 도랑 · 세균)은
#     L13a 조각을 Gemini 에 올려 「같은 인물을 이렇게」로 다시 그리게 했다(U1 ~ U10 · 프롬프트 = L13b_prompt_sprites.txt).
#  ③ PIL: 진홍 호스(혈관 — 조각 둘 사이를 잇는다) · 보의 물줄기 셋 · 인터폰 줄 · 확성기 전선 · 성냥 둘 더 · 붉은 리본 배지(성 안의 모두) · 그림자.
#  자리: 위 줄(발끝 ≤ 690) = 흰 덩이 셋(식세포작용) · 틈의 돌 + 가시 박힌 주민(염증 4징후) · [빈 틈 = 호스에서 비집고 나오는 경비] · 감염된 집 단면 + 인터폰에 외치는 주민 + 이웃 집.
#        가운데 = 가로지르는 진홍 호스(중심 y 762) — 부푼 자리(뚱보 경비의 성냥 위) · 경비가 비집고 나오는 자리.
#        아래 줄 = 달팽이 · 튤립 화분(디펜신) · 세균을 베어 문 경비 · 고름 웅덩이 · 뚱보 경비 · 작은 흰 덩이 · 구멍 난 세균 · 도랑 셋 → 저수지(보).
import sys, os, math, numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s13_lib import *
zdir, dst = sys.argv[1:3]
cv = Canvas(zdir)
cv.castle_wall()

A2G = np.array([94, 183, 76])          # L13a 마당 세균(A2)의 초록(G 가 R · B 보다 22 넘게 큰 화소의 가운데값)
def regreen(c, box, tgt=A2G):
    """상자 안의 초록(세균)을 L13a 세균의 초록으로 — Gemini 가 따라 그린 세균은 회녹 · 올리브로 바랬다."""
    r = c[box[1]:box[3], box[0]:box[2]]; R_, G_, B_ = r[..., 0], r[..., 1], r[..., 2]
    m = (G_ - np.maximum(R_, B_) > 22)
    if m.sum() == 0: return c
    med = np.median(r[m], axis=0)
    r[m] = np.clip(r[m] + (tgt - med), 0, 255).astype(int)
    return c
def regreen_many(c, boxes):
    for b in boxes: c = regreen(c, b)
    return c
def crop_x(sp, x0, x1, feather=0, rows=None):
    """조각을 조각 그림 좌표 x0 ~ x1 만 남긴다(호스 토막의 잘린 끝 마개를 떼어 PIL 호스와 잇는다).
    feather = 잘린 두 끝을 그 폭만큼 서서히 투명하게(rows = 그 일을 할 조각 그림 y 범위 — 호스 줄만)."""
    ox, oy = sp.origin
    s2 = sp.crop((x0 - ox, 0, x1 - ox, sp.height))
    if feather:
        a = np.array(s2); n = feather
        ya, yb = (0, a.shape[0]) if rows is None else (max(0, rows[0] - oy), min(a.shape[0], rows[1] - oy))
        ramp = np.linspace(0.0, 1.0, n)
        a[ya:yb, :n, 3] = (a[ya:yb, :n, 3] * ramp[None, :]).astype(np.uint8)
        a[ya:yb, -n:, 3] = (a[ya:yb, -n:, 3] * ramp[None, ::-1]).astype(np.uint8)
        s2 = Image.fromarray(a, 'RGBA')
    s2.origin = (x0, oy)
    return s2
def clear(sp, boxes):
    """조각 그림 좌표 상자들을 투명하게(떼어 낼 것: 인터폰에 걸린 수화기 · 사람이 든 수화기의 늘어진 줄)."""
    a = np.array(sp); ox, oy = sp.origin
    for x0, y0, x1, y1 in boxes: a[max(0, y0 - oy):max(0, y1 - oy), max(0, x0 - ox):max(0, x1 - ox), 3] = 0
    s2 = Image.fromarray(a, 'RGBA'); s2.origin = sp.origin
    return s2

def fan_matches(sp, box, pivot, angles, pad=70):
    """뚱보 경비의 성냥을 한 움큼으로 — 조각의 성냥(box: 불꽃 + 주먹 위 막대)을 주먹(pivot)을 축으로 돌린 사본을 원본 뒤에 깐다."""
    ox, oy = sp.origin
    big = Image.new('RGBA', (sp.width + pad, sp.height + pad), (0, 0, 0, 0))
    crop = sp.crop((box[0] - ox, box[1] - oy, box[2] - ox, box[3] - oy))
    for ang in angles:
        tmp = Image.new('RGBA', big.size, (0, 0, 0, 0)); tmp.alpha_composite(crop, (box[0] - ox, box[1] - oy + pad))
        big.alpha_composite(tmp.rotate(ang, resample=Image.BICUBIC, center=(pivot[0] - ox, pivot[1] - oy + pad)))
    big.alpha_composite(sp, (0, pad))
    big.origin = (ox, oy - pad)
    return big

def snap(sp, pairs):
    """조각의 빛깔을 PIL 의 것으로 맞춘다(호스 토막 — 이음매에서 빛깔이 튀지 않게): pairs = [(조각 빛, 허용, PIL 빛)]."""
    a = np.array(sp).astype(int)
    for src, tol, dst in pairs:
        m = (np.abs(a[..., :3] - np.array(src)).max(axis=2) <= tol) & (a[..., 3] > 0)
        a[m, :3] = dst[:3]
    s2 = Image.fromarray(a.astype(np.uint8), 'RGBA'); s2.origin = sp.origin
    return s2
def thin(sp, it=1, dark=80):
    """선 가늘이기 — 검은 선의 안쪽 가장자리 화소를 곁의 가장 밝은 불투명 화소 빛으로(크게 그려 줄인 조각의 선이 다른 조각보다 굵어 화풍이 튀었다 — 일치 검사 1회)."""
    a = np.array(sp).astype(np.int32); rgb = a[..., :3].copy(); al = a[..., 3]
    for _ in range(it):
        lum = rgb.sum(axis=2) * (al > 128); best = lum.copy(); col = rgb.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                sl = np.roll(np.roll(lum, dy, 0), dx, 1); sc = np.roll(np.roll(rgb, dy, 0), dx, 1)
                m = sl > best; best = np.where(m, sl, best); col = np.where(m[..., None], sc, col)
        dk = (rgb.max(axis=2) < dark) & (al > 128) & (best > 360)
        rgb = np.where(dk[..., None], col, rgb)
    a[..., :3] = rgb
    s2 = Image.fromarray(a.astype(np.uint8), 'RGBA'); s2.origin = sp.origin
    return s2
def splinter(sp):
    """가시 박힌 손가락: Gemini 의 가시가 깎은 연필 꼴(굵은 막대 + 원뿔 끝 + 심)이라 「연필 · 막대」로 읽혔다(일치 검사 1 · 4회)
    → 손가락 밖의 막대는 떼고(투명) · 손가락 안의 막대 자리는 손가락 빛으로 메우고(inpaint) · 손끝에서 가늘게 뾰족해지는 나뭇조각 가시를 새로 그린다."""
    a = np.array(sp).astype(np.uint8).copy(); ox, oy = sp.origin
    A0 = np.array([662.0, 220.0]); u = np.array([0.897, -0.443]); v = np.array([0.443, 0.897])
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]; P = np.dstack([xx + ox, yy + oy]).astype(float) - A0
    t = P[..., 0] * u[0] + P[..., 1] * u[1]; nn = P[..., 0] * v[0] + P[..., 1] * v[1]
    band = (np.abs(nn) <= 9.5) & (t >= -9)
    a[band & (t > 31), 3] = 0                                                # 손가락 밖: 떼어 낸다
    rgb = a[..., :3].astype(int); red = (rgb[..., 0] > 170) & (rgb[..., 0] - rgb[..., 1] > 60)
    hole = (band & (t <= 31) & ~red).astype(np.uint8) * 255                   # 손가락 안의 막대(나무 · 검은 테)
    a[..., :3] = cv2.inpaint(np.ascontiguousarray(a[..., :3]), hole, 5, cv2.INPAINT_TELEA)
    im = Image.fromarray(a, 'RGBA'); big = im.resize((im.width * S, im.height * S), Image.LANCZOS); d = ImageDraw.Draw(big)
    def q(tt, n_): x, y = A0 + tt * u + n_ * v; return ((x - ox) * S, (y - oy) * S)
    out = [q(18, -4.2), q(44, -2.6), q(52, -3.4), q(76, 0.0), q(50, 1.2), q(40, 2.8), q(18, 4.2)]
    d.polygon(out, fill=(206, 152, 92, 255)); d.line(out + [out[0]], fill=INK, width=int(2.4 * S), joint='curve')
    d.line([q(22, -0.6), q(46, -0.4)], fill=(140, 92, 50, 255), width=int(1.2 * S))
    d.ellipse([q(18, 0)[0] - 4.6 * S, q(18, 0)[1] - 5.6 * S, q(18, 0)[0] + 4.6 * S, q(18, 0)[1] + 5.6 * S], outline=(150, 30, 30, 255), width=int(1.6 * S))
    s2 = big.resize((im.width, im.height), Image.LANCZOS); s2.origin = sp.origin
    return s2
def pus_tint(c, box, d=(-20, -6, 12)):
    """고름 웅덩이 빛: 노른자 · 기름처럼 읽혔다(일치 검사 1회) → 누르스름한 크림빛(초록 기 · 덜 진하게)."""
    r = c[box[1]:box[3], box[0]:box[2]]; R_, G_, B_ = r[..., 0], r[..., 1], r[..., 2]
    m = (R_ > 215) & (G_ > 195) & (R_ - B_ > 40)
    r[m] = np.clip(r[m] + np.array(d), 0, 255)
    return c

def thicken(sp, dark=80):
    """선 굵히기 — 검은 선 곁(네 이웃)의 밝은 불투명 화소를 그 검은 빛으로(줄여 붙인 조각의 선이 가늘어 화풍이 튀었다 — 일치 검사 2회)."""
    a = np.array(sp).astype(np.int32); rgb = a[..., :3].copy(); al = a[..., 3]
    dk = (rgb.max(axis=2) < dark) & (al > 128); col = rgb.copy(); hit = np.zeros(dk.shape, bool)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nd = np.roll(np.roll(dk, dy, 0), dx, 1); nc = np.roll(np.roll(rgb, dy, 0), dx, 1)
        m = nd & ~dk & (al > 128) & ~hit; col[m] = nc[m]; hit |= m
    a[..., :3] = np.where(hit[..., None], col, rgb)
    s2 = Image.fromarray(a.astype(np.uint8), 'RGBA'); s2.origin = sp.origin
    return s2
def hole_wall(sp, shift=(4, 5), col=(56, 124, 44)):
    """구멍 난 세균: 뚫린 구멍(갇힌 투명 덩이)의 위 · 왼쪽 안벽을 짙은 초록 초승달로 — 바탕빛만 비치면 「칠한 점」으로 읽혔다(일치 검사 2회)."""
    a = np.array(sp); al = a[..., 3]
    tr = (al < 128).astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(tr, 4)
    H = np.zeros(al.shape, bool)
    for i in range(1, n):
        x, y, w, h, ar = st[i]
        if ar > 50 and x > 5 and y > 5 and x + w < al.shape[1] - 5 and y + h < al.shape[0] - 5: H |= (lab == i)
    Hs = np.zeros_like(H); dx, dy = shift; Hs[dy:, dx:] = H[:-dy, :-dx]
    cr = H & ~Hs
    a[cr, 0], a[cr, 1], a[cr, 2], a[cr, 3] = col[0], col[1], col[2], 255
    s2 = Image.fromarray(a, 'RGBA'); s2.origin = sp.origin
    return s2

# ── 조각
SPR = {}
SPR['BLOB1'] = cv.comp_sprite('U1', (30, 140, 345, 440))
SPR['BLOB2'] = cv.comp_sprite('U1', (360, 140, 665, 440))
SPR['BLOB3'] = cv.comp_sprite('U1', (690, 140, 995, 440))
SPR['STONES'] = cv.comp_sprite('E1', (525, 250, 955, 525), holes=True, fix=lambda c: inpaint(c, [(744, 380, 812, 400), (549, 446, 610, 474)]))
SPR['MAN'] = splinter(cv.comp_sprite('U4B', (380, 40, 740, 530)))
SPR['HOUSE'] = thin(clear(cv.comp_sprite('U5', (240, 30, 800, 535)), [(739, 250, 790, 450)]))      # 옆벽에 옆모습으로 걸린 인터폰(함 · 수화기 · 줄)은 떼고 L13a 꼴의 인터폰 판을 PIL 로 앞모습으로
SPR['CALLER'] = thin(clear(crop_x(cv.comp_sprite('U6', (655, 75, 980, 545)), 776, 975), [(776, 281, 795, 545)]))
SPR['NBR'] = cv.comp_sprite('U6', (20, 40, 600, 545))      # 이웃 집은 작게 줄여 붙여 선을 가늘이지 않는다(가늘이니 「선이 가늘고 색이 옅다」 — 일치 검사 9회)
HOSE_SNAP = [((196, 53, 80), 26, (196, 53, 80)), ((233, 117, 132), 22, (233, 117, 132))]
SPR['SWELL'] = snap(crop_x(cv.comp_sprite('U7', (50, 200, 480, 440)), 104, 420, 28, (240, 380)), HOSE_SNAP)
SPR['SQZ'] = snap(crop_x(cv.comp_sprite('U7', (545, 55, 975, 425)), 600, 926, 28, (296, 425)), HOSE_SNAP)
SPR['FAT'] = fan_matches(cv.comp_sprite('U3', (250, 30, 780, 540), fix=lambda c: regreen(c, (255, 200, 350, 340))), (612, 36, 712, 188), (703, 215), (-24, -48))
SPR['EATER'] = cv.comp_sprite('U2', (50, 80, 515, 520), holes=[(60, 150, 160, 280)], fix=lambda c: regreen(c, (270, 180, 450, 300)))
SPR['SMALL'] = cv.comp_sprite('U2', (620, 190, 945, 460), fix=lambda c: regreen(c, (625, 195, 760, 340)))
SPR['PUS'] = cv.comp_sprite('U8', (430, 250, 2320, 1280), fix=lambda c: pus_tint(regreen_many(c, [(560, 760, 720, 905), (895, 960, 1065, 1120), (1715, 960, 1870, 1120), (2065, 760, 2210, 905)]), (430, 250, 2320, 1280)))
SPR['POND'] = thicken(cv.comp_sprite('U9', (30, 85, 575, 475)))
SPR['HOLED'] = hole_wall(cv.comp_sprite('U9', (660, 140, 940, 470), holes=True, fix=lambda c: regreen(c, (680, 140, 920, 465))))
SPR['SNAIL'] = cv.comp_sprite('U10', (50, 215, 500, 460), fix=lambda c: regreen(c, (310, 215, 500, 460)))
SPR['TULIP'] = cv.comp_sprite('U10', (565, 60, 955, 480), fix=lambda c: regreen(c, (570, 240, 740, 480)))

# ── 호스(혈관): 가운데 y · 굵기
HY, HD = 762, 56
HTOP = HY - HD / 2
HOSE, HOSE_HI = (196, 53, 80, 255), (233, 117, 132, 255)
def hose_y_bottom(sp, y_top_sprite, s):
    """호스 토막 조각을 호스 위끝(조각 그림의 y_top_sprite)이 HTOP 에 오게 놓을 때의 발끝(조각 아래끝) y."""
    return HTOP + (sp.origin[1] + sp.height - y_top_sprite) * s
S_SW, S_SQ = HD / 115, HD / 110        # 부푼 토막의 양 끝 굵기 115 · 비집는 토막 110(조각 그림 화소)
X_SW, X_SQ = 1180, 930                 # 부푼 토막 · 비집는 토막의 가운데 x

# ── 놓을 자리: (키, 배율, 가운데 x, 발끝 y, 뒤집기, 그림자 반폭)
PL = []
PL += [('STONES', 0.40, 626, 508, False, 0), ('STONES', 0.26, 886, 476, True, 0)]
PL += [('BLOB1', 0.56, 100, 612, False, 70), ('BLOB2', 0.56, 290, 612, False, 70), ('BLOB3', 0.56, 480, 612, False, 70)]
PL += [('MAN', 0.50, 760, 690, False, 70)]
PL += [('HOUSE', 0.72, 1345, 676, False, 0), ('CALLER', 0.47, 1622, 690, False, 40), ('NBR', 0.58, 1885, 690, True, 0)]
# 뚱보 경비(뒤집어 왼쪽을 본다 — 성냥은 저수지 반대쪽): 성냥불 가운데(조각 x 658)가 부푼 토막 가운데 아래 · 불꽃 위끝(조각 y 40)이 호스 아래 36
#  물줄기가 성냥 든 주먹 곁으로 내려와 「물이 불로 간다」로 읽혔다(일치 검사 10회) → 성냥을 저수지에서 먼 쪽으로.
FAT_S = 0.50
fat = SPR['FAT']; fw = fat.width * FAT_S; fx0 = X_SW - fw + (658 - fat.origin[0]) * FAT_S
PL += [('FAT', FAT_S, fx0 + fw / 2, HY + HD / 2 + 36 + (fat.origin[1] + fat.height - 40) * FAT_S, True, 80)]   # 불꽃 끝은 호스 아래 36 — 새는 물방울이 불에 닿지 않게(물 = 끄는 것으로 읽히지 않게)
PL += [('PUS', 0.19, 752, 1046, False, 0), ('EATER', 0.44, 480, 1064, False, 80)]
PL += [('SNAIL', 0.50, 112, 1104, False, 0), ('TULIP', 0.48, 302, 1112, False, 0)]
PL += [('POND', 0.66, 2048 - SPR['POND'].width * 0.66 / 2, 1071, True, 0)]
PL += [('SMALL', 0.52, 1556, 1134, True, 55), ('HOLED', 0.54, 1934, 1144, False, 0)]
PL = [p for p in PL if p[0] in SPR]

lay = cv.layer(); d = ImageDraw.Draw(lay)
for k, sc, cx, bot, fl, sh in PL:
    if sh: ellipse(d, cx, bot - 4, sh, max(7, sh * 0.11), SHADOW)
cv.put(lay)
TF = {}
def put(k, sc, cx, bot, fl):
    TF[k if k not in TF else k + '2'] = cv.place(SPR[k], sc, cx, bot, fl)
for k, sc, cx, bot, fl, sh in PL:
    if k in ('FAT', 'HOLED'): continue          # 뚱보 경비는 호스를 그린 뒤(호스 앞에 선다) · 구멍 난 세균은 셋째 물줄기 뒤에(구멍으로 물줄기가 비친다) · 물줄기 첫째 · 둘째는 모든 조각 위에
    put(k, sc, cx, bot, fl)

# ── 진홍 호스(PIL) — 화면을 가로질러 · 토막 둘은 그 위에
lay = cv.layer(); d = ImageDraw.Draw(lay)
ow = 2.4
d.rectangle([-10 * S, (HTOP) * S, (W + 10) * S, (HTOP + HD) * S], fill=INK)
d.rectangle([-10 * S, (HTOP + ow) * S, (W + 10) * S, (HTOP + HD - ow) * S], fill=HOSE)
d.rectangle([-10 * S, (HTOP + 5.6) * S, (W + 10) * S, (HTOP + 10.2) * S], fill=HOSE_HI)
cv.put(lay)
sw, sq = SPR['SWELL'], SPR['SQZ']
TF['SWELL'] = cv.place(sw, S_SW, X_SW, hose_y_bottom(sw, 252, S_SW))
TF['SQZ'] = cv.place(sq, S_SQ, X_SQ, hose_y_bottom(sq, 307, S_SQ))
for k, sc, cx, bot, fl, sh in PL:
    if k == 'FAT': put(k, sc, cx, bot, fl)

# ── 보의 물줄기 셋(PIL) — 보 윗머리에서: 뚱보 경비 · 작은 흰 덩이가 든 세균 · 구멍 난 세균(그 셋은 물줄기 뒤에 붙인다)
WATER, WATER_HI = (52, 178, 232, 255), (214, 242, 254, 255)
def qbez(p0, p1, p2, n=60):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]
def normals(pts):
    out = []
    for i in range(len(pts)):
        j, k = min(i + 1, len(pts) - 1), max(i - 1, 0)
        tx, ty = pts[j][0] - pts[k][0], pts[j][1] - pts[k][1]; nn = math.hypot(tx, ty) or 1
        out.append((tx / nn, ty / nn, -ty / nn, tx / nn))
    return out
WOUT = (20, 96, 160, 255)              # 물의 테두리는 짙은 파랑(검은 테두리 물줄기는 「파란 관 · 호스」로 읽혔다 — 일치 검사 1 · 2회)
def poly_c(d, pts, fill, w, col=WOUT):
    q = T(pts); d.polygon(q, fill=fill); d.line(q + [q[0]], fill=col, width=max(1, int(w * S)), joint='curve')
def blob_drop(d, x, y, tx, ty, ln, wd):
    """물줄기 방향(tx, ty)으로 길쭉한 물방울 하나."""
    pts = []
    for k in range(16):
        a = 2 * math.pi * k / 16; u, v = math.cos(a) * ln / 2, math.sin(a) * wd / 2
        pts.append((x + u * tx - v * ty, y + u * ty + v * tx))
    poly_c(d, pts, WATER, 1.3)
def drop_c(d, x, y, r): poly_c(d, [(x + r * math.cos(a), y + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)], WATER, 1.2)
def jet(d, p0, p1, p2, w0, cont=0.7, splash=5, sr=12, side_drops=(), wob=0.0, nd=4, spread=85):
    """물줄기(일치 검사 1 ~ 5회: 고른 굵기 · 매끈한 테의 줄기는 「파란 관 · 호스 · 화살」로 읽혔다):
    보에서 나와 cont 까지는 양쪽 테가 따로 출렁이는 한 줄기 → 그 뒤로는 점점 작아지는 길쭉한 물방울 nd 개가 목표까지 이어지고(마지막 방울이 목표에 닿는다) → 닿은 자리에서 뒤로 튀는 물방울 splash 개."""
    pts = qbez(p0, p1, p2, 120); nm = normals(pts); n = len(pts); m = max(2, int(round((n - 1) * cont)) + 1)
    def wid(i, side):
        t = i / (n - 1)
        return w0 * (1 - 0.35 * t) * (1 + 0.22 * math.sin(2 * math.pi * 7.0 * t + wob + side * 1.9) + 0.08 * math.sin(2 * math.pi * 13 * t + side)) / 2
    L, R = [], []
    for i in range(m):
        (x, y), (tx, ty, nx, ny) = pts[i], nm[i]
        a_, b_ = wid(i, 0), wid(i, 1)
        L.append((x + nx * a_, y + ny * a_)); R.append((x - nx * b_, y - ny * b_))
    k0 = max(1, int(m * 0.86)) if cont < 1 else m                              # 끊기는 자리에서는 가늘어져 뾰족하게(뭉툭한 끝은 「잘린 관」으로 읽혔다 — 일치 검사 8회) · 끝까지 닿는 줄기는 끝이 퍼진다
    for i in range(k0, m):
        f = 1 - (i - k0) / max(1, m - 1 - k0) * 0.92
        (x, y), (tx, ty, nx, ny) = pts[i], nm[i]; a_, b_ = wid(i, 0) * f, wid(i, 1) * f
        L[i] = (x + nx * a_, y + ny * a_); R[i] = (x - nx * b_, y - ny * b_)
    (x, y), (tx, ty, nx, ny) = pts[m - 1], nm[m - 1]
    if cont < 1: tip = [(x + tx * 6, y + ty * 6)]
    else:
        we = (wid(m - 1, 0) + wid(m - 1, 1)) / 2 * 1.25
        tip = [(x + (nx * math.cos(a) + tx * math.sin(a) * 0.7) * we, y + (ny * math.cos(a) + ty * math.sin(a) * 0.7) * we) for a in np.linspace(0, math.pi, 9)]
    poly_c(d, L + tip + R[::-1], WATER, 1.2)
    hl = []
    for i in range(6, m - 8):
        (x, y), (tx, ty, nx, ny) = pts[i], nm[i]; w = wid(i, 0) * 0.45; sgn = -1 if ny > 0 else 1
        hl.append((x + sgn * nx * w, y + sgn * ny * w))
    if len(hl) > 1:
        k3 = len(hl) // 3
        for seg in (hl[:k3], hl[k3 + 5:2 * k3], hl[2 * k3 + 5:]):
            if len(seg) > 1: line(d, seg, max(1.2, w0 * 0.12), WATER_HI)
    for k in range(nd):                                                       # 끊겨 이어지는 물방울 — 마지막 것이 목표에 닿는다
        f = (k + 1) / nd; t = cont + (1 - cont) * f - 0.035 * (1 - f)
        i = min(n - 1, int(round((n - 1) * t))); (x, y), (tx, ty, nx, ny) = pts[i], nm[i]
        blob_drop(d, x, y, tx, ty, w0 * (1.15 - 0.25 * f), w0 * (0.62 - 0.16 * f))
    for k, t in enumerate(side_drops):
        i = int((n - 1) * t); (x, y), (tx, ty, nx, ny) = pts[i], nm[i]; sgn = 1 if k % 2 else -1
        drop_c(d, x + sgn * nx * (wid(i, 0) + 6), y + sgn * ny * (wid(i, 0) + 6), 2.6)
    tx, ty = nm[-1][0], nm[-1][1]; base = math.atan2(-ty, -tx)
    for k in range(splash):
        a = base + math.radians(-spread + 2 * spread * k / max(1, splash - 1)); r = sr * (0.85 + 0.3 * (k % 2))
        blob_drop(d, p2[0] + math.cos(a) * r, p2[1] + math.sin(a) * r, math.cos(a), math.sin(a), 8.5, 4.4)
DAM = TF['POND']                       # 저수지 조각(뒤집음)의 좌표 함수
lay = cv.layer(); d = ImageDraw.Draw(lay)
# 놓일 자리를 먼저 셈(붙이기 전에 좌표 함수가 필요하다)
def tf_of(k, sc, cx, bot, fl):
    sp = SPR[k]; w, h = round(sp.width * sc), round(sp.height * sc); x0, y0 = round(cx - w / 2), round(bot - h); ox, oy = sp.origin
    if fl: return lambda x, y: (x0 + w - (x - ox) * sc, y0 + (y - oy) * sc)
    return lambda x, y: (x0 + (x - ox) * sc, y0 + (y - oy) * sc)
P_ = {p[0]: p for p in PL}
f_ = tf_of(*[P_['FAT'][i] for i in range(5)]); sm = tf_of(*[P_['SMALL'][i] for i in range(5)]); ho = tf_of(*[P_['HOLED'][i] for i in range(5)])
# 보 윗머리를 넘치는 물마루(물결 꼴) — 물줄기 셋이 여기서 나간다(일치 검사 2 · 3회: 저수지 모서리에서 나오는 듯 · 저수지를 가리키는 화살로 읽혔다)
E0, E1 = (1745, 963), (1836, 984)                 # 보 윗판의 윗변(왼쪽 기둥 머리 → 오른쪽 기둥 머리)
def on_edge(f, up=0.0):
    x = E0[0] + (E1[0] - E0[0]) * f; y = E0[1] + (E1[1] - E0[1]) * f
    return (x, y - up)
A1_, A2_ = on_edge(0.0, 6), on_edge(0.24, -1)            # 둘 다 보 윗머리 왼쪽 끝에서 위 · 아래로 갈라져(오른쪽 끝에서 나가면 저수지 물 위를 가로지른 띠가 되어 「저수지에서 나온다」로 읽혔다 — 일치 검사 12회)         # 첫째(뚱보 경비 · 멀다)는 보 윗머리 가운데께에서 높이 · 둘째(작은 흰 덩이의 세균 · 가깝다)는 왼쪽 끝에서 낮게
A3_ = (1858, 1036)                      # 셋째는 보 오른쪽 돌 벽의 틈에서 — 그 앞에 선 세균 몸의 구멍을 꿰뚫고 지나간다(구멍 너머로 돌 벽 · 물줄기가 비친다 — 바탕만 비치면 「흰 반창고」로 읽혔다, 일치 검사 9 · 10회)
HC = ho(811.7, 307.0)                   # 구멍 가운데
T1 = f_(482, 440); T2 = sm(700, 262)           # 첫째는 뚱보 경비의 정강이에 — 배 높이로 오면 그가 밀어내는 세균에 먼저 닿았다(일치 검사 전 확인)
T3 = (HC[0] + (HC[0] - A3_[0]) * 0.75, HC[1] + (HC[1] - A3_[1]) * 0.75 + 4)
poly(d, [(A3_[0] + 6 * math.cos(a) * (1 + 0.28 * ((k * 7) % 3 - 1)), A3_[1] + 9 * math.sin(a) * (1 + 0.28 * ((k * 5) % 3 - 1))) for k, a in enumerate(np.linspace(0, 2 * math.pi, 11, endpoint=False))], (34, 30, 28, 255), 1.4)   # 돌 벽 틈(들쭉날쭉한 검은 구멍 — 가는 금은 안 보였고 뾰족한 꼴은 「화살촉 홈」으로 읽혔다, 일치 검사 11 · 13회)
jet(d, A3_, ((A3_[0] + T3[0]) / 2, (A3_[1] + T3[1]) / 2 - 2), T3, 12, cont=0.8, splash=3, sr=9, spread=60, side_drops=(), wob=2.9, nd=3)
cv.put(lay)
for k, sc, cx, bot, fl, sh in PL:
    if k == 'HOLED': put(k, sc, cx, bot, fl)
lay = cv.layer(); d = ImageDraw.Draw(lay)
jet(d, A1_, ((A1_[0] + T1[0]) / 2 + 150, min(A1_[1], T1[1]) - 170), T1, 17, cont=1.0, nd=0, splash=5, sr=14, side_drops=(0.25, 0.5, 0.7), wob=0.3)
jet(d, A2_, ((A2_[0] + T2[0]) / 2 + 6, min(A2_[1], T2[1]) - 26), T2, 14, cont=0.84, splash=4, sr=12, side_drops=(0.45,), wob=1.7)
# 물마루: 보 윗판을 덮어 넘치는 물(물결 윗선 · 앞판을 타고 흐르는 물줄기 셋) — 물줄기들의 시작을 덮는다(매듭처럼 뭉쳐 보였다 — 일치 검사 4회)
crest_top = [on_edge(f, 9 + 4 * math.sin(f * math.pi * 6)) for f in np.linspace(-0.02, 1.02, 28)]
crest_bot = [on_edge(1.02, -5)] + [on_edge(f, -5 - 3 * (1 - abs(2 * f - 1))) for f in np.linspace(0.98, 0.02, 14)] + [on_edge(-0.02, -5)]
poly_c(d, crest_top + crest_bot, WATER, 1.4)
line(d, [on_edge(f, 4 + 2 * math.sin(f * math.pi * 6)) for f in np.linspace(0.08, 0.92, 18)], 1.6, WATER_HI)
cv.put(lay)

# ── 인터폰 줄(수화기 → 집 벽의 인터폰 함) · 확성기 전선(인터폰 함 → 이웃 집 확성기)
def coil(d, a, b, sag, loops, r, w=2.0):
    base = qbez(a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag), b, 900); nm = normals(base); n = len(base)
    pts = []
    for i, ((x, y), (tx, ty, nx, ny)) in enumerate(zip(base, nm)):
        t = i / (n - 1); ph = 2 * math.pi * loops * t; env = min(1.0, t * 10, (1 - t) * 10)
        pts.append((x + (nx * math.sin(ph) + tx * math.cos(ph) * 1.25) * r * env, y + (ny * math.sin(ph) + ty * math.cos(ph) * 1.25) * r * env))
    line(d, pts, w)
lay = cv.layer(); d = ImageDraw.Draw(lay)
H_ = TF['HOUSE']; C_ = TF['CALLER']; N_ = TF['NBR']
# 인터폰 판(L13a 의 것과 같은 꼴 — 회색 판 · 위쪽 스피커 홈 · 오른쪽에 빈 수화기 걸이): 집 오른벽 바깥, 앞모습
wx, wy = H_(737, 300)                   # 오른벽 바깥 선
PX0, PY0, PW, PH = wx - 6, wy + 6, 46, 56
poly(d, [(PX0 + 6, PY0), (PX0 + PW - 6, PY0), (PX0 + PW, PY0 + 6), (PX0 + PW, PY0 + PH - 6), (PX0 + PW - 6, PY0 + PH), (PX0 + 6, PY0 + PH), (PX0, PY0 + PH - 6), (PX0, PY0 + 6)], (164, 170, 170, 255), 2.6)
for k in range(4):
    yy = PY0 + 10 + k * 6; line(d, [(PX0 + 9, yy), (PX0 + PW - 17, yy)], 2.0, (70, 72, 74, 255))
poly(d, [(PX0 + 8, PY0 + 37), (PX0 + PW - 16, PY0 + 37), (PX0 + PW - 16, PY0 + 48), (PX0 + 8, PY0 + 48)], (196, 200, 200, 255), 1.6)
poly(d, [(PX0 + PW - 10, PY0 + 9), (PX0 + PW - 4, PY0 + 9), (PX0 + PW - 4, PY0 + 47), (PX0 + PW - 10, PY0 + 47)], (120, 124, 126, 255), 1.6)   # 빈 걸이
hook = (PX0 + PW - 4, PY0 + 44)
coil(d, C_(802, 290), hook, 40, 8, 4.6, 2.2)
spk = N_(492, 246)
top = (PX0 + PW - 12, PY0)              # 전선: 인터폰 판 윗머리(작은 꼭지)에서 바로 위로 올라 집 밖으로 늘어져 이웃 집 확성기 윗머리로
poly(d, [(top[0] - 4, top[1] - 7), (top[0] + 4, top[1] - 7), (top[0] + 4, top[1] + 1), (top[0] - 4, top[1] + 1)], (120, 124, 126, 255), 1.6)
def cbez(p0, p1, p2, p3, n=60):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0], (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]) for t in np.linspace(0, 1, n)]
e_ = N_(560, 226)
line(d, cbez((top[0], top[1] - 7), (top[0], 400), (e_[0] - 90, 432), e_, 80) + [N_(512, 238)], 4.0)   # 한 번에 휘어 넘어가는 전선 — 수화기 든 이의 머리 위로(일치 검사 3 · 4 · 9회)
cv.put(lay)

# ── 붉은 리본 배지 — 성 안의 모두(흰 덩이 넷 · 흰 옷 경비 다섯 · 주민 셋). 침입자(초록 세균 · 망토 두른 이)에게만 없다.
BAD = [('BLOB1', 88, 345, 9), ('BLOB2', 425, 335, 9), ('BLOB3', 755, 335, 9), ('SMALL', 880, 380, 8),
       ('MAN', 505, 262, 8), ('CALLER', 905, 330, 7), ('NBR', 386, 365, 6),
       ('EATER', 252, 300, 7), ('FAT', 528, 298, 8), ('SQZ', 776, 288, 7), ('PUS', 1019, 783, 6), ('PUS', 1790, 806, 6)]
lay = cv.layer(); d = ImageDraw.Draw(lay)
for k, x, y, r in BAD:
    if k in TF: bx, by = TF[k](x, y); badge(d, bx, by, r)
cv.put(lay)

cv.im.save(dst)
print('ok', dst)
for k, sc, cx, bot, fl, sh in PL + [('SWELL', S_SW, X_SW, hose_y_bottom(sw, 252, S_SW), 0, 0), ('SQZ', S_SQ, X_SQ, hose_y_bottom(sq, 307, S_SQ), 0, 0)]:
    print(f'{k:8s} x {round(cx - SPR[k].width * sc / 2):5d} ~ {round(cx + SPR[k].width * sc / 2):5d}  y {round(bot - SPR[k].height * sc):5d} ~ {round(bot):5d}')

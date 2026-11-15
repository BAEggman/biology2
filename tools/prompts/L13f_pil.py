#!/usr/bin/env python3
# L13f_pil.py <base.png> <out.png> — L13f 「깃발 다섯 연대의 출정」의 PIL 마무리(2026-11-15).
#  바탕 = Gemini S1b(출연진 그림을 올려 장면 통째) + 구역 편집 ZA3 ~ ZJ2(L13f_build.sh).
#  여기서는 Gemini 가 끝내 못 한 것과 「개수 · 자리 · 빛깔이 곧 뜻」인 것만:
#   ⓪ 구역 편집이 남긴 자국 지우기(밀려난 벌레 꼬리 · 호스 끝의 초록 다리 · 쌍둥이 사이 옛 J 고리 · 지팡이 밑의 막대 토막)
#   ① 세균 둘 · 망토 두 손 · 뚱보 경비 배의 작은 Y — 「집게 Y」(두 팔 끝이 안으로 굽어 무는 꼴 · L13f_ylib.claw_y)
#      세균 · 망토: 집게(가변 · N 말단)가 살갗을 물고 곧은 깃대(불변 · Fc)는 바깥으로 — Gemini 는 두 번 다 거꾸로 꽂았고,
#      곧은 Y 는 독자 셋이 「곧은 쪽이 몸에 붙었다」로 거꾸로 읽었다(일치 검사 1 · 2회 · 따로 본 시험 셋) → 집게로 바꾸자 바로 읽혔다.
#      경비(비만세포): 거꾸로 — 깃대 끝이 배에 박히고 집게가 바깥 · 꽃가루 공 하나를 두 집게가 함께 문다(교차결합)
#   ② 이음 깃발(IgA 이량체 — 깃대 끝끼리 맞댄 Y 둘 · 가운데 J 고리)을 우는 아이의 눈물방울 둘 · 샘물 줄기 둘 · 샘 웅덩이 하나에
#   ③ 붉은 리본 배지 — 자기(MHC I): 성 안의 벌 · 경비 · 주민 모두(몸이 보이는 것만). 세균 · 망토 · 벌레 · 꽃가루에는 없다
import sys, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from L13f_ylib import S, claw_y, double_y, body_contour, resample
from s13_lib import disc, badge, RED, RED_D, GOLD_C

W, H = 2048, 1144
src, dst = sys.argv[1:3]
im = Image.open(src).convert('RGB')
assert im.size == (W, H), im.size

def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay):
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    b = im.convert('RGBA'); b.alpha_composite(small); im = b.convert('RGB')

# ── ⓪ 자국 지우기
a = np.array(im)[:, :, ::-1].copy(); m = np.zeros(a.shape[:2], np.uint8)
def mark(box, fn):
    x0, y0, x1, y1 = box; sub = a[y0:y1, x0:x1].astype(int); b_, g_, r_ = sub[..., 0], sub[..., 1], sub[..., 2]
    m[y0:y1, x0:x1] |= (fn(r_, g_, b_) * 255).astype(np.uint8)
wall_not = lambda r, g, b: (np.abs(r - g) > 14) | (np.abs(g - b) > 14) | (np.maximum(np.maximum(r, g), b) < 150)   # 회색 벽이 아닌 것
mark((978, 335, 1080, 360), wall_not); mark((1000, 360, 1080, 390), wall_not)          # 밀려난 벌레의 옛 꼬리 · 그림자(불꽃은 x < 1000 · y > 360)
mark((1615, 325, 1722, 372), lambda r, g, b: g > r + 12)                                # 호스 끝 위 옅은 초록 줄(옛 세균)
mark((1642, 372, 1670, 393), lambda r, g, b: (g > r + 12) | (np.maximum(np.maximum(r, g), b) < 95))
mark((1694, 372, 1720, 395), lambda r, g, b: (g > r + 12) | (np.maximum(np.maximum(r, g), b) < 95))
mark((1638, 393, 1674, 404), lambda r, g, b: g > r + 10)                                # 그 다리의 아랫도리(호스 테 위 — 초록만)
mark((280, 300, 306, 326), lambda r, g, b: np.maximum(np.maximum(r, g), b) < 120)      # 쌍둥이 사이 옛 J 고리
mark((1171, 810, 1192, 850), lambda r, g, b: (np.maximum(np.maximum(r, g), b) < 200) & (r - b < 120))   # 지팡이 밑 막대 토막
def band(p0, p1, hw, keep=None):
    """p0 → p1 선분을 따라 반폭 hw 의 띠를 지울 자리로(keep(r, g, b) 가 참인 픽셀은 남긴다)."""
    bm = np.zeros(m.shape, np.uint8); cv2.line(bm, tuple(map(int, p0)), tuple(map(int, p1)), 255, int(2 * hw))
    if keep is not None:
        b_, g_, r_ = [a[..., k].astype(int) for k in range(3)]; bm[keep(r_, g_, b_)] = 0
    m[:] |= bm
mark((1678, 551, 1688, 561), lambda r, g, b: np.minimum(np.minimum(r, g), b) > 200)       # D 명찰 위 흰 부스러기(옛 명찰 고리)
dark = lambda r, g, b: np.maximum(np.maximum(r, g), b) < 120
mark((1675, 436, 1683, 489), dark)                                                     # 호스 끝에서 하품 벌 머리로 내려오다 끊긴 가는 세로줄(일치 검사 3회)
mark((1346, 588, 1378, 602), lambda r, g, b: (np.maximum(np.maximum(r, g), b) < 200) | (r - b < 60))   # 무리 뒤 모래의 갈색 토막(일치 검사 3회 — 땅선 y < 588 은 그대로)
mark((1424, 590, 1440, 603), lambda r, g, b: (np.maximum(np.maximum(r, g), b) < 200) | (np.minimum(np.minimum(r, g), b) > 225))   # 그 곁 둥근 점
mark((1686, 636, 1706, 653), lambda r, g, b: (r > 190) & (g > 140) & (b < 130))         # 하품 벌 곁 탑 벽의 노란 얼룩(일치 검사 5회)
m = cv2.dilate(m, np.ones((5, 5), np.uint8))
a = cv2.inpaint(a, m, 5, cv2.INPAINT_TELEA)
# 경비 머리 위 성벽의 비스듬한 회색 얼룩(밀려난 벌레의 옛 그림자 — 일치 검사 3회) → 둘레 벽 빛깔로
ys0, xs0 = np.mgrid[340:392, 984:1040]; sub = a[340:392, 984:1040].astype(int)
r_, g_, b_ = sub[..., 2], sub[..., 1], sub[..., 0]
wall = np.median(a[300:330, 1040:1100].reshape(-1, 3), axis=0)
smear = (np.abs(r_ - g_) < 16) & (np.abs(g_ - b_) < 16) & (sub.mean(axis=2) < wall.mean() - 6) & ~((xs0 < 1003) & (ys0 > 352))
smear = cv2.dilate(smear.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
smear &= ~((xs0 < 1001) & (ys0 > 350))                              # 성냥 불꽃 쪽은 건드리지 않는다
al = cv2.GaussianBlur(smear.astype(np.float32), (0, 0), 1.5)[..., None]
a[340:392, 984:1040] = (sub[..., ::1] * (1 - al) + wall[None, None, :] * al).astype(np.uint8)
im = Image.fromarray(a[:, :, ::-1])

# ── ⓪-2 D 자 명찰(곧은 왼쪽 · 둥근 오른쪽 · 빈칸) — Gemini 의 것은 모서리 둥근 네모로 읽혔다(일치 검사 1회)
lay = layer(); d = ImageDraw.Draw(lay)
cx, cy, rx, ry, x0 = 1675, 579, 25, 20, 1653
pts = [(x0, cy - ry)] + [(cx + rx * math.sin(t), cy - ry * math.cos(t)) for t in np.linspace(0, math.pi, 40)] + [(x0, cy + ry)]
d.polygon([(x * S, y * S) for x, y in pts], fill=(250, 250, 250, 255), outline=(24, 20, 18, 255), width=int(2.4 * S))
d.rectangle([1668 * S, 553 * S, 1676 * S, 563 * S], fill=(170, 170, 176, 255), outline=(24, 20, 18, 255), width=int(1.4 * S))
d.line([(474 * S, 306.5 * S), (513 * S, 304.5 * S)], fill=(28, 22, 18, 255), width=int(2.4 * S))   # 별 바퀴 왼쪽 위 깃발 천의 윗테(구역 편집 ZF 상자 끝에서 잘렸다)
for ya, yb in ((421, 459), (527, 590)):                                                 # 진홍 호스 왼쪽의 잘린 곧은 가장자리(ZB 상자 끝 — 「세로 이음 띠」 · 일치 검사 5회)에 테 — 경비 모자 뒤로 내려가는 호스
    d.line([(1100 * S, ya * S), (1099.5 * S, yb * S)], fill=(30, 22, 22, 255), width=int(3.0 * S))
put(lay)

# ── ① 집게 Y(세균 둘 · 망토 두 손 · 뚱보 경비의 배)
bgr = np.array(im)[:, :, ::-1].copy()
def pick(box, k, kind, angs, cen):
    """윤곽 위에서 중심 cen 에서 본 각도 angs(도)에 가장 가까운 점과 바깥 법선."""
    cs, mk = body_contour(bgr, box, kind, k)
    rs = resample(cs[0], 3, mk, box[:2], 0.5); out = []
    for a_ in angs:
        t = math.radians(a_); best = None
        for p, n in rs:
            dd = abs((math.atan2(p[1] - cen[1], p[0] - cen[0]) - t + math.pi) % (2 * math.pi) - math.pi)
            if best is None or dd < best[0]: best = (dd, p, n)
        out.append(best[1:])
    return out
HANDS1 = [(862, 912, 912, 962), (786, 952, 838, 1006)]            # 흰 덩이의 두 손(세균을 쥔)
lay = layer(); d = ImageDraw.Draw(lay)
G1 = pick((770, 885, 915, 1035), 17, 'green', [-80, -35, 10, 55, 100], (850, 960))               # 흰 덩이가 먹는 세균 — 둘은 깃대가 덩이 손 밑으로
G2 = pick((1000, 895, 1140, 1085), 23, 'green', [-100, -50, -140, 20, 160, 60], (1068, 985))     # 깃발투성이로 춤추는 세균
for p, n in G1 + G2: claw_y(d, (p[0] - n[0] * 3, p[1] - n[1] * 3), n, 9.0, 20.0, 20.0, 4.6)
put(lay)
orig = np.array(Image.fromarray(bgr[:, :, ::-1]))                  # 흰 덩이의 손을 깃대 위로(깃대를 쥠)
out = np.array(im)
for x0, y0, x1, y1 in HANDS1:
    sub = orig[y0:y1, x0:x1].astype(int); hm = cv2.dilate((sub.min(axis=2) > 205).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    out[y0:y1, x0:x1][hm] = orig[y0:y1, x0:x1][hm]
im = Image.fromarray(out)
bgr2 = np.array(im)[:, :, ::-1].copy()                             # 망토의 두 손(중화) — 손 둘레를 집게가 물고 깃대는 바깥(소매 · 두건 쪽은 빼고)
cs, mk = body_contour(bgr2, (195, 900, 268, 992), 'skin', 0)
mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
cs = [cc[:, 0, :].astype(float) + np.array([195, 900]) for cc in sorted(cv2.findContours(mk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea, reverse=True)]
def bg_ok(q):
    x, y = int(round(q[0])), int(round(q[1]))
    if not (0 <= x < W and 0 <= y < H): return False
    b_, g_, r_ = [int(v) for v in bgr2[y, x]]
    skin = r_ > 195 and 140 < g_ < 222 and r_ - b_ > 40; purple = b_ > r_ + 15 and b_ > g_ + 25
    return (not skin) and (not purple) and x < 262
lay = layer(); d = ImageDraw.Draw(lay)
for cc in cs[:2]:
    for p, n in resample(cc, 17, mk, (195, 900), 0.5):
        if n[0] > 0.55: continue
        if all(bg_ok((p[0] + n[0] * t, p[1] + n[1] * t)) for t in (8, 13, 18, 23)): claw_y(d, (p[0] - n[0] * 2, p[1] - n[1] * 2), n, 5.8, 12.0, 12.0, 3.2, 4.5, 1.2)
put(lay)
# 뚱보 경비(비만세포)의 IgE — 깃대 끝이 배 왼쪽 윤곽에 박히고 집게가 바깥 · 위 둘은 꽃가루 공 하나를 함께 문다
def pollen(d, cx, cy, r):
    """꽃가루 공 — 노란 공 + 둘레의 뾰족한 가시 + 짙은 점(꽃가루 알갱이의 꼴)."""
    for k in range(16):
        a_ = 2 * math.pi * k / 16
        tip = (cx + math.cos(a_) * r * 1.42, cy + math.sin(a_) * r * 1.42)
        l_ = (cx + math.cos(a_ - 0.2) * r * 0.9, cy + math.sin(a_ - 0.2) * r * 0.9); r2 = (cx + math.cos(a_ + 0.2) * r * 0.9, cy + math.sin(a_ + 0.2) * r * 0.9)
        d.polygon([(x * S, y * S) for x, y in (l_, tip, r2)], fill=(246, 206, 52, 255), outline=(40, 32, 20, 255), width=int(1.1 * S))
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(250, 214, 60, 255), outline=(40, 32, 20, 255), width=int(1.6 * S))
    for k, (dx, dy) in enumerate(((-0.35, -0.3), (0.3, -0.35), (0.0, 0.05), (-0.3, 0.38), (0.38, 0.3))):
        rr = r * 0.11; d.ellipse([(cx + dx * r - rr) * S, (cy + dy * r - rr) * S, (cx + dx * r + rr) * S, (cy + dy * r + rr) * S], fill=(196, 140, 30, 255))
bgr3 = np.array(im)[:, :, ::-1].copy()                             # 배(흰 몸) 실루엣 — 깃대 끝을 배 윤곽 「속으로」 그린 뒤 배를 다시 덮어 박힌 꼴로
wm = ((bgr3.min(axis=2) > 200) * 255).astype(np.uint8); wm[:, :930] = 0; wm[:, 1130:] = 0; wm[:560] = 0; wm[730:] = 0
n_, lab_, st_, _ = cv2.connectedComponentsWithStats(wm); belly = (lab_ == lab_[660, 1030]) & (lab_ > 0)
belly = cv2.dilate(belly.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0     # 검은 윤곽까지
lay = layer(); d = ImageDraw.Draw(lay)
PB, PR = (910.0, 654.0), 12.0                                       # 꽃가루 공
for q in ((969.0, 624.0), (957.0, 684.0)):                          # 배 왼쪽 윤곽의 두 점(배 가장 왼쪽 x: y 624 → 969 · y 684 → 957) → 집게는 공의 겉에
    vx, vy = q[0] - PB[0], q[1] - PB[1]; L_ = math.hypot(vx, vy); ux, uy = vx / L_, vy / L_
    p = (PB[0] + ux * (PR + 1.5), PB[1] + uy * (PR + 1.5)); tot = L_ - PR - 1.5 + 12
    claw_y(d, p, (ux, uy), 8.0, 15.0, tot - 15.0, 4.6)
q, m_ = (978.0, 708.0), (-0.6, 0.8)                                 # 배 왼쪽 아래 — 빈 집게 하나(아직 아무것도 안 문)
claw_y(d, (q[0] + m_[0] * 36, q[1] + m_[1] * 36), (-m_[0], -m_[1]), 8.0, 15.0, 33.0, 4.6)
pollen(d, PB[0], PB[1], PR)
before = np.array(im); put(lay); after = np.array(im)
after[belly] = before[belly]; im = Image.fromarray(after)          # 배가 깃대 끝을 덮는다 = 꽂힘

# ── ①-2 지팡이 연대(IgG)의 깃발 빛깔 — Gemini(ZD)는 잿빛 나무색으로 그렸다 → 다른 Y 깃발과 같은 황토로(「같은 Y 인데 빛깔이 다르다」 — 일치 검사 4회)
a = np.array(im).astype(np.float32); y0, y1, x0, x1 = 605, 1060, 1140, 1720
sub = a[y0:y1, x0:x1]; r_, g_, b_ = sub[..., 0], sub[..., 1], sub[..., 2]
mk = (r_ > 110) & (r_ < 200) & (g_ > 85) & (g_ < 170) & (b_ > 60) & (b_ < 150) & (r_ - b_ > 18) & (r_ - b_ < 70) & (r_ - g_ > 5) & (r_ - g_ < 40)
yy, xx = np.mgrid[y0:y1, x0:x1]; mk &= ~((xx > 1425) & (xx < 1535) & (yy > 680) & (yy < 820))   # 임신부의 갈색 머리는 그대로
n_, lab_, st_, _ = cv2.connectedComponentsWithStats(mk.astype(np.uint8))
keep = np.isin(lab_, [k for k in range(1, n_) if st_[k, 4] >= 25])
f = np.clip((0.3 * r_ + 0.59 * g_ + 0.11 * b_) / 128.0, 0.55, 1.35)[..., None]
new = np.clip(np.array([226, 168, 58], np.float32)[None, None, :] * f, 0, 255)
al = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 0.6)[..., None]
a[y0:y1, x0:x1] = sub * (1 - al) + new * al
im = Image.fromarray(a.astype(np.uint8))

# ── ② 이음 깃발(IgA 이량체) — 눈물 · 샘
lay = layer(); d = ImageDraw.Draw(lay)
for cx, cy, ang, half, arm, spr, w in ((82, 568, 0.0, 5.2, 3.2, 2.8, 1.7), (130, 559, 0.0, 4.2, 2.7, 2.4, 1.5),   # 우는 아이의 눈물방울 둘
                                       (143, 468, 1.45, 6.5, 3.8, 3.3, 1.9), (149, 515, 1.62, 6.5, 3.8, 3.3, 1.9),   # 샘물 줄기
                                       (178, 549, 0.12, 6.5, 3.8, 3.3, 1.9)):                                       # 샘 웅덩이
    double_y(d, cx, cy, ang, half, arm, spr, w)
put(lay)

# ── ③ 붉은 리본 배지(자기) — 아래 BADGES 는 그림을 보며 몸이 보이는 자리마다
def badge_c(d, cx, cy, r):
    """작은 배지(r < 7): 꼬리를 테두리 없는 세모 둘로(L13d · L13e 그대로)."""
    for sx in (-1, 1):
        d.polygon([((cx + sx * 0.15 * r) * S, (cy + 0.5 * r) * S), ((cx + sx * 0.95 * r) * S, (cy + 0.55 * r) * S), ((cx + sx * 0.7 * r) * S, (cy + 1.75 * r) * S)], fill=RED_D)
    disc(d, cx, cy, r, RED, max(1.2, r * 0.2))
    d.ellipse([(cx - 0.4 * r) * S, (cy - 0.4 * r) * S, (cx + 0.4 * r) * S, (cy + 0.4 * r) * S], fill=GOLD_C)
def put_badge(d, cx, cy, r): (badge if r >= 7 else badge_c)(d, cx, cy, r)
BADGES = (                                                                             # 반지름 — 벌이 L13e 보다 커서 1.3 배쯤(작으면 「점」으로 묻힌다)
    (1278, 775, 10), (1310, 705, 8), (1395, 805, 8.5), (1250, 990, 10.5),             # 지팡이 연대(IgG) — 앞쪽 넷
    (1545, 735, 9), (1660, 790, 10), (1628, 940, 10),                                  # 지팡이 연대 — 뒤쪽 셋
    (1720, 1000, 11.5), (1925, 1060, 11), (1550, 322, 7.5), (1842, 385, 7.5),          # 큰 Y 를 든 넷(큰 벌 둘 · 작은 벌 둘)
    (1700, 625, 9), (1852, 640, 7.5), (1950, 620, 7.5),                                # D 자 명찰 벌 · 탑 문의 벌 둘
    (1230, 260, 8.5), (225, 330, 8), (370, 330, 8), (470, 470, 8),                     # 갈퀴 벌 · 쌍둥이 · 바퀴 미는 벌
    (1090, 590, 10), (1479, 850, 9), (120, 610, 8), (640, 905, 11),                    # 뚱보 경비 · 임신부 · 우는 아이 · 흰 덩이(L13b 처럼 몸 왼쪽 위)
)
lay = layer(); d = ImageDraw.Draw(lay)
for cx, cy, r in BADGES: put_badge(d, cx, cy, r)
put(lay)

im.save(dst)
print('saved', dst)

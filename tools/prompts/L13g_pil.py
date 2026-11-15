#!/usr/bin/env python3
# L13g_pil.py <base.png> <out.png> — L13g 「봄 잔칫날의 성」의 PIL 마무리(2026-11-15).
#  바탕 = Gemini S1b(출연진 그림을 올려 장면 통째) + 구역 편집 GZA · GZB · GZC2 · GZD(L13g_build.sh).
#  여기서는 「개수 · 자리 · 빛깔 · 방향이 곧 뜻」인 것만(L13f 의 집게 Y 문법 그대로 — L13f_ylib):
#   ⓪ 자국 지우기 — 쓰러진 사람 셔츠의 글자 같은 낙서 · 아기 손의 파란 병(모유를 먹는데 젖병으로 읽힌다) · 섬 병정 손으로 이어진 전선 끝
#   ⓪-2 거북을 좌우로 뒤집는다 — 바탕의 거북은 발진 난 사람의 반대쪽(왼쪽)을 보고 걸어 「이제야 닿음」이 거꾸로 읽혔다(일치 검사 1회)
#   ① 1형 — 뚱보 경비(비만세포) 배 오른쪽에 거꾸로 박힌 집게 Y 둘(IgE · 깃대가 배에) + 두 집게가 함께 문 꽃가루 공(교차결합)
#   ② 2형 — 호스 유리 방울 속 터진 붉은 원반 조각을 문 작은 집게 Y 셋(수혈된 남의 적혈구에 붙은 항체)
#   ③ 3형 — 쇠 거름망 위에 집게 Y 와 금빛 구슬(녹아 떠다니던 항원)이 사슬처럼 엉긴 덩이(면역복합체 침착)
#   ④ 모유 — 아기 손의 작은 이음 깃발(IgA 이량체 · L13f 쌍둥이의 깃발과 같은 꼴)
#   ⑤ 붉은 리본 배지 — 자기: 성 안의 벌 · 경비 · 주민 · 병정 모두(몸이 보이는 것만). 헝겊 인형 · 조랑말(남의 동물 — 항독소의 출처) · 거북 · 아기에는 없다
import sys, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from L13f_ylib import S, claw_y, double_y, INK, OCHRE
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
mark((818, 980, 842, 1000), lambda r, g, b: np.maximum(np.maximum(r, g), b) < 110)       # 셔츠의 글자 같은 낙서(「ㅊy」)
mark((224, 918, 252, 950), lambda r, g, b: (b > r + 10) | (np.maximum(np.maximum(r, g), b) < 100))   # 아기 손의 파란 병(테까지)
mark((1756, 296, 1802, 347), lambda r, g, b: np.maximum(np.maximum(r, g), b) < 140)     # 기둥의 검은 전선 — 섬 병정 손까지 이어진 아랫도리(「밧줄로 끈다」로 읽힘 · 전선은 기둥에 매달려 늘어진다) · 테의 옅은 띠까지
m = cv2.dilate(m, np.ones((5, 5), np.uint8))
a = cv2.inpaint(a, m, 4, cv2.INPAINT_TELEA)
# ⓪-2 거북 뒤집기(등의 병정째) — 거북 몸의 한 점에서 이어진 덩이만 오려 좌우로(모래 = 밝은 누런 빛 · 그 밖은 덩이) · 위쪽 가족의 발 · 오른쪽 사람의 다리는 빼고 · 빈자리는 그림 전체에서 메워 네모 자국이 없게
X0, Y0, X1, Y1 = 1505, 755, 1840, 1112
sub = a[Y0:Y1, X0:X1].astype(int); b_, g_, r_ = sub[..., 0], sub[..., 1], sub[..., 2]
sandlike = (r_ > 195) & (g_ > 160) & (b_ > 95) & (r_ - b_ > 45) & (r_ - b_ < 125) & (r_ >= g_)
nm = (~sandlike).astype(np.uint8)
nm = cv2.morphologyEx(nm, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)); nm = cv2.morphologyEx(nm, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
yy_, xx_ = np.mgrid[Y0:Y1, X0:X1]
nm[yy_ < 760] = 0; nm[(yy_ < 776) & ((xx_ <= 1668) | (xx_ >= 1732))] = 0   # 위쪽 경례 병정 · 가족의 발(가운데 병정의 높은 모자만 762 까지)
n_, lab_, st_, _ = cv2.connectedComponentsWithStats(nm)
spr = (lab_ == lab_[1000 - Y0, 1680 - X0]) & (lab_ > 0)
cs_, _ = cv2.findContours(spr.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
spr = np.zeros_like(nm); cv2.drawContours(spr, cs_, -1, 1, -1); spr = spr > 0
hole = np.zeros(a.shape[:2], np.uint8); hole[Y0:Y1, X0:X1] = cv2.dilate(spr.astype(np.uint8) * 255, np.ones((7, 7), np.uint8))
fl_img = a[Y0:Y1, X0:X1][:, ::-1].copy(); fl_m = spr[:, ::-1]
a = cv2.inpaint(a, hole, 7, cv2.INPAINT_TELEA)
al = cv2.GaussianBlur(cv2.erode(fl_m.astype(np.uint8), np.ones((2, 2), np.uint8)).astype(np.float32), (0, 0), 0.8)[..., None]
a[Y0:Y1, X0:X1] = (fl_img.astype(np.float32) * al + a[Y0:Y1, X0:X1].astype(np.float32) * (1 - al)).astype(np.uint8)
im = Image.fromarray(a[:, :, ::-1])

# ⓪-3 검은 전선(축삭)에 감긴 흰 테이프(수초) — 기둥 왼쪽으로 늘어진 전선에 흰 테이프 토막 셋(사이사이 맨 전선 = 마디 · 비스듬한 결 = 감김)
bgr0 = np.array(im)[:, :, ::-1].copy(); pts = []
for y in range(206, 296, 1):
    row = bgr0[y, 1770:1830].max(axis=1); xs = np.where(row < 80)[0]
    if len(xs): pts.append((1770 + xs[:max(1, min(len(xs), 6))].mean(), float(y)))
pts = [tuple(np.mean(pts[max(0, k - 3):k + 4], axis=0)) for k in range(len(pts))]
lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
n_p = len(pts)
for t0, t1 in ((0.05, 0.25), (0.36, 0.56), (0.67, 0.87)):
    seg = pts[int(t0 * (n_p - 1)):int(t1 * (n_p - 1)) + 1]
    for colr, ww_ in (((30, 26, 26, 255), 12.6), ((250, 250, 250, 255), 9.6)):
        d.line([(x * S, y * S) for x, y in seg], fill=colr, width=int(ww_ * S), joint='curve')
    for k in range(3, len(seg) - 3, 6):                              # 감긴 결(비스듬한 줄)
        (x, y) = seg[k]; (x2, y2) = seg[min(len(seg) - 1, k + 2)]
        tx, ty = x2 - x, y2 - y; l = math.hypot(tx, ty) or 1; tx, ty = tx / l, ty / l; nx, ny = -ty, tx
        d.line([((x + nx * 4.6 - tx * 2.2) * S, (y + ny * 4.6 - ty * 2.2) * S), ((x - nx * 4.6 + tx * 2.2) * S, (y - ny * 4.6 + ty * 2.2) * S)], fill=(120, 120, 128, 255), width=int(1.3 * S))
small = lay.resize((W, H), Image.LANCZOS); b_ = im.convert('RGBA'); b_.alpha_composite(small); im = b_.convert('RGB')

def claw_between(d, p, q, up, arm, stem, w=3.0, bulge=4.0):
    """두 점 p · q 를 두 집게 끝으로 무는 Y(깃대는 up 쪽으로) — 면역복합체의 사슬 · 교차결합."""
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2; sp = math.hypot(q[0] - p[0], q[1] - p[1]) / 2
    tx, ty = (q[0] - p[0]) / (2 * sp), (q[1] - p[1]) / (2 * sp); nx, ny = ty, -tx
    if nx * up[0] + ny * up[1] < 0: nx, ny = -nx, -ny
    return claw_y(d, (mx, my), (nx, ny), sp, arm, stem, w, bulge, 1.2)
def bead(d, x, y, r):
    d.ellipse([(x - r - 1.2) * S, (y - r - 1.2) * S, (x + r + 1.2) * S, (y + r + 1.2) * S], fill=INK)
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(246, 200, 58, 255))
    d.ellipse([(x - r * 0.45) * S, (y - r * 0.55) * S, (x - r * 0.05) * S, (y - r * 0.15) * S], fill=(255, 238, 160, 255))
def pollen(d, cx, cy, r):
    """꽃가루 공 — L13f 와 같은 꼴(노란 공 + 가시 + 갈색 알갱이 점)."""
    for k in range(16):
        a_ = 2 * math.pi * k / 16
        tip = (cx + math.cos(a_) * r * 1.42, cy + math.sin(a_) * r * 1.42)
        l_ = (cx + math.cos(a_ - 0.2) * r * 0.9, cy + math.sin(a_ - 0.2) * r * 0.9); r2 = (cx + math.cos(a_ + 0.2) * r * 0.9, cy + math.sin(a_ + 0.2) * r * 0.9)
        d.polygon([(x * S, y * S) for x, y in (l_, tip, r2)], fill=(246, 206, 52, 255), outline=(40, 32, 20, 255), width=int(1.1 * S))
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(250, 214, 60, 255), outline=(40, 32, 20, 255), width=int(1.6 * S))
    for dx, dy in ((-0.35, -0.3), (0.3, -0.35), (0.0, 0.05), (-0.3, 0.38), (0.38, 0.3)):
        rr = r * 0.11; d.ellipse([(cx + dx * r - rr) * S, (cy + dy * r - rr) * S, (cx + dx * r + rr) * S, (cy + dy * r + rr) * S], fill=(196, 140, 30, 255))

# ── ① 1형 — 뚱보 경비 배 오른쪽의 IgE 둘 + 꽃가루 공
bgr = np.array(im)[:, :, ::-1].copy()
wm = ((bgr.min(axis=2) > 200) * 255).astype(np.uint8); wm[:, :840] = 0; wm[:, 1010:] = 0; wm[:520] = 0; wm[680:] = 0
n_, lab_, st_, cen_ = cv2.connectedComponentsWithStats(wm)
belly = np.isin(lab_, [k for k in range(1, n_) if st_[k, 4] > 400 and 860 < cen_[k][0] < 1010 and 540 < cen_[k][1] < 690])   # 배는 가운데 솔기선으로 두 쪽 — 둘 다
belly = cv2.dilate(belly.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
lay = layer(); d = ImageDraw.Draw(lay)
PB, PR = (1036.0, 607.0), 15.0                                     # 공을 배 가까이(멀면 깃대가 길어 「집게 · 부젓가락을 쥔 경비」로 보인다) · 공을 키워 두 집게 사이를 띄움(붙으면 「집게 하나」 — 일치 검사 2회)
def edge_in(y):
    xs = np.where(belly[y])[0]; return float(xs.max() - 10)
for yq in (553, 661):                                               # 배 오른쪽 윤곽 12 px 안의 두 점(위 · 아래로 벌려 — 둘이 붙으면 「집게 하나」로 읽혔다 · 일치 검사 1회)
    q = (edge_in(yq), float(yq))
    vx, vy = q[0] - PB[0], q[1] - PB[1]; L_ = math.hypot(vx, vy); ux, uy = vx / L_, vy / L_
    p = (PB[0] + ux * (PR + 1.5), PB[1] + uy * (PR + 1.5))
    claw_y(d, p, (ux, uy), 6.0, 14.0, L_ - PR - 1.5 - 14.0, 4.4)
pollen(d, PB[0], PB[1], PR)
before = np.array(im); put(lay); after = np.array(im)
after[belly] = before[belly]; im = Image.fromarray(after)          # 배가 깃대 끝을 덮는다 = 꽂힘

# ── ② 2형 — 유리 방울 속 터진 원반 조각을 문 작은 집게 Y 셋(깃대는 위 · 바깥)
lay = layer(); d = ImageDraw.Draw(lay)
for (px, py), (nx, ny) in (((1281, 712), (-0.6, -0.8)), ((1318, 708), (0.55, -0.83)), ((1300, 744), (0.0, -1.0))):
    claw_y(d, (px, py), (nx, ny), 6.5, 11.5, 10.0, 3.3, 3.8, 1.2)
put(lay)

# ── ③ 3형 — 쇠 거름망 위의 면역복합체(금빛 구슬 + 집게 Y 의 사슬)
lay = layer(); d = ImageDraw.Draw(lay)
BEADS = [(1282, 1031), (1318, 1046), (1352, 1030), (1322, 1014), (1386, 1046)]
for i, j in ((0, 1), (1, 2), (3, 2), (0, 3), (2, 4)):
    claw_between(d, BEADS[i], BEADS[j], (0.0, -1.0), 9.0, 10.0, 3.0, 3.6)
for x, y in BEADS: bead(d, x, y, 5.2)
put(lay)

# ── ④ 모유 — 아기 손의 작은 이음 깃발(IgA 이량체)
lay = layer(); d = ImageDraw.Draw(lay)
double_y(d, 236, 916, -0.55, 13.0, 7.0, 6.0, 3.2)                  # 일치 검사 1회: 작으면 「가슴께의 작은 Y 하나」 — 크게 · 손에 쥔 꼴로
d.ellipse([(236 - 7.5) * S, (916 - 6.5) * S, (236 + 7.5) * S, (916 + 6.5) * S], fill=(250, 206, 172, 255), outline=(30, 24, 22, 255), width=int(1.8 * S))   # 아기 주먹(이음매를 쥠)
for k in (-1, 1): d.line([((236 + k * 2.5) * S, (911) * S), ((236 + k * 2.5) * S, (916) * S)], fill=(30, 24, 22, 255), width=int(1.2 * S))
put(lay)

# ── ⑤ 붉은 리본 배지(자기)
def badge_c(d, cx, cy, r):
    for sx in (-1, 1):
        d.polygon([((cx + sx * 0.15 * r) * S, (cy + 0.5 * r) * S), ((cx + sx * 0.95 * r) * S, (cy + 0.55 * r) * S), ((cx + sx * 0.7 * r) * S, (cy + 1.75 * r) * S)], fill=RED_D)
    disc(d, cx, cy, r, RED, max(1.2, r * 0.2))
    d.ellipse([(cx - 0.4 * r) * S, (cy - 0.4 * r) * S, (cx + 0.4 * r) * S, (cy + 0.4 * r) * S], fill=GOLD_C)
def put_badge(d, cx, cy, r): (badge if r >= 7 else badge_c)(d, cx, cy, r)
BADGES = (
    (118, 540, 9), (455, 470, 9), (668, 450, 9),                       # 벌 셋(인형 연습 둘 · 빨간 책 나르는 하나)
    (548, 585, 9.5), (778, 672, 8),                                     # 수레 곁 경비 · 침대의 환자(이불 위 — 목 곁은 「상처」로 보인다)
    (185, 880, 9.5),                                                   # 젖 먹이는 엄마
    (885, 548, 10.5), (1105, 600, 9.5), (1053, 857, 12.5), (900, 1040, 10.5),   # 뚱보 경비 · 재채기 · 무릎 꿇은 경비(가슴 회색 원판 위) · 부어 쓰러진 사람
    (1607, 330, 9), (1530, 345, 7), (1725, 345, 7),                     # 섬의 흰 가운 사내 · 그를 미는 병정 둘
    (1960, 250, 7), (1925, 462, 8.5), (1790, 480, 7),                   # 사다리 병정 · 무릎 부은 여자 · 차는 병정
    (1518, 655, 8), (1618, 650, 8), (1716, 648, 8),                     # 경례하는 병정 셋
    (1760, 690, 7), (1830, 650, 8), (1905, 640, 9),                     # 지나가는 가족 셋
    (1739, 885, 6.5), (1654, 880, 6.5), (1579, 880, 6.5),               # 거북 등의 병정 셋(거북을 뒤집어 x' = 3344 − x)
    (1960, 965, 9.5),                                                  # 팔에 발진 난 사람
)
lay = layer(); d = ImageDraw.Draw(lay)
for cx, cy, r in BADGES: put_badge(d, cx, cy, r)
put(lay)

im.save(dst)
print('saved', dst)

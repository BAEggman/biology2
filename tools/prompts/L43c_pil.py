#!/usr/bin/env python3
# L43c_pil.py <in.png> <out.png> — 바탕(+ 구역 편집) 뒤의 PIL 손질.
# 이 그림의 뼈대인 「끈 한 가닥에 무엇이 어떤 차례로 꿰였나」는 Gemini 에게 맡기지 않고 여기서 그린다:
#  ① 금빛 짚끈(DNA) — 바닥 빛(바닥 · 그림자)인 곳에만 그려 물건 뒤로 지나가게 한다(물건마다 끈이 꿰뚫고 나온다).
#     차례: [담 밑] — 사이렌 상자 — 꺼진 인쇄 기계 — (오른쪽 가장자리를 돌아) — 청록 · 회색(빈 단) · 청록 깔판 — 켜진 인쇄 기계 — 빨간 방석
#           — 먼 고리(집사의 손이 꼭대기) — 빈 단 — 응원 단 — [그림 아래로]
#  ② 깔판 셋(청록 = 엑손 · 회색 = 인트론 · L43b 의 빛깔) — 가운데 회색 깔판 위에 빈 응원 단이 놓인다.
#  ③ 응원 단 앞면의 빛깔 자리 셋(응원 단 = 빨강 · 노랑 · 파랑 — 응원단원의 폼폼과 같은 차례 / 빈 단 둘은 다른 빛깔).
import sys, math, numpy as np
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); W, H = im.size
a = np.array(im).astype(int)
INK = (24, 20, 18, 255)

# ── ⓞ 빨간 방석과 그 위 일꾼을 왼쪽으로 32 px 옮긴다 — 바탕 그림에서는 방석이 인쇄 기계의 벨트에 바짝 붙어(틈 3 ~ 5 px)
#      끈이 방석 밑에서 나와 기계로 드는 것이 작은 세모 조각으로만 보였다(일치 검사 5 · 7회: 「이어짐이 약하다 · 닿는지 불분명」).
MV = 32
_X0, _X1, _Y0, _Y1 = 930, 1100, 700, 864
_G = np.array([239, 232, 202], float)
_reg = a[_Y0:_Y1, _X0:_X1].astype(float); _dd = np.abs(_reg - _G).max(axis=2)
_yy, _xx = np.mgrid[_Y0:_Y1, _X0:_X1]
_xb = np.where(_yy <= 792, 1083, np.where(_yy <= 845, 1097, np.where(_yy <= 851, 1094, 1084)))   # 이 금의 오른쪽은 인쇄 기계(톱니 · 벨트 · 크랭크) — 그대로 둔다
_mov = _xx < _xb
_al = np.clip((_dd - 5) / 7, 0, 1) * _mov                                          # 바닥 빛에서 먼 만큼 = 물건(일꾼 · 방석 · 그림자)
assert _al[0].max() == 0 and _al[-1].max() == 0 and _al[:, :MV + 2].max() == 0     # 상자 가장자리는 맨바닥이어야 한다
_out = _reg.copy(); _out[_mov] = _G                                                # 옛 자리는 바닥 빛으로
_sh = np.zeros_like(_al); _sh[:, :-MV] = _al[:, MV:]; _sr = np.zeros_like(_reg); _sr[:, :-MV] = _reg[:, MV:]
_out = _out * (1 - _sh[..., None]) + _sr * _sh[..., None]
# 방석 그림자의 오른쪽 끝은 바탕에서 벨트 뒤에 숨어 있었다 → 그림자 타원(바탕에서 맞춘 것: 중심 (1035.3, 835.9) · 반지름 66.2 × 22.53 · 빛 (182, 176, 161))으로 마저 그린다
_ex = np.sqrt(((_xx - (1035.3 - MV)) / 66.2) ** 2 + ((_yy - 835.9) / 22.53) ** 2)
_sa = np.clip((1 - _ex) * 22.53 / 1.6, 0, 1) * (_xx >= 1097 - MV - 14)
_out = np.minimum(_out, _G * (1 - _sa[..., None]) + np.array([182, 176, 161.]) * _sa[..., None])   # 어두운 쪽만 남긴다 — 방석과 테는 그대로
a[_Y0:_Y1, _X0:_X1] = np.round(_out).astype(int)
im = Image.fromarray(a.astype(np.uint8))

# ── ⓪ 물건 둘레의 흰 번짐(바탕 그림을 키울 때 · 구역을 붙일 때 남는 후광 1 ~ 4 px)을 바닥 빛으로 — 끈 · 깔판이 그 자리에서 끊기지 않게(L10b 에서 배운 것)
import cv2
GND = np.array([239, 232, 202])
isg = np.abs(a - GND).max(axis=2) <= 7
inkm = a.max(axis=2) < 90
light = a.min(axis=2) >= 180
n, lab = cv2.connectedComponents(light.astype(np.uint8), connectivity=4)
cnt = np.bincount(lab[isg], minlength=n); gl = np.where(cnt >= 1500)[0]; gl = gl[gl != 0]
brighter = (a[..., 0] >= 242) & (a[..., 1] >= 236) & (a[..., 2] >= 207)
halo = brighter & np.isin(lab, gl) & (cv2.dilate(inkm.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
halo[:176] = False
a[halo] = GND; im = Image.fromarray(a.astype(np.uint8))
print('후광', int(halo.sum()), 'px')

# ── 종이띠 맨 아래: 바탕 그림의 잿빛 끝 줄(y 1141 ~)과 구역을 붙인 자리의 옅은 줄(y ≈ 1131)을 종이 빛으로
import cv2
reg = a[1100:1144, 1190:1440].copy()
pap = ((reg.min(axis=2) >= 168) & (reg[..., 0] - reg[..., 2] < 22)).astype(np.uint8)
_n, _lab = cv2.connectedComponents(pap, connectivity=4)
pap = _lab == _lab[10, 110]                                                       # 종이 안쪽 한 점(1300, 1110)에서 이어진 곳만 — 검은 테 밖의 그림자는 건드리지 않는다
reg[pap] = (254, 254, 254); a[1100:1144, 1190:1440] = reg
# 종이띠 왼쪽 테와 그 곁 그림자: 붙인 자리 아래 여섯 줄이 어긋난다 → y 1127 줄을 테의 기울기대로 밀어 아래로 이어 그린다
def _edge(y): return 1150 + int(np.argmax(a[y, 1150:1320].max(axis=1) < 80))     # 그 줄에서 종이띠 왼쪽 검은 테의 x
_sl = (_edge(1126) - _edge(1096)) / 30.0
for y in range(1128, 1144):
    sh = int(round(_sl * (y - 1127)))
    a[y, 1140 + sh:1290 + sh] = a[1127, 1140:1290]

im = Image.fromarray(a.astype(np.uint8))

# ── 바닥 가리개: 바닥 빛(239, 232, 202) 또는 그림자 빛(≈ 188, 183, 162)과 그 사이
R_, G_, B_ = a[..., 0], a[..., 1], a[..., 2]
ground = (np.abs(a - GND).max(axis=2) <= 14) | ((R_ >= 168) & (R_ <= 236) & (R_ - B_ >= 14) & (R_ - B_ <= 46) & (np.abs(R_ - G_) <= 12))
ground[:176] = False                                                              # 뒤 담 밑 줄 위는 바닥이 아니다
ground = cv2.morphologyEx(ground.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0   # 한두 픽셀짜리 티는 바닥으로 친다
gmask = Image.fromarray((ground * 255).astype(np.uint8))

S = 3
def spline(pts, n=24):
    """Catmull-Rom 으로 매끈하게."""
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = [np.array(p, float) for p in P[i - 1:i + 3]]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(P[-2])); return out
def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay, clip=True):
    """겹을 줄여 얹는다 — clip 이면 바닥인 곳에만."""
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    if clip:
        al = np.asarray(small.split()[3]).astype(np.float32) * (np.asarray(gmask).astype(np.float32) / 255.0)
        small.putalpha(Image.fromarray(al.astype(np.uint8)))
    base = im.convert('RGBA'); base.alpha_composite(small); im = base.convert('RGB')

# ── ② 깔판 셋(끈보다 먼저 — 끈이 그 위를 지난다)
TEAL, GREY = (70, 178, 172, 255), (158, 162, 170, 255)
lay = layer(); d = ImageDraw.Draw(lay)
for x0, x1, col in ((1334, 1470, TEAL), (1490, 1724, GREY), (1744, 1880, TEAL)):
    q = [(x0 * S, 852 * S), (x1 * S, 852 * S), ((x1 + 20) * S, 776 * S), ((x0 + 20) * S, 776 * S)]
    d.polygon(q, fill=col); d.line(q + [q[0]], fill=INK, width=int(2.6 * S), joint='curve')
put(lay)

# ── ① 금빛 짚끈
ROPE, ROPE_D, ROPE_L = (236, 196, 96, 255), (176, 128, 44, 255), (250, 226, 150, 255)
RW, RO = 13.0, 2.4
def rope(pts, clip=True):
    q = spline(pts)
    # 길을 1 px 걸음으로 고르게 다시 찍는다 — 굵은 꺾은선은 이음매 바깥쪽에 쐐기 틈이 생긴다(PIL) → 원반을 촘촘히 찍어 그린다
    u = [q[0]]; acc = 0.0
    for (x0, y0), (x1, y1) in zip(q, q[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg == 0: continue
        t = 1.0 - acc
        while t <= seg:
            u.append((x0 + (x1 - x0) * t / seg, y0 + (y1 - y0) * t / seg)); t += 1.0
        acc = (acc + seg) % 1.0
    lay = layer(); d = ImageDraw.Draw(lay)
    for r, col in (((RW + 2 * RO) / 2, INK), (RW / 2, ROPE)):
        for x, y in u: d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=col)
    # 꼬임 줄 — 길을 따라 9 px 마다 비스듬한 짧은 줄
    for k in range(5, len(u) - 1, 9):
        (x0, y0), (x1, y1) = u[k - 1], u[k + 1]; seg = math.hypot(x1 - x0, y1 - y0)
        tx, ty = (x1 - x0) / seg, (y1 - y0) / seg; nx, ny = -ty, tx; x, y = u[k]
        h = RW * 0.44
        d.line([((x - nx * h - tx * 3.2) * S, (y - ny * h - ty * 3.2) * S), ((x + nx * h + tx * 3.2) * S, (y + ny * h + ty * 3.2) * S)], fill=ROPE_D, width=int(1.7 * S))
    put(lay, clip)

# 꺼진 유전자 쪽: 담 밑 → 사이렌 상자 → 꺼진 인쇄 기계 → 오른쪽 가장자리 → 깔판 → 켜진 인쇄 기계
rope([(812, 168), (822, 222), (852, 292), (902, 346), (950, 370), (1030, 368), (1109, 362), (1200, 356), (1400, 352), (1560, 356), (1640, 360), (1672, 362)])
# (기계 속은 그리지 않는다 — 굴대 사이 틈으로 끈 토막이 비쳐 지저분하다) 꺼진 인쇄 기계의 오른쪽 옆틀 → 오른쪽 가장자리 → 깔판 → 켜진 인쇄 기계의 오른쪽 옆틀
rope([(1834, 400), (1850, 403), (1884, 416), (1936, 452), (1990, 540), (2006, 660), (1968, 768), (1884, 810), (1700, 806), (1524, 812), (1340, 815), (1308, 814), (1292, 814)])
# 켜진 인쇄 기계(왼쪽 옆틀 뒤로 든다) → 빨간 방석 밑 → 먼 고리의 돌아오는 가닥 → 집사의 손
rope([(1128, 822), (1112, 823), (1094, 826), (1072, 830), (1040, 832), (1008, 832), (958, 830), (942, 808), (926, 760), (884, 660), (770, 562), (650, 524), (560, 520),
      (490, 520), (458, 502), (450, 470), (449, 436)])
# 집사의 손 → 먼 고리의 나가는 가닥(왼쪽 가장자리를 돌아) → 빈 단 → 응원 단. 두 가닥이 손 밑에서 나란히 내려오다 갈라진다(접어 쥔 꼴)
rope([(431, 436), (431, 470), (424, 502), (396, 522), (330, 538), (160, 530), (62, 548), (20, 606), (18, 692), (42, 752), (76, 764), (160, 766), (248, 768),
      (262, 792), (280, 836), (304, 888), (336, 914), (368, 916), (440, 916)])
# 응원 단 → 그림 아래로(끈은 더 이어진다)
rope([(600, 916), (656, 920), (672, 962), (682, 1040), (692, 1150)])

# ── 빈 응원 단 둘은 다시 그린다(바탕 그림의 것은 키운 그대로라 흐리다 — 구역 편집에 넣지 않았다). 끈보다 뒤에 그려 끈이 단을 꿰뚫어 보이게.
WOODF, WOODT, WOODS = (206, 160, 104, 255), (230, 192, 138, 255), (182, 136, 86, 255)
lay = layer(); d = ImageDraw.Draw(lay)
def box3(x0, y0, x1, y1, dx, dy):
    """앞면 (x0, y0) ~ (x1, y1) · 윗면과 옆면은 (dx, −dy) 만큼 뒤로."""
    T = lambda pts: [(x * S, y * S) for x, y in pts]
    for pts, col in (([(x0, y0), (x1, y0), (x1 + dx, y0 - dy), (x0 + dx, y0 - dy)], WOODT), ([(x1, y0), (x1 + dx, y0 - dy), (x1 + dx, y1 - dy), (x1, y1)], WOODS), ([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], WOODF)):
        q = T(pts); d.polygon(q, fill=col); d.line(q + [q[0]], fill=INK, width=int(3.2 * S), joint='curve')
        for x, y in q: r = 1.6 * S; d.ellipse([x - r, y - r, x + r, y + r], fill=INK)
box3(73, 734, 226, 792, 24, 19)                                                    # 먼 고리 도중의 빈 단
box3(1522, 774, 1661, 827, 23, 19)                                                 # 회색 깔판 위의 빈 단
put(lay, clip=False)

# ── ③ 단 앞면의 빛깔 자리
RED, YEL, BLU, GRN, ORG, PUR = (224, 60, 55, 255), (246, 206, 64, 255), (66, 128, 222, 255), (86, 176, 96, 255), (240, 140, 50, 255), (150, 92, 200, 255)
lay = layer(); d = ImageDraw.Draw(lay)
def spot(cx, cy, r, col):
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=col, outline=INK, width=int(2.2 * S))
for cx, col in ((426, RED), (506, YEL), (586, BLU)): spot(cx, 914, 15, col)                 # 응원 단
for cx, col in ((112, GRN), (150, ORG), (188, PUR)): spot(cx, 763, 11, col)                 # 먼 고리 도중의 빈 단
for cx, col in ((1557, PUR), (1592, RED), (1627, GRN)): spot(cx, 800, 10, col)              # 회색 깔판 위의 빈 단
put(lay, clip=False)

im.save(dst)
print('ok', dst, '바닥', round(float(ground.mean()), 3))

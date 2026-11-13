#!/usr/bin/env python3
# L12f_pil1.py <in.png> <out.png> — 바탕(s2) + 구역 편집(E1 쌍둥이 · E2 수반 위 두 사람) 뒤의 PIL 손질.
# 세어야 하는 것 · 방향이 곧 뜻인 것 · 덱의 약속 물건은 Gemini 에게 맡기지 않고 여기서 그린다:
#  ① 붉은 관의 흰 꺾쇠(관제탑 쪽으로)  ② 통 가장자리의 불붙은 성냥(↑) · 놓인 배턴(↓)  ③ 목 방의 흰 바람
#  ④ 입 안: 큰 부스러기 넷을 지우고 → 가위에 걸린 포도 줄 + 끊긴 포도 짝 · 주둥이 셋 밑의 녹는 초록 세균 · 막대사탕 · 흰 소금
#  ⑤ 쇠살문 고리에 건 줄 셋(요원 허리 · CCTV 기둥 · 지프)  ⑥ 차단기 끝의 두 머리 굽은 화살
#  ⑦ 가윗날 사이 물방울 · 초록 병의 넘치는 거품 · 전선 위 노란 불꽃 · 운하 물빛 경계 풀기 · 지프 앞유리 하늘빛
# 차례: L12f_pil0.py → (E2 · E1 · E3 붙임) → 이 파일.
import sys, math, numpy as np
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGBA')
INK = (24, 20, 18, 255); WHITE = (255, 255, 255, 255)

class Patch:
    """(x0, y0) ~ (x1, y1)을 S 배로 그려 줄여 얹는다(매끈한 선)."""
    def __init__(s, x0, y0, x1, y1, S=4):
        s.b = (x0, y0, x1, y1); s.S = S; s.lay = Image.new('RGBA', ((x1 - x0) * S, (y1 - y0) * S), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.lay)
    def T(s, pts): return [((x - s.b[0]) * s.S, (y - s.b[1]) * s.S) for x, y in pts]
    def line(s, pts, fill, w, cap=True):
        W = max(1, int(round(w * s.S))); q = s.T(pts); s.d.line(q, fill=fill, width=W, joint='curve')
        if cap:
            for x, y in (q[0], q[-1]): s.d.ellipse([x - W / 2, y - W / 2, x + W / 2, y + W / 2], fill=fill)
    def oline(s, pts, fill, w, o=2.2, ink=INK): s.line(pts, ink, w + 2 * o); s.line(pts, fill, w)
    def poly(s, pts, fill, ink=INK, o=2.2):
        q = s.T(pts); s.d.polygon(q, fill=fill)
        if ink: s.d.line(q + [q[0]], fill=ink, width=int(round(o * s.S)), joint='curve')
    def ell(s, cx, cy, rx, ry, fill, ink=INK, o=2.2):
        (x0, y0), (x1, y1) = s.T([(cx - rx, cy - ry), (cx + rx, cy + ry)]); s.d.ellipse([x0, y0, x1, y1], fill=fill, outline=ink, width=int(round(o * s.S)) if ink else 0)
    def done(s):
        x0, y0, x1, y1 = s.b; small = s.lay.convert('RGBa').resize((x1 - x0, y1 - y0), Image.LANCZOS).convert('RGBA'); im.alpha_composite(small, (x0, y0))

def bez(p0, p1, p2, n=24): return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [k / n for k in range(n + 1)]]
def rot(pts, cx, cy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg)); return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]
def block_arrow(P, cx, y_tail, y_tip, w=9, head=17, fill=WHITE):
    """세로 블록 화살(흰 속 · 검은 테) — y_tip 쪽이 머리."""
    sg = 1 if y_tip > y_tail else -1; yb = y_tip - sg * head * 0.95
    P.poly([(cx - w / 2, y_tail), (cx + w / 2, y_tail), (cx + w / 2, yb), (cx + head / 2 + 3, yb), (cx, y_tip), (cx - head / 2 - 3, yb), (cx - w / 2, yb)], fill, INK, 2.6)

a = np.array(im)
def erase_disc(cx, cy, r):
    """둥근 것을 둘레 빛(고리의 가운뎃값)으로 메운다."""
    global a
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]; d2 = (xx - cx) ** 2 + (yy - cy) ** 2
    ring = (d2 > (r + 3) ** 2) & (d2 <= (r + 8) ** 2); col = np.median(a[ring][:, :3], axis=0)
    a[d2 <= (r + 1.5) ** 2, :3] = col

# ④-가 입 안의 큰 부스러기 넷 · 잔 부스러기 둘을 지운다(그 자리에 포도 줄 · 침에 섞인 것이 온다) — 이빨 곁의 작은 둘은 남긴다
for cx, cy, r in [(402, 621, 13), (432, 649, 13), (392, 661, 13), (414, 707, 13), (370, 632, 5), (381, 637, 5)]: erase_disc(cx, cy, r)
a[558:568, 602:647, :3] = (184, 139, 129)                       # 목 방: 지운 빵 덩이의 남은 점선 자국
# 운하 물: 맑아진 물(밝은 하늘빛)과 그 뒤 물(조금 짙은 하늘빛)의 세로 경계가 「이음매」로 읽힌다 → 물빛 화소만 가로로 부드럽게 잇는다
LIGHT, MID = np.array([193, 225, 244.]), np.array([158, 203, 232.])
reg = a[862:998, 1440:1700, :3].astype(float); xs = np.arange(1440, 1700)[None, :, None]
tt = np.clip((xs - 1450) / 230.0, 0, 1); tt = tt * tt * (3 - 2 * tt)
isw = (np.abs(reg - LIGHT).sum(axis=2) < 34) | (np.abs(reg - MID).sum(axis=2) < 34) | ((np.abs(reg - (LIGHT + MID) / 2).sum(axis=2) < 40))
grad = LIGHT + (MID - LIGHT) * tt
a[862:998, 1440:1700, :3] = np.where(isw[..., None], np.broadcast_to(grad, reg.shape), reg).astype(np.uint8)
# 붉은 물길의 오른쪽 끝: 오름 관 밑에 바탕이 네모로 비쳐 「단차」로 읽힌다 → 붉게 메우고 아랫선을 끝까지
for y in range(503, 541): a[y, 2023:2043, :3] = a[y, 2019, :3]                 # 줄마다 왼쪽 이웃의 붉은빛으로
a[541:545, 2026:2046, :3] = (30, 18, 16); a[520:545, 2043:2046, :3] = (30, 18, 16)
# 병사 등 뒤(지운 우편함 자리의 가장자리)에 남은 옅은 세로 줄 — 밝은 화소만 왼쪽 맨 바탕 빛으로
for y in range(428, 483):
    row = a[y, 960:973, :3].astype(int); m = row.min(axis=1) > 205; row[m] = a[y, 712, :3]; a[y, 960:973, :3] = row.astype(np.uint8)
# 앞치마의 흐릿한 노란 이삭 무늬: 누런 화소만 앞치마 흰빛으로(네모로 덮으면 「덧댄 조각」이 된다) — 또렷한 이삭은 아래에서 다시 그린다
ap = a[642:714, 521:551, :3].astype(int); yl = (ap[..., 0] - ap[..., 2] > 22) & (ap[..., 0] > 185) & (ap[..., 1] > 165)
wh = np.median(ap[(ap.min(axis=2) > 235)], axis=0) if (ap.min(axis=2) > 235).any() else np.array([250, 250, 250])
ap[yl] = wh; a[642:714, 521:551, :3] = ap.astype(np.uint8)
# 쌍둥이(E1) 붙인 자리의 바탕: 옛 그림의 옅은 세로 얼룩 → 모랫빛에 가까운 화소를 모랫빛 하나로
tw = a[622:864, 1700:1996, :3].astype(int); SAND = np.array([232, 219, 185]); tm = np.abs(tw - SAND).sum(axis=2) < 44
tw[tm] = SAND; a[622:864, 1700:1996, :3] = tw.astype(np.uint8)
# 지프 앞유리: 흰 막대(「분필」로 읽힘) → 유리 하늘빛
ws = a[1012:1052, 1338:1362, :3].astype(int); wm = (ws.min(axis=2) > 150)
ws[wm] = (ws[wm] * 0.35 + np.array([120, 190, 228]) * 0.65).astype(int); a[1012:1052, 1338:1362, :3] = ws.astype(np.uint8)
im = Image.fromarray(a, 'RGBA')

# ① 붉은 관의 흰 꺾쇠 — 맨 위 관은 왼쪽(관제탑)으로 · 오른쪽 끝 오름 관은 위로 · 통 가장자리 가지 관도 위로
P = Patch(560, 14, 2048, 64)
for x in (660, 760, 1010, 1190, 1370, 1550, 1730, 1910): P.line([(x + 8, 30), (x - 5, 39), (x + 8, 48)], WHITE, 3.4)
P.done()
P = Patch(2006, 60, 2048, 500)
for y in (110, 200, 290, 380, 462): P.line([(2020, y + 8), (2029.5, y - 5), (2039, y + 8)], WHITE, 3.4)
P.done()
P = Patch(846, 60, 880, 420)
for y in (120, 220, 320): P.line([(857, y + 5), (862, y - 3), (867, y + 5)], WHITE, 2.4)
P.done()

# ② 통 가장자리: 불붙은 성냥(ECL · 히스타민 — 위 화살) · 놓인 배턴(D · 소마토스타틴 — 아래 화살)
P = Patch(880, 300, 980, 496)
P.oline([(902, 481), (902, 432)], (224, 188, 126, 255), 6.5)                                             # 성냥개비
P.ell(902, 428, 5.5, 7, (150, 40, 34, 255))                                                              # 성냥 머리
fl = [(902, 376), (910, 392), (915, 406), (912, 419), (902, 425), (892, 419), (889, 406), (894, 392)]
P.poly(fl, (246, 140, 34, 255), INK, 2.4)
P.poly([(902, 394), (907, 404), (908, 413), (902, 419), (896, 413), (897, 404)], (255, 224, 90, 255), None)
block_arrow(P, 902, 366, 322)                                                                             # ↑
bt = rot([(920, 476), (966, 476)], 943, 476, -5)                                                         # 놓인 배턴(L49a 의 그 배턴) — 가늘고 긴 주황 막대 · 끝에 흰 띠(굵으면 「빵 롤 · 두루마리」로 읽힌다)
P.oline(bt, (232, 120, 44, 255), 8.6)
for s0 in (0.07, 0.93):
    q = (bt[0][0] + (bt[1][0] - bt[0][0]) * s0, bt[0][1] + (bt[1][1] - bt[0][1]) * s0)
    P.line([(q[0] - 0.2, q[1] - 3.6), (q[0] + 0.4, q[1] + 3.6)], (255, 250, 240, 255), 2.6, cap=False)
block_arrow(P, 944, 404, 450)                                                                             # ↓
P.done()

# ③ 목 방: 콧길에서 내려오는 흰 바람(지운 빵 덩이 자리) + 고리 진 관으로 드는 바람
P = Patch(590, 470, 662, 730)
W2 = (255, 255, 255, 235)
P.line(bez((600, 486), (636, 490), (640, 524)), W2, 3.2); P.line(bez((640, 524), (641, 540), (628, 540)) + bez((628, 540), (620, 538), (624, 530))[1:], W2, 3.2)
P.line(bez((604, 506), (622, 512), (618, 548)), W2, 3.0); P.line(bez((618, 548), (616, 562), (606, 558))[0:18], W2, 3.0)
P.line(bez((650, 654), (648, 684), (628, 694)) + bez((628, 694), (612, 700), (612, 716))[1:], W2, 3.4)      # 고리 진 관으로 드는 바람 — 끝을 말아 「바람」으로
P.line(bez((640, 668), (634, 684), (622, 684)) + bez((622, 684), (614, 683), (617, 676))[1:], W2, 2.8)
P.done()

# ④ 입 안
P = Patch(340, 572, 580, 740)
GR, GRD = (150, 72, 190, 255), (44, 22, 62, 255)
def grape(x, y, r=10):
    P.ell(x, y, r, r, GR, GRD, 2.4); P.ell(x - r * 0.32, y - r * 0.36, r * 0.26, r * 0.2, (206, 150, 232, 255), None)
# 포도 줄(곧은 실에 꿴 포도 = 녹말 · 아밀로스): 빵 끝에서 가위 날 사이까지 — 실은 가늘고 희게 · 끝은 늘어지게(굵고 곧으면 「나무 꼬치」로 읽힌다)
TH, THD = (250, 246, 236, 255), (70, 50, 40, 255)
def thread(pts): P.line(pts, THD, 3.6); P.line(pts, TH, 1.9)
thread(bez((345, 676), (350, 664), (358, 669), 8) + [(366, 669.4), (432, 671.2)] + bez((432, 671.2), (456, 679), (478, 673), 10)[1:])
for x in (366, 388, 410, 432): grape(x, 669 + (x - 350) * 0.027)
# 끊긴 포도 짝(엿당) 둘 — 혀 위에 · 양 끝에 잘린 실 꼬리
for (x1, y1), (x2, y2) in [((454, 711), (474, 707)), ((386, 724), (406, 720))]:
    ux, uy = (x2 - x1) / 20.4, (y2 - y1) / 20.4
    thread(bez((x1 - ux * 17, y1 - uy * 17 + 5), (x1 - ux * 13, y1 - uy * 13 - 2), (x1, y1), 6) + [(x2, y2)] + bez((x2, y2), (x2 + ux * 13, y2 + uy * 13 + 3), (x2 + ux * 17, y2 + uy * 17 - 4), 6)[1:])
    grape(x1, y1, 9.5); grape(x2, y2, 9.5)
# 주둥이 1(x 431) 밑: 방울 맞고 껍질이 금 가 녹는 초록 알약 세균(라이소자임)
bx, by, bang = 424, 626, 18
body = rot([(bx - 11, by), (bx + 11, by)], bx, by, bang)
P.oline(body, (104, 190, 84, 255), 15, 2.2)
P.line(rot([(bx - 3, by - 8), (bx + 1, by - 2), (bx - 3, by + 2), (bx + 1, by + 8)], bx, by, bang), INK, 1.8, cap=False)        # 금
P.line(rot([(bx + 8, by - 8), (bx + 11, by - 3), (bx + 8, by + 1)], bx, by, bang), INK, 1.6, cap=False)
for dx, dy in [(-24, -8), (-27, 5), (22, 13)]: P.ell(bx + dx, by + dy, 3.2, 2.6, (104, 190, 84, 255), INK, 1.4)             # 떨어져 나간 조각
P.line(rot([(bx - 13, by - 3), (bx - 9, by + 1)], bx, by, bang), INK, 1.5, cap=False); P.line(rot([(bx - 13, by + 1), (bx - 9, by - 3)], bx, by, bang), INK, 1.5, cap=False)   # X 눈
# 주둥이 2(x 485) 밑: 분홍 막대사탕(점액성 당단백질 — 막대사탕 = 당 사슬)
lx, ly = 474, 624
P.oline([(lx - 5, ly + 8), (lx - 13, ly + 25)], (250, 244, 232, 255), 2.8, 1.5)
P.ell(lx, ly, 10.5, 10.5, (244, 122, 172, 255), INK, 2.2)
sp = [(lx + 6.5 * (1 - k / 26) * math.cos(k * 0.62), ly + 6.5 * (1 - k / 26) * math.sin(k * 0.62)) for k in range(27)]
P.line(sp, (255, 236, 244, 255), 2.2, cap=False)
# 주둥이 1 의 방울 왼쪽: 흰 소금 알갱이 셋(염) — 일꾼 머리 위에 두면 「어지러운 별」로 읽힌다
for cx, cy, ang in [(397, 585, 18), (411, 600, -22), (384, 598, 40)]:
    P.poly(rot([(cx - 4.2, cy - 4.2), (cx + 4.2, cy - 4.2), (cx + 4.2, cy + 4.2), (cx - 4.2, cy + 4.2)], cx, cy, ang), WHITE, INK, 1.6)
P.done()

# 이빨 곁의 잔 부스러기 넷(큰 것을 지운 대신 — 잘게 부서짐)
P = Patch(338, 585, 384, 704)
for cx, cy, r, ang in [(349, 598, 5, 20), (352, 637, 6, -30), (374, 647, 4, 10), (368, 695, 5, 40)]:
    q = [(cx + r * 1.25 * math.cos(math.radians(k * 45)) * (1 + 0.16 * ((k * 7) % 3 - 1)), cy + r * 0.85 * math.sin(math.radians(k * 45)) * (1 + 0.16 * ((k * 5) % 3 - 1))) for k in range(8)]
    P.poly(rot(q, cx, cy, ang), (216, 164, 98, 255), (112, 72, 34, 255), 1.6)
P.done()

# 앞치마의 밀 이삭(흐릿해 「노란 얼룩」으로 읽힘) — 아래 폭의 무늬를 희게 지우고 또렷한 금빛 이삭 하나를 · 가슴판 무늬는 지운다
P = Patch(516, 640, 562, 716)
GOLD, GOLDD = (236, 178, 30, 255), (140, 96, 10, 255)
s0, s1 = (529, 707), (551, 677)                                                 # 줄기(왼쪽 아래 → 오른쪽 위)
P.line([s0, s1], GOLDD, 1.6, cap=False)
ux, uy = (s1[0] - s0[0]) / 37.2, (s1[1] - s0[1]) / 37.2; nx, ny = -uy, ux
for k in range(4):
    cx, cy = s0[0] + ux * (12 + k * 7), s0[1] + uy * (12 + k * 7)
    for sg in (-1, 1):
        kx, ky = cx + nx * 3.4 * sg + ux * 1.5, cy + ny * 3.4 * sg + uy * 1.5
        P.poly(rot([(kx - 3.6, ky), (kx, ky - 1.9), (kx + 3.6, ky), (kx, ky + 1.9)], kx, ky, math.degrees(math.atan2(uy, ux)) + 28 * sg), GOLD, GOLDD, 0.9)
tx, ty = s1[0] + ux * 2.5, s1[1] + uy * 2.5
P.poly(rot([(tx - 3.8, ty), (tx, ty - 1.9), (tx + 3.8, ty), (tx, ty + 1.9)], tx, ty, math.degrees(math.atan2(uy, ux))), GOLD, GOLDD, 0.9)
P.done()

# ⑤ 쇠살문에 건 줄 셋 — 요원 허리 · CCTV 기둥 · 지프 꽁무니
ROPE, ROPED = (198, 152, 92, 255), (58, 38, 20, 255)
P = Patch(1090, 720, 1500, 1100, S=3)
def rope(pts, w=5.5):
    P.oline(pts, ROPE, w, 1.8, ROPED)
    for k in range(2, len(pts) - 2, 3):                                           # 꼬임 무늬
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]; dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
        P.line([(x0 + nx * w * 0.45 - dx / L * 2, y0 + ny * w * 0.45 - dy / L * 2), (x0 - nx * w * 0.45 + dx / L * 2, y0 - ny * w * 0.45 + dy / L * 2)], ROPED, 1.1, cap=False)
def knot(x, y, r=6.5): P.ell(x, y, r, r, ROPE, ROPED, 1.8)
# 요원: 허리를 두른 줄 + 고리까지
rope(bez((1109, 741), (1148, 752), (1188, 743), 14), 5.0); rope(bez((1109, 754), (1148, 765), (1188, 756), 14), 5.0)      # 허리(팔째)를 두 번 감았다
rope(bez((1189, 752), (1194, 798), (1172, 833), 16)); knot(1189, 750, 6); knot(1171, 835, 6)                       # 요원의 줄은 고리 왼쪽에 매듭
# CCTV 기둥
rope(bez((1196, 846), (1326, 856), (1450, 808), 40)); knot(1195, 846, 6)                                                # 카메라 기둥의 줄은 고리 오른쪽에 따로 매듭
rope([(1450, 798), (1472, 801)], 4.6); rope([(1450, 808), (1472, 811)], 4.6); knot(1449, 804, 6)                        # 기둥을 두 번 감고 매듭
# 지프: 문 가운데 고리 → 꽁무니
rope(bez((1173, 940), (1176, 1010), (1204, 1076), 30)); knot(1205, 1077)
knot(1173, 939, 6.5)
P.done()

# ⑥ 차단기: 팔 끝을 따라 굽은 두 머리 화살(올렸다 · 내렸다)
P = Patch(0, 500, 130, 610)
cx0, cy0, rr = 112, 708, 178
arc = [(cx0 + rr * math.cos(math.radians(t)), cy0 - rr * math.sin(math.radians(t))) for t in range(99, 124)]
P.line(arc, INK, 4.2, cap=False)
def head(p, q):                                                                    # p 에서 q 쪽으로 난 머리
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    P.poly([(q[0] + ux * 9, q[1] + uy * 9), (q[0] - ux * 5 + nx * 8, q[1] - uy * 5 + ny * 8), (q[0] - ux * 5 - nx * 8, q[1] - uy * 5 - ny * 8)], INK, None)
head(arc[2], arc[0]); head(arc[-3], arc[-1])
P.done()

# ⑦ 일치 검사 2회 뒤 덧그림: 가윗날 사이의 물방울(물로 끊는다) · 초록 병에서 넘치는 베이지 거품(기둥 인부도 붓는다) · 전선 위의 노란 불꽃(신경 신호)
P = Patch(450, 650, 490, 690)
dr = [(466, 657), (470.5, 666), (470, 671), (466, 674), (462, 671), (461.5, 666)]
P.poly(dr, (96, 176, 236, 255), INK, 1.6); P.ell(464.6, 668, 1.3, 2.0, (214, 238, 252, 255), None)
P.done()
P = Patch(830, 708, 896, 830)
FO, FOD = (230, 210, 164, 255), (112, 88, 54, 255)
for cx, cy, r in [(873, 757, 5.2), (876, 768, 4.2), (874, 778, 3.2)]: P.ell(cx, cy, r, r * 0.95, FO, FOD, 1.6)                     # 병 어깨로 넘쳐 내리는 거품 방울 셋(줄기로 그리면 「관」으로 읽힌다)
for cx, cy, r in [(849, 743, 8), (872, 743, 8.5), (860, 734, 11), (861, 746, 8)]: P.ell(cx, cy, r, r * 0.9, FO, FOD, 1.7)
for cx, cy, r in [(860, 738, 9), (853, 744, 6.4), (868, 744, 6.8)]: P.ell(cx, cy, r, r * 0.9, FO, None)                               # 거품 속을 메워 한 덩이로(병 주둥이 위로 솟은 거품)
for cx, cy in [(842, 729), (880, 727), (861, 719), (850, 722), (873, 720)]: P.ell(cx, cy, 2.6, 2.6, FO, FOD, 1.3)
P.done()
P = Patch(1755, 392, 1810, 456)                                                                          # 기름 공 사람 허리께 흰 종이 → 덮개 선을 그어 봉투로
P.line([(1768, 414), (1786, 427), (1794, 405)], INK, 1.8, cap=False)
P.done()
P = Patch(120, 340, 210, 430)
cx, cy = 166, 384
star = []
for k in range(14):
    ang = math.radians(k * 360 / 14 + 8); r = 21 if k % 2 == 0 else 9.5
    star.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
P.poly(star, (255, 222, 60, 255), INK, 2.0)
P.done()

im.convert('RGB').save(dst)
print('pil1 ok')

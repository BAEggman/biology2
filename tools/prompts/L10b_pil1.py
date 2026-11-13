#!/usr/bin/env python3
# L10b_pil1.py <in.png> <out.png> — 바탕 + 구역 편집 뒤의 PIL 손질.
# 세어야 하는 것 · 빛깔이 곧 뜻인 것 · 덱의 약속 물건은 Gemini 에게 맡기지 않고 여기서 그린다:
#  ① 객차의 창 빛깔 — 창 = 염기(초록 A · 파랑 U · 빨강 G · 노랑 C): AUG · GAG · CAA · ACC · UAA · UAG · UGA
#  ② 이젤의 체스판 64칸 — 금빛 구슬 61 + 작은 나무판 3
#  ③ 번쩍 든 손가락 끝의 갈고리 둘 + 접이 사다리 + 구슬(C · C · A + 아미노산)
#  ④ 입가의 말풍선 — 빛깔 네모 셋 → 구슬 하나
#  ⑤ 이정표 화살판의 빛깔 구슬 셋(빨강 · 파랑 · 초록) · 짐꾼 사슬의 앞 끝 파란 구슬(천막 사슬의 앞 끝 빨간 구슬은 Z7)
#  ⑥ 발끝의 열쇠(L10a 의 꼴 — 둥근 손잡이 고리 + 자루 + 넓적한 이빨 셋 · 셋째만 빨강) · 옛 끈의 겹줄 지움
#  ⑦ 마무리 손질 — 손님채 테두리의 틈 · 보라 단(한 빛으로 · 허벅지 밑까지) · 땅 위 물건 둘레의 흰 번짐(후광)
import sys, math, numpy as np
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGBA')
INK = (24, 20, 18, 255)
BASE = {'A': (86, 176, 96, 255), 'U': (66, 128, 222, 255), 'G': (226, 74, 62, 255), 'C': (246, 206, 64, 255)}
GOLD = (245, 196, 58, 255); PINK = (242, 128, 176, 255)
WOODC, GRAIN = (206, 160, 104, 255), (164, 120, 74, 255)

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
    def rrect(s, x0, y0, x1, y1, r, fill, ink=INK, o=2.2):
        (a, b), (c, e) = s.T([(x0, y0), (x1, y1)]); s.d.rounded_rectangle([a, b, c, e], radius=r * s.S, fill=fill, outline=ink, width=int(round(o * s.S)) if ink else 0)
    def done(s):
        x0, y0, x1, y1 = s.b; small = s.lay.convert('RGBa').resize((x1 - x0, y1 - y0), Image.LANCZOS).convert('RGBA'); im.alpha_composite(small, (x0, y0))

def rot(pts, cx, cy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg)); return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]
def arc(cx, cy, r, a0, a1, n=24): return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
def bead(P, cx, cy, r, col, o=2.0):
    P.ell(cx, cy, r, r, col, INK, o); P.ell(cx - r * 0.32, cy - r * 0.36, r * 0.30, r * 0.24, (255, 255, 255, 235), None)
def miniplank(P, x0, y0, x1, y1, o=1.8, deg=-9):
    """작은 나무판 — 셋이 든 나무판과 같은 빛 · 결 · 살짝 기울여 세움(문처럼 보이지 않게)."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; w = x1 - x0
    P.poly(rot([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], cx, cy, deg), (198, 146, 92, 255), INK, o)
    for t, k in ((0.3, 0.04), (0.55, -0.05), (0.78, 0.03)):
        P.line(rot([(x0 + w * t, y0 + 3), (x0 + w * (t + k), cy), (x0 + w * t, y1 - 3)], cx, cy, deg), (150, 104, 62, 255), 0.9, cap=False)
def hook(P, cx, cy, r=11, w=5.0, col=(168, 174, 186, 255)):
    """C 자로 굽은 쇠갈고리 — 오른쪽이 트였다."""
    P.oline(arc(cx, cy, r, 50, 310), col, w, 1.8)
def stepladder(P, cx, y0, h=44, half=15):
    """A 자로 벌어진 작은 접이 사다리 — 꼭대기 (cx, y0)."""
    for sx in (-1, 1): P.oline([(cx, y0), (cx + sx * half, y0 + h)], WOODC, 4.6, 1.8)
    for t in (0.38, 0.7): P.oline([(cx - half * t + 1, y0 + h * t), (cx + half * t - 1, y0 + h * t)], WOODC, 3.4, 1.6)
def glass(x0, y0, x1, y1, col):
    """창(유리)의 흰 속만 빛깔로 — 검은 테는 그대로."""
    a = np.array(im); reg = a[y0:y1, x0:x1, :3].astype(int)
    pane = (reg.min(axis=2) > 208) & ((reg.max(axis=2) - reg.min(axis=2)) < 40)
    lum = reg.mean(axis=2, keepdims=True) / 245.0
    out = np.clip(np.array(col[:3])[None, None, :] * np.clip(lum, 0.86, 1.04), 0, 255)
    reg[pane] = out[pane]; a[y0:y1, x0:x1, :3] = reg.astype(np.uint8)
    return Image.fromarray(a)


# ── ① 창 빛깔: 객차 일곱(왼 → 오) = AUG · GAG · CAA · ACC · UAA · UAG · UGA
WIN_X = [(163, 213, 263), (363, 413, 463), (773, 823, 873), (1173, 1223, 1273), (1368, 1418, 1467), (1563, 1613, 1663), (1758, 1808, 1858)]
CODONS = ['AUG', 'GAG', 'CAA', 'ACC', 'UAA', 'UAG', 'UGA']
for xs, cod in zip(WIN_X, CODONS):
    for x, b in zip(xs, cod): im = glass(x - 4, 585, x + 40, 634, BASE[b])
# 도색장의 객차: 첫 창을 칠하는 중(왼쪽 절반만 빨강 · 붓 끝도 빨강)
a = np.array(im); reg = a[918:964, 488:532, :3].astype(int)
pane = (reg.min(axis=2) > 208) & ((reg.max(axis=2) - reg.min(axis=2)) < 40)
SS = 6; lay = Image.new('L', (44 * SS, 46 * SS), 0); dd = ImageDraw.Draw(lay)                 # 칠한 쪽(왼쪽 절반)의 물결진 오른쪽 가장자리를 매끈하게
pts = [(0, 0)] + [((25 + 2.6 * math.sin(t / 4.6) + 1.2 * math.sin(t / 2.1)) * SS, t * SS) for t in np.arange(0, 46.01, 0.5)] + [(0, 46 * SS)]
dd.polygon(pts, fill=255); al = np.asarray(lay.resize((44, 46), Image.LANCZOS)).astype(float) / 255.0
al = al * pane
red = np.array(BASE['G'][:3], float)[None, None, :]
reg = reg * (1 - al[..., None]) + red * al[..., None]; a[918:964, 488:532, :3] = np.clip(reg + 0.5, 0, 255).astype(np.uint8)
br = a[914:942, 494:524, :3].astype(int); tip = (br[..., 0] > 110) & (br[..., 0] < 225) & (br[..., 1] > 60) & (br[..., 1] < 175) & (br[..., 2] > 30) & (br[..., 2] < 140) & (br[..., 0] - br[..., 2] > 40)
lum = br.mean(axis=2, keepdims=True) / 150.0
br[tip] = np.clip(np.array(BASE['G'][:3])[None, None, :] * np.clip(lum, 0.7, 1.05), 0, 255)[tip]; a[914:942, 494:524, :3] = br.astype(np.uint8)
# 노란 페인트 통 둘레의 흰 번짐(바탕 그림의 후광)을 땅 빛으로
hz = a[1000:1104, 842:922, :3].astype(int); halo = (hz[..., 0] > 236) & (hz[..., 1] > 236) & (hz[..., 2] > 198)
gnd = np.median(a[1090:1104, 760:840, :3].reshape(-1, 3), axis=0).astype(int)
hz[halo] = gnd; a[1000:1104, 842:922, :3] = hz.astype(np.uint8)
im = Image.fromarray(a)

# ── 발끝의 열쇠를 다시 그린다 — L10a 의 그 열쇠 꼴로: 둥근 손잡이 고리(구멍에 끈) + 자루 + 넓적한 이빨 셋(창 셋의 한가운데로).
#    셋째(셋째 창 위)만 빨간 고무 = L10a 의 요동 이빨. (막대에 가는 이빨 셋만 있던 첫 꼴은 일치 검사에서 「빗 · 선반」으로 읽혔다.)
KEYG, KEYR = (243, 200, 66, 255), (220, 54, 46, 255)
_a = np.array(im)
DOORBG = tuple(int(v) for v in np.median(_a[572:600, 741:749, :3].reshape(-1, 3), axis=0)) + (255,)      # 문틀 안 바탕(객차 왼쪽)
POSTC = tuple(int(v) for v in np.median(_a[602:640, 950:966, :3].reshape(-1, 3), axis=0)) + (255,)       # 오른쪽 보라 기둥
# 바탕 그림의 옛 끈이 새 끈(L10b_pil0.py 가 그은 것) 오른쪽에 흐린 겹줄로 남았다 → 줄마다 그 오른쪽의 바탕 빛으로 덮는다
for y in range(466, 542):
    xn = 970 + (957 - 970) * (y - 461) / (548 - 461)                                       # 새 끈의 가운데
    x0 = int(math.ceil(xn + 3.2))
    if y < 522: _a[y, x0:int(xn + 16), :3] = np.median(_a[y, int(xn + 18):int(xn + 26), :3], axis=0)      # 방 안 벽 · 바닥 줄 · 돔 밑 띠: 오른쪽이 같은 빛
    else: _a[y, x0:971, :3] = np.median(_a[y, 940:948, :3], axis=0)                                       # 문틀 윗 띠(x 972 에서 끝난다): 왼쪽이 같은 빛
im = Image.fromarray(_a)
P = Patch(736, 528, 996, 606)
P.poly([(741, 548.5), (771, 548.5), (771, 565.2), (750.6, 565.2), (750.6, 569), (741, 569)], DOORBG, None)   # 바탕 그림의 잿빛 자루 끝을 지운다(객차 왼쪽 바깥은 그 밑줄까지)
P.line([(751, 566.6), (772, 566.6)], INK, 2.8, cap=False)                                  # 그 밑 객차 지붕의 윗 테는 다시 긋는다
BX, BY, BR, HR = 958.5, 560.0, 20.0, 7.6                                                   # 손잡이 고리의 가운데 · 바깥 반지름 · 구멍 반지름
P.poly([(768, 551), (944, 551), (944, 565), (768, 565)], KEYG, INK, 2.4)                   # 자루
for cx, col in ((790.5, KEYG), (840.5, KEYG), (890.5, KEYR)):
    P.poly([(cx - 14, 563), (cx + 14, 563), (cx + 14, 597.5), (cx - 14, 597.5)], col, INK, 2.2)
P.poly([(770.6, 553.4), (942, 553.4), (942, 562.6), (770.6, 562.6)], KEYG, None)           # 자루와 이빨 사이의 테를 지운다
for cx, col in ((790.5, KEYG), (840.5, KEYG)):
    P.poly([(cx - 11.8, 560), (cx + 11.8, 560), (cx + 11.8, 566), (cx - 11.8, 566)], col, None)
P.ell(BX, BY, BR, BR, KEYG, INK, 2.4)                                                      # 둥근 손잡이 고리
P.poly([(930, 553.4), (BX - BR + 5, 553.4), (BX - BR + 5, 562.6), (930, 562.6)], KEYG, None)   # 자루와 고리 사이의 테를 지운다
P.ell(BX, BY, HR, HR, POSTC, INK, 2.2)                                                     # 구멍(뒤의 보라 기둥이 비친다)
P.oline([(957.4, 536.5), (958.2, 557.5)], (190, 138, 96, 255), 2.5, 1.5)                   # 신발에서 내려온 끈이 고리를 넘어 구멍에 묶였다
P.ell(958.3, 558.2, 2.9, 2.9, (190, 138, 96, 255), INK, 1.4)                               # 매듭
P.done()

# ── ② 체스판 64칸(바탕 그대로) 위에 금빛 구슬 61 + 작은 나무판 3(맨 아랫줄 오른쪽 세 칸)
P = Patch(56, 782, 346, 1070)
XE = [62, 97.5, 132.5, 167.5, 202.5, 237.5, 272.5, 307.5, 338.5]; YE = [787, 822.5, 857.5, 892.5, 927.5, 962.5, 998.5, 1032.5, 1063.5]
nb = 0
for r in range(8):
    for c in range(8):
        cx, cy = (XE[c] + XE[c + 1]) / 2, (YE[r] + YE[r + 1]) / 2
        if r == 7 and c >= 5: miniplank(P, cx - 8, cy - 13, cx + 8, cy + 13)
        else: bead(P, cx, cy, 10.5, GOLD, 1.8); nb += 1
P.done(); assert nb == 61

# ── ③ 번쩍 든 손에서 줄줄이 늘어진 갈고리 둘 + 접이 사다리 + 구슬(C · C · A + 아미노산)
#    사이는 가는 실로 잇는다 — 쇠 토막으로 이으면 「굽은 것이 셋」으로 읽힌다(일치 검사 4회). 굽은 쇠는 갈고리 둘뿐.
P = Patch(620, 180, 700, 372)
STEEL = (170, 176, 188, 255); THREAD = (104, 100, 104, 255)
P.oline([(683.5, 195.5), (666, 207.6)], THREAD, 1.9, 1.0)                      # 주먹에서 나온 실 → 첫 갈고리의 위 끝
P.oline([(665, 230.4), (665, 246.6)], THREAD, 1.9, 1.0)                        # 첫 갈고리의 아래 끝 → 둘째 갈고리의 위 끝
P.oline([(664.6, 269.4), (656.6, 276)], THREAD, 1.9, 1.0)                      # 둘째 갈고리의 아래 끝 → 사다리 꼭대기
hook(P, 656, 219, 14, 5.6, STEEL); hook(P, 656, 258, 14, 5.6, STEEL)           # 두 갈고리 사이를 띄운다(붙으면 한 덩이로 읽힌다)
stepladder(P, 656, 276, 52, 18)
P.oline([(656, 312), (656, 334)], THREAD, 1.9, 1.0)                            # 사다리 아래 가로대에 맨 실
bead(P, 656, 349, 16, PINK, 2.0)
P.done()

# ── ④ 말풍선: 빛깔 네모 셋(이 객차의 창 = 노랑 · 초록 · 초록) → 구슬 하나
P = Patch(790, 140, 1030, 300)
P.poly([(842, 236), (812, 282), (872, 246)], (255, 255, 255, 255), INK, 2.4)   # 입 쪽으로 난 꼬리
P.rrect(830, 152, 1014, 246, 26, (255, 255, 255, 255), INK, 2.6)
P.poly([(845, 238), (818, 276), (868, 243)], (255, 255, 255, 255), None)       # 꼬리와 몸 사이 선을 지움
for k, b in enumerate('CAA'):
    x0 = 846 + k * 33; P.poly([(x0, 185), (x0 + 28, 185), (x0 + 28, 213), (x0, 213)], BASE[b], INK, 2.0)
P.poly([(948, 195), (962, 195), (962, 189), (974, 199), (962, 209), (962, 203), (948, 203)], (60, 56, 52, 255), None)
bead(P, 992, 199, 14.5, PINK, 2.0)
P.done()

# ── ⑤ 이정표 화살판의 빛깔 구슬 셋 · 사슬의 앞 끝 구슬
RED, BLUE, GREEN = (226, 62, 54, 255), (66, 128, 222, 255), (86, 176, 96, 255)
P = Patch(1150, 810, 1440, 972)
bead(P, 1226, 839, 13, RED); bead(P, 1360, 890, 13, BLUE); bead(P, 1360, 943, 13, GREEN)
P.done()
# 짐꾼의 사슬: 앞 끝(손 가까운 어깨의 구슬) = 파랑 · 몸 구슬에는 빨강 · 파랑 · 초록을 쓰지 않는다
P = Patch(1330, 900, 1560, 1110)
bead(P, 1532, 932, 13.5, BLUE)
bead(P, 1470, 935, 11.5, (242, 128, 176, 255)); bead(P, 1432, 988, 11.5, (250, 190, 140, 255)); bead(P, 1431, 1057, 11.5, (240, 140, 50, 255)); bead(P, 1413, 1074, 11.5, (196, 150, 226, 255))
for (bx, by) in [(1437, 972), (1430, 1004), (1431, 1040)]: P.ell(bx, by, 5.2, 5.2, (196, 196, 202, 255), INK, 1.6)      # 사이 작은 구슬은 잿빛
P.done()
# (천막 지붕의 사슬 · 구멍 · 앞 끝 빨간 구슬은 구역 편집 Z7 이 그렸다)
# 짐꾼 손을 지나는 사슬 끝의 작은 구슬(어두워 막대처럼 읽혔다) → 밝은 구슬
P = Patch(1534, 924, 1602, 976)
P.ell(1545, 936, 5.6, 5.6, (238, 226, 192, 255), INK, 1.6); P.ell(1554, 941.5, 5.2, 5.2, (198, 198, 204, 255), INK, 1.6); P.ell(1572.5, 959.5, 6.2, 6.2, (198, 198, 204, 255), INK, 1.6)
P.done()
# 손님채 오른쪽 위 테두리가 끊긴 자리(세로로 누를 때 생긴 6 px 틈)만 같은 굵기로 잇는다
P = Patch(1936, 910, 1960, 932)
P.line([(1942.6, 919.2), (1947.4, 920.8), (1953.4, 923.0)], (14, 12, 10, 255), 2.0)
P.done()

# 할아버지가 앉은 보라 단: 바탕 그림의 얼룩진 두 빛(위 띠 · 흐린 앞판 · 오른쪽 어두운 줄)을 한 빛으로 고르게
a = np.array(im); reg = a[448:506, 594:800, :3].astype(int)
R_, G_, B_ = reg[..., 0], reg[..., 1], reg[..., 2]
purple = (B_ > R_ + 8) & (R_ > G_ + 12) & (reg.max(axis=2) > 112)                 # 보라 계열만(바지 · 검은 테는 그대로)
reg[purple] = (177, 129, 209); a[448:506, 594:800, :3] = reg.astype(np.uint8)
# 단을 오른쪽으로 허벅지 밑(x 900)까지 늘인다 — 단이 엉덩이 밑에서 끝나 「엉덩이가 떠 보인다」고 읽혔다(일치 검사 5회).
# 다리 밑 테(아래에서 올려다본 첫 검은 줄) 아래의 연보라 벽을 단 빛으로: 밝기 비율을 지켜(테 가장자리의 번짐은 그대로) 옮긴다.
BENCH, LILAC = np.array([177, 129, 209], float), np.array([222, 186, 237], float)
rgbf = a[..., :3].astype(float)
for x in range(794, 899):
    xs = 806 if x <= 804 else x                                                   # 옛 오른쪽 테(세로 검은 줄)와 그 곁의 밝은 줄 자리는 이웃 기둥(x 806)의 밝기를 빌려 지운다
    yi = next(y for y in range(500, 430, -1) if rgbf[y, xs].max() < 110)          # 다리 밑 테
    for y in range(yi + 1, 504):
        t = float(np.clip((rgbf[y, xs] / LILAC).min(), 0, 1))
        if t > 0.93: t = 1.0                                                      # 벽의 잔 얼룩은 옮기지 않는다(고른 한 빛)
        a[y, x, :3] = np.clip(BENCH * t + 0.5, 0, 255).astype(np.uint8)
im = Image.fromarray(a)
P = Patch(790, 452, 910, 512)
P.line([(900, 459.5), (900, 505)], INK, 2.8, cap=False)                           # 늘인 단의 오른쪽 테
P.line([(794, 505.5), (901.4, 505.5)], INK, 3.4, cap=False)                       # 밑 테도 단의 굵기로
P.done()

# 땅 위 물건 둘레의 흰 번짐(바탕 그림 · 구역 편집이 남긴 후광 1 ~ 4 px)을 땅 빛으로 — 「오려 붙인 자국」으로 읽혔다(일치 검사 4회).
# 고치는 곳 = 땅보다 밝고 · 땅과 한 덩이로 이어졌고(물건 속 흰 곳은 검은 테에 막혀 빠진다) · 검은 테에서 4 px 안 · 지평선 아래.
import cv2
a = np.array(im); rgb = a[..., :3].astype(int)
GND = np.array([233, 233, 192])
isg = np.abs(rgb - GND).max(axis=2) <= 7
inkm = rgb.max(axis=2) < 90
light = rgb.min(axis=2) >= 180
n, lab = cv2.connectedComponents(light.astype(np.uint8), connectivity=4)
cnt = np.bincount(lab[isg], minlength=n); ground = np.where(cnt >= 1500)[0]; ground = ground[ground != 0]
brighter = (rgb[..., 0] >= 236) & (rgb[..., 1] >= 236) & (rgb[..., 2] >= 200)
halo = brighter & np.isin(lab, ground) & (cv2.dilate(inkm.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
halo[:560] = False                                                                # 하늘(지평선 위)은 그대로
rgb[halo] = GND; a[..., :3] = rgb.astype(np.uint8); im = Image.fromarray(a)
print('후광', int(halo.sum()), 'px')
im.convert('RGB').save(dst)
print('ok', dst)

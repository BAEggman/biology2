#!/usr/bin/env python3
# L12g_pil1.py <in.png> <out.png> — 바탕(v2) + 옮겨 심기(pil0) + 구역 편집(Z1 통 속 · Z2 호랑이 · Z6 일꾼) 뒤의 PIL 손질.
# 세어야 하는 것 · 방향이 곧 뜻인 것 · 덱의 약속 물건은 Gemini 에게 맡기지 않고 여기서 그린다:
#  ① 구슬 쟁반의 구슬 여덟(필수 아미노산 8) + 아기 손의 구슬 하나(히스티딘)
#  ② 널빤지 가위표 넷 — 쌀밥 공기 · 스티커 여행 가방(옥수수) · 메주(콩) · 소 가슴에 건 가위(소에게는 셀룰레이스가 없다)
#  ③ 장판 두루마리에서 삐져나온 꼬리 꺾인 기름방울(리놀레산 — 작업대의 곧은 꼬리와 짝)
#  ④ 소 속: 책 → 강철 통으로 잇는다(초록 관 지움은 L12g_pil7.py) · 먹이 길의 초록 화살 넷 · 책에서 짜이는 물방울 · 통에서 나온 구슬 셋과 작은 칼
#  ⑤ 풀 깔개를 탄 진흙 벽돌 뒤의 속도선(섬유가 밀어 준다) · 메주 빛깔
# 차례: L12g_pil0.py → Z1 · Z2 붙임(zone3.py) → L12g_pil6.py(Z6) → ZL(입술) · Z7(왼쪽 위 강철 통) 붙임 → L12g_pil7.py(초록 관 지움) → Z8(소 속 강철 통) 붙임 → 이 파일.
import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
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

def rot(pts, cx, cy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg)); return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]
def arrow(P, x0, y0, x1, y1, w=8, head=17, hl=15, fill=(98, 178, 88, 255), o=2.4):
    """(x0,y0) → (x1,y1) 블록 화살."""
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * hl, y1 - uy * hl
    P.poly([(x0 + nx * w / 2, y0 + ny * w / 2), (bx + nx * w / 2, by + ny * w / 2), (bx + nx * head / 2, by + ny * head / 2), (x1, y1),
            (bx - nx * head / 2, by - ny * head / 2), (bx - nx * w / 2, by - ny * w / 2), (x0 - nx * w / 2, y0 - ny * w / 2)], fill, INK, o)
def bead(P, cx, cy, r, col, o=2.0):
    P.ell(cx, cy, r, r, col, INK, o); P.ell(cx - r * 0.32, cy - r * 0.36, r * 0.30, r * 0.24, (255, 255, 255, 235), None)
def planks(P, cx, cy, half, w=9, a1=42, a2=-42):
    """널빤지 둘로 친 가위표(못 다섯)."""
    WOOD, GRAIN, NAIL = (208, 166, 112, 255), (168, 126, 80, 255), (112, 112, 118, 255)
    for ang in (a1, a2):
        P.poly(rot([(cx - half, cy - w / 2), (cx + half, cy - w / 2), (cx + half, cy + w / 2), (cx - half, cy + w / 2)], cx, cy, ang), WOOD, INK, 2.2)
        P.line(rot([(cx - half + 5, cy - 1), (cx + half - 5, cy - 1)], cx, cy, ang), GRAIN, 1.0, cap=False)
    for ang in (a1, a2):
        for t in (-1, 1):
            (nx_, ny_), = rot([(cx + t * (half - 6), cy)], cx, cy, ang); P.ell(nx_, ny_, 2.0, 2.0, NAIL, INK, 0.8)
    P.ell(cx, cy, 2.2, 2.2, NAIL, INK, 0.8)
def knife(P, x, y, L, deg, hl=None):
    """작은 부엌칼 — (x, y) 가 손잡이 끝, deg 방향으로 L 만큼."""
    hl = hl or L * 0.32; bl = L - hl
    blade = [(x + hl, y - 4.6), (x + hl + bl * 0.72, y - 4.6), (x + L, y + 1.5), (x + hl + bl * 0.80, y + 4.4), (x + hl, y + 4.4)]
    P.poly(rot(blade, x, y, deg), (222, 228, 236, 255), INK, 1.8)
    P.poly(rot([(x, y - 3.4), (x + hl, y - 3.4), (x + hl, y + 3.4), (x, y + 3.4)], x, y, deg), (126, 82, 52, 255), INK, 1.8)

a = np.array(im)
# 소 등선(작업대 왼쪽 — 갈색 상자를 지운 자리)의 잔 자국: 등선 위 띠를 하늘로 비우고 등선을 다시 긋는다(아래 PIL)
BX = np.array([1502, 1511, 1520.5, 1528.5, 1534, 1542, 1548, 1554, 1559, 1564.5, 1569, 1575]); BY = np.array([301, 304, 307, 310, 313, 316, 319, 322, 325, 328, 331, 334])
for x in range(1508, 1570):
    yc = float(np.interp(x, BX, BY)); a[int(yc) - 16:int(round(yc)) - 1, x, :3] = (198, 230, 247)
# ── ③-가 장판 두루마리 위의 옛 기름방울 그림을 장판 빛으로 덮는다
MAT = np.array([121, 152, 112])
yy, xx = np.mgrid[144:182, 1142:1176]; em = ((xx - 1158) / 11.5) ** 2 + ((yy - 162) / 15.5) ** 2 <= 1
a[144:182, 1142:1176, :3][em] = MAT
# 장판 두루마리는 초록 그대로 둔다 — 누렇게 바꿨더니 「롤케이크 · 건초 롤」, 마루 무늬를 넣었더니 「벽돌 상자 · 짚단」으로 읽혔다(일치 검사 2 · 3회). 초록 = 「매트 · 잔디 두루마리」 = 바닥에 까는 것.
# 하늘의 후광(물건 둘레의 하늘보다 밝은 푸른 테)과 지평선 바로 위의 밝은 띠 → 하늘빛
SKY = np.array([198, 230, 247], dtype=np.uint8)
sk = a[0:331, :, :3]; halo = (sk[..., 0] > 204) & (sk[..., 0] < 240) & (sk[..., 1] > 233) & (sk[..., 2] > 246); sk[halo] = SKY
hz = a[321:330, :, :3]; band = (hz[..., 1] > 218) & (hz[..., 0] < 216) & (hz[..., 2] > 200) & (hz[..., 0] > 180); hz[band] = SKY
# 왼쪽 위 강철 통(Z7) 밑에 남은 그림자 줄을 지운다
a[318:331, 0:330, :3] = SKY
# 지평선을 y = 331 → 318 로 올린다 — 위 줄의 사람 · 좌판 · 작업대 다리가 하늘에 떠 보이지 않게(발 · 다리 끝이 y 316 ~ 326)
GRASS = np.array([148, 203, 118], dtype=np.uint8)
hz2 = a[318:337, :, :3]; skyish = (np.abs(hz2.astype(int) - SKY.astype(int)).sum(axis=2) < 46) | ((hz2[..., 1] > 190) & (hz2[..., 0] < 210) & (hz2[..., 2] > 125) & (hz2[..., 0] > 135))
hz2[skyish] = GRASS
# 셋째 스펀지만 물에 잠긴 밑동이 하늘빛이었다 → 앞의 둘처럼 짙은 노랑으로(셋이 같아야 「셋 다 물을 빤다」)
s1b = a[846:868, 572:660, :3].reshape(-1, 3).astype(int); ym = (s1b[:, 0] > 170) & (s1b[:, 1] > 130) & (s1b[:, 2] < 110)
SUBY = np.median(s1b[ym], axis=0) if ym.any() else np.array([222, 178, 58])
s3 = a[838:876, 960:1072, :3]; bl = (s3[..., 2].astype(int) > s3[..., 0].astype(int) + 25) & (s3[..., 2] > 170); s3[bl] = SUBY.astype(np.uint8)
# 지렁이 꼴 흙 광: 누런 갈색 → 지렁이 살빛(붉은 흙빛)
wr = a[586:802, 18:218, :3].astype(float); cm = (np.abs(wr - np.array([184., 146., 104.])).sum(axis=2) < 50)
wr[cm] = wr[cm] * np.array([1.07, 0.90, 0.98]) + np.array([4., 0., 8.]); a[586:802, 18:218, :3] = wr.clip(0, 255).astype(np.uint8)
# 통 띠 아랫동의 양 끝에 남은 검은 삐침(뗀 초록 관의 테두리 자국) · 소 턱선의 끝(가위표 널빤지에 닿아 「가위에 이어진 선」으로 읽혔다)을 흰 몸빛으로
yy3, xx3 = np.mgrid[466:492, 1492:1518]
sd = ((xx3 - 1499.5) * 9.5 + (yy3 - 481.5) * 10.0) / 13.79; al = ((xx3 - 1499.5) * 10.0 + (yy3 - 481.5) * (-9.5)) / (10.0 * 10.0 + 9.5 * 9.5)
sp = a[466:492, 1492:1518, :3]; sp[(sd > 2.3) & (sd < 9) & (al > -0.6) & (al < 1.6)] = (249, 250, 245)
jw = a[446:472, 1186:1212, :3]; jw[jw.min(axis=2) < 238] = (249, 250, 245)
# 좌판 오른쪽 다리 끝의 검은 토막
tk = a[313:318, 1182:1194, :3]; tk[tk.sum(axis=2) < 200] = SKY
# 메주: 옛 노란 상자를 지운다(기둥 가로대 y < 167 은 남긴다) → 아래 PIL 에서 금 간 누런 덩이로
a[167:240, 1884:1970, :3] = SKY
# 작업대 위 기름방울(「숟가락 · 올챙이」로 읽혔다)을 지운다 → 아래 PIL 에서 방울 + 지그재그 꼬리로
bd = a[212:251, 1694:1774, :3]; bd[np.abs(bd.astype(int) - SKY.astype(int)).sum(axis=2) > 24] = SKY
# 좌판 오른쪽 다리 밑동(흰 점 · 주황 점) · 오른쪽 뿔 끝 곁의 초록 자국
for y in range(307, 315): a[y, 1152:1182, :3] = a[304, 1152:1182, :3]
a[315:318, 1152:1182, :3] = (24, 20, 18)
hg = a[298:318, 1213:1228, :3]; gmk = (hg[..., 1].astype(int) > hg[..., 0].astype(int) + 14) & (hg[..., 1].astype(int) > hg[..., 2].astype(int) + 14); hg[gmk] = SKY
# 소 입 구석의 새까만 덩이(「얼룩 · 이음매」로 읽혔다) → 입 안의 검붉은 빛
mc = a[426:456, 1164:1186, :3]; dk = mc.sum(axis=2) < 110
dk_in = np.asarray(Image.fromarray((dk * 255).astype('uint8')).filter(ImageFilter.MinFilter(5))) > 0
mc[dk_in] = (124, 48, 54)
im = Image.fromarray(a, 'RGBA')

# ── ① 구슬 쟁반: 여덟 홈에 구슬 여덟(빛깔이 다 다르다 = 서로 다른 여덟 아미노산)
P = Patch(1020, 156, 1134, 208)
COLS = [(228, 62, 62), (245, 150, 44), (250, 214, 64), (96, 190, 92), (72, 190, 212), (72, 112, 222), (154, 94, 212), (246, 246, 246)]
for (cx, cy), col in zip([(1036, 172), (1063, 172), (1090, 172), (1117, 172), (1037, 193), (1064, 193), (1091, 193), (1117, 193)], COLS):
    bead(P, cx, cy - 1, 8.6, col + (255,))
P.done()
# 아기 손의 구슬 하나(분홍 — 쟁반의 여덟과 같은 꼴 · 아홉째)
P = Patch(1370, 172, 1406, 208); bead(P, 1388, 189, 11.0, (246, 132, 182, 255)); P.done()

# ── ③ 기름방울 둘 — 방울 + 지그재그 꼬리(교과서의 지방산 그림): 장판 위의 것은 꼬리가 한 번 크게 꺾였고 · 작업대의 것은 곧다
OIL = (240, 200, 58, 255)
def zigzag(p0, p1, amp=3.2, per=8.5, phase=0):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L; nx, ny = -uy, ux
    n = max(2, int(round(L / (per / 2)))); pts = []
    for k in range(n + 1):
        t = k / n; sgn = 0 if k in (0, n) else (1 if (k + phase) % 2 else -1)
        pts.append((p0[0] + ux * L * t + nx * amp * sgn, p0[1] + uy * L * t + ny * amp * sgn))
    return pts
def oildrop(P, cx, cy, ang, rx=11.5, ry=9.4):
    """눈물 꼴 방울 — 뾰족한 끝이 ang(도) 쪽(꼬리가 나가는 쪽)."""
    pts = []
    for k in range(40):
        th = 2 * math.pi * k / 40; x = rx * math.cos(th); y = ry * math.sin(th)
        if math.cos(th) > 0.55: x += (math.cos(th) - 0.55) * rx * 1.5                # 한쪽을 뾰족하게 당긴다
        pts.append((x, y))
    P.poly(rot([(cx + x, cy + y) for x, y in pts], cx, cy, ang), OIL, INK, 2.0)
    (hx, hy), = rot([(cx - rx * 0.35, cy - ry * 0.38)], cx, cy, ang); P.ell(hx, hy, 3.0, 2.3, (255, 244, 190, 255), None)
# 장판 위: 꼬리가 오른쪽 위로 가다가 한 번 크게 꺾여 내려온다
P = Patch(1136, 124, 1246, 200)
t1 = zigzag((1172, 156), (1214, 148)); t2 = zigzag((1214, 148), (1216, 186), phase=1)      # ㄱ 자: 거의 가로로 가다가 곧장 아래로(「휘어진 톱니」가 아니라 「꺾임」으로 읽히게)
P.oline(t1 + t2[1:], OIL, 2.4, 1.6)
oildrop(P, 1159, 161, -22)
P.done()
# 작업대 위: 꼬리가 곧게 뻗었다
P = Patch(1688, 212, 1780, 256)
P.oline(zigzag((1719, 236), (1770, 224)), OIL, 2.4, 1.6)
oildrop(P, 1706, 240.5, -13)
P.done()
# ── ② 널빤지 가위표: 쌀밥 공기 · 스티커 여행 가방 · 메주
P = Patch(462, 146, 548, 228); planks(P, 503, 187, 33, 6.6); P.done()
P = Patch(468, 236, 570, 330); planks(P, 518, 286, 42, 7.0); P.done()
P = Patch(1876, 160, 1972, 248)
ROPE = (232, 214, 170, 255)
P.oline([(1923, 164), (1923, 184)], ROPE, 2.6, 1.6)                                # 가로대에 맨 끈
P.d.rounded_rectangle([P.T([(1890, 183)])[0][0], P.T([(1890, 183)])[0][1], P.T([(1956, 231)])[0][0], P.T([(1956, 231)])[0][1]], radius=9 * P.S, fill=(176, 124, 70, 255), outline=INK, width=int(2.4 * P.S))
for crack in ([(1898, 196), (1905, 200), (1902, 207)], [(1944, 190), (1940, 197), (1946, 203)], [(1910, 222), (1917, 218), (1925, 223)], [(1938, 214), (1944, 219)]): P.line(crack, (112, 72, 38, 255), 1.5)
for (fx, fy) in [(1900, 214), (1933, 193), (1947, 222), (1912, 190)]: P.ell(fx, fy, 2.2, 1.8, (228, 216, 188, 255), None)   # 흰 곰팡이 점
P.line([(1923, 184), (1923, 230)], (238, 224, 186, 255), 2.0, cap=False); P.line([(1891, 207), (1955, 207)], (238, 224, 186, 255), 2.0, cap=False)   # 열십자로 묶은 가는 끈
planks(P, 1923, 207, 40, 6.6)
P.done()

# ── ② 소 가슴에 못으로 건 가위(통 속 세균이 든 것과 같은 벌린 가위 — 날은 위 · 손잡이 고리는 아래) + 널빤지 가위표
P = Patch(1178, 430, 1264, 530)
cx, cy = 1220, 484                                                                 # 가위 못(축)
BL, HD = (204, 210, 220, 255), (214, 58, 58, 255)
for sg in (-1, 1):
    blade = rot([(cx - 3.8, cy + 4), (cx + 3.8, cy + 4), (cx + 1.2, cy - 40), (cx, cy - 44)], cx, cy, sg * 17)
    P.poly(blade, BL, INK, 1.8)
for sg in (-1, 1):                                                                 # 손잡이 고리(날 반대쪽)
    (hx, hy), = rot([(cx, cy + 21)], cx, cy, sg * 24)
    P.line(rot([(cx, cy + 3), (cx, cy + 13)], cx, cy, sg * 24), INK, 6.4); P.line(rot([(cx, cy + 3), (cx, cy + 13)], cx, cy, sg * 24), HD, 3.0)
    (x0, y0), (x1, y1) = P.T([(hx - 8.2, hy - 9.6), (hx + 8.2, hy + 9.6)]); P.d.ellipse([x0, y0, x1, y1], outline=INK, width=int(6.6 * P.S))
    (x0, y0), (x1, y1) = P.T([(hx - 6.8, hy - 8.2), (hx + 6.8, hy + 8.2)]); P.d.ellipse([x0, y0, x1, y1], outline=HD, width=int(3.2 * P.S))
P.ell(cx, cy, 2.6, 2.6, (120, 120, 126, 255), INK, 1.0)
planks(P, cx, cy - 6, 31, 5.8, 27, -27)
P.done()

# ── ④ 소 속: 먹이 길의 초록 화살 — ㉠ 삼킴(입 → 통) ㉡ 되새김(통 → 입) ㉢ 통 → 책 ㉣ 책 → 강철 통
P = Patch(1240, 340, 1340, 470)
arrow(P, 1256, 358, 1306, 373, 8.5, 19, 16)        # ㉠
arrow(P, 1302, 448, 1252, 428, 8.5, 19, 16)        # ㉡
P.done()
P = Patch(1376, 494, 1412, 532); arrow(P, 1394, 500, 1394, 526, 7.5, 16, 12); P.done()   # ㉢
P = Patch(1452, 528, 1500, 578)
P.poly([(1463, 556), (1488, 556), (1488, 568), (1463, 568)], (227, 167, 162, 255), None)   # 책 → 강철 통을 잇는 분홍 관(양 끝이 책 · 통에 닿는다)
P.line([(1462, 555.5), (1489, 555.5)], INK, 2.2, cap=False); P.line([(1462, 568.5), (1489, 568.5)], INK, 2.2, cap=False)
arrow(P, 1462, 541, 1489, 541, 7.0, 15, 11)        # ㉣
P.done()
# 책(겹주름)에서 짜여 나오는 물방울 셋
P = Patch(1344, 536, 1378, 600)
for (dx, dy, r) in [(1363, 549, 5.6), (1355, 567, 5.0), (1364, 585, 5.6)]:
    P.poly([(dx, dy - r * 1.9), (dx + r * 0.95, dy - r * 0.2), (dx + r * 0.7, dy + r * 0.8), (dx, dy + r * 1.1), (dx - r * 0.7, dy + r * 0.8), (dx - r * 0.95, dy - r * 0.2)], (120, 196, 240, 255), INK, 1.7)
P.done()
# 통에서 소의 몸으로 나온 것 — 구슬 셋(아미노산) + 작은 칼(비타민)
P = Patch(1530, 396, 1640, 482)
for (qx0, qy0, qx1, qy1) in [(1538, 424, 1546, 422), (1540, 438, 1548, 440), (1538, 452, 1546, 457)]: P.line([(qx0, qy0), (qx1, qy1)], INK, 2.0)   # 튀어나온 자국
bead(P, 1562, 416, 8.0, (228, 62, 62, 255)); bead(P, 1582, 428, 8.0, (72, 112, 222, 255)); bead(P, 1564, 440, 8.0, (250, 214, 64, 255))
knife(P, 1568, 463, 46, -8)
P.done()

# 헬리콥터 세균의 회전 날개: Gemini(Z7)가 그린 타원 고리 속 날개가 흐리다 — 날개 둘과 축을 굵게 덧그린다(고리만 보이면 「헤일로」로 읽힌다)
P = Patch(150, 132, 240, 170)
BLD = (86, 92, 104, 255)
P.poly([(194.5, 148.2), (194.5, 151.8), (161, 152.6), (160, 150.2)], BLD, INK, 1.3); P.poly([(194.5, 148.2), (194.5, 151.8), (229, 149.8), (228, 147.4)], BLD, INK, 1.3)
P.ell(194.5, 150, 3.2, 2.6, (52, 54, 62, 255), INK, 1.0)
P.done()
# 나가는 관의 열린 끝(오른쪽) — 둥근 구멍이 보여야 「관」으로 읽힌다
P = Patch(2008, 890, 2048, 1026)                                                    # 구멍의 오른쪽 가장자리는 그림 밖에 걸친다
P.ell(2036, 957, 13.5, 54.5, (188, 195, 204, 255), INK, 2.6)
P.ell(2037.5, 957, 8.2, 44.0, (58, 60, 68, 255), INK, 1.6)
P.done()
# 지렁이 꼴 흙 광: 마디 줄을 더 긋는다(「두루마리 · 굵은 관」으로 읽혔다 — 마디가 촘촘해야 지렁이)
P = Patch(20, 590, 215, 805)
RING = (112, 74, 42, 255)
for (p0, c, p1) in [((76, 607), (86, 622), (104, 632)), ((48, 636), (62, 650), (72, 664)), ((34, 668), (50, 676), (68, 678)), ((30, 700), (48, 700), (68, 696)), ((36, 728), (52, 722), (70, 722)),
                    ((56, 756), (70, 744), (82, 726)), ((80, 774), (90, 754), (100, 728)), ((124, 790), (130, 760), (132, 728)), ((148, 792), (150, 762), (150, 734)), ((190, 778), (186, 756), (182, 738))]:
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]) for t in [k / 10 for k in range(11)]]
    P.line(pts, RING, 2.2)
P.done()
# 흙 광 창 속 유리 단지 셋의 세균: 초록 동그라미뿐이라 세균으로 안 읽혔다 → 눈 · 입이 있는 초록 알약으로
P = Patch(70, 672, 144, 716, S=6)
for gx in (83.3, 106.3, 129.3):
    (x0, y0), (x1, y1) = P.T([(gx - 5.6, 683.5), (gx + 5.6, 706.5)]); P.d.rounded_rectangle([x0, y0, x1, y1], radius=5.4 * P.S, fill=(104, 190, 84, 255), outline=INK, width=int(1.3 * P.S))
    P.ell(gx - 2.1, 691.2, 0.9, 1.0, INK, None); P.ell(gx + 2.1, 691.2, 0.9, 1.0, INK, None)
    P.line([(gx - 2.3, 695.6), (gx, 697.4), (gx + 2.3, 695.6)], INK, 0.9)
P.done()
# 먹이 홈통을 받친 기둥(홈통이 공중에 떠 보였다 — 윗동이 기둥에 걸쳤다)
P = Patch(618, 340, 656, 512)
P.poly([(629, 356), (643, 356), (643, 502), (629, 502)], (150, 104, 62, 255), INK, 2.4)
P.line([(633, 368), (633, 494)], (120, 80, 46, 255), 1.2, cap=False)
P.poly([(625, 350), (647, 350), (647, 358), (625, 358)], (170, 120, 72, 255), INK, 2.2)
P.done()
# 통 띠 아랫동(초록 관을 뗀 자리)과 좌판 다리 끝을 또렷이
P = Patch(1488, 462, 1520, 492); P.line([(1499.5, 481.5), (1509.5, 472)], INK, 3.4, cap=False); P.done()
P = Patch(1146, 308, 1190, 324); P.line([(1153, 316.5), (1180.5, 316.5)], INK, 2.6, cap=False); P.done()

# ── ⑤ 풀 깔개를 탄 진흙 벽돌 뒤의 속도선(오른쪽으로 미끄러진다)
P = Patch(1040, 912, 1136, 972)
for (x0, x1, y) in [(1070, 1122, 926), (1054, 1114, 941), (1070, 1122, 956)]: P.line([(x0, y), (x1, y)], (232, 204, 158, 255), 3.6)
P.done()

# 소 등선(작업대 왼쪽) 다시 긋기
P = Patch(1496, 290, 1580, 345)
pts = [(float(x), float(np.interp(x, BX, BY))) for x in range(1504, 1574, 4)]
P.line(pts, INK, 5.0)
P.done()

im.convert('RGB').save(dst); print('ok pil1')

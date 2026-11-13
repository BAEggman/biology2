#!/usr/bin/env python3
# L53b_pil1.py — 바탕(s1) + E1 뒤의 PIL 손질:
#  ① 사과 사이 「=」 지움  ② 포도에 달린 잎 · 꼭지 지움(짝 손님 · 굴 아래 둘 · 더미) + 사과 문 아래 떠돌이 포도 지움
#  ③ 봉투 곁의 맨 물방울 지움  ④ 봉투를 키우고 봉인에 금빛 고리 넷 문장  ⑤ 회전문 둘을 다시 그림(문짝 하나 / 별 꼴 날개 다섯 · 위아래 트임)
#  ⑥ 흰 방울 ↓ · 어두운 방울 ↑ 작은 화살  ⑦ 아래 물을 L53a 처럼 깊을수록 짙게
import sys, math, cv2, numpy as np
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
im = cv2.imread(src)
UP, DEEP, BUT, SHAFT = (233, 187, 117), (187, 110, 40), (75, 211, 248), (244, 224, 187)      # BGR
INK = (22, 20, 18, 255)
def box_fill(x0, y0, x1, y1, col, keep=None):
    """상자를 한 빛으로 메운다. keep = [(cx, cy, r), …] 원 안은 그대로."""
    yy, xx = np.mgrid[y0:y1, x0:x1]; m = np.ones((y1 - y0, x1 - x0), bool)
    for cx, cy, r in (keep or []): m &= (xx - cx) ** 2 + (yy - cy) ** 2 > r * r
    reg = im[y0:y1, x0:x1]; reg[m] = col
# ① 「=」
box_fill(1340, 206, 1368, 238, UP)
# ② 잎 · 꼭지(포도 윗 테두리는 아래에서 다시 긋는다) — 포도 몸통의 중심 · 반지름은 화소로 잰 값
box_fill(1297, 88, 1352, 124, UP, keep=[(1328, 136, 24.9)])              # 짝 손님 포도(몸통 r 21 + 먹선)
box_fill(1176, 686, 1222, 716, SHAFT, keep=[(1190, 723.3, 16.9)])         # 포도 문 아래 굴 속 포도(r 13)
box_fill(1174, 836, 1214, 862, SHAFT, keep=[(1206.8, 871.3, 16.9)])       # 굴 끝 포도
box_fill(1412, 896, 1468, 964, DEEP)                                      # 사과 문 아래 떠돌이 포도(통째로)
def erase_green(x0, y0, x1, y1, fill):
    """더미 포도에 달린 잎: 초록 몸 + 둘레 먹선만 물빛으로(포도 테두리는 지킨다)."""
    reg = im[y0:y1, x0:x1]; b, g, r = [reg[..., k].astype(int) for k in range(3)]
    core = ((g > r + 14) & (g > b - 28) & (g > 55)).astype(np.uint8)
    purple = ((r > 70) & (b > 105) & (g < 105) & (b > g + 35) & (r > g + 15)).astype(np.uint8)
    white = ((r > 200) & (g > 200) & (b > 200)).astype(np.uint8)
    mk = cv2.dilate(core, np.ones((9, 9), np.uint8)) > 0
    mk &= ~(cv2.dilate(purple | white, np.ones((9, 9), np.uint8)) > 0)
    reg[mk] = fill
erase_green(672, 962, 706, 1006, DEEP); erase_green(824, 898, 874, 942, DEEP); erase_green(886, 972, 924, 1012, DEEP)
# ③ 맨 물방울(파란 빛 + 둘레 먹선) → 버터빛
reg = im[488:600, 428:502].astype(int)
blue = (reg[..., 0] > reg[..., 2] + 40) & (reg[..., 0] > 140)
mk = cv2.dilate(blue.astype(np.uint8) * 255, np.ones((11, 11), np.uint8))
leg = im[486:602, 494:508].copy()                                         # 물방울 오른쪽에 붙은 다리(밤색 먹선)는 따로 간직
im[488:600, 428:502][mk > 0] = BUT
im[486:602, 456:497] = BUT                                                # 물방울 테두리 자국까지
lb, lg, lr = [leg[..., k].astype(int) for k in range(3)]
brown = (lr > lb + 22) & (lr + lg + lb < 420)                             # 다리 빛(밤색) — 물방울의 검푸른 테두리와 가른다
im[486:602, 494:508][brown] = leg[brown]
pil = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
S = 4
def paste_layer(lay, x0, y0, W, H):
    lay = lay.resize((W, H), Image.LANCZOS); pil.paste(lay, (x0, y0), lay)
def top_arc(cx, cy, r, a0, a1, w=4.4, fill=(128, 62, 166, 255)):
    """잎을 지운 포도의 윗 테두리를 다시 긋는다(각도는 화면 기준 · 270 = 위)."""
    R0 = int(r) + 8; x0, y0 = int(cx) - R0, int(cy) - R0; W = H = 2 * R0
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); ox, oy = (cx - x0) * S, (cy - y0) * S
    d.pieslice([ox - r * S, oy - r * S, ox + r * S, oy + r * S], a0, a1, fill=fill)
    d.ellipse([ox - (r - 7) * S, oy - (r - 7) * S, ox + (r - 7) * S, oy + (r - 7) * S], fill=(0, 0, 0, 0))
    d.arc([ox - (r + w / 2) * S, oy - (r + w / 2) * S, ox + (r + w / 2) * S, oy + (r + w / 2) * S], a0, a1, fill=INK, width=int(w * S))
    paste_layer(lay, x0, y0, W, H)
top_arc(1328, 136, 21.4, 205, 335, 3.6, (122, 62, 150, 255))
top_arc(1190, 723.3, 13.2, 215, 345, 3.6)
top_arc(1206.8, 871.3, 13.2, 190, 300, 3.6)
# ④ 큰 봉투 + 금빛 고리 넷 봉인
def envelope(cx, cy, hw, hh, ang, seal_r=27):
    R0 = int(math.hypot(hw, hh)) + 12; x0, y0 = cx - R0, cy - R0; W = H = 2 * R0
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    def T(px, py): return ((R0 + px * ca - py * sa) * S, (R0 + px * sa + py * ca) * S)
    body = [T(-hw, -hh), T(hw, -hh), T(hw, hh), T(-hw, hh)]
    d.polygon(body, fill=(255, 255, 255, 255)); d.line(body + [body[0]], fill=INK, width=int(4.5 * S), joint='curve')
    d.polygon([T(-hw + 4, hh - 3), T(hw - 4, hh - 3), T(hw - 4, hh - 16), T(-hw + 4, hh - 10)], fill=(226, 232, 240, 255))     # 아래 그늘
    d.line([T(-hw, -hh), T(0, 6), T(hw, -hh)], fill=INK, width=int(3.5 * S), joint='curve')                       # 덮개
    d.line([T(-hw, hh), T(-hw * 0.28, 2)], fill=(120, 120, 130, 255), width=int(2.2 * S)); d.line([T(hw, hh), T(hw * 0.28, 2)], fill=(120, 120, 130, 255), width=int(2.2 * S))
    for p in body:
        r = 2.2 * S; d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=INK)
    sx, sy = T(0, 8)
    r = (seal_r + 3) * S; d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=INK)
    r = seal_r * S; d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(244, 188, 44, 255))
    d.arc([sx - r + 3 * S, sy - r + 3 * S, sx + r - 3 * S, sy + r - 3 * S], 200, 260, fill=(253, 224, 130, 255), width=int(3 * S))
    # 고리 넷(육각 셋 + 오각 하나) — steroid.py 꼴 · 봉투와 함께 기울임
    rr = seal_r * 0.30; s3 = math.sqrt(3)
    def hexv(ax, ay): return [(ax + rr * math.cos(math.radians(a)), ay - rr * math.sin(math.radians(a))) for a in (90, 30, -30, -90, -150, 150)]
    A = (0.0, 0.0); B = (s3 * rr, 0.0); C = (1.5 * s3 * rr, -1.5 * rr)
    rings = [hexv(*A), hexv(*B), hexv(*C)]
    e0x = C[0] + s3 / 2 * rr; ap = rr / (2 * math.tan(math.radians(36))); R5 = rr / (2 * math.sin(math.radians(36)))
    D = (e0x + ap, C[1]); rings.append([(D[0] + R5 * math.cos(math.radians(a)), D[1] - R5 * math.sin(math.radians(a))) for a in (144, 72, 0, -72, -144)])
    pts = [p for g in rings for p in g]; mx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2; my = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    def E(p): return T(p[0] - mx, p[1] - my + 8)
    seen = set()
    for g in rings:
        for i in range(len(g)):
            p, q = g[i], g[(i + 1) % len(g)]; k = tuple(sorted([(round(p[0], 1), round(p[1], 1)), (round(q[0], 1), round(q[1], 1))]))
            if k in seen: continue
            seen.add(k); d.line([E(p), E(q)], fill=(96, 52, 8, 255), width=int(3.9 * S))
        for p in g:
            x, y = E(p); r = 1.75 * S; d.ellipse([x - r, y - r, x + r, y + r], fill=(96, 52, 8, 255))
    paste_layer(lay, x0, y0, W, H)
envelope(386, 564, 86, 58, -18, seal_r=39)
# ⑤ 회전문
def drum(cx, cy, wings, cargo):
    G = 19                                              # 위 · 아래 트임의 반각
    # 바탕에 곧장: 문통 안과 트인 곳을 굴의 물빛으로(같은 빛이라 경계가 안 보인다) — 옛 문통 · 옛 문짝 · 옛 손님을 덮는다
    bd = ImageDraw.Draw(pil); shaft = (187, 224, 244)
    bd.ellipse([cx - 57.5, cy - 57.5, cx + 57.5, cy + 57.5], fill=shaft)
    for a0 in (270, 90):
        bd.polygon([(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for r, a in [(50, a0 - G - 3), (74, a0 - G - 1), (88, a0 - G + 3), (90, a0), (88, a0 + G - 3), (74, a0 + G + 1), (50, a0 + G + 3)]], fill=shaft)
    R0 = 92; x0, y0 = cx - R0, cy - R0; W = H = 2 * R0
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def P(r, a): return ((R0 + r * math.cos(math.radians(a))) * S, (R0 + r * math.sin(math.radians(a))) * S)
    def disc(r, col): d.ellipse([(R0 - r) * S, (R0 - r) * S, (R0 + r) * S, (R0 + r) * S], fill=col)
    def band(r1, r0, a0, a1, col): d.arc([(R0 - r1) * S, (R0 - r1) * S, (R0 + r1) * S, (R0 + r1) * S], a0, a1, fill=col, width=int((r1 - r0) * S))
    # 놋쇠 문통 = 양옆 두 굽은 벽(위 · 아래가 트였다)
    for a0, a1 in ((270 + G, 90 - G), (90 + G, 270 - G)):
        band(73, 56.5, a0, a1, INK); band(70.2, 59.3, a0 + 2.2, a1 - 2.2, (214, 164, 52, 255)); band(67.4, 63.6, a0 + 2.2, a1 - 2.2, (240, 200, 96, 255))
    glass, gedge = (128, 190, 236, 255), (40, 70, 110, 255)
    def wing(a, r0=0, r1=52, w=9):
        d.line([P(r0, a), P(r1, a)], fill=gedge, width=int((w + 4.4) * S)); d.line([P(r0, a), P(r1 - 1.2, a)], fill=glass, width=int(w * S))
        d.line([P(r0 + 10, a), P(r1 - 8, a)], fill=(205, 232, 250, 255), width=int(2 * S))
    if wings == 1:
        for a in (-38, 142): wing(a)
        # 도는 방향(시계 방향): 왼쪽 반에서 위로 굽는 화살
        pts = [P(33, a) for a in range(108, 205, 4)]; d.line(pts, fill=INK, width=int(5 * S), joint='curve')
        tip = P(33, 214); b1 = P(42, 198); b2 = P(24, 198); d.polygon([tip, b1, b2], fill=INK)
    else:
        for k in range(5): wing(-54 + k * 72, w=7.5)
    disc(10.5, INK); disc(7.5, (214, 164, 52, 255))
    cargo(d, P)
    paste_layer(lay, x0, y0, W, H)
def grape(d, P, r_a=(30, 12), rad=17):
    x, y = P(*r_a); r = (rad + 2.6) * S; d.ellipse([x - r, y - r, x + r, y + r], fill=INK); r = rad * S; d.ellipse([x - r, y - r, x + r, y + r], fill=(128, 62, 166, 255))
    d.ellipse([x - 9 * S, y - 10 * S, x - 2 * S, y - 4 * S], fill=(176, 120, 206, 255))
def apple(d, P, r_a=(33, -18), rad=14.5):
    x, y = P(*r_a); r = (rad + 2.6) * S; d.ellipse([x - r, y - r, x + r, y + r], fill=INK); r = rad * S; d.ellipse([x - r, y - r, x + r, y + r], fill=(222, 44, 40, 255))
    d.ellipse([x - 8 * S, y - 9 * S, x - 2 * S, y - 4 * S], fill=(246, 140, 130, 255))
    d.line([(x + 1 * S, y - rad * S), (x + 5 * S, y - (rad + 9) * S)], fill=INK, width=int(3 * S))
    d.ellipse([x + 4 * S, y - (rad + 13) * S, x + 16 * S, y - (rad + 6) * S], fill=INK); d.ellipse([x + 6 * S, y - (rad + 11.5) * S, x + 14 * S, y - (rad + 7.5) * S], fill=(92, 176, 84, 255))
# 옛 문통 바깥의 굽은 화살(위 · 아래) — 굴 빛으로 메움(먹빛만 골라)
a = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
def clean_arrows(cx, cy):
    global a
    rr = np.hypot(xx - cx, yy - cy); ang = (np.degrees(np.arctan2(yy - cy, xx - cx)) + 360) % 360
    sect = (rr > 71) & (rr < 86) & (((ang > 236) & (ang < 304)) | ((ang > 56) & (ang < 124)))
    sect |= (rr > 73.2) & (rr < 80) & (((ang > 226) & (ang < 314)) | ((ang > 46) & (ang < 134)))
    notshaft = np.abs(a.astype(int) - np.array(SHAFT)).sum(axis=2) > 36
    mk = (sect & notshaft).astype(np.uint8) * 255; mk = cv2.dilate(mk, np.ones((5, 5), np.uint8)); mk[~sect] = 0
    a[mk > 0] = SHAFT
clean_arrows(1190, 570); clean_arrows(1440, 570)
pil = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))
drum(1190, 570, 1, grape)
drum(1440, 570, 5, apple)
# ⑥ 작은 화살: 흰 방울 ↓ · 어두운 방울 ↑
def arrow(x, y0, y1, w=5.5):
    up = y1 < y0; top, bot = min(y0, y1), max(y0, y1); x0 = x - 16; W = 32; H = bot - top + 8; yb = top - 4
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def T(px, py): return ((px - x0) * S, (py - yb) * S)
    if up:
        d.line([T(x, bot), T(x, top + 12)], fill=INK, width=int(w * S)); d.polygon([T(x, top), T(x - 11, top + 15), T(x + 11, top + 15)], fill=INK)
    else:
        d.line([T(x, top), T(x, bot - 12)], fill=INK, width=int(w * S)); d.polygon([T(x, bot), T(x - 11, bot - 15), T(x + 11, bot - 15)], fill=INK)
    paste_layer(lay, x0, yb, W, H)
arrow(118, 528, 590)          # 흰 방울 곁 ↓
arrow(208, 612, 548)          # 어두운 방울 곁 ↑
# ⑦ 아래 물: 깊을수록 짙게(물빛 화소만 — 물건은 그대로)
a = np.array(pil).astype(np.float32); H0, W0 = a.shape[:2]
deep = np.array([40, 110, 187], np.float32)
dist = np.abs(a - deep).sum(axis=2); m = np.clip((70 - dist) / 40.0, 0, 1); m[:700] = 0
m = cv2.GaussianBlur(m, (0, 0), 1.2)
t = np.clip((np.arange(H0, dtype=np.float32) - 760) / (1144 - 760), 0, 1)[:, None]
target = np.array([33, 46, 94], np.float32); mid = np.array([40, 86, 136], np.float32)
col = np.where(t[..., None] < 0.5, deep + (mid - deep) * (t[..., None] / 0.5), mid + (target - mid) * ((t[..., None] - 0.5) / 0.5))
col = np.broadcast_to(col, a.shape)
out = a * (1 - m[..., None]) + (a - deep + col) * m[..., None]
pil = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
pil.save(dst); print('ok')

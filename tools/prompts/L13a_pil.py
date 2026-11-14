#!/usr/bin/env python3
# L13a_pil.py <조각 폴더(gem_A1 · A2 · B1 · B2 · C1 · P1 · E1 · TW.png)> <out.png> — L13a 「성 방어전 한눈에」 조립.
# 이 그림은 바탕 그림 없이 짓는다(Gemini 의 그림 올리기 동의 창을 누르지 않았으므로 그림을 올려 고치게 할 수 없었다 → 글만으로 그리게 한 조각을 오려 세운다).
#  ① 하늘 · 회색 돌 성벽(성가퀴 · 무너진 틈 · 틈 너머 언덕)은 PIL 이 그린다 — 틈의 자리 · 성벽의 높이를 그림의 짜임에 맞춘다.
#  ② 물건은 모두 Gemini 가 글만 보고 그린 조각 그림(크림빛 민 바탕에 물건 둘 ~ 셋)에서 오려(가장자리에서 이어진 바탕빛을 투명하게) 제자리에 세운다.
#  ③ 셈 · 짝이 뜻인 것은 PIL: 조끼 단추(넷씩 두 줄 = 세포독성 T · 한 줄 넷 = 도움 T) · 주민 셋 가슴의 붉은 꽃 배지 · 게시판 셋과 전단 · 잠옷 병정이 든 종이의 세균 얼굴.
import sys, math, random, numpy as np, cv2
from PIL import Image, ImageDraw
zdir, dst = sys.argv[1:3]
W, H = 2048, 1144
INK = (24, 20, 18, 255)
GND = (239, 232, 202)
SKY = (128, 203, 242, 255)
WALL, WALL_D, WALL_L, WALL_IN = (165, 165, 165, 255), (118, 118, 118, 255), (180, 180, 180, 255), (106, 106, 106, 255)
SHADOW = (203, 196, 168, 255)
im = Image.new('RGB', (W, H), GND)

S = 3
def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay):
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    base = im.convert('RGBA'); base.alpha_composite(small); im = base.convert('RGB')
def T(pts): return [(x * S, y * S) for x, y in pts]
def poly(d, pts, fill, w=3.2, close=True):
    q = T(pts)
    if fill: d.polygon(q, fill=fill)
    if w:
        d.line(q + ([q[0]] if close else []), fill=INK, width=int(w * S), joint='curve')
        for x, y in q: r = w * S / 2; d.ellipse([x - r, y - r, x + r, y + r], fill=INK)
def line(d, pts, w=3.2, col=INK):
    q = T(pts); d.line(q, fill=col, width=int(w * S), joint='curve')
    for x, y in q: r = w * S / 2; d.ellipse([x - r, y - r, x + r, y + r], fill=col)
def disc(d, cx, cy, r, fill, w=2.4):
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=INK if w else fill)
    if w: d.ellipse([(cx - r + w) * S, (cy - r + w) * S, (cx + r - w) * S, (cy + r - w) * S], fill=fill)

# ── 조각 오리기: 조각 그림에서 hint 상자 안에 든 덩이(들)만. 가장자리에서 이어진 바탕빛은 투명 · holes 면 덩이 안에 갇힌 바탕빛(파리채 그물 · 활과 시위 사이 · 난간 살 사이)도 투명
_cache = {}
def comp_sprite(name, hint, holes=False, tol=18, fix=None):
    if name not in _cache:
        c = np.array(Image.open(f'{zdir}/gem_{name}.png').convert('RGB')).astype(int)
        bg = np.median(np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]]), axis=0)
        bgm = (np.abs(c - bg).max(axis=2) <= tol)
        n, lab = cv2.connectedComponents(bgm.astype(np.uint8), connectivity=4)
        border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); border = border[border != 0]
        fg = (~np.isin(lab, border)).astype(np.uint8)
        n2, lab2, st, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
        _cache[name] = (c, lab2, st, bgm)
    c, lab2, st, bgm = _cache[name]
    if fix is not None: c = fix(c.copy())
    x0, y0, x1, y1 = hint
    ids = [i for i in range(1, len(st)) if st[i][0] >= x0 and st[i][1] >= y0 and st[i][0] + st[i][2] <= x1 and st[i][1] + st[i][3] <= y1 and st[i][4] >= 150]
    m = np.isin(lab2, ids); ys, xs = np.where(m); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    if holes is True: m = m & ~bgm
    elif holes:                                                                      # 상자 목록이면 그 상자 안의 갇힌 바탕빛만(얼굴의 밝은 점까지 뚫리지 않게)
        hb = np.zeros_like(bgm)
        for hx0, hy0, hx1, hy1 in holes: hb[hy0:hy1, hx0:hx1] = True
        m = m & ~(bgm & hb)
    al = (m[by0:by1, bx0:bx1] * 255).astype(np.uint8)
    al = cv2.erode(al, np.ones((3, 3), np.uint8)); al = cv2.GaussianBlur(al, (0, 0), 0.9)
    sp = Image.fromarray(np.dstack([c[by0:by1, bx0:bx1].astype(np.uint8), al]), 'RGBA')
    sp.origin = (bx0, by0)
    return sp
def place(sp, scale, cx, bottom, flip=False):
    """조각을 scale 배로 아래 가운데가 (cx, bottom) 에 오게 붙이고, 조각 그림 좌표 → 그림 좌표 함수를 돌려준다."""
    global im
    w, h = max(1, round(sp.width * scale)), max(1, round(sp.height * scale))
    s2 = sp.resize((w, h), Image.LANCZOS)
    if flip: s2 = s2.transpose(Image.FLIP_LEFT_RIGHT)
    x0, y0 = round(cx - w / 2), round(bottom - h)
    base = im.convert('RGBA'); base.alpha_composite(s2, (x0, y0)); im = base.convert('RGB')
    ox, oy = sp.origin
    if flip: return lambda x, y: (x0 + w - (x - ox) * scale, y0 + (y - oy) * scale)
    return lambda x, y: (x0 + (x - ox) * scale, y0 + (y - oy) * scale)
def inpaint(c, boxes, dark=110):
    """상자 안의 검은 획(얼굴)을 둘레 빛깔로 메운다 — Gemini 가 「귀엽게」 그려 넣은 불 · 돌의 얼굴을 지운다."""
    a = c.astype(np.uint8); m = np.zeros(a.shape[:2], np.uint8)
    for x0, y0, x1, y1 in boxes: m[y0:y1, x0:x1] = (a[y0:y1, x0:x1].max(axis=2) < dark) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    return cv2.inpaint(a, m, 4, cv2.INPAINT_TELEA).astype(int)
def unred(c, box):
    """상자 안의 빨강(두루마리를 묶은 리본)을 갈색 끈 빛으로 — 빨간 리본은 덱에서 「선물로 건넨다」(L12g)라 뜻이 샌다."""
    r = c[box[1]:box[3], box[0]:box[2]]; R_, G_, B_ = r[..., 0], r[..., 1], r[..., 2]
    m = (R_ - np.maximum(G_, B_) > 70)
    r[m] = np.stack([R_[m] * 0.62, R_[m] * 0.44, R_[m] * 0.27], axis=1).astype(int)
    return c

def whiten(c, box):
    """상자 안의 크림빛 흰색(바탕빛에 가까운 옷)을 새하얗게 — 다른 경비들의 흰 옷과 같은 빛으로."""
    r = c[box[1]:box[3], box[0]:box[2]]; m = (r.min(axis=2) > 200) & (r[..., 0] - r[..., 2] < 46)
    r[m] = 255
    return c

def teal(c, box):
    """상자 안의 빨강(여자 주민의 원피스)을 청록으로 — 빨간 옷 위에서는 붉은 꽃 배지가 묻힌다."""
    r = c[box[1]:box[3], box[0]:box[2]]; R_, G_, B_ = r[..., 0], r[..., 1], r[..., 2]
    m = (R_ - G_ > 78) & (R_ - B_ > 78)                                             # 갈색 머리카락(R − G ≈ 60)은 건드리지 않는다
    f = R_[m] / 225.0; r[m] = np.stack([64 * f, 168 * f, 160 * f], axis=1).astype(int)
    return c

def stretch_bar(sp, dL, cap=15, post=182, rows=(258, 316)):
    """초소 조각의 가로대를 왼쪽으로 dL 만큼 늘인다(끝마개 cap 은 그대로 · 가운데 토막만 가로로 늘임) — 가로대가 틈 앞을 다 가로지르게."""
    a = np.array(sp); h, w = a.shape[:2]; r0, r1 = rows
    out = np.zeros((h, w + dL, 4), np.uint8); out[:, dL:] = a
    out[r0:r1, dL:dL + post] = 0
    out[r0:r1, :cap] = a[r0:r1, :cap]
    out[r0:r1, cap:post + dL] = np.array(Image.fromarray(a[r0:r1, cap:post], 'RGBA').resize((post - cap + dL, r1 - r0), Image.LANCZOS))
    o = Image.fromarray(out, 'RGBA'); o.origin = (sp.origin[0] - dL, sp.origin[1]); return o
def chaikin(pts, it=2):
    for _ in range(it):
        q = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            q += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = q
    return pts

# ── ① 하늘 · 성벽 · 틈
TOP, FLOOR, LEDGE, WB = 46, 96, 178, 430          # 성가퀴 윗변 · 성가퀴 사이 바닥 · 턱 줄 · 성벽 밑
GAP_L = [(632, TOP), (632, 120), (648, 120), (648, 168), (636, 168), (636, 214), (658, 214), (658, 262), (646, 262), (646, 300), (668, 300), (668, 350), (658, 350), (658, 392), (678, 392), (678, WB)]
GAP_R = [(884, TOP), (884, 112), (868, 112), (868, 160), (880, 160), (880, 206), (858, 206), (858, 250), (870, 250), (870, 296), (848, 296), (848, 344), (860, 344), (860, 388), (838, 388), (838, WB)]
TH = 26                                              # 틈 옆으로 보이는 성벽의 두께(짙은 회색 띠)
lay = layer(); d = ImageDraw.Draw(lay)
d.rectangle([0, 0, W * S, WB * S], fill=SKY)
d.rectangle([0, WB * S, W * S, H * S], fill=GND + (255,))                                        # 언덕은 성벽 밑줄 위로만
d.rectangle([600 * S, 396 * S, 960 * S, (WB + 4) * S], fill=GND + (255,)); line(d, [(600, 396), (960, 396)], 3.0)   # 틈 너머는 하늘뿐 · 틈으로 이어지는 맨바닥(언덕을 그렸더니 망토 뒤에 낀 「초록 네모」로 읽혔다 — 일치 검사 1회)
# 틈 옆의 두께 띠(성벽의 잘린 면) — 벽 몸보다 먼저, 틈 쪽으로 TH 만큼 내밀어
poly(d, GAP_L + [(x + TH, y) for x, y in reversed(GAP_L)], WALL_IN, 3.2)
poly(d, GAP_R + [(x - TH, y) for x, y in reversed(GAP_R)], WALL_IN, 3.2)
# 벽 몸 둘(틈의 왼쪽 · 오른쪽)
poly(d, [(-10, FLOOR), (GAP_L[0][0], FLOOR)] + GAP_L[1:] + [(-10, WB)], WALL, 3.4)
poly(d, [(GAP_R[0][0], FLOOR), (W + 10, FLOOR), (W + 10, WB)] + list(reversed(GAP_R[1:])), WALL, 3.4)
def edge_x(g, y):                                                                                 # 틈 가장자리 꺾은선이 높이 y 에서 지나는 x
    for (x0, y0), (x1, y1) in zip(g, g[1:]):
        if x0 == x1 and y0 <= y <= y1: return x0
for xa, xb in ((-10, edge_x(GAP_L, LEDGE + 7)), (edge_x(GAP_R, LEDGE + 7), W + 10)):               # 턱(두 줄 사이 밝은 띠)
    d.rectangle([xa * S, LEDGE * S, xb * S, (LEDGE + 14) * S], fill=WALL_L)
    line(d, [(xa, LEDGE), (xb, LEDGE)], 3.0); line(d, [(xa, LEDGE + 14), (xb, LEDGE + 14)], 3.0)
# 성가퀴: 앞면 62 + 오른쪽 옆면 14, 사이 48 (틈에 걸리는 것은 그리지 않는다)
MW, MS, PITCH = 62, 14, 124
for k in range(-1, 18):
    x = 18 + k * PITCH
    if x + MW + MS > GAP_L[0][0] - 4 and x < GAP_R[0][0] + 4: continue
    poly(d, [(x + MW, TOP), (x + MW + MS, TOP + 6), (x + MW + MS, FLOOR), (x + MW, FLOOR)], WALL_D, 3.0)
    poly(d, [(x, TOP), (x + MW, TOP), (x + MW, FLOOR), (x, FLOOR)], WALL, 3.2)
    d.rectangle([(x + 2) * S, (FLOOR - 2) * S, (x + MW - 2) * S, (FLOOR + 3) * S], fill=WALL)   # 성가퀴 밑변의 줄을 지워 벽 몸과 한 덩이로
# 틈 가장자리의 성가퀴 반쪽(깨진 끝)
poly(d, [(GAP_L[0][0] - 44, TOP), (GAP_L[0][0], TOP), (GAP_L[0][0], FLOOR), (GAP_L[0][0] - 44, FLOOR)], WALL, 3.2)
d.rectangle([(GAP_L[0][0] - 42) * S, (FLOOR - 2) * S, (GAP_L[0][0] - 2) * S, (FLOOR + 3) * S], fill=WALL)
poly(d, [(GAP_R[0][0], TOP), (GAP_R[0][0] + 50, TOP), (GAP_R[0][0] + 50, FLOOR), (GAP_R[0][0], FLOOR)], WALL, 3.2)
d.rectangle([(GAP_R[0][0] + 2) * S, (FLOOR - 2) * S, (GAP_R[0][0] + 48) * S, (FLOOR + 3) * S], fill=WALL)
# 벽면의 돌(짙은 회색 둥근 네모 — 내성 탑의 돌과 같은 꼴)
random.seed(13)
for (sx, sy, sw, sh) in ((70, 222, 70, 30), (232, 282, 58, 26), (420, 232, 62, 28), (552, 286, 54, 26), (932, 226, 60, 28), (1128, 214, 58, 26), (1300, 286, 62, 28), (1392, 226, 56, 26)):   # 물건에 반쯤 가리는 자리는 비웠다(게시판 · 흰 덩이 뒤에서 「탭 · 창」처럼 비죽 나왔다 — 일치 검사 4 · 5회)
    d.rounded_rectangle([sx * S, sy * S, (sx + sw) * S, (sy + sh) * S], radius=7 * S, fill=INK)
    d.rounded_rectangle([(sx + 3) * S, (sy + 3) * S, (sx + sw - 3) * S, (sy + sh - 3) * S], radius=5 * S, fill=(146, 146, 142, 255))
line(d, [(-10, WB), (GAP_L[-1][0], WB)], 3.6); line(d, [(GAP_R[-1][0], WB), (W + 10, WB)], 3.6)
put(lay)

# ── ② 조각들
def fix_tw(c):
    """내성 탑 조각 손질: 잠옷 앞섶의 작은 단추 셋을 앞섶 빛으로 덮고(「한 줄 넷쯤」으로 세어졌다 — 일치 검사 2회 · 단추의 줄과 개수는 CD4 · CD8 예약),
    오른쪽 병정의 뺨에 내려온 턱끈 한 줄을 지운다(왼쪽 병정에는 없어 「이중선」으로 읽혔다 — 일치 검사 2 · 3회)."""
    a = c.astype(np.uint8).copy()
    for bx, by in ((313.5, 839.5), (310.5, 856.5), (306.0, 873.5)): cv2.circle(a, (round(bx * 8), round(by * 8)), 40, (217, 239, 250), -1, cv2.LINE_AA, 3)
    # 턱끈 = 얼굴 테두리 안쪽으로 나란히 내려온 검은 줄. 테두리와 턱끈 사이에 낀 살빛 실오라기와 얼굴 본바닥 사이의 어두운 것만 살빛으로 덮는다(상자째 덮으면 테두리가 뜯기고, 둘레 빛으로 메우면 얼룩이 남았다 — 일치 검사 4회)
    x0, y0, x1, y1 = 386, 318, 470, 366; r = a[y0:y1, x0:x1].astype(int)
    sk = ((r[..., 0] > 215) & (r[..., 1] > 170) & (r[..., 2] > 135) & (r[..., 0] - r[..., 2] > 30)).astype(np.uint8)
    n, lab = cv2.connectedComponents(sk, connectivity=4); main = lab == lab[345 - y0, 425 - x0]
    sliver = (sk > 0) & ~main; sliver[:, 30:] = False                                # 왼쪽 뺨 쪽(x < 416)의 실오라기만
    k = np.ones((3, 3), np.uint8)
    strap = (sk == 0) & (cv2.dilate(sliver.astype(np.uint8), k, iterations=4) > 0) & (cv2.dilate(main.astype(np.uint8), k, iterations=4) > 0)
    skin = np.median(r[main], axis=0); rr = a[y0:y1, x0:x1]; rr[strap | sliver] = skin
    r2 = a[355:359, 408:417]; r2[r2.max(axis=2) < 190] = skin                         # 턱 선에 붙어 남은 턱끈 밑동(네 줄)
    return a.astype(int)
def fix_b2(c):
    c[367:420, 797:850] = (164, 170, 170)                                             # 인터폰의 단추 열여섯(넷씩 네 줄)을 판 빛으로 덮는다 — 「한 줄에 넷인 둥근 단추」는 CD4 예약
    return c
def fix_e1(c): return inpaint(c, [(203, 230, 272, 262), (744, 380, 812, 400), (549, 446, 610, 474)])
SP = {
 'BLOB': comp_sprite('A3', (50, 85, 485, 500)),                                    # 세균이 통째로 입 안 혀 위에 든 흰 덩이 — 반쯤 물린 것(A1)은 「먹히는지 뱉는지 꿰인 건지」 애매하다고 읽혔다(일치 검사 1 · 3 · 4 · 5회)
 'GUARD': comp_sprite('A1', (620, 40, 980, 520), holes=True),
 'GERM1': comp_sprite('A2', (30, 140, 285, 455), holes=True),
 'GERM2': comp_sprite('A2', (250, 140, 615, 455), holes=True),
 'CLOAK': comp_sprite('A2', (700, 115, 985, 460), fix=lambda c: unred(c, (700, 115, 985, 460))),
 'BOOTH': stretch_bar(comp_sprite('B1', (20, 70, 555, 500)), 172),                    # 가로대를 늘여 틈 앞을 다 가로지르게(끝이 틈 오른쪽 가장자리에서 그쳤다 — 일치 검사 1 · 2회)
 'SACK': comp_sprite('B1', (660, 75, 975, 512)),
 'ARCHER': comp_sprite('F1', (60, 25, 375, 540), holes=[(303, 36, 354, 522)], fix=lambda c: whiten(c, (60, 25, 375, 540))),   # 활과 시위 사이만 뚫는다 ·                      # 활을 세워 쥐고 망보는 궁수 — 시위를 당겨 누군가를 겨눈 궁수(B2)는 겨눈 쪽의 것을 쏘는 것으로 읽혔다(일치 검사 1회 · NK 는 세균을 쏘지 않는다)
 'COTTAGE': comp_sprite('B2', (525, 85, 985, 515), fix=fix_b2),
 'MAN': comp_sprite('C1', (70, 105, 212, 465), holes=True),
 'WOMAN': comp_sprite('C1', (207, 127, 338, 465), holes=True, fix=lambda c: teal(c, (207, 244, 338, 424))),
 'CHILD': comp_sprite('C1', (335, 238, 440, 465), holes=True),
 'DITCH': comp_sprite('C1', (515, 105, 975, 465)),
 'P_TAIL': comp_sprite('F1', (525, 35, 975, 520)),                                # 점선 알약 몸 + 굵은 초록 꼬리 — 꼬리만 그린 전단(P1)은 「초록 뱀」으로 읽혔다(일치 검사 1회)
 'P_ROPE': comp_sprite('P1', (380, 154, 645, 420)),
 'P_SCROLL': comp_sprite('P1', (695, 154, 960, 420), fix=lambda c: unred(c, (695, 215, 960, 420))),
 'BEACON': comp_sprite('E1', (95, 35, 385, 540), holes=True, fix=fix_e1),
 'STONES': comp_sprite('E1', (525, 250, 955, 525), holes=True, fix=fix_e1),
 'TOWER': comp_sprite('TW', (20, 20, 545, 1005), holes=[(30, 450, 140, 612), (424, 450, 540, 612)], fix=fix_tw),   # 발코니 양 끝의 난간 살 사이만 뚫는다
 'HAT': comp_sprite('A3', (540, 125, 755, 445), holes=[(598, 376, 718, 436)]),      # 병정의 검은 털모자(금빛 턱끈) — PIL 로 그린 민 통은 「양동이 · 종 · 돔」으로 읽혔다(일치 검사 1 ~ 5회)
 'BOOT': comp_sprite('A3', (810, 155, 985, 432)),
}
lay = layer(); d = ImageDraw.Draw(lay)
def shadow(cx, cy, rx, ry): d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=SHADOW)

# 자리(모두 2048 x 1144 좌표): (조각, 배율, 가운데 x, 발끝 y, 뒤집기, 그림자 반폭)
TW_S = 1.30
PL = [
 ('STONES', 0.40, 626, 508, False, 0),
 ('STONES', 0.26, 886, 476, True, 0),
 ('BEACON', 0.32, 1322, LEDGE + 4, False, 0),
 ('CLOAK', 0.72, 748, 540, False, 64),                                          # 가로대(초소 조각)가 정강이 앞을 가로막게 — 발끝이 가로대 높이면 「딛고 선 판자」로 읽혔다(일치 검사 3회)
 ('BLOB', 0.72, 172, 606, False, 118),
 ('GUARD', 0.66, 462, 616, False, 70),
 ('BOOTH', 0.80, 1210 - 686 * 0.80 / 2, 596, False, 0),
 ('GERM1', 0.62, 612, 668, False, 52),
 ('GERM2', 0.62, 800, 724, False, 62),
 ('TOWER', TW_S, 2046 - 496 * TW_S / 2, 1140, False, 0),
 ('HAT', 0.42, 1872, 1138, False, 40),
 ('BOOT', 0.40, 1980, 1136, True, 34),
 ('DITCH', 0.74, 164, 1120, False, 0),
 ('SACK', 0.80, 470, 1112, False, 100),
 ('ARCHER', 0.60, 1058, 1124, False, 62),
 ('COTTAGE', 0.66, 1270, 1046, False, 0),
 ('MAN', 0.60, 1392, 1124, False, 34),
 ('WOMAN', 0.60, 1464, 1124, False, 32),
 ('CHILD', 0.60, 1528, 1124, False, 26),
]
for nm, sc, cx, bot, fl, sh in PL:
    if sh: shadow(cx, bot - 4, sh, max(7, sh * 0.11))
shadow(1070, 592, 122, 13)                                                          # 초소 몸통 밑
put(lay)
TF = {}
for nm, sc, cx, bot, fl, sh in PL:
    TF[nm if nm not in TF else nm + '2'] = place(SP[nm], sc, cx, bot, fl)

# ── ③ 게시판과 전단(전단 그림은 Gemini 조각 · 판과 기둥은 PIL)
WOOD, WOOD_D = (176, 124, 72, 255), (140, 96, 54, 255)
def board(d, x0, y0, n, bottom, pw, ph):
    """전단 n 장(장마다 pw x ph)을 붙인 나무 게시판 — 왼쪽 위 (x0, y0) · 기둥이 bottom 까지. 돌려주는 값 = 전단을 붙일 자리들(왼쪽 위)."""
    bw = n * pw + (n + 1) * 14; bh = ph + 28
    posts = [x0 + bw / 2] if n == 1 else [x0 + 34, x0 + bw - 34]
    for px in posts: poly(d, [(px - 11, y0 + bh - 4), (px + 11, y0 + bh - 4), (px + 11, bottom), (px - 11, bottom)], WOOD_D, 3.0)
    poly(d, [(x0, y0), (x0 + bw, y0), (x0 + bw, y0 + bh), (x0, y0 + bh)], WOOD, 3.4)
    for k in range(1, 3): line(d, [(x0 + 6, y0 + bh * k / 3), (x0 + bw - 6, y0 + bh * k / 3)], 1.6, WOOD_D)
    return [(x0 + 14 + k * (pw + 14), y0 + 14) for k in range(n)]
PW = 162; PW1 = 180; PH1 = round(PW1 * SP['P_TAIL'].height / SP['P_TAIL'].width)
lay = layer(); d = ImageDraw.Draw(lay)
shadow(1300, 610, 46, 8); shadow(630, 1112, 34, 7); shadow(928, 1112, 34, 7)
put(lay)
lay = layer(); d = ImageDraw.Draw(lay)
slots1 = board(d, 1196, 352, 1, 610, PW1, PH1)
slots2 = board(d, 596, 806, 2, 1112, PW, PW)
put(lay)
base = im.convert('RGBA')
for nm, (x, y), (pw, ph) in zip(('P_TAIL', 'P_ROPE', 'P_SCROLL'), slots1 + slots2, ((PW1, PH1), (PW, PW), (PW, PW))):
    base.alpha_composite(SP[nm].resize((pw, ph), Image.LANCZOS), (round(x), round(y)))
im = base.convert('RGB')

# ── ④ 조끼 단추 · 붉은 꽃 배지 · 잠옷 병정의 종이
tw = TF['TOWER']
GOLD = (242, 190, 52, 255)
lay = layer(); d = ImageDraw.Draw(lay)
BR = 7.2                                                                              # 단추 반지름(그림 좌표)
for bx in (277, 303):                                                                 # 왼쪽 병정: 넷씩 두 줄 = 여덟(세포독성 T · CD8)
    for by in (388, 400, 412, 424): disc(d, *tw(bx, by), BR, GOLD, 2.2)
for by in (390, 401.5, 413, 424.5): disc(d, *tw(428, by), BR, GOLD, 2.2)             # 오른쪽 병정: 한 줄 넷(도움 T · CD4)
RED, RED_D = (226, 46, 42, 255), (188, 34, 34, 255)
def badge(cx, cy, r):
    """붉은 리본 배지(로제트) — 물결 테두리의 붉은 둥근 꽃 + 금빛 가운데 + 아래로 늘어진 리본 꼬리 둘. 「자기」의 표지(옛 s13p03 의 「전원이 단 둥근 배지」 = MHC I)."""
    w = max(1.5, r * 0.16)
    for sx in (-1, 1):
        poly(d, [(cx + sx * 0.10 * r, cy + 0.55 * r), (cx + sx * 0.62 * r, cy + 0.50 * r), (cx + sx * 0.98 * r, cy + 1.85 * r), (cx + sx * 0.58 * r, cy + 1.55 * r), (cx + sx * 0.30 * r, cy + 1.95 * r)], RED_D, w)
    for k in range(10):
        a = 2 * math.pi * k / 10; disc(d, cx + 0.80 * r * math.cos(a), cy + 0.80 * r * math.sin(a), 0.30 * r, RED, w)
    d.ellipse([(cx - 0.84 * r) * S, (cy - 0.84 * r) * S, (cx + 0.84 * r) * S, (cy + 0.84 * r) * S], fill=RED)
    disc(d, cx, cy, 0.38 * r, (250, 208, 62, 255), w)
# 성 안의 것은 모두 같은 배지를 단다(주민 셋 · 경비 셋 · 궁수 · 병정 둘 · 벌 · 잠옷 병정 · 흰 덩이) — 없는 것은 침입자뿐. 주민만 달면 「배지 없는 경비 · 병정 = 비자기」로 읽힌다(옛 판 logic_0929 가 고친 바로 그 자리)
for nm, (zx, zy), rr in (('MAN', (168, 286), 12), ('WOMAN', (272, 286), 12), ('CHILD', (393, 360), 10),
                         ('GUARD', (847, 289), 11), ('ARCHER', (240, 245), 10), ('BOOTH', (346, 335), 7.5), ('SACK', (824, 358), 6.5),
                         ('TOWER', (264, 370), 8), ('TOWER', (398, 372), 8), ('TOWER', (152, 412), 9), ('TOWER', (291, 847), 8.5), ('BLOB', (124, 392), 13)):
    badge(*TF[nm](zx, zy), rr)
put(lay)
# 잠옷 병정이 든 흰 종이에 세균 한 놈의 얼굴(= 딱 이놈만 쫓는다 · 특이성)
g = SP['GERM1']; gs = (56 * TW_S) / g.height
gg = g.resize((round(g.width * gs), round(g.height * gs)), Image.LANCZOS)
x, y = tw(231, 797); base = im.convert('RGBA'); base.alpha_composite(gg, (round(x - gg.width / 2 + 3), round(y - gg.height / 2))); im = base.convert('RGB')
# 잠옷 병정 발치의 털모자 · 장화 한 짝은 조각(A3)으로 세웠다(PL 의 HAT · BOOT).
im.save(dst)
print('ok', dst)
for nm, sc, cx, bot, fl, sh in PL: print(f'{nm:8s} x {round(cx - SP[nm].width * sc / 2):5d} ~ {round(cx + SP[nm].width * sc / 2):5d}  y {round(bot - SP[nm].height * sc):5d} ~ {round(bot):5d}')

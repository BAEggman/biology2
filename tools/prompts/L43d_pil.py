#!/usr/bin/env python3
# L43d_pil.py <바탕+구역.png> <gem_Z1.png> <gem_Z3.png> <PR.png> <out.png> — L43d 「같은 끈, 다른 공장」 조립.
# 이 그림의 뼈대는 「두 마당의 끈과 가구가 똑같다 · 인쇄 기계가 선 자리와 응원단만 다르다」 — 그 뼈대를 Gemini 에게 맡기지 않는다.
#  ① 마당 가구 한 벌(끈 · 응원 단 둘 · 타탄 깔개 넷 · 그림 팻말 넷)을 함수 하나로 그려 위 마당 · 아래 마당(+ DY)에 똑같이 찍는다.
#  ② 인쇄 기계는 Gemini 가 따로 그린 한 대(PR)를 오려 네 자리에 붙이고, 그 앞에 팻말과 같은 그림의 종이띠를 그린다.
#  ③ 응원단 두 조 · 붉은 벽돌집은 또렷하게 다시 그린 조각(Z1 · Z3)에서 오려 단 위 · 마당 끝에 세운다(Z1 은 Gemini 가 집과 응원단의 사이를 바꿔 돌려줘 통째로 못 붙였다).
#  ④ 담장 밖: 두 아기에서 두 마당으로 가는 초록 화살 둘 · 뼈 속 아주머니에서 혈구로 가는 화살 하나 · 달걀 구멍 위의 끈 타래와 위 마당에서 온 점선.
import sys, math, numpy as np, cv2
from PIL import Image, ImageDraw
src, pZ1, pZ3, pPR, dst = sys.argv[1:6]
im = Image.open(src).convert('RGB'); W, H = im.size
a = np.array(im).astype(int)
INK = (24, 20, 18, 255)
GND = np.array([239, 233, 203])
DY = 531                                                                           # 아래 마당 = 위 마당 + 531(두 담 띠의 아랫줄 y 92 → 623)

# ── ⓞ 바탕의 흐린 벽돌집 · 초록 응원단 · 보라 응원단을 지운다(또렷한 조각을 오려 새로 세운다)
a[100:462, 0:432] = GND; a[640:868, 1196:1434] = GND; a[868:906, 1196:1416] = GND
# ── ⓪ 구역을 붙인 자리의 흰 번짐(후광)을 바닥 빛으로
isg = np.abs(a - GND).max(axis=2) <= 7
inkm = a.max(axis=2) < 90
light = a.min(axis=2) >= 180
n, lab = cv2.connectedComponents(light.astype(np.uint8), connectivity=4)
cnt = np.bincount(lab[isg], minlength=n); gl = np.where(cnt >= 1500)[0]; gl = gl[gl != 0]
brighter = (a[..., 0] >= 243) & (a[..., 1] >= 237) & (a[..., 2] >= 208)
halo = brighter & np.isin(lab, gl) & (cv2.dilate(inkm.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
halo[:, :1416][:96] = False; halo[527:627, :1416] = False                          # 담 띠는 건드리지 않는다
a[halo] = GND
for y0, y1 in ((0, 104), (520, 634)):                                              # 담 띠 오른쪽 끝에 둘린 흰 테(바탕 그림의 것)
    reg = a[y0:y1, 1404:1440]; reg[(reg > GND + 3).all(axis=2)] = GND
print('후광', int(halo.sum()), 'px')
im = Image.fromarray(a.astype(np.uint8))

S = 3
def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay, rows=None):
    """겹을 줄여 얹는다 — rows = (y0, y1) 이면 그 줄들에만."""
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    if rows:
        al = np.asarray(small.split()[3]).copy(); al[:rows[0]] = 0; al[rows[1]:] = 0; small.putalpha(Image.fromarray(al))
    base = im.convert('RGBA'); base.alpha_composite(small); im = base.convert('RGB')
def T(pts): return [(x * S, y * S) for x, y in pts]
def spline(pts, n=24):
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = [np.array(p, float) for p in P[i - 1:i + 3]]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(P[-2])); return out
def resample(q, step=1.0):
    u = [q[0]]; acc = 0.0
    for (x0, y0), (x1, y1) in zip(q, q[1:]):
        seg = math.hypot(x1 - x0, y1 - y0); t = step - acc
        while t <= seg:
            u.append((x0 + (x1 - x0) * t / seg, y0 + (y1 - y0) * t / seg)); t += step
        acc = (acc + seg) % step
    return u
ROPE, ROPE_D = (236, 196, 96, 255), (176, 128, 44, 255)
RW, RO = 13, 2.4
def rope(d, pts, smooth=True):
    """금빛 짚끈 — 1 px 걸음으로 원을 찍어 그린다(넓은 선은 꺾인 마디에 틈이 난다 · L43c)."""
    u = resample(spline(pts) if smooth else pts)
    for r, col in (((RW + 2 * RO) / 2, INK), (RW / 2, ROPE)):
        for x, y in u: d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=col)
    for k in range(5, len(u) - 1, 9):
        (x0, y0), (x1, y1) = u[k - 1], u[k + 1]; seg = math.hypot(x1 - x0, y1 - y0) or 1
        tx, ty = (x1 - x0) / seg, (y1 - y0) / seg; nx, ny = -ty, tx; x, y = u[k]; h = RW * 0.44
        d.line([((x - nx * h - tx * 3.2) * S, (y - ny * h - ty * 3.2) * S), ((x + nx * h + tx * 3.2) * S, (y + ny * h + ty * 3.2) * S)], fill=ROPE_D, width=int(1.7 * S))
def poly(d, pts, fill, w=3.2):
    q = T(pts); d.polygon(q, fill=fill); d.line(q + [q[0]], fill=INK, width=int(w * S), joint='curve')
    for x, y in q: r = w * S / 2; d.ellipse([x - r, y - r, x + r, y + r], fill=INK)

# ── 그림 넷(팻말과 종이띠가 같이 쓴다) — (cx, cy) 가운데 · s = 한 변
def ic_album(d, cx, cy, s):
    """펼친 사진 앨범(L46d 의 그 앨범 = 알부민) — 책등에 고리 셋 · 쪽마다 흰 테 사진 한 장(산과 해 / 사람 얼굴)."""
    w, h, k = s * 1.24, s * 0.80, s * 0.08
    poly(d, [(cx - w / 2 - 4, cy - h / 2 - 3), (cx, cy - h / 2 + k - 3), (cx + w / 2 + 4, cy - h / 2 - 3), (cx + w / 2 + 4, cy + h / 2 + 2), (cx, cy + h / 2 + k + 3), (cx - w / 2 - 4, cy + h / 2 + 2)], (150, 96, 56, 255), 2.4)
    for sg in (-1, 1):
        xo, xi = cx + sg * w / 2, cx + sg * 2.5
        pt = lambda u, v: (xo + (xi - xo) * u, (cy - h / 2 + k * u) + (h - 2) * v)
        poly(d, [pt(0, 0), pt(1, 0), pt(1, 1), pt(0, 1)], (236, 222, 196, 255), 2)
        poly(d, [pt(0.12, 0.16), pt(0.86, 0.16), pt(0.86, 0.84), pt(0.12, 0.84)], (255, 255, 255, 255), 1.6)          # 사진의 흰 테
        q = [pt(0.19, 0.24), pt(0.79, 0.24), pt(0.79, 0.70), pt(0.19, 0.70)]
        if sg < 0:                                                                                                     # 왼쪽 사진: 하늘 · 해 · 초록 산
            d.polygon(T(q), fill=(132, 196, 240, 255))
            d.polygon(T([pt(0.19, 0.70), pt(0.42, 0.40), pt(0.58, 0.58), pt(0.68, 0.46), pt(0.79, 0.62), pt(0.79, 0.70)]), fill=(88, 170, 96, 255))
            sx, sy = pt(0.66, 0.34); d.ellipse([(sx - 3.4) * S, (sy - 3.4) * S, (sx + 3.4) * S, (sy + 3.4) * S], fill=(250, 204, 60, 255))
        else:                                                                                                          # 오른쪽 사진: 사람 얼굴과 어깨
            d.polygon(T(q), fill=(246, 178, 110, 255))
            hx, hy = pt(0.49, 0.42); d.ellipse([(hx - 4.6) * S, (hy - 4.6) * S, (hx + 4.6) * S, (hy + 4.6) * S], fill=(92, 62, 48, 255))
            d.polygon(T([pt(0.28, 0.70), pt(0.34, 0.58), pt(0.64, 0.58), pt(0.70, 0.70)]), fill=(92, 62, 48, 255))
        d.line(T(q + [q[0]]), fill=INK, width=int(1.3 * S))
    for j in (-1, 0, 1):                                                                                               # 책등의 고리 셋
        ry = cy + k + j * h * 0.27
        d.ellipse([(cx - 5) * S, (ry - 3.2) * S, (cx + 5) * S, (ry + 3.2) * S], fill=(200, 204, 210, 255), outline=INK, width=int(1.3 * S))
def ic_vacuum(d, cx, cy, s):
    """빨간 통 청소기(통 · 주름 호스 · 대롱 · 바닥 흡입구 · 전깃줄과 플러그) — 집 청소 = 하우스키핑.
    처음의 빨래 그림은 곁의 굴대 기계를 「빨래 짜는 기계」로 읽히게 했고(일치 검사 1 · 2회), 세워 미는 꼴은 「잔디깎이」로도 읽혔다(3회)."""
    def tube(pts, w, col):
        q = resample(spline(pts))
        for r, c in (((w + 3.2) / 2, INK), (w / 2, col)):
            for x, y in q: d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    bx, by = cx + s * 0.20, cy + s * 0.20
    tube([(bx + s * 0.20, by - s * 0.02), (bx + s * 0.34, by - s * 0.16), (bx + s * 0.30, by - s * 0.36), (bx + s * 0.40, by - s * 0.44)], 1.8, (60, 60, 66, 255))      # 전깃줄
    d.rectangle([(bx + s * 0.36) * S, (by - s * 0.53) * S, (bx + s * 0.46) * S, (by - s * 0.42) * S], fill=(60, 60, 66, 255), outline=INK, width=int(1.2 * S))            # 플러그
    for px in (bx + s * 0.385, bx + s * 0.435): d.line([px * S, (by - s * 0.60) * S, px * S, (by - s * 0.53) * S], fill=INK, width=int(1.6 * S))
    tube([(bx - s * 0.16, by - s * 0.08), (bx - s * 0.30, by - s * 0.34), (bx - s * 0.44, by - s * 0.52), (bx - s * 0.56, by - s * 0.46)], 5, (120, 126, 138, 255))      # 주름 호스
    tube([(bx - s * 0.56, by - s * 0.46), (bx - s * 0.66, by + s * 0.20)], 3.6, (206, 210, 218, 255))                                                                   # 대롱
    poly(d, [(bx - s * 0.84, by + s * 0.30), (bx - s * 0.52, by + s * 0.30), (bx - s * 0.56, by + s * 0.17), (bx - s * 0.76, by + s * 0.17)], (70, 74, 84, 255), 2)     # 바닥 흡입구
    d.ellipse([(bx - s * 0.25) * S, (by - s * 0.17) * S, (bx + s * 0.25) * S, (by + s * 0.17) * S], fill=(222, 62, 56, 255), outline=INK, width=int(2.4 * S))            # 빨간 통
    d.ellipse([(bx - s * 0.10) * S, (by - s * 0.10) * S, (bx + s * 0.06) * S, (by + s * 0.02) * S], fill=(244, 150, 140, 255))
    for wx in (bx - s * 0.13, bx + s * 0.14): d.ellipse([(wx - s * 0.07) * S, (by + s * 0.10) * S, (wx + s * 0.07) * S, (by + s * 0.24) * S], fill=(40, 40, 46, 255), outline=INK, width=int(1.4 * S))
def ic_sun(d, cx, cy, s):
    """해(L43c 의 그 유전자)."""
    r = s * 0.25
    for k in range(8):
        an = k * math.pi / 4; d.line([(cx + r * 1.38 * math.cos(an)) * S, (cy + r * 1.38 * math.sin(an)) * S, (cx + r * 1.95 * math.cos(an)) * S, (cy + r * 1.95 * math.sin(an)) * S], fill=(240, 168, 40, 255), width=int(3.6 * S))
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(250, 202, 52, 255), outline=INK, width=int(2.4 * S))
def ic_crystal(d, cx, cy, s):
    """받침대 위의 맑은 수정 구슬(크리스탈린) — 깎은 면 없는 둥근 공(보석 = 다이닌 예약)."""
    r = s * 0.35; by = cy - s * 0.08
    poly(d, [(cx - s * 0.26, cy + s * 0.46), (cx + s * 0.26, cy + s * 0.46), (cx + s * 0.17, cy + s * 0.25), (cx - s * 0.17, cy + s * 0.25)], (124, 86, 54, 255), 2.2)
    d.ellipse([(cx - r) * S, (by - r) * S, (cx + r) * S, (by + r) * S], fill=(198, 230, 250, 255), outline=INK, width=int(2.6 * S))
    d.ellipse([(cx - r * 0.62) * S, (by - r * 0.66) * S, (cx - r * 0.10) * S, (by - r * 0.30) * S], fill=(255, 255, 255, 255))
    d.arc([(cx - r * 0.72) * S, (by - r * 0.72) * S, (cx + r * 0.72) * S, (by + r * 0.72) * S], 20, 80, fill=(150, 196, 232, 255), width=int(2.4 * S))
    sx, sy = cx + r * 1.02, by - r * 0.98
    d.polygon(T([(sx, sy - 8), (sx + 2, sy - 2), (sx + 8, sy), (sx + 2, sy + 2), (sx, sy + 8), (sx - 2, sy + 2), (sx - 8, sy), (sx - 2, sy - 2)]), fill=(104, 164, 228, 255))   # 네 갈래 별(더하기 표로 읽히지 않게)
ICONS = (ic_album, ic_vacuum, ic_sun, ic_crystal)                                   # 끈을 따라 왼 → 오른: 앨범 · 청소기 · 해 · 수정 구슬

# ── 조각 오리기: 바탕(가장자리에서 이어진 바탕빛 · 그림자빛)을 투명하게
def sprite(path, box, shadow=True, tol=18):
    c = np.array(Image.open(path).convert('RGB')).astype(int)[box[1]:box[3], box[0]:box[2]]
    bg = np.median(np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]]), axis=0)
    R_, G_, B_ = c[..., 0], c[..., 1], c[..., 2]
    bgm = np.abs(c - bg).max(axis=2) <= tol
    if shadow: bgm |= (R_ >= 150) & (R_ <= 234) & (np.abs(R_ - G_) <= 12) & (R_ - B_ >= 8) & (R_ - B_ <= 50)
    n, lab = cv2.connectedComponents(bgm.astype(np.uint8), connectivity=4)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); border = border[border != 0]
    al = (~np.isin(lab, border)).astype(np.uint8) * 255
    al = cv2.erode(al, np.ones((3, 3), np.uint8)); al = cv2.GaussianBlur(al, (0, 0), 0.9)
    return Image.fromarray(np.dstack([c.astype(np.uint8), al]), 'RGBA')
def stick(sp, scale, cx, bottom):
    """조각을 scale 배로 줄여 아래 가운데가 (cx, bottom) 에 오게 붙인다."""
    global im
    w, h = max(1, round(sp.width * scale)), max(1, round(sp.height * scale))
    s2 = sp.resize((w, h), Image.LANCZOS)
    base = im.convert('RGBA'); base.alpha_composite(s2, (round(cx - w / 2), round(bottom - h))); im = base.convert('RGB')
SP_HOUSE = sprite(pZ1, (60, 150, 436, 724)); SP_GRN = sprite(pZ1, (470, 104, 998, 636)); SP_PUR = sprite(pZ3, (46, 84, 876, 940)); SP_PRESS = sprite(pPR, (140, 132, 936, 854), shadow=False)

# ── 마당 가구 한 벌(위 마당 좌표 · dy 를 더해 아래 마당)
YR = 392                                                                           # 끈의 높이
PA, PC = 184, 1164                                                                 # 왼쪽 단 · 오른쪽 단의 앞면 왼쪽 x(너비 150)
X0S = (376, 566, 756, 946)                                                         # 깔개 넷의 자리(190 간격) — 오른쪽 끝에 화살이 들어올 빈 바닥 50 px 를 남긴다
WOODF, WOODT, WOODS = (206, 160, 104, 255), (230, 192, 138, 255), (182, 136, 86, 255)
GRN, PUR = (86, 176, 96, 255), (150, 92, 200, 255)
def box3(d, x0, y0, x1, y1, dx=24, dy_=19):
    for pts, col in (([(x0, y0), (x1, y0), (x1 + dx, y0 - dy_), (x0 + dx, y0 - dy_)], WOODT), ([(x1, y0), (x1 + dx, y0 - dy_), (x1 + dx, y1 - dy_), (x1, y1)], WOODS), ([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], WOODF)):
        poly(d, pts, col)
def furniture(dy):
    lay = layer(); d = ImageDraw.Draw(lay)
    # 끈: 왼쪽 그림 밖 → (벽돌집 · 눈알 앞 바닥) → 왼쪽 단 → 깔개 넷 밑 → 오른쪽 단 → 뒤 담 밑으로
    rope(d, [(-20, 452 + dy), (70, 452 + dy), (128, 448 + dy), (156, 432 + dy), (172, 408 + dy), (190, YR + 1 + dy)])
    rope(d, [(336, YR - 2 + dy), (PC + 8, YR + dy)], smooth=False)
    rope(d, [(PC + 150, YR - 4 + dy), (PC + 170, YR - 14 + dy), (PC + 176, YR - 52 + dy), (PC + 174, YR - 152 + dy), (PC + 166, YR - 252 + dy), (PC + 160, YR - 300 + dy)])
    # 타탄 깔개 넷(프로모터) — 끈이 그 밑을 지난다
    for x0 in X0S:
        p0, p1, p2, p3 = (x0 + 6, 426 + dy), (x0 + 166, 426 + dy), (x0 + 184, 356 + dy), (x0 + 24, 356 + dy)
        d.polygon(T([p0, p1, p2, p3]), fill=(186, 50, 48, 255))
        for t in (0.25, 0.5, 0.75):
            d.line(T([(p0[0] + (p1[0] - p0[0]) * t, p0[1]), (p3[0] + (p2[0] - p3[0]) * t, p3[1])]), fill=(46, 112, 72, 255), width=int(5 * S))
        for t in (0.34, 0.68):
            d.line(T([(p0[0] + (p3[0] - p0[0]) * t, p0[1] + (p3[1] - p0[1]) * t), (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)]), fill=(52, 72, 150, 255), width=int(5 * S))
        poly(d, [p0, p1, p2, p3], None)
    # 응원 단 둘(인핸서) + 앞면 동그라미 둘씩(왼쪽 단 = 초록 · 오른쪽 단 = 보라)
    for x0, col in ((PA, GRN), (PC, PUR)):
        box3(d, x0, 363 + dy, x0 + 150, 421 + dy)
        for cx in (x0 + 50, x0 + 100): d.ellipse([(cx - 13) * S, (YR - 13 + dy) * S, (cx + 13) * S, (YR + 13 + dy) * S], fill=col, outline=INK, width=int(2.2 * S))
    # 그림 팻말 넷(깔개 뒤 기둥)
    for x0, icon in zip(X0S, ICONS):
        cx = x0 + 104
        d.rectangle([(cx - 5) * S, (198 + dy) * S, (cx + 5) * S, (358 + dy) * S], fill=(176, 128, 84, 255), outline=INK, width=int(2.2 * S))
        d.rounded_rectangle([(cx - 60) * S, (108 + dy) * S, (cx + 60) * S, (202 + dy) * S], radius=7 * S, fill=(252, 248, 236, 255), outline=INK, width=int(3.2 * S))
        icon(d, cx, 155 + dy, 74)
    put(lay, rows=(96 + dy, 96 + dy + 440))                                        # 담 띠 위로는 그리지 않는다(끈이 담 밑으로 들어간다)
def machine(k, dy):
    """k 번째 자리에 인쇄 기계 + 팻말과 같은 그림의 종이띠."""
    x0 = X0S[k]
    lay = layer(); d = ImageDraw.Draw(lay)
    poly(d, [(x0 + 60, 398 + dy), (x0 + 132, 398 + dy), (x0 + 190, 518 + dy), (x0 + 98, 518 + dy)], (254, 254, 252, 255), 3)
    ICONS[k](d, x0 + 134, 472 + dy, 50)
    put(lay)
    stick(SP_PRESS, 166 / SP_PRESS.width, x0 + 97, 421 + dy)

furniture(0); furniture(DY)
for k in (0, 1): machine(k, 0)                                                     # 위 마당(간): 앨범 · 청소기
for k in (1, 3): machine(k, DY)                                                    # 아래 마당(수정체): 청소기 · 수정 구슬
stick(SP_HOUSE, 232 / SP_HOUSE.height, 82, 426)                                    # 위 마당 왼쪽 끝의 붉은 벽돌집(간)
stick(SP_GRN, 214 / SP_GRN.height, PA + 87, 356)                                   # 초록 응원단 → 위 마당 왼쪽 단
stick(SP_PUR, 214 / SP_PUR.height, PC + 87, 356 + DY)                              # 보라 응원단 → 아래 마당 오른쪽 단

# ── 담장 밖: 화살 · 끈 타래
def arrow(d, pts, col, w=9, head=24, dash=None):
    q = resample(spline(pts)); (x0, y0), (x1, y1) = q[-8], q[-1]; an = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + head * 0.55 * math.cos(an), y1 + head * 0.55 * math.sin(an))
    hp = [tip, (x1 - head * 0.5 * math.cos(an) + head * 0.62 * math.sin(an), y1 - head * 0.5 * math.sin(an) - head * 0.62 * math.cos(an)), (x1 - head * 0.5 * math.cos(an) - head * 0.62 * math.sin(an), y1 - head * 0.5 * math.sin(an) + head * 0.62 * math.cos(an))]
    for r, c in (((w + 5) / 2, INK), (w / 2, col)):
        for i, (x, y) in enumerate(q[:-6]):
            if dash and (i // dash) % 2: continue
            d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    poly(d, hp, col, 2.6)
lay = layer(); d = ImageDraw.Draw(lay)
AG = (72, 172, 92, 255)
# 배 아기에서 화살 둘 — 든 왼손에서 위 마당 안으로 · 배의 왼쪽 아래 옆구리에서 아래 마당 안으로(한 곳에서 내면 양끝 화살 하나로 읽혔다 · 일치 검사 2회)
arrow(d, [(1456, 536), (1436, 512), (1410, 490), (1372, 472)], AG)
arrow(d, [(1452, 724), (1436, 752), (1410, 784), (1372, 806)], AG)
arrow(d, [(1672, 1004), (1720, 1000), (1760, 1004), (1794, 1012)], AG, w=9, head=24)  # 뼈 속 아주머니 → (뼈 밖의) 붉은 원반 · 흰 옷 경비 — 하나뿐
# 달걀 구멍 위의 끈 타래(네 겹 · 끝이 구멍으로 늘어진다) + 위 마당의 끈 끝에서 온 점선 화살
CX, CY = 1528, 150
rope(d, [(CX + 30, CY + 20), (CX + 40, CY + 34), (CX + 44, CY + 52), (CX + 44, CY + 62)])        # 구멍으로 늘어진 끝
for k in range(4):
    cy = CY + 18 - k * 11
    rope(d, [(CX + 36 * math.cos(t), cy + 12 * math.sin(t)) for t in np.linspace(0.6, 0.6 + 2 * math.pi, 70)], smooth=False)
arrow(d, [(1354, 124), (1394, 112), (1436, 120), (1470, 140)], (150, 120, 84, 255), w=5, head=18, dash=7)   # 담 밑으로 드는 끈의 끝머리에서 끈 타래로
put(lay)
# 떠낸 노른자 밑에 흰자 웅덩이 — 노른자만 놓였을 때는 「오렌지」로 읽혔다(일치 검사 3회). 바닥(과 그림자)인 곳에만 그려 노른자 밑으로 깔리게 한다.
arr = np.array(im).astype(int); R_, G_, B_ = arr[..., 0], arr[..., 1], arr[..., 2]
gm = (np.abs(arr - GND).max(axis=2) <= 14) | ((R_ >= 160) & (R_ <= 236) & (np.abs(R_ - G_) <= 12) & (R_ - B_ >= 10) & (R_ - B_ <= 50))
lay = layer(); d = ImageDraw.Draw(lay)
blob = [(1470 + 60 * (1 + 0.10 * math.sin(3 * t + 0.6)) * math.cos(t), 444 + 25 * (1 + 0.16 * math.cos(2 * t + 0.3)) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 80, endpoint=False)]
poly(d, blob, (253, 253, 250, 255), 2.6)
small = lay.resize((W, H), Image.LANCZOS); al = np.asarray(small.split()[3]).astype(np.float32) * gm; small.putalpha(Image.fromarray(al.astype(np.uint8)))
base = im.convert('RGBA'); base.alpha_composite(small); im = base.convert('RGB')
# 흰 옷 경비의 모자 · 가슴 배지(L46e 의 흰 옷 경비와 같게 — 배지가 없으면 「요리사 · 제빵사」로 읽혔다)
lay = layer(); d = ImageDraw.Draw(lay)
for bx, by, r in ((1991, 916, 5.2), (2003, 992, 6.2)):
    d.ellipse([(bx - r) * S, (by - r) * S, (bx + r) * S, (by + r) * S], fill=(236, 238, 244, 255), outline=INK, width=int(1.5 * S))
    d.ellipse([(bx - r * 0.45) * S, (by - r * 0.45) * S, (bx + r * 0.45) * S, (by + r * 0.45) * S], outline=(120, 128, 142, 255), width=int(1.2 * S))
put(lay)
im.save(dst)
print('ok', dst)

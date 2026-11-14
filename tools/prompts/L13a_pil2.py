#!/usr/bin/env python3
# L13a_pil2.py <base.png> <out.png> — L13a 다시 짓기 「성벽이 뚫린 첫 순간」의 PIL 마무리(2026-11-14 · 사건 장면).
#  바탕 = Gemini 가 통째로 그린 장면 S1(1024 → 2048) + 구역 편집 A1 ~ A4(L13a_build2.sh).
#  여기서는 「개수 · 자리 · 빛깔 · 그림 속 그림이 곧 뜻」인 것만: 붉은 리본 배지(자기 — 성 안의 모두) · 조끼 단추(넷씩 두 줄 = CD8 · 한 줄 넷 = CD4)
#  · 수배 전단 석 장의 그림(꼬리 = 플라젤린 · 꽃 금지 + 금빛 밧줄 = 비메틸화 CpG DNA · 묶은 두루마리 둘 = dsRNA) · 잠옷 병정 종이의 세균 한 놈 얼굴(특이)
#  · 두루마리 끈의 빨강 → 갈색(빨간 리본 = 건넴 예약) · 인터폰 숫자판의 점 지우기(둥근 점은 단추로 센다) · 털모자의 금빛 턱끈(털 뭉치가 모자로 읽히게).
import sys, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s13_lib
from s13_lib import S, INK, poly, line, disc, badge, RED, RED_D, GOLD_C, unred

W, H = 2048, 1144
src, dst = sys.argv[1:3]
im = Image.open(src).convert('RGB')
assert im.size == (W, H), im.size

def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay):
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    b = im.convert('RGBA'); b.alpha_composite(small); im = b.convert('RGB')

# ── ⓪ 지우기 · 빛깔 손질
a = np.array(im)[:, :, ::-1].copy()
m = np.zeros(a.shape[:2], np.uint8)
for x, y in ((1801, 480), (1801, 492), (1801, 505), (1925, 480), (1925, 493), (1925, 506)):   # 발코니 병정 조끼의 회색 점(Gemini) — 지우고 금빛 단추를 센다
    cv2.circle(m, (x, y), 5, 255, -1)
a = cv2.inpaint(a, m, 5, cv2.INPAINT_TELEA)
# 인터폰 숫자판 · 아래 둥근 단추 → 민 판(둥근 점은 단추로 센다 — L13a ⑥)
face = a[880:934, 1486:1517].reshape(-1, 3); br = face.mean(axis=1)
col = np.median(face[(br > 110) & (br < 210)], axis=0).astype(np.uint8)
a[880:934, 1486:1517] = col
im = Image.fromarray(a[:, :, ::-1])
c = np.array(im).astype(int)                                                    # 두루마리 끈 빨강 → 갈색(테두리의 옅은 빨강까지 — unred 의 문턱은 높다)
x0, y0, x1, y1 = 318, 544, 366, 616
r_ = c[y0:y1, x0:x1]; R_, G_, B_ = r_[..., 0], r_[..., 1], r_[..., 2]
mk = (R_ - np.maximum(G_, B_) > 18)                                              # 어두운 테두리(R 37 · G 0 · B 16)까지
lum = R_[mk] * 0.5 + np.maximum(G_[mk], B_[mk]) * 0.5
r_[mk] = np.stack([np.minimum(255, lum * 1.15 + 18), lum * 0.80 + 8, lum * 0.52], axis=1).astype(int)
im = Image.fromarray(c.astype(np.uint8))

# ── ① 수배 전단 석 장 + 잠옷 병정 종이의 한 놈 얼굴
GREEN, GREEN_D = (110, 196, 80, 255), (62, 140, 52, 255)
GOLD, GOLD_D = (242, 196, 64, 255), (196, 146, 30, 255)
def bez(p0, c0, c1, p1, n=24):
    out = []
    for k in range(n + 1):
        t = k / n; u = 1 - t
        out.append(tuple(u ** 3 * p0[i] + 3 * u * u * t * c0[i] + 3 * u * t * t * c1[i] + t ** 3 * p1[i] for i in (0, 1)))
    return out
def capsule(cx, cy, w, h, n=40):
    r = w / 2; pts = []
    for k in range(n // 2 + 1):
        t = math.pi * k / (n // 2); pts.append((cx + r * math.cos(t), cy - (h / 2 - r) - r * math.sin(t)))
    for k in range(n // 2 + 1):
        t = math.pi + math.pi * k / (n // 2); pts.append((cx + r * math.cos(t), cy + (h / 2 - r) - r * math.sin(t)))
    return pts
lay = layer(); d = ImageDraw.Draw(lay)
# (가) 톨게이트 게시판 — 점선 알약(얼굴 없음) + 굵은 초록 물결 꼬리 = 침입자 무리가 두루 단 꼬리(플라젤린)
P = capsule(849, 440, 19, 30, 80); P = P + [P[0]]                               # (압정 밑으로 내림 — 2회: 압정과 겹쳐 「핀 달린 달걀 고리」)                               # 닫힌 알약 둘레를 고른 점선으로(일치 검사 1회: 오른쪽이 열린 가는 선 = 「청진기」)
seg = [math.dist(P[k], P[k + 1]) for k in range(len(P) - 1)]; L_ = sum(seg)
def at(sv):
    acc = 0
    for k, sl in enumerate(seg):
        if acc + sl >= sv: t = (sv - acc) / sl if sl else 0; return (P[k][0] + (P[k + 1][0] - P[k][0]) * t, P[k][1] + (P[k + 1][1] - P[k][1]) * t)
        acc += sl
    return P[-1]
nd = 16
for j in range(nd):
    s0 = L_ * j / nd; line(d, [at(s0 + L_ / nd * q / 4) for q in range(3)], 2.0, (40, 40, 44, 255))
tail = bez((849, 455), (840, 462), (860, 469), (850, 477))
line(d, tail, 6.4); line(d, tail, 3.6, GREEN)
# (나) 자루 곁 게시판 왼쪽 장 — 금빛 꼰 밧줄 토막 + 금지 표지로 지운 분홍 꽃(꽃 = 메틸 도장이 없다)
r0 = bez((783, 945), (786, 933), (790, 919), (796, 906), 11)                   # (압정 밑에서 시작 — 압정과 겹치지 않게)                   # 꼰 밧줄 = 비스듬한 타원 마디를 이어 붙임(평행선 둘은 「막대 둘」로 읽힌다)
line(d, r0, 7.4)
for k in range(len(r0) - 1):
    (xa, ya), (xb, yb) = r0[k], r0[k + 1]; mx, my = (xa + xb) / 2, (ya + yb) / 2
    ang = math.degrees(math.atan2(yb - ya, xb - xa)) + 55
    pts = [(mx + 3.6 * math.cos(math.radians(ang)) * math.cos(t) - 2.0 * math.sin(math.radians(ang)) * math.sin(t),
            my + 3.6 * math.sin(math.radians(ang)) * math.cos(t) + 2.0 * math.cos(math.radians(ang)) * math.sin(t)) for t in [2 * math.pi * j / 16 for j in range(16)]]
    poly(d, pts, GOLD, 1.0)
for (x, y), sgn in ((r0[0], 1), (r0[-1], -1)):                                  # 풀린 끝 올
    for a_ in (-30, 0, 30):
        t = math.radians(a_ + (115 if sgn > 0 else -65)); line(d, [(x, y), (x + 5 * math.cos(t), y + 5 * math.sin(t))], 1.2, GOLD_D)
fx, fy = 812, 925                                                                 # 꽃을 키움(2회: 「분홍 덩이」) — 꽃잎 다섯 · 노란 가운데 · 줄기와 잎
line(d, [(fx, fy + 4), (fx + 1, fy + 11)], 1.6, (70, 150, 60, 255))
for k in range(5):
    t = 2 * math.pi * k / 5 - math.pi / 2; disc(d, fx + 4.6 * math.cos(t), fy + 4.6 * math.sin(t), 3.4, (246, 150, 196, 255), 1.0)
disc(d, fx, fy, 2.4, (250, 214, 70, 255), 0.9)
d.ellipse([(fx - 12.5) * S, (fy - 12.5) * S, (fx + 12.5) * S, (fy + 12.5) * S], outline=(214, 40, 40, 255), width=int(3.0 * S))
line(d, [(fx - 9, fy - 9), (fx + 9, fy + 9)], 3.4, (214, 40, 40, 255))          # 금지 사선(1회: 사선이 흐려 금지로 안 읽힘 → 굵게)
# (다) 자루 곁 게시판 오른쪽 장 — 갈색 끈으로 한데 묶은 흰 두루마리 둘(두 겹 = 이중가닥 RNA) · 양 끝이 말린 종이(3회: 「관 두 개」로 읽힘 → 끝의 말림을 크게)
for cy_ in (877, 893):
    poly(d, [(845, cy_ - 5.5), (880, cy_ - 5.5), (880, cy_ + 5.5), (845, cy_ + 5.5)], (255, 255, 252, 255), 1.6)
    for cx_, sg in ((845, -1), (880, 1)):                                            # 끝마다 말린 종이 — 바깥 테 + 안으로 감기는 소용돌이
        d.ellipse([(cx_ - 4.2) * S, (cy_ - 5.5) * S, (cx_ + 4.2) * S, (cy_ + 5.5) * S], fill=(246, 244, 236, 255), outline=INK[:3] + (255,), width=int(1.4 * S))
        sp = [(cx_ + sg * 0.3 + 3.2 * (1 - t / 10.5) * math.cos(t), cy_ + 4.2 * (1 - t / 10.5) * math.sin(t)) for t in [j * 0.45 for j in range(22)]]
        line(d, sp, 1.0)
line(d, [(862, 869), (862, 901)], 2.8, (140, 92, 52, 255))
line(d, [(862, 901), (858, 907)], 1.8, (140, 92, 52, 255)); line(d, [(862, 901), (866, 907)], 1.8, (140, 92, 52, 255))   # 매듭 끝
# (라) 잠옷 병정의 종이 — 세균 한 놈의 얼굴(특이 — 그놈만 쫓는다)
gx, gy = 1803, 864
poly(d, capsule(gx, gy, 16, 26), GREEN, 1.6)
line(d, [(gx - 5, gy - 6), (gx - 1.5, gy - 4)], 1.3); line(d, [(gx + 5, gy - 6), (gx + 1.5, gy - 4)], 1.3)
disc(d, gx - 3, gy - 2, 1.0, INK, 0); disc(d, gx + 3, gy - 2, 1.0, INK, 0)
line(d, [(gx - 3, gy + 4), (gx, gy + 2.5), (gx + 3, gy + 4)], 1.2)
put(lay)

# ── ①' 흰 덩이 입으로 빨려 드는 바람 줄(2회: 세균을 삼키는지 뱉는지 애매) — 입 왼쪽 밖에서 입 안쪽으로 휘어 드는 줄 셋 + 끝의 작은 화살촉
lay = layer(); d = ImageDraw.Draw(lay)
for P0, C0, C1, P1 in (((1150, 522), (1185, 530), (1215, 544), (1242, 556)), ((1144, 570), (1180, 572), (1212, 574), (1242, 576)), ((1150, 620), (1186, 612), (1216, 602), (1242, 596))):
    pts = bez(P0, C0, C1, P1, 16); line(d, pts, 2.4)
    (xa, ya), (xb, yb) = pts[-3], pts[-1]; ang = math.atan2(yb - ya, xb - xa)
    for da in (2.6, -2.6):
        line(d, [(xb, yb), (xb + 7 * math.cos(ang + da), yb + 7 * math.sin(ang + da))], 2.2)
put(lay)

# ── ② 털모자의 금빛 턱끈(털 뭉치가 장난감 병정 모자로 읽히게 — 점이 아니라 이어진 띠: L13c ㉞)
lay = layer(); d = ImageDraw.Draw(lay)
strap = [((1 - q) ** 2 * 1714 + 2 * (1 - q) * q * 1741 + q * q * 1769, (1 - q) ** 2 * 1022 + 2 * (1 - q) * q * 1058 + q * q * 1022) for q in [k / 20 for k in range(21)]]
line(d, strap, 6.0); line(d, strap, 3.4, (246, 196, 60, 255))
put(lay)

# ── ③ 조끼 단추: 발코니 왼쪽 병정 = 넷씩 두 줄(CD8 · 세포독성) · 오른쪽 병정 = 한 줄 넷(CD4 · 조력)
BTN = (242, 190, 52, 255)
def colm(d, x, y0, y1, r, n=4):
    for k in range(n): disc(d, x, y0 + (y1 - y0) * k / (n - 1), r, BTN, max(1.2, r * 0.32))
lay = layer(); d = ImageDraw.Draw(lay)
colm(d, 1795, 463, 508, 3.6); colm(d, 1810, 463, 508, 3.6)
colm(d, 1925, 463, 508, 3.8)
put(lay)

# ── ④ 붉은 리본 배지 = 자기 — 성 안의 모두(침입자 = 세균 넷 · 보라 망토에게만 없다)
def badge_c(d, cx, cy, r):
    for sx in (-1, 1):
        d.polygon([((cx + sx * 0.15 * r) * S, (cy + 0.5 * r) * S), ((cx + sx * 0.95 * r) * S, (cy + 0.55 * r) * S), ((cx + sx * 0.7 * r) * S, (cy + 1.75 * r) * S)], fill=RED_D)
    disc(d, cx, cy, r, RED, max(1.2, r * 0.2))
    d.ellipse([(cx - 0.4 * r) * S, (cy - 0.4 * r) * S, (cx + 0.4 * r) * S, (cy + 0.4 * r) * S], fill=GOLD_C)
lay = layer(); d = ImageDraw.Draw(lay)
for cx, cy, r in ((720, 468, 7.5), (1156, 132, 6.5), (1058, 530, 8), (1236, 640, 8.5),       # 초소 경비 · 봉화 경비 · 파리채 경비 · 흰 덩이
                  (318, 795, 7.5), (636, 961, 6), (1067, 846, 7.5), (1340, 928, 8),            # 보 경비 · 자루 속 경비 · 궁수 · 인터폰 주민
                  (1628, 478, 6.5), (1810, 380, 7), (1935, 380, 7), (1868, 935, 7.5)):        # 발코니 벌 · 병정 둘(털모자 앞 — 조끼는 단추 자리) · 잠옷 병정
    (badge if r >= 7 else badge_c)(d, cx, cy, r)
put(lay)

im.save(dst)
print('saved', dst)

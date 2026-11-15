#!/usr/bin/env python3
# L13e_pil.py <base.png> <out.png> — L13e 「무기고의 깃발 맞추기」의 PIL 마무리(2026-11-15).
#  바탕 = Gemini 가 통째로 그린 장면 S1(1024 → 2048) + 구역 편집 Z1 · Z2b · Z3b(Z3c) · Z4(L13e_build.sh).
#  여기서는 「개수 · 자리 · 빛깔이 곧 뜻」인 것만: Gemini 가 넣은 글자(「Z.」)와 조끼의 회색 점 지우기 · 조끼 단추(한 줄 넷 = CD4)
#  · 붉은 리본 배지(자기 — 성 안의 벌 · 병정. 세균 둘 · 반은 게인 괴물에는 없다).
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s13_lib import S, disc, badge, RED, RED_D, GOLD_C

W, H = 2048, 1144
src, dst = sys.argv[1:3]
im = Image.open(src).convert('RGB')
assert im.size == (W, H), im.size

def layer(): return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
def put(lay):
    global im
    small = lay.resize((W, H), Image.LANCZOS)
    b = im.convert('RGBA'); b.alpha_composite(small); im = b.convert('RGB')

# ── ⓪ 지우기: 윗칸 침대 곁 벽의 「Z.」(잠 — 글자) · 병정 조끼에 Gemini 가 몰래 찍은 회색 점 셋
a = np.array(im)[:, :, ::-1].copy(); m = np.zeros(a.shape[:2], np.uint8)
cv2.rectangle(m, (1283, 302), (1320, 326), 255, -1)
for x, y in ((1190, 595), (1190, 610), (1190, 625)):
    cv2.circle(m, (x, y), 5, 255, -1)
a = cv2.inpaint(a, m, 5, cv2.INPAINT_TELEA)
im = Image.fromarray(a[:, :, ::-1])

# ── ① 조끼 단추: 한 줄 넷 = CD4(도움 T — 무기고에서 B 곁에 선 T)
GOLD = (242, 190, 52, 255)
lay = layer(); d = ImageDraw.Draw(lay)
for k in range(4):
    disc(d, 1190, 586 + 16 * k, 4.0, GOLD, 1.3)
put(lay)

# ── ② 붉은 리본 배지 — 자기(MHC I): 성 안의 벌 · 병정 모두(몸이 보이는 것만). 세균 · 반은 게인 괴물(실험실에서 만든 융합세포)은 없다
def badge_c(d, cx, cy, r):
    """작은 배지(r < 7): 꼬리를 테두리 없는 세모 둘로(L13d 그대로 — 작은 꼬리선이 글자로 읽혔다)."""
    for sx in (-1, 1):
        d.polygon([((cx + sx * 0.15 * r) * S, (cy + 0.5 * r) * S), ((cx + sx * 0.95 * r) * S, (cy + 0.55 * r) * S), ((cx + sx * 0.7 * r) * S, (cy + 1.75 * r) * S)], fill=RED_D)
    disc(d, cx, cy, r, RED, max(1.2, r * 0.2))
    d.ellipse([(cx - 0.4 * r) * S, (cy - 0.4 * r) * S, (cx + 0.4 * r) * S, (cy + 0.4 * r) * S], fill=GOLD_C)
def put_badge(d, cx, cy, r): (badge if r >= 7 else badge_c)(d, cx, cy, r)
BADGES = (
    (1222, 588, 7.5),                                   # 외눈 안경 병정(조끼 오른쪽 — 단추 줄과 떼어)
    (383, 647, 7.5),                                    # 슬롯머신 둘을 당기는 벌
    (812, 470, 7), (665, 530, 7), (730, 615, 6.5), (665, 725, 7), (795, 705, 7),   # 세균에 깃발을 대는 벌 다섯
    (835, 965, 7), (795, 955, 6),                       # 빛 동그라미 — 불어난 똑같은 벌(몸이 보이는 둘)
    (1207, 960, 7),                                     # 깃발 끝을 줄로 가는 벌
    (1469, 877, 7), (1800, 869, 7), (1792, 1031, 7),    # 호스 구멍에 깃발을 넣는 둘 · 쓰러진 하나
    (1375, 342, 6), (1555, 380, 6.5),                   # 윗칸 침대의 수염 벌 둘
    (1510, 590, 5.5), (1557, 572, 5.5),                 # 아랫칸 — 책 읽는 벌 · 깃발을 던지는 벌
)
lay = layer(); d = ImageDraw.Draw(lay)
for cx, cy, r in BADGES: put_badge(d, cx, cy, r)
put(lay)

im.save(dst)
print('saved', dst)

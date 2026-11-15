#!/usr/bin/env python3
# L10a_pil.py <in.png> <out.png> — L10a 덧붙임(2026-11-15 · 17장 · 지시서 차례 6)의 PIL 몫.
#  ① 스캐닝 점선: 겨자색 중산모(5′ 캡)에서 왼쪽 정거장 밑 작은 상자까지 레일 위를 따라온 점선 + 끝의 화살촉(오른쪽 = 3′ 쪽)
#     — 작은 소단위체가 캡에 붙은 뒤 레일을 훑어 왔다(새 정거장 s13 · 코사크 춤꾼 앞에서 멈춤).
#  ② GTP 칩: 덱의 【짙은 회색 네모 칩】 = GTP. 금이 간 칩 = 쓴 GTP(쪼개진 동전 = 쓴 ATP 와 같은 말버릇 · 네모 ↔ 동그라미).
#     정거장 앞 바닥에 — 왼쪽(개시) 하나 · 가운데(신장 — 코돈 인식 · 자리옮김) 둘 · 오른쪽(종결 뒤 해리) 둘. 수는 PIL 로 세어 그린다.
import sys, math
from PIL import Image, ImageDraw

INK = (28, 24, 22)
DASH = dict(y=881, x0=176, x1=246, seg=10, gap=7, w=5)
HEAD = (258, 881)                                   # 화살촉 끝(오른쪽)
CHIP = 34                                           # 칩 한 변
CHIPS = [(380, 1048, -8),                           # 왼쪽 정거장(개시 · 하나)
         (1002, 1048, 6), (1052, 1052, -10),        # 가운데 정거장(신장 · 둘)
         (1708, 1048, 9), (1758, 1052, -6)]         # 오른쪽 정거장(해리 · 둘)

def dashes(img):
    K = 6; x0, x1, y = DASH['x0'] - 10, HEAD[0] + 10, DASH['y']
    box = (x0, y - 16, x1, y + 16)
    big = img.crop(box).resize(((box[2] - box[0]) * K, (box[3] - box[1]) * K), Image.LANCZOS); d = ImageDraw.Draw(big)
    X = lambda v: (v - box[0]) * K; Y = lambda v: (v - box[1]) * K
    x = DASH['x0']
    while x < DASH['x1']:
        xe = min(x + DASH['seg'], DASH['x1'])
        d.rounded_rectangle([X(x), Y(y) - DASH['w'] * K / 2, X(xe), Y(y) + DASH['w'] * K / 2], radius=DASH['w'] * K / 2, fill=INK)
        x = xe + DASH['gap']
    hx, hy = HEAD; L, hw = 14, 8
    d.polygon([(X(hx), Y(hy)), (X(hx - L), Y(hy - hw)), (X(hx - L), Y(hy + hw))], fill=INK)
    img.paste(big.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS), box[:2])

def chip(img, cx, cy, ang):
    K = 8; R = CHIP * 0.75 + 6
    box = (int(cx - R), int(cy - R), int(cx + R), int(cy + R)); S = box[2] - box[0]
    big = img.crop(box).resize((S * K, S * K), Image.LANCZOS); d = ImageDraw.Draw(big)
    c = (cx - box[0]) * K, (cy - box[1]) * K; h = CHIP / 2 * K; a = math.radians(ang)
    rot = lambda px, py: (c[0] + px * math.cos(a) - py * math.sin(a), c[1] + px * math.sin(a) + py * math.cos(a))
    sq = lambda s: [rot(-s, -s), rot(s, -s), rot(s, s), rot(-s, s)]
    d.polygon([(x, y + 3 * K) for x, y in sq(h)], fill=(196, 190, 168))                    # 바닥 그림자
    d.polygon(sq(h + 2.2 * K), fill=INK)                                                    # 먹 테
    d.polygon(sq(h), fill=(92, 92, 98))                                                     # 짙은 회색
    d.polygon([rot(-h, -h), rot(h, -h), rot(h * 0.55, -h * 0.55), rot(-h * 0.55, -h * 0.55)], fill=(132, 132, 140))   # 윗면 빛
    crack = [(-h * 0.95, -h * 0.25), (-h * 0.35, -h * 0.05), (-h * 0.1, -h * 0.45), (h * 0.3, -h * 0.1), (h * 0.95, h * 0.2)]
    d.line([rot(x, y) for x, y in crack], fill=INK, width=int(2.4 * K), joint='curve')       # 금(쓴 칩)
    img.paste(big.resize((S, S), Image.LANCZOS), box[:2])

def main(src, out):
    img = Image.open(src).convert('RGB')
    dashes(img)
    for cx, cy, ang in CHIPS: chip(img, cx, cy, ang)
    img.save(out); print('→', out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

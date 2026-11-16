#!/usr/bin/env python3
# L12a_pil.py <in.png> <out.png> — L12a 덧붙임(2026-11-16 · 42장 · 지시서 차례 7)의 PIL 몫.
#  새 정거장 s14 = 펩시노겐 활성화 사슬(구역 편집 AB2 — 흙 항아리 물줄기를 맞은 첫 병이 검게 · 검은 병이 닿은 이웃 병이 노란 불꽃과 함께 검게).
#  병이 검어지는 순간 마개가 튀어 날아간다 = 활성 부위를 덮던 조각이 떨어져 활성 부위가 드러난다(G1-88).
#   ① 물줄기 밑 첫 병의 목에서 오른쪽 위로 튀는 빨간 왕관 마개
#   ② 노란 불꽃 자리 — 반쯤 검어진 병의 목에서 아래 왼쪽(사슬과 직각)으로 튀는 빨간 왕관 마개
#   마개 뒤에는 병목 쪽으로 짧은 움직임 줄 둘.
import sys, math
from PIL import Image, ImageDraw

INK = (28, 26, 24)
RED, RED_D, RED_L = (214, 44, 38), (150, 26, 24), (240, 120, 100)
CAPS = [  # (cx, cy, 반지름, 기울기°, 날아온 쪽 단위벡터(병목 쪽))
    (586, 612, 12, -28, (-0.93, -0.36)),
    (678, 870, 11, 24, (0.62, -0.78)),
]

def cap(img, cx, cy, r, ang, back):
    K = 8; R = r * 3.2
    box = (int(cx - R), int(cy - R), int(cx + R), int(cy + R)); S = box[2] - box[0]
    big = img.crop(box).resize((S * K, S * K), Image.LANCZOS); d = ImageDraw.Draw(big)
    c = ((cx - box[0]) * K, (cy - box[1]) * K); a = math.radians(ang)
    rot = lambda px, py: (c[0] + (px * math.cos(a) - py * math.sin(a)) * K, c[1] + (px * math.sin(a) + py * math.cos(a)) * K)
    # 움직임 줄 둘(병목 쪽 · 마개 뒤)
    bx, by = back; nx, ny = -by, bx
    for off, L in ((-0.5, 0.95), (0.5, 0.7)):
        p0 = (cx + bx * r * 1.3 + nx * r * off, cy + by * r * 1.3 + ny * r * off)
        p1 = (p0[0] + bx * r * L, p0[1] + by * r * L)
        d.line([((p0[0] - box[0]) * K, (p0[1] - box[1]) * K), ((p1[0] - box[0]) * K, (p1[1] - box[1]) * K)], fill=INK, width=int(2.2 * K))
        for p in (p0, p1):
            q = ((p[0] - box[0]) * K, (p[1] - box[1]) * K); w = 1.1 * K
            d.ellipse([q[0] - w, q[1] - w, q[0] + w, q[1] + w], fill=INK)
    # 왕관 마개 — 옆 띠(주름 진 치마) + 윗면(납작한 타원)
    sk = []
    n = 14
    for i in range(n + 1):
        t = math.pi * i / n
        x = -r * math.cos(t)
        yb = r * 0.38 + (r * 0.32 if i % 2 else r * 0.16)
        sk.append(rot(x, yb))
    top_l, top_r = rot(-r, 0), rot(r, 0)
    poly = [top_l] + sk + [top_r]
    d.polygon(poly, fill=RED_D, outline=INK, width=int(2.0 * K))
    d.polygon([rot(r * math.cos(t), r * 0.42 * math.sin(t)) for t in [2 * math.pi * k / 48 for k in range(48)]], fill=INK)
    d.polygon([rot(r * 0.86 * math.cos(t), r * 0.30 * math.sin(t)) for t in [2 * math.pi * k / 48 for k in range(48)]], fill=RED)
    d.polygon([rot(-r * 0.45 + r * 0.30 * math.cos(t), -r * 0.08 + r * 0.09 * math.sin(t)) for t in [2 * math.pi * k / 24 for k in range(24)]], fill=RED_L)
    img.paste(big.resize((S, S), Image.LANCZOS), box[:2])

def main(src, out):
    img = Image.open(src).convert('RGB')
    for cx, cy, r, ang, back in CAPS: cap(img, cx, cy, r, ang, back)
    img.save(out); print('→', out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

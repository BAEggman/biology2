#!/usr/bin/env python3
# discs.py in out — L14b 망원경 두 끝: 왼쪽 냅킨 고리 면 = 9×3(삼중관 아홉 · 가운데 빔) · 오른쪽 털 대롱 끝 = 9+2(이중관 아홉 + 가운데 둘 · 다이닌 팔 = 작은 다이아몬드)
import sys, math
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
S = 6
im = Image.open(src).convert('RGB')
INK = (24, 22, 20)
def work(box, fn):
    x0, y0, x1, y1 = box
    reg = im.crop(box).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS)
    d = ImageDraw.Draw(reg)
    T = lambda p: ((p[0] - x0) * S, (p[1] - y0) * S)
    fn(d, T)
    reg = reg.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    im.paste(reg, (x0, y0))
def circ(d, T, c, r, fill, w=1.3):
    cx, cy = T(c); R = r * S
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=fill, outline=INK, width=max(1, int(w * S)))
# 1) 9×3 — 냅킨 고리 면(고리 띠 위에 삼중관 아홉 · 가운데 구멍은 그대로)
CX, CY, RX, RY = 482.5, 866.0, 47.0, 43.5      # 고리 바깥 타원
HX, HY, HRX, HRY = 486.0, 865.0, 25.0, 26.0    # 구멍
def nine_three(d, T):
    for k in range(9):
        th = math.radians(90 + k * 40)
        # 띠 가운데(바깥 · 구멍 사이)
        ox, oy = CX + RX * math.cos(th), CY - RY * math.sin(th)
        ix, iy = HX + HRX * math.cos(th), HY - HRY * math.sin(th)
        mx, my = (ox + ix) / 2, (oy + iy) / 2
        # 삼중관 방향: 접선에서 안쪽으로 30° 기운 바람개비
        ph = th + math.radians(90 - 32)
        ux, uy = math.cos(ph), -math.sin(ph)
        for j in (-1, 0, 1):
            circ(d, T, (mx + j * 5.6 * ux, my + j * 5.6 * uy), 3.1, (236, 242, 226), 1.1)
            cx, cy = T((mx + j * 5.6 * ux, my + j * 5.6 * uy)); rr = 0.9 * S
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(150, 168, 120))
work((425, 812, 540, 920), nine_three)
# 2) 9+2 — 털 대롱 끝(크림 원판)
GX, GY, GRX, GRY = 657.5, 885.0, 42.0, 45.5
def nine_two(d, T):
    # 가운데 둘
    for j in (-1, 1):
        circ(d, T, (GX + j * 5.2, GY), 4.0, (246, 244, 232), 1.2)
    # 가운데를 싼 옅은 고리(중심 집) — 얇게
    cx, cy = T((GX, GY)); d.ellipse([cx - 13 * S, cy - 11 * S, cx + 13 * S, cy + 11 * S], outline=(150, 140, 120), width=int(0.8 * S))
    for k in range(9):
        th = math.radians(90 + k * 40)
        r = 0.70
        mx, my = GX + GRX * r * math.cos(th), GY - GRY * r * math.sin(th)
        ph = th + math.radians(90)          # 접선
        ux, uy = math.cos(ph), -math.sin(ph)
        a = (mx - 3.2 * ux, my - 3.2 * uy); b = (mx + 3.2 * ux, my + 3.2 * uy)
        circ(d, T, a, 3.7, (246, 244, 232), 1.2)
        circ(d, T, b, 3.4, (232, 228, 210), 1.2)
        # 다이닌 팔 — 다음 이중관 쪽(접선 방향)으로 내민 작은 다이아몬드
        tip = (b[0] + 7.0 * ux + 0.6 * math.cos(th), b[1] + 7.0 * uy - 0.6 * math.sin(th))
        nx, ny = -uy, ux
        q = [T((tip[0] + 3.6 * ux, tip[1] + 3.6 * uy)), T((tip[0] + 2.6 * nx, tip[1] + 2.6 * ny)), T((tip[0] - 3.6 * ux, tip[1] - 3.6 * uy)), T((tip[0] - 2.6 * nx, tip[1] - 2.6 * ny))]
        d.polygon(q, fill=(170, 222, 246)); d.line(q + [q[0]], fill=INK, width=max(1, int(0.9 * S)))
        d.line([q[0], q[2]], fill=(120, 170, 200), width=max(1, int(0.5 * S)))
work((610, 834, 706, 936), nine_two)
im.save(dst)

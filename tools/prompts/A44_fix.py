#!/usr/bin/env python3
# A44_fix.py — 44장 덧붙임 구역 편집 뒤 손질(2026-11-15 · Opus 5.5).
#   L17c: ① CA2 를 붙인 상자 윗선(y 335) 위에 남은 옛 김 가닥 끝을 하늘빛으로 메운다(맨 왼쪽 김은 이제 병으로 들어감)
#         ② 병으로 빨려 드는 김 띠 위에 꺾쇠 둘(▸) — 띠만으로는 「병에서 새어 나와 물통으로」로 거꾸로 읽혔다(일치 검사 2회 ✕).
#   L17d: 들머리 물줄기 넷에 흰 소금 알갱이 · 작은 칼 셋을 또렷하게 — Gemini 의 반짝이 · 칼이 작고 흐려 「물만」으로도 읽혔다(1회 △).
# 사용: python3 A44_fix.py <L17c|L17d> <in.png> <out.png>
import sys, math, random
import numpy as np, cv2
from PIL import Image, ImageDraw

S = 3
INK = (40, 36, 34, 255)

def layer(img, box):
    x0, y0, x1, y1 = box
    lay = Image.new('RGBA', ((x1 - x0) * S, (y1 - y0) * S), (0, 0, 0, 0))
    return lay, ImageDraw.Draw(lay), (lambda p: ((p[0] - x0) * S, (p[1] - y0) * S))

def put(img, lay, box):
    x0, y0, x1, y1 = box
    small = lay.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    base = img.convert('RGBA'); base.alpha_composite(small, (x0, y0)); return base.convert('RGB')

def chevron(d, P, c, ang, size=8.0, w=2.6, col=(64, 64, 74, 255)):
    ux, uy = math.cos(ang), math.sin(ang); tx, ty = -uy, ux
    tip = (c[0] + ux * size * 0.5, c[1] + uy * size * 0.5)
    a = (c[0] - ux * size * 0.5 + tx * size * 0.6, c[1] - uy * size * 0.5 + ty * size * 0.6)
    b = (c[0] - ux * size * 0.5 - tx * size * 0.6, c[1] - uy * size * 0.5 - ty * size * 0.6)
    for colr, ww in (((245, 245, 248, 255), w + 2.0), (col, w)):
        d.line([P(a), P(tip), P(b)], fill=colr, width=int(round(ww * S)), joint='curve')

def knife(d, P, c, ang, L=24.0):
    ux, uy = math.cos(ang), math.sin(ang); tx, ty = -uy, ux
    hb = (c[0] - ux * L * 0.5, c[1] - uy * L * 0.5); hm = (c[0] - ux * L * 0.08, c[1] - uy * L * 0.08)
    tip = (c[0] + ux * L * 0.5, c[1] + uy * L * 0.5)
    blade = [(hm[0] + tx * 2.6, hm[1] + ty * 2.6), (tip[0], tip[1]), (hm[0] - tx * 2.2, hm[1] - ty * 2.2)]
    d.polygon([P(p) for p in blade], fill=(228, 232, 238, 255), outline=INK, width=int(1.3 * S))
    d.line([P(hb), P(hm)], fill=INK, width=int(6.2 * S)); d.line([P(hb), P(hm)], fill=(132, 84, 46, 255), width=int(3.8 * S))

def grain(d, P, c, r=2.6):
    X, Y = P(c); R = r * S
    d.ellipse([X - R, Y - R, X + R, Y + R], fill=(255, 255, 255, 255), outline=(70, 74, 84, 255), width=int(0.9 * S))

def L17c(img):
    a = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    x0, y0, x1, y1 = 306, 296, 346, 337
    c = a[y0:y1, x0:x1].astype(int)
    m = (((c.max(axis=2) - c.min(axis=2)) < 60) & (c.sum(axis=2) < 560)) | ((c.max(axis=2) - c.min(axis=2)) < 28)   # 잿빛 김 선 · 흰 속
    m = cv2.dilate(m.astype(np.uint8) * 255, np.ones((5, 5), np.uint8))
    M = np.zeros(a.shape[:2], np.uint8); M[y0:y1, x0:x1] = m
    a = cv2.inpaint(a, M, 5, cv2.INPAINT_TELEA)
    img = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))
    box = (290, 340, 410, 490); lay, d, P = layer(img, box)
    chevron(d, P, (353, 428), -math.pi / 2 - 0.08, size=12.0, w=3.2)      # 띠 위 · 물통 수면에서 위로
    chevron(d, P, (337, 370), math.pi + 0.25, size=12.0, w=3.2)           # 띠 위 · 왼쪽 병 아가리로
    return put(img, lay, box)

def L17d(img):
    box = (0, 180, 330, 340); lay, d, P = layer(img, box)
    rnd = random.Random(17)
    holes = [(58, 195), (132, 212), (207, 228), (282, 244)]
    for hx, hy in holes:                                       # 물줄기를 따라 아래 왼쪽으로 · 끝 너머 조금
        for k in range(7):
            t = 0.25 + 0.75 * k / 6
            c = (hx - 30 * t + rnd.uniform(-7, 7), hy + 12 + 62 * t + rnd.uniform(-4, 4))
            grain(d, P, c, rnd.uniform(2.2, 3.0))
    for c, ang in (((40, 268), 1.15), ((104, 290), 1.9), ((178, 312), 1.35)):
        knife(d, P, c, ang)
    return put(img, lay, box)

if __name__ == '__main__':
    which, src, out = sys.argv[1:4]
    img = Image.open(src).convert('RGB')
    img = {'L17c': L17c, 'L17d': L17d}[which](img)
    img.save(out); print(which, 'ok')

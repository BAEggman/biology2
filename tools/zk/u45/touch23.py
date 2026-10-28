#!/usr/bin/env python3
"""touch23.py — s45u01 v4b(b129 뒤 잔손질): cur22 → cur23
 ① 행 5 — 맞물리던 왼 토막에도 금화만 하나(반짝 · 방패 없음) → 왼 토막 = 금화만 받은 1,3-BPG · 오른 토막 = 금화 + 방패 + 반짝 = G3P(두 걸음이 나란히)
 ② 행 12 — 첫 방 걸상 끝에 밀려난 방울(작고 옅어 H⁺ 로 읽힘)을 작업장의 어두운 방울과 같은 꼴 · 짙기로(작업장 방울을 떠다 붙임)
 ③ 행 17 · 18 — 안쪽 방(유관속초)에도 흰 방울 둘(어두운 방울이 훨씬 많다 = CO₂ 농축 · 「O₂ 가 아예 못 든다」 오독 막기)"""
import sys, os, math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, gaussian_filter
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
B = np.asarray(Image.open('cur22.png').convert('RGB')).astype(np.uint8); H, W, _ = B.shape
SS = 4
S = lambda x, y: (x * SS, y * SS)
def overlay(img, fn):
    lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); fn(ImageDraw.Draw(lay))
    im2 = img.convert('RGBA'); im2.alpha_composite(lay.resize((W, H), Image.LANCZOS)); return im2.convert('RGB')

# ── ② 밀려난 방울: 옛 것 지우고 작업장 방울(106~123 · 463~491)을 0.82 배로
A = B.copy()
m = np.zeros((H, W), np.uint8); m[680:701, 899:913] = 1
A = cv2.inpaint(A, binary_dilation(m, iterations=1).astype(np.uint8), 4, cv2.INPAINT_TELEA)
img = Image.fromarray(A)
def drop(d, cx, cy, h, w):
    """어두운 방울(작업장 방울 꼴) — 뾰족한 위 · 둥근 아래 · 짙은 윤곽 · 세로 광택"""
    T = np.linspace(0, 2 * math.pi, 90)
    pts = [S(cx + (w / 2) * math.sin(t) * abs(math.sin(t / 2)) ** 0.9 * 1.25, cy - (h / 2) * math.cos(t)) for t in T]
    d.polygon(pts, fill=(92, 101, 110, 255))
    d.line(pts + [pts[0]], fill=(36, 40, 44, 255), width=int(SS * 1.3))
    hl = [S(cx - w * 0.12 + (w * 0.12) * math.sin(t), cy + h * 0.05 + (h * 0.22) * math.cos(t)) for t in T]
    d.polygon(hl, fill=(168, 178, 186, 220))
img = overlay(img, lambda d: drop(d, 906.0, 681.0, 19.0, 11.0))      # 걸상 윗면 오른끝으로 밀려난 CO₂

# ── ③ 안쪽 방 흰 방울 둘
def bubbles(d):
    for (bx, by, r) in [(1480.0, 577.0, 4.8), (1431.0, 697.0, 4.6)]:
        d.ellipse([S(bx - r, by - r), S(bx + r, by + r)], fill=(250, 251, 253, 255), outline=(126, 138, 156, 255), width=int(SS * 1.1))
        d.ellipse([S(bx - r * 0.55, by - r * 0.6), S(bx - r * 0.05, by - r * 0.1)], fill=(255, 255, 255, 255))
        d.arc([S(bx - r * 0.75, by - r * 0.75), S(bx + r * 0.75, by + r * 0.75)], 20, 110, fill=(200, 208, 222, 255), width=int(SS * 0.9))
img = overlay(img, bubbles)

# ── ① 왼 토막 금화(탁자 금화 꼴 — 세로 타원 · 왼쪽 두께 띠 · 안쪽 테)
def coin_edge(d, cx, cy, r, ang=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    def P(u, v): return S(cx + u * ca - v * sa, cy + u * sa + v * ca)
    rx, ry = r * 0.58, r
    T = np.linspace(0, 2 * math.pi, 72)
    edge = [P(rx * math.cos(t) - r * 0.28, ry * math.sin(t)) for t in T]
    face = [P(rx * math.cos(t), ry * math.sin(t)) for t in T]
    d.polygon(edge, fill=(176, 122, 26, 255)); d.line(edge + [edge[0]], fill=(52, 34, 10, 255), width=int(SS * 1.3))
    d.polygon(face, fill=(236, 190, 58, 255)); d.line(face + [face[0]], fill=(52, 34, 10, 255), width=int(SS * 1.3))
    inner = [P(rx * 0.72 * math.cos(t), ry * 0.78 * math.sin(t)) for t in T]
    d.line(inner + [inner[0]], fill=(186, 136, 30, 255), width=int(SS * 1.1))
    mid = [P(rx * 0.34 * math.cos(t) + r * 0.05, ry * 0.42 * math.sin(t)) for t in T]
    d.polygon(mid, fill=(246, 210, 96, 255))
img = overlay(img, lambda d: coin_edge(d, 284.0, 612.5, 10.0))
# 토막 윗등이 동전 밑동을 살짝 덮는다(박힌 꼴) — 토막 화소(크림 · 밤색 · 윤곽)를 동전 아래 3px 띠에서 되살림
C = np.asarray(img).copy()
band = np.zeros((H, W), bool); band[621:625, 276:293] = True
sub = B.astype(int)
piece = band & ((sub.mean(axis=2) > 150) | (sub.mean(axis=2) < 90))
C[piece] = B[piece]
img = Image.fromarray(C)

img.save('cur23.png')
for (b, n, k2) in [((240, 580, 380, 650), 'v23_pieces.png', 6), ((860, 640, 930, 710), 'v23_drop.png', 8), ((1380, 530, 1510, 760), 'v23_chamber.png', 4)]:
    img.crop(b).resize(((b[2] - b[0]) * k2, (b[3] - b[1]) * k2), Image.LANCZOS).save(n)
print('cur23 saved')

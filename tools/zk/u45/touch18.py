#!/usr/bin/env python3
"""touch18.py — s45u01 v2b(b126 뒤 잔손질): cur17 → cur18
 ① 미끄럼틀 출구 막대에 반짝 둘(꽂이 막대와 같은 표지 — 반짝 = 환원된 G3P) ② 벽 아래 구멍을 테 없는 까만 구멍으로 · 막대 끝이 구멍 속으로
 ③ C₄ 바닥의 금화 막대 — 마디 셋이 다 보이게(금화는 막대 윗등에 반쯤 박음) ④ C₄ 사람 손 막대 끝에서 흰 방울 하나가 튕겨 나감(O₂ 는 안 붙는다)"""
import sys, os, math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
sys.path.insert(0, '/tmp/b2/tools/zk/u45'); import rods
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
B = np.asarray(Image.open('cur17.png').convert('RGB')).astype(np.uint8); H, W, _ = B.shape
A = B.copy()
SS = 4
def overlay(draw_fn):
    global img
    lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); draw_fn(d)
    im2 = img.convert('RGBA'); im2.alpha_composite(lay.resize((W, H), Image.LANCZOS)); img = im2.convert('RGB')
S = lambda x, y: (x * SS, y * SS)
# ── ③ 옛 금화 지움(금빛 · 짙은 테 화소) → inpaint
sub = A[746:776, 1490:1512].astype(int); R, G, Bb = sub[..., 0], sub[..., 1], sub[..., 2]
m = np.zeros((H, W), np.uint8)
m[746:776, 1490:1512] = (((R - Bb > 60) & (G - Bb > 30)) | (sub.mean(axis=2) < 90)).astype(np.uint8)
m[766:776, 1490:1512] = 0                       # 막대 아래쪽 띠는 새 막대가 덮는다
m = binary_dilation(m, iterations=1).astype(np.uint8)
A = cv2.inpaint(A, m, 4, cv2.INPAINT_TELEA)
# ── ② 구멍: 테 없는 까만 구멍(반원 — 바닥선에 걸침)
img = Image.fromarray(A)
def hole(d):
    d.pieslice([S(499, 588), S(529, 618)], 180, 360, fill=(26, 20, 16, 255))
    d.rectangle([S(499, 603), S(529, 617)], fill=(26, 20, 16, 255))
    d.arc([S(499, 588), S(529, 618)], 180, 360, fill=(12, 9, 7, 255), width=int(SS * 1.6))
overlay(hole)
# 미끄럼틀 판자(구멍 위로 지나가는 부분)는 원본으로 되살림 — 판자 화소: 갈색 나무
sub = B[585:625, 495:535].astype(int); Rr, Gg, Bv = sub[..., 0], sub[..., 1], sub[..., 2]
plank = (Rr - Bv > 25) & (Rr - Bv < 90) & (sub.mean(axis=2) > 95) & (sub.mean(axis=2) < 200) & (Gg - Bv > 10)
# 판자는 구멍 오른쪽 아래로 지나간다 — x>=513 쪽 판자 화소만
xs = np.arange(495, 535)[None, :].repeat(40, 0)
pm = np.zeros((H, W), bool); pm[585:625, 495:535] = plank & (xs >= 512)
pm = binary_dilation(pm, iterations=1) & np.pad(np.ones((40, 40), bool), ((585, H - 625), (495, W - 535)))
C = np.asarray(img).copy(); C[pm] = B[pm]; img = Image.fromarray(C)
# 출구 막대 다시(끝이 구멍 속으로 사라짐 — 아래 둥근 끝 없음)
img = rods.draw_rod(img, (542, 540), (519, 593), 3, 10, first='cream', cap1=False)
def hole_lip(d):   # 구멍 위 테두리가 막대 끝을 살짝 덮음
    d.arc([S(499, 588), S(529, 618)], 200, 300, fill=(12, 9, 7, 255), width=int(SS * 1.6))
overlay(hole_lip)
# ── ① 반짝 둘(꽂이 막대와 같은 4꼭지 별)
def spark(d, x, y, r):
    for (dx, dy) in [(r, 0), (0, r)]:
        d.line([S(x - dx, y - dy), S(x + dx, y + dy)], fill=(70, 70, 60, 255), width=int(SS * 1.6))
    d.polygon([S(x, y - r), S(x + r * 0.22, y - r * 0.22), S(x + r, y), S(x + r * 0.22, y + r * 0.22), S(x, y + r), S(x - r * 0.22, y + r * 0.22), S(x - r, y), S(x - r * 0.22, y - r * 0.22)], fill=(255, 252, 230, 255))
overlay(lambda d: (spark(d, 524, 547, 5.5), spark(d, 516, 572, 4.5)))
# ── ③ 새 금화 막대
img = rods.draw_rod(img, (1461, 773), (1505, 763), 3, 11, first='cream')
img = rods.coin(img, (1484, 760), 5.8, ang=0.0, squash=1.0)
# ── ④ 흰 방울이 막대 끝에서 튕겨 나감
def bounce(d):
    x, y, r = 1549, 668, 5.5
    d.ellipse([S(x - r, y - r), S(x + r, y + r)], fill=(252, 252, 250, 255), outline=(110, 114, 120, 255), width=int(SS * 1.3))
    d.ellipse([S(x - r * 0.55, y - r * 0.6), S(x - r * 0.1, y - r * 0.15)], fill=(255, 255, 255, 255))
    for k, (r1, a0, a1) in enumerate([(9, 200, 260), (14, 205, 255)]):
        d.arc([S(1566 - r1, 690 - r1), S(1566 + r1, 690 + r1)], a0, a1, fill=(60, 64, 70, 255), width=int(SS * 1.2))
overlay(bounce)
img.save('cur18.png')
for (b, n) in [((480, 520, 580, 630), 'v18_hole.png'), ((1440, 730, 1530, 790), 'v18_c4rod.png'), ((1530, 640, 1640, 730), 'v18_bounce.png')]:
    img.crop(b).resize(((b[2] - b[0]) * 5, (b[3] - b[1]) * 5), Image.LANCZOS).save(n)
print('cur18 saved')

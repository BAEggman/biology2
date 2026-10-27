#!/usr/bin/env python3
"""touch15.py — s45u01 v2(b125 뒤): cur14 → cur15
 ① 작업장 방울 둘을 스코프 위로 줄 세움(차례로 하나씩 · 세 바퀴) ② 미끄럼틀 막대 = 마디 셋, 아래 끝이 벽 구멍으로 들어감
 ③ 문간 토막 둘 = 마디 둘 ④ 짐꾼 막대 금화 = 테 두른 납작 동전(정면 원) ⑤ 포도 = 윤기 · 꼭지 있는 낱알
 ⑥ C₄ 관 다섯을 띠 둘로 묶어 한 다발"""
import sys, os, math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
sys.path.insert(0, '/tmp/b2/tools/zk/u45'); import rods
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
B = np.asarray(Image.open('cur14.png').convert('RGB')).astype(np.uint8); H, W, _ = B.shape
A = B.copy()
Lf = lambda s: s.astype(int).mean(axis=2)
def dropmask(x0, y0, x1, y1):
    s = B[y0:y1, x0:x1].astype(int); L = s.mean(axis=2)
    m = (L < 175) & (np.abs(s[..., 0] - s[..., 2]) < 40) & (np.abs(s[..., 0] - s[..., 1]) < 30)
    m = binary_dilation(m, iterations=1)
    M = np.zeros((H, W), bool); M[y0:y1, x0:x1] = m; return M
# ── ① 방울 둘 옮기기
moves = [((207, 551, 228, 586), (121, 503)), ((153, 604, 172, 637), (106, 462))]   # (옛 상자, 새 왼위 모서리)
sprites = []
for (x0, y0, x1, y1), (nx, ny) in moves:
    M = dropmask(x0, y0, x1, y1)
    sprites.append((B[y0:y1, x0:x1].copy(), M[y0:y1, x0:x1].copy(), nx, ny))
    A = cv2.inpaint(A, binary_dilation(M, iterations=2).astype(np.uint8), 5, cv2.INPAINT_TELEA)
for (spr, m, nx, ny) in sprites:
    h, w = m.shape; reg = A[ny:ny + h, nx:nx + w]; reg[m] = spr[m]; A[ny:ny + h, nx:nx + w] = reg
img = Image.fromarray(A)
# ── ② 미끄럼틀 막대(마디 셋) — 옛 막대를 덮고 아래 끝은 구멍 속으로
hole = np.zeros((H, W), bool); s = B[588:618, 498:528].astype(int); hole[588:618, 498:528] = s.mean(axis=2) < 95
img = rods.draw_rod(img, (542, 540), (517, 597), 3, 10, first='cream')
C = np.asarray(img).copy(); C[hole] = B[hole]; img = Image.fromarray(C)
# ── ③ 문간 토막 둘(마디 둘)
img = rods.draw_rod(img, (963, 734), (945, 783), 2, 10, first='cream')
img = rods.draw_rod(img, (1087, 744), (1099, 785), 2, 10, first='tan')
# ── ④ 짐꾼 금화 — 정면 원(테 두른 납작 동전)
for (p0, p1) in [((626, 665), (760, 528)), ((636, 676), (765, 539)), ((641, 689), (767, 551))]:
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    cx, cy = p0[0] + ux * 16 - uy * 3.5, p0[1] + uy * 16 + ux * 3.5
    img = rods.coin(img, (cx, cy), 7.2, ang=0.0, squash=1.0)
# ── ⑤ 포도(윤기 · 꼭지)
SS = 4
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
def grape(x, y, r=4.6, stem=False):
    S = lambda a, b: (a * SS, b * SS)
    d.ellipse([S(x - r, y - r * 1.06), S(x + r, y + r * 1.06)], fill=(104, 50, 132, 255), outline=(52, 22, 70, 255), width=int(SS * 1.1))
    d.ellipse([S(x - r * 0.75, y - r * 0.8), S(x + r * 0.35, y + r * 0.3)], fill=(140, 84, 170, 255))
    d.ellipse([S(x - r * 0.55, y - r * 0.62), S(x - r * 0.1, y - r * 0.18)], fill=(236, 220, 246, 255))
    if stem:
        d.line([S(x + 0.2, y - r * 1.02), S(x + 1.4, y - r * 1.02 - 3.2)], fill=(96, 72, 38, 255), width=int(SS * 1.4))
for (x, y, st) in [(866, 763, True), (875, 767, False), (868, 772, False), (881, 769, True), (879, 779, False), (893, 769, True), (909, 773, False), (900, 783, True)]:
    grape(x, y, 4.7, st)
img = img.convert('RGBA'); img.alpha_composite(lay.resize((W, H), Image.LANCZOS)); img = img.convert('RGB')
# ── ⑥ 관 다발 띠 둘(관 다섯 · x 1415~1471)
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
for yb in (402, 452):
    pts_top = [((1413 + t * 60) * SS, (yb + 2.2 * math.sin(math.pi * t)) * SS) for t in np.linspace(0, 1, 30)]
    pts_bot = [((1413 + t * 60) * SS, (yb + 6 + 2.2 * math.sin(math.pi * t)) * SS) for t in np.linspace(1, 0, 30)]
    d.polygon(pts_top + pts_bot, fill=(110, 74, 44, 255), outline=(48, 30, 18, 255))
    d.line(pts_top, fill=(48, 30, 18, 255), width=SS * 1); d.line(pts_bot, fill=(48, 30, 18, 255), width=SS * 1)
    d.line([(p[0], p[1] + 1.6 * SS) for p in pts_top], fill=(168, 124, 82, 255), width=SS * 1)
img = img.convert('RGBA'); img.alpha_composite(lay.resize((W, H), Image.LANCZOS)); img = img.convert('RGB')
img.save('cur15.png')
for (b, n) in [((80, 430, 280, 660), 'v15_drops.png'), ((470, 510, 580, 630), 'v15_slide.png'), ((900, 700, 1120, 800), 'v15_stubs.png'),
               ((600, 620, 700, 710), 'v15_coins.png'), ((800, 730, 925, 800), 'v15_grapes.png'), ((1380, 330, 1500, 520), 'v15_pipes.png')]:
    img.crop(b).resize(((b[2] - b[0]) * 3, (b[3] - b[1]) * 3), Image.LANCZOS).save(n)
print('cur15 saved')

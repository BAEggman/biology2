#!/usr/bin/env python3
"""touch_a.py — s45u02 「빛 받는 꼬투리」 PIL 손질 1: cur6 → cur7
 ① 〔B 꼬투리〕 스트로마 깔개 위 — s45u01 C₄ 안쪽 방의 루비빛 렌즈 스코프(기둥 · 받침 · 발톱)를 0.6 배로 떠 옮기고,
    마디 다섯 막대(PIL · rods.draw_rod)를 렌즈 앞에 기대 세우고 어두운 방울을 그 끝에(같은 물건 · 같은 동작 = 탄소고정이 여기서)
 ② 〔D 걸상〕 초록 · 노랑 자리의 헤엄이 · 방울을 지우고(inpaint), 주황 자리에 작은 방울 둘
 쓰는 곳: python3 touch_a.py <작업폴더> <s45u01 final png>"""
import sys, os, math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_fill_holes, label, gaussian_filter
sys.path.insert(0, '/tmp/b2/tools/zk/u45'); import rods
os.chdir(sys.argv[1]); U01 = sys.argv[2]
B = np.asarray(Image.open('cur6.png').convert('RGB')).copy(); H, W, _ = B.shape
SS = 4
S = lambda x, y: (x * SS, y * SS)
def overlay(img, fn):
    lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); fn(ImageDraw.Draw(lay))
    im2 = img.convert('RGBA'); im2.alpha_composite(lay.resize((W, H), Image.LANCZOS)); return im2.convert('RGB')

# ── ① 스코프 떠 옮기기(기둥 · 받침 · 발톱까지 — 배경과 다른 화소 중 막대 · 방울 · 방 벽선은 뺀다)
U = np.asarray(Image.open(U01).convert('RGB')).astype(int)
sx0, sy0, sx1, sy1 = 1386, 630, 1512, 742
sub = U[sy0:sy1, sx0:sx1]
sat = sub.max(axis=2) - sub.min(axis=2); L = sub.mean(axis=2)
yy, xx = np.mgrid[sy0:sy1, sx0:sx1]
rodzone = ((xx < 1405) & (yy > 674)) | ((xx > 1455) & (yy < 642))      # 작업장 막대 · 들창 막대
colour = (sat > 40) & ~rodzone
near = binary_dilation(colour, iterations=3)
ink = (L < 80) & near & ~rodzone
mask = binary_fill_holes(binary_dilation(colour | ink, iterations=1)) & ~rodzone
drop = (sat < 26) & (L > 70) & (L < 160)
mask &= ~(drop & ~binary_dilation(colour, iterations=1))
lab, n = label(mask); sizes = np.bincount(lab.ravel()); sizes[0] = 0
mask = np.isin(lab, [i for i in range(1, n + 1) if sizes[i] >= 25])
k = 0.6
sw, sh = int(round((sx1 - sx0) * k)), int(round((sy1 - sy0) * k))
spr = cv2.resize(sub.astype(np.uint8), (sw, sh), interpolation=cv2.INTER_AREA).astype(float)
msk = cv2.resize(gaussian_filter(mask.astype(float), 0.6), (sw, sh), interpolation=cv2.INTER_AREA)
msk = np.clip(msk * 1.3, 0, 1)[..., None]
dx, dy = 636, 634                                       # 렌즈 가운데 ≈ (636 + 19*0.6 , 634 + 30*0.6) = (647, 652)
roi = B[dy:dy + sh, dx:dx + sw].astype(float)
B[dy:dy + sh, dx:dx + sw] = np.clip(roi * (1 - msk) + spr * msk, 0, 255).astype(np.uint8)
img = Image.fromarray(B)
claw = mask & (L < 110) & ((xx - 1405) ** 2 + (yy - 660) ** 2 < 34 ** 2)
# 마디 다섯 막대 — 렌즈 앞(왼 아래)에서 깔개로
img = rods.draw_rod(img, (640, 704), (646, 660), 5, 7, first='tan')
def drop_fn(d, cx, cy, h, w):
    T = np.linspace(0, 2 * math.pi, 90)
    pts = [S(cx + (w / 2) * math.sin(t) * abs(math.sin(t / 2)) ** 0.9 * 1.25, cy - (h / 2) * math.cos(t)) for t in T]
    d.polygon(pts, fill=(92, 101, 110, 255)); d.line(pts + [pts[0]], fill=(36, 40, 44, 255), width=int(SS * 1.1))
    hl = [S(cx - w * 0.12 + (w * 0.12) * math.sin(t), cy + h * 0.05 + (h * 0.22) * math.cos(t)) for t in T]
    d.polygon(hl, fill=(168, 178, 186, 220))
# 방울은 막대 윗끝 · 렌즈 왼아래(발톱이 누르는 자리) — 스코프 위에 그린다
img = overlay(img, lambda d: drop_fn(d, 639.5, 655.0, 14.0, 9.0))

# ── ② 걸상: 초록 · 노랑 자리 헤엄이 · 방울을 cur5(붙이기 전)로 되돌림 + 주황 자리 작은 방울 둘
A = np.asarray(img).copy(); P5 = np.asarray(Image.open('cur5.png').convert('RGB'))
for (x0, y0, x1, y1) in [(1740, 600, 1780, 656), (1786, 600, 1846, 660)]:
    A[y0:y1, x0:x1] = P5[y0:y1, x0:x1]
img = Image.fromarray(A)
def bub(d, cx, cy, r):
    d.ellipse([S(cx - r, cy - r), S(cx + r, cy + r)], fill=(250, 251, 253, 255), outline=(120, 132, 150, 255), width=int(SS * 0.9))
    d.ellipse([S(cx - r * 0.5, cy - r * 0.55), S(cx - r * 0.05, cy - r * 0.1)], fill=(255, 255, 255, 255))
# (주황 자리 작은 방울은 touch_b 가 띠 한가운데에 — v2)
img.save('cur7.png')
for (b, nm, kk) in [((590, 600, 820, 720), 'v7_stroma.png', 4), ((1660, 580, 1900, 670), 'v7_bench.png', 4)]:
    img.crop(b).resize(((b[2] - b[0]) * kk, (b[3] - b[1]) * kk), Image.LANCZOS).save(nm)
print('cur7 saved')

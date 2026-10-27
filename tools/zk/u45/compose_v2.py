#!/usr/bin/env python3
"""compose_v2.py — s45u01 r1: cur0 위에 편집 조각을 다시 붙이되
 · E1 은 방울 셋만(타원 가면) — Gemini 가 스코프 둘레에 그린 점선 테두리를 버리고 바탕 스코프를 지킨다
 · 작업장 막대(마디 다섯)는 PIL 로 정확히 — 아래 발톱 뒤로 지나가게(발톱을 바탕에서 되살림)
 · E2 는 스코프 눈대롱 자리를 지킨다
 · 짐꾼 막대 셋(마디 다섯씩) + 금화 셋을 PIL 로 다시 — 손은 되살림
출력 cur12.png → floorfix → cur12b.png"""
import json, subprocess, sys, os, math, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation, binary_fill_holes
sys.path.insert(0, '/tmp/b2/tools/zk/u45'); import rods
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(float)
def box2(name):
    cj = json.load(open(f'crop_{name}.json')); S = cj['scale']; return [v * S for v in cj['box']]
def fitarr(name, fitname):
    bx0, by0, bx1, by1 = box2(name)
    return np.asarray(Image.open(fitname).convert('RGB').resize((bx1 - bx0, by1 - by0), Image.LANCZOS)).astype(float)
def paste_mask(C, name, F, M):
    bx0, by0, bx1, by1 = box2(name)
    C[by0:by1, bx0:bx1] = C[by0:by1, bx0:bx1] * (1 - M[..., None]) + F * M[..., None]
def diff_core(C, name, F, thr):
    bx0, by0, bx1, by1 = box2(name)
    return gaussian_filter(np.abs(C[by0:by1, bx0:bx1] - F).mean(axis=2), 1.0) > thr
def feather(m, f=1.5): return np.clip(gaussian_filter(m.astype(float), f) * 1.3, 0, 1)
def glob_poly_mask(shape, polys=(), ellipses=(), rects=()):
    im = Image.new('L', (shape[1], shape[0]), 0); d = ImageDraw.Draw(im)
    for p in polys: d.polygon(p, fill=255)
    for e in ellipses: d.ellipse(e, fill=255)
    for r in rects: d.rectangle(r, fill=255)
    return np.asarray(im) > 0
C0 = load('cur0.png'); C = C0.copy(); H, W, _ = C.shape
# ── E1: 방울 셋만
F1 = fitarr('E1', 'fit_E1.png'); bx0, by0, bx1, by1 = box2('E1')
drops = glob_poly_mask((H, W), ellipses=[(123, 544, 145, 581), (204, 551, 228, 582), (150, 601, 174, 634)])[by0:by1, bx0:bx1]
m = binary_dilation(diff_core(C, 'E1', F1, 10), iterations=2) & drops
paste_mask(C, 'E1', F1, feather(m, 0.8))
# ── 작업장 막대(마디 다섯) — 아래 발톱 뒤로
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8'))
img = rods.draw_rod(img, (101, 666), (133, 585), 5, 11, first='tan')
C = np.asarray(img).astype(float)
prong = np.zeros((H, W), bool); sub = C0[566:606, 114:156]; prong[566:606, 114:156] = sub.mean(axis=2) < 105
prong = binary_dilation(prong, iterations=1) & glob_poly_mask((H, W), rects=[(114, 566, 156, 606)])
C[prong] = C0[prong]
# 맨 위 방울을 다시 위에
mt = binary_dilation(diff_core(C0, 'E1', F1, 10), iterations=2) & glob_poly_mask((H, W), ellipses=[(123, 544, 145, 581)])[by0:by1, bx0:bx1]
paste_mask(C, 'E1', F1, feather(mt, 0.8))
# ── E2 ~ E10
def dm(name, fitname, thr=14, dil=4, own=None, keep=(), protect=None, fe=1.5):
    F = fitarr(name, fitname); bx0, by0, bx1, by1 = box2(name); h, w = F.shape[:2]
    R = np.zeros((h, w), bool)
    for (x0, y0, x1, y1) in (own or [(0, 0, w, h)]): R[max(0, y0):y1, max(0, x0):x1] = True
    m = binary_fill_holes(binary_dilation(diff_core(C, name, F, thr), iterations=dil)) & R
    for (x0, y0, x1, y1) in keep: m[max(0, y0):y1, max(0, x0):x1] = False
    if protect is not None: m &= ~protect[by0:by1, bx0:bx1]
    paste_mask(C, name, F, feather(m, fe)); return int(m.sum())
def rm(name, fitname, own, fe=2.0):
    F = fitarr(name, fitname); bx0, by0, bx1, by1 = box2(name); h, w = F.shape[:2]
    m = np.zeros((h, w), bool)
    for (x0, y0, x1, y1) in own: m[max(0, y0):y1, max(0, x0):x1] = True
    paste_mask(C, name, F, feather(m, fe)); return int(m.sum())
scope_eye = glob_poly_mask((H, W), polys=[[(150, 560), (175, 560), (268, 600), (268, 632), (240, 634), (140, 600)]])
print('E2', dm('E2', 'fit_E2.png', protect=scope_eye))
print('E3', rm('E3', 'fit_E3b.png', [(0, 40, 208, 200)]))
print('E4', dm('E4', 'fit_E4.png'))
print('E5', dm('E5', 'fit_E5.png', keep=[(135, 268, 176, 335), (128, 368, 150, 425)]))
print('E6', rm('E6', 'fit_E6.png', [(8, 330, 166, 536)], fe=2.5))
print('E7', dm('E7', 'fit_E7.png'))
print('E8', dm('E8', 'fit_E8.png'))
print('E9', dm('E9', 'fit_E9.png', thr=12))
print('E10', dm('E10', 'fit_E10.png', dil=5, own=[(50, 150, 300, 296)]))
# ── 짐꾼 막대 셋 + 금화 — 손 되살림
before = C.copy()
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8'))
for (p0, p1) in [((626, 665), (760, 528)), ((636, 676), (765, 539)), ((641, 689), (767, 551))]:
    img = rods.draw_rod(img, p0, p1, 5, 12, first='cream')
for (p0, p1) in [((626, 665), (760, 528)), ((636, 676), (765, 539)), ((641, 689), (767, 551))]:
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    cx, cy = p0[0] + ux * 16 - uy * 4.5, p0[1] + uy * 16 + ux * 4.5      # 앞끝 옆구리(위쪽)
    img = rods.coin(img, (cx, cy), 6.5, ang=math.atan2(uy, ux), squash=0.62)
C = np.asarray(img).astype(float)
# 손: 살빛 화소(E4 판)를 덩어리로 골라 + 둘레 1~2px 의 짙은 윤곽만 — 옛 막대 조각은 되살리지 않는다
from scipy.ndimage import label, binary_closing
hx0, hy0, hx1, hy1 = 665, 585, 730, 650
Sb = before[hy0:hy1, hx0:hx1]; Rr, Gg, Bb = Sb[..., 0], Sb[..., 1], Sb[..., 2]; Lb = Sb.mean(axis=2)
skin = (Rr - Bb >= 25) & (Rr - Bb <= 75) & (Lb >= 150) & (Lb <= 228) & (Rr - Gg >= 8) & (Rr - Gg <= 45) & (Gg > Bb)
lab, nl = label(skin); keep = np.zeros_like(skin)
for i in range(1, nl + 1):
    ys, xs = np.where(lab == i)
    if len(ys) >= 15 and abs(xs.mean() + hx0 - 692) < 16 and abs(ys.mean() + hy0 - 619) < 16: keep |= (lab == i)
keep = binary_fill_holes(binary_closing(keep, iterations=2))
ring = binary_dilation(keep, iterations=2) & ~keep & (Lb < 105)
hm = np.zeros((H, W), bool); hm[hy0:hy1, hx0:hx1] = keep | ring
C[hm] = before[hm]
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save('cur12.png')
subprocess.run(['python3', '/tmp/b2/tools/zk/u45/floorfix.py', 'cur12.png', 'cur12b.png'], check=True)
im = Image.open('cur12b.png')
im.crop((90, 520, 400, 700)).resize((930, 540), Image.LANCZOS).save('v12_hall.png')
im.crop((600, 500, 790, 710)).resize((570, 630), Image.LANCZOS).save('v12_porter.png')
print('done')

#!/usr/bin/env python3
"""fix_rods.py — cur12b → cur13: 마디 수가 뜻을 나르는 막대를 PIL 로 정확히(옛 막대는 캡슐 가면으로 지우고 같은 축에 다시)
 · 첫 방(광호흡) 긴 막대 = 다섯 · 흰 방울 위에
 · 두 방 집 안쪽 방 긴 막대 = 다섯 · 끝 방울 위에
 · 두 방 집 사람 손의 짧은 막대 = 셋 · 손 · 매달린 방울 위에
 · 탑 아래층 긴 막대 = 다섯 · 방울 위에
 · 두 방 집 바닥의 납작 금화 하나 지움(금화 박힌 막대 하나만 남김) · 안쪽 방 흰 방울 하나 지움"""
import sys, os, math, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_fill_holes, label, binary_closing
import cv2
sys.path.insert(0, '/tmp/b2/tools/zk/u45'); import rods
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
src = sys.argv[2] if len(sys.argv) > 2 else 'cur12b.png'
B = np.asarray(Image.open(src).convert('RGB')).astype(float); H, W, _ = B.shape
img = Image.fromarray(B.astype('uint8'))
Lf = lambda s: s.mean(axis=2)
def restore(mask):
    global img
    C = np.asarray(img).astype(float); C[mask] = B[mask]; img = Image.fromarray(np.clip(C, 0, 255).astype('uint8'))
def boxmask(x0, y0, x1, y1, cond):
    m = np.zeros((H, W), bool); sub = B[y0:y1, x0:x1]; m[y0:y1, x0:x1] = cond(sub); return m
def capsule(p0, p1, r):
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    d.line([p0, p1], fill=255, width=int(2 * r)); d.ellipse([p0[0] - r, p0[1] - r, p0[0] + r, p0[1] + r], fill=255); d.ellipse([p1[0] - r, p1[1] - r, p1[0] + r, p1[1] + r], fill=255)
    return np.asarray(im) > 0
def erase(mask, rad=4):
    global img
    img = Image.fromarray(cv2.inpaint(np.asarray(img), mask.astype(np.uint8), rad, cv2.INPAINT_TELEA))
gray = lambda s: (Lf(s) < 160) & (np.abs(s[..., 0] - s[..., 2]) < 30) & (np.abs(s[..., 0] - s[..., 1]) < 22)
white = lambda s: s.min(axis=2) > 205
def skinmask(x0, y0, x1, y1):
    Sb = B[y0:y1, x0:x1]; Rr, Gg, Bb = Sb[..., 0], Sb[..., 1], Sb[..., 2]
    sk = (Rr - Bb >= 20) & (Rr - Bb <= 80) & (Lf(Sb) >= 140) & (Lf(Sb) <= 218) & (Rr - Gg >= 16) & (Gg > Bb)
    lab, nl = label(sk); keep = np.zeros_like(sk)
    for i in range(1, nl + 1):
        if (lab == i).sum() >= 25: keep |= (lab == i)
    keep = binary_fill_holes(binary_closing(keep, iterations=2)); ring = binary_dilation(keep, iterations=2) & ~keep & (Lf(Sb) < 105)
    m = np.zeros((H, W), bool); m[y0:y1, x0:x1] = keep | ring; return m
# ── 안쪽 방 흰 방울 · 바닥 납작 금화 지움
erase(binary_dilation(boxmask(1468, 604, 1494, 630, white), iterations=2))
erase(binary_dilation(boxmask(1512, 756, 1540, 774, lambda s: (s[..., 0] - s[..., 2] > 70) | (Lf(s) < 110)), iterations=2), 3)
# ── 첫 방 긴 막대(다섯)
img = rods.draw_rod(img, (822, 452), (891, 584), 5, 10, first='cream')
restore(boxmask(882, 572, 912, 604, white) | boxmask(884, 597, 912, 606, lambda s: Lf(s) < 95))
# ── 두 방 집 안쪽 긴 막대(다섯)
erase(capsule((1385, 768), (1402, 674), 8) & ~boxmask(1388, 652, 1414, 690, gray))
img = rods.draw_rod(img, (1385, 767), (1400, 680), 5, 11, first='cream')
restore(boxmask(1388, 652, 1414, 690, gray))
# ── 탑 아래층 긴 막대(다섯)
erase((capsule((1865, 747), (1898, 647), 7) | capsule((1897, 652), (1913, 616), 6)) & ~boxmask(1890, 672, 1916, 698, gray))
img = rods.draw_rod(img, (1866, 746), (1896, 670), 5, 10, first='cream')
restore(boxmask(1890, 672, 1916, 698, gray))
# ── 두 방 집 사람 손의 짧은 막대(셋)
hand = skinmask(1588, 655, 1626, 700); drop = boxmask(1558, 694, 1582, 720, gray)
erase(capsule((1566, 692), (1629, 669), 8) & ~hand & ~drop)
img = rods.draw_rod(img, (1567, 691), (1628, 670), 3, 11, first='cream')
restore(hand | drop)
# ── 바닥 금화 자리: 오른쪽 맨땅(1600~1628)의 결을 옮겨 붙임(깃털)
C = np.asarray(img).astype(float)
src_p = B[756:775, 1600:1629].copy(); h_, w_ = src_p.shape[:2]
M = np.ones((h_, w_)); M[:2] = 0; M[-2:] = 0; M[:, :3] = 0; M[:, -3:] = 0
from scipy.ndimage import gaussian_filter
M = np.clip(gaussian_filter(M, 1.5) * 1.4, 0, 1)
C[756:775, 1506:1535] = C[756:775, 1506:1535] * (1 - M[..., None]) + src_p * M[..., None]
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8'))
img.save('cur13.png')
for (b, n) in [((800, 430, 930, 640), 'v13_room1.png'), ((1360, 600, 1640, 790), 'v13_c4.png'), ((1840, 620, 1960, 760), 'v13_cam.png')]:
    img.crop(b).resize(((b[2] - b[0]) * 3, (b[3] - b[1]) * 3), Image.LANCZOS).save(n)
print('cur13 saved')

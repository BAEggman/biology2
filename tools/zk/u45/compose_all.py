#!/usr/bin/env python3
"""compose_all.py — s45u01 r1: cur0(바탕 B 2배) 위에 편집 조각(fit_E*)을 차례로 다시 붙인다(고친 가면으로 한 번에).
E1 은 색 가면(막대 크림·밤색 · 방울 회청색만) — 스코프·작업대 가장자리의 「점선 이음」(두 그림의 테두리가 번갈아 남는 것)을 막는다."""
import json, subprocess, sys, os, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation, binary_fill_holes
D = sys.argv[1] if len(sys.argv) > 1 else '.'
os.chdir(D)
def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(float)
def box2(name):
    cj = json.load(open(f'crop_{name}.json')); S = cj['scale']; return [v * S for v in cj['box']]
def paste(C, name, fitname, M):
    bx0, by0, bx1, by1 = box2(name)
    F = np.asarray(Image.open(fitname).convert('RGB').resize((bx1 - bx0, by1 - by0), Image.LANCZOS)).astype(float)
    reg = C[by0:by1, bx0:bx1]; C[by0:by1, bx0:bx1] = reg * (1 - M[..., None]) + F * M[..., None]
def diffmask(C, name, fitname, thr=14, dil=4, own=None, keep=(), feather=1.5, color=None):
    bx0, by0, bx1, by1 = box2(name)
    F = np.asarray(Image.open(fitname).convert('RGB').resize((bx1 - bx0, by1 - by0), Image.LANCZOS)).astype(float)
    C0 = C[by0:by1, bx0:bx1]; h, w = F.shape[:2]
    d = gaussian_filter(np.abs(C0 - F).mean(axis=2), 1.0)
    R = np.zeros((h, w), bool)
    for (x0, y0, x1, y1) in (own or [(0, 0, w, h)]): R[max(0, y0):y1, max(0, x0):x1] = True
    chg = (d > thr) & R
    if color is not None:
        core = chg & color(F)
        m = core.copy()
        for _ in range(3): m = binary_dilation(m) & (chg | binary_dilation(core, iterations=1))
        m = binary_fill_holes(m) & R
    else:
        m = binary_fill_holes(binary_dilation(chg, iterations=dil)) & R
    M = m.astype(float)
    for (x0, y0, x1, y1) in keep: M[max(0, y0):y1, max(0, x0):x1] = 0
    M = np.clip(gaussian_filter(M, feather) * 1.3, 0, 1)
    return M, F
def rectmask(name, own, feather=2.0):
    bx0, by0, bx1, by1 = box2(name); h, w = by1 - by0, bx1 - bx0
    M = np.zeros((h, w))
    for (x0, y0, x1, y1) in own: M[max(0, y0):y1, max(0, x0):x1] = 1
    return np.clip(gaussian_filter(M, feather) * 1.3, 0, 1)
def rod_or_drop(F):
    R, G, B = F[..., 0], F[..., 1], F[..., 2]; L = F.mean(axis=2)
    rod = (R > 150) & (G > 115) & (B > 60) & (R - B > 35) & (R - G < 60) & (L > 150)   # 크림 · 밤색 마디(놋쇠보다 밝고 덜 노랗다)
    brass = (R - B > 90) & (G - B > 45)                                                # 놋쇠 스코프 — 빼다
    drop = (L > 70) & (L < 165) & (np.abs(R - G) < 18) & (B >= R - 8) & (B - R < 40)  # 회청색 방울 · 어두운 끝 마디(까만 윤곽선은 빼다)
    return (rod & ~brass) | drop
C = load('cur0.png')
steps = [
    ('E1', 'fit_E1.png', dict(thr=12, color=rod_or_drop)),
    ('E2', 'fit_E2.png', dict(thr=14, dil=4)),
    ('E3', 'fit_E3b.png', 'rect', [(0, 40, 208, 200)]),
    ('E4', 'fit_E4.png', dict(thr=14, dil=4)),
    ('E5', 'fit_E5.png', dict(thr=14, dil=4, keep=[(135, 268, 176, 335), (128, 368, 150, 425)])),
    ('E6', 'fit_E6.png', 'rect', [(8, 330, 166, 536)]),
    ('E7', 'fit_E7.png', dict(thr=14, dil=4)),
    ('E8', 'fit_E8.png', dict(thr=14, dil=4)),
    ('E9', 'fit_E9.png', dict(thr=12, dil=4)),
    ('E10', 'fit_E10.png', dict(thr=14, dil=5, own=[(50, 150, 300, 296)])),
]
for st in steps:
    name, fit = st[0], st[1]
    if st[2] == 'rect':
        M = rectmask(name, st[3]); paste(C, name, fit, M)
    else:
        M, F = diffmask(C, name, fit, **st[2]); paste(C, name, fit, M)
    print('pasted', name, int((M > 0.5).sum()))
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save('cur11.png')
subprocess.run(['python3', '/tmp/b2/tools/zk/u45/floorfix.py', 'cur11.png', 'cur11b.png'], check=True)
print('done cur11b')

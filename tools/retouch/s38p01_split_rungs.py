#!/usr/bin/env python3
"""s38p01 — 사다리 가로대 12개: 가운데 고리(통짜 막대에 끼운 고리 하나)를 지우고 그 자리를 틈으로 끊어
두 조각으로 만든 뒤, 틈을 갈고리로만 잇는다(초록 A-T 둘 · 붉은 G-C 셋).
확대한 두 칸은 제미나이 v2(끊긴 두 조각)에서 옮기고 틈을 넓혀 큰 갈고리를 그린다(초록 둘 · 붉은 셋).
사용: python3 s38p01_split_rungs.py ORIG.png V2.png OUT.png"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

orig_p, v2_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
O = Image.open(orig_p).convert('RGB')
W, H = O.size
assert (W, H) == (1024, 559), (W, H)
a = np.asarray(O).astype(np.float32)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
lum = (R + G + B) / 3
sat = a.max(2) - a.min(2)
red = (R - G > 30) & (R - B > 40) & (lum < 190)
olv = (np.abs(R - G) < 20) & (G - B > 35) & (lum < 185)
gray = (sat < 28) & (lum > 70) & (lum < 170)
gray[330:, 580:] = False
bgm = (lum > 225) & (sat < 45)
yy, xx = np.mgrid[0:H, 0:W]
rng = np.random.default_rng(38)

RINGS = [(109,452),(189,420),(255,388),(326,354),(388,317),(451,289),
         (593,232),(628,197),(678,170),(797,123),(841,95),(895,69)]
SS = 8  # supersampling for strokes
GAP = 11.0   # final gap along the rod
HWB = 9.5    # rod half-width incl. outline (clone band)
RD = 5       # search radius for the ring's dark outline
ink = Image.new('L', (W*SS, H*SS), 0)      # dark stroke alpha
dink = ImageDraw.Draw(ink)
lab, _ = ndi.label(gray)
out = a.copy()
report = []
for cx, cy in RINGS:
    m = ((xx-cx)**2 + (yy-cy)**2) < 30**2
    nr, ng = (red & m).sum(), (olv & m).sum()
    col = 'R' if nr > ng else 'G'
    rod = (red if col == 'R' else olv) & m
    ys, xs = np.nonzero(rod)
    pts = np.stack([xs-cx, ys-cy], 1).astype(float)
    c = pts.mean(0); _, _, vt = np.linalg.svd(pts-c, full_matrices=False)
    d = vt[0] if vt[0][0] > 0 else -vt[0]
    n = np.array([-d[1], d[0]])
    vrod = float(np.median(pts @ n))
    # ring component (gray) + outline: dilate
    k = lab[cy, cx]
    if k == 0:
        # nearest labelled pixel
        sl = lab[cy-6:cy+7, cx-6:cx+7]; k = np.bincount(sl[sl > 0]).argmax()
    ring = lab == k
    ring = ndi.binary_dilation(ring, iterations=3)
    rys, rxs = np.nonzero(ring)
    ru = (rxs-cx)*d[0] + (rys-cy)*d[1]
    rv = (rxs-cx)*n[0] + (rys-cy)*n[1]
    u0 = float((ru.min()+ru.max())/2)
    g = float(ru.max()-ru.min()) + 2          # gap covers the ring's axial thickness
    g = max(g, 13.0)
    vlo, vhi = float(rv.min())-2, float(rv.max())+2
    # erase region E in rod frame
    U = (xx-cx)*d[0] + (yy-cy)*d[1]
    V = (xx-cx)*n[0] + (yy-cy)*n[1]
    core = lab == k
    near = ndi.binary_dilation(core, iterations=RD)
    ringd = core | (near & (lum < 150))
    ringd = ndi.binary_dilation(ringd, iterations=1) & near
    gapb = (np.abs(U-u0) <= GAP/2) & (np.abs(V - vrod) <= HWB)
    E = ringd | gapb
    # background colour: local median of bg-like pixels in annulus
    ann = (((xx-cx)**2 + (yy-cy)**2) < 45**2) & ~E & bgm
    bgc = np.median(a[ann], axis=0)
    noise = rng.normal(0, 2.2, (E.sum(), 3))
    out[E] = np.clip(bgc + noise, 0, 255)
    # rebuild the rod up to a narrow gap gs by cloning intact rod along the axis
    gs = GAP
    band = (np.abs(V - vrod) <= HWB)
    F = E & band & (np.abs(U-u0) > gs/2)
    fy, fx = np.nonzero(F)
    sgn = np.sign(U[fy, fx] - u0)
    shift = (g/2 - gs/2) + 3.0  # g = ring axial extent (dilated) + 2
    sx = fx + sgn*shift*d[0]; sy = fy + sgn*shift*d[1]
    for ch in range(3):
        out[fy, fx, ch] = ndi.map_coordinates(a[..., ch], [sy, sx], order=1)
    g = gs
    # stroke geometry (in supersampled px)
    def P(u, v):
        x = cx + u*d[0] + v*n[0]; y = cy + u*d[1] + v*n[1]
        return (x*SS, y*SS)
    hw = 8.0  # rod half-width for end caps
    for s in (-1, 1):
        ue = u0 + s*g/2
        dink.line([P(ue, vrod-hw), P(ue, vrod+hw)], fill=255, width=int(1.9*SS))
    # hooks
    nh = 2 if col == 'G' else 3
    offs = [-3.4, 3.4] if nh == 2 else [-5.2, 0.0, 5.2]
    for vo in offs:
        v = vrod + vo
        ua, ub = u0 - g/2 + 0.6, u0 + g/2 - 0.6
        # shank from left face across the gap, then a small curl back at the right face (hook tip)
        pts_h = []
        steps = 18
        for i in range(steps+1):
            t = i/steps
            u = ua + (ub-ua-2.2)*t
            pts_h.append(P(u, v - 1.2*math.sin(math.pi*t)))
        # curl: quarter-to-half circle at the right end
        rr = 1.8
        cu, cv = ub - 2.2, v + rr
        for i in range(1, 13):
            th = -math.pi/2 + math.pi*i/12
            pts_h.append(P(cu + rr*math.cos(th), cv + rr*math.sin(th)))
        dink.line(pts_h, fill=255, width=int(1.35*SS), joint='curve')
    report.append((cx, cy, col, round(math.degrees(math.atan2(d[1], d[0])),1), round(u0,1), round(g,1), round(vrod,1), nh))

# ---------- enlarged rungs (lower right): pieces from Gemini v2, gap widened/narrowed to 34 px ----------
V2 = np.asarray(Image.open(v2_p).convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
BX0, BX1, BY0, BY1 = 575, 1012, 332, 530
reg = np.zeros((H, W), bool); reg[BY0:BY1, BX0:BX1] = True
# wipe the old enlarged rungs in the base: flat background + light noise
bgc_big = np.median(a[BY0:BY1, BX0:BX1][bgm[BY0:BY1, BX0:BX1]], axis=0)
old_obj = reg & (np.abs(a - bgc_big).sum(2) > 24)
old_obj = ndi.binary_dilation(old_obj, iterations=3) & reg
out[old_obj] = np.clip(bgc_big + rng.normal(0, 2.0, (old_obj.sum(), 3)), 0, 255)
bg2 = np.median(V2[BY0:BY1, BX0:BX1].reshape(-1, 3), axis=0)
obj2 = reg & (np.abs(V2 - bg2).sum(2) > 24)
obj2 = ndi.binary_fill_holes(ndi.binary_closing(obj2, iterations=2)) & reg
# pieces WITHOUT the little end nubs of v2: (row band, keep-left x<=, keep-right x>=, dx left, dx right, rod top, rod bottom)
XA, XB = 834, 860          # end faces after the shift — 26 px gap
PIECES = [((340, 425), 834, 864, 0, -4, 369, 406),     # green A-T
          ((435, 525), 800, 864, +34, -4, 464, 498)]   # red G-C
endl = Image.new('L', (W*SS, H*SS), 0); dE = ImageDraw.Draw(endl)
for (y0, y1), kl, kr, dxl, dxr, rt, rb in PIECES:
    for side, dx in (('L', dxl), ('R', dxr)):
        m = np.zeros((H, W), bool); m[y0:y1, BX0:BX1] = True
        m &= obj2
        if side == 'L': m[:, kl+1:] = False
        else: m[:, :kr] = False
        ys_, xs2 = np.nonzero(m)
        al_ = ndi.gaussian_filter(m.astype(np.float32), 0.6)
        tx = xs2 + dx
        ok = (tx >= 0) & (tx < W)
        A = al_[ys_[ok], xs2[ok]][:, None]
        SRC = V2[ys_[ok], xs2[ok]]
        if (y0, side) == (435, 'R'):
            # v2 has a pale watermark patch over x 915..950: rod part cloned from 30 px to the left, disc from the original
            xo = xs2[ok]; yo = ys_[ok]
            rodp = (xo >= 912) & (xo < 938)
            SRC[rodp] = V2[yo[rodp], xo[rodp] - 30]
            disc = xo >= 938
            SRC[disc] = a[yo[disc], xo[disc]]
        out[ys_[ok], tx[ok]] = out[ys_[ok], tx[ok]]*(1-A) + SRC*A
    # close the end faces where the nubs were
    dE.line([((XA-0.5)*SS, (rt+1)*SS), ((XA-0.5)*SS, (rb-1)*SS)], fill=255, width=int(2.8*SS))
    dE.line([((XB+0.5)*SS, (rt+1)*SS), ((XB+0.5)*SS, (rb-1)*SS)], fill=255, width=int(2.8*SS))
EL = np.asarray(endl.resize((W, H), Image.LANCZOS)).astype(np.float32)[..., None]/255.0
out = out*(1-EL) + np.array([30, 24, 20], np.float32)*EL
# big hooks across the gaps (green 2 · red 3): dark wire + light core, each curls round a peg on the right face
bigH = Image.new('L', (W*SS, H*SS), 0); dB = ImageDraw.Draw(bigH)
bigC = Image.new('L', (W*SS, H*SS), 0); dC = ImageDraw.Draw(bigC)
def hook(xa, xb, peg_y, dB, dC):
    r = 3.4
    cxh, cyh = xb - 6.5, peg_y
    y = peg_y - r
    pts = [(xa, y)]
    for i in range(1, 17):
        t = i/16; pts.append((xa + (cxh - xa)*t, y))
    for i in range(1, 25):
        th = -math.pi/2 + (math.pi*1.30)*i/24
        pts.append((cxh + r*math.cos(th), cyh + r*math.sin(th)))
    P2 = [(px*SS, py*SS) for px, py in pts]
    dB.line(P2, fill=255, width=int(3.0*SS), joint='curve')
    dC.line(P2, fill=255, width=int(1.0*SS), joint='curve')
    dB.line([(xb*SS, cyh*SS), ((cxh-0.3)*SS, cyh*SS)], fill=255, width=int(2.4*SS))
    hr = 1.6
    dB.ellipse([(cxh-hr)*SS, (cyh-hr)*SS, (cxh+hr)*SS, (cyh+hr)*SS], fill=255)
for py in (382.0, 393.0):
    hook(XA+1.0, XB-1.0, py, dB, dC)
for py in (471.0, 481.0, 491.0):
    hook(XA+1.0, XB-1.0, py, dB, dC)
BL = np.asarray(bigH.resize((W, H), Image.LANCZOS)).astype(np.float32)[..., None]/255.0
CL = np.asarray(bigC.resize((W, H), Image.LANCZOS)).astype(np.float32)[..., None]/255.0
out = out*(1-BL) + np.array([44, 42, 44], np.float32)*BL
out = out*(1-CL*0.55) + np.array([150, 150, 155], np.float32)*(CL*0.55)

inkL = ink.resize((W, H), Image.LANCZOS)
al = np.asarray(inkL).astype(np.float32)[..., None] / 255.0
INK = np.array([38, 34, 32], np.float32)
out = out*(1-al) + INK*al
res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
res.save(out_p)
for r in report: print(r)

# L17a picture fix — rebuilds final_new.png from the original (read only).
#   item 1  station 8 porter: three white sacks -> two (the middle and bottom shoulder sacks are
#           merged into one fat sack: their dividing outline is removed, a new right edge drawn)
#   item 2a station 3 net: thorns on every net line and on the top rope (barbed-wire look)
#   item 2b station 3 balls: the three bouncing spiky balls shrunk in place (body ~41 -> ~24 px),
#           their spikes redrawn bolder at the old spike angles so they still read as spiky
# usage: python3 fix.py   (writes final_new.png next to this script)
import os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
from skimage.morphology import skeletonize

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = SP + '/L17a/r1/final_v1.png'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'final_new.png')


# ----------------------------------------------------------------------------------------- helpers
def lum(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def pl_dist(px, py, pl):
    d = np.full(np.shape(px), 1e9)
    for (x1, y1), (x2, y2) in zip(pl[:-1], pl[1:]):
        vx, vy = x2 - x1, y2 - y1
        L2 = vx * vx + vy * vy
        t = np.clip(((px - x1) * vx + (py - y1) * vy) / max(L2, 1e-9), 0, 1)
        d = np.minimum(d, np.hypot(px - (x1 + t * vx), py - (y1 + t * vy)))
    return d


def stroke_alpha(pl, width, x0, y0, w, h, ss=8):
    yy, xx = np.mgrid[0:h * ss, 0:w * ss]
    px = x0 + (xx + 0.5) / ss - 0.5
    py = y0 + (yy + 0.5) / ss - 0.5
    d = pl_dist(px, py, pl)
    a = (d <= width / 2).astype(float)
    return a.reshape(h, ss, w, ss).mean(axis=(1, 3))


def poly_mask(poly, x0, y0, w, h, ss=8):
    im = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(im).polygon([((x - x0 + 0.5) * ss, (y - y0 + 0.5) * ss) for x, y in poly], fill=255)
    return np.array(im.resize((w, h), Image.BOX)).astype(float) / 255


def harmonic_fill(win, D, known, iters=3000):
    """fill D by Laplace relaxation; neighbours that are neither D nor known are ignored"""
    out = win.copy()
    usable = D | known
    out[D] = win[known].mean(axis=0)
    H, W = D.shape
    for _ in range(iters):
        acc = np.zeros_like(out)
        cnt = np.zeros(D.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            src = np.zeros_like(out)
            ok = np.zeros(D.shape, bool)
            ys = slice(max(dy, 0), H + min(dy, 0))
            yd = slice(max(-dy, 0), H + min(-dy, 0))
            xs = slice(max(dx, 0), W + min(dx, 0))
            xd = slice(max(-dx, 0), W + min(-dx, 0))
            src[yd, xd] = out[ys, xs]
            ok[yd, xd] = usable[ys, xs]
            acc += src * ok[..., None]
            cnt += ok
        nv = acc / np.maximum(cnt, 1)[..., None]
        out[D] = nv[D]
    return out


def harmonic_solve(win, D, known, tether=None, eps=1e-3):
    """exact Laplace fill of D (sparse solve); boundary values from 'known' neighbours, others ignored;
    a very weak pull towards 'tether' keeps pockets without a known neighbour defined"""
    H, W = D.shape
    idx = -np.ones(D.shape, int)
    ys, xs = np.nonzero(D)
    idx[ys, xs] = np.arange(len(ys))
    n = len(ys)
    A = lil_matrix((n, n))
    b = np.zeros((n, 3))
    for k, (y, x) in enumerate(zip(ys, xs)):
        deg = 0
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if not (0 <= yy < H and 0 <= xx < W):
                continue
            if D[yy, xx]:
                A[k, idx[yy, xx]] = -1
                deg += 1
            elif known[yy, xx]:
                b[k] += win[yy, xx]
                deg += 1
        A[k, k] = deg + eps
        if tether is not None:
            b[k] += eps * tether
    A = A.tocsr()
    out = win.copy()
    out[ys, xs] = np.stack([spsolve(A, b[:, c]) for c in range(3)], 1)
    return out


# ------------------------------------------------------------------ item 1: station 8 sacks 3 -> 2
SX0, SY0, SX1, SY1 = 1752, 486, 1848, 556
# bottom outline of the middle sack (face outline -> its right tip)
SACK_M = [(1762.0, 518.0), (1769.5, 520.6), (1780.5, 527.5), (1782.7, 530.3), (1786.6, 530.3),
          (1789.5, 526.5), (1796.6, 526.5), (1808.7, 523.3), (1820.3, 516.4), (1830.5, 510.4)]
# upper-right edge of the bottom sack (junction -> bottom tip)
SACK_B = [(1821.0, 516.0), (1826.0, 521.0), (1830.0, 525.0), (1833.5, 529.0)]
# new right edge of the merged sack: upper tip -> shallow notch -> lower tip
SACK_NEW = [(1831.6, 508.2), (1830.4, 511.8), (1829.4, 515.5), (1829.3, 519.2),
            (1830.3, 523.0), (1832.1, 526.9), (1833.7, 529.3)]
SACK_EDGE_W = 3.3


def fix_sack(a):
    a = a.astype(float).copy()
    X0, Y0, X1, Y1 = SX0, SY0, SX1, SY1
    win = a[Y0:Y1, X0:X1].copy()
    h, w = win.shape[:2]
    L = lum(win)
    yy, xx = np.mgrid[0:h, 0:w]
    PX = (xx + X0).astype(float)
    PY = (yy + Y0).astype(float)
    sat = win.max(axis=2) - win.min(axis=2)
    dM = pl_dist(PX, PY, SACK_M)
    dB = pl_dist(PX, PY, SACK_B)
    band = ((dM <= 2.4) | ((dM <= 4.2) & (L < 185))) & (PX >= 1764.5)
    band |= ((dB <= 2.4) | ((dB <= 4.2) & (L < 185))) & (PY <= 526.5) & (PX <= 1831.5)
    notch_poly = [(1820.3, 516.4), (1830.5, 510.4)] + SACK_NEW[1:] + [(1833.5, 529.0), (1830.0, 525.0),
                                                                    (1826.0, 521.0), (1821.0, 516.0)]
    notch = poly_mask(notch_poly, X0, Y0, w, h) > 0.01
    D = band | notch
    dN = pl_dist(PX, PY, SACK_NEW)
    ys_new = np.array([p[1] for p in SACK_NEW])
    xs_new = np.array([p[0] for p in SACK_NEW])
    x_edge = np.interp(PY, ys_new, xs_new)
    right_of_new = (PY >= ys_new[0]) & (PY <= ys_new[-1]) & (PX > x_edge + 0.6) & (dN > 1.0)
    D &= ~right_of_new
    D &= (PX >= 1764.5)
    known = (~D) & (sat < 32) & (L > 150)          # sack white / light grey only
    filled = harmonic_fill(win, D, known)
    al = stroke_alpha(SACK_NEW, SACK_EDGE_W, X0, Y0, w, h)
    ink = np.array([8.0, 7.0, 6.0])
    a[Y0:Y1, X0:X1] = filled * (1 - al[..., None]) + ink * al[..., None]
    return a


# --------------------------------------------------------- item 2b: station 3 balls shrunk in place
BALLS = {'A': (885.1, 312.5), 'B': (737.8, 370.5), 'C': (580.9, 494.9)}
SCALE = 0.58       # body (outer edge of the ring) 41.6 px -> 24.1 px
R_BODY = 20.8
R_OUT = 31.0
SPIKE_GEO = 10
R_CUT = 23.8
MARGIN = 40


def ball_spike_alpha(r, PX, PY, cx, cy, spikes, s, x0, y0, w, h, ss=8, gap=40.0, base=2.4):
    """one tapered spike per old spike (same angle; gaps wider than 'gap' degrees filled evenly),
    so the smaller ball stays visibly spiky"""
    lab, n = ndi.label(spikes & (r > R_BODY + 0.8), structure=np.ones((3, 3)))
    sp = []
    for i in range(1, n + 1):
        c = lab == i
        if c.sum() < 2:
            continue
        ang = np.degrees(np.arctan2((PY[c] - cy).mean(), (PX[c] - cx).mean()))
        sp.append((ang % 360, r[c].max()))
    sp.sort()
    full = []
    for k, (ang, rm) in enumerate(sp):
        full.append((ang, rm))
        nxt = sp[(k + 1) % len(sp)][0] + (360 if k == len(sp) - 1 else 0)
        g = nxt - ang
        if g > gap:
            m = int(round(g / 25.0)) - 1
            for j in range(1, m + 1):
                full.append(((ang + g * j / (m + 1)) % 360, R_BODY + 3.0))
    rr = s * R_BODY
    lay = Image.new('L', (w * ss, h * ss), 0)
    d = ImageDraw.Draw(lay)
    for ang, rm in full:
        t = np.radians(ang)
        ux, uy = np.cos(t), np.sin(t)
        nx, ny = -uy, ux
        Lt = float(np.clip(0.6 * (rm - R_BODY) + 1.8, 3.0, 4.5))
        bx, by = cx + ux * (rr - 1.0), cy + uy * (rr - 1.0)
        tx, ty = cx + ux * (rr + Lt), cy + uy * (rr + Lt)
        pts = [(bx - nx * base / 2, by - ny * base / 2), (tx, ty), (bx + nx * base / 2, by + ny * base / 2)]
        d.polygon([((x - x0 + 0.5) * ss, (y - y0 + 0.5) * ss) for x, y in pts], fill=255)
    return np.array(lay.resize((w, h), Image.BOX)).astype(float) / 255


def shrink_ball(a, cx, cy, s=SCALE, seed=0):
    a = a.astype(float).copy()
    x0, y0 = int(cx) - MARGIN, int(cy) - MARGIN
    x1, y1 = int(cx) + MARGIN + 1, int(cy) + MARGIN + 1
    win = a[y0:y1, x0:x1].copy()
    h, w = win.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    PX = xx + x0
    PY = yy + y0
    r = np.hypot(PX - cx, PY - cy)
    L = lum(win)
    ann = (r > 28) & (r < 36)
    med = np.median(win[ann], axis=0)
    bglike = np.abs(win - med).max(axis=2) < 18
    bg = win[ann & bglike].mean(axis=0)
    Lbg = lum(bg[None, None, :])[0, 0]
    # old ball alpha: disc (body + ring) + dark spikes grown from the ring
    a_disc = np.clip(R_BODY + 0.5 - r, 0, 1)
    dark = (L < Lbg - 45) & (r <= R_OUT)
    grown = r <= R_BODY
    for _ in range(SPIKE_GEO):
        grown = grown | (ndi.binary_dilation(grown, structure=np.ones((3, 3))) & dark)
    spikes = grown & (r > R_BODY - 1)
    spikes_soft = ndi.binary_dilation(spikes, iterations=1) & (r <= R_OUT + 0.8)
    a_dark = np.clip((Lbg - L) / (Lbg - 15.0), 0, 1) * spikes_soft
    M = np.maximum(a_disc, a_dark)
    foot = (r <= R_BODY + 0.5) | spikes
    dfoot = ndi.distance_transform_edt(~foot)
    fz = np.kron(foot, np.ones((4, 4), bool))
    dfoot_s = ndi.distance_transform_edt(~fz)[1::4, 1::4] / 4.0 + 0.4
    # streaks / lines that reach away from the ball are kept (cut cleanly near the old ball)
    far = np.abs(win - bg).max(axis=2) > 28
    flab, fn = ndi.label(far & (dfoot > 0.5), structure=np.ones((3, 3)))
    feat = np.zeros_like(far)
    for i in range(1, fn + 1):
        comp = flab == i
        if dfoot[comp].max() <= 7.5:
            continue
        g2 = comp & (dfoot > 6.0)
        for _ in range(5):
            g2 = g2 | (ndi.binary_dilation(g2, structure=np.ones((3, 3))) & comp)
        feat |= g2 | (comp & (dfoot > 4.0))
    feat = ndi.binary_dilation(feat, structure=np.ones((3, 3)))
    keep = feat * np.clip(r - R_CUT + 0.5, 0, 1) * np.clip(dfoot_s - 3.0 + 0.5, 0, 1)
    keep[(L < Lbg - 45) & (dfoot <= 4.0)] = 0
    # repaint the old ball + its light fringe + faint shading ring (up to 7 px out)
    D = (dfoot <= 7.0) | (r <= R_BODY + 4.5)
    tol = np.abs(win - bg).max(axis=2) < 14
    known = (~D) & tol & ~feat
    fill = harmonic_solve(win, D & ~(keep >= 1), known, tether=bg)
    dist = ndi.distance_transform_edt(~D)
    rng = np.random.default_rng(seed)
    hp = win - ndi.median_filter(win, size=(3, 3, 1))
    sel = (dist >= 2) & (dist <= 10) & tol
    sd = hp[sel].std(axis=0)
    g = rng.normal(0, 1, D.sum())
    e = rng.normal(0, 1, (D.sum(), 3))
    fill[D] += (0.8 * g[:, None] + 0.6 * e) * sd
    # smaller ball: area-sampled minification of the premultiplied ball layer, same centre
    P = win * M[..., None]
    ss = 5
    acc = np.zeros((h, w, 3))
    accm = np.zeros((h, w))
    for i in range(ss):
        for j in range(ss):
            ox = (j + 0.5) / ss - 0.5
            oy = (i + 0.5) / ss - 0.5
            sx = cx + ((PX + ox) - cx) / s - x0
            sy = cy + ((PY + oy) - cy) / s - y0
            for c in range(3):
                acc[..., c] += ndi.map_coordinates(P[..., c], [sy, sx], order=1, mode='constant', cval=0)
            accm += ndi.map_coordinates(M, [sy, sx], order=1, mode='constant', cval=0)
    P2 = acc / ss ** 2
    M2 = accm / ss ** 2
    out = P2 + (1 - M2)[..., None] * fill
    al = ball_spike_alpha(r, PX, PY, cx, cy, spikes, s, x0, y0, w, h)
    ink = np.median(win[(r > R_BODY - 3.5) & (r < R_BODY) & (L < 60)], axis=0)
    out = out * (1 - al[..., None]) + ink * al[..., None]
    res = win.copy()
    kk = keep[..., None]
    res[D] = (kk * win + (1 - kk) * out)[D]
    a[y0:y1, x0:x1] = res
    return a


def fix_balls(a):
    out = a.astype(float)
    for k, name in enumerate('ABC'):
        cx, cy = BALLS[name]
        out = shrink_ball(out, cx, cy, seed=17 + k)
    return out


# --------------------------------------------------------- item 2a: thorns on the net (barbed wire)
NX0, NY0, NX1, NY1 = 436, 326, 1004, 664
MESH_POLY = [(452, 546), (520, 539), (600, 522), (700, 492), (800, 456), (900, 408), (962, 363),
             (976, 352), (978, 470), (950, 482), (920, 496), (880, 510), (840, 524), (800, 538),
             (760, 554), (720, 570), (680, 587), (640, 603), (600, 624), (560, 642), (530, 652),
             (500, 650), (468, 634), (452, 612)]
EXCL_BANK = [(944, 447), (970, 410), (1004, 410), (1004, 520), (960, 520), (930, 452)]
GRASS_EDGE = [(466, 568), (476, 588), (483.5, 600), (489.5, 612), (497, 624), (503, 633), (510, 642),
              (515, 648), (521, 654), (528, 660), (536, 668)]
ROPE_ROUGH = [(452, 543), (500, 538), (550, 531), (600, 520), (650, 506), (700, 491), (750, 474),
              (800, 455), (850, 432), (900, 406), (950, 376), (968, 362)]
THORN_INK = np.array([2.0, 5.0, 11.0])


def poly_fill(poly, x0, y0, w, h):
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).polygon([(x - x0, y - y0) for x, y in poly], fill=255)
    return np.array(im) > 0


def mesh_segments(a):
    L = lum(a.astype(float))
    x0, y0, x1, y1 = NX0, NY0, NX1, NY1
    w, h = x1 - x0, y1 - y0
    ink = L[y0:y1, x0:x1] < 105
    region = poly_fill(MESH_POLY, x0, y0, w, h)
    dt = ndi.distance_transform_edt(ink)
    thick = ndi.binary_dilation(dt >= 2.6, iterations=3) & ink
    thin = ink & ~thick & region
    sk = skeletonize(thin)
    k = np.ones((3, 3), int)
    nb = ndi.convolve(sk.astype(int), k, mode='constant') - sk
    junc = sk & (nb >= 3)
    jz = ndi.binary_dilation(junc, iterations=3)
    parts = sk & ~jz
    lab, n = ndi.label(parts, structure=np.ones((3, 3)))
    segs = []
    for i in range(1, n + 1):
        yy, xx = np.nonzero(lab == i)
        if len(xx) < 5:
            continue
        P = np.stack([xx + x0, yy + y0], 1).astype(float)
        c = P.mean(0)
        U, S, Vt = np.linalg.svd(P - c, full_matrices=False)
        d = Vt[0]
        if d[0] < 0:
            d = -d
        t = (P - c) @ d
        res = np.abs((P - c) @ np.array([-d[1], d[0]]))
        ang = np.degrees(np.arctan2(d[1], d[0]))
        segs.append(dict(c=c, d=d, tmin=t.min(), tmax=t.max(), len=t.max() - t.min(), ang=ang, res=res.max()))
    return segs


def family(ang):
    if 12 <= ang <= 48:
        return 'A'
    if -78 <= ang <= -38:
        return 'B'
    return None


def inside(poly, x, y):
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            c = not c
        j = i
    return c


def pl_dist1(x, y, pl):
    best = 1e9
    for (x1, y1), (x2, y2) in zip(pl[:-1], pl[1:]):
        vx, vy = x2 - x1, y2 - y1
        t = min(max(((x - x1) * vx + (y - y1) * vy) / (vx * vx + vy * vy), 0), 1)
        best = min(best, np.hypot(x - (x1 + t * vx), y - (y1 + t * vy)))
    return best


def rope_centre(a, x_from=456, x_to=966):
    L = lum(a.astype(float))
    xr = np.array([p[0] for p in ROPE_ROUGH], float)
    yr = np.array([p[1] for p in ROPE_ROUGH], float)
    xs, ys = [], []
    for x in range(x_from, x_to + 1):
        y0 = np.interp(x, xr, yr)
        col = L[int(y0) - 12:int(y0) + 13, x]
        dark = col < 80
        best = None
        i = 0
        while i < len(dark):
            if dark[i]:
                j = i
                while j < len(dark) and dark[j]:
                    j += 1
                mid = (i + j - 1) / 2 + int(y0) - 12
                if best is None or (j - i) > best[0] + 1 or ((j - i) >= best[0] - 1 and abs(mid - y0) < abs(best[1] - y0)):
                    best = (j - i, mid)
                i = j
            else:
                i += 1
        if best is not None and best[0] >= 4:
            xs.append(x)
            ys.append(best[1])
    xs = np.array(xs, float)
    ys = np.array(ys, float)
    ysm = ndi.median_filter(ys, size=9, mode='nearest')
    ysm = ndi.uniform_filter1d(ysm, size=7, mode='nearest')
    return xs, ysm


def mesh_thorn_sites(segs, min_len=5.0, spacing=13.0):
    out = []
    for s in segs:
        f = family(s['ang'])
        if f is None or s['res'] > 1.6 or s['len'] < min_len:
            continue
        c, d = s['c'], s['d']
        if inside(EXCL_BANK, c[0], c[1]):
            continue
        n = max(1, int(round(s['len'] / spacing)))
        for k in range(n):
            t = s['tmin'] + (k + 0.5) * (s['tmax'] - s['tmin']) / n
            p = c + d * t
            if pl_dist1(p[0], p[1], GRASS_EDGE) < 5.0:
                continue
            out.append((p[0], p[1], d[0], d[1]))
    keep = []
    for p in out:
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= 8.0 ** 2 for q in keep):
            keep.append(p)
    return keep


def rope_thorn_sites(xs, ys, step=14.0, x_from=462, x_to=962):
    m = (xs >= x_from) & (xs <= x_to)
    P = np.stack([xs[m], ys[m]], 1)
    seg = np.hypot(*np.diff(P, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    out = []
    t = step * 0.5
    while t < cum[-1] - 2:
        i = int(np.clip(np.searchsorted(cum, t) - 1, 0, len(P) - 2))
        f = (t - cum[i]) / max(seg[i], 1e-6)
        p = P[i] + f * (P[i + 1] - P[i])
        j0, j1 = max(i - 5, 0), min(i + 6, len(P) - 1)
        dd = P[j1] - P[j0]
        dd = dd / np.hypot(*dd)
        out.append((p[0], p[1], dd[0], dd[1]))
        t += step
    return out


def thorn(d, cx, cy, ux, uy, length, base, ss, ox, oy):
    nx, ny = -uy, ux
    b = base / 2
    pts = [(cx - nx * b, cy - ny * b), (cx + ux * length, cy + uy * length), (cx + nx * b, cy + ny * b),
           (cx - ux * b * 0.6, cy - uy * b * 0.6)]
    d.polygon([((x - ox + 0.5) * ss, (y - oy + 0.5) * ss) for x, y in pts], fill=255)


def thorn_alpha(src, mesh_len=7.0, mesh_base=2.8, rope_len=9.0, rope_base=3.6, ss=6):
    """thorns alternate sides along each line, slightly swept (rose-stem / barbed-wire look)"""
    x0, y0, x1, y1 = NX0, NY0, NX1, NY1
    lay = Image.new('L', ((x1 - x0) * ss, (y1 - y0) * ss), 0)
    d = ImageDraw.Draw(lay)

    def rot(ux, uy, deg):
        t = np.radians(deg)
        return ux * np.cos(t) - uy * np.sin(t), ux * np.sin(t) + uy * np.cos(t)

    msites = mesh_thorn_sites(mesh_segments(src))
    for (cx, cy, ux, uy) in msites:
        for off, ang in ((-3.2, 70), (3.2, -70)):
            vx, vy = rot(ux, uy, ang)
            thorn(d, cx + ux * off, cy + uy * off, vx, vy, mesh_len, mesh_base, ss, x0, y0)
    xs, ys = rope_centre(src)
    rsites = rope_thorn_sites(xs, ys)
    for (cx, cy, ux, uy) in rsites:
        for off, ang in ((-3.5, 70), (3.5, -70)):
            vx, vy = rot(ux, uy, ang)
            thorn(d, cx + ux * off, cy + uy * off, vx, vy, rope_len, rope_base, ss, x0, y0)
    al = np.array(lay.resize((x1 - x0, y1 - y0), Image.BOX)).astype(float) / 255
    return al, len(msites), len(rsites)


def add_thorns(a, src):
    al, nm, nr = thorn_alpha(src)
    out = a.astype(float).copy()
    reg = out[NY0:NY1, NX0:NX1]
    out[NY0:NY1, NX0:NX1] = reg * (1 - al[..., None]) + THORN_INK * al[..., None]
    return out, nm, nr


# ------------------------------------------------------------------------------------------ main
if __name__ == '__main__':
    src = np.array(Image.open(SRC).convert('RGB'))
    assert src.shape == (1144, 2048, 3)
    out = fix_sack(src)
    out = fix_balls(out)
    out, nm, nr = add_thorns(out, src)        # thorn positions are read from the original
    res = np.clip(np.round(out), 0, 255).astype(np.uint8)
    Image.fromarray(res, 'RGB').save(OUT)
    print('saved', OUT, res.shape, 'mesh thorn sites', nm, 'rope thorn sites', nr)

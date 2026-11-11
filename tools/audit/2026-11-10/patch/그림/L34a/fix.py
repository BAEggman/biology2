# -*- coding: utf-8 -*-
"""L34a picture fix — PIL / numpy / cv2 only.
Rebuilds  SP/picfix/L34a/final_new.png  from the read-only original  SP/L34a/r1/final_v1.png.

Item 1: the coat figure on the upper workbench had TWO heads coming out of one coat.
        -> keep the left head (the front one, complete outline), erase both heads,
           paste the kept head centred over the V of the collar (dx = +17 px),
           wall colour where the heads were, re-ink the edges that were cut
           (collar tops, white shirt-collar tops, chin, right ear + jaw) and lower the
           two collar tips (they were hidden against the old jaws) into rounded shoulders.
Item 2: lower floor, the two arch rims.  Inside the light voussoir band (with its own shaded inner
        face) the dark barrel band was cut into three strands (bricks | bricks | smooth) by two thick
        double lines: L2 and the pair L3+L4.  -> those three thick lines are traced and replaced by
        ordinary thin mortar joints (same width/tone as the other brick joints), so the rim reads as
        exactly two layers: one light stone band + one dark band.  Ends stop where cannons / log hide
        them; at the crown, where each line runs into the voussoir edge, the new line widens back to
        the old thickness and the last few px stay original (they merge into the voussoir edge).
        The voussoir edge (L0) and the stones' shaded inner face (L1) are not touched.
Coordinates: original 2048x1144 pixel grid, pixel centres at integers.
"""
import os
import numpy as np, cv2
from PIL import Image, ImageDraw

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = SP + '/L34a/r1/final_v1.png'
OUTDIR = SP + '/picfix/L34a'

A = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)

SS = 8   # every drawn mask is rendered 8x larger and averaged down (anti-aliasing)


class ROI:
    def __init__(s, x0, y0, x1, y1):
        s.x0, s.y0, s.x1, s.y1 = x0, y0, x1, y1
        s.w, s.h = x1 - x0, y1 - y0

    def _map(s, P):
        P = np.asarray(P, float)
        return np.stack([(P[:, 0] - s.x0 + 0.5) * SS, (P[:, 1] - s.y0 + 0.5) * SS], 1)

    def _down(s, m):
        return m.reshape(s.h, SS, s.w, SS).mean((1, 3))

    def poly(s, pts):
        im = Image.new('L', (s.w * SS, s.h * SS), 0)
        ImageDraw.Draw(im).polygon([tuple(p) for p in s._map(pts)], fill=255)
        return s._down(np.asarray(im, np.float32) / 255.0)

    def stroke(s, pts, width):
        P = np.asarray(pts, float)
        w = np.full(len(P), float(width)) if np.isscalar(width) else np.asarray(width, float)
        q = s._map(P)
        im = np.zeros((s.h * SS, s.w * SS), np.uint8)
        for (x, y), ww in zip(q, w):
            cv2.circle(im, (int(round(x * 16)), int(round(y * 16))), max(1, int(round(ww * SS / 2 * 16))),
                       255, -1, lineType=cv2.LINE_8, shift=4)
        return s._down(im.astype(np.float32) / 255.0)


def spline(ctrl, step=0.1):
    """Catmull-Rom through the control points, resampled every ~step px."""
    P = np.asarray(ctrl, float)
    E = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(E) - 2):
        p0, p1, p2, p3 = E[i - 1], E[i], E[i + 1], E[i + 2]
        n = max(2, int(np.hypot(*(p2 - p1)) / step))
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-1])
    return np.array(out)


def ramp(n, a=0, b=0, lo=0.45):
    f = np.ones(n)
    if a:
        f[:a] = np.linspace(lo, 1, a)
    if b:
        f[-b:] = np.minimum(f[-b:], np.linspace(1, lo, b))
    return f


def over(base, col, m):
    m = np.clip(m, 0, 1)[..., None]
    return base * (1 - m) + np.asarray(col, np.float32) * m


INK = np.array([12.0, 6.0, 3.0])        # outline core colour (median of the darkest outline pixels)
BG = np.array([246.0, 235.0, 189.0])    # wall colour around the heads (median, std < 1.4)
HALO = BG + np.array([5.0, 10.0, 26.0])  # the thin light ring every outline has against the wall
SKIN = np.array([241.0, 196.0, 166.0])  # face skin (cheek median)
LW = 2.45                               # outline width (measured 2.4-2.8 px, soft)
BLUR = 0.5                              # outline softness (the original lines are not razor sharp)


def wall(h, w, seed):
    rng = np.random.default_rng(seed)
    return BG[None, None, :] + rng.normal(0, 1, (h, w, 3)) * np.array([0.6, 0.35, 1.2])


def soft(m, s=BLUR):
    return np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), s), 0, 1)


# ================================================================== item 1 : one head
DX = 17
R1 = ROI(1226, 118, 1350, 204)

# kept head = left head, its outline cut tight (core + ~0.8 px) where it touched other things
S_POLY = [(1234, 122), (1288.4, 122), (1288.4, 157.5), (1289.3, 160.0), (1289.2, 163.0),
          (1288.3, 165.5), (1287.2, 167.5), (1285.5, 169.0), (1283.5, 170.2), (1281.6, 171.2),
          (1281.4, 175.2), (1280.4, 177.8), (1279.0, 179.2), (1277.7, 180.6), (1276.8, 182.0),
          (1276.2, 183.6), (1275.1, 184.8), (1273.6, 186.3), (1272.0, 187.3), (1270.4, 188.3),
          (1268.2, 189.4), (1265.0, 189.6), (1262.0, 190.1), (1259.4, 188.6), (1257.4, 187.1),
          (1255.4, 185.1), (1254.4, 183.9), (1252.8, 181.3), (1251.6, 179.4), (1250.4, 177.2),
          (1249.7, 175.1), (1249.2, 172.0), (1246.0, 169.0), (1240.0, 160.0), (1234.0, 150.0)]

# --- centre lines (final coordinates) -------------------------------------------------------
# left collar: outer corner -> lowered, rounded top (old tip was at 1252.5,179.5) -> V corner
C_LEFT = [(1243.7, 192.0), (1244.3, 189.6), (1246.0, 187.8), (1248.0, 186.4), (1250.5, 185.4),
          (1253.0, 185.0), (1255.3, 185.4), (1257.3, 186.4), (1259.5, 187.6), (1262.0, 189.3)]
# white shirt-collar top (left), from the V corner up to where it meets the new chin
C_SHIRT_L = [(1262.0, 189.3), (1265.0, 188.8), (1268.0, 188.6), (1270.0, 187.6), (1271.5, 186.6),
             (1273.0, 185.6)]
# right: white shirt-collar top, collar top, lowered rounded corner (old tip 1321,181), outer edge
C_RIGHT = [(1294.8, 179.4), (1296.0, 182.0), (1298.0, 184.5), (1300.0, 186.5), (1302.0, 188.4),
           (1304.0, 189.4), (1306.0, 190.6), (1308.0, 191.0), (1310.0, 190.9), (1312.0, 190.4),
           (1314.0, 189.4), (1316.0, 188.4), (1318.0, 187.6), (1320.0, 187.1), (1322.0, 187.1),
           (1324.0, 187.9), (1325.6, 189.4), (1326.6, 191.4), (1327.5, 193.4)]
# new head lower outline + right ear (old coordinates of the kept head, shifted by DX)
CHIN_OLD = [(1249.9, 172.5), (1250.5, 175.0), (1251.2, 177.0), (1252.3, 179.0), (1253.5, 180.6),
            (1255.0, 183.3), (1256.0, 184.5), (1258.0, 186.5), (1260.0, 188.0), (1262.0, 189.4),
            (1265.0, 188.8), (1268.0, 188.6), (1270.0, 187.5), (1271.5, 186.5), (1273.0, 185.5),
            (1274.5, 184.0), (1275.5, 183.0), (1276.0, 181.5), (1277.0, 180.0), (1278.3, 178.5),
            (1279.5, 177.0), (1280.5, 175.0), (1280.6, 171.5), (1280.9, 170.0)]
# ear, final coordinates: small C under the hair, like the ears of the red-vest pair
EAR = [(1297.9, 169.6), (1299.6, 168.7), (1301.3, 167.4), (1302.6, 165.6), (1303.2, 163.4),
       (1303.1, 161.2), (1302.3, 159.3), (1300.9, 157.9), (1299.3, 157.0)]
EAR_IN = [(1300.2, 160.2), (1301.2, 162.0), (1301.1, 164.0), (1300.0, 165.6)]


def fix_heads(img):
    R = R1
    src = A[R.y0:R.y1, R.x0:R.x1].copy()
    cur = img[R.y0:R.y1, R.x0:R.x1].copy()

    # only pixels that are not plain wall (+2 px) are touched, so the wall around stays bit-identical
    nonbg = (np.abs(src - BG[None, None, :]).max(-1) > 7).astype(np.uint8)
    near = cv2.dilate(nonbg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))).astype(np.float32)
    Ms = R.poly(S_POLY) * near
    Ms_new = np.zeros_like(Ms); Ms_new[:, DX:] = Ms[:, :-DX]
    spr = np.zeros_like(src); spr[:, DX:] = src[:, :-DX]

    # erase region: everything above the (new) collar / shirt top lines -> wall
    low = (spline(C_LEFT, 0.5).tolist() + spline(C_SHIRT_L, 0.5).tolist()
           + [(1276.0, 182.0), (1286.0, 182.0), (1293.5, 177.5)]
           + spline(C_RIGHT, 0.5).tolist()
           + [(1329.4, 192.6), (1332.0, 190.5), (1350, 190.5), (1350, 118), (1235, 118), (1235, 187.0),
              (1240.8, 188.4), (1242.6, 191.0)])
    Em = R.poly(low) * near

    out = cur * (1 - Em[..., None]) + wall(R.h, R.w, 7) * Em[..., None]
    out = out * (1 - Ms_new[..., None]) + spr * Ms_new[..., None]

    # ear: skin interior (old ear pixels were grey-pink) keeping their light/dark pattern
    ear_poly = EAR + [(1297.6, 157.4), (1297.2, 169.6)]
    Mear = R.poly(ear_poly) * Ms_new
    Lum = out @ np.array([0.299, 0.587, 0.114], np.float32)
    Lskin = SKIN @ np.array([0.299, 0.587, 0.114])
    tinted = np.clip(SKIN[None, None, :] * np.clip(Lum / Lskin, 0.55, 1.05)[..., None], 0, 255)
    out = out * (1 - Mear[..., None]) + tinted * Mear[..., None]
    # area outside the new ear but inside the pasted sprite near the ear (old greyish pixels) -> wall
    ear_out = R.poly([(1299.3, 156.2), (1306.5, 156.2), (1306.5, 171.0), (1297.0, 171.0)]) \
        * (1 - R.poly(ear_poly + [(1297.0, 171.0)]))
    out = out * (1 - ear_out[..., None]) + wall(R.h, R.w, 11) * ear_out[..., None]

    # ink
    chin = spline([(x + DX, y) for x, y in CHIN_OLD])
    ear = spline(EAR)
    ear_in = spline(EAR_IN)
    sl = spline(C_SHIRT_L)
    items = [(spline(C_LEFT), LW), (sl, LW * ramp(len(sl), b=8, lo=0.7)), (spline(C_RIGHT), LW),
             (chin, LW * ramp(len(chin), a=25, lo=0.6)), (ear, LW * 0.95)]
    ink = np.zeros((R.h, R.w), np.float32)
    halo = np.zeros((R.h, R.w), np.float32)
    for P, w in items:
        ink = np.maximum(ink, R.stroke(P, w))
        halo = np.maximum(halo, R.stroke(P, np.asarray(w) + 3.6))
    ink = soft(ink)
    wallzone = np.clip(np.maximum(Em - Ms_new, ear_out), 0, 1)
    halo = soft(np.clip(halo - ink, 0, 1) * wallzone, 0.6)
    out = over(out, HALO, halo)
    out = over(out, INK, ink)
    inner = soft(R.stroke(ear_in, 1.1), 0.45)
    out = over(out, (150.0, 95.0, 70.0), inner * 0.85)

    img = img.copy()
    img[R.y0:R.y1, R.x0:R.x1] = out
    return img


# ================================================================== item 2 : arch rims
LUM = np.array([0.299, 0.587, 0.114], np.float32)
JOINT_INK = np.array([24.0, 19.0, 13.0])   # colour of the thin brick joints (core)


def runs1d(v, thr=70.0):
    out = []
    i = 0; n = len(v)
    while i < n:
        if v[i] < thr:
            j = i
            while j < n and v[j] < thr:
                j += 1
            w = np.clip(110.0 - v[i:j], 1, None)
            out.append((i, j - 1, i + float((np.arange(j - i) * w).sum() / w.sum())))
            i = j
        else:
            i += 1
    return out


def scan_line(L, axis, coords, start, lo, hi, maxjump=2.5, maxw=6, thr=70.0, slope0=0.0, top=False):
    """follow one thick line row by row (axis='row', position = x) or column by column (position = y);
    the position is predicted from the local slope so T-joints / crossings do not derail it"""
    coords = list(coords)
    pos = float(start); slope = float(slope0); last_c = coords[0]; hist = [(coords[0], pos)]
    out = []
    for c in coords:
        pred = pos + slope * (c - last_c)
        gap = abs(c - last_c)
        prof = L[c, lo:hi] if axis == 'row' else L[lo:hi, c]
        best = None
        mw = maxw * np.sqrt(1 + slope * slope)          # a slanted line crosses more pixels
        for a, b, cen in runs1d(prof, thr):
            if top:
                # the voussoir edge: other lines merge into it from BELOW, so take the upper
                # edge of the topmost dark run (+2.5 px = centre of a 5 px line)
                p = lo + a + 2.5
                d = abs(p - pred)
                if b - a + 1 <= 20 and d <= maxjump + 0.6 * max(0, gap - 1) and (best is None or p < best[1]):
                    best = (d, p)
                continue
            if b - a + 1 > mw:
                continue
            d = abs(lo + cen - pred)
            if d <= maxjump + 0.6 * max(0, gap - 1) and (best is None or d < best[0]):
                best = (d, lo + cen)
        if best is None:
            continue
        pos = best[1]; last_c = c
        hist.append((c, pos))
        if len(hist) >= 6:
            (c0, p0), (c1, p1) = hist[-6], hist[-1]
            if c1 != c0:
                slope = (p1 - p0) / (c1 - c0)
        out.append((pos, c) if axis == 'row' else (c, pos))
    return out


def resample(P, step=1.0):
    P = np.asarray(P, float)
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    s = np.arange(0, d[-1], step)
    return np.stack([np.interp(s, d, P[:, 0]), np.interp(s, d, P[:, 1])], 1)


def gsmooth(P, sig):
    if sig <= 0:
        return P.copy()
    k = int(3 * sig) + 1
    g = np.exp(-np.arange(-k, k + 1) ** 2 / (2 * sig * sig)); g /= g.sum()
    Q = np.pad(P, ((k, k), (0, 0)), mode='edge')
    return np.stack([np.convolve(Q[:, 0], g, 'valid'), np.convolve(Q[:, 1], g, 'valid')], 1)


def trace_arch_line(L, x850, slope, xlo, xhi, y_end, top_dir, top_end, ref=False):
    """row scan on the steep side (y from y_end up to 700), then column scan over the crown"""
    up = scan_line(L, 'row', range(850, 699, -1), x850, xlo, xhi, slope0=slope)
    down = scan_line(L, 'row', range(851, y_end + 1), x850, xlo, xhi, slope0=slope)
    (xa, ya), (xb, yb) = up[-6], up[-1]
    cols = range(int(round(xb)) + top_dir, top_end, top_dir)
    top = scan_line(L, 'col', cols, yb, 590, 760, slope0=(yb - ya) / (xb - xa), top=ref)
    P = np.array(down[::-1] + up + top, float)
    # drop stray acquisitions (> 1.5 px off a heavily smoothed version), then smooth lightly
    for _ in range(2):
        R = resample(P, 1.0); S = gsmooth(R, 6)
        d = np.min(np.hypot(P[:, None, 0] - S[None, :, 0], P[:, None, 1] - S[None, :, 1]), 1)
        P = P[d < 1.5]
    return gsmooth(resample(P, 0.5), 3)


def dist_to(P, Q):
    out = np.empty(len(P))
    for i in range(0, len(P), 400):
        a = P[i:i + 400]
        out[i:i + 400] = np.min(np.hypot(a[:, None, 0] - Q[None, :, 0], a[:, None, 1] - Q[None, :, 1]), 1)
    return out


def curve_field(R, P, w, radius):
    """distance from every ROI pixel centre (within radius) to the dense centre line P,
    and the weight w of the nearest centre-line point"""
    D = np.full((R.h, R.w), np.inf, np.float32); Wn = np.zeros((R.h, R.w), np.float32)
    m = np.zeros((R.h, R.w), np.uint8)
    q = np.round(P - [R.x0, R.y0]).astype(int)
    ok = (q[:, 0] >= 0) & (q[:, 0] < R.w) & (q[:, 1] >= 0) & (q[:, 1] < R.h)
    m[q[ok, 1], q[ok, 0]] = 1
    k = int(2 * radius + 3) | 1
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    ys, xs = np.nonzero(m)
    X = (xs + R.x0).astype(np.float32); Y = (ys + R.y0).astype(np.float32)
    Px = P[:, 0].astype(np.float32); Py = P[:, 1].astype(np.float32)
    for i in range(0, len(xs), 3000):
        d2 = (X[i:i + 3000, None] - Px[None]) ** 2 + (Y[i:i + 3000, None] - Py[None]) ** 2
        j = np.argmin(d2, 1)
        D[ys[i:i + 3000], xs[i:i + 3000]] = np.sqrt(d2[np.arange(len(j)), j])
        Wn[ys[i:i + 3000], xs[i:i + 3000]] = w[j]
    return D, Wn


def thin_lines(img, R, curves, refs, r_zone=4.0, r_ring=7.5, w_joint=2.2, w_end=4.8,
               d_full=15.0, d_trim=7.0):
    """replace thick lines (centre lines in `curves`) by thin joints inside ROI R.
    refs: centre lines that stay (the voussoir edge).  A curve stops where it runs into a ref line
    (the last bit stays original and merges into it); just before that the new line widens a little.
    Dark pixels that are not this line's own core (voussoir edge, brick joints) are never touched."""
    sub = img[R.y0:R.y1, R.x0:R.x1].copy()
    D = np.full((R.h, R.w), np.inf, np.float32); W = np.zeros((R.h, R.w), np.float32)
    for P in curves:
        d = np.min([dist_to(P, Q) for Q in refs], 0) if refs else np.full(len(P), 99.0)
        keep = d >= d_trim
        if not keep.all():
            first = int(np.argmin(keep))
            P, d = P[:first], d[:first]
        w = np.clip((d - d_trim) / (d_full - d_trim), 0, 1).astype(np.float32)
        Dc, Wc = curve_field(R, P, w, r_ring + 2)
        closer = Dc < D
        D[closer] = Dc[closer]; W[closer] = Wc[closer]
    has = np.isfinite(D)
    Lsub = sub @ LUM
    other = ((Lsub < 85) & (D > 3.6)).astype(np.uint8)
    other = cv2.dilate(other, np.ones((3, 3), np.uint8)).astype(bool)
    Z = np.where(has & ~other, np.clip(r_zone + 0.5 - D, 0, 1), 0)    # thick line + its AA
    wl = w_joint + (1 - W) * (w_end - w_joint)                          # redrawn line width
    J = np.where(has, np.clip(wl / 2 + 0.5 - D, 0, 1), 0)
    RG = np.where(has, np.clip((wl + 2.8) / 2 + 0.5 - D, 0, 1), 0)
    mask = (Z > 0.01).astype(np.uint8)
    u8 = np.clip(np.round(sub), 0, 255).astype(np.uint8)
    inp = cv2.inpaint(u8, mask, 4, cv2.INPAINT_TELEA).astype(np.float32)
    out = sub * (1 - Z[..., None]) + inp * Z[..., None]
    # the old thick line also had a light rim (sharpening ring) 4-7 px out: pull only the BRIGHT
    # deviations there back to the local brick tone (dark joints that meet the line are kept)
    base = cv2.medianBlur(np.clip(np.round(out), 0, 255).astype(np.uint8), 11).astype(np.float32)
    dev = (out - base) @ LUM
    rz = np.where(has, np.clip(np.minimum(D - (r_zone - 1.5), r_ring + 0.5 - D), 0, 1), 0)
    k = (rz * np.clip((dev - 2.0) / 4.0, 0, 1))[..., None] * 0.75
    out = out * (1 - k) + base * k
    ring = np.clip(soft(RG, 0.6) - soft(J, 0.6), 0, 1)
    out = out + 7.0 * ring[..., None]
    a = soft(J, 0.6) * 0.9
    out = out * (1 - a[..., None]) + JOINT_INK[None, None, :] * a[..., None]
    img = img.copy()
    img[R.y0:R.y1, R.x0:R.x1] = out
    return img


def fix_arches(img):
    L = A @ LUM
    # left arch: steep side on the left, crown runs to the right (x increasing)
    ref_L = trace_arch_line(L, 40.5, -0.35, 0, 400, 990, +1, 640, ref=True)
    cl = [trace_arch_line(L, 160.5, -0.25, 0, 400, 944, +1, 640),
          trace_arch_line(L, 201.0, -0.30, 0, 400, 924, +1, 640),
          trace_arch_line(L, 224.5, -0.30, 0, 400, 912, +1, 640)]
    img = thin_lines(img, ROI(96, 590, 640, 960), cl, [ref_L])
    # right arch: steep side on the right, crown runs to the left
    ref_R = trace_arch_line(L, 2002.5, 0.30, 1600, 2048, 1060, -1, 1400, ref=True)
    cr = [trace_arch_line(L, 1882.0, 0.25, 1600, 2048, 993, -1, 1400),
          trace_arch_line(L, 1837.5, 0.30, 1600, 2048, 972, -1, 1400),
          trace_arch_line(L, 1814.5, 0.30, 1600, 2048, 985, -1, 1400)]
    img = thin_lines(img, ROI(1400, 590, 1930, 1000), cr, [ref_R])
    return img


def main():
    img = A.copy()
    img = fix_heads(img)
    img = fix_arches(img)
    res = np.clip(np.round(img), 0, 255).astype(np.uint8)
    Image.fromarray(res, 'RGB').save(os.path.join(OUTDIR, 'final_new.png'))
    return res


if __name__ == '__main__':
    main()

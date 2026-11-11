#!/usr/bin/env python3
"""L19d picture fix (PIL / numpy / cv2 only).  Rebuilds final_new.png from the read-only original.

  python3 fix.py [original.png] [out.png]

 1. bar-end plates 5|1 -> 5|3 (left door: both bars, floor bar; die-3 diagonal top-right / centre / bottom-left)
 2. workbench plates -> left plate keeps only its top 5, right plate keeps only its bottom 3
 3. station 2, left board: wipe the 6th dot beside the stamp head, turn the pale flat patch under the head
    back into plain wood and give the head back the outline the patch had cut off
 4. right door: remove the two bars still hanging on it (wall, jamb, leaf, panel frames, records, rat's tail
    rebuilt), and lay a second broken bar (copy of the existing broken one) on the floor
"""
import sys
import numpy as np, cv2
from PIL import Image

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
ORIG = SP + '/L19d/r1/final_v1.png'
OUT = SP + '/picfix/L19d/final_new.png'

# ============================================================== common helpers
def harmonic_fill(img, dom, valid=None, iters=3000, tol=0.02):
    """membrane (Laplace) fill of dom from the surrounding pixels; neighbours that are neither in dom
    nor valid are ignored"""
    H, W = dom.shape
    if valid is None:
        valid = ~dom
    ys, xs = np.nonzero(dom)
    y0, y1 = max(ys.min()-2, 0), min(ys.max()+3, H)
    x0, x1 = max(xs.min()-2, 0), min(xs.max()+3, W)
    D = dom[y0:y1, x0:x1]; V = valid[y0:y1, x0:x1] & ~D
    U = img[y0:y1, x0:x1].astype(np.float64).copy()
    use = (D | V).astype(np.float64)
    ring = cv2.dilate(D.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & V
    U[D] = U[ring].mean(0)
    for _ in range(iters):
        P = np.pad(U, ((1, 1), (1, 1), (0, 0)), mode='edge')
        M = np.pad(use, ((1, 1), (1, 1)), mode='constant')
        s = (P[:-2, 1:-1]*M[:-2, 1:-1, None] + P[2:, 1:-1]*M[2:, 1:-1, None] +
             P[1:-1, :-2]*M[1:-1, :-2, None] + P[1:-1, 2:]*M[1:-1, 2:, None])
        n = (M[:-2, 1:-1] + M[2:, 1:-1] + M[1:-1, :-2] + M[1:-1, 2:])[..., None]
        new = s/np.maximum(n, 1e-9)
        diff = np.abs(new[D]-U[D]).max()
        U[D] = new[D]
        if diff < tol:
            break
    out = img.copy()
    out[y0:y1, x0:x1][D] = U[D]
    return out

def disc_mask(shape, centres, r):
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W]
    m = np.zeros(shape, bool)
    for (cx, cy) in centres:
        x0, x1 = int(cx-r-2), int(cx+r+3); y0, y1 = int(cy-r-2), int(cy+r+3)
        m[y0:y1, x0:x1] |= np.hypot(xx[y0:y1, x0:x1]-cx, yy[y0:y1, x0:x1]-cy) <= r
    return m

def catmull(pts, n=12):
    P = np.array(pts, float); P = np.vstack([P[0], P, P[-1]]); out = []
    for i in range(1, len(P)-2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
    out.append(P[-2])
    return np.array(out)

def poly_mask(shape, pts, ss=4):
    H, W = shape
    m = np.zeros((H*ss, W*ss), np.uint8)
    p = (np.array(pts, float)*ss + (ss-1)/2.0)
    cv2.fillPoly(m, [np.round(p*16).astype(np.int32)], 255, lineType=cv2.LINE_8, shift=4)
    return cv2.resize(m.astype(np.float32)/255, (W, H), interpolation=cv2.INTER_AREA) > 0.02

# ============================================================== item 1: plates 5|1 -> 5|3
def stamp_dot(img, src, sc, d, r_full=6.0, r_zero=7.5):
    """copy the dot centred at sc to sc+d (integer shift) multiplicatively: dst *= 1 + w*(src/bg - 1)"""
    sx, sy = int(round(sc[0])), int(round(sc[1])); dx, dy = d
    R = 9
    P = src[sy-R:sy+R+1, sx-R:sx+R+1]
    gy, gx = np.mgrid[-R:R+1, -R:R+1].astype(np.float32)
    r = np.hypot(gx-(sc[0]-sx), gy-(sc[1]-sy))
    gP = P.mean(2)
    bg = np.median(P[(r >= 7.0) & (r <= 9.0) & (gP > 170)], axis=0)
    ratio = P/bg
    t = np.clip((r_zero-r)/(r_zero-r_full), 0, 1)
    w = 0.5-0.5*np.cos(np.pi*t)
    dark = (gP < 175).astype(np.uint8)                 # never carry ink that is not part of this dot
    _, lab = cv2.connectedComponents(dark, connectivity=8)
    own = (lab == lab[R, R]) & (dark > 0)
    excl = cv2.dilate(((dark > 0) & ~own).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    w[excl] = 0
    D = img[sy+dy-R:sy+dy+R+1, sx+dx-R:sx+dx+R+1]
    D[:] = np.clip(D*(1+w[..., None]*(ratio-1)), 0, 255)

def shift_patch(img, src, c, d, r_full=3.6, r_zero=5.2):
    """wipe a small stray dot at c with the pixels at c+d (along the plate border), colour-matched"""
    cx, cy = c; dx, dy = d
    R = 7
    x0, y0 = int(round(cx))-R, int(round(cy))-R
    gy, gx = np.mgrid[y0:y0+2*R+1, x0:x0+2*R+1].astype(np.float32)
    r = np.hypot(gx-cx, gy-cy)
    t = np.clip((r_zero-r)/(r_zero-r_full), 0, 1); w = (0.5-0.5*np.cos(np.pi*t))[..., None]
    S = src[y0+dy:y0+dy+2*R+1, x0+dx:x0+dx+2*R+1].copy()
    D = img[y0:y0+2*R+1, x0:x0+2*R+1]
    ring = (r >= r_zero) & (r <= r_zero+2) & (S.mean(2) > 190) & (D.mean(2) > 190)
    S += (np.median(D[ring], axis=0)-np.median(S[ring], axis=0))
    D[:] = D*(1-w)+S*w

# centre dot of each right cell (its existing single dot) and the integer offsets of the 5-pattern's
# top-right / bottom-left dots from the 5-pattern's centre dot, measured on the same plate.
# (the two plates of the right door are not listed: those bars are removed in item 4)
PLATES = {
    'left door, upper (broken) bar': ((756.6, 329.1), [(8, -10), (-8, 12)]),
    'left door, lower bar':          ((759.4, 484.6), [(9, -10), (-10, 9)]),
    'floor bar':                     ((1252.9, 791.9), [(4, -8), (-4, 10)]),
}

def item1(img, src):
    shift_patch(img, src, (1231.9, 788.8), (10, -3))   # floor plate: stray small dot beside the divider
    for c, offs in PLATES.values():
        for d in offs:
            stamp_dot(img, src, c, d)

# ============================================================== item 2: workbench plates
WB_L_BOTTOM = [(1907.5, 458.1), (1943.8, 456.7), (1927.0, 477.8), (1910.4, 498.5), (1947.4, 497.3)]
WB_L_KEEP = [(1901.7, 385.8), (1938.1, 385.0), (1921.2, 405.6), (1904.5, 426.3), (1941.5, 425.3)]
WB_R_TOP = [(1999.1, 404.1)]
WB_R_KEEP = [(2020.3, 455.4), (2004.2, 476.1), (1988.3, 496.7)]

def erase_face_dots(img, src, erase, keep, r=13.0):
    H, W = img.shape[:2]
    g = src.mean(2)
    dom = disc_mask((H, W), erase, r)                   # dot + its light halo
    ink = (g < 175) & ~disc_mask((H, W), erase, 9.0)    # borders, divider, kept dots
    ink = cv2.dilate(ink.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    keepd = disc_mask((H, W), keep, 10.5)
    dom &= ~ink
    return harmonic_fill(img, dom, ~dom & ~ink & ~keepd)

def item2(img, src):
    out = erase_face_dots(img, src, WB_L_BOTTOM, WB_L_KEEP)
    out = erase_face_dots(out, src, WB_R_TOP, WB_R_KEEP)
    img[:] = out

# ============================================================== item 3: station 2, left board
INK3 = np.array([10.0, 3.0, 2.0])
DOTS5 = [(474.0, 468.0), (524.0, 468.0), (499.0, 484.0), (474.0, 501.1), (524.0, 501.1)]
RIGHT_ARC = [(518.9, 426.5), (519.6, 430.0), (520.2, 434.0), (520.4, 438.0), (520.1, 442.0), (519.1, 445.5),
             (517.4, 448.5), (515.3, 451.0)]
BOTTOM = [(455.5, 470.2), (459.5, 469.2), (463.5, 467.3), (467.5, 464.3), (472.0, 461.8), (478.0, 460.6), (484.0, 459.5),
          (490.0, 457.8), (496.0, 456.6), (502.0, 455.9), (507.0, 455.5), (511.0, 454.6), (513.5, 452.8)]

def stroke_alpha(shape, pts, width, ss=4):
    H, W = shape
    C = catmull(pts)
    x0, y0 = int(C[:, 0].min()-width-3), int(C[:, 1].min()-width-3)
    x1, y1 = int(C[:, 0].max()+width+4), int(C[:, 1].max()+width+4)
    m = np.zeros(((y1-y0)*ss, (x1-x0)*ss), np.uint8)
    q = np.round((C-[x0, y0])*ss*16 + 8*(ss-1)).astype(np.int32)
    cv2.polylines(m, [q.reshape(-1, 1, 2)], False, 255, thickness=int(round(width*ss)), lineType=cv2.LINE_AA, shift=4)
    a = cv2.resize(m.astype(np.float32)/255.0, (x1-x0, y1-y0), interpolation=cv2.INTER_AREA)
    A = np.zeros((H, W), np.float32); A[y0:y1, x0:x1] = a
    return A, C

def item3(img, src):
    H, W = img.shape[:2]
    g = src.mean(2)
    R, G, B = src[..., 0], src[..., 1], src[..., 2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wood = (R > 180) & (G > 140) & (R-B > 60) & ~((R > 224) & (G > 186))
    dots = disc_mask((H, W), DOTS5, 8.6)
    aR, CR = stroke_alpha((H, W), RIGHT_ARC, 3.4)
    aB, CB = stroke_alpha((H, W), BOTTOM, 3.2)
    # (a) the 6th dot: right of the head's right outline, within r<=12.5 of the dot
    cxs = np.interp(yy, CR[:, 1], CR[:, 0], left=np.nan, right=np.nan)
    d6 = (np.hypot(xx-528.0, yy-441.0) <= 12.5) & (yy >= 426) & (yy <= 456) & (xx <= 539)
    D6 = d6 & np.where(np.isnan(cxs), xx > 515.5, xx > cxs+1.2) & (aR < 0.98)
    # (b) the pale flat patch: below the new bottom outline, above the divider, inside the board face
    o = np.argsort(CB[:, 0]); cb = np.interp(xx, CB[o, 0], CB[o, 1])
    face = np.zeros((H, W), bool); face[450:510, 456:539] = True
    outline_left = np.zeros((H, W), bool)           # the board's left outline (dark run + its AA) stays
    for y in range(450, 510):
        row = g[y, 448:475]
        dk = np.nonzero(row < 60)[0]
        if len(dk):
            e = dk[0]
            while e+1 < len(row) and row[e+1] < 60:
                e += 1
            while e+1 < len(row) and row[e+1] < 150:
                e += 1
            outline_left[y, 448:448+e+1] = True
    P = face & (yy > cb+1.0) & ~outline_left & ~dots & (xx >= 456)
    P &= ~((xx > 510) & (yy < 456))                  # the head's lower-right outline stub stays
    dom = P | D6
    ink = (g < 120) & ~dom
    valid = wood & ~dom & ~dots & ~ink & (np.abs(xx-500) < 60) & (np.abs(yy-460) < 70)
    out = harmonic_fill(img, dom, valid)
    # (c) the head's outline: right end (was hidden by the 6th dot) and bottom (cut away by the patch)
    for a in (aR, aB):
        out = out*(1-a[..., None]) + INK3*a[..., None]
    for y in range(462, 510):                          # one anti-aliasing pixel next to the board's left outline
        row = g[y, 448:475]
        dk = np.nonzero(row < 60)[0]
        if not len(dk):
            continue
        e = dk[0]
        while e+1 < len(row) and row[e+1] < 60:
            e += 1
        x = 448+e+1
        if dom[y, x] and row[e+1] >= 150 and not dots[y, x]:
            out[y, x] = 0.45*INK3 + 0.55*out[y, x]
    img[:] = out

# ============================================================== item 4: right door
def ytop_U(x): return 279.0 + 0.4966*(x-1173.5)
def ytop_L(x): return 472.0 + 0.557*(x-1200.0)
def ybot_L(x): return 507.0 + 0.554*(x-1148.0)

# bar + outline + its light halo + soft cast shadow (door and wall); jagged ends included
U_POLY = [(1160, 275), (1326, ytop_U(1326)), (1331.5, 364.5), (1331.5, 377), (1329, 390), (1319, 403), (1317, 415.5),
          (1300, 414), (1280, 410.5), (1260, 401), (1240, 390), (1220, 380), (1200, 372.5), (1185, 366), (1170, 361),
          (1158, 355), (1149, 342), (1144, 330), (1147, 317), (1156, 291)]
L_POLY = [(1165, 458), (1181, ytop_L(1181)), (1349, ytop_L(1349)), (1360, 571), (1370.5, 582), (1370.5, 590),
          (1360, 595), (1358, 605), (1359, 613), (1353, 621), (1347, ybot_L(1347)+9),
          (1320, ybot_L(1320)+13), (1290, ybot_L(1290)+15), (1260, ybot_L(1260)+18), (1230, ybot_L(1230)+18),
          (1200, ybot_L(1200)+18), (1180, ybot_L(1180)+15), (1165, 535), (1152, 525), (1146, 512), (1144, 500), (1150, 485)]

def runs(col_mask):
    idx = np.nonzero(col_mask)[0]
    if not len(idx):
        return []
    out = []; a = idx[0]; p = a
    for v in idx[1:]:
        if v != p+1:
            out.append((a, p)); a = v
        p = v
    out.append((a, p))
    return out

def side_rows(bad, x, y_from, step, limit, need):
    out = []; y = y_from
    while len(out) < need and ((step < 0 and y >= limit) or (step > 0 and y <= limit)):
        if bad[y, x]:
            break
        out.append(y); y += step
    return out

def boundary_val(src, bad, x, y_from, step, limit, k=5):
    rows = side_rows(bad, x, y_from, step, limit, k)
    return np.median(src[rows, x], axis=0) if len(rows) >= 3 else None

def region_fill(img, src, M, xs, bad, lim_above, lim_below, use_top=True, use_bot=True, apply=True, skip=3):
    """per column: linear interpolation between the median colour a few rows above the gap and a few rows
    below it.  The door, jamb and wall are flat colour with vertical lines, so this reproduces them exactly."""
    out = {}
    for x in xs:
        r = runs(M[:, x])
        if not r:
            continue
        ya, yb = r[0][0], r[-1][1]
        n = yb-ya+1
        ta = boundary_val(src, bad, x, ya-1-skip, -1, lim_above(x)) if use_top else None
        tb = boundary_val(src, bad, x, yb+1+skip, +1, lim_below(x)) if use_bot else None
        if ta is None and tb is None:
            continue
        if ta is None: ta = tb
        if tb is None: tb = ta
        t = np.linspace(0, 1, n)[:, None]
        v = (1-t)*ta + t*tb
        out[x] = (ya, yb, v)
        if apply:
            img[ya:yb+1, x] = v
    return out

def y_ptop_lower(x): return 476.0-0.2125*(x-1250.0)   # lower panel, top edge outer line
def c_in(x): return 368.7+0.046*(1328.0-x)            # upper panel, hidden bottom edge, inner line (outer +4.5)
def y_pti(x): return 481.0-0.225*(x-1250.0)           # lower panel, top edge inner line
def y_bi(x): return 632.5-0.41*(x-1250.0)             # lower panel, bottom edge inner line
COS_B = 1.0/np.sqrt(1+0.41**2)

def remove_upper(img, src, U, L):
    bad = U | L
    region_fill(img, src, U, range(1140, 1184), bad, lambda x: 150, lambda x: 455)              # wall
    region_fill(img, src, U, range(1184, 1240), bad, lambda x: 242 if 1208 <= x <= 1228 else 150,
                lambda x: 466)                                                                 # jamb + stile
    xs = range(1240, 1332)                                                                     # upper panel
    A = region_fill(img, src, U, xs, bad, lambda x: 200, lambda x: 0, use_bot=False, apply=False)
    B = region_fill(img, src, U, xs, bad, lambda x: 0, lambda x: int(y_ptop_lower(x))-5, use_top=False, apply=False)
    xs_p = np.arange(1316, 1347); prof = np.median(src[290:345, 1316:1347], axis=0)    # right frame edge profile
    for x in xs:
        if x not in A:
            continue
        ya, yb, va = A[x]; vb = B[x][2]
        db = np.arange(ya, yb+1)-c_in(x)
        vert = max(1250.5-x, x-1328.5)
        pb = np.stack([np.interp(1328.5+db, xs_p, prof[:, c]) for c in range(3)], -1)   # bottom edge = right edge turned
        wa = np.clip((-1.5-db)/1.5, 0, 1)[:, None]
        wb = np.clip((db-8.5)/1.5, 0, 1)[:, None]
        v = wa*va + wb*vb + (1-wa-wb)*pb
        wv = np.clip((vert-db)+0.5, 0, 1)[:, None]                                        # mitred corners
        wv = np.where((db < 10)[:, None], wv, 0)
        img[ya:yb+1, x] = wv*va + (1-wv)*v

def lower_bottom_profile(src):
    D = []; V = []
    for x in range(1258, 1296):
        for y in range(int(y_bi(x))-12, int(y_bi(x))+18):
            D.append((y-y_bi(x))*COS_B); V.append(src[y, x])
    D = np.array(D); V = np.array(V, float)
    bins = np.array([b for b in np.arange(-10, 16.01, 0.5) if ((D >= b-0.25) & (D < b+0.25)).sum() >= 5])
    prof = np.array([np.median(V[(D >= b-0.25) & (D < b+0.25)], axis=0) for b in bins])
    return bins, prof

def remove_lower(img, L, tail_cut=1206):
    S = img.copy()
    bad = L
    region_fill(img, S, L, range(1140, 1155), bad, lambda x: 300, lambda x: 600)               # wall
    region_fill(img, S, L, range(1155, 1184), bad, lambda x: 300, lambda x: 0, use_bot=False)  # wall over the tail
    region_fill(img, S, L, range(1184, tail_cut), bad, lambda x: 300, lambda x: 0, use_bot=False)
    region_fill(img, S, L, range(tail_cut, 1240), bad, lambda x: 300, lambda x: 572 if 1208 <= x <= 1228 else 640)
    xs = range(1240, 1350)                                                                      # lower panel
    A = region_fill(img, S, L, xs, bad, lambda x: int(y_pti(x))+4 if x < 1334 else 482, lambda x: 0,
                    use_bot=False, apply=False)
    B = region_fill(img, S, L, xs, bad, lambda x: 0, lambda x: (int(y_bi(x))-4 if x < 1300 else 642) if x < 1336 else 0,
                    use_top=False, apply=False)
    bins, prof = lower_bottom_profile(S)
    for x in xs:
        if x not in A:
            continue
        ya, yb, va = A[x]
        n = yb-ya+1
        if x in B and x < 1300:
            t = np.linspace(0, 1, n)[:, None]; t = t*t*(3-2*t)
            img[ya:yb+1, x] = (1-t)*va + t*B[x][2]
            continue
        vb = B[x][2] if x in B else va
        db = (np.arange(ya, yb+1)-y_bi(x))*COS_B
        pb = np.stack([np.interp(db, bins, prof[:, c]) for c in range(3)], -1)
        wa = np.clip((-5.5-db)/1.5, 0, 1)[:, None]
        wb = np.clip((db-9.5)/1.5, 0, 1)[:, None]
        v = wa*va + wb*vb + (1-wa-wb)*pb
        wv = np.clip(((x-1326.6)-db)+0.5, 0, 1)[:, None]                                  # mitre with the right frame
        img[ya:yb+1, x] = wv*va + (1-wv)*v

def fill_records_gap(img, src, L):
    """right of the leaf edge the bar's tip lay over the record pile: continue each row's record band
    leftwards from the first original pixels right of the gap, and continue the leaf's edge line"""
    S = img.copy()
    edge = np.median(src[520:552, 1350], axis=0)
    edge2 = np.median(src[520:552, 1349], axis=0)
    for y in range(550, 630):
        xs = [x for x in range(1349, 1373) if L[y, x]]
        if not xs:
            continue
        e = max(xs)
        ref = np.median(S[y, e+1:e+4], axis=0)
        for x in xs:
            img[y, x] = edge2 if x == 1349 else (edge if x == 1350 else ref)

def raster(shape, box, draw, ss=8):
    x0, y0, x1, y1 = box
    m = np.zeros(((y1-y0)*ss, (x1-x0)*ss), np.uint8)
    draw(m, lambda P: np.round(((np.asarray(P)-[x0, y0])*ss+(ss-1)/2.0)*16).astype(np.int32), ss)
    a = cv2.resize(m.astype(np.float32)/255, (x1-x0, y1-y0), interpolation=cv2.INTER_AREA)
    A = np.zeros(shape, np.float32); A[y0:y1, x0:x1] = a
    return A

TAIL_L = [(1178.6, 545.0), (1181.0, 542.6), (1183.6, 540.5), (1186.0, 538.9), (1188.3, 537.9)]
TAIL_R = [(1180.6, 549.6), (1182.6, 547.4), (1184.8, 544.4), (1186.7, 541.5), (1188.3, 537.9)]
TAIL_INK = np.array([24.0, 15.0, 13.0]); TAIL_PINK = np.array([205.0, 178.0, 170.0])

def draw_tail_tip(img):
    """the rat's tail used to vanish under the lower bar: short tapered tip crossing the jamb line"""
    H, W = img.shape[:2]
    Lc, Rc = catmull(TAIL_L, 10), catmull(TAIL_R, 10)
    box = (1170, 528, 1200, 558)
    poly = np.vstack([Lc, Rc[::-1]])
    af = raster((H, W), box, lambda m, T, ss: cv2.fillPoly(m, [T(poly).reshape(-1, 1, 2)], 255, cv2.LINE_AA, 4))
    al = raster((H, W), box, lambda m, T, ss: [cv2.polylines(m, [T(C).reshape(-1, 1, 2)], False, 255,
                                                             thickness=int(round(1.9*ss)), lineType=cv2.LINE_AA, shift=4)
                                               for C in (Lc, Rc)])
    img[:] = img*(1-af[..., None]) + TAIL_PINK*af[..., None]
    img[:] = img*(1-al[..., None]) + TAIL_INK*al[..., None]

# ---- second broken bar on the floor: copy of the existing two halves
POLY_LP = [(1156, 795), (1262, 766), (1335, 748), (1343, 752), (1346, 766), (1362, 770), (1372, 785),
           (1370, 792), (1203, 853), (1192, 851), (1160, 828)]
POLY_RP = [(1372, 757), (1385, 750), (1404, 745), (1478, 724), (1551, 707), (1560, 710), (1580, 733),
           (1577, 742), (1434, 791), (1416, 800), (1398, 801), (1378, 790), (1372, 772)]
SHIFT_LP = (-115, 140)     # the half with the 5|3 plate
SHIFT_RP = (-305, 305)     # the other half

def dark_component(src, poly, thr=95):
    H, W = src.shape[:2]
    P = poly_mask((H, W), poly)
    d = ((src.mean(2) < thr) & P).astype(np.uint8)
    _, lab, st, _ = cv2.connectedComponentsWithStats(d, connectivity=8)
    return (lab == 1+int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8), P

def outline_mask(src, poly):
    """inside of the piece's closed black outline"""
    d, P = dark_component(src, poly)
    cnts, _ = cv2.findContours(d, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    f = np.zeros_like(d); cv2.drawContours(f, cnts, -1, 1, thickness=-1)
    return f.astype(bool) & P

def hull_mask(src, poly, x_split, y_split):
    """convex hull of the outline (the right half touches records, so its fill leaks); the exact filled
    outline is kept at the jagged end below y_split so the floor between the teeth is not copied"""
    d, P = dark_component(src, poly)
    H, W = d.shape
    ys, xs = np.nonzero(d)
    h = np.zeros_like(d); cv2.fillPoly(h, [cv2.convexHull(np.stack([xs, ys], 1).astype(np.int32))], 1)
    f = outline_mask(src, poly)
    xx = np.arange(W)[None, :]; yy = np.arange(H)[:, None]
    return np.where((xx < x_split) & (yy >= y_split), f, h.astype(bool)) & P

def paste_piece(img, src, mask, shift):
    dx, dy = shift
    m = mask.astype(np.uint8)
    a = m.astype(np.float32) + 0.5*(cv2.dilate(m, np.ones((3, 3), np.uint8))-m).astype(np.float32)
    ys, xs = np.nonzero(a > 0)
    y0, y1, x0, x1 = ys.min(), ys.max()+1, xs.min(), xs.max()+1
    A = a[y0:y1, x0:x1, None]
    D = img[y0+dy:y1+dy, x0+dx:x1+dx]
    D[:] = D*(1-A) + src[y0:y1, x0:x1]*A

def floor_copy(img):
    S = img.copy()
    mL = outline_mask(S, POLY_LP)
    mR = hull_mask(S, POLY_RP, 1400, 763)
    H, W = mR.shape
    yy, xx = np.mgrid[0:H, 0:W]
    mR &= ~((xx >= 1404) & (yy > -0.3313*xx + 1262.26 + 0.5))      # stop at the bottom outline's outer edge
    paste_piece(img, S, mL, SHIFT_LP)
    paste_piece(img, S, mR, SHIFT_RP)

def item4(img):
    H, W = img.shape[:2]
    U, L = poly_mask((H, W), U_POLY), poly_mask((H, W), L_POLY)
    S1 = img.copy()
    remove_upper(img, S1, U, L)
    remove_lower(img, L)
    fill_records_gap(img, S1, L)
    draw_tail_tip(img)
    floor_copy(img)

# ============================================================== main
if __name__ == '__main__':
    src_path = sys.argv[1] if len(sys.argv) > 1 else ORIG
    out_path = sys.argv[2] if len(sys.argv) > 2 else OUT
    src = np.array(Image.open(src_path).convert('RGB')).astype(np.float64)
    img = src.copy()
    item1(img, src)
    item2(img, src)
    item3(img, src)
    item4(img)
    out = np.clip(img+0.5, 0, 255).astype(np.uint8)
    Image.fromarray(out, 'RGB').save(out_path)
    d = np.abs(out.astype(int)-np.array(Image.open(src_path).convert('RGB')).astype(int)).sum(2) > 0
    ys, xs = np.nonzero(d)
    print(out_path, out.shape, 'changed px', int(d.sum()), 'bbox', xs.min(), ys.min(), xs.max(), ys.max())

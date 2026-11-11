# -*- coding: utf-8 -*-
"""L45c 그림 고침 — 원본 final_v2.png 에서 final_new.png 를 다시 만든다 (PIL · numpy · cv2 만).

  항목 1  점선 둘레길(순환 전자 흐름)의 오른쪽 끝: 방패 윗테 → 정자 지붕 꼭대기(첨탑 끝).
          첨탑 바로 위부터 방패까지 내려가던 점선 토막 16개를 지우고(하늘 이어 그리기),
          남은 호 끝에서 첨탑 끝으로 휘어 내려가는 토막 둘을 원본 토막을 옮겨 붙여 잇는다.
  항목 2  계단 발치 쿠션 윗면의 붉은 구슬 무더기 둘을 지우고(계단 밑선 · 초록 바탕 이어 그리기),
          두 국자 구슬 줄 끝(계단 밑선 바로 앞)에 겉천의 작은 틈(갈색 속 · 검은 테)을 그리고,
          줄의 구슬 하나(원본 구슬을 옮겨 씀)가 틈 속으로 반쯤 들어가게 한다.

  쓰는 법:  python3 fix.py      → final_new.png · cmp_1.png · cmp_2.png (같은 폴더)
"""
import os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = SP + '/L45c/r1/final_v2.png'          # 읽기만 한다
OUT = SP + '/picfix/L45c/'


# ───────────────────────────── 공통 ─────────────────────────────
def disk(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def harmonic_fill(img, mask, iters):
    """mask 안을 둘레 값만으로 매끈하게 메운다(라플라스 풀이)."""
    out = img.copy()
    ys, xs = np.where(mask)
    y0, y1 = ys.min() - 2, ys.max() + 3
    x0, x1 = xs.min() - 2, xs.max() + 3
    sub = out[y0:y1, x0:x1].copy()
    m = mask[y0:y1, x0:x1]
    ring = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m
    sub[m] = sub[ring].mean(0)
    for _ in range(iters):
        avg = (np.roll(sub, 1, 0) + np.roll(sub, -1, 0) + np.roll(sub, 1, 1) + np.roll(sub, -1, 1)) / 4.0
        sub[m] = avg[m]
    out[y0:y1, x0:x1] = sub
    return out


# ───────────────────────────── 항목 1: 점선 둘레길 ─────────────────────────────
SKY = np.array([175., 231., 252.])     # 이 둘레의 하늘 빛(재어 본 값 — 거의 평평)
TIP = np.array([1658.8, 147.5])        # 정자 첨탑 끝(첫 어두운 화소 148행)
PITCH, HALF = 22.7, 6.5                # 원본 토막 간격 · 토막 반길이
K_KEEP = 3                             # 왼쪽부터 0..3 번 토막(…(1622.7,112.7))까지 남긴다
BEZ_A, BEZ_B, GAP = 20.0, 15.0, 6.0    # 잇는 굽은 길(3차 베지에) 손잡이 · 첨탑 끝과의 틈


def find_dashes(a):
    x0, y0, x1, y1 = 1540, 80, 1960, 345
    sub = a[y0:y1, x0:x1]
    core = (sub[:, :, 1] < 200) & (sub[:, :, 2] < 215)
    n, lab, st, cen = cv2.connectedComponentsWithStats(core.astype(np.uint8), connectivity=8)
    out = []
    for i in range(1, n):
        ar = st[i, 4]
        if ar < 20 or ar > 400:          # 정자(큰 덩이) · 티끌 빼고
            continue
        m = np.zeros(a.shape[:2], bool)
        m[y0:y1, x0:x1] = (lab == i)
        mo = cv2.moments((lab == i).astype(np.uint8))
        th = 0.5 * np.degrees(np.arctan2(2 * mo['mu11'], mo['mu20'] - mo['mu02']))
        out.append(dict(c=(cen[i][0] + x0, cen[i][1] + y0), th=th, mask=m))
    out.sort(key=lambda d: d['c'][0])
    return out


def bezier(P0, P1, P2, P3, n=2000):
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3) * P0 + 3 * ((1 - t) ** 2) * t * P1 + 3 * (1 - t) * t * t * P2 + (t ** 3) * P3


def arclen(pts):
    return np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]


def at_s(pts, s):
    d = arclen(pts)
    i = int(np.clip(np.searchsorted(d, s), 1, len(d) - 1))
    f = (s - d[i - 1]) / (d[i] - d[i - 1] + 1e-9)
    p = pts[i - 1] + (pts[i] - pts[i - 1]) * f
    tv = pts[min(i + 3, len(pts) - 1)] - pts[max(i - 4, 0)]
    return p, np.degrees(np.arctan2(tv[1], tv[0]))


def item1(a, out, log):
    src = a
    D = find_dashes(src)
    assert len(D) == 20, len(D)
    P = [np.array(d['c']) for d in D]
    kept = list(range(0, K_KEEP + 1))
    erased = list(range(K_KEEP + 1, len(D)))
    log.append('항목1: 토막 %d개 찾음 · 남김 %d개(왼쪽) · 지움 %d개' % (len(D), len(kept), len(erased)))

    # ① 지우기 — 지울 토막 몸통을 9px 넓혀(흰 테 · 번짐까지) 하늘로 메운다
    core_er = np.zeros(a.shape[:2], np.uint8)
    for i in erased:
        core_er |= D[i]['mask'].astype(np.uint8)
    core_all = np.zeros(a.shape[:2], np.uint8)
    for d in D:
        core_all |= d['mask'].astype(np.uint8)
    core_kept = np.zeros(a.shape[:2], np.uint8)
    for i in kept:
        core_kept |= D[i]['mask'].astype(np.uint8)
    E = cv2.dilate(core_er, disk(9)).astype(bool)
    nonsky = np.abs(src - SKY).max(2) > 14
    obj = nonsky & ~cv2.dilate(core_all, disk(5)).astype(bool)        # 정자 · 방패 · 구름
    E &= ~cv2.dilate(obj.astype(np.uint8), disk(3)).astype(bool)        # 방패 윗테의 흰 테는 건드리지 않음
    E &= ~cv2.dilate(core_kept, disk(5)).astype(bool)                   # 남기는 토막의 테도 그대로
    n, lab = cv2.connectedComponents(E.astype(np.uint8))
    for i in range(1, n):
        m = lab == i
        ring = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m
        tmp = out.copy()
        tmp[ring & (np.abs(out - SKY).max(2) > 6)] = SKY                # 둘레에 걸린 테 화소는 하늘값으로
        f = harmonic_fill(tmp, m, 1500)
        out[m] = f[m]

    # ② 잇기 — 남은 호 끝(3번 토막)에서 첨탑 끝으로 휘어 내려가는 길에 토막을 원본 간격대로 놓는다
    PK = P[K_KEEP]
    t0 = P[K_KEEP + 1] - P[K_KEEP - 1]
    t0 = t0 / np.linalg.norm(t0)
    Ept = TIP - np.array([0, GAP])
    pts = bezier(PK, PK + BEZ_A * t0, Ept - np.array([0, BEZ_B]), Ept)
    L = arclen(pts)[-1]
    nn = max(1, int(round((L - HALF) / PITCH)))
    pitch = (L - HALF) / nn
    spire = cv2.dilate(obj.astype(np.uint8), disk(1)).astype(bool)
    H, W = a.shape[:2]
    for k in range(1, nn + 1):
        p, th = at_s(pts, pitch * k)
        j = min(erased, key=lambda i: abs(D[i]['th'] - th))           # 기울기가 가장 가까운 원본 토막
        sc = np.array(D[j]['c'])
        dx, dy = int(round(p[0] - sc[0])), int(round(p[1] - sc[1]))   # 돌리지 않고 옮기기만
        am = cv2.dilate(D[j]['mask'].astype(np.uint8), disk(4)).astype(np.float32)
        am = np.clip(cv2.GaussianBlur(am, (0, 0), 1.0) * 1.25, 0, 1)
        Mt = np.float32([[1, 0, dx], [0, 1, dy]])
        am_s = cv2.warpAffine(am, Mt, (W, H), flags=cv2.INTER_NEAREST)
        src_s = cv2.warpAffine(src.astype(np.float32), Mt, (W, H), flags=cv2.INTER_NEAREST).astype(np.float64)
        am_s[spire] = 0
        out[:] = out * (1 - am_s[..., None]) + src_s * am_s[..., None]
        log.append('항목1: 새 토막 (%.1f,%.1f) 기울기 %.0f° ← 원본 %d번 토막(%.1f°) 옮김 %+d,%+d'
                   % (sc[0] + dx, sc[1] + dy, th, j, D[j]['th'], dx, dy))
    log.append('항목1: 잇는 길 길이 %.1f px · 토막 간격 %.1f px(원본 %.1f) · 끝 토막과 첨탑 끝 틈 %.0f px'
               % (L, pitch, PITCH, GAP))
    return out


# ───────────────────────────── 항목 2: 구슬 무더기 → 겉천의 틈 ─────────────────────────────
DS = np.arange(-14, 40.01, 0.25)        # 계단 밑선에서 잰 세로 거리(위 − / 아래 +)
PILES = {
    'L': dict(box=(852, 686, 930, 742), corner=(867, 699), protect_beads=[(897.8, 681.0)],
              edge_cols=list(range(866, 872)) + list(range(914, 936, 2)), prof_cols=list(range(914, 952, 2)),
              slot_x=898.0),
    'R': dict(box=(940, 704, 1034, 762), protect_beads=[(981.5, 703.5), (990.2, 689.7)],
              edge_cols=list(range(934, 956, 2)) + list(range(1016, 1042, 2)),
              prof_cols=list(range(934, 956, 2)) + list(range(1016, 1046, 2)),
              slot_x=985.0),
}
SLOT = dict(dy=8.0, Lx=17.0, Hup=3.0, Hdn=6.0, k=2.0, bead_off=(0.0, 1.0))   # 구슬 아래 ⅓쯤이 앞 입술 뒤로 잠김
BROWN = np.array([150., 85., 66.])      # 정거장 5 양동이 밑 틈 속 빛 (재어 본 값)
BLACK = np.array([8., 6., 4.])
LIFT = np.array([21., 3., 23.])          # 이 그림 윤곽선 바깥의 밝은 테(초록 위) — 재어 본 값
BEAD_SRC = (897.7, 681.4)               # 옮겨 쓸 원본 구슬(왼쪽 줄 맨 끝 구슬)
SS = 4                                  # 4배로 그려 줄이기


def edge_center(Lum, x, yguess, half=8):
    col = Lum[yguess - half:yguess + half + 1, x]
    w = np.clip(120 - col, 0, None)
    return (np.arange(yguess - half, yguess + half + 1) * w).sum() / max(w.sum(), 1e-6)


def fit_edge(a, cols):
    Lum = a.mean(2)
    xs = np.array(cols, float)
    ys = np.array([edge_center(Lum, x, int(round(704.6 + 0.2365 * (x - 920)))) for x in cols])
    m, c = np.polyfit(xs, ys, 1)
    return m, c


def profile(a, cols, m, c):
    vals = []
    for x in cols:
        yf = m * x + c + DS
        y0 = np.floor(yf).astype(int)
        f = (yf - y0)[:, None]
        vals.append(a[y0, x] * (1 - f) + a[y0 + 1, x] * f)
    return np.median(np.array(vals), axis=0)


def render_model(box, m, c, prof):
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = yy - (m * xx + c)
    out = np.zeros((y1 - y0, x1 - x0, 3))
    for ch in range(3):
        out[..., ch] = np.interp(d, DS, prof[:, ch])
    return out


def restore_piles(a, out, log):
    models = {}
    for k, P in PILES.items():
        m, c = fit_edge(a, P['edge_cols'])
        prof = profile(a, P['prof_cols'], m, c)
        x0, y0, x1, y1 = P['box']
        B = render_model(P['box'], m, c, prof)            # 무더기 없는 「밑선 + 초록 + 베이지」 본
        sub = a[y0:y1, x0:x1]
        dev = np.abs(sub - B).max(2)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        R_, G_ = sub[..., 0], sub[..., 1]
        seed = (R_ - G_ > 45) & (R_ > 110) & ((yy - (m * xx + c)) > -2)   # 밑선 위/아래의 무더기 구슬
        core = (dev > 28).astype(np.uint8)
        n, lab = cv2.connectedComponents(core, connectivity=8)
        keep = np.zeros_like(core)
        for i in range(1, n):
            if (seed & (lab == i)).any():
                keep[lab == i] = 1
        zone = cv2.dilate(keep, disk(6)).astype(bool)
        mk = cv2.dilate(keep, disk(3)).astype(bool) | (zone & (dev > 8))   # 구슬 + 검은 테 + 흰 테
        mk = cv2.morphologyEx(mk.astype(np.uint8), cv2.MORPH_CLOSE, disk(2)).astype(bool)
        mk = cv2.dilate(mk.astype(np.uint8), disk(1)).astype(bool)
        prot = np.zeros_like(mk)
        for (bx, by) in P['protect_beads']:                  # 떨어지는 줄의 구슬은 건드리지 않음
            prot |= ((xx - bx) ** 2 + (yy - by) ** 2) <= 8.5 ** 2
        if 'corner' in P:                                    # 계단 왼 모서리 · 그 그늘
            prot |= (xx < P['corner'][0]) & (yy < P['corner'][1])
        mk &= ~prot
        assert not (mk[:3].any() or mk[-3:].any() or mk[:, :3].any() or mk[:, -3:].any())
        resid = sub - B
        rf = resid.copy()
        rf[mk] = 0
        rf[prot] = 0
        rh = harmonic_fill(rf, mk, 3000)                     # 둘레와의 작은 차이를 매끈히 이어 붙임
        s2 = out[y0:y1, x0:x1].copy()
        s2[mk] = (B + rh)[mk]
        out[y0:y1, x0:x1] = s2
        models[k] = (m, c)
        ys_, xs_ = np.where(mk)
        log.append('항목2: 무더기 %s 지움 — 화소 %d · 상자 [%d,%d,%d,%d] · 밑선 기울기 %.4f'
                   % (k, mk.sum(), xs_.min() + x0, ys_.min() + y0, xs_.max() - xs_.min() + 1,
                      ys_.max() - ys_.min() + 1, m))
    return out, models


def bead_patch(src, c=BEAD_SRC, R=6.6):
    cx, cy = c
    x0, y0 = int(cx) - 9, int(cy) - 9
    p = src[y0:y0 + 19, x0:x0 + 19].copy()
    yy, xx = np.mgrid[y0:y0 + 19, x0:x0 + 19]
    r = np.hypot(xx - cx, yy - cy)
    lum = p.mean(2)
    m = np.clip((R - r) / 1.0, 0, 1)
    m = np.where(r > 4.5, m * np.clip((170 - lum) / 40, 0, 1), m)   # 구슬 둘레의 베이지 흰 테는 빼고
    return x0 - cx, y0 - cy, p, m


def draw_slot(out, src, C, m, edge_c, Lx, Hup, Hdn, k, bead_off):
    """계단 밑선과 나란한 작은 틈(렌즈꼴): 바깥 = 검은 테, 속 = 갈색, 구슬은 앞 입술 뒤로 반쯤 잠긴다."""
    pad = 12
    x0 = int(np.floor(C[0] - Lx - pad)); x1 = int(np.ceil(C[0] + Lx + pad))
    y0 = int(np.floor(C[1] - Lx * abs(m) - pad - 8)); y1 = int(np.ceil(C[1] + Lx * abs(m) + pad))
    H4, W4 = (y1 - y0) * SS, (x1 - x0) * SS
    nrm = np.hypot(1, m)
    u = np.array([1, m]) / nrm            # 밑선 방향
    nv = np.array([-m, 1]) / nrm          # 밑선에 수직(보는 이 쪽 +)
    s = np.linspace(-Lx, Lx, 600)
    pr = np.clip(np.sin(np.pi * (s + Lx) / (2 * Lx)), 0, 1) ** 0.8
    Cc = np.array(C, float)
    up = Cc + s[:, None] * u - (Hup * pr)[:, None] * nv
    dn = Cc + s[:, None] * u + (Hdn * pr)[:, None] * nv
    poly = np.concatenate([up, dn[::-1]])
    p4 = ((poly - np.array([x0, y0])) * SS).astype(np.int32)
    ob = np.zeros((H4, W4), np.uint8)
    cv2.fillPoly(ob, [p4], 1)
    inn = cv2.erode(ob, disk(int(round(k * SS))))
    halo = cv2.dilate(ob, disk(int(round(1.6 * SS)))) & ~ob
    yy4, xx4 = np.mgrid[0:H4, 0:W4]
    px = (xx4 + 0.5) / SS + x0
    py = (yy4 + 0.5) / SS + y0
    ss_ = (px - C[0]) * u[0] + (py - C[1]) * u[1]
    dd_ = (px - C[0]) * nv[0] + (py - C[1]) * nv[1]
    prf = np.where(np.abs(ss_) < Lx, np.clip(np.sin(np.pi * (np.clip(ss_, -Lx, Lx) + Lx) / (2 * Lx)), 0, 1) ** 0.8, 0)
    vis = (dd_ < Hdn * prf - k) & (np.abs(ss_) < Lx - 1)      # 앞 입술(아래 테)보다 위 = 구슬이 보이는 곳
    Dn = lambda mm: cv2.resize(mm.astype(np.float32), (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    obd, innd, halod, visd = Dn(ob), Dn(inn), Dn(halo), Dn(vis)
    reg = out[y0:y1, x0:x1].copy()
    yy, xx = np.mgrid[y0:y1, x0:x1]
    halod = halod * np.clip(((yy - (m * xx + edge_c)) - 2.5) / 1.5, 0, 1)   # 계단 밑선 위로는 테 없음
    reg = reg * (1 - 0.85 * halod[..., None]) + np.clip(reg + LIFT, 0, 255) * (0.85 * halod[..., None])
    reg = reg * (1 - obd[..., None]) + BLACK * obd[..., None]
    reg = reg * (1 - innd[..., None]) + BROWN * innd[..., None]
    ox, oy, bp, bm = bead_patch(src)
    qx = int(round(C[0] + bead_off[0] + ox))
    qy = int(round(C[1] + bead_off[1] + oy))
    hh, ww = bm.shape
    sl = (slice(qy - y0, qy - y0 + hh), slice(qx - x0, qx - x0 + ww))
    al = bm * visd[sl]
    reg[sl] = reg[sl] * (1 - al[..., None]) + bp * al[..., None]
    out[y0:y1, x0:x1] = reg
    return out, (x0, y0, x1 - x0, y1 - y0)


def item2(a, out, log):
    out, models = restore_piles(a, out, log)
    for k, P in PILES.items():
        m, c = models[k]
        x = P['slot_x']
        C = (x, m * x + c + SLOT['dy'])
        out, bx = draw_slot(out, a, C, m, c, SLOT['Lx'], SLOT['Hup'], SLOT['Hdn'], SLOT['k'], SLOT['bead_off'])
        log.append('항목2: 틈 %s — 가운데 (%.1f,%.1f) · 길이 %.0f · 높이 %.1f · 구슬 1개 반쯤 잠김'
                   % (k, C[0], C[1], 2 * SLOT['Lx'], SLOT['Hup'] + SLOT['Hdn']))
    return out


# ───────────────────────────── 비교 조각 ─────────────────────────────
def get_font(sz):
    for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
              '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf']:
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def make_cmp(before, after, box, path, maxlong=1400, gap=12, top=40):
    x, y, w, h = box
    sc = min((maxlong - gap) / 2 / w, 8.0)
    pw, ph = int(round(w * sc)), int(round(h * sc))
    b = before.crop((x, y, x + w, y + h)).resize((pw, ph), Image.LANCZOS)
    a = after.crop((x, y, x + w, y + h)).resize((pw, ph), Image.LANCZOS)
    im = Image.new('RGB', (2 * pw + gap, ph + top), 'white')
    im.paste(b, (0, top))
    im.paste(a, (pw + gap, top))
    d = ImageDraw.Draw(im)
    f = get_font(26)
    d.text((8, 6), 'BEFORE', fill=(0, 0, 0), font=f)
    d.text((pw + gap + 8, 6), 'AFTER', fill=(0, 0, 0), font=f)
    im.save(path)
    return im.size


def changed_boxes(a8, o8, split_x=1300):
    ch = np.any(a8 != o8, axis=2)
    res = {}
    for name, sel in [('item1', np.s_[:, split_x:]), ('item2', np.s_[:, :split_x])]:
        m = np.zeros_like(ch)
        m[sel] = ch[sel]
        if m.any():
            ys, xs = np.where(m)
            res[name] = [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]
    return res, int(ch.sum())


def main():
    src_img = Image.open(SRC).convert('RGB')
    a = np.asarray(src_img).astype(np.float64)
    out = a.copy()
    log = []
    out = item1(a, out, log)
    out = item2(a, out, log)
    o8 = np.clip(np.round(out), 0, 255).astype(np.uint8)
    new_img = Image.fromarray(o8, 'RGB')
    assert new_img.size == (2048, 1144)
    new_img.save(OUT + 'final_new.png')
    print('cmp_1', make_cmp(src_img, new_img, (1540, 60, 420, 300), OUT + 'cmp_1.png'))
    print('cmp_2', make_cmp(src_img, new_img, (850, 640, 190, 130), OUT + 'cmp_2.png'))
    boxes, n = changed_boxes(np.asarray(src_img), o8)
    for s in log:
        print(s)
    print('달라진 자리:', boxes, '· 달라진 화소 수', n)


if __name__ == '__main__':
    main()

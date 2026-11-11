#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L11d 그림 고침 (PIL · numpy · cv2 만 씀)
  원본 : SP/L11d/r1/final_v1.png   (읽기만)
  결과 : SP/picfix/L11d/final_new.png  + cmp_1.png · cmp_2.png

항목 1  굴뚝집 고리(미토콘드리아 환형 DNA)의 오른쪽 아래 틈을 메워 완전히 닫힌 고리로.
        인부가 들고 있던 판자(+ 판자 밑 막대 · 흰 테)를 지우고, 두 손은 닫힌 고리 위에 얹힌 모습.
  방법  고리는 세로축 x=1734.5 에 대칭인 입체 고리(윗면 방사형 판자 + 아래쪽 바깥 옆면 띠)다.
        왼쪽 고리를 거울로 뒤집어 오른쪽 아래에 깔되, '원 공간'(중심 (1734.5,630), 세로 x1.55)에서
        - 각도: 거울의 이음줄 m5.5 → 팔 사이 원본 이음줄 B, 거울 이음줄 m42.3 → 원본 고리 끝면 선
          에 오도록 그 사이를 선형으로 눌러 붙이고(판자 3장, 압축 약 17~21%),
        - 반지름: 안 테두리 · 윗면 바깥 윤곽 · 옆면 띠 아래 윤곽을 기준으로 정규화해
          띠의 자리 · 두께가 그 각도의 자연스러운 값(아래 이음매 근처는 원본 오른쪽 값)이 되게 한다.
        원본 끝면 선은 그대로 남아 판자 사이 이음줄이 되고, 옆면 띠는 x>=1884 부터 거울 띠로 바뀐다
        (원본의 굵은 띠 끝 막대 대신 가는 띠 이음 자국).
        바닥(잔디 · 인부 그림자 · 구멍 초록)은 원본의 깨끗한 픽셀을 그대로 쓰고, 판자가 덮던 곳만
        주변에서 메운다(inpaint). 인부(두 손 · 두 소매 · 소매 끝 옅은 줄)는 원본 픽셀 그대로 위에 얹는다.
항목 2  담장 오른쪽 아래의 갈색(판자처럼 보이는) 띠 조각들을 담장 돌 색으로 바꾼다.
        윤곽선은 그대로 두고, 갈색→돌 색 차이를 밝기 비례로 더한다(번짐 · 하이라이트 관계 유지).
"""
import os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = SP + '/L11d/r1/final_v1.png'
OUTDIR = SP + '/picfix/L11d'
OUT = OUTDIR + '/final_new.png'

# ----------------------------------------------------------------------------- geometry
CX, CY, K = 1734.5, 630.0, 1.55          # ring centre ; circle space v = (y-CY)*K


def m55(r):                               # mirror seam (circle-space angle, deg) vs radius
    return 7.028 + 0.0537 * (r - 158)


def m423(r):
    return 43.767 + 0.02685 * (r - 158)


def red(r):                               # original ring end cut (kept, becomes a seam)
    return 39.956 + 0.01177 * (r - 158)


def ab(r):                                # original seam B between the arms (kept)
    return 10.6 + 0.0537 * (r - 165.8)


# natural radii of the mirrored ring per angle (measured on the mirror image)
TH_T = np.array([-20, 0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 50, 56, 60, 90.])
RE_T = np.array([193.4, 193.5, 194.0, 195.1, 196.3, 197.4, 198.5, 199.6, 201.2, 203.6, 205.6,
                 207.2, 209.0, 212.0, 214.6, 216.5, 230.])          # top-surface outer outline
TB_T = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 2.25, 4.5, 6.3, 7.0, 7.6, 9.0, 9.8, 11.0, 12.0,
                 12.5, 15.])                                         # side-band thickness


def r_in_pm(th):
    return 119.5 - 0.07 * np.clip(th, 0, 90)


def r_e_pm(th):
    return np.interp(th, TH_T, RE_T)


def t_pm(th):
    return np.interp(th, TH_T, TB_T)


def sstep(x, a, b):
    s = np.clip((x - a) / (b - a), 0, 1)
    return s * s * (3 - 2 * s)


def r_e_d(th):                            # destination: toward the original right side near the joint
    return r_e_pm(th) - 0.5 * sstep(th, 28, 40)


def t_d(th):
    return t_pm(th) - 1.1 * sstep(th, 28, 40)


def comps(m, minsize):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    out = np.zeros_like(m)
    for i in range(1, n):
        if st[i, 4] >= minsize:
            out |= (lab == i)
    return out


# ----------------------------------------------------------------------------- item 1
def item1(im):
    H, W = im.shape[:2]
    X0, Y0, X1, Y1 = 1795, 600, 1950, 760
    sub = im[Y0:Y1, X0:X1].copy()
    h, w = sub.shape[:2]
    yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float64)
    u = xx - CX
    v = (yy - CY) * K
    th = np.degrees(np.arctan2(v, u))
    r = np.hypot(u, v)

    # --- angular map dest -> source (mirror) ---
    rc = np.clip(r, 118, 205)
    a0, a1 = ab(rc), red(rc)
    s0, s1 = m55(rc), m423(rc)
    t = (th - a0) / (a1 - a0)
    ths = np.where(t < 0, th + (s0 - a0), np.where(t > 1, th + (s1 - a1), s0 + t * (s1 - s0)))
    # --- radial normalisation (inner edge / outer outline / side band) ---
    ri_d, re_d, tb_d = r_in_pm(th), r_e_d(th), t_d(th)
    ri_s, re_s, tb_s = r_in_pm(ths), r_e_pm(ths), t_pm(ths)
    rs = np.where(r < ri_d, r - ri_d + ri_s,
         np.where(r < re_d, ri_s + (r - ri_d) * (re_s - ri_s) / (re_d - ri_d),
         np.where(r < re_d + tb_d, re_s + (r - re_d) * tb_s / tb_d,
                  r - (re_d + tb_d) + (re_s + tb_s))))
    xm = CX + rs * np.cos(np.radians(ths))
    ym = CY + rs * np.sin(np.radians(ths)) / K
    Wm = cv2.remap(im, (2 * CX - xm).astype(np.float32), ym.astype(np.float32),
                   cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    Wm = np.clip(Wm, 0, 255)

    # --- region P (soft, ~1 px feather) ---
    gy, gx = np.gradient(t)
    gt = np.hypot(gx, gy) + 1e-9
    ext = np.clip((r - 182) / 14.0, 0, 1) * 0.30            # near the rim: reach up under the sleeve
    pa = np.clip((t + ext) / gt + 0.5, 0, 1)                 # below seam B
    pb_top = np.clip((1 - t) / gt + 0.5, 0, 1)               # above the end cut (centre line)
    pb_rim = np.clip((xx - 1884.0) + 0.5, 0, 1)              # rim + side band: from x=1884
    rim_w = sstep(r - re_d, -2.5, -1.0) * (th > 30)
    pb = pb_top * (1 - rim_w) + np.maximum(pb_top, pb_rim) * rim_w
    prad = np.clip((r - 86) + 0.5, 0, 1) * np.clip((226 - r) + 0.5, 0, 1)
    pxl = np.clip((1931.5 - xx) + 0.5, 0, 1)                 # never reach the legs / shoe
    P_ring = pa * pb * prad * pxl
    # hole side: the board's left end + outline + white halo left in the hole
    poly = np.array([[1810, 650], [1816, 639], [1826, 632], [1847, 632], [1849, 640], [1854, 645],
                     [1846, 672], [1840, 676], [1822, 676], [1811, 678]], np.int32)
    pm_hole = np.zeros((h, w), np.uint8)
    cv2.fillPoly(pm_hole, [poly - np.array([X0, Y0])], 1)
    pm_hole = np.clip(cv2.GaussianBlur(pm_hole.astype(np.float32), (0, 0), 0.7), 0, 1)
    P = np.maximum(P_ring, pm_hole)

    # --- ground (grass / worker shadow / hole green): original where clean, else inpainted ---
    R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]
    green = (G - R > 20) & (G - B > 40)
    dng = cv2.distanceTransform(green.astype(np.uint8), cv2.DIST_L2, 5)
    clean = green & (dng >= np.where(r < 112, 7.5, 4.5))   # hole side: also drop the board's faint ringing
    GD = cv2.inpaint(np.clip(sub, 0, 255).astype(np.uint8), (~clean).astype(np.uint8) * 255, 6,
                     cv2.INPAINT_TELEA).astype(np.float32)
    GD = np.where(clean[..., None], sub, GD)

    # --- new ring over ground: ring pixels from the warped mirror, its edge blended onto ground ---
    mR, mG, mB = Wm[..., 0], Wm[..., 1], Wm[..., 2]
    g = np.clip((mG - mB - 20) / 80.0, 0, 1) * np.clip((mG - mR - 10) / 40.0, 0, 1)
    GSRC = np.array([149., 204., 101.], np.float32)
    wgreen = (mG - mR > 20) & (mG - mB > 40)
    n, lab = cv2.connectedComponents((~wgreen).astype(np.uint8), connectivity=8)
    sil = (lab == lab[690 - Y0, 1870 - X0])
    dsil = cv2.distanceTransform((~sil).astype(np.uint8), cv2.DIST_L2, 5)
    ratio = np.clip(Wm / GSRC, 0, 1.25)
    near = np.clip((3.5 - dsil) / 1.0, 0, 1)[..., None]
    ground_mod = GD * (near * ratio + (1 - near))
    newbg = Wm * (1 - g[..., None]) + ground_mod * g[..., None]
    newbg = np.where((dsil > 3.5)[..., None], GD, newbg)

    # --- worker matte: hands, sleeves (+ the light cuff edge) kept from the original on top ---
    Rf, Gf, Bf = im[..., 0], im[..., 1], im[..., 2]
    Lf = im.mean(2)
    box = np.zeros((H, W), bool)
    box[Y0:Y1, X0:X1] = True
    skin = (Rf > 190) & (Lf > 170) & ((Rf - Bf) < 95) & (Rf > Gf) & box
    sleeve = (Bf > Rf + 4) & (Gf > Rf) & (Lf > 95) & (Lf < 215) & box
    skin_big = comps(skin, 25)
    sleeve_big = comps(sleeve, 60)
    dsk = cv2.distanceTransform((~skin_big).astype(np.uint8), cv2.DIST_L2, 5)
    n, lab, st, _ = cv2.connectedComponentsWithStats(skin.astype(np.uint8), connectivity=8)
    skin_all = skin_big.copy()
    for i in range(1, n):                                    # fingertips split off by an outline
        cm = (lab == i)
        if st[i, 4] >= 4 and dsk[cm].min() <= 5.5:
            skin_all |= cm
    cuff = np.zeros((H, W), bool)
    cuff[662:677, 1914:1921] = True
    sat = im.max(2) - im.min(2)
    cuff &= (Lf > 90) & (sat < 30) & ((Gf - Rf) < 12)
    fill = (skin_all | sleeve_big | cuff)[Y0:Y1, X0:X1].astype(np.uint8)
    fill = cv2.morphologyEx(fill, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    ff = fill.copy()
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 1)
    fill = fill.astype(bool) | (ff == 0)
    dfill = cv2.distanceTransform((~fill).astype(np.uint8), cv2.DIST_L2, 5)
    dark = np.clip((150 - sub.mean(2)) / (150 - 10), 0, 1)
    DMAX = 3.7                                               # outline of the hands / sleeves
    aw = np.where(dfill <= 1.5, 1.0, dark * np.clip((DMAX - dfill) / 1.0, 0, 1))
    DARK = np.array([8., 5., 4.], np.float32)
    wl = np.where((dfill <= 1.5)[..., None], sub, DARK)
    comp = aw[..., None] * wl + (1 - aw[..., None]) * newbg

    outsub = P[..., None] * comp + (1 - P[..., None]) * sub
    out = im.copy()
    out[Y0:Y1, X0:X1] = outsub
    keep = np.ones((H, W), bool)
    keep[Y0:Y1, X0:X1] = (P <= 0)
    out[keep] = im[keep]
    return out


# ----------------------------------------------------------------------------- item 2
def item2(src, base):
    H, W = src.shape[:2]
    R, G, B = src[..., 0], src[..., 1], src[..., 2]
    L = src.mean(2)
    box = np.zeros((H, W), bool)
    box[788:1144, 1527:1666] = True                          # below the ring, right of the stone column
    reg = box & ~(G > R + 3)                                 # never touch grass / grass-outline blends
    STONE = np.array([177.4, 169.8, 152.3], np.float32)     # stone column fill
    BROWN = np.array([157.3, 140.0, 110.1], np.float32)     # brown band fill
    wgt = np.clip(L / BROWN.mean(), 0, 1)                    # dark outline -> ~no shift
    hue = (R - B) / np.maximum(L, 1.0)                       # stone/grey <= 0.16 , tan/brown >= 0.24
    whue = np.clip((hue - 0.16) / 0.08, 0, 1)
    shifted = np.clip(src + (STONE - BROWN) * (wgt * whue)[..., None], 0, 255)
    out = base.copy()
    out[reg] = shifted[reg]
    return out


# ----------------------------------------------------------------------------- comparison sheets
def cmp_sheet(before, after, box, path, maxw=1400):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gap, top = 12, 44
    sc = min((maxw - gap) / (2 * w), 1400 / (h + top))
    pw, ph = int(w * sc), int(h * sc)
    A = Image.fromarray(before).crop(box).resize((pw, ph), Image.LANCZOS)
    B = Image.fromarray(after).crop(box).resize((pw, ph), Image.LANCZOS)
    sheet = Image.new('RGB', (2 * pw + gap, ph + top), (255, 255, 255))
    sheet.paste(A, (0, top))
    sheet.paste(B, (pw + gap, top))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
    except Exception:
        f = ImageFont.load_default()
    d.text((10, 7), 'BEFORE', fill=(0, 0, 0), font=f)
    d.text((pw + gap + 10, 7), 'AFTER', fill=(0, 0, 0), font=f)
    sheet.save(path)


def bbox(diff):
    ys, xs = np.nonzero(diff)
    if not len(xs):
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]


def main():
    src8 = np.asarray(Image.open(SRC).convert('RGB'))
    assert src8.shape == (1144, 2048, 3)
    im = src8.astype(np.float32)
    o1 = item1(im)
    o2 = item2(im, o1)
    out8 = np.clip(np.rint(o2), 0, 255).astype(np.uint8)
    Image.fromarray(out8, 'RGB').save(OUT)

    o1_8 = np.clip(np.rint(o1), 0, 255).astype(np.uint8)
    d1 = np.abs(o1_8.astype(int) - src8.astype(int)).max(2) > 0
    d2 = np.abs(out8.astype(int) - o1_8.astype(int)).max(2) > 0
    dall = np.abs(out8.astype(int) - src8.astype(int)).max(2) > 0
    print('item1 changed px', int(d1.sum()), 'bbox [x,y,w,h]', bbox(d1))
    print('item2 changed px', int(d2.sum()), 'bbox [x,y,w,h]', bbox(d2))
    print('all   changed px', int(dall.sum()), 'bbox [x,y,w,h]', bbox(dall))

    cmp_sheet(src8, out8, (1700, 565, 1960, 770), OUTDIR + '/cmp_1.png')
    cmp_sheet(src8, out8, (1470, 760, 1690, 1144), OUTDIR + '/cmp_2.png')


if __name__ == '__main__':
    main()

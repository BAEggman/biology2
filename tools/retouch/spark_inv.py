#!/usr/bin/env python3
"""spark_inv.py — 제미나이 반짝이 별을 **덧씌움 되돌림**으로 지운다(별 밑의 결 · 선 · 물건을 그대로 살림 — 결 복제 spark_clone 이
옮겨 붙일 데가 없는 판: 신발 · 바지 · 바구니 · 물방울 판 · 바위 위의 별).

별 = 반투명 흰 네 꼭지 별 (|x|/R)^p + (|y|/R)^p ≤ 1 · p 0.69 · 1024 정사각에서 중심 (903.5, 903.5) · R ≈ 25.4
     (넓은 판은 sparkfind 가 찾은 자리 — 여백/R ≈ 4.74).
10/2 에 잰 것:
  · 별 안 알파는 고르다 — 지우기 전 원본 40여 장의 알파 지도를 판마다 별 안 중앙값으로 나눠 화소마다 가중 중앙값을 내면
    안 1.00 ± 0.05 · 가장자리는 해석식 윤곽과 겹친다.
  · 덧씌움은 **sRGB 값에서** 흰색 쪽으로 a 만큼: I′ = I + a(255 − I). s22p03 은 별 안 먹선(둘레 3% 분위 5 → 안 126)과
    크림(180 → 214)이 같은 a 0.45~0.48 을 준다(선형 빛으로 보면 0.21 · 0.44 로 갈림).
  · 가장자리 무름이 판마다 다르다(σ 0.5~2.5px — 판이 거친 크기 바꿈 · 다시 그리기). 끝 뾰족 부분은 더 흐리다.
  · a 는 판마다 0.2~0.85(별이 겹친 판은 짙다). 한 판 안에서는 하나.
방법:
  ① 자리: 주어진 (cx, cy, R) 둘레 ±0.5px · R ±1 에서 윤곽 안 1.5px − 밖 1.5px 차 중앙값이 가장 큰 것.
  ② 가장자리 옆모습: 윤곽 법선을 따라 깊이 −6..+8px 마다 (I(d) − I(밖 7px))/(255 − I(밖 7px)) 의 가중 중앙값을 재고,
     「바깥으로 e px 넓힌 별을 두 가우스 섞음 (1−β)G(σ1) + βG(σ2) 로 무르게 한 틀」의 같은 옆모습과 맞춘다(e · σ1 · β · σ2 격자).
  ③ a 고르기 — 옆모습 맞춤의 a 는 크림처럼 밝은 바탕에서 크게 흔들린다(s12p01 0.96 · 실제 ≈ 0.5). 그래서 a 를 0..0.9 에서 훑으며
     되돌린 그림을 (가) 윤곽 건너 밝기 차(깊이 1.5 · 3px 짝 차 중앙값의 절댓값)와 (나) 별 안 색이 둘레(별 밖 4..30px)에 없는 색인가
     (안 화소마다 둘레 색 가운데 가장 가까운 것까지 거리의 90% 분위 — 지나친 되돌림의 주황 · 올리브 · 검정 얼룩)로 재어
     (가) + AW·(나) 가 가장 작은 a (AW 기본 1 — 얼룩보다 남은 별이 낫다).
  ④ 되돌림: I = (I′ − 255·a·Mb)/(1 − a·Mb).
  ⑤ 톤 맞춤: 안 2.5px · 밖 2.5px 짝 차를 윤곽 따라 이동 중앙값(±25점)으로 고르고 역거리 가중으로 안을 메워 더함(±10 으로 자름) —
     되돌림이 압축 색차를 함께 키워 남던 노르스름한 마름모(s42p01)를 지운다.
  ⑥ 잡음: 별 안만 비국소 평균, 섞는 무게 = (그 자리 키움 − 1)/(최대 키움 − 1).
  ⑦ 윤곽 띠(|부호거리| ≤ 1.5px): 윤곽 법선 방향 7점(±3px) 중앙값 — 윤곽과 나란한 가는 테와 끝 뾰족 부분의 남은 밝기를 지운다.
     ★ 선 지키기: **원본(별 있는)에서도** 법선 중앙값보다 15 넘게 어두웠던 화소는 진짜 선이라 그대로 둔다(흰 덧씌움은 대비를 줄일 뿐
     뒤집지 않는다). 첫 판은 이것이 없어 윤곽을 비스듬히 지나는 먹선을 판마다 40~90화소 지웠다(10/2). 이어 띠의 색차(Cb · Cr)만 5×5 중앙값
     (--chroma N: 별 안 전체 색차를 N×N 중앙값 — 짙은 별 밑의 무지개 얼룩).
  ⑦′ 밝아짐 막기: 흰 덧씌움을 걷으면 화소는 어두워지기만 한다 — 결과가 원본보다 6 넘게 밝은 화소는 되돌림 직후 값으로.
     --keepdark L: 원본 밝기 < L 인 물건(+1px)은 원본 그대로(별이 물건 끝에 살짝 걸친 판 — s19p02l 짚).
  ⑧ 거르기: a < 0.04 이거나 윤곽 건너 차가 절반 넘게 줄지 않으면 「별 아님」 — 그대로 둔다.
한계(10/2): a > 0.7 인 별이 흰 · 크림 물건 위에 앉은 판(s43p02 탁자 다리 · s18p01)은 키움이 커 얼룩이 남고,
     별 둘이 겹친 판(s34p04)은 둘째 별이 남는다 — 판마다 따로.
사용: python3 spark_inv.py SRC.png OUT.png cx,cy,R [--cmp CMP.png] [--a A] [--e E --s1 S1 --beta B --s2 S2] [--aw W] [--tone T]
      [--band B] [--h H] [--minred F] [--fix] [--verbose]"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import cv2

P = 0.69
SS = 8


def star(R, cx, cy, x0, y0, w, h):
    ys = (np.arange(h * SS) + 0.5) / SS - 0.5 + y0
    xs = (np.arange(w * SS) + 0.5) / SS - 0.5 + x0
    XX, YY = np.meshgrid(xs, ys)
    m = ((np.abs(XX - cx) / R) ** P + (np.abs(YY - cy) / R) ** P <= 1).astype(np.float64)
    return m.reshape(h, SS, w, SS).mean(axis=(1, 3))


def contour(R, cx, cy, depth, x0=0, y0=0, frac=0.62):
    """윤곽 위 점(끝 뾰족 부분 빼고 |x|,|y| ≤ frac·R)과 바깥 법선 — 안 · 밖 depth px 자리 (행, 열)"""
    th = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
    ct, st = np.cos(th), np.sin(th)
    X = np.sign(ct) * R * np.abs(ct) ** (2 / P); Y = np.sign(st) * R * np.abs(st) ** (2 / P)
    keep = (np.abs(X) <= frac * R) & (np.abs(Y) <= frac * R) & (np.abs(X) > 0.5) & (np.abs(Y) > 0.5)
    X, Y = X[keep], Y[keep]
    gx = np.sign(X) * (np.abs(X) / R) ** (P - 1); gy = np.sign(Y) * (np.abs(Y) / R) ** (P - 1)
    n = np.hypot(gx, gy); gx, gy = gx / n, gy / n
    pin = (cy + Y - gy * depth - y0, cx + X - gx * depth - x0)
    pout = (cy + Y + gy * depth - y0, cx + X + gx * depth - x0)
    return pin, pout


def samp(img, pts):
    return np.stack([ndi.map_coordinates(img[..., k], pts, order=1, mode='nearest') for k in range(3)], axis=1)


def sd_field(R, cx, cy, x0, y0, w, h, ss=4):
    """해석식 별의 부호 거리(px, 안 +) — ss 배 덧표본"""
    ys = (np.arange(h * ss) + 0.5) / ss - 0.5 + y0
    xs = (np.arange(w * ss) + 0.5) / ss - 0.5 + x0
    XX, YY = np.meshgrid(xs, ys)
    ins = ((np.abs(XX - cx) / R) ** P + (np.abs(YY - cy) / R) ** P) <= 1
    return (ndi.distance_transform_edt(ins) - ndi.distance_transform_edt(~ins)) / ss


def edge_model(SD, e, s1, s2, beta, ss=4):
    """가장자리를 바깥으로 e px 옮긴 별(덧표본 → 화소 덮임)을 두 가우스 섞음으로 무르게: (1−β)G(s1) + βG(s2)"""
    m = (SD > -e).astype(np.float64)
    hh, ww = m.shape[0] // ss, m.shape[1] // ss
    M0 = m.reshape(hh, ss, ww, ss).mean(axis=(1, 3))
    Mb = (1 - beta) * ndi.gaussian_filter(M0, s1)
    if beta > 0:
        Mb += beta * ndi.gaussian_filter(M0, s2)
    return Mb


DEPTHS = np.arange(-6, 8.01, 0.5)


def measure_profile(img, R, cx, cy, x0, y0, ref=7.0):
    """윤곽 법선을 따라 깊이 d(안 +)마다 (I(d) − I(밖 ref)) / (255 − I(밖 ref)) 의 가중 중앙값"""
    _, pref = contour(R, cx, cy, ref, x0, y0)
    Iref = samp(img, pref)
    wgt = 255 - Iref
    prof = []
    for d in DEPTHS:
        pin, pout = contour(R, cx, cy, abs(d), x0, y0)
        Iv = samp(img, pin if d >= 0 else pout)
        a = (Iv - Iref) / np.maximum(wgt, 1)
        ok = wgt > 25
        av, wv = a[ok], wgt[ok]
        if len(av) < 20:
            return None
        o = np.argsort(av); cw = np.cumsum(wv[o])
        prof.append(float(av[o][np.searchsorted(cw, cw[-1] / 2)]))
    return np.array(prof)


def model_profile(Mb, R, cx, cy, x0, y0):
    out = []
    for d in DEPTHS:
        pin, pout = contour(R, cx, cy, abs(d), x0, y0)
        v = ndi.map_coordinates(Mb, pin if d >= 0 else pout, order=1, mode='nearest')
        out.append(float(np.median(v)))
    return np.array(out)


def alpha_mode(Ic, G, R, cx, cy, x0, y0, depth=3.0):
    pin, pout = contour(R, cx, cy, depth, x0, y0)
    gi = ndi.map_coordinates(G, pin, order=1); go = ndi.map_coordinates(G, pout, order=1)
    Ii, Io = samp(Ic, pin), samp(Ic, pout)
    d = 255 - Io
    a = (Ii - Io) / np.maximum(d, 1)
    for gthr in (6, 10, 16):
        flat = (gi < gthr) & (go < gthr)
        ok = flat[:, None] & (d > 20)
        if ok.sum() >= 60:
            av, wv = a[ok], d[ok]
            xs = np.arange(-0.2, 0.97, 0.005)
            kde = np.array([(wv * np.exp(-0.5 * ((av - x) / 0.03) ** 2)).sum() for x in xs])
            k = int(np.argmax(kde))
            # 최빈값 둘레 ±0.06 안 짝의 가중 평균으로 다듬기
            sel = np.abs(av - xs[k]) < 0.06
            return float((av[sel] * wv[sel]).sum() / wv[sel].sum()), int(flat.sum()), gthr
    return float('nan'), 0, None


def alpha_ink(Ic, R, cx, cy, x0, y0):
    h, w = Ic.shape[:2]
    L = Ic.mean(axis=2)
    core = star(R * 0.85, cx, cy, x0, y0, w, h) > 0.99
    M = star(R, cx, cy, x0, y0, w, h) > 0.01
    ring = ndi.binary_dilation(M, iterations=22) & ~ndi.binary_dilation(M, iterations=4)
    pi_, po_ = np.percentile(L[core], 3), np.percentile(L[ring], 3)
    if po_ > 60 or pi_ < po_:
        return float('nan')
    return float((pi_ - po_) / (255 - po_))


def main():
    args = sys.argv[1:]
    src, dst = args[0], args[1]
    cx0, cy0, R0 = (float(v) for v in args[2].split(','))
    opt = lambda k, d=None, f=float: f(args[args.index(k) + 1]) if k in args else d
    A0 = opt('--a'); Hh = opt('--h'); CMP = opt('--cmp', None, str)
    MINRED = opt('--minred', 0.5)
    FIX = '--fix' in args
    E0 = opt('--e'); S1 = opt('--s1'); S2 = opt('--s2'); B0 = opt('--beta')
    BAND = opt('--band', 1.5)
    AW = opt('--aw', 1.0)            # 낯선색 무게
    TONE = opt('--tone', 10.0)       # 톤 맞춤 한도(RGB) — 0 이면 끔
    CHROMA = opt('--chroma', 0.0)    # > 0 이면 별 안 전체 색차를 그 크기 중앙값으로
    KEEPDARK = opt('--keepdark', 0.0)  # > 0 이면 원본 밝기가 그보다 낮은 화소(+1px)는 원본 그대로

    I = np.asarray(Image.open(src).convert('RGB')).astype(np.float64)
    H, W = I.shape[:2]
    hb = int(R0 * 1.5) + 14
    x0, y0 = max(0, int(cx0) - hb), max(0, int(cy0) - hb)
    x1, y1 = min(W, int(cx0) + hb), min(H, int(cy0) + hb)
    Ic = I[y0:y1, x0:x1]
    h, w = Ic.shape[:2]
    G = ndi.gaussian_gradient_magnitude(Ic.mean(axis=2), 1.0)

    # ① 자리 다듬기: 해석식 대비(안 2px − 밖 2px)가 가장 큰 중심 ±0.5 · R ±1 (fit 은 윤곽 기준을 정할 뿐 — 무름 · 넓힘은 ②에서)
    R, cx, cy = R0, cx0, cy0
    if not FIX:
        best = None
        for dR in (-1.0, -0.5, 0.0, 0.5, 1.0):
            for dx in (-0.5, 0.0, 0.5):
                for dy in (-0.5, 0.0, 0.5):
                    pin, pout = contour(R0 + dR, cx0 + dx, cy0 + dy, 1.5, x0, y0)
                    di = samp(Ic, pin).mean(axis=1) - samp(Ic, pout).mean(axis=1)
                    c = float(np.median(di))
                    if best is None or c > best[0]:
                        best = (c, R0 + dR, cx0 + dx, cy0 + dy)
        _, R, cx, cy = best
    # ② 가장자리 옆모습 재기 → 두 가우스 섞음 무름 + 넓힘 e + 알파 맞추기
    prof = measure_profile(Ic, R, cx, cy, x0, y0)
    SD = sd_field(R, cx, cy, x0, y0, w, h)
    fit = None
    if prof is not None:
        es = [E0] if E0 is not None else list(np.arange(-3.0, 2.01, 0.25))
        s1s = [S1] if S1 is not None else [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5]
        bs = [B0] if B0 is not None else [0.0, 0.15, 0.3]
        s2s = [S2] if S2 is not None else [3.0, 5.0]
        for e in es:
            for s1 in s1s:
                for beta in bs:
                    for s2 in (s2s if beta > 0 else [0.0]):
                        Mb = edge_model(SD, e, s1, s2, beta)
                        mp = model_profile(Mb, R, cx, cy, x0, y0)
                        a = float((prof * mp).sum() / max((mp * mp).sum(), 1e-9)) if A0 is None else A0
                        err = float(((prof - a * mp) ** 2).sum())
                        if fit is None or err < fit[0]:
                            fit = (err, a, e, s1, s2, beta)
    if fit is None:
        print('옆모습을 못 잼 — 그대로 둠'); Image.fromarray(I.astype(np.uint8)).save(dst); return
    err, A_fit, e, s1, s2, beta = fit
    Mb = edge_model(SD, e, s1, s2, beta)
    # ②′ a 고르기 — 옆모습 맞춤의 a 는 크림처럼 밝은 바탕(255 − 밖 이 작다)에서 크게 흔들린다(s12p01 0.96 · 실제 ≈ 0.5).
    #     그래서 a 를 0..0.9 에서 훑으며 되돌린 그림을 **두 잣대**로 잰다:
    #       (가) 윤곽 건너 밝기 차(깊이 1.5 · 3px 짝 차의 중앙값 절댓값 — 별이 남거나 파이면 커진다)
    #       (나) 별 안 색이 둘레(별 밖 4..30px)에 없는 색인가 — 안 화소마다 둘레 색 가운데 가장 가까운 것까지 거리의 90% 분위
    #            (지나친 되돌림은 주황 · 올리브 · 검정 얼룩을 만든다 — 둘레에 없는 색)
    #     점수 = (가) + AW × (나) 가 가장 작은 a (AW 기본 1 — 얼룩보다 남은 별이 낫다).
    from scipy.spatial import cKDTree
    SDp0 = SD.reshape(h, 4, w, 4).mean(axis=(1, 3))
    ringm = (SDp0 < -4 - e) & (SDp0 > -30 - e)
    rc = Ic[ringm]
    if len(rc) > 4000:
        rc = rc[np.random.RandomState(0).choice(len(rc), 4000, replace=False)]
    tree = cKDTree(rc)
    insm = Mb > 0.3

    def score(A_):
        aM_ = (A_ * Mb)[..., None]
        J_ = (Ic - 255.0 * aM_) / np.maximum(1 - aM_, 0.05)
        st = 0.0
        for dep in (1.5, 3.0):
            pin, pout = contour(R, cx, cy, dep, x0, y0)
            di = samp(J_, pin).mean(axis=1) - samp(J_, pout).mean(axis=1)
            st += abs(float(np.median(di)))
        dist = tree.query(np.clip(J_[insm], -60, 320), k=1)[0]
        an = float(np.percentile(dist, 90))
        return st + AW * an, st, an

    if A0 is None:
        cands = []
        for A_ in np.arange(0.0, 0.901, 0.02):
            sc_ = score(A_)
            cands.append((sc_[0], A_, sc_[1], sc_[2]))
        if '--verbose' in args:
            print('  a     score  윤곽차  낯선색')
            for c_ in cands:
                print('  %.2f  %6.1f  %6.1f  %6.1f' % (c_[1], c_[0], c_[2], c_[3]))
        best_sc = min(cands)
        lo = best_sc[1]
        for A_ in np.arange(max(0, lo - 0.02), min(0.9, lo + 0.02) + 1e-9, 0.005):
            sc_ = score(A_)
            if sc_[0] < best_sc[0]:
                best_sc = (sc_[0], A_, sc_[1], sc_[2])
        A = float(best_sc[1])
        sc0 = score(0.0)
        SCORE = (sc0, best_sc)
    else:
        A = A0
        SCORE = (score(0.0), (None, A0) + score(A0)[1:])
    aM = (A * Mb)[..., None]
    J = (Ic - 255.0 * aM) / np.maximum(1 - aM, 0.05)
    J_raw = J.copy()
    prof_after = measure_profile(J, R, cx, cy, x0, y0)
    r0 = float(np.abs(prof).max()); r1 = float(np.abs(prof_after).max()) if prof_after is not None else float('nan')
    info = 'R %.2f c (%.2f, %.2f)  a %.3f (옆모습 맞춤 %.2f)  넓힘 %+.2f  무름 %.2f(+%.0f%% σ%.0f)  옆모습 최대 %.2f → %.2f  맞춤 오차 %.3f  윤곽차 %.1f → %.1f  낯선색 %.1f → %.1f' % (
        R, cx, cy, A, A_fit, e, s1, beta * 100, s2, r0, r1, err, SCORE[0][1], SCORE[1][2], SCORE[0][2], SCORE[1][3])
    if A0 is None and (A < 0.04 or SCORE[1][2] > (1 - MINRED) * SCORE[0][1]):
        print('별 아님(또는 너무 흐림) — 그대로 둠 | ' + info)
        Image.fromarray(I.astype(np.uint8)).save(dst)
        return
    # ②″ 톤 맞춤: 되돌린 안쪽(깊이 2.5px)과 바깥(2.5px) 짝 차를 윤곽을 따라 이동 중앙값(±25점)으로 고르고,
    #     안쪽 화소마다 윤곽 점들의 역거리 가중 평균으로 메워 더한다(±TONE 로 자름 — 물건이 별 안에 든 판에서 물건 색을 끌어가지 않게).
    #     되돌림의 남은 색조(키움이 압축 색차를 함께 키워 노르스름 · 푸르스름한 마름모가 남던 것 — s42p01)를 지운다.
    if TONE > 0:
        pin, pout = contour(R, cx, cy, 2.5, x0, y0, frac=0.9)
        dd = samp(Ic, pout) - samp(J, pin)
        n_ = len(dd)
        if n_ > 60:
            k_ = 25
            ext = np.concatenate([dd[-k_:], dd, dd[:k_]], axis=0)
            sm = np.array([np.median(ext[i:i + 2 * k_ + 1], axis=0) for i in range(n_)])
            sm = np.clip(sm, -TONE, TONE)
            py_, px_ = pin
            yy, xx = np.mgrid[0:h, 0:w]
            sel = Mb > 0.02
            qy, qx = yy[sel], xx[sel]
            d2 = (qy[:, None] - py_[None, :]) ** 2 + (qx[:, None] - px_[None, :]) ** 2
            wt = 1.0 / (d2 + 4.0)
            Cf = (wt @ sm) / wt.sum(axis=1, keepdims=True)
            Cimg = np.zeros((h, w, 3)); Cimg[sel] = Cf
            J = J + Cimg * np.clip(Mb / 0.5, 0, 1)[..., None]
    # ③ 잡음
    amp = 1.0 / max(1 - A, 0.05)
    hh = Hh if Hh is not None else 1.0 + 2.4 * (amp - 1)
    if A > 0.12:
        sub = np.clip(J + 0.5, 0, 255).astype(np.uint8)
        den = cv2.fastNlMeansDenoisingColored(np.ascontiguousarray(sub[..., ::-1]), None, hh, hh, 5, 15)[..., ::-1].astype(np.float64)
        ampM = 1.0 / np.maximum(1 - A * Mb, 0.05)
        wd = np.clip((ampM - 1) / max(amp - 1, 1e-3), 0, 1)[..., None]
        J = J * (1 - wd) + den * wd
    # ④ 윤곽 띠 다듬기: |부호거리| ≤ BAND 화소는 **윤곽 법선 방향 7점(±3px) 중앙값**으로 — 윤곽과 나란한 가는 테(틀이 반 화소 어긋난 것)와
    #    끝 뾰족 부분의 남은 밝기는 지우고, 윤곽을 가로지르는 진짜 선은 법선을 따라 이어져 있어 남는다.
    if BAND > 0:
        SDp = SD.reshape(h, 4, w, 4).mean(axis=(1, 3)) + e      # 화소 부호거리(넓힌 윤곽 기준)
        gy_, gx_ = np.gradient(ndi.gaussian_filter(SDp, 1.0))
        nn = np.maximum(np.hypot(gx_, gy_), 1e-6); gx_, gy_ = gx_ / nn, gy_ / nn
        band = np.abs(SDp) <= BAND + 1
        ys, xs = np.nonzero(band)
        stack, stack0 = [], []
        for t in (-3, -2, -1, 0, 1, 2, 3):
            pts = (ys + gy_[ys, xs] * t, xs + gx_[ys, xs] * t)
            stack.append(samp(J, pts)); stack0.append(samp(Ic, pts))
        med = np.median(np.array(stack), axis=0)
        med0 = np.median(np.array(stack0), axis=0)
        wb = np.clip(1 - (np.abs(SDp[ys, xs]) - BAND), 0, 1)[:, None]
        # 선 지키기(10/2 — 첫 52판에서 윤곽을 비스듬히 지나는 먹선이 중앙값에 지워져 밝기가 +100~200 오른 화소가 판마다 40~90개):
        #   흰 덧씌움은 대비를 줄일 뿐 뒤집지 않는다 — **원본(별 있는)에서도** 법선 중앙값보다 15 넘게 어두웠던 화소는 진짜 선이니 그대로,
        #   되돌림이 만든 테(원본에서는 매끈한 가장자리)는 중앙값으로.
        dark0 = (med0.mean(axis=1) - Ic[ys, xs].mean(axis=1))[:, None]
        wb = wb * np.clip(1 - (dark0 - 10) / 10, 0, 1)
        J[ys, xs] = J[ys, xs] * (1 - wb) + med * wb
    # ⑤ 테 색
    edge = ndi.binary_dilation((Mb > 0.03) & (Mb < 0.97), iterations=1)
    if CHROMA > 0:
        # 별 안 전체의 색차를 크게 고름 — 되돌림이 압축 색차를 키워 생긴 무지개 · 주황 얼룩(밝은 바탕 위 짙은 별)을 지운다. 밝기는 그대로.
        edge = edge | (Mb > 0.03)
    Y = 0.299 * J[..., 0] + 0.587 * J[..., 1] + 0.114 * J[..., 2]
    Cb = J[..., 2] - Y; Cr = J[..., 0] - Y
    ks = 5 if CHROMA <= 0 else int(CHROMA)
    Cb = np.where(edge, ndi.median_filter(Cb, size=ks), Cb); Cr = np.where(edge, ndi.median_filter(Cr, size=ks), Cr)
    Rr = Cr + Y; Bb = Cb + Y; Gg = (Y - 0.299 * Rr - 0.114 * Bb) / 0.587
    J = np.stack([Rr, Gg, Bb], axis=2)
    # ⑧ 밝아짐 막기: 흰 덧씌움을 걷어 내면 화소는 어두워지기만 한다 — 결과 밝기가 원본(별 있는)보다 6 넘게 밝으면
    #    (톤 맞춤 · 띠 중앙값 · 색차 고르기가 먹선을 지운 자리) 되돌림 직후 값으로 돌린다.
    Lr, Lo_ = J.mean(axis=2), Ic.mean(axis=2)
    over = Lr > Lo_ + 6
    if over.any():
        J0 = np.clip(J_raw, 0, 255)
        J[over] = np.minimum(J0[over], Ic[over])
    if KEEPDARK > 0:
        # 어두운 물건(원본 밝기 < KEEPDARK — 별이 얹혀도)은 원본 그대로 — 별이 물건 끝에 살짝 걸친 판에서 물건을 회색으로 만들지 않게
        Lo = Ic.mean(axis=2)
        keep = ndi.binary_dilation(Lo < KEEPDARK, iterations=1)
        wk = ndi.gaussian_filter(keep.astype(float), 0.8)[..., None]
        J = J * (1 - wk) + Ic * wk
    out = I.copy()
    out[y0:y1, x0:x1] = J
    out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(dst)
    if CMP:
        hb2 = int(R * 2.4)
        bx = (int(cx) - hb2, int(cy) - hb2, int(cx) + hb2, int(cy) + hb2)
        a_img = Image.fromarray(I.astype(np.uint8)).crop(bx).resize((300, 300), Image.LANCZOS)
        b_img = Image.fromarray(out).crop(bx).resize((300, 300), Image.LANCZOS)
        cm = Image.new('RGB', (610, 300), 'white'); cm.paste(a_img, (0, 0)); cm.paste(b_img, (310, 0)); cm.save(CMP)
    print(info + '  키움 %.2f  h %.1f' % (amp, hh))


if __name__ == '__main__':
    main()

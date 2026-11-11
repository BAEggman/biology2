# fix.py — L34b 그림 고침 (원본에서 final_new.png 를 다시 만든다)
# 원본: SP/L34b/r1/final_v1.png (읽기만)  ·  결과: SP/picfix/L34b/final_new.png
import numpy as np, cv2
from PIL import Image

SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
SRC = f'{SP}/L34b/r1/final_v1.png'
OUT = f'{SP}/picfix/L34b'

LUMA = np.array([.299, .587, .114], np.float32)
WIN_D = 70                                         # 창을 아래로 늘리는 양(px)
INK = np.array([20, 10, 3], np.float32)          # 윤곽선 먹색(가장 진한 픽셀들에서)


def smooth_fill(img, known, sigma):
    """known(bool) 픽셀만으로 정규화 가우스 합성곱 → 매끈한 바탕장 (먼 곳은 더 큰 시그마로 메움)"""
    k = known.astype(np.float32)
    out = None
    for sg in (sigma, sigma * 2.5, sigma * 6):
        num = cv2.GaussianBlur(img * k[..., None], (0, 0), sg, borderType=cv2.BORDER_REPLICATE)
        den = cv2.GaussianBlur(k, (0, 0), sg, borderType=cv2.BORDER_REPLICATE)[..., None]
        est = num / np.maximum(den, 1e-9)
        ok = den > 0.02
        if out is None:
            out = est.copy(); good = ok[..., 0].copy()
        else:
            m = ~good
            out[m] = est[m]; good |= ok[..., 0]
    return out


def ink_alpha(c, fills):
    """c ≈ a*INK + (1-a)*fill 의 a (fills 중 잔차가 가장 작은 것)"""
    best_a = np.zeros(c.shape[:2], np.float32)
    best_r = np.full(c.shape[:2], 1e9, np.float32)
    for f in fills:
        f = np.asarray(f, np.float32)
        if f.ndim == 1:
            f = np.broadcast_to(f, c.shape)
        d = f - INK
        a = ((f - c) * d).sum(-1) / np.maximum((d * d).sum(-1), 1e-6)
        a = np.clip(a, 0, 1)
        r = np.linalg.norm(c - (a[..., None] * INK + (1 - a[..., None]) * f), axis=-1)
        m = r < best_r
        best_a[m] = a[m]
        best_r[m] = r[m]
    return best_a


# ---------------------------------------------------------------- 항목 1
def fix_sacks(img):
    """오른쪽 껍질 속 겨자색 자루 넷 → 셋 : 뒤 가운데 자루(왼 뒤 · 오른쪽 자루 뒤)를 지운다"""
    x0, y0, x1, y1 = 1835, 430, 2015, 600
    c = img[y0:y1, x0:x1].copy()
    H, W = c.shape[:2]
    L = c @ LUMA
    yel = np.array([207, 169, 40], np.float32)

    # 먹선(L<90)을 벽으로 한 씨앗 채우기 — 물건 속을 하나씩 가른다
    n, lab = cv2.connectedComponents((L >= 90).astype(np.uint8), connectivity=4)
    def region(x, y):
        l = lab[y - y0, x - x0]
        assert l != 0, (x, y)
        return lab == l

    # 뒤 가운데 자루: 몸통(채우기) + 꼭지(선반 아래 회색 띠, 손 다각형)
    knot = np.zeros((H, W), np.uint8)
    poly = np.array([[1904, 451], [1947, 451], [1949, 462], [1940, 466], [1905, 466]]) - [x0, y0]
    cv2.fillPoly(knot, [poly.astype(np.int32)], 1)
    back = region(1925, 478) | (knot > 0)

    # 앞 물건 속(그대로 둘 쪽): 왼 뒤 몸통·꼭지 · 오른쪽 몸통·꼭지·띠 · 앞 아래 몸통·꼭지 · 선반 밝은 면
    F = np.zeros((H, W), bool)
    for (x, y) in [(1870, 500), (1866, 466), (1960, 540), (1960, 482), (1956, 496), (1900, 570), (1872, 520)]:
        F |= region(x, y)
    F[:447 - y0, :] |= (L[:447 - y0, :] >= 140)
    F &= ~back
    dF_flood = cv2.distanceTransform((~F).astype(np.uint8), cv2.DIST_L2, 5)
    # 오른쪽 자루 꼭지는 통째 보호(속의 작은 밝은 주머니까지): 행마다 왼선 바깥 가장자리(L=75)를 재어 그 1px 안쪽부터
    KR = np.zeros((H, W), bool)
    for y in range(467, 496):
        row = L[y - y0, 1934 - x0:1960 - x0]
        k = int(np.argmax(row < 75))
        xe = 1934 + k - 1 + (row[k - 1] - 75) / (row[k - 1] - row[k])
        KR[y - y0, int(np.ceil(xe + 1.0)) - x0:1987 - x0] = True
    F |= KR

    dF = cv2.distanceTransform((~F).astype(np.uint8), cv2.DIST_L2, 5)
    dB = cv2.distanceTransform((~back).astype(np.uint8), cv2.DIST_L2, 5)

    # 매끈한 바탕장: 확실한 바탕(먹에서 떨어진 갈색 회색)만으로 정규화 합성곱
    bgc = np.array([155, 126, 84], np.float32)
    dink = cv2.distanceTransform((L >= 100).astype(np.uint8), cv2.DIST_L2, 5)
    Bk = (np.linalg.norm(c - bgc, axis=2) < 30) & (dink >= 3.5) & ~back & ~F
    Bk[: 451 - y0, :] = False
    bgf = smooth_fill(c, Bk, 9)

    # 먹 덮임 = min(원본에서 추정한 덮임, 앞 물건 윤곽 모델)
    a_orig = ink_alpha(c, [yel, np.array([120, 104, 86], np.float32), bgf])
    a_mod = np.clip((6.75 - dF) / 1.25, 0, 1)     # 원본 먹 띠: F 가장자리에서 1~5px, 바깥 AA 6~7px
    a = np.minimum(a_orig, a_mod)
    # 먹은 진한 심에서 2px 안에서만(뒤 자루 노랑의 그늘을 먹으로 읽지 않게)
    K = (a_orig >= 0.65) & (dF <= 5.5)
    dK = cv2.distanceTransform((~K).astype(np.uint8), cv2.DIST_L2, 5)
    a = np.minimum(a, np.clip(2.5 - dK, 0, 1))
    # 이음매 두 곳: 뒤 자루 윤곽이 앞 윤곽에 붙던 자리 — 이웃의 깨끗한 가장자리를 이은 선 바깥은 먹을 없앤다
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    # (가) 왼 뒤 자루 윗선 x 1885~1894 : 윗 가장자리(L=75 를 지나는 자리)를 이웃 열에서 재어 3차로 이음
    ex = np.array([1882, 1883, 1884, 1885, 1886, 1893, 1894, 1895, 1896, 1897], np.float32)
    ey = []
    for x in ex.astype(int):
        col = L[469 - y0:482 - y0, x - x0]
        k = int(np.argmax(col < 75))
        ey.append(469 + k - 1 + (col[k - 1] - 75) / (col[k - 1] - col[k]))
    cf = np.polyfit(ex - 1890, np.array(ey), 3)
    win = (xx >= 1885) & (xx <= 1894) & (yy >= 462) & (yy <= 478)
    edge = np.polyval(cf, xx - 1890)
    a = np.where(win, np.minimum(a, np.clip(yy + 0.5 - edge, 0, 1)), a)
    # (나) 오른쪽 자루 꼭지 왼 위 모서리 : 윗 가장자리 y≈465.7 (x≥1953 에서 잰 값), 왼 가장자리 x≈1941.3
    col_e = []
    for x in range(1953, 1961):
        col = L[460 - y0:470 - y0, x - x0]
        k = int(np.argmax(col < 75))
        col_e.append(460 + k - 1 + (col[k - 1] - 75) / (col[k - 1] - col[k]))
    ytop = float(np.median(col_e))
    win = (xx >= 1940) & (xx <= 1956) & (yy >= 452) & (yy <= 467)
    cov = np.minimum(np.clip(yy + 0.5 - ytop, 0, 1), np.clip(xx + 0.5 - 1941.3, 0, 1))
    a = np.where(win, np.minimum(a, cov), a)

    new = a[..., None] * INK + (1 - a[..., None]) * bgf
    keep = (dF_flood <= 2.5) | KR                  # 앞 물건 안쪽 안티에일리어싱 · 오른쪽 꼭지는 원본 그대로
    new = np.where(keep[..., None], c, new)
    # 고칠 자리: 뒤 자루에서 10px 안(8.5~10 에서 원본과 섞어 이음새를 없앤다)
    f = np.clip((10.0 - dB) / 1.5, 0, 1)
    f[F] = 0
    f[: 449 - y0 + 1, :] = 0                       # 선반 윤곽선 위는 아래에서 따로
    res = c * (1 - f[..., None]) + new * f[..., None]

    # 선반 아래 윤곽선 다시 긋기(x 1900~1950): 깨끗한 이웃 열의 단면을 휜 중심선에 맞춰 옮긴다
    xs_fit = np.array([1860, 1880, 1895, 1897, 1950, 1955, 1960, 1975], np.float32)
    def center(col):
        prof = L[444 - y0:453 - y0, col - x0]
        k = np.argmin(prof)
        # 부화소 중심(최솟값 둘레 포물선)
        if 0 < k < len(prof) - 1:
            p0, p1, p2 = prof[k - 1], prof[k], prof[k + 1]
            den = p0 - 2 * p1 + p2
            off = 0.5 * (p0 - p2) / den if den != 0 else 0
        else:
            off = 0
        return 444 + k + off
    ys_fit = np.array([center(int(x)) for x in xs_fit])
    coef = np.polyfit(xs_fit, ys_fit, 2)
    yc = lambda x: np.polyval(coef, x)
    src_cols = [1896, 1897, 1950, 1951]
    for x in range(1900, 1951):
        cy = yc(x)
        acc = np.zeros((14, 3), np.float32)
        for sx in src_cols:
            sy = yc(sx)
            # 원본 열 sx 를 (cy - sy) 만큼 옮겨 y = cy-5 .. cy+8 을 채움
            yy = np.arange(14) + int(np.floor(cy)) - 5
            src_y = yy - (cy - sy)
            col = img[:, sx]
            i0 = np.floor(src_y).astype(int); t = (src_y - i0)[:, None]
            acc += col[i0] * (1 - t) + col[i0 + 1] * t
        prof = acc / len(src_cols)
        yy = np.arange(14) + int(np.floor(cy)) - 5
        for j, y in enumerate(yy):
            rel = y - cy
            if rel < -2.5:
                continue                           # 선반 밝은 면 — 원본 유지
            # 윤곽선 아래쪽은 바탕장으로 부드럽게 넘김
            if rel > 4.5:
                tw = min(1.0, (rel - 4.5) / 2.0)
                v = prof[j] * (1 - tw) + bgf[y - y0, x - x0] * tw
            else:
                v = prof[j]
            res[y - y0, x - x0] = v
        # 윤곽선 띠 아래 ~ 꼭지 자리의 바탕은 위(res)에서 이미 채움
    out = img.copy()
    out[y0:y1, x0:x1] = res
    return out


# ---------------------------------------------------------------- 항목 2
def shift1d(v, s):
    """1차원 단면 v 를 s 픽셀(부화소) 옮긴 것 (끝값 유지)"""
    n = len(v)
    src = np.arange(n) - s
    src = np.clip(src, 0, n - 1)
    i0 = np.floor(src).astype(int); i1 = np.minimum(i0 + 1, n - 1); t = (src - i0)
    if v.ndim == 2:
        t = t[:, None]
    return v[i0] * (1 - t) + v[i1] * t


def put_line_profile(dst, src_img, src_cols, src_center, tgt_cols, tgt_center, half=6, rows_ok=None):
    """거의 가로인 선: 원본의 깨끗한 열(src_cols) 단면을 중심 맞춰 평균 → 목표 열에 목표 중심으로 놓는다"""
    prof = []
    for sx in src_cols:
        cy = src_center(sx)
        y0 = int(np.floor(cy)) - half - 2
        col = src_img[y0:y0 + 2 * half + 5, sx]
        prof.append(shift1d(col, -(cy - np.floor(cy)) - 2.0)[: 2 * half + 1])   # 중심 → 인덱스 half
    prof = np.mean(prof, 0)
    for x in tgt_cols:
        cy = tgt_center(x)
        base = int(np.floor(cy)) - half
        frac = cy - np.floor(cy)
        seg = shift1d(np.vstack([prof, prof[-1:]]), frac)[: 2 * half + 1]
        for j in range(2 * half + 1):
            y = base + j
            if rows_ok is None or rows_ok(x, y):
                dst[y, x] = np.minimum(dst[y, x], seg[j])      # 어두운 쪽만(밑의 다른 선을 지우지 않게)


def fix_tube(img):
    out = img.copy()
    L = img @ LUMA

    # ---- 2-가: 벽 단면의 홈 + 창 왼쪽 관 토막을 지우고 돌·벽돌을 잇는다
    M = np.zeros(img.shape[:2], np.uint8)
    cv2.rectangle(M, (247, 569), (272, 625), 1, -1)        # 홈(테두리 AA 포함)
    cv2.rectangle(M, (247, 581), (337, 612), 1, -1)        # 관 토막(윗·아래 AA 포함)
    M = M.astype(bool)
    # 바탕(돌=벽돌 같은 색): 먹에서 3px 떨어진 둘레 픽셀로 매끈하게
    ink = (L < 125).astype(np.uint8)
    dink = cv2.distanceTransform(1 - ink, cv2.DIST_L2, 5)
    win = np.zeros_like(M); win[540:660, 230:350] = True
    known = win & ~M & (dink >= 3) & (L > 125) & (L < 175)
    known[:, 337:] = False                                   # 창틀 오른쪽(흰 구멍)은 쓰지 않음
    fill = smooth_fill(img[530:670, 220:360], known[530:670, 220:360], 6)
    sub = out[530:670, 220:360]
    sub[M[530:670, 220:360]] = fill[M[530:670, 220:360]]

    # (1) 고리 오른쪽 경계선(거의 세로) x 274~288 · 관에 가렸던 582~611 행: 위(579) · 아래(616) 단면을 중심 맞춰 섞음
    def hcenter(y):
        row = L[y, 272:290]; w = np.clip(143 - row, 0, None)
        return 272 + (np.arange(18) * w).sum() / w.sum()
    ca, cb = hcenter(579), hcenter(616)
    Pa = img[579, 270:292].copy(); Pb = img[616, 270:292].copy()
    for y in range(580, 616):
        t = (y - 579) / (616 - 579)
        c = ca * (1 - t) + cb * t
        seg = (1 - t) * shift1d(Pa, c - ca) + t * shift1d(Pb, c - cb)
        for i, x in enumerate(range(270, 292)):
            if M[y, x] and 274 <= x <= 287:
                out[y, x] = seg[i]

    # (2) 벽돌 줄눈 A: x≥301 의 보이는 부분(곧은 선)을 관 뒤로 고리선까지 잇는다
    cA = lambda x: 579.6 - 0.52 * (x - 301)
    put_line_profile(out, img, [309, 310, 311, 312, 318, 319], cA, range(282, 301), cA, half=5,
                     rows_ok=lambda x, y: M[y, x] and y >= 581)

    # (3) 고리 아래 이음선: 보이는 왼쪽 끝(x 243~246)의 단면을 기울기 −0.37 로 고리선(x≈278)까지
    cJ = lambda x: 622.5 - 0.37 * (x - 250)
    cJsrc = {243: 626.3, 244: 625.3, 245: 624.7, 246: 624.5}
    put_line_profile(out, img, [243, 244, 245, 246], lambda x: cJsrc[x], range(247, 279), cJ, half=5,
                     rows_ok=lambda x, y: M[y, x] and x < 278 - 0)

    # ---- 2-나: 네모 구멍(창)을 아래로 D px 늘린다 — 관이 구멍 속을 지나고 아래위로 빈 틈이 보이게
    D = WIN_D
    c_back = lambda x: 577.7 - 0.53 * (x - 343)      # 문턱 뒷선(흰 구멍 아래 경계) 중심
    c_jb = lambda x: 554.6 + 0.16 * (x - 389)        # 옆면 아랫선 중심
    c_s = lambda x: 582.6 - 0.61 * (x - 390)         # 문턱 비스듬한 오른선 중심(x 400~418 에서 잼)
    W = out.copy()                                   # 관을 뺀 창 바탕
    for x in range(342, 430):
        if x <= 383:
            y_ins = int(round(c_back(x) - 11)); y_end = 587                # 흰 구멍 열: 뒷선 위 옅은 테(중심−9~−5)까지 함께 옮김
        elif x <= 392:
            y_ins = 541; y_end = int(np.floor(c_s(x))) + 1                  # 흰/옆면 경계선(545 부터 모서리로 휨 → 그 위에서 끼움)
        elif x <= 418:
            y_ins = int(round(c_jb(x) - 6)); y_end = int(np.floor(c_s(x))) + 1
        elif x <= 422:
            y_ins = 549; y_end = int(np.floor(c_s(x))) + 1
        else:
            y_ins = 549; y_end = 567                                        # 오른 틀선과 그 바깥 AA(모서리까지)
        col = img[:, x]
        if 384 <= x <= 392:
            # 경계선은 손그림이라 출렁임 → 곧은 구간(522~540행)의 중앙 단면을 반복해 끼움
            W[y_ins:y_ins + D, x] = np.median(img[522:541, x], axis=0)
        elif x >= 419:
            # 오른 틀선 둘레도 같은 까닭으로 바로 위 곧은 구간(530~548행) 중앙 단면을 반복
            W[y_ins:y_ins + D, x] = np.median(img[530:549, x], axis=0)
        else:
            W[y_ins:y_ins + D, x] = col[y_ins - D:y_ins]                   # 바로 위 D 줄을 끼워 넣음
        W[y_ins + D:y_end + D, x] = col[y_ins:y_end]                       # 문턱을 통째 D 내림
    # 문턱 아래 모서리선의 아래 반쪽(새 자리 밑은 벽돌): 앞선(가로)은 위 반쪽과 대칭, 비스듬한 선은 원본 x 400~418 단면
    a_fe = {1: 0.96, 2: 0.55, 3: 0.05}
    a_s = lambda dv: float(np.interp(dv, [0, 0.8, 1.8, 2.8, 3.8], [1, 1, 0.68, 0.2, 0]))
    for x in range(342, 423):
        ylo = min(586, int(np.floor(c_s(x)))) + D - 2
        for y in range(ylo, 586 + D + 8):
            al = 0.0
            if x <= 385 and y > 586 + D:
                al = a_fe.get(y - 586 - D, 0.0)
            if x >= 383:
                cs = c_s(x) + D
                if y >= int(np.floor(c_s(x))) + 1 + D:
                    al = max(al, a_s(y - cs))
            if al > 0:
                W[y, x] = al * INK + (1 - al) * W[y, x]

    # ---- 2-다: 관을 제자리에 다시 얹는다(관은 창 앞) — 몸통 585~608 은 원본, 위·아래 AA 줄은 새 바탕에 합성
    res = W.copy()
    xs = range(339, 432)
    for x in xs:
        res[585:609, x] = img[585:609, max(x, 342)]
    # 위 AA(583·584): 왼쪽(벽돌 위 x 320~334)과 오른쪽(벽돌 위 x 428~436) 원본에서 잰 덮임을 x 로 잇는다
    def cover(rows, xa, xb, bg_rows):
        bgL = np.median(L[bg_rows[0]:bg_rows[1], xa:xb])
        return {r: float(np.clip((bgL - np.median(L[r, xa:xb])) / (bgL - 10), 0, 1)) for r in rows}
    tl = cover([582, 583, 584], 320, 335, (612, 618)); tr = cover([582, 583, 584], 428, 437, (612, 618))
    for x in xs:
        t = (x - 339) / (431 - 339)
        for r in (582, 583, 584):
            al = (1 - t) * tl[r] + t * tr[r]
            res[r, x] = al * INK + (1 - al) * W[r, x]
    # 아래 AA(609~612): 원본은 벽돌 위 — 원본 x 350~430 의 덮임을 행마다 x 에 대해 1차로 맞춰(관이 오른쪽으로
    # 아주 조금 처짐 · 줄눈 점은 빼고) 새 바탕에 합성. 창틀 혹이 있던 x<350 은 x=350 값.
    fitx = np.arange(350, 431)
    for r in (609, 610, 611, 612):
        av = np.clip((148 - L[r, 350:431]) / (148 - 10), 0, 1)
        k = np.polyfit(fitx, av, 1)
        resid = np.abs(av - np.polyval(k, fitx)); ok = resid < 0.08
        k = np.polyfit(fitx[ok], av[ok], 1)
        for x in xs:
            al = float(np.clip(np.polyval(k, max(x, 350)), 0, 1))
            res[r, x] = al * INK + (1 - al) * W[r, x]

    # ---- 2-라: 왼 틀선(벽의 모서리)을 관 위로 572 ~ 새 앞선까지 긋는다 → 관이 벽 뒤에서 나와 구멍으로 든다
    # 틀선 단면 덮임: 원본 520~556 행 중앙값(왼쪽은 벽돌 L155, 오른쪽은 흰 255 기준)
    af = {}
    for x in range(334, 343):
        m = float(np.median(L[520:557, x]))
        bgL = 155.0 if x <= 338 else 255.0
        af[x] = float(np.clip((bgL - m) / (bgL - 3), 0, 1))
    bri = smooth_fill(out[560:680, 300:345], (L[560:680, 300:345] > 125) & (L[560:680, 300:345] < 175)
                      & (np.arange(300, 345)[None, :] <= 333), 5)          # 틀선 왼쪽 밑 벽돌(깨끗한)
    # 572~580 행은 틀선 왼쪽 AA 밑이 원본 벽돌 → 원본에서 틀선 덮임을 걷어낸 값 대신 매끈한 벽돌을 쓴다
    yb = 586 + D
    fe = {yb - 2: 0.55, yb - 1: 0.96, yb: 1.0, yb + 1: 0.96, yb + 2: 0.55, yb + 3: 0.05}   # 앞선 세로 단면
    for y in range(572, yb + 4):
        v = 1.0 if y <= yb else a_fe.get(y - yb, 0.0)                      # 틀선 아래 끝은 앞선 아래 반쪽처럼
        for x in range(334, 342):
            under = bri[y - 560, x - 300] if x <= 337 else res[y, 342]
            if x <= 339:
                al = af[x] * v                                              # 모서리 바깥은 틀선 바깥 AA 그대로(삐져나오지 않게)
            else:
                al = max(af[x] * v, fe.get(y, 0.0))
            res[y, x] = al * INK + (1 - al) * under
    return out, res


def main():
    img = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
    out = fix_sacks(img)                 # 항목 1
    _, out = fix_tube(out)               # 항목 2 (x<500 만 읽고 씀 — 항목 1 자리와 겹치지 않음)
    out8 = np.clip(np.round(out), 0, 255).astype(np.uint8)
    Image.fromarray(out8, 'RGB').save(f'{OUT}/final_new.png')
    return out8


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# L13f_ylib.py — L13f 「깃발 다섯 연대의 출정」의 작은 Y 깃발(항체) 그리기(2026-11-15).
#  Gemini 는 「세균에 갈래 끝으로 붙고 깃대가 바깥을 향한 Y」를 끝내 거꾸로(깃대를 꽂은 핀) 그렸다(ZI · ZJ 두 번) — 그래서 세균 · 망토 손의
#  깃발은 지운 뒤(ZI2 · ZJ2) 여기서 윤곽을 따라 하나씩 세운다: 두 갈래 끝(가변 · N 말단)이 살갗에 닿고, 깃대(불변 · Fc)는 바깥으로.
#  이음 깃발(IgA 이량체 — 눈물방울 · 웅덩이)도 같은 붓으로.
import math, numpy as np, cv2
from PIL import Image, ImageDraw

S = 3
INK = (28, 22, 18, 255)
OCHRE = (226, 168, 58, 255)
OCHRE_D = (190, 130, 40, 255)

def _seg(d, p, q, w, col):
    d.line([(p[0] * S, p[1] * S), (q[0] * S, q[1] * S)], fill=col, width=max(1, int(round(w * S))))
    for x, y in (p, q):
        r = w * S / 2; d.ellipse([x * S - r, y * S - r, x * S + r, y * S + r], fill=col)

def y_shape(d, tip_l, tip_r, fork, end, w=2.6, ink=1.3):
    """Y 하나 — 두 갈래 끝 tip_l · tip_r, 갈림 fork, 깃대 끝 end. 검은 테 → 황토 속."""
    for col, ww in ((INK, w + 2 * ink), (OCHRE, w)):
        _seg(d, tip_l, fork, ww, col); _seg(d, tip_r, fork, ww, col); _seg(d, fork, end, ww, col)

def stand_y(d, p, n, spread=5.5, arm=7.5, stem=13.0, w=2.6):
    """살갗 위의 점 p(바깥 법선 n)에 두 갈래 끝을 대고 깃대를 바깥으로 세운 Y."""
    nx, ny = n; tx, ty = -ny, nx
    tl = (p[0] + tx * spread, p[1] + ty * spread); tr = (p[0] - tx * spread, p[1] - ty * spread)
    fk = (p[0] + nx * arm, p[1] + ny * arm); en = (fk[0] + nx * stem, fk[1] + ny * stem)
    y_shape(d, tl, tr, fk, en, w)
    return en

def double_y(d, cx, cy, ang, half=11.0, arm=5.0, spread=4.2, w=2.2, hook=True):
    """이음 깃발(IgA 이량체) — 깃대 끝끼리 맞댄 Y 둘(>—<) · 가운데 J 고리(작은 회색 갈고리)."""
    ux, uy = math.cos(ang), math.sin(ang); vx, vy = -uy, ux
    for sg in (-1, 1):
        fk = (cx + sg * ux * half, cy + sg * uy * half)
        tl = (fk[0] + sg * ux * arm + vx * spread, fk[1] + sg * uy * arm + vy * spread)
        tr = (fk[0] + sg * ux * arm - vx * spread, fk[1] + sg * uy * arm - vy * spread)
        y_shape(d, tl, tr, fk, (cx, cy), w, 1.1)
    if hook:
        r = 2.4; d.arc([(cx - r) * S, (cy - r - 1) * S, (cx + r) * S, (cy + r - 1) * S], 0, 200, fill=(120, 120, 128, 255), width=int(1.6 * S))

def body_contour(img_bgr, box, kind='green', open_k=21):
    """box 안에서 몸통(초록 세균 · 살빛 손)의 바깥 윤곽(테 포함)을 돌려준다 — 팔 · 다리 같은 가는 것은 열기(opening)로 뗀다."""
    x0, y0, x1, y1 = box
    c = img_bgr[y0:y1, x0:x1].astype(int); b, g, r = c[..., 0], c[..., 1], c[..., 2]
    if kind == 'green': m = (g > r + 25) & (g > b + 25) & (g > 90)
    else: m = (r > 195) & (g > 140) & (g < 222) & (b > 100) & (b < 200) & (r - b > 40)
    m = (m * 255).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))                        # 검은 테까지
    if open_k: m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_k, open_k)))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cs = sorted(cs, key=cv2.contourArea, reverse=True)
    return [(cc[:, 0, :] + np.array([x0, y0])).astype(float) for cc in cs], m

def resample(pts, step, mask, off, phase=0.5):
    """닫힌 윤곽 pts 를 호 길이 step 마다 → (점, 바깥 법선). 바깥은 mask(몸통 = 255) 밖으로 가는 쪽."""
    P = np.vstack([pts, pts[:1]]); seg = np.hypot(*np.diff(P, axis=0).T); L = np.concatenate([[0], np.cumsum(seg)])
    ox, oy = off; H, W = mask.shape
    def inside(q):
        x, y = int(round(q[0] - ox)), int(round(q[1] - oy))
        return 0 <= x < W and 0 <= y < H and mask[y, x] > 0
    out = []
    for s in np.arange(step * phase, L[-1], step):
        i = min(len(seg) - 1, np.searchsorted(L, s) - 1); t = (s - L[i]) / max(1e-6, seg[i]); p = P[i] + (P[i + 1] - P[i]) * t
        j0, j1 = max(0, i - 5), min(len(P) - 1, i + 6); tv = P[j1] - P[j0]; tv = tv / max(1e-6, np.hypot(*tv))
        n = np.array([tv[1], -tv[0]])
        if inside(p + n * 6) and not inside(p - n * 6): n = -n
        out.append((tuple(p), tuple(n)))
    return out

def _qb(p0, p1, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]

def claw_y(d, p, n, spread=9.0, arm=17.0, stem=20.0, w=4.6, bulge=7.0, ink=1.4, pen=False):
    """집게 Y — 두 팔이 바깥으로 부풀었다가 끝이 안으로 굽어 살갗을 집는다(게 집게 · 【하늘색 Y자 집게】와 같은 꼴) · 깃대는 바깥으로 곧게.
    pen = 팔 끝 바로 위 바깥쪽에 작은 깃발 천(세모 둘) — 작게 그리면 「가시」로 읽혀 쓰지 않는다(기본 False)."""
    nx, ny = n; tx, ty = -ny, nx
    fk = (p[0] + nx * arm, p[1] + ny * arm); en = (fk[0] + nx * stem, fk[1] + ny * stem)
    arms = []
    for sg in (-1, 1):
        tip = (p[0] + sg * tx * spread, p[1] + sg * ty * spread)
        ctl = (p[0] + nx * arm * 0.55 + sg * tx * (spread + bulge), p[1] + ny * arm * 0.55 + sg * ty * (spread + bulge))
        arms.append((_qb(fk, ctl, tip), sg, tip, ctl))
    for colr, ww in ((INK, w + 2 * ink), (OCHRE, w)):
        for pts, sg, tip, ctl in arms:
            d.line([(x * S, y * S) for x, y in pts], fill=colr, width=int(round(ww * S)), joint='curve')
            for x, y in (pts[0], pts[-1]):
                r = ww * S / 2; d.ellipse([x * S - r, y * S - r, x * S + r, y * S + r], fill=colr)
        _seg(d, fk, en, ww, colr)
    if pen:
        for pts, sg, tip, ctl in arms:
            q = pts[-4]; q2 = pts[-8]                                          # 팔 끝 가까이 두 점
            ox, oy = sg * tx * 7.5 + nx * 1.5, sg * ty * 7.5 + ny * 1.5            # 바깥 옆으로
            tri = [q, q2, ((q[0] + q2[0]) / 2 + ox, (q[1] + q2[1]) / 2 + oy)]
            d.polygon([(x * S, y * S) for x, y in tri], fill=(236, 182, 74, 255), outline=INK, width=int(1.3 * S))
    return en

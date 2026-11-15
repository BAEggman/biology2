#!/usr/bin/env python3
# L43f_pil.py <in.png> <out.png> — L43f 끝손질(2026-11-15 · Opus 5.5): 가닥의 방향은 Gemini 가 못 지켜서 PIL 로 그린다.
#  끈 = 금빛 · 갈색 두 가닥을 꼰 것(DNA). 금빛 가닥의 5′→3′ = 왼쪽 → 오른쪽 · 갈색 = 오른쪽 → 왼쪽(역평행).
#  오른쪽 비탈 기계(오른쪽으로 내려감): 주형 = 갈색(기계 밑) · 암호 = 금빛(기계 위로 넘는 짧은 고리).
#  왼쪽 비탈 기계(왼쪽으로 내려감): 주형 = 금빛(기계 밑) · 암호 = 갈색(Gemini 가 그린 고리 그대로).
#  ① 기계 밑 구간(갈라진 두 점 사이)의 끈을 주형 가닥 한 줄로 덧칠(바퀴 · 기계는 위로 되살림)
#  ② 오른쪽 기계에 금빛 암호 가닥의 짧은 고리(뒤 → 기계 위 → 앞) · 종이는 그 위로 되살림
#  ③ 화살촉 — 가닥의 5′→3′: 암호 가닥 · 종이(RNA)는 비탈 아래(기계가 가는 쪽) · 주형 가닥은 비탈 위(거꾸로 읽힘)
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import cv2

GOLD = (230, 186, 84); BROWN = (162, 100, 70); INK = (24, 20, 16)
W_STRAND = 15          # 가닥 굵기(바깥 먹선 포함은 + 6)
W_TPL = 19             # 기계 밑 주형 가닥 — 밑의 꼰 끈을 다 덮게

def spline(pts, n=24):
    """Catmull-Rom — 점들을 지나는 매끈한 곡선."""
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(np.array, (P[i - 1], P[i], P[i + 1], P[i + 2]))
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(np.array(pts[-1], float))
    return [tuple(map(float, p)) for p in out]

def stroke(img, pts, col, w=W_STRAND, ink=3):
    d = ImageDraw.Draw(img); c = spline(pts)
    d.line(c, fill=INK, width=w + 2 * ink, joint='curve')
    for p in (c[0], c[-1]): d.ellipse([p[0] - (w / 2 + ink), p[1] - (w / 2 + ink), p[0] + (w / 2 + ink), p[1] + (w / 2 + ink)], fill=INK)
    d.line(c, fill=col, width=w, joint='curve')
    for p in (c[0], c[-1]): d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)
    # 가닥의 결(옅은 빗금) — 끈의 꼰 결과 어울리게
    hl = tuple(min(255, int(v * 1.12)) for v in col); sh = tuple(int(v * 0.82) for v in col)
    d.line([(x - 0.0, y - w * 0.22) for x, y in c], fill=hl, width=max(2, w // 5), joint='curve')
    d.line([(x, y + w * 0.25) for x, y in c], fill=sh, width=max(2, w // 6), joint='curve')
    return c

def arclen_points(c, fracs):
    seg = [math.dist(c[i], c[i + 1]) for i in range(len(c) - 1)]; L = sum(seg); out = []
    for f in fracs:
        t = f * L; acc = 0
        for i, s in enumerate(seg):
            if acc + s >= t:
                u = (t - acc) / s if s else 0
                p = (c[i][0] + u * (c[i + 1][0] - c[i][0]), c[i][1] + u * (c[i + 1][1] - c[i][1]))
                ang = math.atan2(c[i + 1][1] - c[i][1], c[i + 1][0] - c[i][0]); out.append((p, ang)); break
            acc += s
    return out

def arrowhead(img, p, ang, L=24, hw=8, fill=INK, edge=(255, 255, 255)):
    """자루 달린 작은 화살(→) — 머리만 있는 세모는 비스듬하면 방향이 헷갈렸다(정삼각형에 가까워 ▼ 로 읽힘)."""
    d = ImageDraw.Draw(img); x, y = p; ux, uy = math.cos(ang), math.sin(ang); nx, ny = -uy, ux
    tip = (x + 0.5 * L * ux, y + 0.5 * L * uy)
    hb = (x + 0.0 * L * ux, y + 0.0 * L * uy)                   # 머리 밑동
    tail = (x - 0.55 * L * ux, y - 0.55 * L * uy)
    l = (hb[0] + hw * nx, hb[1] + hw * ny); r = (hb[0] - hw * nx, hb[1] - hw * ny)
    sw = max(3, L // 7)
    d.line([tail, hb], fill=edge, width=sw + 4); d.polygon([tip, l, r], fill=edge)
    d.line([tip, l, r, tip], fill=edge, width=4)
    d.line([tail, hb], fill=fill, width=sw); d.polygon([tip, l, r], fill=fill)

def arrows_on(img, c, fracs, reverse=False, **kw):
    for p, a in arclen_points(c, fracs): arrowhead(img, p, a + (math.pi if reverse else 0), **kw)

def grey_mask(a, box):
    """기계 · 바퀴(낮은 채도의 회색)와 그 먹선 — 덧칠 뒤 위로 되살릴 곳."""
    x0, y0, x1, y1 = box; sub = a[y0:y1, x0:x1].astype(int)
    mx, mn = sub.max(axis=2), sub.min(axis=2)
    g = ((mx - mn) < 34) & (mx > 55) & (mx < 235)
    g = cv2.morphologyEx(g.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(g)
    keep = np.zeros_like(g)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 120: keep[lab == i] = 1
    keep = cv2.dilate(keep, np.ones((7, 7), np.uint8))
    m = np.zeros(a.shape[:2], np.uint8); m[y0:y1, x0:x1] = keep; return m

def paper_mask(a, box):
    """흰 종이띠(빛깔 네모 · 먹선 포함) — 덧칠 뒤 위로 되살릴 곳."""
    x0, y0, x1, y1 = box; sub = a[y0:y1, x0:x1].astype(int)
    w = (sub.min(axis=2) > 205).astype(np.uint8)
    w = cv2.morphologyEx(w, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(w)
    keep = np.zeros_like(w)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 400: keep[lab == i] = 1
    keep = cv2.dilate(keep, np.ones((7, 7), np.uint8))
    m = np.zeros(a.shape[:2], np.uint8); m[y0:y1, x0:x1] = keep; return m

def restore(img, orig, mask):
    m = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    return Image.composite(orig, img, m)

def erase_rope(img, a, pts, width=36, grey_box=None, flat=False, keep_line=None):
    """주형 구간의 꼰 끈을 풀밭으로 지운다(그 위에 한 가닥을 새로 그리려고) — 기계 · 바퀴(회색)는 지우지 않는다.
    flat=True 면 띠 안의 끈 빛(황갈 · 갈색 · 먹선)만 골라 둘레 풀빛 한 가지로 채운다(번짐 없이 · keep_line 의 먹선은 남김)."""
    band = np.zeros(a.shape[:2], np.uint8)
    cv2.polylines(band, [np.int32(spline(pts))], False, 1, width)
    if grey_box is not None: band[grey_mask(a, grey_box) > 0] = 0
    if flat:
        ai = a.astype(int); R, G, B = ai[..., 0], ai[..., 1], ai[..., 2]
        grass0 = (G > R + 30) & (G > B + 60)
        ring = (cv2.dilate(band, np.ones((15, 15), np.uint8)) > 0) & (band == 0) & grass0
        col = np.median(a[ring], axis=0)
        near = np.abs(ai - col).max(axis=2) < 14                     # 풀빛과 거의 같은 것만 「풀」(끈 가장자리의 흐린 테까지 지운다)
        m = (band > 0) & ~near
        if keep_line is not None:
            kl = np.zeros(a.shape[:2], np.uint8); cv2.polylines(kl, [np.int32(keep_line)], False, 1, 5); m &= kl == 0
        out = np.array(img); out[m] = col.astype(np.uint8)
        return Image.fromarray(out)
    src = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    out = cv2.inpaint(src, band * 255, 6, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

# ── 자리(2048 × 1144 · b4 기준) ─────────────────────────────
# 오른쪽 기계: 뒤(비탈 위) 갈라짐 R · 앞(비탈 아래) 갈라짐 S · 그 사이 끈의 가운데 줄
R_R, R_S = (1362, 372), (1505, 520)
R_ROPE = [(1362, 372), (1384, 395), (1420, 434), (1450, 470), (1474, 490), (1505, 520)]
R_ARCH = [(1362, 372), (1352, 330), (1368, 288), (1404, 258), (1452, 244), (1504, 248), (1544, 270), (1564, 312), (1568, 370), (1556, 430), (1532, 482), (1505, 520)]
R_PAPER = [(1277, 283), (1307, 302), (1337, 320), (1367, 328), (1397, 316), (1427, 299)]    # 초록 띠 → 기계(종이 흰 칸의 가운데 줄)
L_PAPER = [(835, 266), (805, 284), (775, 307), (745, 337), (715, 372), (685, 402), (655, 422)]   # 초록 띠 → 기계
# 왼쪽 기계: 앞(비탈 아래 · 왼쪽) S' · 뒤(비탈 위 · 오른쪽) R'
L_S, L_R = (468, 580), (712, 390)
L_ROPE = [(468, 580), (500, 570), (530, 560), (562, 546), (600, 522), (630, 494), (656, 462), (680, 432), (698, 408), (712, 390)]
# 세발자전거 기계(Pol III)의 제 끈 — 처음엔 오른쪽 기계의 금빛 고리 밑에서 나와 「끈이 두 갈래로 갈라진다」로 읽혀(일치 검사 2회) 고리 근처를 지우고 올 풀린 끝을 단다
TRI_ROPE = [(1346, 243), (1370, 237), (1400, 232), (1440, 230), (1480, 234), (1520, 240), (1556, 250), (1578, 258)]   # 바탕 b4 의 끈 가운데 줄(언덕 등성이 선에서 시작)
TRI_END = (1599, 265)
RIDGE = [(1262, 186), (1300, 211), (1340, 237), (1372, 258), (1392, 272)]   # 언덕 등성이의 가는 먹선 — 지우지 않는다
L_ARCH = [(712, 390), (688, 382), (652, 362), (612, 342), (575, 336), (540, 340), (512, 358), (500, 392), (497, 440), (500, 500), (504, 548), (490, 574), (468, 580)]

def frayed_end(img, p, ang, n=6, L=13, col=(206, 168, 102)):
    """올 풀린 끈 끝 — 끝에서 뒤쪽(ang 반대)으로 부채꼴로 흩어진 짧은 올."""
    d = ImageDraw.Draw(img); x, y = p
    for k in range(n):
        t = math.radians(-34 + 68 * k / (n - 1)); a2 = ang + math.pi + t
        q = (x + L * math.cos(a2), y + L * math.sin(a2))
        d.line([p, q], fill=INK, width=4); d.line([p, q], fill=col, width=2)

def main(src, out):
    img = Image.open(src).convert('RGB'); orig = img.copy(); a = np.array(orig)
    img = erase_rope(img, a, TRI_ROPE, width=34, flat=True, keep_line=RIDGE)   # ⓪ 세발 기계의 끈 머리를 고리 밖으로
    frayed_end(img, TRI_END, math.atan2(300 - 262, 1700 - 1588))
    # ① 오른쪽: 기계 밑 = 갈색 주형 한 줄 · 바퀴 · 기계 되살림
    img = erase_rope(img, a, R_ROPE, grey_box=(1370, 360, 1520, 500))
    stroke(img, R_ROPE, BROWN)
    img = restore(img, orig, grey_mask(a, (1370, 360, 1520, 500)))
    # ② 오른쪽: 금빛 암호 고리 → 종이 되살림
    c_ra = stroke(img, R_ARCH, GOLD)
    img = restore(img, orig, paper_mask(a, (1330, 270, 1460, 350)))
    # ① 왼쪽: 기계 밑 = 금빛 주형 한 줄 · 바퀴 · 기계 · 갈색 고리 다리 · 종이 되살림
    img = erase_rope(img, a, L_ROPE, grey_box=(520, 470, 640, 575))
    stroke(img, L_ROPE, GOLD)
    img = restore(img, orig, grey_mask(a, (520, 470, 640, 575)))
    leg = np.zeros(a.shape[:2], np.uint8); cv2.polylines(leg, [np.int32([(500, 392), (497, 440), (500, 500), (504, 548), (494, 568)])], False, 1, 22)
    img = restore(img, orig, leg)
    img = restore(img, orig, paper_mask(a, (620, 330, 760, 450)))
    # ③ 화살 — 가닥 · 종이의 5′→3′
    arrows_on(img, c_ra, [0.30, 0.55, 0.80])                 # 금빛 암호: 뒤 → 앞(비탈 아래)
    arrows_on(img, spline(R_ROPE), [0.88], reverse=True)       # 갈색 주형(앞 구간): 기계 쪽(비탈 위)
    arrows_on(img, spline(L_ARCH), [0.30, 0.55, 0.80])         # 갈색 암호: 뒤 → 앞(비탈 아래 · 왼쪽)
    arrows_on(img, spline(L_ROPE), [0.12, 0.80])               # 금빛 주형: 비탈 위(오른쪽) 쪽
    arrows_on(img, spline(R_PAPER), [0.30, 0.72], L=20, hw=6)  # 종이: 초록 띠 → 기계(비탈 아래)
    arrows_on(img, spline(L_PAPER), [0.30, 0.72], L=20, hw=6)
    img.save(out); print('→', out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

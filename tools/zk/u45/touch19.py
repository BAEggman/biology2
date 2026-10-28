#!/usr/bin/env python3
"""touch19.py — s45u01 v3(b127 뒤): cur18 → cur19
 ① 금화를 「구슬」이 아닌 납작 동전으로 — 탁자 위 Gemini 금화 꼴(세로 타원 · 한쪽 두께 띠 · 안쪽 테 · 광택점 없음): 짐꾼 막대 셋 · C₄ 바닥 막대
 ② C₄ 사람 손 막대 = 마디 넷(끝 마디가 방울빛 — 셋 + 방울 하나) · 매달린 방울 지움
 ③ 들창 막대(놋쇠 관으로 읽힘) → 마디 넷 막대(안쪽 끝이 방울빛) · 흰 번짐 지움
 ④ 탑 아래층 공변세포(땅콩으로 읽힘)를 지움 — 새로 그리기는 Gemini G1(위층과 같은 콩팥 · 가늘고 맞붙음)"""
import sys, os, math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
sys.path.insert(0, '/tmp/b2/tools/zk/u45'); import rods
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
B = np.asarray(Image.open('cur18.png').convert('RGB')).astype(np.uint8); H, W, _ = B.shape
A = B.copy(); SS = 4
S = lambda x, y: (x * SS, y * SS)
def overlay(img, fn):
    lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); fn(ImageDraw.Draw(lay))
    im2 = img.convert('RGBA'); im2.alpha_composite(lay.resize((W, H), Image.LANCZOS)); return im2.convert('RGB')
def box_mask(x0, y0, x1, y1, cond, src=None):
    src = B if src is None else src
    m = np.zeros((H, W), np.uint8); s = src[y0:y1, x0:x1].astype(int); m[y0:y1, x0:x1] = cond(s).astype(np.uint8); return m
gold = lambda s: (s[..., 0] - s[..., 2] > 70) & (s[..., 1] - s[..., 2] > 35) & (s[..., 0] > 150)
# ── 지우기: 짐꾼 금화 셋(금빛 + 짙은 테) · C₄ 바닥 금화 · 손 막대 방울 · 들창 막대 + 흰 번짐 · 낮 공변세포
m = np.zeros((H, W), np.uint8)
for (cx, cy) in [(636, 655), (646, 666), (651, 679)]:
    m |= box_mask(cx - 12, cy - 12, cx + 12, cy + 12, gold)
m |= box_mask(1474, 748, 1496, 768, gold)
m = binary_dilation(m, iterations=2).astype(np.uint8)
A = cv2.inpaint(A, m, 3, cv2.INPAINT_TELEA)
# 손 막대의 매달린 방울(회색) 지움
md = box_mask(1560, 692, 1578, 712, lambda s: (s.mean(axis=2) < 150) & (np.abs(s[..., 0] - s[..., 2]) < 35))
A = cv2.inpaint(A, binary_dilation(md, iterations=2).astype(np.uint8), 4, cv2.INPAINT_TELEA)
# 들창 막대 + 흰 번짐(1468~1500 · 612~636) — 들창 테(어두운 세로선 x≥1498)는 남김
mh = np.zeros((H, W), np.uint8); mh[612:637, 1466:1498] = 1
A = cv2.inpaint(A, mh, 5, cv2.INPAINT_TELEA)
# 낮 공변세포(1912~1962 · 552~656) → 벽빛으로
mc = np.zeros((H, W), np.uint8); mc[552:657, 1913:1962] = 1
A = cv2.inpaint(A, mc, 6, cv2.INPAINT_TELEA)
img = Image.fromarray(A)
# ── 금화(탁자 금화 꼴)
def coin_edge(d, cx, cy, r, ang):
    """세로 타원 동전(장축 = ang 방향) · 한쪽 두께 띠 · 안쪽 테"""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(u, v):   # u: 단축(두께 쪽) · v: 장축
        return S(cx + u * ca - v * sa, cy + u * sa + v * ca)
    rx, ry = r * 0.58, r
    T = np.linspace(0, 2 * math.pi, 72)
    edge = [P(rx * math.cos(t) - r * 0.28, ry * math.sin(t)) for t in T]          # 두께(뒷면) — 왼쪽으로 비킨 타원
    face = [P(rx * math.cos(t), ry * math.sin(t)) for t in T]
    d.polygon(edge, fill=(176, 122, 26, 255), outline=(52, 34, 10, 255))
    d.line(edge + [edge[0]], fill=(52, 34, 10, 255), width=int(SS * 1.3))
    d.polygon(face, fill=(236, 190, 58, 255))
    d.line(face + [face[0]], fill=(52, 34, 10, 255), width=int(SS * 1.3))
    inner = [P(rx * 0.72 * math.cos(t), ry * 0.78 * math.sin(t)) for t in T]
    d.line(inner + [inner[0]], fill=(186, 136, 30, 255), width=int(SS * 1.1))
    mid = [P(rx * 0.34 * math.cos(t) + r * 0.05, ry * 0.42 * math.sin(t)) for t in T]
    d.polygon(mid, fill=(246, 210, 96, 255))
def coins(d):
    # 짐꾼 막대 셋 — 막대 축에 직각으로 선 동전, 앞끝 옆구리(아래쪽 등)에 반쯤 박힘
    for (p0, p1) in [((626, 665), (760, 528)), ((636, 676), (765, 539)), ((641, 689), (767, 551))]:
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
        cx, cy = p0[0] + ux * 17 + (-uy) * 5.0, p0[1] + uy * 17 + ux * 5.0
        coin_edge(d, cx, cy, 8.0, math.atan2(uy, ux))
    coin_edge(d, 1483, 757, 7.5, 0.0)
img = overlay(img, coins)
# 짐꾼 손은 되살림(살빛 덩어리) — 동전이 손을 덮지 않게
from scipy.ndimage import label, binary_closing, binary_fill_holes
Sb = B[585:650, 665:730].astype(float); Rr, Gg, Bb = Sb[..., 0], Sb[..., 1], Sb[..., 2]; Lb = Sb.mean(axis=2)
skin = (Rr - Bb >= 25) & (Rr - Bb <= 75) & (Lb >= 150) & (Lb <= 228) & (Rr - Gg >= 8) & (Rr - Gg <= 45) & (Gg > Bb)
lab, nl = label(skin); keep = np.zeros_like(skin)
for i in range(1, nl + 1):
    ys, xs = np.where(lab == i)
    if len(ys) >= 15 and abs(xs.mean() + 665 - 692) < 16 and abs(ys.mean() + 585 - 619) < 16: keep |= (lab == i)
keep = binary_fill_holes(binary_closing(keep, iterations=2)); ring = binary_dilation(keep, iterations=2) & ~keep & (Lb < 105)
hm = np.zeros((H, W), bool); hm[585:650, 665:730] = keep | ring
C = np.asarray(img).copy(); C[hm] = B[hm]; img = Image.fromarray(C)
# ── ② 손 막대 마디 넷(끝이 방울빛) · 손 되살림
Sb = B[655:700, 1588:1626].astype(float); Rr, Gg, Bb = Sb[..., 0], Sb[..., 1], Sb[..., 2]; Lb = Sb.mean(axis=2)
sk = (Rr - Bb >= 20) & (Rr - Bb <= 80) & (Lb >= 140) & (Lb <= 218) & (Rr - Gg >= 16) & (Gg > Bb)
lab, nl = label(sk); keep = np.zeros_like(sk)
for i in range(1, nl + 1):
    if (lab == i).sum() >= 25: keep |= (lab == i)
keep = binary_fill_holes(binary_closing(keep, iterations=2)); ring = binary_dilation(keep, iterations=2) & ~keep & (Lb < 105)
hand = np.zeros((H, W), bool); hand[655:700, 1588:1626] = keep | ring
img = rods.draw_rod(img, (1630, 669), (1558, 693), 4, 11, first='cream', dark_last=True)
C = np.asarray(img).copy(); C[hand] = B[hand]; img = Image.fromarray(C)
# ── ③ 들창 막대(마디 넷 · 안쪽 끝 방울빛)
img = rods.draw_rod(img, (1516, 626), (1470, 629), 4, 10, first='cream', dark_last=True)
# 들창 테 오른쪽 세로선을 막대 위로 다시(막대가 구멍을 지난다)
def hatch_edge(d):
    d.line([S(1508.5, 609), S(1508.5, 619.5)], fill=(40, 36, 32, 255), width=int(SS * 1.6))
    d.line([S(1508.5, 633.5), S(1508.5, 641)], fill=(40, 36, 32, 255), width=int(SS * 1.6))
img = overlay(img, hatch_edge)
# ── ④ 낮 공변세포: 위층과 같은 초록 · 가늘어져 맞붙음(곧은 안쪽 벽)
def closed_cells(d):
    GREEN, GREEN_HL, RIM, OUT = (128, 166, 76, 255), (168, 200, 104, 255), (78, 104, 52, 255), (28, 30, 20, 255)
    for side in (-1, 1):
        cx0 = 1937.5
        pts = []
        for t in np.linspace(-math.pi / 2, math.pi / 2, 60):
            x = cx0 + side * (14.5 * math.cos(t)); y = 604 + 43 * math.sin(t)
            pts.append((x, y))
        pts = [(cx0, 604 - 43)] + pts + [(cx0, 604 + 43)]
        poly = [S(x, y) for (x, y) in pts]
        d.polygon(poly, fill=GREEN)
        inner = [S(cx0 + side * 10.5 * math.cos(t), 604 + 37 * math.sin(t)) for t in np.linspace(-math.pi / 2, math.pi / 2, 50)]
        d.line(inner, fill=RIM, width=int(SS * 1.3))
        hl = [S(cx0 + side * 7.5 * math.cos(t) + side * 1.5, 596 + 22 * math.sin(t)) for t in np.linspace(-math.pi / 2.4, math.pi / 2.6, 30)]
        d.line(hl, fill=GREEN_HL, width=int(SS * 3.2))
        d.line(poly + [poly[0]], fill=OUT, width=int(SS * 1.8))
    d.line([S(1937.5, 561), S(1937.5, 647)], fill=OUT, width=int(SS * 1.8))
# (④ 그리기는 Gemini G1 로 — 여기서는 지우기만)
img.save('cur19.png')
for (b, n) in [((600, 620, 700, 710), 'v19_porter.png'), ((1440, 600, 1640, 780), 'v19_c4.png'), ((1880, 520, 1980, 670), 'v19_day.png')]:
    img.crop(b).resize(((b[2] - b[0]) * 4, (b[3] - b[1]) * 4), Image.LANCZOS).save(n)
print('cur19 saved')

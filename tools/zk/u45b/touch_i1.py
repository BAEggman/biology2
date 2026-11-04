#!/usr/bin/env python3
"""touch_i1.py — s45u02 v10 (b140 닻대조 뒤 · 사용자 「한 장 유지, 손질 계속」 · 잣대 「닻 판 대조」)
닻 s45u01 은 둘 다 맞히고 이 판은 둘 다 놓친 행을 그림으로 세운다:
 ① 행 12 — 무대 무리 전체(두 자매 · 당근 · 쌍둥이와 사발)를 **밧줄 한 바퀴**가 허리께로 둘러 앞에서 매듭지었다
           (한 줄로 맨 무리 = 한 덩이 = 광계 — 系 는 실로 이어 맨 것 · 약속 #170). 뒤쪽 반은 인물 뒤로(벽 화소에만), 앞쪽 반은 인물 앞으로.
 ② 행 9 — 사발 양 테에서 두 쌍둥이 목으로 **끈 둘**(둘이 사발을 함께 멨다 — 반응중심 = 쌍 + 사발, 떨어지지 않는 한 몸 · #170).
 ③ 행 10 — 걸상 초록 띠 헤엄이 위에 **아주 작은 방울 하나**(녹색광 광합성은 가장 적지만 ⚠ 없는 것은 아니다).
 ④ 손질 자국(b140 채점자가 확인) — d 글자 속 점 · 안개 흰 얼룩 · 꼬투리 렌즈 위 곱슬 철사.
사용: touch_i1.py in.png out.png"""
import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, binary_dilation

src, dst = sys.argv[1:3]
img = Image.open(src).convert('RGB'); W, H = img.size
A = np.asarray(img).astype(float)
SS = 4
S = lambda p: (p[0] * SS, p[1] * SS)
lum = A.mean(axis=2); sat = A.max(axis=2) - A.min(axis=2)

HEMP, HEMP_D, HEMP_L, INK = (186, 146, 84), (126, 92, 50), (226, 196, 140), (58, 40, 24)

def rope(d, pts, w, ticks=True):
    """pts: 1x 좌표의 점 줄. w: 1x 굵기. 테 · 몸 · 꼰 결 · 윗빛."""
    P = [S(p) for p in pts]
    d.line(P, fill=INK + (255,), width=int(SS * (w + 2.0)), joint='curve')
    d.line(P, fill=HEMP + (255,), width=int(SS * w), joint='curve')
    # 윗빛(법선 위쪽으로 w·0.22)
    hl = []
    for i in range(len(pts)):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, len(pts) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; n = math.hypot(tx, ty) or 1
        nx, ny = ty / n, -tx / n
        if ny > 0: nx, ny = -nx, -ny
        hl.append(S((pts[i][0] + nx * w * 0.22, pts[i][1] + ny * w * 0.22)))
    d.line(hl, fill=HEMP_L + (200,), width=max(1, int(SS * w * 0.28)), joint='curve')
    if not ticks: return
    # 꼰 결: 길이 4.2 px 마다 비스듬한 짧은 금
    acc = 0.0
    for i in range(1, len(pts)):
        a, b = pts[i - 1], pts[i]
        seg = math.hypot(b[0] - a[0], b[1] - a[1]); acc += seg
        if acc < 4.2: continue
        acc = 0.0
        tx, ty = (b[0] - a[0]) / (seg or 1), (b[1] - a[1]) / (seg or 1)
        nx, ny = ty, -tx
        c = b
        p0 = (c[0] - nx * w * 0.48 - tx * 1.2, c[1] - ny * w * 0.48 - ty * 1.2)
        p1 = (c[0] + nx * w * 0.48 + tx * 1.2, c[1] + ny * w * 0.48 + ty * 1.2)
        d.line([S(p0), S(p1)], fill=HEMP_D + (235,), width=max(1, int(SS * 0.9)))

def down(lay):
    return np.asarray(lay.resize((W, H), Image.LANCZOS)).astype(float)

def comp(A, L, mask=None):
    al = L[..., 3:4] / 255.0
    if mask is not None: al = al * mask[..., None]
    return A * (1 - al) + L[..., :3] * al

# ── ① 밧줄 한 바퀴(행 12)
cx, cy, rx, ry = 1185.0, 511.5, 285.0, 63.5          # 뒤 반은 쌍둥이 액자 머리 위(y≈449 — 머리 윗변 458~464)로 · 앞 반은 사발 밑(y≈574)으로
def ell(t):
    return (cx + rx * math.cos(t), cy + ry * math.sin(t) + 0.7 * math.sin(5.0 * t))
back = [ell(math.pi + k * math.pi / 240) for k in range(241)]          # 위(뒤) 반
front = [ell(k * math.pi / 240) for k in range(241)]                    # 아래(앞) 반
# 뒤 반: 벽 화소(밝고 덜 짙은)에만 — 인물 · 금빛 물결 뒤로 숨는다
bg = ((lum > 212) & (lum < 245) & (sat < 36)).astype(float)       # 아주 흰 빛줄기(당근 망토에 닿는 흰 빔)는 앞의 것으로
bg = gaussian_filter(bg, 0.6)
L = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); rope(ImageDraw.Draw(L), back, 4.6)
Lb = down(L)
# 뒤 반은 조금 옅게(멀다)
Lb[..., :3] = Lb[..., :3] * 0.92 + np.array([236, 232, 220]) * 0.08
A = comp(A, Lb, bg)
# 앞 반 그늘(인물 위 · 아래로 3 px 비켜 흐림)
L = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
dd.line([S((p[0] + 1.0, p[1] + 3.2)) for p in front], fill=(30, 22, 16, 92), width=int(SS * 5.5), joint='curve')
Ls = np.asarray(L.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.6))).astype(float)
A = comp(A, Ls)
# 앞 반 밧줄
L = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
rope(dd, front, 5.2)
# 매듭(앞 가운데 조금 왼쪽 · 당근과 쌍둥이 사이) + 늘어진 두 끝 — 「맸다(系)」가 보이게 매듭을 크게
tk = math.acos((1150.0 - cx) / rx); kx, ky = ell(tk)
for side, (dx1, dx2), ln in ((-1, (-4.0, -8.5), 19.0), (1, (3.5, 7.5), 16.0)):
    pts = []
    for i in range(17):
        s_ = i / 16.0
        pts.append((kx + side * 2.0 + dx1 * s_ + (dx2 - dx1) * s_ * s_, ky + 4 + ln * s_))
    rope(dd, pts, 3.8, ticks=True)
    tip = pts[-1]
    for j in (-1.6, -0.5, 0.6, 1.6):          # 풀린 끝 술
        dd.line([S(tip), S((tip[0] + j, tip[1] + 3.6))], fill=HEMP_D + (230,), width=int(SS * 0.8))
dd.ellipse([S((kx - 7.0, ky - 5.4)), S((kx + 7.0, ky + 5.8))], fill=HEMP + (255,), outline=INK + (255,), width=int(SS * 1.2))
dd.arc([S((kx - 5.0, ky - 3.8)), S((kx + 5.0, ky + 4.2))], 200, 340, fill=HEMP_D + (255,), width=int(SS * 1.0))
dd.arc([S((kx - 4.0, ky - 1.2)), S((kx + 4.4, ky + 4.6))], 20, 160, fill=HEMP_D + (255,), width=int(SS * 1.0))
dd.arc([S((kx - 3.0, ky - 3.0)), S((kx + 1.0, ky + 0.0))], 180, 300, fill=HEMP_L + (220,), width=int(SS * 0.8))
A = comp(A, down(L))

# ── ② 사발을 두 쌍둥이 목에 건 끈 둘(행 9)
def bez(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [k / n for k in range(n + 1)]]
L = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
cordL = bez((1213.5, 552.0), (1203.0, 528.0), (1197.5, 504.5))
cordR = bez((1251.5, 552.0), (1262.0, 528.0), (1265.0, 504.5))
for c in (cordL, cordR):
    rope(dd, c, 2.0, ticks=False)
for (x, y) in ((1213.5, 552.0), (1251.5, 552.0)):              # 테에 맨 작은 매듭
    dd.ellipse([S((x - 2.0, y - 1.8)), S((x + 2.0, y + 2.0))], fill=HEMP + (255,), outline=INK + (255,), width=int(SS * 0.8))
A = comp(A, down(L))

# ── ③ 초록 띠 헤엄이 위 아주 작은 방울(행 10)
L = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
bx_, by_, r = 1767.5, 619.0, 2.3
dd.ellipse([S((bx_ - r - 0.7, by_ - r - 0.7)), S((bx_ + r + 0.7, by_ + r + 0.7))], fill=(150, 160, 178, 255))
dd.ellipse([S((bx_ - r, by_ - r)), S((bx_ + r, by_ + r))], fill=(250, 251, 253, 255))
dd.ellipse([S((bx_ - 1.1, by_ - 1.3)), S((bx_ + 0.1, by_ - 0.2))], fill=(255, 255, 255, 255))
A = comp(A, down(L))

# ── ④ 손질 자국
def nfill(A, M, box, sig=2.2):
    """M(1 = 걷을 화소) 을 둘레 화소의 가중 평균(정규화 합성곱)으로 메움 — box 안에서만."""
    x0, y0, x1, y1 = box
    sub = A[y0:y1, x0:x1]; m = M[y0:y1, x0:x1]; keep = 1.0 - m
    num = np.stack([gaussian_filter(sub[..., c] * keep, sig) for c in range(3)], axis=2)
    den = gaussian_filter(keep, sig)[..., None]
    fill = num / np.maximum(den, 1e-6)
    ms = np.clip(gaussian_filter(m, 0.6) * 1.3, 0, 1)[..., None]
    A[y0:y1, x0:x1] = sub * (1 - ms) + fill * ms
    return A
# d 글자 속 점: 고리 안 짙은 화소를 몸 빛으로
M = np.zeros((H, W))
box = (1825, 509, 1833, 516)
for y in range(box[1], box[3]):
    for x in range(box[0], box[2]):
        if lum[y, x] < 130: M[y, x] = 1.0
body = np.array([176.0, 135.0, 124.0])
ms = np.clip(gaussian_filter(M, 0.5) * 1.2, 0, 1)
for y in range(box[1] - 1, box[3] + 1):
    for x in range(box[0] - 1, box[2] + 1):
        if ms[y, x] > 0 and lum[y, x] < 200:      # 노랑 고리는 건드리지 않음
            A[y, x] = A[y, x] * (1 - ms[y, x]) + body * ms[y, x]
# 안개 흰 얼룩: 넉넉한 타원 안을 둘레 안개만으로 메움(문턱 등고선이 남지 않게 — v7 교훈 · 같은 재질 화소만 경계로)
yy, xx = np.mgrid[0:H, 0:W]
E = (((xx - 1798.5) / 15.0) ** 2 + ((yy - 402.0) / 7.5) ** 2)
hole = (E < 1.0).astype(float)
x0, y0, x1, y1 = 1764, 380, 1834, 425
sub = A[y0:y1, x0:x1]; keep = 1.0 - hole[y0:y1, x0:x1]
num = np.stack([gaussian_filter(sub[..., c] * keep, 5.0) for c in range(3)], axis=2)
den = gaussian_filter(keep, 5.0)[..., None]
fill = num / np.maximum(den, 1e-6)
ms = np.clip(1.25 - E[y0:y1, x0:x1], 0, 1)[..., None]           # 가장자리 0.25 폭에서 천천히
ms = gaussian_filter(ms[..., 0], 1.2)[..., None]
A[y0:y1, x0:x1] = sub * (1 - ms) + fill * ms
# 결 되살림: 아주 옅은 잡결(둘레 안개의 잡결 세기 만큼)
rng = np.random.default_rng(7)
noise = gaussian_filter(rng.normal(0, 1.0, (y1 - y0, x1 - x0)), 0.7) * 1.6
A[y0:y1, x0:x1] += (noise[..., None] * ms)
# 렌즈 위 곱슬 철사: 벽 화소(밝고 덜 짙은)만 둘레로 — 루비 렌즈 · 테 화소는 쓰지 않는다
M = np.zeros((H, W))
for y in range(633, 644):
    for x in range(645, 658):
        if lum[y, x] < 168: M[y, x] = 1.0
M = binary_dilation(M > 0, iterations=1).astype(float); M[644:, :] = 0
x0, y0, x1, y1 = 630, 618, 672, 646
sub = A[y0:y1, x0:x1]
wall = ((lum[y0:y1, x0:x1] > 168) & (sat[y0:y1, x0:x1] < 48)).astype(float)
keep = wall * (1.0 - M[y0:y1, x0:x1])
num = np.stack([gaussian_filter(sub[..., c] * keep, 2.5) for c in range(3)], axis=2)
den = gaussian_filter(keep, 2.5)[..., None]
fill = num / np.maximum(den, 1e-6)
ms = np.clip(gaussian_filter(M[y0:y1, x0:x1], 0.6) * 1.4, 0, 1)
ms[(y0 + np.arange(y1 - y0))[:, None].repeat(x1 - x0, 1) >= 643] = 0     # 렌즈 테 줄은 그대로
A[y0:y1, x0:x1] = sub * (1 - ms[..., None]) + fill * ms[..., None]

Image.fromarray(np.clip(A, 0, 255).astype('uint8')).save(dst)
print('ok', dst)

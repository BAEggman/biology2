# u02v4.py — cur4 → cur5 (b117 뒤 손질): ① 상행지 벽의 T자 핀 16개 → 이음매에 메운 역청 띠 ② 가위표 뒤 V 를 통째로 보이게(크게 · 볼트 셋 · 널빤지는 그 위로)
#  ③ 자루 셋 뒤에 펌프 쪽에서 문 안으로 날아드는 움직임 꼬리 ④ 동전을 테두리 있는 납작한 동전으로 ⑤ 병사 발치 받침을 짙은 갈색 나무로(요와 안 헷갈리게)
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, gaussian_filter
A = np.asarray(Image.open('cur4.png').convert('RGB')).astype(float); H, W, _ = A.shape
rng = np.random.default_rng(23)
lum = A.mean(axis=2); sat = (A.max(axis=2) - A.min(axis=2)) / (A.max(axis=2) + 1e-6)
# ── ① T 핀 지우기
pins = [(905, y) for y in (250, 305, 359, 414, 469)] + [(1011, y) for y in (250, 305, 359, 414, 469)] + [(920, y) for y in (561, 615, 668, 722)] + [(992, y) for y in (561, 615, 668, 722)]
m = np.zeros((H, W), np.uint8)
for (cx, y) in pins:
    box = (slice(y - 6, y + 11), slice(cx - 12, cx + 12)); m[box] = (lum[box] < 95)
m = binary_dilation(m, iterations=1).astype(np.uint8)
# ── ② V: 널빤지 가면(나무색 + 그 둘레 먹선)과 옛 V 판(흰 무채색) 가면
R, G, B = A[..., 0], A[..., 1], A[..., 2]
reg = (slice(320, 505), slice(176, 336))
wood = np.zeros((H, W), bool); wood[reg] = (R[reg] > 150) & (G[reg] > 120) & (R[reg] - B[reg] > 35)
wood = binary_dilation(wood, iterations=1)
outline = np.zeros((H, W), bool); outline[reg] = lum[reg] < 80
boards = wood | (binary_dilation(wood, iterations=3) & outline)
A0 = np.asarray(Image.open('cur0.png').convert('RGB')).astype(float)
plate = np.zeros((H, W), bool); plate[reg] = (np.abs(A[reg] - A0[reg]).mean(axis=2) > 22) | ((lum[reg] > 196) & (sat[reg] < 0.07))
stream = (B - R > 6) & (lum > 140)
plate &= ~binary_dilation(stream, iterations=1)
plate_m = (binary_dilation(plate, iterations=3) & ~boards)
m |= plate_m.astype(np.uint8)
C8 = cv2.inpaint(np.clip(A, 0, 255).astype('uint8'), m, 5, cv2.INPAINT_TELEA); C = C8.astype(float)
board_px = A.copy()                                          # 널빤지 화소(원본)
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img, 'RGBA')
STEEL, STEEL_D, OUT = (236, 238, 234), (196, 200, 196), (52, 48, 44)
def Vfit(cx, top, bot, half, w, r):
    a = math.atan2(half, bot - top); k = (w / 2) / math.sin(a)
    pts = [(cx - half - w / 2, top), (cx - half + w / 2, top), (cx, bot - k), (cx + half - w / 2, top), (cx + half + w / 2, top), (cx + w * 0.3, bot + w * 0.3), (cx - w * 0.3, bot + w * 0.3)]
    d.polygon(pts, fill=STEEL, outline=OUT); d.line(pts + [pts[0]], fill=OUT, width=2)
    ins = [(cx - half - w / 2 + w * 0.22, top + w * 0.22), (cx - half + w / 2 - w * 0.22, top + w * 0.22), (cx, bot - k - w * 0.45), (cx + half - w / 2 + w * 0.22, top + w * 0.22), (cx + half + w / 2 - w * 0.22, top + w * 0.22), (cx + w * 0.12, bot + w * 0.05), (cx - w * 0.12, bot + w * 0.05)]
    d.line(ins + [ins[0]], fill=STEEL_D, width=1)
    for (bx, by) in [(cx - half, top + w * 0.55), (cx + half, top + w * 0.55), (cx, bot - k - w * 0.25 - r * 0.6)]:
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(96, 90, 84), outline=OUT); d.ellipse([bx - r * 0.45, by - r * 0.55, bx + r * 0.05, by - r * 0.05], fill=(210, 206, 200))
Vfit(250, 340, 478, 40, 18, 3.6)
C = np.asarray(img).astype(float)
bm = gaussian_filter(boards.astype(float), 0.5)
C = C * (1 - bm[..., None]) + board_px * bm[..., None]           # 널빤지를 V 위로 되돌린다
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img, 'RGBA')
# 못(V 두 팔 사이 · 벽에 박힘)
d.line([(250, 366), (257, 376)], fill=(58, 58, 62), width=3); d.ellipse([245, 361, 254, 370], fill=(84, 84, 90), outline=(30, 30, 34))
# ── ① 역청: 상행지 두 벽의 널빤지 이음매(세로 금)를 새까만 역청으로 메움 + 널빤지 끝 가로 이음매 몇 개
TAR, GLOSS = (14, 12, 12, 255), (160, 160, 160, 230)
def vseam(x, ya, yb, skip=None):
    y = ya
    while y < yb:
        if skip and skip[0] <= y <= skip[1]: y = skip[1] + 1; continue
        seg = min(yb, y + 14)
        w = 1.8 + rng.random() * 1.0
        d.polygon([(x - w, y), (x + w, y), (x + w * 0.9 + rng.normal(0, 0.3), seg), (x - w * 0.9 + rng.normal(0, 0.3), seg)], fill=TAR)
        if rng.random() < 0.35:
            by = y + rng.random() * 14; r = 2.2 + rng.random() * 1.2; d.ellipse([x - r, by - r * 0.8, x + r, by + r * 0.8], fill=TAR)
        if rng.random() < 0.3:
            gy = y + rng.random() * 12; d.line([(x - 0.6, gy), (x - 0.6, gy + 3)], fill=GLOSS, width=1)
        y = seg
def hjoint(xa, xb, y):
    top = [(x, y - 1.6 - rng.random() * 0.8) for x in np.linspace(xa, xb, 5)]
    bot = [(x, y + 1.6 + rng.random() * 0.8) for x in np.linspace(xb, xa, 5)]
    d.polygon(top + bot, fill=TAR); d.line([(xa + 2, y - 0.8), (xa + 5, y - 0.8)], fill=GLOSS, width=1)
vseam(908, 170, 474)                       # 위 굵은 토막 왼 벽
vseam(1015, 170, 238)
vseam(1015, 272, 474, skip=(322, 412))     # 오른 벽(칼 홈 · 투입구 자리 건너뜀)
vseam(924, 494, 760)                       # 아래 가는 토막 왼 벽
vseam(987, 494, 760)                       # 오른 벽
for y in (360, 430):
    hjoint(897, 919, y)
for y in (300, 440):
    hjoint(1004, 1027, y)
for y in (560, 640, 720):
    hjoint(912, 925, y); hjoint(980, 1000, y)
# ── ③ 자루 셋의 움직임 꼬리(펌프 쪽 → 문 안 구리관): 각 자루의 오른 아래로 가는 곡선 셋
for (sx, sy, s) in [(1912, 108, 0.6), (1932, 124, 0.8), (1958, 148, 1.0)]:
    for k in range(3):
        a0 = (k - 1) * 5 * s
        pts = [(sx + 8 * s + t * 20 * s, sy + 6 * s + a0 + t * 14 * s + math.sin(t * 3) * 2) for t in np.linspace(0, 1, 6)]
        d.line(pts[1:5], fill=(255, 255, 255, 190), width=1)
# 펌프 머리에서 문 아래 문턱까지 옅은 점선 궤적
for t in np.linspace(0.08, 0.92, 9):
    x = 1966 + (1940 - 1966) * t - math.sin(t * math.pi) * 18; y = 228 + (150 - 228) * t - math.sin(t * math.pi) * 10
    d.ellipse([x - 1.3, y - 1.3, x + 1.3, y + 1.3], fill=(255, 255, 255, 210))
# ── ④ 동전: 옛 반원 지우고 테두리 있는 납작한 동전(투입구에 반쯤)
C = np.asarray(img).astype(float); C[219:236, 1956:1976] = A[219:236, 1936:1956]
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img, 'RGBA')
d.pieslice([1957, 220, 1975, 250], 180, 360, fill=(226, 178, 34, 255), outline=(70, 50, 10, 255))
d.arc([1960, 223, 1972, 247], 180, 360, fill=(160, 112, 18, 255), width=1)
d.line([(1962, 229), (1969, 226)], fill=(255, 236, 140, 255), width=1)
d.line([(1955, 235), (1977, 235)], fill=(28, 26, 24, 255), width=2)
# ── ⑤ 병사 받침 짙은 갈색
C = np.asarray(img).astype(float); sx0, sy0, sx1, sy1 = 1014, 289, 1092, 317; regc = C[sy0:sy1, sx0:sx1]
l2 = regc.mean(axis=2); s2 = (regc.max(axis=2) - regc.min(axis=2)) / (regc.max(axis=2) + 1e-6)
woodp = (regc[..., 0] - regc[..., 2] > 30) & (l2 > 120)
t = np.clip((l2 - 130) / 90, 0, 1)[..., None]
dk = np.array([110, 74, 44]) * (1 - t) + np.array([160, 116, 74]) * t
regc[woodp] = dk[woodp]; C[sy0:sy1, sx0:sx1] = regc
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8'))
img.save('cur5.png')
img.crop((170, 320, 350, 500)).resize((540, 540), Image.LANCZOS).save('v5_V.png')
img.crop((870, 280, 1040, 780)).resize((340, 1000), Image.LANCZOS).save('v5_asc.png')
img.crop((1820, 20, 2048, 340)).resize((456, 640), Image.LANCZOS).save('v5_door.png'); print('cur5 saved')

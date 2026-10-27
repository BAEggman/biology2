# u02pil.py — cur3 → cur4: s17u02 남은 손질(PIL)
#  ① 꺾인 뒤 수로 위·아래 널빤지 이음매에 새까만 역청(덩이 · 광 · 흘러내림) ② 운하 물의 옛 합성 단(x≈1525·1585) 가로 섞기 + 둘째 기계 뒤 물빛 한 단 더 옅게
#  ③ 첫 기계 네모 투입구로 관 속 흰 결정이 빨려 드는 자취 ④ 병사 발치 돌석판 → 나무 받침 ⑤ 펌프 동전 투입구에 금빛 동전 반쯤
import math, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
A = np.asarray(Image.open('cur3.png').convert('RGB')).astype(float); C = A.copy(); H, W, _ = A.shape
rng = np.random.default_rng(17)
# ② 물: 가로 블러를 매끈한 곳에만(x 1480~1640 · y 89~155) + 둘째 기계 뒤 옅게
y0, y1, x0, x1 = 89, 156, 1470, 1650
Wt = C[y0:y1, x0:x1]; Bl = np.stack([gaussian_filter(Wt[..., c], (1.0, 26)) for c in range(3)], axis=2)
dif = np.abs(Wt - Bl).mean(axis=2); al = np.clip(1 - dif / 14, 0, 1) * 0.9; al = gaussian_filter(al, 1.0)
f = 8; M = np.ones_like(al); M[:3] = 0; M[-3:] = 0; M[:, :f] = 0; M[:, -f:] = 0; M = gaussian_filter(M, 4); M /= M.max(); al *= M
C[y0:y1, x0:x1] = Wt * (1 - al[..., None]) + Bl * al[..., None]
pale = np.array([232, 241, 238], float)
for x in range(1760, 1872):
    t = min(1.0, (x - 1760) / 40) * 0.28
    col = C[89:156, x]; isw = (col[:, 2] > col[:, 0] - 4) & (col.mean(axis=1) > 150)   # 물빛(푸르스름) 만
    col[isw] = col[isw] * (1 - t) + pale * t; C[89:156, x] = col
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img, 'RGBA')
# ① 역청 이음매
TAR, GLOSS = (16, 14, 14, 255), (150, 150, 150, 220)
def tarseam(x, ya, yb, drip=False):
    pts_l, pts_r = [], []
    for y in np.linspace(ya, yb, 9):
        w = 2.4 + rng.random() * 1.6; c = x + rng.normal(0, 0.5)
        pts_l.append((c - w, y)); pts_r.append((c + w, y))
    d.polygon(pts_l + pts_r[::-1], fill=TAR)
    for _ in range(2):
        by = ya + rng.random() * (yb - ya); bx = x + rng.normal(0, 1.0); r = 2 + rng.random() * 1.6
        d.ellipse([bx - r, by - r * 0.8, bx + r, by + r * 0.8], fill=TAR)
    gy = ya + (yb - ya) * (0.25 + rng.random() * 0.4); d.ellipse([x - 1.6, gy - 1.2, x + 0.4, gy + 1.0], fill=GLOSS)
    if drip:
        L = 5 + rng.random() * 5; d.line([(x + 0.5, yb), (x + 0.5, yb + L)], fill=TAR, width=2); d.ellipse([x - 1.5, yb + L - 1, x + 2.5, yb + L + 3], fill=TAR)
for i, x in enumerate([1070, 1190, 1310, 1430, 1550, 1640, 1790]):
    tarseam(x, 64, 86, drip=False)
for i, x in enumerate([1136, 1256, 1376, 1496, 1616, 1736, 1856]):
    tarseam(x, 158, 184, drip=(i % 2 == 1))
# ③ 투입구로 빨려 드는 결정 — 깔때기꼴로 모여 드는 흰 알갱이(선 없이) + 옅은 소용돌이 물결 둘
MX, MY = 984, 392
for k in range(34):
    t = rng.random() ** 0.7
    bx = 926 + (MX - 6 - 926) * t
    h = 38 * (1 - t) + 3
    by = MY + rng.uniform(-h, h)
    r = 2.1 - 1.0 * t + rng.random() * 0.4
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 255, 255, 255), outline=(150, 178, 178, 255))
for k in range(9):
    bx = 968 + rng.random() * 22; by = MY + rng.uniform(-9, 9); r = 1.0 + rng.random() * 0.6
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=(250, 250, 246, 255))
for (a0, a1, rr) in [(150, 210, 30), (140, 220, 46)]:
    d.arc([MX - rr * 2, MY - rr, MX, MY + rr], a0, a1, fill=(225, 246, 246, 140), width=1)
# ④ 돌석판 → 나무 받침(x 1016~1090 · y 290~316)
sx0, sy0, sx1, sy1 = 1014, 289, 1092, 317
Cc = np.asarray(img).astype(float); reg = Cc[sy0:sy1, sx0:sx1]
lum = reg.mean(axis=2); sat = (reg.max(axis=2) - reg.min(axis=2)) / (reg.max(axis=2) + 1e-6)
stone = (sat < 0.14) & (lum > 95)
wood_hi, wood_lo = np.array([224, 196, 140]), np.array([168, 132, 84])
t = np.clip((lum - 110) / 120, 0, 1)[..., None]
woodc = wood_lo * (1 - t) + wood_hi * t
reg[stone] = woodc[stone]
Cc[sy0:sy1, sx0:sx1] = reg
img = Image.fromarray(np.clip(Cc, 0, 255).astype('uint8')); d = ImageDraw.Draw(img, 'RGBA')
for gy in (296, 302, 309):
    d.line([(sx0 + 4, gy + rng.normal(0, 0.4)), (sx1 - 5, gy + rng.normal(0, 0.4))], fill=(140, 104, 60, 150), width=1)
# ⑤ 동전 반쯤(투입구 중심 1966, 235)
d.chord([1959, 222, 1973, 248], 180, 360, fill=(232, 186, 40, 255), outline=(70, 50, 10, 255))
d.arc([1961, 224, 1971, 246], 200, 300, fill=(255, 236, 140, 255), width=1)
d.line([(1957, 235), (1975, 235)], fill=(30, 28, 26, 255), width=2)
img.save('cur4.png')
img.crop((900, 40, 1900, 200)).resize((1500, 240), Image.LANCZOS).save('v4_canal.png')
img.crop((900, 270, 1110, 460)).resize((630, 570), Image.LANCZOS).save('v4_intake.png')
img.crop((1930, 210, 2000, 260)).resize((420, 300), Image.LANCZOS).save('v4_coin.png'); print('cur4 saved')

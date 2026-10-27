# v9pil.py — cur7 → cur8: ① 병사의 칼을 넓은 곧은 단검(글라디우스)으로 ② 물실을 「벽 틈에서 나와 옆으로 휘어 껍질에 스미는 실 + 불규칙한 젖은 얼룩」으로 ③ 구리관 다리에 흐름 화살(왼 ↓ · 오른 ↑)
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation
A = np.asarray(Image.open('cur7.png').convert('RGB')).astype(float); H, W, _ = A.shape
rng = np.random.default_rng(9)
# ── ① 옛 가는 칼(날 x 408~420 · y 76~104)을 인페인트로 지운다(물결 고리는 남김)
R, G, B = A[..., 0], A[..., 1], A[..., 2]
reg = A[74:106, 404:424]; m = np.zeros((H, W), np.uint8)
blade = (reg.mean(axis=2) < 150) | ((reg.std(axis=2) < 10) & (reg.mean(axis=2) > 150) & (reg.mean(axis=2) < 215))
m[74:106, 404:424] = blade
m[74:106, 404:424] &= 1
m = binary_dilation(m, iterations=1).astype(np.uint8)
C8 = cv2.inpaint(np.clip(A, 0, 255).astype('uint8'), m, 3, cv2.INPAINT_TELEA)
img = Image.fromarray(C8); d = ImageDraw.Draw(img, 'RGBA')
STEEL, RIDGE, OUT = (226, 229, 232), (168, 174, 180), (38, 38, 42)
cx = 413
# 날: 코등이 아래 y 79 에서 시작 · 너비 8 → 끝에서 9 로 살짝 부풀었다가 뾰족(글라디우스 잎꼴)
pts = [(cx - 4, 79), (cx + 4, 79), (cx + 4.6, 96), (cx, 108), (cx - 4.6, 96)]
d.polygon(pts, fill=STEEL, outline=OUT); d.line(pts + [pts[0]], fill=OUT, width=1)
d.line([(cx, 80), (cx, 104)], fill=RIDGE, width=1)
# 물속 부분(y ≥ 92)은 물빛을 덮어 잠긴 듯
d.polygon([(cx - 4.8, 92), (cx + 4.8, 92), (cx + 4.6, 96), (cx, 108), (cx - 4.6, 96)], fill=(150, 196, 200, 95))
# 코등이(가로) · 손잡이 끝(손 위로 둥근 자루머리)
d.rectangle([cx - 8, 75, cx + 8, 79], fill=(132, 104, 64), outline=OUT)
# ── ② 물실: 옛 얼룩·선 자리(x 1124~1177 · y 486~527)를 아래 깨끗한 껍질 행(y 530~571)으로 덮고 다시
C = np.asarray(img).astype(float)
x0, x1, y0, y1 = 1124, 1177, 486, 527
patch = A[530:530 + (y1 - y0), x0:x1].copy()
M = np.ones((y1 - y0, x1 - x0)); M[:3] = 0; M[-3:] = 0; M[:, :3] = 0; M = gaussian_filter(M, 1.4); M /= M.max()
C[y0:y1, x0:x1] = C[y0:y1, x0:x1] * (1 - M[..., None]) + patch * M[..., None]
# 젖은 얼룩: 실 끝(왼쪽) 둘레만 · 작고 들쭉날쭉 · 옅게
L = Image.new('L', (W, H), 0); dl = ImageDraw.Draw(L)
for k in range(7):
    ex = 1138 + rng.normal(0, 4); ey = 501 + rng.normal(0, 3); rx = 4 + rng.random() * 5; ry = 3 + rng.random() * 3
    dl.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill=255)
Ln = gaussian_filter(np.asarray(L).astype(float), 1.6) / 255
nz = gaussian_filter(rng.random((H, W)), 1.5); Ln = np.clip(Ln * (0.6 + 0.6 * nz), 0, 1)
wet = np.array([132, 156, 166], float)
C = C * (1 - 0.42 * Ln[..., None]) + wet * 0.42 * Ln[..., None]
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img, 'RGBA')
# 널빤지의 금(세로 틈) + 그 틈에서 나와 왼쪽으로 살짝 위로 휘며 껍질 속으로 가늘어지는 물실
d.line([(1182, 500), (1181, 513)], fill=(34, 30, 28, 255), width=2)
pts = [(1181 - i, 507 - 0.16 * i - 2.2 * math.sin(i / 4.2) * (1 - i / 56)) for i in range(0, 46)]
for k in range(len(pts) - 1):
    w = 3 if k < 28 else 2
    d.line([pts[k], pts[k + 1]], fill=(44, 138, 162, 255), width=w)
d.line([(x, y - 1.2) for (x, y) in pts[:32]], fill=(196, 238, 244, 230), width=1)
# ── ③ 구리관 흐름 화살(다리 면에 새긴 짙은 구리색 화살촉) — 왼 다리(x≈1744) ↓ · 오른 다리(x≈1774) ↑
DARK = (96, 54, 30, 255); HL = (236, 190, 150, 255)
def chevron(cx, cy, up, s=7):
    if up: p = [(cx - s, cy + s * 0.55), (cx, cy - s * 0.55), (cx + s, cy + s * 0.55)]
    else:  p = [(cx - s, cy - s * 0.55), (cx, cy + s * 0.55), (cx + s, cy - s * 0.55)]
    d.line(p, fill=DARK, width=3, joint='curve'); d.line([(x, y - 1) for (x, y) in p], fill=HL, width=1)
for y in (440, 470, 600, 630):
    chevron(1744, y, up=False)
for y in (440, 470, 600, 630):
    chevron(1774, y, up=True)
img.save('cur8.png')
img.crop((370, 10, 450, 120)).resize((480, 660), Image.LANCZOS).save('v9_sword.png')
img.crop((1100, 440, 1220, 540)).resize((600, 500), Image.LANCZOS).save('v9_thread.png')
img.crop((1700, 220, 1840, 760)).resize((280, 1080), Image.LANCZOS).save('v9_pipe.png'); print('cur8 saved')

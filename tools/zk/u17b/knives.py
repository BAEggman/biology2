# knives.py — cur2 → cur3: 문 앞 칼 둘을 지우고(인페인트) 날이 문 반대쪽(아래 왼쪽 · 방 안)을 향한 칼 둘로 다시 그린다 — 「칼 둘이 문으로 들어온다」
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
A = np.asarray(Image.open('cur2.png').convert('RGB')).astype(float); H, W, _ = A.shape
x0, y0, x1, y1 = 1858, 158, 1936, 224
S = A[y0:y1, x0:x1]
lum = S.mean(axis=2); sat = (S.max(axis=2) - S.min(axis=2)) / (S.max(axis=2) + 1e-6)
steel = (lum > 170) & (sat < 0.07)
handle = (S[..., 0] - S[..., 2] > 30) & (lum < 140)
dark = lum < 75
m = steel | handle | dark
n, lab, stats, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
keep = np.zeros_like(m)
for i in sorted(range(1, n), key=lambda i: -stats[i, cv2.CC_STAT_AREA])[:4]:
    if stats[i, cv2.CC_STAT_AREA] > 40: keep |= (lab == i)
mm = np.zeros((H, W), np.uint8); mm[y0:y1, x0:x1] = binary_dilation(keep, iterations=2)
print('erase px', int(mm.sum()))
C8 = cv2.inpaint(np.clip(A, 0, 255).astype('uint8'), mm, 5, cv2.INPAINT_TELEA)
img = Image.fromarray(C8); d = ImageDraw.Draw(img)
OUT = (34, 30, 28); STEEL = (222, 226, 230); EDGE = (250, 252, 252); WOOD = (118, 78, 44); WOOD_L = (160, 112, 70)
def knife(hx, hy, tx, ty, bw=7):
    L = math.hypot(tx - hx, ty - hy); ux, uy = (tx - hx) / L, (ty - hy) / L; nx, ny = -uy, ux
    hl = L * 0.36; gx, gy = hx + ux * hl, hy + uy * hl            # 손잡이 끝 → 날 시작
    # 손잡이
    hw = bw * 0.75
    hp = [(hx + nx * hw / 2, hy + ny * hw / 2), (gx + nx * hw / 2, gy + ny * hw / 2), (gx - nx * hw / 2, gy - ny * hw / 2), (hx - nx * hw / 2, hy - ny * hw / 2)]
    d.polygon(hp, fill=WOOD, outline=OUT); d.line([hp[0], hp[1]], fill=WOOD_L, width=1)
    for t in (0.3, 0.7):
        rx, ry = hx + ux * hl * t, hy + uy * hl * t; d.ellipse([rx - 1.2, ry - 1.2, rx + 1.2, ry + 1.2], fill=(210, 200, 180))
    # 날: 등은 곧고 날은 끝으로 휘어 모인다
    bp = [(gx + nx * bw / 2, gy + ny * bw / 2), (tx, ty), (gx - nx * bw * 0.35, gy - ny * bw * 0.35)]
    bp = [(gx + nx * bw / 2, gy + ny * bw / 2), (gx + ux * (L - hl) * 0.75 + nx * bw * 0.45, gy + uy * (L - hl) * 0.75 + ny * bw * 0.45), (tx, ty),
          (gx + ux * (L - hl) * 0.6 - nx * bw * 0.45, gy + uy * (L - hl) * 0.6 - ny * bw * 0.45), (gx - nx * bw / 2, gy - ny * bw / 2)]
    d.polygon(bp, fill=STEEL, outline=OUT)
    d.line([bp[0], bp[1], bp[2]], fill=EDGE, width=1)
    d.line([(gx + nx * (bw / 2 + 0.5), gy + ny * (bw / 2 + 0.5)), (gx - nx * (bw / 2 + 0.5), gy - ny * (bw / 2 + 0.5))], fill=OUT, width=2)
# 칼 1: 손잡이(문 쪽 위 오른쪽) → 날 끝(아래 왼쪽)
knife(1922, 166, 1864, 196)
knife(1930, 186, 1872, 214)
img.save('cur3.png'); img.crop((1820, 20, 2048, 340)).resize((456, 640), Image.LANCZOS).save('v_door3.png'); print('cur3 saved')

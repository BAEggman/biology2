# u01v7b.py — cur3(v5 + Gemini 창) → cur4: ① 호스 이음선 계단(y≈593)은 호스 화소에만 램프 ② U 안쪽 삼베 그물의 곧은 아래 끊김(y≈591 · x 262~336)을 물결 테두리로
import math, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
A = np.asarray(Image.open('cur3.png').convert('RGB')).astype(float); C = A.copy(); H, W, _ = A.shape
R, G, B = A[..., 0], A[..., 1], A[..., 2]; lum = A.mean(axis=2)
hose = (B - R > 6) & (lum > 80) & (lum < 225)
xa, xb = 186, 400
step = A[595:599, xa:xb].mean(axis=0) - A[588:592, xa:xb].mean(axis=0)
step = np.stack([gaussian_filter(step[:, c], 6) for c in range(3)], axis=1)
for k, y in enumerate(range(571, 594)):
    t = (k + 1) / 23; hm = hose[y, xa:xb].astype(float)
    C[y, xa:xb] += step * t * hm[:, None]
# ② 그물 끊김: x 262~336 · 물결 선 아래는 바닥(12행 아래 화소), 위는 그물(그대로)
rng = np.random.default_rng(5)
edge = {x: 591 + 3.5 * math.sin(x / 6.5) + 1.8 * math.sin(x / 2.7 + 1) for x in range(262, 337)}
for x in range(262, 337):
    ye = edge[x]
    for y in range(584, 600):
        if hose[y, x]: continue
        if ye < y <= 593:                       # 물결이 끊김보다 위 → 바닥(끊김 바로 아래 맨 면 3행을 위로 깐다)
            C[y, x] = A[594 + int(y - ye) % 3, x]
        elif 593 < y <= ye:                     # 물결이 끊김보다 아래 → 그물(6행 위에서)
            C[y, x] = A[y - 6, x]
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img)
pts = [(x, edge[x]) for x in range(262, 337) if not hose[int(edge[x]), x]]
segs = []; cur = []
for (x, y) in pts:
    if cur and x - cur[-1][0] > 1: segs.append(cur); cur = []
    cur.append((x, y))
if cur: segs.append(cur)
for s_ in segs:
    if len(s_) > 2: d.line(s_, fill=(40, 34, 28), width=2)
img.save('cur4.png')
from PIL import ImageEnhance
ImageEnhance.Contrast(img.crop((200, 560, 420, 630))).enhance(2.0).resize((880, 280), Image.NEAREST).save('v_useam7.png'); print('cur4 saved')

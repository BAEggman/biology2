# vfix.py — cur1 → cur2 (v5 PIL 손질 ①): 수갱의 큰 V 를 불투명 대칭 V 로 바깥면에 다시(유령 오른팔 지움) · 아래 요소 문 곁 V 를 같은 크기로 ·
#   창 1 의 격자 물방울 지우고 창 4 의 유리 쪽마다 한 줄(네 줄, 구리관 쪽으로) · 체→자루 소금 줄기 + 체 밑 물방울 · 칼끝 물결
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation

src = Image.open('cur1u.png').convert('RGB')
A = np.asarray(src).astype(float)          # 원본(읽기 전용)
C = A.copy()                               # 작업본
H, W, _ = C.shape

def feather_paste(C, patch, x0, y0, f=3, sides='tblr'):
    h, w = patch.shape[:2]
    M = np.ones((h, w))
    if 't' in sides: M[:f, :] = 0
    if 'b' in sides: M[-f:, :] = 0
    if 'l' in sides: M[:, :f] = 0
    if 'r' in sides: M[:, -f:] = 0
    M = gaussian_filter(M, f / 1.5); M = np.clip(M / M.max(), 0, 1)
    reg = C[y0:y0 + h, x0:x0 + w]; C[y0:y0 + h, x0:x0 + w] = reg * (1 - M[..., None]) + patch * M[..., None]

# ── A. 큰 V 지우기 ──
# A1 물속 유령 팔(x 1205~1241 · y 398~577): 오른쪽 깨끗한 열(x 1243~1250)의 세로 램프 + 깨끗한 행(y 330~390 · 578~600)에서 잰 왼 가장자리 하이라이트 가로 프로필
x0, x1, ya, yb = 1205, 1241, 398, 577
ref = A[:, 1243:1250].mean(axis=1)                                   # (H,3) 행마다 기준 물빛
rows = list(range(330, 390)) + list(range(578, 600))
hl = np.mean([A[y, x0:x1] - ref[y] for y in rows], axis=0)            # (w,3) 가로 프로필
patch = np.array([ref[y] + hl for y in range(ya, yb)])
feather_paste(C, patch, x0, ya, f=5, sides='tbr')
# A2 테 기둥 위 흰 막대(x 1177~1204 · y 440~556): 위 깨끗한 행(y 300~416)을 그대로 내려 복제
feather_paste(C, A[296:420, 1170:1205].copy(), 1170, 436, f=4, sides='tbl')

# ── B. 작은 V 지우기(x 1162~1204 · y 648~712): 바로 위 문 없는 행(y 560~624) 복제 — 널빤지 결은 세로
mV = np.zeros((H, W), np.uint8); sub = A[644:714, 1166:1214]; mV[644:714, 1166:1214] = (sub.min(axis=2) > 200)
mV = binary_dilation(mV, iterations=2).astype(np.uint8)
C8 = np.clip(C, 0, 255).astype('uint8'); C8 = cv2.inpaint(C8, mV, 4, cv2.INPAINT_TELEA); C = C8.astype(float)

img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img)
FILL, OUT = (246, 246, 242), (70, 62, 55)
def bar(p0, p1, w, fill, outline):
    (x0, y0), (x1, y1) = p0, p1; dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
    d.polygon([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], fill=fill, outline=outline)
def V(cx, top, bot, half, w):
    a = math.atan2(half, bot - top); k = (w / 2) / math.sin(a)
    pts = [(cx - half - w / 2, top), (cx - half + w / 2, top), (cx, bot - k), (cx + half - w / 2, top), (cx + half + w / 2, top),
           (cx + 5, bot + 5), (cx - 5, bot + 5)]
    d.polygon(pts, fill=FILL, outline=OUT); d.line(pts + [pts[0]], fill=OUT, width=2, joint='curve')
# ── C. 새 큰 V (수갱 바깥면 · 물실 바로 위) · 아래 V (문 곁)
V(1174, 362, 468, 34, 17)
V(1194, 583, 689, 34, 17)

# ── D. 창 1 격자 지우기 ──
C = np.asarray(img).astype(float)
C[387:433, 1417:1457] = A[387:433, 1462:1502]                 # 창 2 를 창 1 자리에
# 벽의 빗금 점(초록빛)을 인페인트
R, G, B = A[..., 0], A[..., 1], A[..., 2]
m = (G - R >= 4) & (B - R >= -6) & (A.mean(axis=2) < 175)
mask = np.zeros((H, W), np.uint8); mask[394:450, 1402:1462] = m[394:450, 1402:1462]
mask[387:433, 1417:1457] = 0
mask = binary_dilation(mask, iterations=2).astype(np.uint8)
C8 = np.clip(C, 0, 255).astype('uint8'); C8 = cv2.inpaint(C8, mask, 3, cv2.INPAINT_TELEA); C = C8.astype(float)

img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img)
# ── E. 창 4(x 1550~1586 · y 390~429)의 유리 쪽마다 물방울 한 줄 — 네 줄이 오른쪽(구리관 x 1738)으로 빠진다
DROP, DOUT = (90, 160, 175), (40, 105, 120)
def drop(x, y, r=1.7):
    d.ellipse([x - r, y - r, x + r, y + r], fill=DROP, outline=DOUT)
    d.polygon([(x - r * 0.7, y - r * 0.5), (x, y - r * 2.1), (x + r * 0.7, y - r * 0.5)], fill=DROP)
for (xs, y) in [(1557, 396), (1573, 404), (1557, 414), (1573, 422)]:
    x = xs
    while x <= 1728:
        drop(x, y); x += 9
# ── F. 체→자루 소금 줄기 + 체 밑 물방울 + 칼끝 물결 ──
d.polygon([(246, 33), (251, 33), (238, 50), (232, 50)], fill=(250, 250, 246), outline=(150, 150, 140))
for (x, y) in [(234, 46), (238, 44), (231, 49), (236, 48), (240, 47)]:
    d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(255, 255, 255), outline=(170, 170, 160))
for (x, y) in [(262, 50), (258, 58), (266, 62)]:
    drop(x, y, 1.6)
for (rx, ry) in [(12, 4), (20, 6)]:
    d.ellipse([415 - rx, 108 - ry, 415 + rx, 108 + ry], outline=(225, 240, 240), width=1)
img.save('cur2.png')
img.crop((1080, 300, 1320, 760)).resize((480, 920), Image.LANCZOS).save('v_cur2_shaft.png')
img.crop((1380, 370, 1760, 460)).resize((1140, 270), Image.LANCZOS).save('v_cur2_win.png')
img.crop((120, 0, 540, 200)).resize((1260, 600), Image.LANCZOS).save('v_cur2_quay.png')
print('cur2 saved')

# u01v8.py — final_v7 → v8 (b120 뒤): ① 창 안 털 위 흰 알갱이 여덟(둥근 진주로 읽힘)을 「모난 소금 결정」으로 — 같은 자리에 조금 큰 흰 정육면체
#   (밝은 윗면 + 그늘진 옆면 + 짙은 윤곽) 여덟 + 작은 결정 넷  ② 흐름 화살촉 — 굵은 범포 호스 윗몸에 ↓ 둘씩 두 쌍(들어오는 관) ·
#   가는 구리관 곧은 몸에 ↑ 둘씩 두 쌍(나가는 관) — s17u03 구리관 화살과 같은 꼴  ③ 호스 몸의 y≈594 가로 이음 자국을 세로로만 고르게
#   (이미 마감된 png 위 — finish 를 다시 돌리지 않는다)
import math, sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter1d, binary_dilation
src, out = sys.argv[1], sys.argv[2]
A = np.asarray(Image.open(src).convert('RGB')).astype(float); H, W, _ = A.shape
C = A.copy()
R, G, B = A[..., 0], A[..., 1], A[..., 2]
# ── ③ 이음 자국: 호스 화소(푸른 회색)만, 행 588~601 을 세로 가우스로
hose = (B - R > 10) & (B > 110)
y0, y1 = 586, 604
band = C[y0:y1].copy()
sm = np.stack([gaussian_filter1d(band[..., c], 1.6, axis=0) for c in range(3)], axis=2)
m = hose[y0:y1].copy(); m[:, :150] = False; m[:, 400:] = False
w = np.zeros(m.shape); w[2:-2] = 1.0; w = gaussian_filter1d(w, 1.0, axis=0) * m
C[y0:y1] = band * (1 - w[..., None]) + sm * w[..., None]
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img, 'RGBA')
# ── ① 소금 결정
OUT = (58, 60, 68, 255); TOP = (250, 250, 247, 255); SIDE = (196, 202, 210, 255); HL = (255, 255, 255, 255)
def crystal(cx, cy, s, ang):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    def P(u, v): return (cx + u * ca - v * sa, cy + u * sa + v * ca)
    h = s / 2
    sq = [P(-h, -h), P(h, -h), P(h, h), P(-h, h)]
    d.polygon(sq, fill=TOP, outline=OUT)
    # 그늘진 옆면(아래 · 오른쪽 반의 삼각) — 결정 면
    d.polygon([P(h, -h), P(h, h), P(-h, h), P(h * 0.15, h * 0.15)], fill=SIDE)
    d.line(sq + [sq[0]], fill=OUT, width=1)
    d.line([P(h * 0.15, h * 0.15), P(h, -h)], fill=(150, 156, 166, 255), width=1)
    d.point([P(-h * 0.45, -h * 0.45)], fill=HL)
# 옛 진주 자리(가운데) — 조금 크게 덮는다
pearls = [(420.6, 305.0), (424.4, 312.0), (442.1, 295.1), (454.9, 283.7), (467.2, 275.8), (477.0, 273.4), (408.9, 329.7), (405.6, 313.5)]
angs = [18, -24, 33, -12, 27, -35, 8, -20]
sizes = [7.5, 7, 8, 7.5, 7, 7.5, 7, 7]
for (x, y), a, s in zip(pearls, angs, sizes):
    crystal(x, y, s, a)
# 작은 결정 넷(털 끝에 흩어진 부스러기)
for (x, y, s, a) in [(433, 303, 4.5, 40), (448, 291, 4.5, -15), (461, 281, 4, 25), (414, 321, 4.5, -30)]:
    crystal(x, y, s, a)
# ── ② 흐름 화살(자루 달린 화살 — 맨 꺾쇠는 「V」로 읽힐 수 있어 피한다 · V 는 ADH 예약)
def arrow(cx, ytail, yhead, half, shaft, dark, hl):
    up = yhead < ytail; sgn = -1 if up else 1
    hl_len = half * 1.15
    yb = yhead - sgn * hl_len                     # 촉 밑변
    body = [(cx - shaft / 2, ytail), (cx + shaft / 2, ytail), (cx + shaft / 2, yb), (cx + half, yb), (cx, yhead), (cx - half, yb), (cx - shaft / 2, yb)]
    d.polygon(body, fill=dark)
    d.line([(cx - half + 1.5, yb - sgn * 1.2), (cx, yhead - sgn * 2.2)], fill=hl, width=1)
CU_D, CU_H = (74, 38, 20, 255), (240, 200, 164, 255)
for (yt, yh) in [(128, 92), (232, 196)]:
    arrow(573, yt, yh, 7.5, 3.2, CU_D, CU_H)
HO_D, HO_H = (40, 54, 72, 255), (206, 220, 232, 255)
for (yt, yh) in [(52, 112), (150, 210)]:
    arrow(195, yt, yh, 14, 6, HO_D, HO_H)
img.save(out)
img.crop((370, 250, 510, 345)).resize((840, 570), Image.LANCZOS).save(out.replace('.png', '_win.png'))
img.crop((110, 20, 620, 300)).save(out.replace('.png', '_arrows.png'))
img.crop((150, 560, 420, 630)).resize((1080, 280), Image.LANCZOS).save(out.replace('.png', '_seam.png'))
print('saved', out)

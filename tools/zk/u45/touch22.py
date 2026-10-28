#!/usr/bin/env python3
"""touch22.py — s45u01 v4(b128 뒤): cur22c → cur22
 Gemini G2(C₄ 바깥 방 — 땀 흘리는 사람이 빨간 말굽 자석을 들었고 막대가 자석 끝에 매달림 · 흰 방울 둘 튕김)
 · G3(CAM 밤 — 무릎 꿇은 사람이 같은 자석을 막대 끝 방울에 댐) · G4(장인이 방패를 기울여 금화 토막 끝을 누름)
 는 zpaste 로 이미 붙였다(cur22a → b → c). 여기서는 PIL 만:
 ① C₄ 자석에 매달린 막대를 마디 넷(아래 셋 크림 · 밤색 · 크림 + 맨 위 방울빛)으로 다시 — 자석 왼 극 끝을 막대 위로 되살림
 ② 첫 방 벽의 동전 틈 → 쇠 동전 판(가로 틈) + 그 틈에 반쯤 빠져 드는 금화(탁자 금화 꼴)
 ③ 짐꾼 등 뒤 속도선 셋(왼쪽으로 걷는다)"""
import sys, os, math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
sys.path.insert(0, '/tmp/b2/tools/zk/u45'); import rods
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
B = np.asarray(Image.open('cur22c.png').convert('RGB')).astype(np.uint8); H, W, _ = B.shape
SS = 4
S = lambda x, y: (x * SS, y * SS)
def overlay(img, fn):
    lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); fn(ImageDraw.Draw(lay))
    im2 = img.convert('RGBA'); im2.alpha_composite(lay.resize((W, H), Image.LANCZOS)); return im2.convert('RGB')

# ── ① C₄ 자석 막대
# 자석 왼 극(은빛 끝 + 윤곽) 화소를 먼저 떠 둔다
x0, y0, x1, y1 = 1568, 698, 1594, 720
sub = B[y0:y1, x0:x1].astype(int)
L = sub.mean(axis=2); sat = sub.max(axis=2) - sub.min(axis=2)
silver = (L > 150) & (sat < 40)
red = (sub[..., 0] - sub[..., 1] > 70) & (sub[..., 0] > 140)
tip = silver | red
tip = binary_dilation(tip, iterations=1) & ((L < 95) | tip)      # 짙은 윤곽 한 겹
TIP = np.zeros((H, W), bool); TIP[y0:y1, x0:x1] = tip
img = Image.fromarray(B)
img = rods.draw_rod(img, (1577, 767), (1577, 711), 4, 10, first='cream', dark_last=True)
C = np.asarray(img).copy(); C[TIP] = B[TIP]; img = Image.fromarray(C)

# ── ② 동전 판
A = np.asarray(img).copy()
m = np.zeros((H, W), np.uint8); m[370:417, 873:893] = 1; m[346:381, 874:893] = 1      # 옛 틈 · 동전 · 떨어지는 선
A = cv2.inpaint(A, m, 5, cv2.INPAINT_TELEA)
img = Image.fromarray(A)
PX0, PY0, PX1, PY1 = 870.5, 369.5, 900.5, 413.5
SLOT = (876.5, 386.5, 894.5, 391.5)
CX, CY, CR = 885.5, 381.0, 9.2
def plate(d):
    d.rounded_rectangle([S(PX0, PY0), S(PX1, PY1)], radius=4 * SS, fill=(178, 180, 183, 255), outline=(48, 48, 52, 255), width=int(SS * 1.6))
    d.line([S(PX0 + 2.5, PY0 + 3.0), S(PX1 - 3.0, PY0 + 3.0)], fill=(222, 224, 226, 255), width=int(SS * 1.2))      # 윗 모서리 빛
    d.line([S(PX0 + 2.5, PY0 + 3.5), S(PX0 + 2.5, PY1 - 3.5)], fill=(214, 216, 218, 255), width=int(SS * 1.0))
    for (sx, sy) in [(875.0, 374.5), (896.0, 374.5), (875.0, 408.5), (896.0, 408.5)]:
        d.ellipse([S(sx - 1.6, sy - 1.6), S(sx + 1.6, sy + 1.6)], fill=(96, 96, 100, 255), outline=(48, 48, 52, 255))
    d.rounded_rectangle([S(SLOT[0], SLOT[1]), S(SLOT[2], SLOT[3])], radius=1.5 * SS, fill=(20, 20, 22, 255))
img = overlay(img, plate)
def coin_layer(d, cx, cy, r):
    rx, ry = r * 0.62, r
    T = np.linspace(0, 2 * math.pi, 72)
    edge = [S(cx + rx * math.cos(t) - r * 0.28, cy + ry * math.sin(t)) for t in T]
    face = [S(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in T]
    d.polygon(edge, fill=(176, 122, 26, 255)); d.line(edge + [edge[0]], fill=(52, 34, 10, 255), width=int(SS * 1.3))
    d.polygon(face, fill=(236, 190, 58, 255)); d.line(face + [face[0]], fill=(52, 34, 10, 255), width=int(SS * 1.3))
    inner = [S(cx + rx * 0.72 * math.cos(t), cy + ry * 0.78 * math.sin(t)) for t in T]
    d.line(inner + [inner[0]], fill=(186, 136, 30, 255), width=int(SS * 1.1))
    mid = [S(cx + rx * 0.34 * math.cos(t) + r * 0.05, cy + ry * 0.42 * math.sin(t)) for t in T]
    d.polygon(mid, fill=(246, 210, 96, 255))
# 동전은 틈 위로 반만(틈 가운데 아래는 판이 가린다)
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); coin_layer(ImageDraw.Draw(lay), CX, CY, CR)
la = np.asarray(lay).copy(); la[int((SLOT[1] + 2.2) * SS):, :, 3] = 0
def falls(d):   # 동전 위 떨어지는 선 셋
    for (fx, fa, fb) in [(880.0, 357.0, 368.0), (885.5, 352.0, 366.0), (891.0, 357.0, 368.0)]:
        d.line([S(fx, fa), S(fx, fb)], fill=(70, 74, 64, 210), width=int(SS * 1.1))
img = overlay(img, falls)
lay = Image.fromarray(la).resize((W, H), Image.LANCZOS)
im2 = img.convert('RGBA'); im2.alpha_composite(lay); img = im2.convert('RGB')
def slot_lip(d):   # 틈의 아랫입술(동전이 그 속으로 들어간다)
    d.line([S(SLOT[0] + 0.8, SLOT[3] - 0.6), S(SLOT[2] - 0.8, SLOT[3] - 0.6)], fill=(20, 20, 22, 255), width=int(SS * 2.2))
    d.line([S(SLOT[0] + 0.5, SLOT[3] + 0.8), S(SLOT[2] - 0.5, SLOT[3] + 0.8)], fill=(120, 122, 126, 255), width=int(SS * 0.9))
img = overlay(img, slot_lip)

# ── ③ 짐꾼 등 뒤 속도선
def speed(d):
    for (xa, ya, xb, yb) in [(745, 626, 769, 624), (749, 645, 772, 644), (745, 664, 767, 664)]:
        d.line([S(xa, ya), S(xb, yb)], fill=(78, 70, 62, 230), width=int(SS * 1.5))
img = overlay(img, speed)

img.save('cur22.png')
for (b, n, k) in [((1520, 640, 1650, 790), 'v22_magnet.png', 5), ((850, 330, 920, 430), 'v22_slot.png', 8), ((600, 500, 800, 790), 'v22_porter.png', 3)]:
    img.crop(b).resize(((b[2] - b[0]) * k, (b[3] - b[1]) * k), Image.LANCZOS).save(n)
print('cur22 saved')

# vcross.py — cur0 → cur1: 하행지 곁 「못에 걸고 가위표 친 V」를 수도관 엘보에서 덱의 쇠 V 이음쇠(볼트 셋)로 —
#   엘보 자리를 벽으로 메우고(인페인트) → 쇠 V(못에 걸림) → 널빤지 두 장을 V 위로 다시 그린다(가위표가 V 를 덮는다)
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
A = np.asarray(Image.open('cur0.png').convert('RGB')).astype(float); H, W, _ = A.shape
def sat(X): mx = X.max(axis=2); mn = X.min(axis=2); return (mx - mn) / (mx + 1e-6)
# 1) 지울 영역: 두 널빤지 + 엘보 전체(벽 위에 다시 그린다) — 널빤지 다각형 + 엘보 상자
def board_poly(p0, p1, w, ext=0):
    (x0, y0), (x1, y1) = p0, p1; dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy * w / 2, ux * w / 2
    x0, y0, x1, y1 = x0 - ux * ext, y0 - uy * ext, x1 + ux * ext, y1 + uy * ext
    return [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
BA = ((203, 368), (313, 474)); BB = ((294, 373), (207, 472)); BW = 17
mimg = Image.new('L', (W, H), 0); dm = ImageDraw.Draw(mimg)
dm.polygon(board_poly(*BA, BW + 6, 3), fill=255); dm.polygon(board_poly(*BB, BW + 6, 3), fill=255)
dm.rectangle([226, 376, 300, 438], fill=255)
m = np.asarray(mimg) > 0
# 물줄기(푸른 빛)는 지우지 않는다
blue = (A[..., 2] - A[..., 0] > 6) & (A.mean(axis=2) > 150)
m &= ~binary_dilation(blue, iterations=1)
m = binary_dilation(m, iterations=1).astype(np.uint8)
C8 = cv2.inpaint(np.clip(A, 0, 255).astype('uint8'), m, 6, cv2.INPAINT_TELEA)
# 벽 줄눈 결을 살리려고 인페인트한 곳에 같은 행 왼쪽 벽(x-110) 결을 약하게 섞는다
C = C8.astype(float)
ys, xs = np.where(m > 0)
for y, x in zip(ys, xs):
    if x - 110 >= 0: C[y, x] = 0.55 * C[y, x] + 0.45 * A[y, x - 110]
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img)
# 2) 쇠 V (s17u03 과 같은 꼴) — 가위표 한가운데 위에
STEEL, STEEL_D, OUT = (232, 234, 230), (196, 200, 196), (62, 56, 50)
def Vfit(cx, top, bot, half, w, r):
    a = math.atan2(half, bot - top); k = (w / 2) / math.sin(a)
    pts = [(cx - half - w / 2, top), (cx - half + w / 2, top), (cx, bot - k), (cx + half - w / 2, top), (cx + half + w / 2, top), (cx + w * 0.3, bot + w * 0.3), (cx - w * 0.3, bot + w * 0.3)]
    d.polygon(pts, fill=STEEL, outline=OUT); d.line(pts + [pts[0]], fill=OUT, width=2)
    ins = [(cx - half - w / 2 + w * 0.22, top + w * 0.22), (cx - half + w / 2 - w * 0.22, top + w * 0.22), (cx, bot - k - w * 0.45), (cx + half - w / 2 + w * 0.22, top + w * 0.22), (cx + half + w / 2 - w * 0.22, top + w * 0.22), (cx + w * 0.12, bot + w * 0.05), (cx - w * 0.12, bot + w * 0.05)]
    d.line(ins + [ins[0]], fill=STEEL_D, width=1)
    for (bx, by) in [(cx - half, top + w * 0.55), (cx + half, top + w * 0.55), (cx, bot - k - w * 0.25 - r * 0.6)]:
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(96, 90, 84), outline=OUT); d.ellipse([bx - r * 0.45, by - r * 0.55, bx + r * 0.05, by - r * 0.05], fill=(210, 206, 200))
VCX, VTOP, VBOT, VH, VW = 255, 380, 440, 26, 13
Vfit(VCX, VTOP, VBOT, VH, VW, 3.0)
# 3) 널빤지 둘(B 먼저 · A 가 위) — 나무색 · 결 · 먹선 · 양 끝 못
WOOD, WOOD_D, WOUT = (214, 190, 140), (176, 150, 104), (44, 38, 32)
def board(p0, p1):
    poly = board_poly(p0, p1, BW)
    d.polygon(poly, fill=WOOD)
    (x0, y0), (x1, y1) = p0, p1; L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    for off in (-4.5, 0.5, 5):
        d.line([(x0 + nx * off + ux * 4, y0 + ny * off + uy * 4), (x1 + nx * off - ux * 4, y1 + ny * off - uy * 4)], fill=WOOD_D, width=1)
    d.line(poly + [poly[0]], fill=WOUT, width=2)
    for t in (0.1, 0.9):
        px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        d.ellipse([px - 2.2, py - 2.2, px + 2.2, py + 2.2], fill=(70, 62, 54))
board(*BB); board(*BA)
img.save('cur1.png'); img.crop((180, 330, 340, 490)).resize((640, 640), Image.LANCZOS).save('v_V1.png'); print('cur1 saved')

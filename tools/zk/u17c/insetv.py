# insetv.py — cur2 → cur3: 오른 틀선 칸(0.6 배 수갱 무리)의 옛 V 둘(흰 막대 + 반투명 팔 · 작은 V)을 지우고 큰 그림과 같은 꼴의 V 둘을 0.6 배로
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, gaussian_filter
A = np.asarray(Image.open('cur2.png').convert('RGB')).astype(float); C = A.copy(); H, W, _ = A.shape
def T(X, Y): return ((X - 810) * 0.6 + 496, (Y - 204) * 0.6 + 330)
# 1) 위 유령 V 자리(칸 좌표 x 716~756 · y 459~545: 테 기둥 + 옅은 물) → 바로 위 행(373~459) 세로 복제, 위아래 깃털
x0, x1, y0, y1 = 716, 757, 459, 546; h = y1 - y0
patch = A[y0 - h:y0, x0:x1].copy()
M = np.ones((h, x1 - x0)); M[:4, :] = 0; M[-4:, :] = 0; M = gaussian_filter(M, 2.0); M = np.clip(M / M.max(), 0, 1)
reg = C[y0:y1, x0:x1]; C[y0:y1, x0:x1] = reg * (1 - M[..., None]) + patch * M[..., None]
# 2) 옛 흰 자국 가면(두 상자) — 새 V 를 그린 뒤 V 밖에 남는 것만 인페인트
boxes = [(708, 455, 758, 548), (708, 590, 742, 642)]
old = np.zeros((H, W), bool)
for (a, b, c, d) in boxes:
    sub = C[b:d, a:c]; old[b:d, a:c] = (sub.min(axis=2) > 205)
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img)
vm = Image.new('L', (W, H), 0); dm = ImageDraw.Draw(vm)
FILL, OUT = (246, 246, 242), (70, 62, 55)
def V(cx, top, bot, half, w):
    a = math.atan2(half, bot - top); k = (w / 2) / math.sin(a)
    pts = [(cx - half - w / 2, top), (cx - half + w / 2, top), (cx, bot - k), (cx + half - w / 2, top), (cx + half + w / 2, top), (cx + 3, bot + 3), (cx - 3, bot + 3)]
    d.polygon(pts, fill=FILL, outline=OUT); d.line(pts + [pts[0]], fill=OUT, width=1); dm.polygon(pts, fill=255)
for (cx, top, bot) in [(1174, 362, 468), (1194, 583, 689)]:
    (a, b) = T(cx, top); (_, c) = T(cx, bot); V(a, b, c, 34 * 0.6, 17 * 0.6)
vmask = binary_dilation(np.asarray(vm) > 0, iterations=2)
rem = binary_dilation(old & ~vmask, iterations=1) & ~vmask
print('남은 흰 자국 px', int(rem.sum()))
C8 = cv2.inpaint(np.asarray(img), rem.astype(np.uint8), 3, cv2.INPAINT_TELEA)
Image.fromarray(C8).save('cur3.png')
Image.fromarray(C8).crop((480, 320, 800, 740)).resize((640, 840), Image.LANCZOS).save('v_cur3_inset.png'); print('cur3 saved')

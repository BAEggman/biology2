#!/usr/bin/env python3
"""move_walker.py — s31u01 v3 행 13 · 14: Gemini 가 「오른쪽으로 걷게」를 사람을 안뜰 쪽문 곁으로 옮겨 그렸다(안뜰 양동이 셋 셈이 깨진다).
→ 오른쪽을 보고 걷는 새 모습(fit_W 의 x 438~512 · y 8~128)만 떼어 옛 자리(문간 뒤 · 발 y≈183 · 가운데 x≈105)에 1.2 배로 옮기고,
   옛 자리 바탕은 Gemini 가 비운 것(fit_W), 새 자리는 원본(crop_W — 빈 벽)으로 · 뒤(왼쪽)로 옅은 발자국 셋.
사용: move_walker.py cur.png crop_W.json crop_W.png fit_W.png out.png"""
import sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation, binary_fill_holes, binary_opening
cur, cj, cw, fw, out = sys.argv[1:6]
B = np.asarray(Image.open(cur).convert('RGB')).astype(float)
c = json.load(open(cj)); S = c['scale']; bx0, by0, bx1, by1 = [v * S for v in c['box']]
C0 = np.asarray(Image.open(cw).convert('RGB')).astype(float)
F = np.asarray(Image.open(fw).convert('RGB').resize((bx1 - bx0, by1 - by0), Image.LANCZOS)).astype(float)
R = C0.copy()
# ① 옛 자리 → 비운 바탕(fit_W)
x0, y0, x1, y1 = 52, 40, 152, 196
R[y0:y1, x0:x1] = F[y0:y1, x0:x1]
# ② 새 모습 떼기: 새 자리에서 원본(빈 벽)과 달라진 화소
sx0, sy0, sx1, sy1 = 436, 6, 514, 130
# 모양 떼기는 GrabCut(사각형 안 사람 · 바탕은 벽 · 모래) — 달라진 화소(diff)는 Gemini 가 벽 빛을 조금 바꿔 바탕까지 잡혔다(후광)
import cv2
sub = np.ascontiguousarray(np.clip(F[sy0:sy1, sx0:sx1], 0, 255).astype('uint8')[..., ::-1])
gm = np.zeros(sub.shape[:2], np.uint8); bg = np.zeros((1, 65), np.float64); fg = np.zeros((1, 65), np.float64)
cv2.grabCut(sub, gm, (3, 3, sub.shape[1] - 6, sub.shape[0] - 5), bg, fg, 8, cv2.GC_INIT_WITH_RECT)
m = (gm == cv2.GC_FGD) | (gm == cv2.GC_PR_FGD)
m = binary_opening(m, iterations=1); m = binary_fill_holes(m)
spr = Image.fromarray(np.clip(F[sy0:sy1, sx0:sx1], 0, 255).astype('uint8'))
msk = Image.fromarray((gaussian_filter(m.astype(float), 0.8) * 255).astype('uint8'))
k = 1.2
W, H = int(round((sx1 - sx0) * k)), int(round((sy1 - sy0) * k))
spr = spr.resize((W, H), Image.LANCZOS); msk = msk.resize((W, H), Image.LANCZOS)
# 발 밑(스프라이트 안 y≈120 → 1.2 배 144) 을 옛 발 y 183 에, 가운데(475 → (475-436)*1.2=47) 를 x 105 에
px, py = int(round(105 - (475 - sx0) * k)), int(round(183 - (121 - sy0) * k))
Sa = np.asarray(spr).astype(float); Ma = np.asarray(msk).astype(float)[..., None] / 255
h, w = R.shape[:2]
ys, xs = max(0, py), max(0, px); ye, xe = min(h, py + H), min(w, px + W)
R[ys:ye, xs:xe] = R[ys:ye, xs:xe] * (1 - Ma[ys - py:ye - py, xs - px:xe - px]) + Sa[ys - py:ye - py, xs - px:xe - px] * Ma[ys - py:ye - py, xs - px:xe - px]
# ③ 발자국 셋(뒤 · 왼쪽 — 걷는 쪽과 반대) — 옅은 모래 그늘 타원
im = Image.fromarray(np.clip(R, 0, 255).astype('uint8')); S4 = 4
lay = Image.new('L', (w * S4, h * S4), 0); dr = ImageDraw.Draw(lay)
for (fx, fy) in [(58, 186), (40, 192), (22, 186)]:
    dr.ellipse([(fx - 5) * S4, (fy - 2) * S4, (fx + 5) * S4, (fy + 2) * S4], fill=255)
L = np.asarray(lay.resize((w, h), Image.LANCZOS)).astype(float)[..., None] / 255 * 0.35
A2 = np.asarray(im).astype(float); A2 = A2 * (1 - L) + np.array([150., 135., 110.]) * L
B[by0:by1, bx0:bx1] = A2
Image.fromarray(np.clip(B, 0, 255).astype('uint8')).save(out); print('ok', px, py, W, H)

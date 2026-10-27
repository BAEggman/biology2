#!/usr/bin/env python3
"""touch14.py — cur13 → cur14: ① 작업대 오른쪽 위 잘린 막대 토막(옛 E1 조각 · 2배 235~253 · 642~653) 지움
② 두 방 집 안쪽 방 들창 곁 흰 번짐(지운 흰 방울 자국) → 벽빛
③ 두 방 집 바깥 방(잎살 초록)에 흰 방울(O₂) 여섯 — s20u03 흰 방울 꼴(흰 속 · 옅은 회색 테 · 작은 반짝)"""
import sys, os, numpy as np, cv2
from PIL import Image, ImageDraw
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
A = np.asarray(Image.open('cur13.png').convert('RGB')).astype(np.uint8).copy(); H, W, _ = A.shape
# ① 토막: 크림·밤색 화소만 가면 → inpaint
sub = A[638:657, 230:258].astype(int); R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]; L = sub.mean(axis=2)
m = np.zeros((H, W), np.uint8)
m[638:657, 230:258] = (((L > 195) & (R - B > 15)) | ((L < 120))).astype(np.uint8)
m[638:657, 230:234] = 0
k = np.ones((3, 3), np.uint8); m = cv2.dilate(m, k, iterations=1)
A = cv2.inpaint(A, m, 4, cv2.INPAINT_TELEA)
# ② 흰 번짐: 벽빛 중앙값으로
wall = A[640:660, 1445:1462].reshape(-1, 3); wall = wall[wall.astype(int).mean(axis=1) > 180]
wc = np.median(wall, axis=0)
sub = A[604:626, 1470:1496].astype(int); L = sub.mean(axis=2)
mm = (L > 200) & (np.abs(sub[..., 0] - sub[..., 2]) < 40)
reg = A[604:626, 1470:1496].astype(float); reg[mm] = reg[mm] * 0.25 + wc * 0.75; A[604:626, 1470:1496] = reg.astype(np.uint8)
# ③ 흰 방울
img = Image.fromarray(A); SS = 4
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
def bub(x, y, r):
    d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=(252, 252, 250, 255), outline=(120, 124, 128, 255), width=int(SS * 1.3))
    d.ellipse([(x - r * 0.55) * SS, (y - r * 0.6) * SS, (x - r * 0.1) * SS, (y - r * 0.15) * SS], fill=(255, 255, 255, 255))
for (x, y, r) in [(1262, 468, 6.5), (1300, 528, 6), (1272, 612, 7), (1318, 676, 6), (1522, 452, 6.5), (1556, 500, 6)]:
    bub(x, y, r)
img = img.convert('RGBA'); img.alpha_composite(lay.resize((W, H), Image.LANCZOS)); img = img.convert('RGB')
img.save('cur14.png')
img.crop((1230, 400, 1640, 720)).save('v14_c4.png'); img.crop((200, 600, 330, 680)).resize((520, 320), Image.LANCZOS).save('v14_bench.png')
print('cur14 saved')

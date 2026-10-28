#!/usr/bin/env python3
"""touch_c.py — s45u02: cur8 → cur9 · 오른 자매 꼬리 옛 토막(쿠션 오른 모서리 위에 남은 말린 끝)을 지우고 쿠션 윤곽을 잇는다.
 쿠션 쪽 · 풀밭 쪽을 따로 메운다(한쪽 화소만 보고 inpaint) → 윤곽선을 원래 선 굵기 · 빛깔로 이어 긋는다."""
import sys, os, numpy as np, cv2
from PIL import Image, ImageDraw
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
A = np.asarray(Image.open('cur8.png').convert('RGB')).copy(); H, W, _ = A.shape
EDGE = [(1405, 606), (1414, 612), (1421, 618), (1430, 628), (1440, 641), (1450, 654), (1460, 669), (1468, 682), (1473, 690), (1480, 698), (1486, 705)]
chunk = np.zeros((H, W), np.uint8)
cv2.fillPoly(chunk, [np.array([[1434, 642], [1453, 642], [1468, 653], [1480, 668], [1481, 688], [1466, 690], [1452, 674], [1436, 664]], np.int32)], 1)
# 윤곽 바깥(풀밭) 쪽 반평면 — 윤곽 꺾은선의 오른쪽 위
grass_side = np.zeros((H, W), np.uint8)
cv2.fillPoly(grass_side, [np.array(EDGE + [(1520, 705), (1520, 590), (1405, 590)], np.int32)], 1)
cush_side = 1 - grass_side
box = np.zeros((H, W), np.uint8); box[630:700, 1425:1490] = 1
# 쿠션 쪽 메우기: 풀밭 쪽을 다 가리고 inpaint(쿠션 화소만 본다)
m1 = ((chunk | (grass_side & box)) > 0).astype(np.uint8)
F1 = cv2.inpaint(A, m1, 6, cv2.INPAINT_TELEA)
# 풀밭 쪽 메우기: 쿠션 쪽을 다 가리고 inpaint
m2 = ((chunk | (cush_side & box)) > 0).astype(np.uint8)
F2 = cv2.inpaint(A, m2, 6, cv2.INPAINT_TELEA)
out = A.copy()
sel1 = (chunk > 0) & (cush_side > 0); sel2 = (chunk > 0) & (grass_side > 0)
out[sel1] = F1[sel1]; out[sel2] = F2[sel2]
img = Image.fromarray(out)
SS = 4
lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
d.line([(x * SS, y * SS) for (x, y) in [(1433, 632)] + EDGE[4:9]], fill=(32, 32, 28, 255), width=int(SS * 2.3), joint='curve')   # 꼬리 뒤는 비움
im2 = img.convert('RGBA'); im2.alpha_composite(lay.resize((W, H), Image.LANCZOS)); img = im2.convert('RGB')
img.save('cur9.png')
img.crop((1400, 600, 1500, 710)).resize((400, 440), Image.LANCZOS).save('v9_rtail.png')
print('cur9 saved')

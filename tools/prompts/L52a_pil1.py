import cv2, numpy as np
im = cv2.imread('y1.png'); H, W = im.shape[:2]
# 1) 하늘로 솟은 노란 빛줄기 지움
mask = np.zeros((H, W), np.uint8)
reg = im[0:272, 556:630].astype(int)
m = (((reg[..., 0] - reg[..., 2]) < 40).astype(np.uint8) * 255)
m = cv2.dilate(m, np.ones((7, 7), np.uint8)); mask[0:272, 556:630] = m
im = cv2.inpaint(im, mask, 9, cv2.INPAINT_TELEA)
# 2) 다섯째 접시(갈색 덩이) 지움
med = np.array([161, 186, 201])
m2 = np.zeros((H, W), np.uint8)
cv2.ellipse(m2, (146, 1060), (80, 46), 0, 0, 360, 255, -1)
m2[:1023, :] = 0
# 3) 접시 윗테 남은 활(x 120~172 · y 1008~1034) — 탁자빛과 다른 곳만
reg = im[1008:1034, 120:172].astype(int)
d = np.abs(reg - med).sum(axis=2)
mm = (d > 40).astype(np.uint8) * 255
mm[:10, :18] = 0
m2[1008:1034, 120:172] = np.maximum(m2[1008:1034, 120:172], cv2.dilate(mm, np.ones((3, 3), np.uint8)))
fill = im.copy(); fill[m2 > 0] = med
a = cv2.GaussianBlur((m2 > 0).astype(np.float32), (0, 0), 1.2)[..., None]
im = (fill.astype(np.float32) * a + im.astype(np.float32) * (1 - a)).astype(np.uint8)
cv2.imwrite('work.png', im)

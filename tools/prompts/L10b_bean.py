#!/usr/bin/env python3
# L10b_bean.py <gem_Z6b.png> <out.png> — 구역 편집 Z6b 의 콩 모양 손님채를 세로로 눌러(0.72) 길고 낮은 콩 꼴로 만든다.
# Gemini 는 두 번 다 폭 : 높이 ≈ 1.4 로 그렸다 → 일치 검사에서 「사과 · 호박 · 입」으로 읽혔다(L52a 의 손님채는 1.5 ~ 1.6). 집만 눌러 2 : 1 쯤으로.
# 집 = 윗 테두리 곡선 아래쪽. 그 위의 오두막(초록 꼬투리)은 그대로 두고, 집에 가려 있던 오두막 밑동은 벽 무늬를 아래로 이어 그린다.
import sys, cv2, numpy as np
g = cv2.imread(sys.argv[1]); H, W = g.shape[:2]
bg = np.median(g[60:200, 60:400].reshape(-1, 3), axis=0).astype(np.uint8)
F, YB = 0.72, 956                                                    # 누르는 배율 · 바닥(그림자 아래)
# 바탕 = 그림 가장자리에서 바탕색으로 이어진 곳(허용 16). 그 밖 = 집 · 오두막 · 그림자 · 레일
diff = np.abs(g.astype(int) - bg.astype(int)).max(axis=2)
near = (diff <= 16).astype(np.uint8)
n, lab = cv2.connectedComponents(near, connectivity=4)
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
outside = np.isin(lab, list(edge)); fg = ~outside
# 집과 오두막을 가르는 선: 오두막 밑(x 600 ~ 900)은 손으로 딴 집의 윗 테두리 곡선, 그 밖은 y 240(왼쪽) · y 400(오른쪽)
CX = [600, 640, 680, 720, 760, 784, 786, 810, 840, 868, 900]; CY = [291, 291, 293, 299, 309, 319, 331, 334, 352, 380, 394]
cut = np.full(W, 240, int)
for x in range(600, W): cut[x] = int(np.interp(x, CX, CY)) if x <= 900 else 400
yy = np.mgrid[0:H, 0:W][0]
below = yy >= cut[None, :]
bld = fg & below
marg = np.where(np.arange(W) < 786, 3, 0)
bld = (cv2.dilate(bld.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0) & (yy >= cut[None, :] - marg[None, :])      # 테두리 둘레의 밝은 번짐까지(오두막 바닥 줄은 건드리지 않는다)
out = g.copy()
out[bld] = bg                                                         # 집을 들어낸다
# 가려 있던 오두막 밑동(x 672 ~ 800 · y 292 ~ 322)을 위 벽 무늬를 내려 이어 그린다 + 바닥 검은 줄
for x in range(668, 806):
    out[286:323, x] = g[284, x]
out[322:329, 672:806] = (18, 20, 24)
# 오두막 그림자(오른쪽 바닥)는 원래 그림에서 곡선 위쪽이라 그대로다
# 집을 세로로 눌러 붙인다
crop = g[240:YB].copy(); m = bld[240:YB].astype(np.uint8) * 255
nh = int(round((YB - 240) * F))
c2 = cv2.resize(crop, (W, nh), interpolation=cv2.INTER_AREA); m2 = cv2.resize(m, (W, nh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
y0 = YB - nh
reg = out[y0:YB].astype(np.float32)
out[y0:YB] = np.clip(reg * (1 - m2[..., None]) + c2.astype(np.float32) * m2[..., None] + 0.5, 0, 255).astype(np.uint8)
# 오두막 밑에 겹쳐 있던 자리(x 650 ~ 820): 눌린 집의 윗 테두리 위에 따라온 오두막 벽 조각 · 세로 줄 끝을 지운다
tops = []
for x in range(640, 901):
    col = out[440:600, x].max(axis=1) < 70; ys = np.where(col)[0]
    tops.append(440 + (int(ys[0]) if len(ys) else 0))
tops = np.array(tops); sm = np.array([int(np.median(tops[max(0, i - 7):i + 8])) for i in range(len(tops))])
for i, x in enumerate(range(640, 901)):
    if 650 <= x <= 890: out[440:sm[i], x] = bg
cv2.imwrite(sys.argv[2], out)
print('ok', sys.argv[2], 'bg', bg[::-1], '집 픽셀', int(bld.sum()))

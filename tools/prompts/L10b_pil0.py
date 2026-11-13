#!/usr/bin/env python3
# L10b_pil0.py <base.png> <gem_Z1.png> <out.png> — 구역 편집 Z1(돔 안 — 할아버지를 곧추 앉힘)을 손으로 맞춰 붙인다.
# Gemini 가 돔 안만 다시 잡아(1024x765 · 문틀과 객차는 잘림) 돌려줘 zone3.py 의 정합이 서지 않았다(정합 점 7개).
# 바지 · 종이의 자리로 잰 닮음 변환: 올린 조각 = 1.06 × 돌려받은 그림 + (−32, 25.5) → 바탕 = 0.5797 × 돌려받은 그림 + (542.5, 73.95).
# 붙이는 곳은 바탕의 돔 안쪽(보라 벽에 둘러싸인 곳)뿐 — 벽 · 문틀 · 객차 · 열쇠는 바탕 그대로. 신발에서 열쇠 고리로 가는 끈은 다시 긋는다.
import sys, cv2, numpy as np
base = cv2.imread(sys.argv[1]); g = cv2.imread(sys.argv[2])
H, W = base.shape[:2]
K, TX, TY = 0.5797, 542.5, 73.95
A = np.float32([[K, 0, TX], [0, K, TY]])
warp = cv2.warpAffine(g, A, (W, H), flags=cv2.INTER_AREA)
valid = cv2.warpAffine(np.full(g.shape[:2], 255, np.uint8), A, (W, H), flags=cv2.INTER_NEAREST) > 250
valid = cv2.erode(valid.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
def wall(im):
    b, gg, r = [im[..., i].astype(int) for i in range(3)]
    return (abs(r - 160) < 34) & (abs(gg - 95) < 34) & (abs(b - 204) < 38)
def ink(im): return im.max(axis=2) < 70
# 돔 안쪽 = 보라 벽(+ 검은 테)에 둘러싸인 곳
x0, y0, x1, y1 = 530, 30, 1160, 540
reg = base[y0:y1, x0:x1]
bar = (wall(reg) | ink(reg)).astype(np.uint8)
bar = cv2.dilate(bar, np.ones((3, 3), np.uint8))
free = (1 - bar).astype(np.uint8)
n, lab = cv2.connectedComponents(free, connectivity=4)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
# 벽에 둘러싸인 덩이 가운데 연보라 방(가장 큰 것)을 씨앗으로, 그 안의 사람 · 걸상 · 종이까지 메운다
sizes = [(int((lab == k).sum()), k) for k in range(1, n) if k not in border]
room = lab == max(sizes)[1]
room = cv2.morphologyEx(room.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
cnt, _ = cv2.findContours(room, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
inside = np.zeros_like(room); cv2.drawContours(inside, [max(cnt, key=cv2.contourArea)], -1, 1, -1)
inside = cv2.erode(inside, np.ones((7, 7), np.uint8)) > 0
full = np.zeros((H, W), bool); full[y0:y1, x0:x1] = inside
full &= valid
out = base.copy()
LILAC = np.array([239, 189, 222], np.uint8)                       # BGR
gw = wall(warp)
gw = cv2.dilate(gw.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
# 돌려받은 그림의 벽이 바탕의 방 안으로 들어온 곳(벽 꼴이 조금 달라서)은 연보라로 — 다만 걸상(보라)은 살린다: 걸상은 방 아래쪽
yy = np.mgrid[0:H, 0:W][0]
gwall_only = gw & (yy < 420)
out[full & ~gwall_only] = warp[full & ~gwall_only]
out[full & gwall_only] = LILAC
# 신발에서 열쇠 고리로 내려가는 끈(바탕의 끈은 옛 신발 자리에서 내려온다 → 방 아래쪽부터 다시 긋는다)
SX, SY = int(round(TX + K * 737)), int(round(TY + K * 668))       # 돌려받은 그림에서 끈이 신발을 떠나는 자리
RX, RY = 957, 548                                                   # 열쇠 고리 꼭대기
big = cv2.resize(out[430:560, 920:1000], None, fx=4, fy=4, interpolation=cv2.INTER_LANCZOS4)
def P(x, y): return (int(round((x - 920) * 4)), int(round((y - 430) * 4)))
cv2.line(big, P(SX, SY), P(RX, RY), (24, 20, 18), 22, cv2.LINE_AA); cv2.line(big, P(SX, SY), P(RX, RY), (96, 138, 190), 10, cv2.LINE_AA)
out[430:560, 920:1000] = cv2.resize(big, (80, 130), interpolation=cv2.INTER_AREA)
cv2.imwrite(sys.argv[3], out)
print('ok', int(full.sum()), 'px · 끈', (SX, SY), '→', (RX, RY))

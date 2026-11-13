#!/usr/bin/env python3
# L12g_pil0.py <v2 바탕 2048> <s1 바탕 2048> <out> — 구역 편집 앞의 손질(덤 지움 · 첫 바탕에서 옮겨 심기).
#  바탕은 둘째 생성(v2 · L12g_src/s2.webp)을 쓴다. 첫 생성(s1)이 더 나은 두 곳만 s1 에서 옮겨 심는다:
#   ① 헛간 오른쪽(나가는 관 · 입술 둘 · 손잡이 쥔 사람) — v2 는 입술이 바퀴 꼴 + 역기 드는 사람이 덤으로 생겼다.
#   ② 좌판(차양 · 궤짝 셋 · 장판 두루마리) — v2 는 동전 넷뿐 · 벽돌이 납작 · 장판이 초(양초) 꼴 둘.
#  지움: 좌판 오른쪽의 큰 초록 기둥(양초 꼴) · 작업대 왼쪽의 갈색 상자 + 불꽃 꼴 기름방울 · 진흙 속 납작한 초록 빗금 셋.
#  고름: 운하의 묽은 물 → 진흙 이음매(x≈429 의 세로 금)와 세로 줄무늬를 매끈한 번짐으로.
import sys
import numpy as np
from PIL import Image
v2 = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.int32)
s1 = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(np.int32)
out = v2.copy()
SKY = np.array([198, 230, 247])
def nonsky(a): return np.abs(a - SKY).sum(2) > 36
def greenish(a): return (a[..., 1] > a[..., 0] + 22) & (a[..., 1] > a[..., 2] + 22)

# ── ① 헛간 오른쪽을 s1 에서(두 바탕의 헛간 오른쪽 벽 x≈1798 · 돌 윗줄 y≈802 · 아랫줄 y≈1088 이 같다)
out[760:1088, 1801:2048] = s1[760:1088, 1801:2048]

# ── ② 좌판: v2 것을 지우고 s1 것을 옮겨 심는다
orig = v2
# (가) 지움 — y < 296 은 x 700 ~ 1272 전부(좌판 + 큰 초록 기둥 윗부분)
out[60:296, 700:1273] = SKY
# (나) 왼쪽 다리 밑동(x 700 ~ 1100 · y 296 ~ 331 위)
out[296:330, 700:1100] = SKY
# (다) 오른쪽 다리(검은 줄 x 1176 ~ 1190) — 소 머리 윗줄(y≈318) 위까지만
out[296:316, 1170:1196] = SKY
# (라) 큰 초록 기둥 밑동 — 뿔(앞) · 소 등선은 남긴다
for x in range(1204, 1270):
    if x < 1223: ytop = 302                                   # 뿔 끝 위쪽만
    else: ytop = int(340 - (x - 1222) * (40 / 78.0)) - 5       # 소 등선 바로 위까지
    if ytop > 296: out[296:ytop, x] = SKY
# (마) s1 좌판을 옮김(dx = +290 · dy = +6): 하늘 위의 것(y < 304)은 하늘 아닌 것 모두 · 풀 위(y 304 ~ 323)는 다리만
DX, DY = 290, 6
src = s1[70:126, 426:915]; m = np.abs(src - SKY).sum(2) > 14                  # 차양(왼쪽 끝이 더 나와 있다)
dst = out[70 + DY:126 + DY, 426 + DX:915 + DX]; dst[m] = src[m]
src = s1[126:292, 437:913]; m = np.abs(src - SKY).sum(2) > 14                 # 궤짝 · 상판 · 장판(s1 의 여행 가방 x<437 은 빼고)
dst = out[126 + DY:292 + DY, 437 + DX:913 + DX]; dst[m] = src[m]
for (xa, xb) in ((438, 484), (858, 904)):
    src = s1[292:324, xa:xb]; m = ((src[..., 0] > src[..., 1] + 8) & (src[..., 1] > src[..., 2] + 8)) | (src.sum(2) < 210)   # 다리(갈색 · 검은 테두리)만
    y0, y1 = 292 + DY, 324 + DY
    dst = out[y0:y1, xa + DX:xb + DX]
    if xa > 800:                                               # 오른쪽 다리는 소 머리 윗줄 위까지만
        keep = np.zeros_like(m); keep[:max(0, 316 - y0), :] = True; m = m & keep
    dst[m] = src[m]

# (바) 끝손질 — 오른쪽 다리를 소 머리 윗줄까지 잇고 · 오른쪽 뿔 끝에 남은 초록 기둥 자국을 지운다
for y in range(315, 319):
    row = out[y, 1148:1192]; srow = out[314, 1148:1192]
    m = (np.abs(row - SKY).sum(1) < 60) | (row.sum(1) < 120)
    keep = out[y, 1148:1192].sum(1) < 120
    if y >= 318: m = m & ~keep                                   # 머리 윗줄(검정)은 남긴다
    row[m] = srow[m]
out[296:305, 1204:1226] = SKY
out[304:306, 1211:1218] = np.array([24, 22, 20])               # 뿔 끝의 검은 테두리

# ── ③ 작업대 왼쪽의 갈색 상자 + 불꽃 꼴 기름방울을 지운다(소 등선 위쪽만 · 하늘은 x=1602 열에서)
xs = np.array([1502, 1511, 1520.5, 1528.5, 1534, 1542, 1548, 1554, 1559, 1564.5, 1569, 1575, 1600])
ys = np.array([301, 304, 307, 310, 313, 316, 319, 322, 325, 328, 331, 334, 345])
for x in range(1518, 1594):
    ylim = int(np.interp(x, xs, ys)) - 4
    for y in range(176, min(ylim, 324)):
        out[y, x] = SKY
for x in range(1519, 1531):                                    # 상자 왼쪽 테두리의 끝동
    out[296:int(np.interp(x, xs, ys)) - 2, x] = SKY
reg = out[296:326, 1516:1596]; tan = (reg[..., 0] > reg[..., 1] + 20) & (reg[..., 1] > reg[..., 2] + 20) & (reg[..., 0] > 150); reg[tan] = SKY   # 등선 바로 위에 남은 갈색 실오라기
out[176:206, 1590:1606] = SKY                                  # 불꽃 꼴 기름방울의 꼬리 끝
for x in range(1516, 1562):                                    # 등선 바로 위의 갈색 실오라기 — 등선(검정)의 윗가장자리를 아래에서 찾아 그 위를 하늘로
    y = int(np.interp(x, xs, ys)) + 7
    while y > 290 and out[y, x].sum() >= 200: y -= 1           # 흰 몸 → 검은 등선
    while y > 290 and out[y, x].sum() < 200: y -= 1            # 등선 → 그 위
    seg = out[y - 12:y + 1, x]; seg[np.abs(seg - SKY).sum(1) > 20] = SKY
out[300:318, 1184:1196] = SKY                                  # 오른쪽 다리 곁의 검은 토막(v2 다리 자국)

# ── ④ 운하: 묽은 물 → 진흙을 매끈한 번짐으로 · 납작한 초록 빗금 지움
Y0, Y1, X0, X1 = 848, 1070, 0, 1160
band = out[Y0:Y1, X0:X1]
# 열마다 바탕색(중앙값) — 물건(스펀지 물결 · 풀 다발 · 못의 돌)은 중앙값에서 멀다
med = np.median(band[62:172], axis=0)                           # (W, 3)
# 매끈한 목표색: 왼쪽 묽은 물(213,194,157)에서 x=700 의 진흙색까지 S 곡선 · 그 오른쪽은 중앙값을 넓게 평균
k = 61; pad = np.pad(med, ((k // 2, k // 2), (0, 0)), mode='edge')
smooth = np.stack([np.convolve(pad[:, c], np.ones(k) / k, mode='valid') for c in range(3)], 1)
PALE = np.array([213., 194., 157.]); tgt = smooth.copy()
xa, xb = 200, 700
for x in range(X0, xb):
    if x < xa: tgt[x] = PALE
    else:
        t = (x - xa) / (xb - xa); t = t * t * (3 - 2 * t)
        tgt[x] = PALE * (1 - t) + smooth[xb] * t
dist = np.abs(band - med[None, :, :]).sum(2)
isbg = dist < 30
# 납작한 초록 빗금(테두리 없는 연초록 줄) — 다발 · 깔개 풀(진한 테두리)과 달리 주변에 어두운 픽셀이 없다
g = (band[..., 1] - band[..., 0]) > -12                           # 진흙은 R 이 G 보다 35 쯤 크다 — 초록기가 조금만 돌아도 빗금
dark = band.sum(2) < 200
from PIL import ImageFilter
def dil(mask, r):
    im = Image.fromarray((mask * 255).astype('uint8')).filter(ImageFilter.MaxFilter(2 * r + 1)); return np.asarray(im) > 0
near_dark = dil(dark, 5)
hatch = np.zeros_like(g)
for (hx0, hx1, hy0, hy1) in ((620, 770, 925, 995), (860, 1010, 925, 995), (1040, 1148, 925, 992)):
    sub = np.zeros_like(g); sub[hy0 - Y0:hy1 - Y0, hx0 - X0:hx1 - X0] = True
    hatch |= g & sub & ~near_dark
hatch = dil(hatch, 2)
# 빗금 자리는 위쪽 바탕색으로(짙은 진흙 덩이 위에 걸친 것은 그 색으로)
for y, x in zip(*np.nonzero(hatch)):
    yy = y
    while yy > 0 and hatch[yy, x]: yy -= 1
    band[y, x] = band[max(0, yy - 2), x]
# 셋째 빗금은 짙은 진흙 덩이 위에 놓였다 — 덩이 색으로 덮는다(오른쪽 풀 깔개의 테두리 진 줄기는 남긴다)
sub = band[934 - Y0:986 - Y0, 1052 - X0:1150 - X0]
BLOB = np.median(band[925 - Y0:935 - Y0, 1080 - X0:1120 - X0].reshape(-1, 3), axis=0)
gm = (sub[..., 1] - sub[..., 0]) > -14
xx = np.arange(1052, 1150)[None, :]; yy2 = np.arange(934, 986)[:, None]
gm &= (xx < 1150 - (yy2 < 950) * 6)                             # 깔개 풀(x ≥ 1144 · 위쪽)은 건드리지 않는다
sub[dil(gm, 2)] = BLOB.astype(np.int32)
dist = np.abs(band - med[None, :, :]).sum(2); isbg = dist < 34
w = np.clip((985 - np.arange(X0, X1)) / 85.0, 0, 1)[None, :, None]          # 짙은 진흙 덩이 앞(x 900 ~ 985)에서 원래 색으로 풀린다
mix = (band * (1 - w) + np.broadcast_to(tgt[None, :, :], band.shape) * w)
band[isbg] = mix[isbg].astype(np.int32)
Image.fromarray(out.clip(0, 255).astype('uint8')).save(sys.argv[3])
print('ok pil0')

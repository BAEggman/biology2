#!/usr/bin/env python3
"""s31p04 — 개념 논리 m 1·2(산소가 없어 막히는 것은 전자전달 = 담 너머 물레방아 길):
판자로 막힌 것이 **네모 문틀 + 청회색 문짝**(31단원에서 네모 문 = 피루브산이 들어가는 문지기 문, s31p01·s31p02)이라
「피루브산이 못 들어간다」로 읽히던 것 → 제미나이 v1(같은 너비·높이의 **둥근 벽돌 아치 + 어두운 굴** · 문틀·문짝 없음 ·
엇갈린 판자 둘과 앞의 가득 찬 양동이 더미 그대로) — s31p02 에서 양동이를 내려놓던 담 밑 아치(담 너머 물레방아로 가는 길)와 같은 문법.
  ① 아치 자리만 옮김: σ2 밝기 차 > 12 인 화소 가운데 아치 구역(x 150..385 · y 180..470) 안의 가장 큰 덩어리 → 닫기 3 · 구멍 메움 · 넓힘 3 · σ1.5 섞음.
     (제미나이는 판 전체를 살짝 다시 그렸다 — 양동이 더미 국소 차 ~8 · 손수레 사람 > 14. 나머지는 모두 설치본 그대로.)
     판자·양동이 위치는 원본과 어긋남 0px(판자 끝 · 윗줄 양동이 테에서 확인) — 옮기지 않는다.
  ② 오른쪽 아래 옛 흐린 반짝이(≈(903,907), 크림 바탕 위 아주 옅은 흰 별 — 고역 통과로 보면 또렷): 바로 아래(0, +44)의 맨 크림 바탕을
     크림 화소에만(L > 205 · 검은 선·피라미드에서 2px 밖) 옮겨 덮음. (둘레 백분위로 낮추는 안은 별 속이 넓어 둥근 얼룩이 남았다.)
사용: python3 s31p04_arch_paste.py ORIG.png V1.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

op, vp, dst = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(op).convert('RGB')).astype(np.float64)
V = np.asarray(Image.open(vp).convert('RGB')).astype(np.float64)
assert O.shape == V.shape == (1024, 1024, 3), (O.shape, V.shape)
H, W = O.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]

# ① 아치
d = ndi.gaussian_filter(np.abs(O - V).mean(axis=2), 2.0)
zone = (xx >= 150) & (xx < 385) & (yy >= 180) & (yy < 470)
m = (d > 12) & zone
lab, n = ndi.label(m)
sz = ndi.sum(m, lab, range(1, n + 1))
m = lab == (1 + int(np.argmax(sz)))
m = ndi.binary_closing(m, iterations=3)
m = ndi.binary_fill_holes(m)
m = ndi.binary_dilation(m, iterations=3) & zone
w = ndi.gaussian_filter(m.astype(float), 1.5)
out = O * (1 - w[..., None]) + V * w[..., None]
ys, xs = np.nonzero(m)
print('arch px', int(m.sum()), 'bbox', (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))

# ② 흐린 반짝이 — 별 속이 넓고 평평해 둘레 백분위로는 덜 낮아진다(가운데 둥근 얼룩이 남음) →
#    바로 아래(0, +44)의 맨 크림 바탕을 옮겨 덮는다. 크림 화소만(L > 205 · 검은 선·피라미드에서 2px 밖) · σ1.2 섞음.
X0, X1, Y0, Y1 = 874, 934, 884, 934
DY = 44
L = out.mean(axis=2)
sub = np.zeros((H, W), bool)
sub[Y0:Y1, X0:X1] = True
cream_all = (L > 205) & ~ndi.binary_dilation(L < 190, iterations=2)
cream = sub & cream_all
# 상자 가장자리 6px 는 서서히(아래 끝이 줄로 남지 않게)
ramp = np.ones((Y1 - Y0, X1 - X0))
for i in range(6):
    t = (i + 1) / 7.0
    ramp[i, :] *= t; ramp[-1 - i, :] *= t; ramp[:, i] *= t; ramp[:, -1 - i] *= t
box = np.zeros((H, W)); box[Y0:Y1, X0:X1] = ramp
wc = ndi.gaussian_filter(cream.astype(float), 1.2) * cream * box
src = np.roll(out, -DY, axis=0)
# 톤 맞춤: 상자 둘레 크림(10px 고리)의 중앙값 − 옮겨 올 자리 크림의 중앙값
ringb = np.zeros((H, W), bool); ringb[Y0 - 10:Y1 + 10, X0 - 10:X1 + 10] = True; ringb[Y0:Y1, X0:X1] = False
ringb &= cream_all
srcb = np.zeros((H, W), bool); srcb[Y0 + DY:Y1 + DY, X0:X1] = True; srcb &= cream_all
off = out[ringb].mean(axis=0) - out[srcb].mean(axis=0)
src = src + off
out = out * (1 - wc[..., None]) + src * wc[..., None]
print('faint sparkle px', int(cream.sum()), 'source rows', Y0 + DY, Y1 + DY, 'tone offset', off.round(1))

Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
Image.fromarray((w * 255).astype(np.uint8)).save(dst.replace('.png', '_mask.png'))
print('saved', dst)

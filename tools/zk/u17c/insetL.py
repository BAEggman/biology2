# insetL.py — cur3 → cur4: 왼 틀선 칸(ADH 없음)의 요도 큰 그림처럼 「소금 아래 켜」로 — cur1u(V 그리기 전 · 문 있음)의 더미 구역을 0.6 배로 붙이되
#   문 상자 자리는 그 위 행(소금 덮개 · 널빤지)을 내려 메운다(왼 칸에는 문이 없다)
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
S = np.asarray(Image.open('cur1u.png').convert('RGB')).astype(float)
C = np.asarray(Image.open('cur3.png').convert('RGB')).astype(float); H, W, _ = C.shape
X0, Y0, X1, Y1 = 880, 556, 1176, 836
reg = Image.fromarray(np.clip(S[Y0:Y1, X0:X1], 0, 255).astype('uint8'))
w, h = round((X1 - X0) * 0.6), round((Y1 - Y0) * 0.6)
P = np.asarray(reg.resize((w, h), Image.LANCZOS)).astype(float)
def T(X, Y): return (round((X - 810) * 0.6 + 144), round((Y - 204) * 0.6 + 330))
px, py = T(X0, Y0); print('왼 칸 붙일 자리', px, py, px + w, py + h)
# 문 상자(1134~1177 · 612~669) → 패치 좌표
dx0, dy0 = round((1134 - X0) * 0.6), round((612 - Y0) * 0.6); dx1, dy1 = round((1177 - X0) * 0.6), round((669 - Y0) * 0.6)
dh = dy1 - dy0
P[dy0:dy1, dx0:dx1] = P[dy0 - dh:dy0, dx0:dx1]
# 누런 가루 점(문 왼쪽 1095~1134 · 620~662)도 같은 식으로 위 행을 내린다 — 왼 칸에는 가루가 없다
gx0, gy0, gx1, gy1 = round((1095 - X0) * 0.6), round((618 - Y0) * 0.6), dx0, round((664 - Y0) * 0.6)
gh = gy1 - gy0; P[gy0:gy1, gx0:gx1] = P[gy0 - gh:gy0, gx0:gx1]
f = 6
M = np.ones((h, w)); M[:f, :] = 0; M[-f:, :] = 0; M[:, :f] = 0; M[:, -f:] = 0
M = gaussian_filter(M, f / 1.5); M = np.clip(M / M.max(), 0, 1)
# 칸 테두리 안쪽만(칸 안 좌표 x 144~ · y 330~726)
r = C[py:py + h, px:px + w]; C[py:py + h, px:px + w] = r * (1 - M[..., None]) + P * M[..., None]
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save('cur4.png')
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).crop((130, 320, 460, 740)).resize((660, 840), Image.LANCZOS).save('v_cur4_insetL.png'); print('cur4 saved')

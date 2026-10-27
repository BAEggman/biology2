# grains3.py — s20u02 cur0 → cur1: 꼭대기 굽이의 알갱이 일곱을 지우고(Gemini 맨 초록 속으로 메움) 바깥 벽 안쪽 22px 매끈한 곡선을 따라
#   아래 알갱이 하나(y≈262)를 본으로 21px 간격 · 곡선 방향만큼 돌려 다시 붙인다(뾰족한 흰 끝이 늘 안쪽 아래를 향하게)
import numpy as np, cv2, math
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, gaussian_filter
from scipy.interpolate import splprep, splev
A = np.asarray(Image.open('cur0.png').convert('RGB')).astype(float); C = A.copy(); H, W, _ = A.shape
F = np.asarray(Image.open('fit_S1.png').convert('RGB')).astype(float); OX, OY = 1000, 60
outer = np.array([(1060, 99), (1096, 100), (1122, 110), (1140, 120), (1154, 130), (1166, 140), (1172, 150), (1180, 160), (1188, 170),
                  (1194, 180), (1198, 190), (1202, 200), (1206, 210), (1210, 220), (1212, 230), (1214, 240), (1218, 250), (1220, 260),
                  (1222, 270), (1224, 280), (1225, 290)], float)
tck, u = splprep([outer[:, 0], outer[:, 1]], s=60)
uu = np.linspace(0, 1, 2000); X, Y = splev(uu, tck); dX, dY = splev(uu, tck, der=1)
T = np.stack([dX, dY], 1); T /= np.linalg.norm(T, axis=1, keepdims=True)
N_in = np.stack([T[:, 1], -T[:, 0]], 1) * -1          # 진행 방향(왼 위 → 오른 아래)의 오른쪽 = 바깥 → 안쪽은 반대
# 확인: 안쪽 법선은 왼쪽 아래를 가리켜야 한다
mid = 1000; print('N_in mid', N_in[mid])
if N_in[mid][0] > 0: N_in = -N_in
S = np.r_[0, np.cumsum(np.hypot(np.diff(X), np.diff(Y)))]
# 1) 안쪽 영역을 Gemini 속으로(바깥 벽 12px 띠 · 바깥은 원본)
reg = (slice(90, 300), slice(1040, 1240)); yy, xx = np.mgrid[reg]
from scipy.spatial import cKDTree
tree = cKDTree(np.stack([X, Y], 1)); dist, idx = tree.query(np.stack([xx.ravel(), yy.ravel()], 1)); dist = dist.reshape(xx.shape); idx = idx.reshape(xx.shape)
vec = np.stack([xx - X[idx], yy - Y[idx]], -1); side = (vec * N_in[idx]).sum(-1)
R_ = (side > 0) & (dist >= 12) & (yy >= 118) & (yy <= 234) & (xx >= 1094)
Rm = np.zeros((H, W)); Rm[reg] = R_; Rm = gaussian_filter(Rm, 1.5)
FF = C.copy(); FF[OY:OY + F.shape[0], OX:OX + F.shape[1]] = F
C = C * (1 - Rm[..., None]) + FF * Rm[..., None]
# 2) 본 알갱이(y≈262)
R, G, B = A[..., 0], A[..., 1], A[..., 2]
yel = (R > 190) & (G > 140) & (B < 120)
n, lab, st, cen = cv2.connectedComponentsWithStats(yel[120:330, 1090:1240].astype(np.uint8))
gs = sorted([(i, cen[i][0] + 1090, cen[i][1] + 120) for i in range(1, n) if st[i][4] > 40], key=lambda g: g[2])
tmpl = min(gs, key=lambda g: abs(g[2] - 262)); anchor = min(gs, key=lambda g: abs(g[2] - 241))
i, tcx, tcy = tmpl; x, y, w, h, a = st[i]; x += 1090; y += 120; pad = 7
xa, ya, xb, yb = x - pad, y - pad, x + w + pad, y + h + pad
body = (lab[ya - 120:yb - 120, xa - 1090:xb - 1090] == i)
lumS = A[ya:yb, xa:xb].mean(axis=2)
mk = binary_dilation(body, iterations=2) | (binary_dilation(body, iterations=5) & (lumS > 222))
mk = binary_dilation(mk, iterations=1)
Sp = A[ya:yb, xa:xb]; spr = Image.fromarray(np.dstack([Sp, mk * 255.0]).clip(0, 255).astype('uint8'), 'RGBA')
kt = int(np.argmin(np.hypot(X - (tcx + 23), Y - tcy)))          # 본 알갱이 자리의 곡선 방향
ang_t = math.degrees(math.atan2(T[kt, 1], T[kt, 0]))
# 3) 새 자리: anchor 에서 곡선(22px 안쪽)을 따라 위로 21px 간격 일곱
OXc, OYc = X + N_in[:, 0] * 22, Y + N_in[:, 1] * 22
Sc = np.r_[0, np.cumsum(np.hypot(np.diff(OXc), np.diff(OYc)))]
ka = int(np.argmin(np.hypot(OXc - anchor[1], OYc - anchor[2])))
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8'))
for j in range(1, 8):
    s_t = Sc[ka] - 21 * j
    if s_t < 0: break
    k = int(np.searchsorted(Sc, s_t)); px, py = OXc[k], OYc[k]
    ang = math.degrees(math.atan2(T[k, 1], T[k, 0]))
    rot = spr.rotate(-(ang - ang_t), resample=Image.BICUBIC, expand=True)
    img.alpha_composite(rot.convert('RGBA'), (0, 0)) if False else None
    base = img.convert('RGBA'); base.alpha_composite(rot, (round(px - rot.width / 2), round(py - rot.height / 2))); img = base.convert('RGB')
img.save('cur1.png')
img.crop((960, 80, 1260, 340)).resize((900, 780), Image.LANCZOS).save('v1_top.png'); print('cur1 saved')

# quay.py — cur0 → cur1: 둑 위 네 무리를 두 패로 — 병사를 나그네 곁으로(왼 패) · 알+레몬을 베·분필 곁으로(오른 패) · 체 밑 방울은 물방울로
import numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation

C = np.asarray(Image.open('cur0.png').convert('RGB')).astype(float).copy()
A = C.copy()
def sat(X): mx = X.max(axis=2); mn = X.min(axis=2); return (mx - mn) / (mx + 1e-6)
def lum(X): return X.mean(axis=2)
def quay_bg(x0, y0, x1, y1):
    """둑 배경(빈 자리 x 600~1000 의 같은 행)을 복제해 지운다"""
    w = x1 - x0; src_x = 620
    C[y0:y1, x0:x1] = A[y0:y1, src_x:src_x + w]
def sprite(box, thr_s=0.12, thr_l=120, extra=None):
    x0, y0, x1, y1 = box; S = A[y0:y1, x0:x1]
    bg = A[y0:y1, 620:620 + (x1 - x0)]
    m = (np.abs(S - bg).mean(axis=2) > 22)
    m = binary_dilation(m, iterations=1)
    return S, m
def paste(S, m, px, py):
    M = np.clip(gaussian_filter(m.astype(float), 0.6) * 1.3, 0, 1); h, w = S.shape[:2]
    reg = C[py:py + h, px:px + w]; C[py:py + h, px:px + w] = reg * (1 - M[..., None]) + S * M[..., None]

# 1) 병사 (x 488~545, y 14~96) → 나그네 오른쪽 (x 372)
sS, sm = sprite((486, 12, 548, 98))
quay_bg(486, 12, 548, 98)
paste(sS, sm, 372, 12)
# 칼날이 운하 뒷벽 홈으로 들어가는 선(y 86~98)은 스프라이트에 포함됨
# 2) 알 + 레몬 둑 위 부분 (x 800~870, y 44~84) → 베 왼쪽 (x 980)
eS, em = sprite((796, 40, 874, 86))
quay_bg(796, 40, 874, 86)
paste(eS, em, 980, 40)
# 레몬(물에 뜬 것 x 770~860, y 86~130) → 오른쪽으로 같은 거리(+184) 옮김 — 물 배경은 같은 행의 x+184 자리에 원래 물이 있으니 그 자리에 스프라이트만 더함
lS = A[86:132, 770:862]; lbg = A[86:132, 954:1046]
lm = (lS[..., 0] > 150) & (lS[..., 1] > 130) & (lS[..., 2] < 110)   # 노랑
lm = binary_dilation(lm, iterations=2)
# 지우기: 물 배경을 같은 행 왼쪽(x 650~742)에서
C[86:132, 770:862] = A[86:132, 650:742]
paste(lS, lm, 954, 86)
# 3) 체 밑 방울: x 262~300, y 96~120 의 흰 점들을 청록 물방울로
reg = C[96:122, 258:302]; wm = (lum(reg) > 200) & (sat(reg) < 0.15)
C[96:122, 258:302][wm] = np.array([150, 200, 205], float)
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save('cur1.png')
Image.open('cur1.png').crop((0, 0, 1300, 230)).save('v_quay1.png')

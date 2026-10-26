# room_fix.py — out_M3.png(1024) → room_v2.png: 오른 벽의 문·펌프·V 를 뒷벽으로(창 3+4 와 같은 벽) · 수레 0.75 · 오른 벽은 맨 회벽
import numpy as np, cv2
from PIL import Image
from scipy.ndimage import binary_dilation, gaussian_filter

A = np.asarray(Image.open('out_M3.png').convert('RGB')).astype(float)
H, W, _ = A.shape
def sat(X):
    mx = X.max(axis=2); mn = X.min(axis=2); return (mx - mn) / (mx + 1e-6)
def lum(X): return X.mean(axis=2)

def cut(x0, y0, x1, y1, thr_s=0.13, thr_l=95):
    S = A[y0:y1, x0:x1].copy(); m = (sat(S) > thr_s) | (lum(S) < thr_l)
    m = binary_dilation(m, iterations=1); return S, m
def paste(C, S, m, px, py, scale=1.0):
    if scale != 1.0:
        w, h = round(S.shape[1] * scale), round(S.shape[0] * scale)
        S = np.asarray(Image.fromarray(S.astype('uint8')).resize((w, h), Image.LANCZOS)).astype(float)
        m = np.asarray(Image.fromarray((m * 255).astype('uint8')).resize((w, h), Image.LANCZOS)).astype(float) / 255
    else: m = m.astype(float)
    M = np.clip(gaussian_filter(m, 0.7) * 1.3, 0, 1); h, w = S.shape[:2]
    reg = C[py:py + h, px:px + w]; C[py:py + h, px:px + w] = reg * (1 - M[..., None]) + S * M[..., None]
    return (px, py, px + w, py + h)

C = A.copy()
# 1) 스프라이트 미리 잘라 두기 (원본 A 에서)
door_S, door_m = cut(800, 592, 898, 866)          # 반쯤 열린 문(오른 벽)
pump_S, pump_m = cut(898, 708, 1000, 842)         # 펌프
V_S, V_m = cut(795, 236, 920, 400, thr_s=0.0, thr_l=250)  # V: 흰색이라 색으로 못 자름 → 바탕(회벽)보다 밝거나 윤곽 어두운 것
Vr = A[236:400, 795:920]; bg = np.median(Vr[5:20, 5:20].reshape(-1, 3), axis=0)
V_m = (np.sqrt(((Vr - bg) ** 2).sum(axis=2)) > 22); V_m = binary_dilation(V_m, iterations=1)
cart_S, cart_m = cut(425, 640, 800, 888); cart_m[:, 350:] = False   # 모서리 선(x 783)과 문 가장자리 제외

# 2) 오른 벽: 세로로 고른 회벽이라 열마다 y 430~580 평균색으로 메우고, 바닥은 왼쪽 바닥을 거울로 복제
def yf_right(x): return int(826 + (x - 788) * (66 / 162))
clean = A[424:588, 788:953].copy(); ch = clean.shape[0]      # 오른 벽의 깨끗한 띠(V 아래 · 문 위)
for y in range(216, 424): C[y, 788:953] = clean[(y - 216) % ch]
for y in range(588, 906): C[y, 788:953] = clean[(y - 588) % ch]
for x in range(788, 953):
    yf = yf_right(x); xm = int(215 - (x - 788) * (143 / 164)); C[yf:906, x] = A[yf:906, xm]
cream = A[500, 990]; C[690:860, 953:1024] = cream
# 3) 수레 자리: 뒷벽(y 640~822)은 두 줄 사이 띠(y 415~505)를 세로로 깔고, 바닥(822~888)은 바퀴 밑 바닥(889~925)을 깔고 → 수레 0.75 로 다시
band = A[418:496, 425:788].copy(); bh = band.shape[0]
for y in range(640, 822): C[y, 425:788] = band[(y - 640) % bh]
fl = A[889:925, 425:788].copy(); fh = fl.shape[0]
for y in range(822, 889): C[y, 425:788] = fl[(y - 822) % fh]
cb = paste(C, cart_S, cart_m, 400, 888 - round(248 * 0.75), 0.75)
print('cart', cb)
# 4) 문 · 펌프 · V 를 뒷벽에
db = paste(C, door_S, door_m, 690, 826 - round(274 * 0.53), 0.53); print('door', db)
pb = paste(C, pump_S, pump_m, 742, 826 - 8 - round(134 * 0.42), 0.42); print('pump', pb)
vb = paste(C, V_S, V_m, 702, 420, 0.58); print('V', vb)
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save('room_v2.png')
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).resize((600, 600), Image.LANCZOS).save('v_room_v2.png')

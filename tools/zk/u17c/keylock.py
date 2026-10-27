# keylock.py — cur2 → cur3: Gemini(out_K1) 의 열쇠·열린 자물쇠를 원본 해상도에서 스프라이트로 떼어 1.35× · 1.5× 크게 붙인다(결은 Gemini 그대로)
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, binary_fill_holes, gaussian_filter, binary_opening
O = np.asarray(Image.open('out_K1.png').convert('RGB')).astype(float)
C = np.asarray(Image.open('cur2.png').convert('RGB')).astype(float); H, W, _ = C.shape
SX, SY = 120 / 1024, 92 / 765
def lum(X): return X.mean(axis=2)
def sat(X): mx = X.max(axis=2); mn = X.min(axis=2); return (mx - mn) / (mx + 1e-6)
def sprite(box, mask):
    x0, y0, x1, y1 = box; S = O[y0:y1, x0:x1]; m = mask(S)
    m = binary_opening(m, iterations=1); m = binary_fill_holes(m); m = binary_dilation(m, iterations=2)
    return S, m
def paste(S, m, cx, cy, scale):
    w, h = round(S.shape[1] * SX * scale), round(S.shape[0] * SY * scale)
    Si = np.asarray(Image.fromarray(S.astype('uint8')).resize((w, h), Image.LANCZOS)).astype(float)
    Mi = np.asarray(Image.fromarray((m * 255).astype('uint8')).resize((w, h), Image.LANCZOS)).astype(float) / 255
    Mi = np.clip(gaussian_filter(Mi, 0.5) * 1.2, 0, 1)
    px, py = round(cx - w / 2), round(cy - h / 2)
    reg = C[py:py + h, px:px + w]; C[py:py + h, px:px + w] = reg * (1 - Mi[..., None]) + Si * Mi[..., None]
    return (px, py, px + w, py + h)
# 열쇠(out x 405~530 · y 225~420): 어두운 쇠 + 무채색 하이라이트
kS, km = sprite((405, 225, 530, 420), lambda S: (lum(S) < 125) | ((sat(S) < 0.10) & (lum(S) < 190)))
kb = paste(kS, km, 311, 39, 1.35); print('key', kb)
# 자물쇠(out x 140~430 · y 560~722): 바탕(둑 돌)과의 색 거리
def lockmask(S):
    bg = np.median(np.concatenate([S[:8].reshape(-1, 3), S[-8:].reshape(-1, 3)]), axis=0)
    m = (np.sqrt(((S - bg) ** 2).sum(axis=2)) > 42) | (lum(S) < 105)
    m = binary_dilation(m, iterations=3); m = binary_fill_holes(m)
    return m
lS, lm = sprite((140, 562, 430, 714), lockmask)
# 장화(cur2 x 294~324 · y 64~90 의 어두운 화소)를 기억해 두었다가 위에 다시 올린다
bx0, by0, bx1, by1 = 294, 64, 324, 90
boot = C[by0:by1, bx0:bx1].copy(); bm = (lum(boot) < 92)
bm = binary_dilation(bm, iterations=1)
lb = paste(lS, lm, 289, 76, 1.3); print('lock', lb)
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save('cur3.png')
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).crop((260, 10, 380, 100)).resize((960, 720), Image.LANCZOS).save('v_key_lock3.png')
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).crop((140, 0, 460, 120)).resize((1280, 480), Image.LANCZOS).save('v_left_group3.png'); print('cur3 saved')

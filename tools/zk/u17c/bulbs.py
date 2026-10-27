# bulbs.py — cur6 → cur7: 구리관 위 유리 구 둘을 같은 지름(52)으로 — 왼 위 58→52 · 오른 위 48→52(바닥 굽이 구 60 은 그대로)
#   비는 자리: 다리 열은 아래 띠(y 440~452)를 세로 타일 · 벽 열은 같은 행의 좌우 바깥 화소를 가로 보간
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
A = np.asarray(Image.open('cur6.png').convert('RGB')).astype(float); C = A.copy(); H, W, _ = A.shape
LEGS = [(1734, 1754), (1760, 1788)]
def is_leg(x): return any(a <= x < b for a, b in LEGS)
def shrink(cx, cy, r_out, target_d, strip_y=440):
    r = r_out + 3
    x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
    S = A[y0:y1, x0:x1].copy()
    yy, xx = np.mgrid[y0:y1, x0:x1]; m = ((xx - cx) ** 2 + (yy - cy) ** 2) <= (r_out + 1.5) ** 2
    mo = ((xx - cx) ** 2 + (yy - cy) ** 2) <= (r_out + 3) ** 2
    strip = A[strip_y:strip_y + 12]
    for i, y in enumerate(range(y0, y1)):
        sel = np.where(mo[i])[0]
        if len(sel) == 0: continue
        xa, xb = x0 + sel.min() - 1, x0 + sel.max() + 1
        la, lb = A[y, xa - 3:xa].mean(axis=0), A[y, xb + 1:xb + 4].mean(axis=0)
        for j in sel:
            x = x0 + j
            if is_leg(x): C[y, x] = strip[i % 12, x] + (A[y, 1700:1708].mean(axis=0) - A[strip_y + i % 12, 1700:1708].mean(axis=0))
            else:
                t = (x - xa) / max(1, xb - xa); C[y, x] = la * (1 - t) + lb * t
    sc = target_d / (2 * r_out); w = h = round(2 * r * sc)
    Si = np.asarray(Image.fromarray(S.astype('uint8')).resize((w, h), Image.LANCZOS)).astype(float)
    Mi = np.asarray(Image.fromarray((m * 255).astype('uint8')).resize((w, h), Image.LANCZOS)).astype(float) / 255
    Mi = gaussian_filter(Mi, 0.6)
    px, py = round(cx - w / 2), round(cy - h / 2)
    reg = C[py:py + h, px:px + w]; C[py:py + h, px:px + w] = reg * (1 - Mi[..., None]) + Si * Mi[..., None]
    print('bulb', (cx, cy), 'r', r_out, '->', target_d / 2)
shrink(1743, 344, 29, 52)
shrink(1776, 271, 24, 52)
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save('cur7.png')
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).crop((1700, 220, 1840, 420)).resize((420, 600), Image.LANCZOS).save('v_pipe7b.png'); print('cur7 saved')

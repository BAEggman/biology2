# patchfix.py — cur → out: 방 안 수레·펌프 둘레의 네모 패치(붙인 배경의 색조 단)를 바깥 벽·바닥과 행마다 맞춘다(수레·펌프 화소는 그대로)
import sys, numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, gaussian_filter
src, dst = sys.argv[1], sys.argv[2]
A = np.asarray(Image.open(src).convert('RGB')).astype(float); C = A.copy()
def fix(x0, x1, y0, y1, objmask, margin=12):
    # objmask: (H,W) bool of object pixels to keep
    for y in range(y0, y1):
        row = A[y]
        def mean_bg(xa, xb):
            sel = [x for x in range(xa, xb) if not objmask[y, x]]
            return row[sel].mean(axis=0) if len(sel) >= 3 else None
        oL, iL = mean_bg(x0 - margin, x0 - 1), mean_bg(x0 + 1, x0 + margin)
        oR, iR = mean_bg(x1 + 1, x1 + margin), mean_bg(x1 - margin, x1 - 1)
        dL = (oL - iL) if (oL is not None and iL is not None) else np.zeros(3)
        dR = (oR - iR) if (oR is not None and iR is not None) else np.zeros(3)
        for x in range(x0, x1):
            if objmask[y, x]: continue
            t = (x - x0) / max(1, x1 - x0 - 1)
            C[y, x] = row[x] + dL * (1 - t) + dR * t
R, G, B = A[..., 0], A[..., 1], A[..., 2]; lum = A.mean(axis=2)
obj = ((R - B > 25) & (R > 90)) | (lum < 70) | ((R > 180) & (G > 150) & (B < 90))   # 갈색 · 검정 · 노랑 동전
obj = binary_dilation(obj, iterations=2)
fix(1440, 1540, 438, 513, obj)      # 수레 패치
fix(1570, 1612, 452, 512, obj)      # 펌프 패치
# 경계 줄 부드럽게
for (x0, x1, y0, y1) in [(1440, 1540, 438, 513), (1570, 1612, 452, 512)]:
    for ch in range(3):
        bl = gaussian_filter(C[..., ch], 1.2)
        for xx in (x0, x1):
            m = ~obj[y0:y1, xx - 2:xx + 2]; C[y0:y1, xx - 2:xx + 2, ch][m] = bl[y0:y1, xx - 2:xx + 2][m]
        for yy in (y0, y1):
            m = ~obj[yy - 2:yy + 2, x0:x1]; C[yy - 2:yy + 2, x0:x1, ch][m] = bl[yy - 2:yy + 2, x0:x1][m]
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save(dst); print('patchfix', dst)

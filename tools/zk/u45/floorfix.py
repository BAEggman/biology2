# floorfix.py — E10 조각 아래 이음(2배 y≈756): 탑 아래층 바닥을 조각 바닥빛(모래빛)으로 이어 칠하고(옛 항아리 밑동 지움) 사다리 다리 두 줄은 원본 그대로
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
src, out = sys.argv[1:3]
A = np.asarray(Image.open(src).convert('RGB')).astype(float); C = A.copy()
x0, x1, ys, ye = 1748, 1966, 755, 784
band = A[738:754, x0:x1].reshape(-1, 3)
sandy = band[(band[:, 0] > 200) & (band[:, 1] > 165) & (band[:, 2] > 100) & (band[:, 2] < 175)]
base = np.median(sandy, axis=0); print('floor colour', base.round())
legs = [(1753, 1768), (1808, 1823)]
rng = np.random.default_rng(3)
for k, y in enumerate(range(ys, ye)):
    t = k / (ye - ys)
    for x in range(x0, x1):
        if any(a <= x < b for (a, b) in legs): continue
        C[y, x] = base * (1 - 0.12 * t) + rng.normal(0, 2.0, 3)
for c in range(3):
    seg = C[ys - 6:ys + 6, x0:x1, c].copy()
    C[ys - 3:ys + 3, x0:x1, c] = gaussian_filter1d(seg, 1.2, axis=0)[3:9]
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save(out)
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).crop((1680, 700, 2020, 830)).resize((1020, 390), Image.LANCZOS).save(out.replace('.png', '_floor.png'))
print('floor fixed')

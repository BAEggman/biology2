# bandfix.py — cur → out: 아래 두 띠(붉은 섬광)의 위·아래 테에서 옅게 바랜 구간(x 445~500 · 725~770)의 색을 같은 줄의 짙은 금빛 테에 맞춘다
import sys, numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
A = np.asarray(Image.open(src).convert('RGB')).astype(float); C = A.copy()
def fix(xa, xb, rows, refx):
    for y in rows:
        row = A[y]
        ref = [row[x] for x in refx if (row[x][0] > 180 and row[x][1] > 130 and row[x][2] < 118 and row[x][0] - row[x][2] > 80)]
        seg = [x for x in range(xa, xb) if (row[x][0] > 180 and row[x][1] > 140 and row[x][2] >= 110 and row[x][0] - row[x][1] < 60)]
        if len(ref) < 3 or len(seg) < 3: continue
        tgt = np.median(np.array(ref), axis=0); cur = np.median(np.array([row[x] for x in seg]), axis=0)
        for x in seg: C[y, x] = row[x] + (tgt - cur)
rows = list(range(631, 644)) + list(range(681, 693))
fix(445, 502, rows, list(range(415, 440)) + list(range(502, 516)) + list(range(560, 640)))
fix(722, 772, rows, list(range(695, 720)) + list(range(772, 790)) + list(range(815, 832)))
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save(dst); print('bandfix', dst)

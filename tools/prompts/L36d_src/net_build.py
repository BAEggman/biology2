"""N-L36d-01 — 오른쪽 잎(s3)의 잔맥 끝을 이웃 맥에 이어 닫힌 고리(그물)를 보인다.
바탕 = 커밋 f29239e2 의 lesson/img/L36d.webp. 다른 구역은 건드리지 않는다(s3 상자 밖은 다시 압축한 잡음만).
독자 검사(2026-11-21 · 글 없이 그림만): 「갈라진 줄끼리 다시 이어져 막힌 칸을 이룬다 · 닫힌 칸 8~12」 · 이름 「그물맥」 · 덧그린 티는 「조금」(위 · 오른쪽 아래 가장자리 곁의 각진 칸).
쓰는 법: python3 tools/prompts/L36d_src/net_build.py [--write]   (--write 가 없으면 /tmp 에만 쓴다)
"""
import io, json, random, subprocess, sys
from collections import deque
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

BASE = 'f29239e2'
X0, Y0, X1, Y1 = 1640, 320, 2048, 700          # s3 상자 [1640,320,408,370] 를 감싼 구역
raw = subprocess.run(['git', 'show', f'{BASE}:lesson/img/L36d.webp'], capture_output=True, check=True).stdout
im = Image.open(io.BytesIO(raw)).convert('RGB')
A = np.array(im).astype(int)
S = A[Y0:Y1, X0:X1]; r, g, b = S[..., 0], S[..., 1], S[..., 2]; lum = S.mean(2)

# 1) 잎 몸(초록 채움 → 닫기 · 구멍 메우기) · 테두리 안쪽
leafcol = (g > r + 20) & (g > b + 40) & (lum > 85) & (lum < 170)
lab, n = ndi.label(leafcol)
L = lab[500 - Y0, 1840 - X0]
leaf = ndi.binary_fill_holes(ndi.binary_closing(lab == L, structure=np.ones((3, 3)), iterations=9))
inner = ndi.binary_erosion(leaf, iterations=8)
# 2) 맥 = 어두운 선 + 옅은 초록 맥 → 한 덩이 → 뼈대
dark = (lum < 85) & inner
light = inner & (b > 85) & (lum > 112) & ~dark
V = ndi.binary_fill_holes(ndi.binary_closing(dark | light, iterations=2) & inner)
lab2, n2 = ndi.label(V, structure=np.ones((3, 3)))
V = lab2 == (np.argmax(ndi.sum(V, lab2, range(1, n2 + 1))) + 1)
sk = skeletonize(V)
pts = np.argwhere(sk); idx = {tuple(p): i for i, p in enumerate(pts)}
nbrs = [[idx[(y + dy, x + dx)] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
         if (dy or dx) and (y + dy, x + dx) in idx] for y, x in pts]

def walk(i):
    path = [i]; prev = -1; cur = i
    while len(path) < 400:
        if len(nbrs[cur]) > 2 and cur != i: break
        nx = [j for j in nbrs[cur] if j != prev and j not in path[-3:]]
        if not nx: break
        prev, cur = cur, nx[0]; path.append(cur)
    return path

def geo(s):
    D = np.full(len(pts), 10 ** 9); D[s] = 0; q = deque([s])
    while q:
        c = q.popleft()
        for j in nbrs[c]:
            if D[j] > D[c] + 1: D[j] = D[c] + 1; q.append(j)
    return D

# 3) 끝(가지 길이 8 이상) → 눈으로는 가깝고(7–42 px) 맥을 따라가면 먼(≥ 3배 · 60 px) 맥 점에 잇는다 = 닫힌 고리
tips = [i for i in range(len(pts)) if len(nbrs[i]) == 1 and len(walk(i)) >= 8]
edges, seen = [], set()
for t in tips:
    y, x = pts[t]; D = geo(t); e = np.hypot(pts[:, 0] - y, pts[:, 1] - x)
    ok = (e >= 7) & (e <= 42) & (D >= np.maximum(3.0 * e, 60))
    if not ok.any(): continue
    j = np.where(ok)[0][np.argmin(e[ok])]; q = pts[j]
    seg = [(int(round(y + (q[0] - y) * s)), int(round(x + (q[1] - x) * s))) for s in np.linspace(0, 1, 25)]
    if not all(inner[a, c] for a, c in seg): continue
    if sum(V[a, c] for a, c in seg[4:-4]) > 2: continue
    key = (min(t, j), max(t, j))
    if key in seen: continue
    seen.add(key); edges.append(((y, x), (q[0], q[1])))

# 4) 그리기 — 가는 잔맥과 같은 빛깔 · 굵기(2.2 px) · 살짝 휜 선 · 4배로 그려 줄임
random.seed(7); SS = 4; W, H = X1 - X0, Y1 - Y0
ov = Image.new('L', (W * SS, H * SS), 0); d = ImageDraw.Draw(ov)
for (y0, x0), (y1, x1) in edges:
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2; dx, dy = x1 - x0, y1 - y0; Ln = max(1e-6, (dx * dx + dy * dy) ** .5)
    k = random.choice([-1, 1]) * 0.12 * Ln; cx, cy = mx - dy / Ln * k, my + dx / Ln * k
    P = [(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1) * SS + SS / 2,
          ((1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1) * SS + SS / 2) for t in np.linspace(0, 1, 40)]
    d.line(P, fill=255, width=int(2.2 * SS), joint='curve')
ov = ov.resize((W, H), Image.LANCZOS)
patch = im.crop((X0, Y0, X1, Y1)); patch.paste(Image.new('RGB', (W, H), (22, 40, 12)), (0, 0), ov)
out = im.copy(); out.paste(patch, (X0, Y0))
assert not (np.array(ov) > 0)[~inner].any(), '잎 밖으로 그렸다'
dst = 'lesson/img/L36d.webp' if '--write' in sys.argv else '/tmp/L36d_net.webp'
out.save(dst, 'WEBP', quality=92, method=6)
print(f'이은 잔맥 {len(edges)} · 끝 {len(tips)} → {dst}')

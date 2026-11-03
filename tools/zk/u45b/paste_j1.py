#!/usr/bin/env python3
"""paste_j1.py — s45u02 v9 ① 행 4: Gemini(Argon) 편집 J1(오른 아래 무더기 LR 을 두 겹으로 · 그 뒤의 벽과 바닥 깔개 · 술을 이어 그림)을
c9a 위에 붙인다 — 붙이는 곳은 LR 아래쪽(x 726 ~ 812 · y 612 ~ 706)만, 둘레 바뀌지 않은 벽 · 깔개 화소로 빛 맞춤, 달라진 화소만(문턱 9) · 가장자리 1.5 px 번짐.
(v7 · v8 의 가운데 무더기 MR 난쟁이는 그 아래가 넓은 빈 벽으로 남아 「회색 네모 메움 자국」으로 읽혔다(b138 · b139) — 바닥 가까운 LR 를 줄이면 그 뒤가 바닥 깔개라 비어 보이지 않는다)
사용: paste_j1.py c9a.png crop_J1.json fit_J1.png out.png"""
import sys, json, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation
cur, cj, fit, out = sys.argv[1:5]
B = np.asarray(Image.open(cur).convert('RGB')).astype(float)
c = json.load(open(cj)); S = c['scale']; bx0, by0, bx1, by1 = [v * S for v in c['box']]
F = np.asarray(Image.open(fit).convert('RGB').resize((bx1 - bx0, by1 - by0), Image.LANCZOS)).astype(float)
C0 = B[by0:by1, bx0:bx1]
h, w = F.shape[:2]
yy, xx = np.mgrid[0:h, 0:w]
X0, X1, Y0, Y1 = 726 - bx0, 812 - bx0, 612 - by0, 706 - by0
R = (xx >= X0) & (xx < X1) & (yy >= Y0) & (yy < Y1)
ring = binary_dilation(R, iterations=10) & ~R
same = ring & (np.abs(C0 - F).mean(2) < 25)
d = (C0 - F)[same].mean(0); print('빛 맞춤', d.round(1), int(same.sum()))
Fc = np.clip(F + d, 0, 255)
diff = gaussian_filter(np.abs(C0 - Fc).mean(2), 1.0)
m = (diff > 9) & R
m = binary_dilation(m, iterations=2) & R
M = gaussian_filter(m.astype(float), 1.5) * R
B[by0:by1, bx0:bx1] = C0 * (1 - M[..., None]) + Fc * M[..., None]
Image.fromarray(np.clip(B, 0, 255).astype('uint8')).save(out)
print('붙인 화소', int(m.sum()))

#!/usr/bin/env python3
"""s21p02b — 개념 논리 M(외군이 먼저 갈라져야): 긴 가로대에 외군 · 가운데 인형 · 목도리 쌍이 한꺼번에 걸려 세 갈래이던 것 →
긴 가로대 → [외군] + [둘째 가로대 → [가운데 인형] + [셋째 작은 가로대 → 목도리 둘]].
제미나이 v1 은 둘째 가로대에 셋을 한꺼번에 걺(내군 셋 갈래) · v2 는 가운데 인형을 도로 맨 위 가로대로 올림 → v1 을 바탕으로
① v2 의 작은 가로대(x 770..935 · y 97..123 · 가운데 매달이 고리 x 853 · 양 끝 고리 785 · 918)를 dy +30 으로 옮겨 셋째 가로대로
② 둘째 가로대에서 목도리 쪽 끈 둘(x 786 · 919)과 그 고리를 지움(가로대 결은 12px 옆에서 · 바깥은 바탕 한 색)
③ 둘째 가로대 매달이 고리(x 853) 밑에서 셋째 가로대 고리까지 끈을 v1 의 x 853 끈(y 70..80)에서 옮겨 이음
⑤ 둘째 가로대를 x 878 에서 끝냄(끝마개는 원래 끝에서 옮김) — 셋째 가로대 위로 겹쳐 뻗어 두 겹처럼 보이지 않게
④ 오른쪽 인형 오른 다리의 반짝이 표식(x 930..947 · y 440..482)을 같은 줄 왼 다리 빛깔로 덮음
사용: python3 s21p02b_nest_bars.py V1.png V2.png OUT.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
v1p, v2p, dst = sys.argv[1], sys.argv[2], sys.argv[3]
A = np.asarray(Image.open(v1p).convert('RGB')).astype(np.float32)
B = np.asarray(Image.open(v2p).convert('RGB')).astype(np.float32)
assert A.shape == B.shape == (559, 1024, 3)
rng = np.random.default_rng(212)
out = A.copy()
bg = np.median(A[60:100, 700:800].reshape(-1, 3), axis=0)
# ② second-bar loops at 786 / 919 → bar grain from 12 px to the left; outside the bar body → background
for xc in (786, 919):
    x0, x1 = xc - 7, xc + 8
    out[106:120, x0:x1] = A[106:120, x0 - 14:x1 - 14]           # bar body rows (grain)
    for y in list(range(100, 106)) + list(range(120, 132)):
        for x in range(x0, x1):
            if A[y, x].mean() < bg.mean() - 12:
                out[y, x] = bg + rng.normal(0, 1.5, 3)
# keep the bar's top/bottom outline continuous: copy the outline rows from the left too
    out[102:106, x0:x1] = A[102:106, x0 - 14:x1 - 14]
    out[119:123, x0:x1] = A[119:123, x0 - 14:x1 - 14]
# ① third bar from v2 (alpha by colour distance to v2 background)
bg2 = np.median(B[60:95, 700:800].reshape(-1, 3), axis=0)
X0, X1, Y0, Y1, DY = 770, 936, 96, 124, 30
sub = B[Y0:Y1, X0:X1]
m = np.abs(sub - bg2).sum(2) > 30
m = ndi.binary_closing(m, iterations=1)
m = ndi.binary_fill_holes(m)
# drop the string stubs above the loops/ below the end loops (keep only rows 97..123 of bar + loops)
al = ndi.gaussian_filter(m.astype(np.float32), 0.6)[..., None]
tgt = out[Y0 + DY:Y1 + DY, X0:X1]
# first clear the old scarf strings in the target band (they would show through gaps)
for y in range(Y0 + DY - 6, Y1 + DY):
    for x in list(range(780, 793)) + list(range(913, 926)):
        if out[y, x].mean() < bg.mean() - 12:
            out[y, x] = bg + rng.normal(0, 1.5, 3)
tgt = out[Y0 + DY:Y1 + DY, X0:X1]
out[Y0 + DY:Y1 + DY, X0:X1] = tgt * (1 - al) + sub * al
# ③ connecting string at x 853 between the second bar (bottom ≈ 121) and the third bar's hanging loop (top ≈ 127)
strip = A[70:80, 849:858]
for y0 in range(121, 129, 10):
    h = min(10, 129 - y0)
    out[y0:y0 + h, 849:858] = strip[:h]
# ⑤ shorten the second bar so it clearly ends just past its hanging point (x 853): new end cap at x 866..878, the rest → background
cap = out[98:126, 924:936].copy()
for y in range(98, 126):
    for x in range(866, 937):
        if out[y, x].mean() < bg.mean() - 8 or abs(out[y, x] - bg).sum() > 25:
            out[y, x] = bg + rng.normal(0, 1.5, 3)
capm = np.abs(cap - bg).sum(2) > 25
reg = out[98:126, 866:878]
reg[capm] = cap[capm]
out[98:126, 866:878] = reg
# the connecting string at x 853 must stay: it is at x 849..858 (left of 866), untouched
# ④ sparkle on the right leg of the right-most puppet
for y in range(440, 483):
    ref = A[y, 914:926]
    ref = ref[(ref.mean(1) > 150)]
    if len(ref) < 3:
        continue
    leg = np.median(ref, axis=0)
    for x in range(930, 948):
        p = out[y, x]
        if p.mean() > leg.mean() + 6 and p.mean() > 150:
            out[y, x] = leg + rng.normal(0, 1.2, 3)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst); print('ok', dst)

# u01v9.py — v8(cur1) → v9 (b123 뒤): 좌판 세 칸에 동물 더하기(Gemini ST1 · 3.1 Pro) — 바뀐 화소만 사각형 안에서 골라 붙인다
#   ① 왼 칸 수조 속 올챙이(물속 = 암모니아 · 개구리와 사는 곳이 갈린다) ② 가운데 칸: 누런 요 밑에 숨은 상어(주둥이 · 꼬리) ·
#   반쯤 열린 바구니에서 내다보는 강아지(포유) ③ 오른 칸: 알 옆구리의 도마뱀(파충) · 알 앞 선반의 딱정벌레(곤충)
#   Gemini 가 지운 개구리 밑 동전 셋 · 개구리는 원본 그대로 둔다(사각형 밖)
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation, binary_fill_holes
cur, crop, fit, out = sys.argv[1:5]
B = np.asarray(Image.open(cur).convert('RGB')).astype(float)
c = np.asarray(Image.open(crop).convert('RGB')).astype(float)
f = np.asarray(Image.open(fit).convert('RGB')).astype(float)
OX, OY = 1530, 30
d = gaussian_filter(np.abs(c - f).mean(axis=2), 1.2)
chg = d > 14
rects = {  # 조각 2배 좌표 (x0,y0,x1,y1)
    'tadpole': (138, 172, 176, 198),
    'snout':   (198, 152, 238, 182),
    'puppy':   (272, 118, 322, 166),
    'tail':    (272, 182, 334, 236),
    'lizard':  (340, 116, 374, 188),
    'beetle':  (340, 188, 370, 212),
}
keep_orig = [(206, 196, 248, 214)]   # 동전 셋 줄 — 원본
M = np.zeros(chg.shape, bool)
for k, (x0, y0, x1, y1) in rects.items():
    sub = chg[y0:y1, x0:x1]
    sub = binary_fill_holes(binary_dilation(sub, iterations=3))
    M[y0:y1, x0:x1] |= sub
    print(k, int(sub.sum()))
for (x0, y0, x1, y1) in keep_orig: M[y0:y1, x0:x1] = False
A = gaussian_filter(M.astype(float), 1.2)
A = np.clip(A * 1.25, 0, 1)
C = B.copy(); h, w = c.shape[:2]
reg = C[OY:OY + h, OX:OX + w]
C[OY:OY + h, OX:OX + w] = reg * (1 - A[..., None]) + f * A[..., None]
Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save(out)
im = Image.fromarray(np.clip(C, 0, 255).astype('uint8'))
im.crop((1640, 120, 2000, 280)).resize((1080, 480), Image.LANCZOS).save(out.replace('.png', '_stall.png'))
print('saved', out)

# ── 2단계(같은 파일 · 함수로): 가시 공 넷을 0.6 배로(Gemini BL1) — 공 자리 사각형만 깃털 섞기
def balls(cur, crop, fit, out):
    B = np.asarray(Image.open(cur).convert('RGB')).astype(float)
    c = np.asarray(Image.open(crop).convert('RGB')).astype(float)
    f = np.asarray(Image.open(fit).convert('RGB')).astype(float)
    OX, OY = 560, 560
    M = np.zeros(c.shape[:2])
    for (x0, y0, x1, y1) in [(154, 95, 230, 169), (215, 134, 298, 248), (78, 169, 158, 242)]:
        M[y0:y1, x0:x1] = 1
    M = gaussian_filter(M, 3.0); M = np.clip(M * 1.6 - 0.3, 0, 1)
    C = B.copy(); h, w = c.shape[:2]
    C[OY:OY + h, OX:OX + w] = C[OY:OY + h, OX:OX + w] * (1 - M[..., None]) + f * M[..., None]
    im = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); im.save(out)
    im.crop((560, 560, 960, 860)).resize((800, 600), Image.LANCZOS).save(out.replace('.png', '_balls.png'))
    print('balls saved', out)

# ── 3단계: 왼쪽 벽 지평선의 흐린 회색 얼룩(「지운 듯한 유령」) — 벽 화소만 행마다 맑은 벽 빛(85 백분위)의 세로 기울기로 고르게
def wall(cur, out):
    A = np.asarray(Image.open(cur).convert('RGB')).astype(float); C = A.copy()
    L = A.mean(axis=2)
    for (x0, x1) in [(28, 136), (258, 366)]:
        y0, y1 = 118, 211
        seg = A[y0:y1, x0:x1]; Ls = L[y0:y1, x0:x1]
        wallm = (Ls > 185) & (seg[..., 0] - seg[..., 2] > 8)          # 크림 벽(호스 · 덕트 · 선 제외)
        ref = np.zeros((y1 - y0, 3))
        for i in range(y1 - y0):
            px = seg[i][wallm[i]]
            ref[i] = np.percentile(px, 85, axis=0) if len(px) > 10 else seg[i].mean(axis=0)
        ref = np.stack([gaussian_filter(ref[:, k], 4) for k in range(3)], axis=1)
        tgt = np.repeat(ref[:, None, :], x1 - x0, axis=1)
        a = gaussian_filter(wallm.astype(float), 1.0) * 0.9
        # 가장자리(위 · 양옆) 깃털
        fe = np.ones((y1 - y0, x1 - x0)); fe[:6] = 0; fe[:, :5] = 0; fe[:, -5:] = 0; fe = gaussian_filter(fe, 3)
        a *= fe
        C[y0:y1, x0:x1] = seg * (1 - a[..., None]) + tgt * a[..., None]
    im = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); im.save(out); print('wall saved', out)

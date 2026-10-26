# v6.py — cur4 → cur5 (b112 뒤): ① V 다섯(큰 그림 둘 · 오른 칸 둘 · 방 하나)을 「흰 글자」가 아니라 「볼트 박힌 쇠 이음쇠」로 —
#   강철빛 판 + 볼트 머리 셋 + 안쪽 테  ② 왼 칸(ADH 없음)의 V 자리 둘에 빈 꽂이(움푹한 V 홈, 점선 테)  ③ 둑 운하 물의 네모 합성 자국을 가로로 고르게
import math, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
A = np.asarray(Image.open('cur4.png').convert('RGB')).astype(float); H, W, _ = A.shape
C = A.copy()
# ── ③ 운하 물(y 92~158 · x 60~1186): 가로 긴 블러를 「매끈한 곳」에만 섞는다(레몬·분필·칼·물결은 남긴다)
y0, y1, x0, x1 = 92, 158, 60, 1186
Wt = C[y0:y1, x0:x1]; Bl = np.stack([gaussian_filter(Wt[..., c], (1.2, 28)) for c in range(3)], axis=2)
dif = np.abs(Wt - Bl).mean(axis=2); al = np.clip(1 - dif / 16, 0, 1) * 0.85
al = gaussian_filter(al, 1.0)
f = 6; M = np.ones_like(al); M[:f, :] = 0; M[-f:, :] = 0; M[:, :f] = 0; M[:, -f:] = 0; M = gaussian_filter(M, 3); M = M / M.max()
al *= M
C[y0:y1, x0:x1] = Wt * (1 - al[..., None]) + Bl * al[..., None]
# ── ① 방 V 자리를 왼쪽 주기(45px) 벽으로 되메움(창 사이 벽 무늬가 같다)
C[348:394, 1546:1590] = A[348:394, 1501:1545]
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img, 'RGBA')
STEEL, STEEL_D, OUT = (232, 234, 230), (196, 200, 196), (62, 56, 50)
def Vfit(cx, top, bot, half, w, r):
    a = math.atan2(half, bot - top); k = (w / 2) / math.sin(a)
    pts = [(cx - half - w / 2, top), (cx - half + w / 2, top), (cx, bot - k), (cx + half - w / 2, top), (cx + half + w / 2, top),
           (cx + w * 0.3, bot + w * 0.3), (cx - w * 0.3, bot + w * 0.3)]
    d.polygon(pts, fill=STEEL, outline=OUT); d.line(pts + [pts[0]], fill=OUT, width=max(1, round(w / 8)))
    # 안쪽 테(판 가장자리 단) — 바깥 윤곽 안쪽에 옅은 선
    ins = [(cx - half - w / 2 + w * 0.22, top + w * 0.22), (cx - half + w / 2 - w * 0.22, top + w * 0.22), (cx, bot - k - w * 0.45),
           (cx + half - w / 2 + w * 0.22, top + w * 0.22), (cx + half + w / 2 - w * 0.22, top + w * 0.22), (cx + w * 0.12, bot + w * 0.05), (cx - w * 0.12, bot + w * 0.05)]
    d.line(ins + [ins[0]], fill=STEEL_D, width=max(1, round(w / 9)))
    # 볼트 머리 셋: 두 팔 끝 · 꼭지 위
    for (bx, by) in [(cx - half, top + w * 0.55), (cx + half, top + w * 0.55), (cx, bot - k - w * 0.25 - r * 0.6)]:
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(96, 90, 84), outline=OUT)
        d.ellipse([bx - r * 0.45, by - r * 0.55, bx + r * 0.05, by - r * 0.05], fill=(210, 206, 200))
def T_R(X, Y): return ((X - 810) * 0.6 + 496, (Y - 204) * 0.6 + 330)   # 오른 칸
def T_L(X, Y): return ((X - 810) * 0.6 + 144, (Y - 204) * 0.6 + 330)   # 왼 칸
# 큰 그림 둘(이미 그린 흰 V 위에 덮어 그린다 — 같은 자리 · 같은 크기)
Vfit(1174, 362, 468, 34, 17, 4.2)
Vfit(1194, 583, 689, 34, 17, 4.2)
# 오른 칸 둘
for (cx, top, bot) in [(1174, 362, 468), (1194, 583, 689)]:
    (a, b) = T_R(cx, top); (_, c) = T_R(cx, bot); Vfit(a, b, c, 34 * 0.6, 17 * 0.6, 2.6)
# 방 하나
Vfit(1566, 355, 386, 13, 7.5, 1.9)
# ── ② 왼 칸: 빈 꽂이 둘 — 움푹한 V 홈(어두운 반투명 채움 + 점선 테)
def socket(cx, top, bot, half, w):
    a = math.atan2(half, bot - top); k = (w / 2) / math.sin(a)
    pts = [(cx - half - w / 2, top), (cx - half + w / 2, top), (cx, bot - k), (cx + half - w / 2, top), (cx + half + w / 2, top),
           (cx + w * 0.3, bot + w * 0.3), (cx - w * 0.3, bot + w * 0.3)]
    d.polygon(pts, fill=(70, 60, 50, 95))
    # 점선 테
    P = pts + [pts[0]]
    for i in range(len(P) - 1):
        (xa, ya), (xb, yb) = P[i], P[i + 1]; L = math.hypot(xb - xa, yb - ya); n = max(2, int(L / 4))
        for j in range(0, n, 2):
            t0, t1 = j / n, min(1, (j + 1) / n)
            d.line([(xa + (xb - xa) * t0, ya + (yb - ya) * t0), (xa + (xb - xa) * t1, ya + (yb - ya) * t1)], fill=(50, 44, 40, 230), width=1)
    # 빈 볼트 구멍 셋
    for (bx, by) in [(cx - half, top + w * 0.55), (cx + half, top + w * 0.55), (cx, bot - k - w * 0.25 - 1.5)]:
        d.ellipse([bx - 1.8, by - 1.8, bx + 1.8, by + 1.8], fill=(40, 36, 32, 220))
for (cx, top, bot) in [(1174, 362, 468), (1194, 583, 689)]:
    (a, b) = T_L(cx, top); (_, c) = T_L(cx, bot); socket(a, b, c, 34 * 0.6, 17 * 0.6)
img.save('cur5.png')
img.crop((1100, 330, 1300, 720)).resize((400, 780), Image.LANCZOS).save('v_cur5_V.png')
img.crop((130, 320, 800, 740)).resize((1005, 630), Image.LANCZOS).save('v_cur5_insets.png')
img.crop((1520, 330, 1620, 440)).resize((400, 440), Image.LANCZOS).save('v_cur5_roomV.png')
img.crop((840, 60, 1200, 180)).resize((1080, 360), Image.LANCZOS).save('v_cur5_canal.png')
print('cur5 saved')

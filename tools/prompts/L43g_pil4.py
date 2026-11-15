#!/usr/bin/env python3
# L43g_pil4.py <in.png> <out.png> — L43g 끝손질 넷째(2026-11-15 · 일치 검사 4회 뒤).
#  ① 맨 왼쪽(오래 버티는) 두루마리의 네모 스물셋이 흐린 파스텔 여러 빛(분홍 · 청록 · 보라 · 회색 …)이라 다른 종이의 또렷한 네 빛 네모와
#     「같은 종류로 안 읽힌다」(4회). 이 세계의 RNA 네모는 네 빛(초록 A · 빨강 G · 노랑 C · 파랑 U — L10b 객차 창)뿐이다 →
#     종이 흰 바탕을 찾아 그 안의 구멍(= 네모 칸)을 잡고, 칸 속(먹 테두리 밖)만 네 빛으로 다시 칠한다(밝기 비율로 음영 유지).
#     칸 둘레(먹 테 바깥의 번진 띠)까지 칠하면 테 바깥에 빛 테가 생긴다 → 구멍을 2 픽셀 깎은 안쪽만 칠한다.
#  ② 일꾼이 손에 든 앞머리 종이가 베이지 그늘이라 「흰 여백」으로 잘 안 읽힌다(3 · 4회) → 종이 흰빛 쪽으로 60 % 밝힌다. 앞머리의 잔 회색 점 하나(5회 「작은 검은 선」)도 지운다.
#  ③ 기계 뒤 문어가 찢는 흰 종이 뭉치에 네모가 없어 치켜든 토막(빨강 · 파랑 · 노랑)과 견줄 수 없다(5회) → 같은 차례의 작은 네모 셋을 찍는다
#     (바이러스 RNA 가 siRNA 와 꼭 맞아 잘림 = RNAi).
import sys
import numpy as np
import cv2
from PIL import Image

COL = {'G': (75, 170, 83), 'R': (218, 61, 67), 'Y': (244, 214, 65), 'B': (64, 129, 185)}
SEQ = 'GRYBRGBYYRGBGYBRRBGYBGRYG'                 # 읽는 차례(위 → 아래 · 줄마다 왼 칸 → 오른 칸)대로 — 일부러 들쭉날쭉
REG = (180, 800, 560, 1080)                     # 두루마리 몸통(네모 줄)
HEAD = (100, 800, 245, 990)                     # 손에 든 앞머리 종이
WHITE = np.array([248, 247, 243], float)
SPECK = (252, 829, 256, 836)                    # 앞머리의 잔 회색 점
INK = (40, 34, 30)
TORN = [(1381, 336, 'R'), (1381, 348, 'B'), (1380, 360, 'Y')]   # 찢기는 종이 뭉치의 네모(가운데 x · y · 빛)
TW, TH, TR = 8, 7, 1.6

def vivid_squares(a):
    X0, Y0, X1, Y1 = REG
    sub = a[Y0:Y1, X0:X1].astype(float)
    lum = sub.mean(2); sat = sub.max(2) - sub.min(2)
    paper = ((lum > 215) & (sat < 28)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(paper, 8)
    pm = (lab == (np.argmax(st[1:, 4]) + 1)).astype(np.uint8)        # 가장 큰 흰 덩이 = 두루마리 종이
    h, w = pm.shape
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats((1 - pm).astype(np.uint8), 4)
    sq = []
    for i in range(1, n2):
        x, y, ww, hh, ar = st2[i]
        if x > 0 and y > 0 and x + ww < w and y + hh < h and 120 < ar < 600:   # 종이 안에 갇힌 구멍 = 네모 칸
            m = lab2 == i; ys, xs = np.where(m)
            core = cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=2) > 0   # 테 바깥 번진 띠는 뺀다
            sq.append((ys.mean(), xs.mean(), core))
    # 읽는 차례: 두루마리가 오른쪽 아래로 휘므로 (y + 0.35 x) 로 줄을 세우고, 같은 줄은 x 차례
    sq.sort(key=lambda t: t[0] + 0.35 * t[1])
    for k, (cy, cx, m) in enumerate(sq):
        inner = m & (lum > 95)                                           # 먹 테두리(어두움)는 둔다
        if inner.sum() == 0: continue
        ref = np.median(lum[inner])
        t = np.clip(lum / max(ref, 1), 0.78, 1.12)[..., None]
        c = np.array(COL[SEQ[k % len(SEQ)]], float)
        sub = np.where(inner[..., None], np.clip(c * t, 0, 255), sub)
    a[Y0:Y1, X0:X1] = sub.astype(np.uint8)
    return len(sq)

def lighten_head(a):
    x0, y0, x1, y1 = HEAD
    sub = a[y0:y1, x0:x1].astype(float); r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    lum = sub.mean(2); sat = sub.max(2) - sub.min(2)
    beige = (lum > 185) & (sat >= 8) & (sat < 45) & (r >= g) & (g >= b)
    sub = np.where(beige[..., None], sub + 0.6 * (WHITE - sub), sub)
    a[y0:y1, x0:x1] = np.clip(sub, 0, 255).astype(np.uint8)
    return int(beige.sum())

def erase_speck(a):
    x0, y0, x1, y1 = SPECK
    sub = a[y0:y1, x0:x1].astype(int); lum = sub.mean(2); sat = sub.max(2) - sub.min(2)
    m = (sat < 30) & (lum < 236)
    sub[m] = WHITE.astype(int); a[y0:y1, x0:x1] = sub.astype(np.uint8)

def torn_squares(img):
    from PIL import ImageDraw
    K = 8
    for cx, cy, k in TORN:
        x0, y0 = int(cx - TW / 2 - 3), int(cy - TH / 2 - 3); SW, SH = TW + 7, TH + 7
        big = img.crop((x0, y0, x0 + SW, y0 + SH)).resize((SW * K, SH * K), Image.LANCZOS); d = ImageDraw.Draw(big)
        bx0, by0 = (cx - TW / 2 - x0) * K, (cy - TH / 2 - y0) * K; bx1, by1 = bx0 + TW * K, by0 + TH * K
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=TR * K, fill=INK)
        t = 1.2 * K
        d.rounded_rectangle([bx0 + t, by0 + t, bx1 - t, by1 - t], radius=max(TR - 0.8, 0.3) * K, fill=COL[k])
        img.paste(big.resize((SW, SH), Image.LANCZOS), (x0, y0))
    return img

def main(src, out):
    a = np.array(Image.open(src).convert('RGB'))
    n = vivid_squares(a); hb = lighten_head(a); erase_speck(a)
    a = np.array(torn_squares(Image.fromarray(a)))
    Image.fromarray(a).save(out); print('→', out, '· 네모', n, '· 앞머리 픽셀', hb)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

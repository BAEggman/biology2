#!/usr/bin/env python3
# L48g_pil.py <in.png> <out.png> — L48g 「아래층의 두 번째 이별과 마당의 시상식」 PIL 손질(2026-11-15 · Opus 5.5)
#  ① 은메달 이발사가 든 다발 — 누런 반쪽을 하늘색으로(일치 검사 1회 △ 「두 빛깔이 흐리다」) → 남색 + 하늘색 = 재조합 염색체(L48f 이발사)
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SKY = [(110, (100, 128, 140)), (150, (139, 168, 179)), (195, (179, 210, 222)), (228, (207, 237, 247))]


def ramp(stops, L):
    xs = np.array([s[0] for s in stops], float); cs = np.array([s[1] for s in stops], float)
    return np.stack([np.interp(L, xs, cs[:, k]) for k in range(3)], -1)


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def tan_to_sky(a, pts, feather=1.5):
    """누런 짚(r > b + 25 · g > b + 10 · r ≥ g · 밝음)을 하늘색 짚으로 — 밝기 순위대로 · 가장자리 흐림."""
    m = Image.new('L', (a.shape[1], a.shape[0]), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    w = np.array(m.filter(ImageFilter.GaussianBlur(feather))).astype(float) / 255
    L = lum(a); sel = (w > 0.01) & (a[..., 0] > a[..., 2] + 25) & (a[..., 1] > a[..., 2] + 10) & (a[..., 0] >= a[..., 1] - 5) & (L > 95)   # 풀밭(초록: g > r)은 빼고
    b = a.copy(); t = np.clip((L[sel] - 95) / (235 - 95), 0, 1)
    b[sel] = ramp(SKY, 115 + t * 113)
    a[:] = a * (1 - w[..., None]) + b * w[..., None]
    return int(sel.sum())


def inpaint(a, box):
    """작은 자국 지우기(둘레 빛으로 메움)."""
    import cv2
    x0, y0, x1, y1 = box
    u = np.clip(a, 0, 255).astype(np.uint8); m = np.zeros(u.shape[:2], np.uint8); m[y0:y1, x0:x1] = 255
    a[:] = cv2.inpaint(u, m, 5, cv2.INPAINT_TELEA).astype(float)


def spore_teal(a, box):
    """④ 푸른곰팡이의 포자 구름 — 베이지 구름이 「연기 · 김」으로 읽혔다(일치 검사 2 · 3회 △) → 곰팡이 빛(청록)으로. 윤곽 · 풀밭은 그대로."""
    x0, y0, x1, y1 = box; r = a[y0:y1, x0:x1]
    L = lum(r); beige = (r[..., 0] > r[..., 2] + 12) & (r[..., 0] >= r[..., 1] - 4) & (L > 150)
    t = np.clip((L[beige] - 150) / 75, 0, 1)[:, None]
    lo, hi = np.array([118, 178, 176.]), np.array([186, 228, 224.])
    r[beige] = lo * (1 - t) + hi * t
    return int(beige.sum())


def main(src, dst):
    a = np.array(Image.open(src).convert('RGB')).astype(float)
    n = tan_to_sky(a, [(1500, 486), (1546, 484), (1544, 530), (1520, 536), (1502, 532)]) \
        + tan_to_sky(a, [(1478, 562), (1512, 560), (1517, 607), (1479, 607)])
    print('이발사 다발 누런 쪽 → 하늘색', n)
    inpaint(a, (848, 632, 870, 725))      # ② 오른쪽 방 — GB 의 비스듬한 칸막이 윗동(H3 상자 722 위에 남은 말뚝)
    inpaint(a, (486, 466, 507, 495)); inpaint(a, (523, 466, 547, 493))      # ③ 계단 밑 — 옛 짚단 발 둘(H6 오림 아래 끝 475 밖에 남음)
    print('포자 구름 → 청록', spore_teal(a, (1830, 935, 1895, 992)))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

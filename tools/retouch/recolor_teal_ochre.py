#!/usr/bin/env python3
"""recolor_teal_ochre.py — 상자 안의 **청록(회청) 깃발 면**만 **황토**로 바꾼다(명암은 그대로).
s13p02 의 규칙 「깃발 청록 = IgE(1형) · 황토 = IgG·IgM(2·3형)」에 형제 판 깃발을 맞추려고 만듦(2026-10-01):
  s13p01 IgM 오각 고리의 다섯 깃발(청록 → 황토) · s13p02 3형 깃발 안쪽 접힌 면(청록 → 황토 그늘).
깃발 면 찾기: 청록 씨앗(색상 120..200° · 채도 > 0.1 · 명도 0.3..0.85)이 20% 넘게 든, 잉크(명도 ≤ 0.33)·바탕(명도 ≥ 0.88)으로
  갈린 4-연결 덩어리(> 100px) — 연필 결 때문에 채도가 거의 없는 회색 화소(색상 60..70°)까지 한 면으로 잡는다.
  (첫 판은 색상 창만 써서 면 가장자리 회청이 테두리처럼 남았다.)
새 색 = HSV(H 34°, S 0.47, V = 0.79·v/0.56 (≤ 0.97)) — 원래 명암 비를 그 판 바지(황토 H 32.5 · S 0.5 · V 0.78)에 맞춘 명도로.
사용: python3 recolor_teal_ochre.py ORIG OUT x0,y0,x1,y1 [x0,y0,x1,y1 ...]"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def rgb2hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(axis=2); mn = a.min(axis=2); d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = (mx == r) & m; gg = (mx == g) & m & ~rr; bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6; h[gg] = ((b - r)[gg] / d[gg]) + 2; h[bb] = ((r - g)[bb] / d[bb]) + 4
    return h * 60, np.where(mx > 0, d / np.maximum(mx, 1e-6), 0), mx


def hsv2rgb(h, s, v):
    h = (h % 360) / 60; i = np.floor(h).astype(int) % 6; f = h - np.floor(h)
    p = v * (1 - s); q = v * (1 - s * f); t = v * (1 - s * (1 - f))
    out = np.zeros(h.shape + (3,))
    for k, (R, G, B) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        m = i == k
        out[m] = np.stack([R[m], G[m], B[m]], axis=1)
    return out


if __name__ == '__main__':
    op, dst = sys.argv[1], sys.argv[2]
    boxes = [tuple(int(v) for v in b.split(',')) for b in sys.argv[3:]]
    A = np.asarray(Image.open(op).convert('RGB')).astype(np.float64) / 255
    H, S, V = rgb2hsv(A)
    reg = np.zeros(H.shape, bool)
    for (x0, y0, x1, y1) in boxes:
        reg[y0:y1, x0:x1] = True
    seed = reg & (H > 120) & (H < 200) & (S > 0.1) & (V > 0.3) & (V < 0.85)
    cand = reg & (V > 0.33) & (V < 0.88) & (S < 0.45)
    lab, n = ndi.label(cand)                      # 4-연결(기본)
    face = np.zeros_like(cand)
    for k in range(1, n + 1):
        c = lab == k
        sz = c.sum()
        if sz > 100 and seed[c].mean() > 0.2:
            face |= c
    face = ndi.binary_fill_holes(face) & cand
    # 잉크 곁 반쯤 섞인 화소까지 1px
    face |= ndi.binary_dilation(face, iterations=1) & reg & (V > 0.3) & (V < 0.9)
    w = ndi.gaussian_filter(face.astype(float), 0.5) * reg
    w = np.maximum(w, face.astype(float))
    new = hsv2rgb(np.full(H.shape, 34.0), np.full(H.shape, 0.47), np.clip(np.minimum(0.97, 0.79 * V / 0.56), 0, 1))
    out = A * (1 - w[..., None]) + new * w[..., None]
    Image.fromarray(np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)).save(dst)
    print('faces px %d' % int(face.sum()))

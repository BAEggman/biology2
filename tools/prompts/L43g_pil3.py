#!/usr/bin/env python3
# L43g_pil3.py <in.png> <out.png> — L43g 끝손질 셋째(2026-11-15 · 일치 검사 3회 뒤 ZR 다음).
#  아래 오른쪽 문어(불완전 일치 → 번역 억제)가 ZR 로 치켜든 토막의 네모가 두루마리 위 네모(초록 · 빨강 · 노랑 · 파랑)와 똑같이 그려졌다
#  = 「칸칸이 꼭 맞음」(완전 일치 · 아래 가운데 문어의 몫)으로 읽힌다. 끝 두 칸을 바꿔 일부만 맞게 한다:
#  끝(치켜든 쪽)에서 팔 쪽으로 초록 · 빨강 · 노랑 · 파랑 → 초록 · 빨강 · 빨강 · 초록(앞뒤 대칭 — 어느 쪽에서 읽어도 첫 칸 초록만 두루마리와 같고
#  끝 칸들은 다르다 · 처음엔 초록 · 빨강 · 파랑 · 초록으로 했더니 일치 검사 5회가 「읽는 방향에 따라 앞 두 칸 / 첫 칸만」으로 갈렸다).
import sys
import numpy as np
from PIL import Image

GRN, RED = (75, 170, 83), (218, 61, 67)
# (상자 x0, y0, x1, y1, 원래 빛, 새 빛) — 2048 × 1144 기준
SWAP = [
    (1338, 844, 1356, 862, (244, 214, 65), RED),     # 셋째 칸 노랑 → 빨강
    (1322, 862, 1342, 878, (79, 130, 180), GRN),     # 넷째 칸 파랑 → 초록(문어 다리 끝에 반쯤 가림)
]

def shift(a, box, src, dst, tol=90.0):
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1].astype(float)
    d = np.abs(sub - np.array(src, float)).max(axis=2)
    w = np.clip(1 - d / tol, 0, 1)[..., None]
    sub = sub + w * (np.array(dst, float) - np.array(src, float))
    a[y0:y1, x0:x1] = np.clip(sub, 0, 255).astype(np.uint8)

def yellow_to(a, box, src, dst):
    """노랑과 그 테두리 번짐(노랑 + 먹)을 밝기 비율대로 새 빛으로 — 거리 기준만으로는 노란 테가 남았다."""
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1].astype(float); r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    m = (r - b > 50) & (g - b > 30) & (r > 90) & (g > 0.72 * r)          # 노란 기운(주황 문어 다리 g ≈ 0.5 r 는 뺌)
    lum = sub.mean(axis=2); t = np.clip(lum / np.mean(src), 0, 1.1)[..., None]
    sub = np.where(m[..., None], np.array(dst, float) * t, sub)
    a[y0:y1, x0:x1] = np.clip(sub, 0, 255).astype(np.uint8)

def main(src, out):
    a = np.array(Image.open(src).convert('RGB'))
    x0, y0, x1, y1, s, d = SWAP[0]; yellow_to(a, (x0, y0, x1, y1), s, d)
    x0, y0, x1, y1, s, d = SWAP[1]; shift(a, (x0, y0, x1, y1), s, d)
    Image.fromarray(a).save(out); print('→', out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

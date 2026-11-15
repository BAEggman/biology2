#!/usr/bin/env python3
# L43g_pil.py <in.png> <out.png> — L43g 끝손질(2026-11-15 · Opus 5.5).
#  ① 찢긴 두루마리(왼쪽 조각)의 빛깔 네모를 문어가 치켜든 토막과 같은 차례(초록 · 빨강 · 노랑 · 파랑)로 — Gemini 는 초록 · 파랑 · 빨강 · 노랑으로 그렸다(「칸칸이 꼭 맞음」이 안 섬)
#  ② 문어 머리의 꼬불한 먹 자국(「S3」 · 글자처럼 읽힐 수 있음)을 문어 살빛으로 지운다
import sys
import numpy as np
from PIL import Image, ImageFilter

RED, YEL, BLU = (218, 74, 75), (245, 222, 47), (64, 129, 185)
# (상자 x0, y0, x1, y1, 원래 빛, 새 빛) — 2048 × 1144 기준
SQUARES = [
    (1125, 1052, 1145, 1066, (64, 129, 185), RED),    # 둘째 칸 파랑 → 빨강
    (1141, 1039, 1161, 1055, (218, 74, 75), YEL),     # 셋째 칸 빨강 → 노랑
    (1158, 1029, 1175, 1044, (245, 222, 47), BLU),    # 넷째 칸 노랑 → 파랑
]
MARK = (1084, 876, 1106, 905)                         # 문어 머리의 먹 자국
TEAR = (484, 282, 498, 306)                           # 구멍에서 나오는 일꾼 뺨의 눈물(웃는 얼굴에 눈물 — 우는 일꾼과 헷갈림 · 일치 검사 1회)

def recolor(a, box, src, dst, tol=70):
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1].astype(int)
    m = np.abs(sub - np.array(src)).max(axis=2) < tol
    sub[m] = dst
    a[y0:y1, x0:x1] = sub.astype(np.uint8)

def erase_mark(img, box):
    x0, y0, x1, y1 = box
    a = np.array(img).astype(int)
    sub = a[y0:y1, x0:x1]
    skin = (sub[..., 0] > 190) & (sub[..., 1] > 80) & (sub[..., 1] < 150) & (sub[..., 2] < 110)
    col = np.median(sub[skin], axis=0)
    dark = sub.max(axis=2) < 175                      # 먹 자국(어두운 갈색)
    sub[dark] = col
    a[y0:y1, x0:x1] = sub
    out = Image.fromarray(a.astype(np.uint8))
    # 이음 자리를 아주 살짝 흐리게(그 상자 안만)
    soft = out.crop(box).filter(ImageFilter.GaussianBlur(0.8)); out.paste(soft, box[:2])
    return out

def erase_tear(img, box):
    """뺨의 물방울(먹 테 + 하늘빛)을 둘레 살빛으로."""
    x0, y0, x1, y1 = box
    a = np.array(img).astype(int); sub = a[y0:y1, x0:x1]
    ring = np.concatenate([a[y0 - 3:y0, x0:x1].reshape(-1, 3), a[y1:y1 + 3, x0:x1].reshape(-1, 3), a[y0:y1, x0 - 3:x0].reshape(-1, 3), a[y0:y1, x1:x1 + 3].reshape(-1, 3)])
    skin = ring[(ring[:, 0] > 190) & (ring[:, 0] > ring[:, 2] + 30)]
    col = np.median(skin, axis=0)
    off = np.abs(sub - col).max(axis=2) > 18
    sub[off] = col
    a[y0:y1, x0:x1] = sub
    out = Image.fromarray(a.astype(np.uint8))
    soft = out.crop(box).filter(ImageFilter.GaussianBlur(0.7)); out.paste(soft, box[:2])
    return out

def main(src, out):
    img = Image.open(src).convert('RGB'); a = np.array(img)
    for x0, y0, x1, y1, s, d in SQUARES: recolor(a, (x0, y0, x1, y1), s, d)
    img = erase_mark(Image.fromarray(a), MARK)
    img = erase_tear(img, TEAR)
    img.save(out); print('→', out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

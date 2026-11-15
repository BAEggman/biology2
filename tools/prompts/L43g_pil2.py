#!/usr/bin/env python3
# L43g_pil2.py <in.png> <out.png> — L43g 끝손질 둘째(2026-11-15 · 일치 검사 1 · 2회 뒤).
#  ① 씨름꾼이 깔고 앉은 두루마리는 온통 흰 종이라 「머리 쪽 여백에 앉음」이 그림에서 안 섰다(1회 △).
#     일꾼이 잡아당기는 쪽 종이에 빛깔 네모 넷을 한 줄로 찍는다 → 씨름꾼은 네모가 시작되기 전의 흰 여백(5′ UTR)에 앉은 것이 보인다.
#     네모 빛깔 차례는 문어 토막(초록 · 빨강 · 노랑 · 파랑)과 일부러 다르게(파랑 · 노랑 · 초록 · 빨강) — 「맞는 토막」으로 읽히지 않게.
#  ② 맨 왼쪽 두루마리 앞머리의 흐린 회색 줄 자국(「빈 윤곽 네모」로 읽혀 머리 여백이 흐려짐 · 2회 △) → 종이 흰빛으로.
#  (탁자 밑 「호스 같은 줄」과 아래 가운데 문어 머리의 잔 얼룩은 PIL 로 메우니 자국이 남아 구역 편집 ZT 로 지웠다 — L43g_build.sh)
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

GRN, RED, YEL, BLU = (80, 165, 90), (218, 74, 75), (245, 222, 47), (64, 129, 185)
INK = (40, 34, 30)
# (가운데 x, 가운데 y, 빛) — 2048 × 1144 기준 · 종이 오른쪽 맑은 띠(x 744 ~ 757 · 구김 선은 x ≤ 740)
SQ = [(748, 714, BLU), (748, 730, YEL), (748, 746, GRN), (748, 762, RED)]
W, H, R = 12, 10, 2.4
DASH = [(212, 826), (244, 811), (252, 812), (252, 840), (238, 845), (220, 845)]   # 왼쪽 두루마리 앞머리의 회색 줄 자국(다각형 · 첫 보라 네모 x ≥ 254 는 뺌)

def squares(img):
    K = 8
    for cx, cy, col in SQ:
        x0, y0 = int(cx - W / 2 - 3), int(cy - H / 2 - 3); SW, SH = W + 7, H + 7
        big = img.crop((x0, y0, x0 + SW, y0 + SH)).resize((SW * K, SH * K), Image.LANCZOS); d = ImageDraw.Draw(big)
        bx0, by0 = (cx - W / 2 - x0) * K, (cy - H / 2 - y0) * K; bx1, by1 = bx0 + W * K, by0 + H * K
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=R * K, fill=INK)
        t = 1.3 * K
        d.rounded_rectangle([bx0 + t, by0 + t, bx1 - t, by1 - t], radius=(R - 0.8) * K, fill=col)
        hl = tuple(min(255, int(c + (255 - c) * 0.35)) for c in col)
        d.rounded_rectangle([bx0 + t + 0.8 * K, by0 + t + 0.8 * K, bx0 + W * K * 0.55, by0 + H * K * 0.42], radius=0.8 * K, fill=hl)
        img.paste(big.resize((SW, SH), Image.LANCZOS), (x0, y0))
    return img

def erase_dashes(img):
    a = np.array(img).astype(int)
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).polygon(DASH, fill=255); m = np.array(m) > 0
    lum = a.mean(axis=2); sat = a.max(axis=2) - a.min(axis=2)
    paper = m & (lum > 225) & (sat < 25)
    col = np.median(a[paper], axis=0)
    grey = m & (lum > 70) & (lum <= 236) & (sat < 40)          # 회색 줄(먹 테두리 lum ≤ 70 · 빛깔 네모 sat ≥ 40 는 둔다)
    a[grey] = col
    return Image.fromarray(a.astype(np.uint8))

def main(src, out):
    img = Image.open(src).convert('RGB')
    img = squares(img)
    img = erase_dashes(img)
    img.save(out); print('→', out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

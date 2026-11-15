#!/usr/bin/env python3
# L54c_pil.py <in.png> <out.png> — L54c 끝손질(2026-11-15 · 일치 검사 1회 뒤).
#  나침반 바늘이 「멈춰 있다」로 읽혀(△) — 나침반 안쪽 판(가운데 1622.5,463 · 반지름 16.5)을 새로 그린다:
#  흰 판 · 굵은 둥근 화살표(바늘 둘레를 도는 방향) · 빨강/파랑 바늘 끝이 휩쓸고 간 부채꼴 잔상 · 바늘 · 가운데 축.
#  8 배로 크게 그려 줄여 붙인다(선이 매끈하게).
import sys, math
from PIL import Image, ImageDraw, ImageFilter

CX, CY, R_IN = 1622.5, 463.0, 16.5
K = 8                                   # 확대 배율

def compass(img):
    x0, y0 = int(CX - 20), int(CY - 20); x1, y1 = int(CX + 21), int(CY + 21)
    W, H = (x1 - x0) * K, (y1 - y0) * K
    cx, cy = (CX - x0) * K, (CY - y0) * K
    big = img.crop((x0, y0, x1, y1)).resize((W, H), Image.LANCZOS)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = R_IN * K
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 240, 234, 255))          # 흰 판
    def pt(rad, ang): return (cx + rad * K * math.cos(math.radians(ang)), cy + rad * K * math.sin(math.radians(ang)))
    # 굵은 둥근 화살표(반지름 13 · 290°) + 화살촉
    rr = 13.0 * K; a0, a1 = -30, 260
    d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1, fill=(25, 25, 25, 255), width=int(2.3 * K))
    tip = pt(13.0, a1 + 22); bL = pt(13.0 - 3.4, a1 - 2); bR = pt(13.0 + 3.4, a1 - 2)
    d.polygon([tip, bL, bR], fill=(25, 25, 25, 255))
    # 바늘 — 지나온 자리의 흐린 잔상 셋(25° 씩 뒤 · 점점 옅게) 위에 지금 자리(빨강 끝 -55° · 파랑 끝 125°).
    #  (끝이 휩쓸고 간 꼬리를 호로 그리면 빨강 호 + 바늘이 숫자 「7」처럼 읽혀 버렸다 → 잔상으로)
    def needle(a, col, al):
        t = pt(10.0, a); s1 = pt(2.2, a + 90); s2 = pt(2.2, a - 90)
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(g)
        dg.polygon([t, s1, (cx, cy), s2], fill=col + (al,), outline=(30, 30, 30, al) if al == 255 else None)
        return g
    for k, al in ((3, 45), (2, 80), (1, 125)):
        a = -55 - 25 * k
        lay = Image.alpha_composite(lay, needle(a, (215, 55, 45), al)); lay = Image.alpha_composite(lay, needle(a + 180, (60, 95, 180), al))
    lay = Image.alpha_composite(lay, needle(-55, (215, 55, 45), 255)); lay = Image.alpha_composite(lay, needle(125, (60, 95, 180), 255))
    d = ImageDraw.Draw(lay)
    d.ellipse([cx - 1.8 * K, cy - 1.8 * K, cx + 1.8 * K, cy + 1.8 * K], fill=(60, 60, 60, 255))  # 축
    big = Image.alpha_composite(big.convert('RGBA'), lay).convert('RGB')
    small = big.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    m = Image.new('L', (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).ellipse([CX - x0 - R_IN, CY - y0 - R_IN, CX - x0 + R_IN, CY - y0 + R_IN], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(0.6))
    img.paste(small, (x0, y0), m)
    return img

def main(src, out):
    img = Image.open(src).convert('RGB')
    compass(img)
    img.save(out)
    print('→', out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

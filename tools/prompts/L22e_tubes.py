#!/usr/bin/env python3
"""L22e_tubes.py <in.png> <out.png> [--list] — 그루터기 단면 초록 고리(관다발형성층) 둘레 관 토막의 빛깔을 자리대로 바로잡는다(2026-11-16).
  고리 안쪽(가운데 쪽) 토막 = 청록(2차 물관부 = 목재) · 바깥쪽(껍질 쪽) 토막 = 분홍(2차 체관부). Gemini 는 두 번(S1 · ZP)이나 토막을 섞어 그렸다 → 빛깔만 바꾼다.
  고리 = 타원(가운데 CX, CY · 반지름 AX, AY — 열마다 밝은 초록 띠의 앞 · 뒤 y 를 재어 맞춤). 덩이 평균 채도 < 0.34 · 명도 < 0.45 · 넓이 < 60 = 관 아님(일꾼 바지 · 돋보기 알) · 오른쪽 위 = 파란 천막 — 그대로 둔다. 토막 = 분홍 / 청록 화소 덩이 · 무게중심이 타원 안이면 청록 · 밖이면 분홍. 빛깔 바꿈 = HSV 색상만 돌리고 채도 · 명도는 두 빛깔의 중앙값 비로 맞춘다."""
import sys, colorsys
import numpy as np, cv2
from PIL import Image
CX, CY, AX, AY = 980, 441, 253, 81
ROI = (668, 318, 1290, 560)                         # 단면 둘레(천막 · 하늘 밖)
PINK = (334, 0.39, 0.80); TEAL = (176, 0.45, 0.70)    # 중앙값(H°, S, V)
src, out = sys.argv[1], sys.argv[2]; LIST = '--list' in sys.argv
skip = [tuple(map(int, a[7:].split(','))) for a in sys.argv if a.startswith('--skip=')]   # 그대로 둘 덩이(무게중심 x,y)
im = np.array(Image.open(src).convert('RGB')); H, W = im.shape[:2]
x0, y0, x1, y1 = ROI
sub = im[y0:y1, x0:x1].astype(np.float32) / 255
hsv = cv2.cvtColor(sub, cv2.COLOR_RGB2HSV)            # H 0..360, S 0..1, V 0..1 (float 입력)
h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
yy, xx = np.mgrid[y0:y1, x0:x1]
ell = ((xx - CX) / (AX + 60)) ** 2 + ((yy - CY) / (AY + 45)) ** 2 < 1   # 단면 안 + 고리 바깥 띠까지
pink = (h > 312) & (h < 352) & (s > 0.17) & (v > 0.38) & ell
teal = (h > 158) & (h < 196) & (s > 0.18) & (v > 0.30) & ell
def comps(mask):
    m = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    return [(lab == i, st[i], cen[i]) for i in range(1, n) if st[i][4] >= 25]
res = im.copy().astype(np.float32) / 255; changed = 0
for name, mask, want_in in (('분홍', pink, False), ('청록', teal, True)):
    for m, st, (cx, cy) in comps(mask):
        gx, gy = cx + x0, cy + y0
        r = ((gx - CX) / AX) ** 2 + ((gy - CY) / AY) ** 2
        ms, mv = float(s[m].mean()), float(v[m].mean())
        inside = r < 1
        wrong = inside != want_in
        tag = '✕ 바꿈' if wrong else '○'
        if ms < 0.34 or mv < 0.45 or st[4] < 60: tag = '· 둠(관 아님 — 바지 · 돋보기 알 · 작은 조각)'; wrong = False
        if gx > 1225 and gy < 395: tag = '· 둠(파란 천막)'; wrong = False
        if any(abs(gx - a) < 6 and abs(gy - b) < 6 for a, b in skip): tag = '· 둠(--skip)'; wrong = False
        if LIST or wrong: print(f'{name} 덩이 무게중심 ({gx:.0f},{gy:.0f}) 넓이 {st[4]} 상자 {st[2]}x{st[3]} S {ms:.2f} V {mv:.2f} r²={r:.2f} {"안" if inside else "밖"} {tag}')
        if not wrong: continue
        a, b = (PINK, TEAL) if name == '분홍' else (TEAL, PINK)
        mm = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        mm &= (s > 0.10) & (v > 0.25)            # 테두리 검은 선은 그대로
        hh = (h[mm] - a[0] + b[0]) % 360; ss = np.clip(s[mm] * b[1] / a[1], 0, 1); vv = np.clip(v[mm] * b[2] / a[2], 0, 1)
        rgb = cv2.cvtColor(np.dstack([hh, ss, vv]).astype(np.float32), cv2.COLOR_HSV2RGB).reshape(-1, 3)
        reg = res[y0:y1, x0:x1]; reg[mm] = rgb; changed += int(mm.sum())
Image.fromarray((np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out)
print('바꾼 화소', changed)

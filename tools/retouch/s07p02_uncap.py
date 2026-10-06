#!/usr/bin/env python3
"""s07p02_uncap.py — 배턴 양끝의 짙은 마구리(띠 + 끝면)를 몸통 결로 덮어 민 나무 배턴으로 (10/6 블라인드 재검: 마구리 때문에 「밀방망이」로 읽힘).
배턴 축(두 끝점)과 반너비를 주면, 마구리 구간의 안쪽 화소를 축 가운데 단면(같은 수직 오프셋 s)의 색으로 바꾼다. 바깥 윤곽(|s| > hw-1.5)과 끝 2px 는 그대로.
사용: python3 s07p02_uncap.py SRC OUT 'x0,y0,x1,y1,hw,capA,capB' ...   (끝점 A→B · hw 반너비 · capA/capB = 각 끝 마구리 길이 px)"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float64)
H, W = im.shape[:2]
out = im.copy()
for spec in sys.argv[3:]:
    x0, y0, x1, y1, hw, ca, cb = (float(v) for v in spec.split(','))
    A = np.array([x0, y0]); B = np.array([x1, y1]); L = np.linalg.norm(B - A); d = (B - A) / L; n = np.array([-d[1], d[0]])
    C = (A + B) / 2
    ys, xs = np.mgrid[0:H, 0:W]
    px = xs - C[0]; py = ys - C[1]
    t = px * d[0] + py * d[1]; s = px * n[0] + py * n[1]
    inside = (np.abs(s) <= hw - 1.5)
    capm = inside & (((t >= -L / 2 + 2) & (t <= -L / 2 + ca)) | ((t <= L / 2 - 2) & (t >= L / 2 - cb)))
    # 참조 단면: 마구리 바로 안쪽 몸통(끝에서 ca+4 … ca+10 · cb 쪽도 같이)의 평균 — 가운데는 손이 잡고 있을 수 있어 안 쓴다
    for side, capside, tref in ((-1, (t >= -L / 2 + 2) & (t <= -L / 2 + ca), -L / 2 + ca + 4), (1, (t <= L / 2 - 2) & (t >= L / 2 - cb), L / 2 - cb - 4)):
        m = inside & capside
        for k in range(3):
            acc = np.zeros(H * W); cnt = 0
            for tr in (tref, tref + side * -2, tref + side * -4, tref + side * -6):
                sx = C[0] + tr * d[0] + s * n[0]; sy = C[1] + tr * d[1] + s * n[1]
                acc += ndi.map_coordinates(im[..., k], [sy.ravel(), sx.ravel()], order=1, mode='nearest'); cnt += 1
            ch = out[..., k]; ch[m] = (acc / cnt).reshape(H, W)[m]
    print(spec, 'replaced px', int(capm.sum()))
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)

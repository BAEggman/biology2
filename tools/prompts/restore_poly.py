#!/usr/bin/env python3
"""restore_poly.py <orig.png> <img.png> "x,y;x,y;…" [feather] — 구역 편집으로 붙인 뒤, 다각형 안을 원래 그림(orig)의 픽셀로 되돌린다(2026-11-14 · L13a 다시 짓기).
  상자 하나에 들어간 이웃 물건(예: 지붕 모서리)이 Gemini 그림에서 어긋났을 때, 상자를 둘로 쪼개면 상자마다 옮김이 달라 이음매가 생긴다 → 상자 하나로 붙이고 그 물건만 되돌린다."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
orig, img = sys.argv[1], sys.argv[2]
pts = [tuple(map(float, p.split(','))) for p in sys.argv[3].split(';')]
feather = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
a = Image.open(orig).convert('RGB'); b = Image.open(img).convert('RGB')
m = Image.new('L', a.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
if feather: m = m.filter(ImageFilter.GaussianBlur(feather))
out = Image.composite(a, b, m); out.save(img)
print('restored', len(pts), 'pts', int((np.array(m) > 0).sum()), 'px')

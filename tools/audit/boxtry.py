#!/usr/bin/env python3
# boxtry.py — 정거장 상자를 그림 위에 그려 눈으로 맞춰 본다(상자 고침 담당 · 그림 고침 뒤 상자 다시 잡기).
# 사용: python3 tools/audit/boxtry.py <과ID> <정거장 번호(0부터)> ['[[x,y,w,h],…]'] [--out 경로] [--pad 140]
#   상자를 안 주면 지금 상자만(파랑). 주면 지금 상자(파랑 점선) + 새 상자(빨강 굵은 선). 다른 정거장의 상자는 회색 가는 선 + 번호.
#   가장자리 눈금의 숫자는 원본(2048×1144) 좌표다.
import json, sys, os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def norm(b): return [] if not b else (b if isinstance(b[0], list) else [b])
def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    opt = {sys.argv[i]: sys.argv[i + 1] for i in range(1, len(sys.argv) - 1) if sys.argv[i].startswith('--')}
    a = [x for x in a if x not in opt.values()]
    lid, k = a[0], int(a[1]); new = norm(json.loads(a[2])) if len(a) > 2 else []
    pad = int(opt.get('--pad', 140))
    d = json.load(open(os.path.join(ROOT, 'lessons', lid + '.json'), encoding='utf-8'))
    im = Image.open(os.path.join(ROOT, 'lesson', 'img', lid + '.webp')).convert('RGB'); W, H = im.size
    cur = norm(d['stops'][k].get('box'))
    for x, y, w, h in new:
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > W or y + h > H: print(f'✕ 그림 밖: {[x, y, w, h]} (그림 {W}×{H})')
    allb = cur + new
    if not allb: allb = [[0, 0, W, H]]
    x0 = max(0, min(b[0] for b in allb) - pad); y0 = max(0, min(b[1] for b in allb) - pad)
    x1 = min(W, max(b[0] + b[2] for b in allb) + pad); y1 = min(H, max(b[1] + b[3] for b in allb) + pad)
    c = im.crop((x0, y0, x1, y1)); sc = min(3.0, 1000 / max(c.size)); c = c.resize((max(1, int(c.width * sc)), max(1, int(c.height * sc))), Image.LANCZOS)
    M = 34; out = Image.new('RGB', (c.width + M, c.height + M), 'white'); out.paste(c, (M, M)); dr = ImageDraw.Draw(out)
    try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    except Exception: f = ImageFont.load_default()
    T = lambda x, y: (M + (x - x0) * sc, M + (y - y0) * sc)
    step = 50 if (x1 - x0) <= 700 else 100
    for gx in range((x0 // step + 1) * step, x1, step): px = T(gx, 0)[0]; dr.line([px, M - 6, px, M], fill='black'); dr.text((px - 12, 6), str(gx), fill='black', font=f)
    for gy in range((y0 // step + 1) * step, y1, step): py = T(0, gy)[1]; dr.line([M - 6, py, M, py], fill='black'); dr.text((1, py - 7), str(gy), fill='black', font=f)
    for j, s in enumerate(d['stops']):
        if j == k: continue
        for x, y, w, h in norm(s.get('box')):
            if x + w < x0 or y + h < y0 or x > x1 or y > y1: continue
            p, q = T(x, y), T(x + w, y + h); dr.rectangle([p, q], outline=(120, 120, 120), width=1); dr.text((max(M, p[0]) + 3, max(M, p[1]) + 2), str(j), fill=(90, 90, 90), font=f)
    for x, y, w, h in cur:
        p, q = T(x, y), T(x + w, y + h)
        if new:
            for t in range(0, int(q[0] - p[0]), 14): dr.line([p[0] + t, p[1], min(q[0], p[0] + t + 7), p[1]], fill=(0, 90, 255), width=2); dr.line([p[0] + t, q[1], min(q[0], p[0] + t + 7), q[1]], fill=(0, 90, 255), width=2)
            for t in range(0, int(q[1] - p[1]), 14): dr.line([p[0], p[1] + t, p[0], min(q[1], p[1] + t + 7)], fill=(0, 90, 255), width=2); dr.line([q[0], p[1] + t, q[0], min(q[1], p[1] + t + 7)], fill=(0, 90, 255), width=2)
        else: dr.rectangle([p, q], outline=(0, 90, 255), width=3)
    for x, y, w, h in new: dr.rectangle([T(x, y), T(x + w, y + h)], outline=(230, 0, 0), width=3)
    path = opt.get('--out') or f'/tmp/boxtry_{lid}_{k}.png'
    os.makedirs(os.path.dirname(path), exist_ok=True); out.save(path)
    print(f'{path}  본 범위 x {x0}~{x1} · y {y0}~{y1}  지금 상자 {cur}  새 상자 {new}')
if __name__ == '__main__': main()

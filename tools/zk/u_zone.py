"""u_zone.py — 생물 덱 통합판용 구역 도구 (zone_kit.py 를 넓힌 것 · 2026-10-13)
zone_kit 과 다른 점: ① 자를 폭을 구역마다 정한다(9:16 이 아니어도 됨) ② 「차지」를 x 범위가 아니라 사각형(x0,y0,x1,y1)으로 —
 같은 x 에 위(사물함)·아래(벤치) 구역이 겹치는 판이 있다 ③ 정합 띠를 구역마다 고른다.
좌표는 모두 바탕 1배(예: 1262×572) 기준. 작업 캔버스는 2배(base2x).

  python3 u_zone.py crop  base2x.png  NAME  CX  W  [--out DIR]      → DIR/crop_NAME.png (2배 조각 = 올릴 그림) + DIR/crop_NAME.json
  python3 u_zone.py compose base2x.png crop_NAME.json zone_out.png  X0,Y0,X1,Y1  out.png  [--band 0.07,0.38] [--feather 12] [--search 14]
        zone_out.png(제미나이 결과)을 조각 크기로 되돌려, 띠에서 ±search 로 정합한 뒤 차지 사각형만 깃털 섞어 붙인다.
        차지 사각형 바깥은 바탕 그대로. 출력: 정합 dx dy mse · 차지 안 바뀐 정도.
"""
import sys, json, argparse
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

def cmd_crop(a):
    B = Image.open(a.base).convert('RGB'); S = 2
    W1, H1 = B.width // S, B.height // S
    w = a.W; x0 = int(round(a.CX - w / 2)); x0 = max(0, min(W1 - w, x0))
    box = [x0, 0, x0 + w, H1]
    B.crop(tuple(v * S for v in box)).save(f'{a.out}/crop_{a.NAME}.png')
    json.dump({'name': a.NAME, 'box': box, 'scale': S}, open(f'{a.out}/crop_{a.NAME}.json', 'w'))
    print('crop', a.NAME, 'box(1배)', box, '올릴 크기', (w * S, H1 * S))

def cmd_compose(a):
    B = np.asarray(Image.open(a.base).convert('RGB')).astype(float); H, W, _ = B.shape
    cj = json.load(open(a.cropjson)); S = cj['scale']; bx0, by0, bx1, by1 = [v * S for v in cj['box']]
    zw, zh = bx1 - bx0, by1 - by0
    Z = np.asarray(Image.open(a.zone).convert('RGB').resize((zw, zh), Image.LANCZOS)).astype(float)
    ox0, oy0, ox1, oy1 = [int(v) * S for v in a.own.split(',')]
    band = [float(v) for v in a.band.split(',')]; ya, yb = int(zh * band[0]), int(zh * band[1])
    xa, xb = int(zw * .04), int(zw * .96); R = a.search; best = None
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            ys, ye = by0 + ya + dy, by0 + yb + dy; xs, xe = bx0 + xa + dx, bx0 + xb + dx
            if ys < 0 or xs < 0 or ye > H or xe > W: continue
            e = np.mean((Z[ya:yb, xa:xb] - B[ys:ye, xs:xe]) ** 2)
            if best is None or e < best[0]: best = (e, dx, dy)
    e, dx, dy = best
    # 편집본을 바탕 좌표에 놓기
    L = B.copy(); cov = np.zeros((H, W))
    ys = np.arange(zh) + by0 + dy; xs = np.arange(zw) + bx0 + dx
    vy = (ys >= 0) & (ys < H); vx = (xs >= 0) & (xs < W)
    L[np.ix_(ys[vy], xs[vx])] = Z[np.ix_(np.where(vy)[0], np.where(vx)[0])]; cov[np.ix_(ys[vy], xs[vx])] = 1
    # 차지 사각형 가면(깃털) — 그림 바깥 테두리 변은 깃털 없이
    F = a.feather * S
    M = np.zeros((H, W)); M[oy0:oy1, ox0:ox1] = 1
    M = gaussian_filter(M, F / 2.0)
    hard = np.zeros((H, W), bool); hard[max(0, oy0 + F):oy1 - F, max(0, ox0 + F):ox1 - F] = True
    M[hard] = 1
    M *= cov
    C = B * (1 - M[..., None]) + L * M[..., None]
    Image.fromarray(np.clip(C, 0, 255).astype('uint8')).save(a.out)
    inside = M > 0.5
    chg = np.sqrt(np.mean((L[inside] - B[inside]) ** 2)) if inside.any() else 0
    print(f'compose {cj["name"]}: 정합 dx={dx/S:+.1f} dy={dy/S:+.1f}(1배) mse={e:.1f}' + ('  ⚠ mse 큼' if e > 300 else '') + f' · 차지 안 바뀐 정도 rms {chg:.1f}')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('crop'); p.add_argument('base'); p.add_argument('NAME'); p.add_argument('CX', type=float); p.add_argument('W', type=int); p.add_argument('--out', default='.')
    p = sp.add_parser('compose'); p.add_argument('base'); p.add_argument('cropjson'); p.add_argument('zone'); p.add_argument('own'); p.add_argument('out')
    p.add_argument('--band', default='0.07,0.38'); p.add_argument('--feather', type=int, default=12); p.add_argument('--search', type=int, default=14)
    a = ap.parse_args(); {'crop': cmd_crop, 'compose': cmd_compose}[a.cmd](a)

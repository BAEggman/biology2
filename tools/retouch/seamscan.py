#!/usr/bin/env python3
"""seamscan.py — 옛 붙임 자국(곧은 가로·세로 경계에서 톤이나 그림이 뚝 끊기는 네모 조각) 찾기.
s36p03 오른쪽 나무 수관에서 「가지가 곧은 선으로 잘린 네모 조각 + 줄 둘」이 9/17 전수 감사를 지나쳐 남아 있던 것(10/1 발견) 때문에 만듦.

행 y 와 y+1 사이(또는 열 x 와 x+1 사이)를 경계 후보로 보고:
  위 덩이(y−3..y−1) 평균과 아래 덩이(y+2..y+4) 평균의 차 S — 두 덩이가 저마다 매끈(덩이 안 세로 변화 < SM)한 화소에서만 —
  |S| ≥ ST 이고 부호가 같은 화소가 K px 창 안에 FR 이상이면 「곧은 톤 단절」 후보.
  그림 자체의 곧은 선(땅선·선반·탁자 끝)도 걸리므로 결과는 **눈으로 훑을 후보 목록**이다(자동 판정 아님).
사용: python3 seamscan.py OUT.json [pid ...]   (없으면 tools/blind/png 전부)
      python3 seamscan.py --sheet OUT.json SHEET_PREFIX [N]   (점수 높은 N 개를 조각 모음판으로)"""
import sys, os, glob, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

K, ST, SM, FR = 72, 2.0, 2.0, 0.55


def scan_axis(L):
    B = ndi.gaussian_filter(L, 0.7)
    h, w = B.shape
    out = []
    ys = np.arange(3, h - 5)
    up = (B[ys - 3] + B[ys - 2] + B[ys - 1]) / 3
    dn = (B[ys + 2] + B[ys + 3] + B[ys + 4]) / 3
    S = dn - up
    smooth = (np.abs(B[ys - 1] - B[ys - 3]) < SM) & (np.abs(B[ys + 4] - B[ys + 2]) < SM)
    pos = (smooth & (S >= ST)).astype(np.float32)
    neg = (smooth & (S <= -ST)).astype(np.float32)
    fp = ndi.uniform_filter1d(pos, K, axis=1, mode='constant')
    fn = ndi.uniform_filter1d(neg, K, axis=1, mode='constant')
    f = np.maximum(fp, fn)
    best = f.max(axis=1)
    for i in np.argsort(-best):
        if best[i] < FR:
            break
        y = int(ys[i])
        # 이미 고른 줄 ±4 안이면 건너뜀
        if any(abs(y - o['pos']) <= 4 for o in out):
            continue
        row = f[i]
        # 문턱을 넘는 가장 긴 구간
        on = row >= FR
        lab, n = ndi.label(on)
        segs = []
        for j in range(1, n + 1):
            xs = np.nonzero(lab == j)[0]
            segs.append((xs.min() - K // 2, xs.max() + K // 2))
        a, b = max(segs, key=lambda s: s[1] - s[0])
        a, b = max(0, int(a)), min(w - 1, int(b))
        sgn = 1 if fp[i, row.argmax()] >= fn[i, row.argmax()] else -1
        mag = float(np.abs(S[i, a:b + 1][(pos[i, a:b + 1] + neg[i, a:b + 1]) > 0]).mean()) if (pos[i, a:b + 1] + neg[i, a:b + 1]).any() else 0.0
        out.append(dict(pos=y, a=a, b=b, len=b - a, score=float(best[i]), sign=sgn, mag=round(mag, 1)))
        if len(out) >= 4:
            break
    return out


def scan(path):
    L = np.asarray(Image.open(path).convert('L')).astype(np.float32)
    res = []
    for o in scan_axis(L):
        o['axis'] = 'h'; res.append(o)
    for o in scan_axis(L.T.copy()):
        o['axis'] = 'v'; res.append(o)
    return res


def sheet(js, prefix, N=60):
    items = []
    for pid, lst in js.items():
        for o in lst:
            items.append((o['score'] * min(1.0, o['len'] / 160.0), pid, o))
    items.sort(key=lambda t: -t[0])
    items = items[:N]
    per = 12
    for s in range(0, len(items), per):
        chunk = items[s:s + per]
        tiles = []
        for sc, pid, o in chunk:
            im = Image.open('tools/blind/png/%s.png' % pid).convert('RGB')
            W, H = im.size
            if o['axis'] == 'h':
                cx = (o['a'] + o['b']) // 2; cy = o['pos']
            else:
                cx = o['pos']; cy = (o['a'] + o['b']) // 2
            bw, bh = 240, 150
            x0 = min(max(0, cx - bw // 2), W - bw); y0 = min(max(0, cy - bh // 2), H - bh)
            t = im.crop((x0, y0, x0 + bw, y0 + bh)).resize((bw * 2, bh * 2), Image.LANCZOS)
            d = ImageDraw.Draw(t)
            # 경계 자리 표시: 조각 바깥 테두리에 작은 눈금만(그림 위에는 안 그림)
            if o['axis'] == 'h':
                yy = (o['pos'] - y0) * 2 + 1
                d.line([(0, yy), (10, yy)], fill=(255, 0, 0), width=3); d.line([(bw * 2 - 11, yy), (bw * 2 - 1, yy)], fill=(255, 0, 0), width=3)
            else:
                xx = (o['pos'] - x0) * 2 + 1
                d.line([(xx, 0), (xx, 10)], fill=(255, 0, 0), width=3); d.line([(xx, bh * 2 - 11), (xx, bh * 2 - 1)], fill=(255, 0, 0), width=3)
            tiles.append((t, '%s %s%d [%d..%d] s%.2f m%.1f' % (pid, o['axis'], o['pos'], o['a'], o['b'], o['score'], o['mag'])))
        cols = 3
        rows = (len(tiles) + cols - 1) // cols
        S = Image.new('RGB', (cols * 490, rows * 325), 'white')
        d = ImageDraw.Draw(S)
        for k, (t, lab) in enumerate(tiles):
            X = (k % cols) * 490; Y = (k // cols) * 325
            S.paste(t, (X, Y + 18)); d.text((X + 2, Y + 2), lab, fill=(0, 0, 0))
        S.save('%s_%02d.png' % (prefix, s // per))
        print('%s_%02d.png' % (prefix, s // per), [c[1] for c in chunk])


if __name__ == '__main__':
    if sys.argv[1] == '--sheet':
        js = json.load(open(sys.argv[2]))
        sheet(js, sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 60)
    else:
        outp = sys.argv[1]
        pids = sys.argv[2:] or [os.path.basename(p)[:-4] for p in sorted(glob.glob('tools/blind/png/*.png'))]
        js = {}
        for pid in pids:
            r = scan('tools/blind/png/%s.png' % pid)
            if r:
                js[pid] = r
        json.dump(js, open(outp, 'w'), ensure_ascii=False, indent=0)
        n = sum(len(v) for v in js.values())
        print('panels with candidates', len(js), 'candidates', n)

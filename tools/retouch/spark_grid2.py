#!/usr/bin/env python3
"""spark_grid2.py — 반짝이 표식 모음판(2×2)을 **별 자리·크기가 판마다 다를 때** 만들고 되옮긴다(`spark_grid_paste.py` 의 일반판).
넓은 판(1024×506 · 559 · 572 · 765 · 412 · 338 · 1526)은 별이 오른쪽·아래에서 같은 거리 m(≈ 84..124) · R ≈ 14..22 에 있다
(2026-10-01 훑기 — 제미나이 출력 크기에 따라 자리가 다름). 1024 정사각 판의 (903.5, 903.5) · R 25.4 별과 같은 모양(p 0.69).

  make  GRID.png TILES.json pid@cx,cy,R ×(≤9)   — 판마다 별을 가운데 둔 C = round(200·R/25.4) 정사각 조각(그림 안으로 밀어 넣음)을
                                                  넷 이하면 512 로 키워 2×2, 다섯~아홉이면 341 로 키워 3×3 모음판을 만들고, 조각 상자를 TILES.json 에 적는다.
  paste GRID_OUT.png TILES.json OUTDIR          — 칸마다 C 로 줄여 어긋남(±4, 별 밖 제곱차)을 재고, 판마다 다시 맞춘 별(spark_clone.fit_geometry,
                                                  ±1)을 4px 넓힌 자리만 되옮김 · 둘레 4px 고리 차를 σ3 로 고르게 해 라플라스 막으로 톤 맞춤 · σ1.5 섞음.
입력 판은 tools/blind/png/<pid>.png (무손실 설치본)."""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spark_clone import star_mask_full, fit_geometry, membrane


def make(grid_path, tiles_path, specs, n=2):
    T = 1024 // n
    G = Image.new('RGB', (1024, 1024), (255, 255, 255))
    tiles = []
    for k, sp in enumerate(specs):
        pid, at = sp.split('@')
        cx, cy, R = (float(v) for v in at.split(','))
        im = Image.open('tools/blind/png/%s.png' % pid).convert('RGB')
        W, H = im.size
        C = int(round(200 * R / 25.4))
        x0 = int(round(cx - C / 2)); y0 = int(round(cy - C / 2))
        x0 = min(max(0, x0), W - C); y0 = min(max(0, y0), H - C)
        G.paste(im.crop((x0, y0, x0 + C, y0 + C)).resize((T, T), Image.LANCZOS), ((k % n) * T, (k // n) * T))
        tiles.append(dict(pid=pid, k=k, n=n, box=[x0, y0, x0 + C, y0 + C], cx=cx, cy=cy, R=R))
    G.save(grid_path)
    json.dump(tiles, open(tiles_path, 'w'), indent=1)
    print('grid', grid_path, [t['pid'] for t in tiles])


def paste(grid_path, tiles_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    grid = Image.open(grid_path).convert('RGB')
    assert grid.size == (1024, 1024), grid.size
    for t in json.load(open(tiles_path)):
        pid, k = t['pid'], t['k']
        n = t.get('n', 2); TT = 1024 // n
        x0, y0, x1, y1 = t['box']; C = x1 - x0
        full = np.asarray(Image.open('tools/blind/png/%s.png' % pid).convert('RGB')).astype(np.float64)
        H, W = full.shape[:2]
        tile = grid.crop(((k % n) * TT, (k // n) * TT, (k % n) * TT + TT, (k // n) * TT + TT)).resize((C, C), Image.LANCZOS)
        T = np.asarray(tile).astype(np.float64)
        O = full[y0:y1, x0:x1]
        L = full.mean(axis=2)
        c, R, cx, cy = fit_geometry(L, t['R'], t['cx'], t['cy'], span=1.0)
        M = star_mask_full(R, cx, cy, H, W)[y0:y1, x0:x1]
        away = ~ndi.binary_dilation(M > 0.01, iterations=6)
        e8 = max(4, C // 25)
        away[:e8, :] = away[-e8:, :] = False; away[:, :e8] = away[:, -e8:] = False
        best = None
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                Ts = np.roll(np.roll(T, dy, axis=0), dx, axis=1)
                e = ((Ts - O)[away] ** 2).mean()
                if best is None or e < best[0]:
                    best = (e, dx, dy)
        e, dx, dy = best
        Ts = np.roll(np.roll(T, dy, axis=0), dx, axis=1)
        mask = ndi.binary_dilation(M > 0.01, iterations=4)
        D = O - Ts
        rb = ndi.binary_dilation(mask, iterations=4) & ~mask
        num = np.stack([ndi.gaussian_filter(D[..., q] * rb, 3.0) for q in range(3)], axis=2)
        den = ndi.gaussian_filter(rb.astype(float), 3.0)[..., None]
        corr = membrane(num / np.maximum(den, 1e-6), mask)
        src = Ts.copy(); src[mask] += corr[mask]
        w = np.maximum(ndi.gaussian_filter(mask.astype(float), 1.5), mask.astype(float))
        out = full.copy()
        out[y0:y1, x0:x1] = O * (1 - w[..., None]) + src * w[..., None]
        out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
        Image.fromarray(out).save(os.path.join(outdir, pid + '.png'))
        hb = int(R * 2.6)
        bx = (int(cx) - hb, int(cy) - hb, int(cx) + hb, int(cy) + hb)
        a_img = Image.fromarray(full.astype(np.uint8)).crop(bx).resize((300, 300), Image.LANCZOS)
        b_img = Image.fromarray(out).crop(bx).resize((300, 300), Image.LANCZOS)
        cmp_ = Image.new('RGB', (610, 300), 'white'); cmp_.paste(a_img, (0, 0)); cmp_.paste(b_img, (310, 0))
        cmp_.save(os.path.join(outdir, pid + '_cmp.png'))
        print('%-8s tile %d  shift (%d, %d) rms %.1f  R %.2f c (%.1f, %.1f)  tone %s' % (pid, k, dx, dy, np.sqrt(e), R, cx, cy, corr[mask].mean(axis=0).round(1)))


if __name__ == '__main__':
    if sys.argv[1] == 'make':
        specs = sys.argv[4:]
        n = 2 if len(specs) <= 4 else 3
        make(sys.argv[2], sys.argv[3], specs[:n * n], n)
    elif sys.argv[1] == 'paste':
        paste(sys.argv[2], sys.argv[3], sys.argv[4])

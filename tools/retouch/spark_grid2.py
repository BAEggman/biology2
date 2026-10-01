#!/usr/bin/env python3
"""spark_grid2.py — 반짝이 표식 모음판(2×2)을 **별 자리·크기가 판마다 다를 때** 만들고 되옮긴다(`spark_grid_paste.py` 의 일반판).
넓은 판(1024×506 · 559 · 572 · 765 · 412 · 338 · 1526)은 별이 오른쪽·아래에서 같은 거리 m(≈ 84..124) · R ≈ 14..22 에 있다
(2026-10-01 훑기 — 제미나이 출력 크기에 따라 자리가 다름). 1024 정사각 판의 (903.5, 903.5) · R 25.4 별과 같은 모양(p 0.69).

  make  GRID.png TILES.json pid@cx,cy,R ×(≤9)   — 판마다 별을 가운데 둔 C = round(200·R/25.4) 정사각 조각(그림 안으로 밀어 넣음)을
                                                  넷 이하면 512 로 키워 2×2, 다섯~아홉이면 341 로 키워 3×3 모음판을 만들고, 조각 상자를 TILES.json 에 적는다.
  paste GRID_OUT.png TILES.json OUTDIR          — 칸마다 C 로 줄여 어긋남(±4, 테두리 띠 제곱차)을 재고, 제미나이 톤을 맞춘 뒤(조용한 화소 σ15)
                                                  **원본이 더 밝은 곳**(σ1.5 밝기 차 > 7 · 60px 넘는 덩어리 · 가운데 76% 에 걸침 = 지운 흰 별)을
                                                  메워 4px 넓힌 자리만 되옮김 · 둘레 4px 고리 차를 라플라스 막으로 톤 맞춤 · σ1.5 섞음.
                                                  (넓은 판은 별 자리가 「오른쪽·아래 같은 거리」가 아니라 판마다 달라 — s42p01 은 (932, 487) — 추정 자리 대신 지운 자리로 잡는다.
                                                   조각은 C = max(170, 200·R/25.4) 로 넉넉히.)
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
        C = max(170, int(round(200 * R / 25.4)))
        C = min(C, W, H)
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
        # 어긋남(±4): 가운데 70% 밖(별이 없을 테두리 띠)의 제곱차 최소
        yy_, xx_ = np.mgrid[0:C, 0:C]
        e8 = max(4, C // 25)
        rim = ((xx_ < C * 0.15) | (xx_ > C * 0.85) | (yy_ < C * 0.15) | (yy_ > C * 0.85))
        rim[:e8, :] = rim[-e8:, :] = False; rim[:, :e8] = rim[:, -e8:] = False
        best = None
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                Ts = np.roll(np.roll(T, dy, axis=0), dx, axis=1)
                e = ((Ts - O)[rim] ** 2).mean()
                if best is None or e < best[0]:
                    best = (e, dx, dy)
        e, dx, dy = best
        Ts = np.roll(np.roll(T, dy, axis=0), dx, axis=1)
        # 제미나이의 판 전체 톤 차를 먼저 맞춘 뒤(조용한 화소의 O − T 를 σ15 로 번짐), 원본이 더 밝은 곳(= 지운 흰 별)을 찾는다
        d0 = ndi.gaussian_filter(np.abs(O - Ts).mean(axis=2), 2.0)
        calm = d0 < 10
        den = ndi.gaussian_filter(calm.astype(float), 15)
        Tt = Ts.copy()
        for q in range(3):
            Tt[..., q] += ndi.gaussian_filter((O[..., q] - Ts[..., q]) * calm, 15) / np.maximum(den, 1e-3)
        Dl = ndi.gaussian_filter(O.mean(axis=2) - Tt.mean(axis=2), 1.5)
        cand = Dl > 7
        lab_, n_ = ndi.label(cand)
        keep = np.zeros_like(cand)
        cen = (xx_ > C * 0.12) & (xx_ < C * 0.88) & (yy_ > C * 0.12) & (yy_ < C * 0.88)
        for i_ in range(1, n_ + 1):
            comp = lab_ == i_
            if comp.sum() >= 60 and (comp & cen).any():
                keep |= comp
        mask = ndi.binary_fill_holes(ndi.binary_closing(keep, iterations=3))
        mask = ndi.binary_dilation(mask, iterations=4)
        R = cx = cy = float('nan')
        D = O - Tt
        rb = ndi.binary_dilation(mask, iterations=4) & ~mask
        num = np.stack([ndi.gaussian_filter(D[..., q] * rb, 3.0) for q in range(3)], axis=2)
        den = ndi.gaussian_filter(rb.astype(float), 3.0)[..., None]
        corr = membrane(num / np.maximum(den, 1e-6), mask) if mask.any() else np.zeros_like(O)
        src = Tt.copy(); src[mask] += corr[mask]
        w = np.maximum(ndi.gaussian_filter(mask.astype(float), 1.5), mask.astype(float))
        out = full.copy()
        out[y0:y1, x0:x1] = O * (1 - w[..., None]) + src * w[..., None]
        out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
        Image.fromarray(out).save(os.path.join(outdir, pid + '.png'))
        bx = (x0, y0, x1, y1)
        a_img = Image.fromarray(full.astype(np.uint8)).crop(bx).resize((300, 300), Image.LANCZOS)
        b_img = Image.fromarray(out).crop(bx).resize((300, 300), Image.LANCZOS)
        cmp_ = Image.new('RGB', (610, 300), 'white'); cmp_.paste(a_img, (0, 0)); cmp_.paste(b_img, (310, 0))
        cmp_.save(os.path.join(outdir, pid + '_cmp.png'))
        ys_, xs_ = np.nonzero(mask)
        bb = (int(xs_.min()) + x0, int(ys_.min()) + y0, int(xs_.max()) + x0, int(ys_.max()) + y0) if mask.any() else None
        print('%-8s tile %d  shift (%d, %d) rms %.1f  star px %d bbox %s  tone %s' % (pid, k, dx, dy, np.sqrt(e), int(mask.sum()), bb, (corr[mask].mean(axis=0).round(1) if mask.any() else None)))


if __name__ == '__main__':
    if sys.argv[1] == 'make':
        specs = sys.argv[4:]
        n = 2 if len(specs) <= 4 else 3
        make(sys.argv[2], sys.argv[3], specs[:n * n], n)
    elif sys.argv[1] == 'paste':
        paste(sys.argv[2], sys.argv[3], sys.argv[4])

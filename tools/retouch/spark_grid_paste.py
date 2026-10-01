#!/usr/bin/env python3
"""spark_grid_paste.py — 제미나이가 반짝이 표식을 지운 2×2 모음판(`tools/prompts/spark_grid_지우기_v1.md`)에서
칸마다 별 자리만 원래 판에 되옮긴다. 별이 물건 위에 걸친 판(장화 끈 · 양동이 테 · 바짓단 · 화분 · 벽 위 끝 …) 용 —
평평하거나 결이 되풀이되는 판은 `spark_clone.py`.

모음판: 판마다 (804, 804, 1004, 1004) 를 512 로 키워 칸 순서(왼위 · 오위 · 왼아래 · 오아래)로 놓은 1024.
  ① 칸을 200 으로 줄이고(LANCZOS) 원본 조각과 어긋남을 잰다 — 별(넓힘 6) 밖 화소의 제곱차가 가장 작은 정수 어긋남(±4).
  ② 덮을 곳 = 판마다 다시 맞춘 별(M > 0.01, spark_clone 의 fit_geometry)을 4px 넓힘.
  ③ 톤 맞춤 = 덮을 곳 둘레 4px 고리의 (원본 − 제미나이) 차를 σ3 로 고르게 해 라플라스 막으로 이어 더함(spark_clone 의 membrane).
  ④ σ1.5 섞음(안은 다 바꿈).
사용: python3 spark_grid_paste.py GRID.png OUTDIR pid1 pid2 pid3 pid4   (입력 tools/blind/png/<pid>.png — 무손실 설치본; 빈 칸은 -)"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spark_clone import star_mask_full, fit_geometry, membrane

X0, Y0, C = 804, 804, 200


def paste_one(grid, k, pid, outdir):
    full = np.asarray(Image.open('tools/blind/png/%s.png' % pid).convert('RGB')).astype(np.float64)
    tile = grid.crop(((k % 2) * 512, (k // 2) * 512, (k % 2) * 512 + 512, (k // 2) * 512 + 512)).resize((C, C), Image.LANCZOS)
    T = np.asarray(tile).astype(np.float64)
    O = full[Y0:Y0 + C, X0:X0 + C]
    L = full.mean(axis=2)
    c, R, cx, cy = fit_geometry(L)
    M = star_mask_full(R, cx, cy)[Y0:Y0 + C, X0:X0 + C]
    away = ~ndi.binary_dilation(M > 0.01, iterations=6)
    away[:8, :] = away[-8:, :] = False; away[:, :8] = away[:, -8:] = False
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
    Ds = num / np.maximum(den, 1e-6)
    corr = membrane(Ds, mask)
    src = Ts.copy()
    src[mask] += corr[mask]
    w = np.maximum(ndi.gaussian_filter(mask.astype(float), 1.5), mask.astype(float))
    Onew = O * (1 - w[..., None]) + src * w[..., None]
    out = full.copy()
    out[Y0:Y0 + C, X0:X0 + C] = Onew
    out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(outdir, pid + '.png'))
    a_img = Image.fromarray(full.astype(np.uint8)).crop((840, 840, 970, 970)).resize((300, 300), Image.LANCZOS)
    b_img = Image.fromarray(out).crop((840, 840, 970, 970)).resize((300, 300), Image.LANCZOS)
    cmp_ = Image.new('RGB', (610, 300), 'white'); cmp_.paste(a_img, (0, 0)); cmp_.paste(b_img, (310, 0))
    cmp_.save(os.path.join(outdir, pid + '_cmp.png'))
    print('%-8s tile %d  shift (%d, %d) rms %.1f  R %.2f c (%.1f, %.1f)  tone %s' % (pid, k, dx, dy, np.sqrt(e), R, cx, cy, corr[mask].mean(axis=0).round(1)))


if __name__ == '__main__':
    gp, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    grid = Image.open(gp).convert('RGB')
    assert grid.size == (1024, 1024), grid.size
    for k, pid in enumerate(sys.argv[3:7]):
        if pid != '-':
            paste_one(grid, k, pid, outdir)

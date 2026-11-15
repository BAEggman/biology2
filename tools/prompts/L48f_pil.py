#!/usr/bin/env python3
# L48f_pil.py <in.png> <out.png> — L48f 「짚단 부부의 혼례와 이혼」 PIL 손질(2026-11-15 · Opus 5.5)
#  ① 이발사 — 끝 바꿔 꽂기(교차): 이발사가 쥔 잘린 끝(하늘색)을 남색으로 · 남색 신랑의 왼쪽 삐친 끝을 하늘색으로
#     = 「신랑 끝엔 이미 하늘색이 꽂혔고, 신랑에게서 자른 남색 끝을 신부 쪽으로 꽂는 중」(비자매끼리 맞바꿈 · 재조합)
#  빛깔은 밝기 순위로 옮긴다(검은 윤곽 · 살빛 · 가위 손잡이는 그대로 — 푸른 기가 센 짚만).
import sys
import numpy as np
from PIL import Image, ImageDraw

NAVY = [(30, (30, 38, 62)), (55, (45, 55, 79)), (80, (69, 83, 112)), (115, (108, 117, 136))]
SKY = [(110, (100, 128, 140)), (150, (139, 168, 179)), (195, (179, 210, 222)), (228, (207, 237, 247))]


def ramp(stops, L):
    xs = np.array([s[0] for s in stops], float); cs = np.array([s[1] for s in stops], float)
    return np.stack([np.interp(L, xs, cs[:, k]) for k in range(3)], -1)


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def poly_mask(size, pts):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).polygon(pts, fill=255); return np.array(m) > 0


def soft_swap(a, pts, to, feather=2.0):
    """다발 끝 빛깔 바꾸기 — 다각형(자르는 선 + 다발 밖까지 넉넉히)을 흐려 가장자리를 부드럽게 섞는다. to = 'sky' | 'navy'."""
    from PIL import ImageFilter
    m = Image.new('L', (a.shape[1], a.shape[0]), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    w = np.array(m.filter(ImageFilter.GaussianBlur(feather))).astype(float)[..., None] / 255
    b = a.copy()
    n = (navy_to_sky if to == 'sky' else sky_to_navy)(b, [(0, 0), (a.shape[1], 0), (a.shape[1], a.shape[0]), (0, a.shape[0])], dry=w[..., 0] > 0.01)
    a[:] = a * (1 - w) + b * w
    return n


def navy_to_sky(a, pts, dry=None):
    """남색 짚 → 하늘색 짚(밝기 35~110 → 110~228). 윤곽(밝기 < 30)은 그대로."""
    m = poly_mask((a.shape[1], a.shape[0]), pts) if dry is None else dry
    L = lum(a); blue = (a[..., 2] - a[..., 0] > 18) & (L >= 30) & (L < 130)
    sel = m & blue
    t = np.clip((L[sel] - 30) / (115 - 30), 0, 1)
    a[sel] = ramp(SKY, 110 + t * (228 - 110))
    return int(sel.sum())


def sky_to_navy(a, pts, dry=None):
    """하늘색 짚 → 남색 짚(밝기 95~250 → 40~112). 윤곽 · 살빛 · 갈색은 그대로."""
    m = poly_mask((a.shape[1], a.shape[0]), pts) if dry is None else dry
    L = lum(a); blue = (a[..., 2] - a[..., 0] > 14) & (L >= 95)
    sel = m & blue
    t = np.clip((L[sel] - 95) / (250 - 95), 0, 1)
    a[sel] = ramp(NAVY, 40 + t * (112 - 40))
    return int(sel.sum())


def inpaint(a, box):
    """작은 자국 지우기(둘레 빛으로 메움)."""
    import cv2
    x0, y0, x1, y1 = box
    u = np.clip(a, 0, 255).astype(np.uint8); m = np.zeros(u.shape[:2], np.uint8); m[y0:y1, x0:x1] = 255
    a[:] = cv2.inpaint(u, m, 5, cv2.INPAINT_TELEA).astype(float)


def strands(a):
    """③ 세사기 바닥의 가는 실 — Gemini 가 잿빛으로 그려 두 빛깔이 안 갈렸다(일치 검사 1회 △) → 어두운 가닥은 남색, 밝은 가닥은 하늘색으로."""
    m = poly_mask((a.shape[1], a.shape[0]), [(15, 805), (195, 805), (195, 836), (392, 840), (392, 975), (15, 975)])
    L = lum(a); grey = (a[..., 2] >= a[..., 0] + 3) & (L >= 50)
    dark = m & grey & (L < 112); light = m & grey & (L >= 112)
    a[dark] = ramp(NAVY, 40 + (np.clip((L[dark] - 50) / 62, 0, 1)) * 70)
    a[light] = ramp(SKY, 125 + (np.clip((L[light] - 112) / 110, 0, 1)) * 103)
    return int(dark.sum()), int(light.sum())


def strip_marks(a, polys, max_area=40, max_side=14):
    """⑤ 멍석 띠 결의 잔 점 · 짧은 금 지우기 — 가까이 보면 「손글씨 줄」처럼 읽혔다(일치 검사 2회 (가)).
    띠 빛(누런 짚: g/r > 0.80 · 밝음)에 둘러싸인 작은 어두운 덩이만(긴 윤곽 · 감긴 띠 사이 금은 덩이가 커서 남는다)."""
    import cv2
    u = np.clip(a, 0, 255).astype(np.uint8); H, W = u.shape[:2]
    reg = np.zeros((H, W), np.uint8)
    for pts in polys:
        cv2.fillPoly(reg, [np.array(pts, np.int32)], 255)
    f = u.astype(float); L = lum(f); gr = f[..., 1] / np.maximum(f[..., 0], 1)
    stripc = (gr > 0.80) & (L > 140) & (f[..., 0] > f[..., 2] + 40)
    dark = (L < 150) & (reg > 0) & ~stripc
    n, lab, stt, _ = cv2.connectedComponentsWithStats(dark.astype(np.uint8), 8)
    mask = np.zeros((H, W), np.uint8); k = 0
    ker = np.ones((5, 5), np.uint8)
    for i in range(1, n):
        x, y, w, h, ar = stt[i]
        if ar > max_area or max(w, h) > max_side: continue
        comp = (lab[y:y + h, x:x + w] == i).astype(np.uint8)
        y0, y1, x0, x1 = max(0, y - 3), min(H, y + h + 3), max(0, x - 3), min(W, x + w + 3)
        cm = np.zeros((y1 - y0, x1 - x0), np.uint8); cm[y - y0:y - y0 + h, x - x0:x - x0 + w] = comp
        ring = (cv2.dilate(cm, ker) > 0) & (cm == 0)
        if ring.sum() == 0 or stripc[y0:y1, x0:x1][ring].mean() < 0.7: continue
        mask[y0:y1, x0:x1][cv2.dilate(cm, np.ones((3, 3), np.uint8)) > 0] = 255; k += 1
    a[:] = cv2.inpaint(u, mask, 3, cv2.INPAINT_TELEA).astype(float)
    return k


def main(src, dst):
    im = Image.open(src).convert('RGB'); a = np.array(im).astype(float)
    n1 = sky_to_navy(a, [(528, 446), (531, 404), (545, 372), (572, 368), (600, 383), (592, 410), (568, 440), (552, 452)])
    n2 = navy_to_sky(a, [(424, 478), (452, 470), (462, 488), (458, 540), (428, 545), (418, 512)])
    print('이발사: 쥔 끝 → 남색', n1, '· 신랑 왼쪽 끝 → 하늘색', n2)
    inpaint(a, (1543, 835, 1556, 851))      # ② 앞 하늘색 짚단 그림자 속 옛 장화 윤곽 토막(ZF 상자 밖 칸막이 줄에 남음)
    # ③ 세사기 실의 두 빛깔은 Gemini 구역 편집 ZS 로 했다(strands() 는 쓰지 않음 — 잿빛을 PIL 로 물들이면 탁했다)
    # ④ 춤판 X 짚단 넷 — 안쪽(점선 쪽) 위 다발 끝에 짝의 빛깔(교차 뒤 재조합 염색분체 · 일치 검사 1회 (다) 「춤판 짚단에 교차 흔적이 없다」)
    t = [soft_swap(a, [(1506, 452), (1556, 435), (1566, 400), (1540, 397), (1506, 397)], 'sky', 2.5),                  # 뒤 남색 X 의 안쪽(오른쪽) 위 다발 끝 → 하늘색(위 397 — 뒤 구경꾼 푸른 바지 피함)
         soft_swap(a, [(1610, 446), (1663, 462), (1653, 400), (1612, 400)], 'navy', 2.5),                                  # 뒤 하늘색 X 의 안쪽(왼쪽) 위 다발 끝 → 남색
         soft_swap(a, [(1522, 720), (1582, 708), (1584, 655), (1532, 655), (1518, 672)], 'navy', 2.5),                     # 앞 하늘색 X 의 안쪽(오른쪽) 위 다발 끝 → 남색
         soft_swap(a, [(1608, 712), (1668, 726), (1666, 686), (1660, 664), (1640, 652), (1608, 656)], 'sky', 2.5)]        # 앞 남색 X 의 안쪽(왼쪽) 위 다발 끝 → 하늘색(오른쪽 1666 — 모자 피함)
    print('춤판 X 끝', t)
    k = strip_marks(a, [[(140, 640), (430, 640), (430, 735), (210, 735), (205, 775), (140, 775)],      # 할머니의 띠 · 두루마리
                        [(425, 500), (610, 500), (610, 800), (425, 800)],                              # 이발사 곁 칭칭 감긴 띠
                        [(520, 660), (905, 660), (905, 895), (520, 895)]])                             # 바닥에 풀린 띠
    print('띠 잔 점 지움', k)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

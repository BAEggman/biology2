#!/usr/bin/env python3
# L53a_pil1.py — 바탕(s1) + E1 · E2 뒤의 PIL 손질: 덤으로 매달린 구슬 둘 지움 · 금빛 덩이 셋을 콜레스테롤 타일(고리 넷 문장)로 · 언 곳 타일 둘레 안 언 자리 · 이웃 부교의 하늘색 Y 집게
import sys, math, cv2, numpy as np
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
im = cv2.imread(src)
def erase_rows(x0, x1, y0, y1, lw=4, rw=4, side=None):
    """x0..x1 · y0..y1 을 왼 · 오른 깨끗한 기둥 빛으로 줄마다 이어 메운다(side='R' 이면 오른쪽 빛만)."""
    for y in range(y0, y1):
        L = np.median(im[y, x0 - lw:x0].astype(float), axis=0); R = np.median(im[y, x1:x1 + rw].astype(float), axis=0)
        if side == 'R': L = R
        for x in range(x0, x1):
            t = (x - x0 + 0.5) / (x1 - x0); im[y, x] = (L * (1 - t) + R * t).astype(np.uint8)
# ① 덤으로 매달린 작은 구슬 묶음 둘(파란 머리 1616 · 1762 아래) — 주변부 단백질은 1329 아래 구슬 공 하나만
erase_rows(1588, 1646, 772, 856)
# 묶음 아래로 늘어진 실 끝(등불 빛 속) — 어두운 실만 골라 둘레 빛으로 메움
reg = im[856:892, 1592:1648].astype(int); med = np.median(reg.reshape(-1, 3), axis=0)
mk = ((med.sum() - reg.sum(axis=2)) > 70).astype(np.uint8) * 255; mk = cv2.dilate(mk, np.ones((5, 5), np.uint8))
full = np.zeros(im.shape[:2], np.uint8); full[856:892, 1592:1648] = mk
im = cv2.inpaint(im, full, 5, cv2.INPAINT_TELEA)
erase_rows(1744, 1781, 772, 850)
pil = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
S = 4
def tile(cx, cy, w=50, h=78):
    """금빛 타일 + 고리 넷(육각 셋 + 오각 하나) 문장 — 세로로 세워 그린다."""
    x0, y0 = cx - w // 2 - 6, cy - h // 2 - 6; W, H = w + 12, h + 12
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def T(p): return ((p[0] - x0) * S, (p[1] - y0) * S)
    bx0, by0, bx1, by1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    d.rounded_rectangle([T((bx0, by0)), T((bx1, by1))], radius=6 * S, fill=(22, 20, 18, 255))
    d.rounded_rectangle([T((bx0 + 3, by0 + 3)), T((bx1 - 3, by1 - 3))], radius=4 * S, fill=(244, 188, 44, 255))
    d.polygon([T((bx0 + 3, by0 + 22)), T((bx0 + 22, by0 + 3)), T((bx0 + 30, by0 + 3)), T((bx0 + 3, by0 + 30))], fill=(252, 216, 110, 255))   # 빗금 광택
    # 고리 넷: steroid.py 의 꼴을 90° 돌려 세움(가로 ↔ 세로)
    r = 9.4; s3 = math.sqrt(3)
    def hexv(ax, ay): return [(ax + r * math.cos(math.radians(a)), ay - r * math.sin(math.radians(a))) for a in (90, 30, -30, -90, -150, 150)]
    A = (0.0, 0.0); B = (s3 * r, 0.0); C = (1.5 * s3 * r, -1.5 * r)
    rings = [hexv(*A), hexv(*B), hexv(*C)]
    e0x = C[0] + s3 / 2 * r; ap = r / (2 * math.tan(math.radians(36))); R5 = r / (2 * math.sin(math.radians(36)))
    D = (e0x + ap, C[1]); rings.append([(D[0] + R5 * math.cos(math.radians(a)), D[1] - R5 * math.sin(math.radians(a))) for a in (144, 72, 0, -72, -144)])
    pts = [p for g in rings for p in g]; mx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2; my = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    def rot(p): return (cx - (p[1] - my), cy + (p[0] - mx))      # 90° 돌림
    seen = set()
    for g in rings:
        for i in range(len(g)):
            p, q = g[i], g[(i + 1) % len(g)]; k = tuple(sorted([(round(p[0], 1), round(p[1], 1)), (round(q[0], 1), round(q[1], 1))]))
            if k in seen: continue
            seen.add(k); d.line([T(rot(p)), T(rot(q))], fill=(96, 52, 8, 255), width=int(3.0 * S))
        for p in g:
            x, y = T(rot(p)); rr = 1.5 * S; d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(96, 52, 8, 255))
    lay = lay.resize((W, H), Image.LANCZOS); pil.paste(lay, (x0, y0), lay)
def halo(cx, cy, rx, ry):
    """언 곳의 타일 둘레: 얼지 않은(노란) 자리 — 선은 남기고 빛깔만 버터빛으로."""
    a = np.array(pil).astype(np.float32); H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]; dd = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    m = np.clip((1.15 - dd) / 0.55, 0, 1); m[(yy < 449) | (yy > 696)] = 0      # 띠 안에서만
    m[xx > 314] = 0                                                              # 소 다리는 물들이지 않는다
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2.0)
    gray = a.mean(axis=2, keepdims=True) / 238.0; butter = np.array([250, 218, 97], np.float32)
    tint = np.clip(butter * np.clip(gray, 0, 1.06), 0, 255)
    out = a * (1 - m[..., None]) + tint * m[..., None]
    return Image.fromarray(out.astype(np.uint8))
pil = halo(268, 500, 80, 62)
tile(611, 501); tile(700, 640); tile(288, 500)
# ④ 이웃 부교에서 내려온 하늘색 Y 집게가 막대사탕을 집는다(면역글로불린 · 세포-세포 인식)
def yclamp(cx, top, joint, tips, claws=()):
    x0, y0 = cx - 60, top - 8; W, H = 120, 110
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def T(p): return ((p[0] - x0) * S, (p[1] - y0) * S)
    def stroke(p, q, w, col):
        d.line([T(p), T(q)], fill=col, width=int(w * S))
        for z in (p, q):
            x, y = T(z); rr = w * S / 2; d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)
    segs = [((cx, top), (cx, joint))] + [((cx, joint), t) for t in tips] + [(t, c) for t, c in zip(tips, claws)]
    for p, q in segs: stroke(p, q, 15, (22, 20, 18, 255))
    for p, q in segs: stroke(p, q, 9, (150, 226, 252, 255))
    for t in (claws or tips):      # 집게발
        x, y = T(t); rr = 6.5 * S; d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(22, 20, 18, 255)); rr = 3.6 * S; d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(150, 226, 252, 255))
    lay = lay.resize((W, H), Image.LANCZOS); pil.paste(lay, (x0, y0), lay)
yclamp(1691, 150, 170, [(1667, 220), (1715, 220)], claws=[(1673, 230), (1709, 230)])
# ⑤ 잠수부가 든 부표 사람: 다리 끝이 곁 기둥의 감긴 사슬에 닿아 「사슬을 끈다」로 읽힘 → 다리 끝을 버터빛으로 덮어 줄임
arr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR); mk = np.zeros(arr.shape[:2], np.uint8)
for p, q in [((1048, 529), (1064, 499)), ((1065, 543), (1091, 517))]:
    cv2.line(mk, p, q, 255, 13); cv2.circle(mk, q, 7, 255, -1)
arr = cv2.inpaint(arr, mk, 6, cv2.INPAINT_TELEA)
pil = Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))
# 덮으며 지워진 구슬 테두리(초록 · 보라 구슬 왼쪽 아래)를 살림: 원본에서 구슬 쪽만 되가져옴
orig = Image.open(src).convert('RGB')
for (bx, by, br) in [(1073, 489, 13), (1075, 505, 12), (1097, 510, 11)]:
    m = Image.new('L', pil.size, 0); ImageDraw.Draw(m).ellipse([bx - br, by - br, bx + br, by + br], fill=255); pil.paste(orig, (0, 0), m)
# ⑥ 아랫줄로 내려놓는 굽은 화살(플립)
lay = Image.new('RGBA', (80 * S, 90 * S), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
ox, oy = 1010, 615
pts = [(1036 - ox + 7 * math.sin(t * math.pi), 630 - oy + t * 46) for t in [i / 20 for i in range(21)]]
dd.line([(x * S, y * S) for x, y in pts], fill=(20, 20, 20, 255), width=int(6.0 * S), joint='curve')
ex, ey = pts[-1]; dd.polygon([((ex - 12) * S, (ey - 4) * S), ((ex + 12) * S, (ey - 4) * S), (ex * S, (ey + 13) * S)], fill=(20, 20, 20, 255))
lay = lay.resize((80, 90), Image.LANCZOS); pil.paste(lay, (ox, oy), lay)
# ⑦ 녹는 끝의 기운 기둥 꼭대기: 줄무늬 막대(막대사탕 · 곤봉으로 읽힘) 지우고 빨간 구슬만
a = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
reg = a[336:414, 1912:1992].astype(int)
notwater = ~((reg[..., 0] > reg[..., 2] + 25) & (reg[..., 0] > 150))
yy, xx = np.mgrid[336:414, 1912:1992]
notwater &= ~((xx - 1964) ** 2 + (yy - 392) ** 2 <= 19 ** 2)           # 아래 파란 구슬은 그대로
mk = cv2.dilate(notwater.astype(np.uint8) * 255, np.ones((7, 7), np.uint8))
mk[((xx - 1964) ** 2 + (yy - 392) ** 2 <= 16.5 ** 2)] = 0
mk[((xx - 1946) ** 2 + (yy - 380) ** 2 <= 7 ** 2)] = 255             # 파란 구슬 왼쪽 위에 남는 옛 테두리 자국
full = np.zeros(a.shape[:2], np.uint8); full[336:414, 1912:1992] = mk
a = cv2.inpaint(a, full, 7, cv2.INPAINT_TELEA)
src_a = a.copy()
for y in range(366, 392):                 # 파란 구슬 왼쪽 위에 번진 어두운 자국 → 왼쪽 물빛을 옮겨 옴
    for x in range(1934, 1958):
        if (x - 1946) ** 2 + (y - 379) ** 2 > 11 ** 2: continue
        if (x - 1964) ** 2 + (y - 392) ** 2 <= 17 ** 2 or (x - 1961) ** 2 + (y - 361) ** 2 <= 16 ** 2: continue
        a[y, x] = src_a[y, x - 22]
pil = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))
lay = Image.new('RGBA', (44 * S, 44 * S), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
cx = cy = 22 * S; r = 15.5 * S
dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(22, 20, 18, 255)); r2 = 12.6 * S
dd.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(226, 52, 40, 255))
dd.ellipse([cx - 7 * S, cy - 8 * S, cx - 1 * S, cy - 3 * S], fill=(246, 150, 135, 255))
lay = lay.resize((44, 44), Image.LANCZOS); pil.paste(lay, (1961 - 22, 361 - 22), lay)
pil.save(dst); print('ok')

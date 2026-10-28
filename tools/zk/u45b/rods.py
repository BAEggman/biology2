"""rods.py — 마디 진 막대(크림 · 밤색이 번갈아 · 짙은 윤곽 · 마디 이음선)를 정확한 마디 수로 그린다(4배로 그려 줄여 붙임 · 안티에일리어싱).
draw_rod(img, p0, p1, n, w, first='cream', dark_last=False, cap0=True, cap1=True) — p0 → p1 축, n 마디, 지름 w(px).
coin(img, c, r, ang) — 테 있는 납작 금화가 막대 옆구리에 반쯤 박힌 꼴(타원)."""
import math
import numpy as np
from PIL import Image, ImageDraw
CREAM, TAN, DARK, OUT = (247, 236, 205), (206, 172, 124), (104, 110, 118), (52, 40, 30)
SS = 4
def _layer(img):
    return Image.new('RGBA', (img.width * SS, img.height * SS), (0, 0, 0, 0))
def _flush(img, lay):
    small = lay.resize(img.size, Image.LANCZOS)
    base = img.convert('RGBA'); base.alpha_composite(small)
    return base.convert('RGB')
def draw_rod(img, p0, p1, n, w, first='cream', dark_last=False, cap0=True, cap1=True, joints=True):
    lay = _layer(img); d = ImageDraw.Draw(lay)
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    if ny > 0: nx, ny = -nx, -ny                    # n 이 위쪽(화면 y 감소)을 향하게 — 하이라이트 쪽
    h = w / 2.0
    def S(x, y): return (x * SS, y * SS)
    def quad(a, b, hh):
        return [S(a[0] + nx * hh, a[1] + ny * hh), S(b[0] + nx * hh, b[1] + ny * hh), S(b[0] - nx * hh, b[1] - ny * hh), S(a[0] - nx * hh, a[1] - ny * hh)]
    ow = 2.0
    # 바깥 윤곽(몸통 + 둥근 끝)
    d.polygon(quad(p0, p1, h + ow), fill=OUT + (255,))
    for (px, py), cap in ((p0, cap0), (p1, cap1)):
        if cap: d.ellipse([S(px - h - ow, py - h - ow), S(px + h + ow, py + h + ow)], fill=OUT + (255,))
    seg = L / n
    cols = []
    for k in range(n):
        c = CREAM if (k % 2 == 0) == (first == 'cream') else TAN
        if dark_last and k == n - 1: c = DARK
        cols.append(c)
    for k in range(n):
        a = (x0 + ux * seg * k, y0 + uy * seg * k); b = (x0 + ux * seg * (k + 1), y0 + uy * seg * (k + 1))
        c = cols[k]
        d.polygon(quad(a, b, h), fill=c + (255,))
        # 아래쪽 그늘 띠 · 위쪽 하이라이트
        shade = tuple(int(v * 0.86) for v in c); hl = tuple(min(255, int(v * 1.06 + 8)) for v in c)
        a2 = (a[0] - nx * h * 0.35, a[1] - ny * h * 0.35); b2 = (b[0] - nx * h * 0.35, b[1] - ny * h * 0.35)
        d.polygon([S(a2[0], a2[1]), S(b2[0], b2[1]), S(b[0] - nx * h, b[1] - ny * h), S(a[0] - nx * h, a[1] - ny * h)], fill=shade + (255,))
        a3 = (a[0] + nx * h * 0.55, a[1] + ny * h * 0.55); b3 = (b[0] + nx * h * 0.55, b[1] + ny * h * 0.55)
        d.line([S(*a3), S(*b3)], fill=hl + (255,), width=max(1, int(SS * w * 0.12)))
    # 둥근 끝 채움
    if cap0:
        d.ellipse([S(x0 - h, y0 - h), S(x0 + h, y0 + h)], fill=cols[0] + (255,))
        d.ellipse([S(x0 - h * 0.62, y0 - h * 0.62), S(x0 + h * 0.62, y0 + h * 0.62)], outline=OUT + (200,), width=SS)
    if cap1:
        d.ellipse([S(x1 - h, y1 - h), S(x1 + h, y1 + h)], fill=cols[-1] + (255,))
    # 마디 이음선
    if joints:
        for k in range(1, n):
            cx, cy = x0 + ux * seg * k, y0 + uy * seg * k
            d.line([S(cx + nx * (h + 0.5), cy + ny * (h + 0.5)), S(cx - nx * (h + 0.5), cy - ny * (h + 0.5))], fill=OUT + (255,), width=int(SS * 1.6))
    return _flush(img, lay)
def coin(img, c, r, ang=0.0, squash=0.55):
    lay = _layer(img); d = ImageDraw.Draw(lay)
    cx, cy = c
    rx, ry = r, r * squash
    # 회전 타원을 다각형으로
    pts = [(cx + rx * math.cos(t) * math.cos(ang) - ry * math.sin(t) * math.sin(ang), cy + rx * math.cos(t) * math.sin(ang) + ry * math.sin(t) * math.cos(ang)) for t in np.linspace(0, 2 * math.pi, 64)]
    S = lambda p: (p[0] * SS, p[1] * SS)
    d.polygon([S(p) for p in pts], fill=(214, 168, 40, 255), outline=(92, 62, 18, 255))
    d.line([S(p) for p in pts] + [S(pts[0])], fill=(92, 62, 18, 255), width=int(SS * 1.4))
    pts2 = [(cx + 0.72 * (x - cx), cy + 0.72 * (y - cy)) for (x, y) in pts]
    d.line([S(p) for p in pts2] + [S(pts2[0])], fill=(176, 128, 26, 255), width=int(SS * 1.0))
    hx, hy = cx - rx * 0.35 * math.cos(ang) + ry * 0.3 * math.sin(ang), cy - rx * 0.35 * math.sin(ang) - ry * 0.3 * math.cos(ang)
    d.ellipse([S((hx - r * 0.18, hy - r * 0.12)), S((hx + r * 0.18, hy + r * 0.12))], fill=(255, 236, 160, 255))
    return _flush(img, lay)

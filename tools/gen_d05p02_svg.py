#!/usr/bin/env python3
"""d05p02 「거리와 재조합빈도」 SVG 생성기.

세 띠
  A 검정교배 자손 네 무리 — 부모형 둘이 높고 재조합형 둘이 낮다. RF = 재조합형/전체 × 100
  B 초파리 지도 자        — 눈금이 곧 위치다. 거리는 빼고, 인접 구간은 더한다
  C 지도거리 vs 관측 RF   — 짧으면 거의 같고, 멀어지면 벌어지다가 50%에서 천장에 부딪힌다
"""
import os, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d05p02.svg')

W, H = 880, 786
TEAL_F, TEAL_S, TEAL_T = '#CCFBF1', '#0F766E', '#115E59'
ORNG_F, ORNG_S, ORNG_T = '#FFEDD5', '#C2410C', '#9A3412'
GREY, DARK, MID, LINE = '#9CA3AF', '#374151', '#6B7280', '#E5E7EB'

# ── 자료 (전부 실제 카드에서 온 값이다)
CLASSES = [('부모형', 410), ('부모형', 405), ('재조합형', 90), ('재조합형', 95)]
LOCI = [(0.0, '짧은 더듬이'), (16.5, '고동색 눈'), (48.5, '검은 몸'), (57.5, '주홍색 눈'),
        (67.0, '흔적 날개'), (75.5, '아래로 휜 날개'), (104.5, '갈색 눈')]


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def band_a():
    g = [txt(14, 26, 'A. 검정교배 자손 네 무리', 12.5, 700, GREY, 'start')]
    base, maxh, bw, gap, x0 = 196, 132, 62, 26, 84
    top = max(v for _, v in CLASSES)
    for i, (kind, v) in enumerate(CLASSES):
        x = x0 + i * (bw + gap)
        h = maxh * v / top
        par = kind == '부모형'
        f, s, tc = (TEAL_F, TEAL_S, TEAL_T) if par else (ORNG_F, ORNG_S, ORNG_T)
        g.append('<rect x="%g" y="%g" width="%g" height="%g" rx="4" fill="%s" stroke="%s" '
                 'stroke-width="1.4"/>' % (x, base - h, bw, h, f, s))
        g.append(txt(x + bw / 2, base - h - 9, str(v), 13, 700, tc))
    # 무리 묶음
    l1, r1 = x0, x0 + 2 * bw + gap
    l2, r2 = x0 + 2 * (bw + gap), x0 + 4 * bw + 3 * gap
    for (l, r, lab, tc) in ((l1, r1, '부모형 — 많다', TEAL_T), (l2, r2, '재조합형 — 적다', ORNG_T)):
        g.append('<path d="M%g 204 L%g 212 L%g 212 L%g 204" fill="none" stroke="%s" '
                 'stroke-width="1.4"/>' % (l, l, r, r, GREY))
        g.append(txt((l + r) / 2, 229, lab, 11.5, 700, tc))
    g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.6"/>'
             % (x0 - 12, base, r2 + 12, base, GREY))

    # 계산 상자
    g.append('<rect x="470" y="46" width="386" height="176" rx="8" fill="#F9FAFB" '
             'stroke="#D1D5DB" stroke-width="1.3"/>')
    g.append(txt(663, 74, '재조합빈도(교차율)', 13, 700, DARK))
    g.append(txt(663, 104, '재조합형 수 ÷ 전체 수 × 100', 13.5, 700, MID))
    g.append('<line x1="506" y1="120" x2="820" y2="120" stroke="%s" stroke-width="1.2"/>' % LINE)
    tot = sum(v for _, v in CLASSES)
    rec = sum(v for k, v in CLASSES if k == '재조합형')
    g.append(txt(663, 148, '(90 + 95) ÷ %d × 100' % tot, 13, 700, DARK))
    g.append(txt(663, 178, '= %g %%' % (rec / tot * 100), 21, 700, ORNG_T))
    g.append(txt(663, 204, '★ 1 %% = 1 cM 이므로 곧 %g cM' % (rec / tot * 100), 12, 700, MID))
    return ''.join(g)


def band_b():
    y = 320
    x0, x1 = 96, 806
    span = LOCI[-1][0]
    def px(p): return x0 + (x1 - x0) * p / span
    g = [txt(14, 268, 'B. 초파리 지도 자 — 눈금이 곧 위치다', 12.5, 700, GREY, 'start')]
    g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="2.4" '
             'stroke-linecap="round"/>' % (x0, y, x1, y, '#6B7280'))
    for i, (p, name) in enumerate(LOCI):
        x = px(p)
        g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.8"/>'
                 % (x, y - 9, x, y + 9, '#374151'))
        g.append('<circle cx="%g" cy="%g" r="5.5" fill="#14B8A6" stroke="#0F766E" '
                 'stroke-width="1.6"/>' % (x, y))
        g.append(txt(x, y - 16, ('%g' % p), 11.5, 700, DARK))
        row = 0 if i % 2 == 0 else 1
        g.append(txt(x, y + 26 + row * 17, name, 9.5, 700, MID))
    # 예시 구간 — 빼기와 더하기
    a, b, c = px(48.5), px(57.5), px(67.0)
    g.append('<path d="M%g 396 L%g 396" stroke="%s" stroke-width="1.6" fill="none"/>'
             % (a, b, ORNG_S))
    g.append('<path d="M%g 392 L%g 400 M%g 392 L%g 400" stroke="%s" stroke-width="1.6"/>'
             % (a, a, b, b, ORNG_S))
    g.append(txt((a + b) / 2, 388, '9.0', 10.5, 700, ORNG_T))
    g.append('<path d="M%g 396 L%g 396" stroke="%s" stroke-width="1.6" fill="none"/>'
             % (b, c, ORNG_S))
    g.append('<path d="M%g 392 L%g 400" stroke="%s" stroke-width="1.6"/>' % (c, c, ORNG_S))
    g.append(txt((b + c) / 2, 388, '9.5', 10.5, 700, ORNG_T))
    g.append('<path d="M%g 424 L%g 424" stroke="%s" stroke-width="1.8" fill="none"/>'
             % (a, c, TEAL_S))
    g.append('<path d="M%g 420 L%g 428 M%g 420 L%g 428" stroke="%s" stroke-width="1.8"/>'
             % (a, a, c, c, TEAL_S))
    g.append(txt((a + c) / 2, 446, '67.0 − 48.5 = 18.5 = 9.0 + 9.5', 11, 700, TEAL_T))
    g.append(txt(x1, 446, '단위 = map unit (cM)', 11, 700, MID, 'end'))
    return ''.join(g)


def band_c():
    # 축
    px0, px1, py0, py1 = 128, 748, 738, 524     # py0 = RF 0, py1 = RF 60
    dmax, rmax = 250.0, 60.0
    def X(d): return px0 + (px1 - px0) * d / dmax
    def Y(r): return py0 - (py0 - py1) * r / rmax
    g = [txt(14, 490, 'C. 지도거리와 실제 관측 재조합빈도', 12.5, 700, GREY, 'start')]
    g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.6"/>'
             % (px0, py0, px1, py0, MID))
    g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.6"/>'
             % (px0, py0, px0, py1, MID))
    g.append(txt((px0 + px1) / 2, 778, '지도거리 (cM)', 11.5, 700, MID))
    g.append('<text x="%g" y="%g" text-anchor="middle" font-size="11.5" font-weight="700" '
             'fill="%s" transform="rotate(-90 %g %g)">관측 재조합빈도 (%%)</text>'
             % (86, (py0 + py1) / 2, MID, 86, (py0 + py1) / 2))
    for d in (0, 50, 100, 150, 200, 250):
        g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.2"/>'
                 % (X(d), py0, X(d), py0 + 6, MID))
        g.append(txt(X(d), py0 + 20, str(d), 10.5, 700, MID))
    for r in (0, 25, 50):
        g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.2"/>'
                 % (px0 - 6, Y(r), px0, Y(r), MID))
        g.append(txt(px0 - 12, Y(r) + 4, str(r), 10.5, 700, MID, 'end'))

    # 천장 50%
    g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="7 5"/>' % (px0, Y(50), px1, Y(50), ORNG_S))
    g.append(txt(px1, Y(50) - 10, '★ 이론적 최대 50 % — 못 넘는다', 11.5, 700, ORNG_T, 'end'))

    # 이론선 y = x
    g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="4 4"/>' % (X(0), Y(0), X(rmax), Y(rmax), GREY))
    g.append(txt(X(46), Y(56), '자 눈금 그대로라면', 10.5, 700, GREY, 'start'))

    # 관측 곡선 — 50에서 포화
    pts = []
    d = 0.0
    while d <= dmax + 0.01:
        r = 50 * (1 - math.exp(-d / 50.0))
        pts.append('%g %g' % (X(d), Y(r)))
        d += 4.0
    g.append('<path d="M%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (' L'.join(pts), TEAL_S))

    # 표시점
    for d, lab in ((9.0, '가까우면 거의 같다'), (200.0, '멀면 천장에 붙는다')):
        r = 50 * (1 - math.exp(-d / 50.0))
        g.append('<circle cx="%g" cy="%g" r="5" fill="#FFFFFF" stroke="%s" stroke-width="2.2"/>'
                 % (X(d), Y(r), TEAL_S))
    g.append(txt(X(30), Y(24), '가까우면 거의 같다', 10.5, 700, TEAL_T, 'end'))
    g.append(txt(X(200), Y(50 * (1 - math.exp(-200 / 50.0))) + 24, '멀면 천장에 붙는다',
                 10.5, 700, TEAL_T, 'middle'))
    # 원점
    g.append('<circle cx="%g" cy="%g" r="5" fill="#FFFFFF" stroke="%s" stroke-width="2.2"/>'
             % (X(0), Y(0), TEAL_S))
    g.append(txt(X(14), Y(3), '0 % — 아주 가깝거나 교차를 못 본 것', 10.5, 700, MID, 'start'))
    return ''.join(g)


def main():
    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td6 dd6">' % (W, H)]
    p.append('<title id="td6">재조합빈도와 지도거리 — 세는 법, 재는 법, 그리고 천장</title>')
    p.append('<desc id="dd6">위 띠는 검정교배 자손 네 무리를 막대로 세운 것이다. '
             '앞의 두 무리가 높고(부모형 410과 405) 뒤의 두 무리가 낮으며(재조합형 90과 95), '
             '옆 상자에서 재조합형을 전체로 나눠 18.5퍼센트를 얻는다. '
             '가운데 띠는 초파리 지도 자로 0부터 104.5까지 일곱 자리에 유전자가 찍혀 있고, '
             '48.5와 57.5 사이 9.0, 57.5와 67.0 사이 9.5를 더하면 48.5와 67.0 사이 18.5가 됨을 보인다. '
             '아래 띠는 지도거리에 대한 실제 관측 재조합빈도 곡선으로, 짧은 거리에서는 점선인 '
             '자 눈금과 거의 겹치다가 멀어질수록 아래로 벌어지고 50퍼센트 선에 붙어 더 오르지 않는다.</desc>')
    p.append('<line x1="14" y1="244" x2="866" y2="244" stroke="%s" stroke-width="1.3"/>' % LINE)
    p.append('<line x1="14" y1="466" x2="866" y2="466" stroke="%s" stroke-width="1.3"/>' % LINE)
    p.append(band_a())
    p.append(band_b())
    p.append(band_c())
    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg, '백틱·역슬래시가 들어가면 주입이 깨진다'
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))


if __name__ == '__main__':
    main()

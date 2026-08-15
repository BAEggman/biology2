#!/usr/bin/env python3
"""d05p06 「모건의 흰눈 초파리 — 눈색이 X를 따라다닌다」 SVG 생성기.

★ 이 도해의 문법 (d05 어휘 그대로)
  긴 청록 막대 = X 염색체 · 짧은 청록 막대 = Y 염색체(눈색 자리가 아예 없다)
  채운 빨간 원 = w+ (야생형 빨간눈, 우성) · 빈 원 = w (흰눈, 열성)
  상자 바탕이 붉으면 빨간눈 개체, 희면 흰눈 개체다.

읽는 순서
  P   빨간눈 암컷(w+/w+) × 흰눈 수컷(w/Y)
  배우자  난자는 X 한 가지 · 정자는 X 또는 Y 두 가지
  F1  딸도 아들도 전부 빨간눈 — 빨간눈이 우성이기 때문
  F2  2×2 격자에서 흰눈은 수컷 칸 하나뿐
  옆  X^w X^w(흰눈 암컷)는 이 교배에서 나오지 않는다 — 양쪽 X가 다 w여야 한다

좌표와 개수가 곧 사실이라 손으로 쓰지 않는다.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d05p06.svg')

W, H = 880, 916

TEAL, TEAL_D = '#5EEAD4', '#0F766E'          # 성염색체
RED_F, RED_D = '#DC2626', '#7F1D1D'          # w+ (빨간눈 대립유전자)
EMPTY_F, EMPTY_D = '#FFFFFF', '#374151'      # w  (흰눈 대립유전자)
DARK, MID, GREY, LINE = '#374151', '#6B7280', '#9CA3AF', '#E5E7EB'
REDBOX_F, REDBOX_S, REDBOX_T = '#FEE2E2', '#DC2626', '#991B1B'
WHTBOX_F, WHTBOX_S, WHTBOX_T = '#FFFFFF', '#6B7280', '#374151'
PALE, PALE_S = '#F9FAFB', '#D1D5DB'


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def geno(x, y, parts, size=13, fill=DARK, anchor='middle'):
    """유전자형 표기. parts = [('X','w+'), ('Y',None)] → X^w+ Y"""
    up = size * 0.40
    out = []
    for i, (base, sup) in enumerate(parts):
        if i:
            out.append('<tspan> </tspan>')
        out.append('<tspan>%s</tspan>' % base)
        if sup:
            out.append('<tspan font-size="%g" dy="-%g">%s</tspan>'
                       '<tspan dy="%g"></tspan>' % (size * 0.68, up, sup, up))
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="700" '
            'fill="%s">%s</text>' % (x, y, anchor, size, fill, ''.join(out)))


def xbar(cx, cy, allele, h=54, w=13):
    """긴 청록 막대(X) — 가운데에 눈색 자리 원이 하나. allele: 'W'(w+) | 'w'"""
    f, d = (RED_F, RED_D) if allele == 'W' else (EMPTY_F, EMPTY_D)
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="6" fill="%s" stroke="%s" '
            'stroke-width="1.6"/>'
            '<circle cx="%g" cy="%g" r="5.6" fill="%s" stroke="%s" stroke-width="1.6"/>'
            % (cx - w / 2, cy - h / 2, w, h, TEAL, TEAL_D, cx, cy, f, d))


def ybar(cx, cy, h=26, w=13, off=14):
    """짧은 청록 막대(Y) — 원 자리가 아예 없다. 긴 막대와 아래끝을 맞춘다."""
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="6" fill="%s" stroke="%s" '
            'stroke-width="1.6"/>' % (cx - w / 2, cy - h / 2 + off, w, h, TEAL, TEAL_D))


def bars(cx, cy, spec, gap=26, bh=54):
    """spec = ['W','w'] 또는 ['W','Y']. bh = 긴 막대 높이(짧은 막대는 그 절반 아래에 붙는다)"""
    g = []
    n = len(spec)
    sh = bh * 0.48
    for i, s in enumerate(spec):
        x = cx + (i - (n - 1) / 2) * gap
        g.append(ybar(x, cy, h=sh, off=(bh - sh) / 2) if s == 'Y'
                 else xbar(x, cy, s, h=bh))
    return ''.join(g)


def indiv(cx, cy, sex, spec, gtparts, pheno, w=214, h=112):
    """개체 한 칸. pheno: '빨간눈' | '흰눈' — 상자 바탕색이 곧 표현형이다."""
    red = pheno == '빨간눈'
    f, s, t = (REDBOX_F, REDBOX_S, REDBOX_T) if red else (WHTBOX_F, WHTBOX_S, WHTBOX_T)
    g = ['<rect x="%g" y="%g" width="%g" height="%g" rx="9" fill="%s" stroke="%s" '
         'stroke-width="1.8"/>' % (cx - w / 2, cy - h / 2, w, h, f, s)]
    g.append(txt(cx - w / 2 + 18, cy - h / 2 + 22, sex, 15, 700, t, 'start'))
    g.append(geno(cx + 14, cy - h / 2 + 23, gtparts, 13, t, 'middle'))
    g.append(bars(cx, cy + 6, spec))
    g.append(txt(cx, cy + h / 2 - 9, pheno, 11.5, 700, t))
    return ''.join(g)


def gambox(cx, cy, spec, gtparts, w=96, h=74):
    g = ['<rect x="%g" y="%g" width="%g" height="%g" rx="8" fill="%s" stroke="%s" '
         'stroke-width="1.3"/>' % (cx - w / 2, cy - h / 2, w, h, PALE, PALE_S)]
    g.append(bars(cx, cy - 8, spec, gap=22, bh=38))
    g.append(geno(cx, cy + h / 2 - 8, gtparts, 11.5, MID))
    return ''.join(g)


def main():
    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td10 dd10">' % (W, H)]
    p.append('<title id="td10">모건의 흰눈 초파리 — 눈색이 X 염색체를 따라다닌다</title>')
    p.append('<desc id="dd10">빨간눈 암컷과 흰눈 수컷의 교배를 두 세대에 걸쳐 늘어놓은 격자다. '
             '긴 청록 막대가 X 염색체이고 짧은 청록 막대가 Y 염색체인데, Y에는 눈색 자리인 원이 아예 없다. '
             '채운 빨간 원이 야생형 w+ 대립유전자이고 빈 원이 흰눈 w 대립유전자다. '
             '어버이는 빨간눈 암컷과 흰눈 수컷이고, 난자는 X 한 가지만, 정자는 X와 Y 두 가지를 낸다. '
             '자손 1대는 딸도 아들도 모두 빨간눈이다. '
             '자손 2대 2×2 격자에서는 네 칸 가운데 흰눈이 수컷 칸 하나뿐이다. '
             '오른쪽 옆 상자는 두 X가 모두 흰눈 대립유전자여야 암컷이 흰눈이 된다는 것과, '
             'Y에 짝 자리가 없어 수컷이 반접합이라는 것을 따로 보인다.</desc>')
    p.append('<defs><marker id="a6" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" '
             'markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="%s"/>'
             '</marker></defs>' % GREY)
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="#FFFFFF"/>' % (W, H))

    # ── 제목
    p.append(txt(440, 28, '모건의 흰눈 초파리 — 눈색이 X를 따라다닌다', 16, 700, DARK))
    p.append(txt(440, 48, '빨간눈 암컷 × 흰눈 수컷을 두 세대 늘어놓으면, 흰눈이 수컷 칸에만 떨어진다',
                 11, 700, MID))

    # ── 범례
    p.append('<rect x="22" y="62" width="836" height="46" rx="8" fill="%s" stroke="%s" '
             'stroke-width="1.2"/>' % (PALE, PALE_S))
    p.append(xbar(46, 85, 'W', h=34, w=11))
    p.append(txt(60, 89, 'X 염색체 — 눈색 자리가 있다', 10.5, 700, MID, 'start'))
    p.append(ybar(250, 78, h=20, w=11))
    p.append(txt(264, 89, 'Y 염색체 — 눈색 자리가 아예 없다', 10.5, 700, MID, 'start'))
    p.append('<circle cx="502" cy="85" r="6" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (RED_F, RED_D))
    p.append(geno(516, 82, [('w', '+')], 11, MID, 'start'))
    p.append(txt(516, 96, '야생형 빨간눈 · 우성', 10, 700, MID, 'start'))
    p.append('<circle cx="676" cy="85" r="6" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (EMPTY_F, EMPTY_D))
    p.append(txt(690, 82, 'w', 11, 700, MID, 'start'))
    p.append(txt(690, 96, '흰눈 · 열성', 10, 700, MID, 'start'))

    # ── 어버이(P)
    p.append('<rect x="22" y="120" width="836" height="130" rx="9" fill="#FFFFFF" '
             'stroke="%s" stroke-width="1.3"/>' % PALE_S)
    p.append(txt(36, 140, '어버이 (P)', 11.5, 700, GREY, 'start'))
    p.append(indiv(250, 190, '♀', ['W', 'W'], [('X', 'w+'), ('X', 'w+')], '빨간눈'))
    p.append(txt(440, 196, '×', 20, 700, GREY))
    p.append(indiv(630, 190, '♂', ['w', 'Y'], [('X', 'w'), ('Y', None)], '흰눈'))

    # ── 배우자
    p.append('<rect x="22" y="262" width="836" height="112" rx="9" fill="#FFFFFF" '
             'stroke="%s" stroke-width="1.3"/>' % PALE_S)
    p.append(txt(36, 282, '만드는 배우자', 11.5, 700, GREY, 'start'))
    p.append(gambox(250, 322, ['W'], [('X', 'w+')]))
    p.append(txt(250, 368, '난자는 X 한 가지뿐', 10.5, 700, MID))
    p.append(gambox(576, 322, ['w'], [('X', 'w')]))
    p.append(gambox(684, 322, ['Y'], [('Y', None)]))
    p.append(txt(630, 368, '정자는 X 또는 Y — 두 가지', 10.5, 700, MID))
    p.append(txt(440, 326, '성을 정하는 쪽은 정자다', 10.5, 700, GREY))

    # ── F1
    p.append('<rect x="22" y="386" width="836" height="160" rx="9" fill="#FFFFFF" '
             'stroke="%s" stroke-width="1.3"/>' % PALE_S)
    p.append(txt(36, 406, '자손 1대 (F1)', 11.5, 700, GREY, 'start'))
    p.append(indiv(250, 462, '♀', ['W', 'w'], [('X', 'w+'), ('X', 'w')], '빨간눈'))
    p.append(indiv(630, 462, '♂', ['W', 'Y'], [('X', 'w+'), ('Y', None)], '빨간눈'))
    p.append(txt(440, 440, '★ 딸도 아들도', 11.5, 700, REDBOX_T))
    p.append(txt(440, 458, '모두 빨간눈', 11.5, 700, REDBOX_T))
    p.append(txt(440, 480, '빨간눈이 우성이라서다', 10, 700, MID))
    p.append(txt(250, 534, '딸의 두 X 중 하나는 반드시 아버지 것이다', 10, 700, MID))
    p.append(txt(630, 534, '아들의 X 하나는 반드시 어머니 것이다', 10, 700, MID))

    # ── F2 격자 (왼쪽)
    gx, gy = 22, 558
    gw, gh = 486, 306
    p.append('<rect x="%g" y="%g" width="%g" height="%g" rx="9" fill="#FFFFFF" stroke="%s" '
             'stroke-width="1.3"/>' % (gx, gy, gw, gh, PALE_S))
    p.append(txt(gx + 14, gy + 20, 'F1끼리 교배 → 자손 2대 (F2)', 11.5, 700, GREY, 'start'))
    cw, ch = 186, 100
    cx0, cy0 = gx + 100, gy + 76
    p.append(txt(gx + 56, gy + 44, '어머니 ↓', 10, 700, GREY))
    p.append(txt(cx0 + cw, gy + 44, '아버지 →', 10, 700, GREY))
    # 열 머리 — 아버지 배우자
    for j, (spec, gt) in enumerate([(['W'], [('X', 'w+')]), (['Y'], [('Y', None)])]):
        p.append(geno(cx0 + j * cw + cw / 2, gy + 66, gt, 12, MID))
    # 행 머리 — 어머니 배우자
    for i, (spec, gt) in enumerate([(['W'], [('X', 'w+')]), (['w'], [('X', 'w')])]):
        p.append(geno(gx + 56, cy0 + i * ch + ch / 2 + 4, gt, 12, MID))
    cells = [
        ([('X', 'w+'), ('X', 'w+')], '♀ 빨간눈', True),
        ([('X', 'w+'), ('Y', None)], '♂ 빨간눈', True),
        ([('X', 'w+'), ('X', 'w')], '♀ 빨간눈', True),
        ([('X', 'w'), ('Y', None)], '♂ 흰눈', False),
    ]
    specs = [['W', 'W'], ['W', 'Y'], ['W', 'w'], ['w', 'Y']]
    for k, (gt, lab, red) in enumerate(cells):
        i, j = divmod(k, 2)
        bx, by = cx0 + j * cw, cy0 + i * ch
        f, s, t = (REDBOX_F, REDBOX_S, REDBOX_T) if red else (WHTBOX_F, WHTBOX_S, WHTBOX_T)
        p.append('<rect x="%g" y="%g" width="%g" height="%g" rx="8" fill="%s" stroke="%s" '
                 'stroke-width="%g"/>' % (bx, by, cw, ch, f, s, 1.4 if red else 2.4))
        p.append(geno(bx + cw / 2, by + 22, gt, 12.5, t))
        p.append(bars(bx + cw / 2, by + 56, specs[k], gap=24, bh=44))
        p.append(txt(bx + cw / 2, by + ch - 14, lab, 11, 700, t))
    p.append(txt(gx + gw / 2, gy + gh - 14,
                 '★ 네 칸 가운데 흰눈은 수컷 칸 하나뿐이다', 11.5, 700, REDBOX_T))

    # ── 옆 상자 둘 (오른쪽)
    sx, sw = 524, 334
    p.append('<rect x="%g" y="%g" width="%g" height="146" rx="9" fill="%s" stroke="%s" '
             'stroke-width="1.8"/>' % (sx, gy, sw, WHTBOX_F, WHTBOX_S))
    p.append(txt(sx + sw / 2, gy + 24, '암컷이 흰눈이 되려면', 12, 700, DARK))
    p.append(geno(sx + sw / 2, gy + 48, [('X', 'w'), ('X', 'w')], 13, WHTBOX_T))
    p.append(bars(sx + sw / 2, gy + 84, ['w', 'w'], gap=26))
    p.append(txt(sx + sw / 2, gy + 124, '양쪽 X가 다 빈 원이어야 한다 — 이 교배에서는 안 나온다',
                 10, 700, MID))

    p.append('<rect x="%g" y="%g" width="%g" height="146" rx="9" fill="%s" stroke="%s" '
             'stroke-width="1.3"/>' % (sx, gy + 160, sw, PALE, PALE_S))
    p.append(txt(sx + sw / 2, gy + 184, '수컷은 짝 자리가 없다 — 반접합', 12, 700, DARK))
    p.append(bars(sx + sw / 2, gy + 228, ['w', 'Y'], gap=30))
    p.append(txt(sx + sw / 2, gy + 274, '한 유전자좌에 대립유전자가 하나뿐이라', 10, 700, MID))
    p.append(txt(sx + sw / 2, gy + 290, '가릴 짝이 없어 열성이 그대로 나타난다', 10, 700, MID))

    # ── 결론 띠
    p.append('<line x1="14" y1="884" x2="866" y2="884" stroke="%s" stroke-width="1.3"/>' % LINE)
    p.append(txt(440, 904,
                 '★ 눈색이 성을 따라 갈린다 — 눈색 유전자가 X 염색체 위에 얹혀 있다는 뜻이고, '
                 '이것이 염색체설의 첫 직접 증거다', 11.5, 700, DARK))

    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg, '백틱·역슬래시가 들어가면 주입이 깨진다'
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))


if __name__ == '__main__':
    main()

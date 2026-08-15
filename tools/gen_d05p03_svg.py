#!/usr/bin/env python3
"""d05p03 「성결정 네 체계」 SVG 생성기.

★ 문법 하나 — heterogametic은 「배우자를 두 종류 만드는 쪽」이다.
  칸이 하나면 homo, 둘이면 hetero. 체계 이름이 아니라 칸 개수를 센다.

  X-Y  암 XX → 칸 하나 / 수 XY → 칸 둘 ★ 수컷
  X-O  암 XX → 칸 하나 / 수 XO → 칸 둘 ★ 수컷   (하나는 성염색체가 없는 배우자)
  Z-W  암 ZW → 칸 둘 ★ 암컷 / 수 ZZ → 칸 하나
  반수체-2배체  성염색체로 갈리지 않는다 — 수정되면 암컷(2n), 안 되면 수컷(n)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d05p03.svg')

W, H = 880, 700
TEAL, TEAL_D = '#14B8A6', '#0F766E'        # X 계열
VIOL, VIOL_D = '#8B5CF6', '#6D28D9'        # Z 계열
HOT_F, HOT_S, HOT_T = '#FFEDD5', '#C2410C', '#9A3412'   # hetero 강조
GREY, DARK, MID, LINE = '#9CA3AF', '#374151', '#6B7280', '#E5E7EB'

COLW, GAP, X0 = 200, 14, 22


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def chrom(cx, cy, kind):
    """성염색체 한 개. kind: X Y Z W O(없음)"""
    long_, col = {'X': (True, TEAL), 'Y': (False, TEAL),
                  'Z': (True, VIOL), 'W': (False, VIOL), 'O': (True, None)}[kind]
    h = 34 if long_ else 20
    y = cy - h / 2
    if col is None:
        return ('<rect x="%g" y="%g" width="13" height="%g" rx="6" fill="none" stroke="%s" '
                'stroke-width="1.6" stroke-dasharray="3 3"/>' % (cx - 6.5, y, h, GREY))
    dk = TEAL_D if col == TEAL else VIOL_D
    return ('<rect x="%g" y="%g" width="13" height="%g" rx="6" fill="%s" stroke="%s" '
            'stroke-width="1.6"/>' % (cx - 6.5, y, h, col, dk))


def gamete_box(cx, cy, kinds, hot):
    """배우자 한 종류를 담은 칸. kinds = 그 안에 들어가는 성염색체 목록."""
    w, h = 46, 46
    f, s = ('#FFFFFF', HOT_S) if hot else ('#FFFFFF', '#D1D5DB')
    g = ['<rect x="%g" y="%g" width="%g" height="%g" rx="7" fill="%s" stroke="%s" '
         'stroke-width="%g"/>' % (cx - w / 2, cy - h / 2, w, h, f, s, 2.0 if hot else 1.3)]
    n = len(kinds)
    for i, k in enumerate(kinds):
        g.append(chrom(cx + (i - (n - 1) / 2) * 17, cy, k))
    return ''.join(g)


def sex_row(cx, y, label, pair, gametes, hot):
    """한 성(性)의 줄 — 성염색체 구성 → 배우자 칸. cx는 열 중심이다.

    자리를 열 중심 기준으로 잡는다. 예전에는 행 중심을 따로 넘겨받아
    라벨이 열 상자 밖으로 12px 삐져나갔다 — 렌더해서 잡았다."""
    g = [txt(cx - 95, y + 4, label, 12, 700, HOT_T if hot else MID, 'start')]
    n = len(pair)
    for i, k in enumerate(pair):
        g.append(chrom(cx - 52 + (i - (n - 1) / 2) * 18, y, k))
    g.append('<path d="M%g %g L%g %g" stroke="%s" stroke-width="1.5" fill="none" '
             'marker-end="url(#a2)"/>' % (cx - 28, y, cx - 12, y, GREY))
    m = len(gametes)
    for i, gk in enumerate(gametes):
        g.append(gamete_box(cx + 8 + i * 50, y, gk, hot))
    mid = cx + 8 + (m - 1) * 25
    lab = '두 종류' if m == 2 else '한 종류'
    tc = HOT_T if hot else MID
    g.append(txt(mid, y + 40, '칸 %d — %s' % (m, lab), 10.5, 700, tc))
    if hot:
        g.append(txt(mid, y - 34, '★ hetero', 11, 700, HOT_T))
    return ''.join(g)


def column(i, name, example, female, male, verdict, vhot, rows=True):
    x = X0 + i * (COLW + GAP)
    cx = x + COLW / 2
    g = ['<rect x="%g" y="66" width="%g" height="300" rx="9" fill="#FFFFFF" stroke="%s" '
         'stroke-width="1.3"/>' % (x, COLW, '#D1D5DB')]
    g.append(txt(cx, 34, name, 14.5, 700, DARK))
    g.append(txt(cx, 54, example, 10.5, 700, MID))
    if rows:
        g.append(sex_row(cx, 140, female[0], female[1], female[2], female[3]))
        g.append('<line x1="%g" y1="216" x2="%g" y2="216" stroke="%s" stroke-width="1.1"/>'
                 % (x + 14, x + COLW - 14, LINE))
        g.append(sex_row(cx, 268, male[0], male[1], male[2], male[3]))
    # 결론 배지
    bf, bs, bt = (HOT_F, HOT_S, HOT_T) if vhot else ('#F3F4F6', '#D1D5DB', MID)
    g.append('<rect x="%g" y="326" width="%g" height="30" rx="15" fill="%s" stroke="%s" '
             'stroke-width="1.3"/>' % (x + 16, COLW - 32, bf, bs))
    g.append(txt(cx, 346, verdict, 11.5, 700, bt))
    return ''.join(g)


def main():
    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td7 dd7">' % (W, H)]
    p.append('<title id="td7">성결정 네 체계 — 배우자를 두 종류 만드는 쪽이 heterogametic이다</title>')
    p.append('<desc id="dd7">네 열로 XY, XO, ZW, 반수체-2배체 체계를 늘어놓았다. '
             '각 열에서 암컷과 수컷의 성염색체 구성을 막대로 그리고 그 오른쪽에 만들어지는 배우자 칸을 두었다. '
             '칸이 하나면 homogametic, 둘이면 heterogametic이고 굵은 주황 테두리로 표시했다. '
             'XY와 XO는 수컷이 칸 둘이고, ZW는 암컷이 칸 둘이다. '
             '반수체-2배체는 성염색체로 갈리지 않아 수정 여부가 성을 정한다. '
             '아래에 사람에서 더 묻는 것으로 SRY, 약 2개월, X 불활성화와 바소체, 삼색 고양이를 붙였다.</desc>')
    p.append('<defs><marker id="a2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" '
             'markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="%s"/>'
             '</marker></defs>' % GREY)

    p.append(column(0, 'X - Y', '사람 · 초파리',
                    ('암', ['X', 'X'], [['X']], False),
                    ('수', ['X', 'Y'], [['X'], ['Y']], True),
                    'hetero = 수컷', True))
    p.append(column(1, 'X - O', '메뚜기 · 귀뚜라미',
                    ('암', ['X', 'X'], [['X']], False),
                    ('수', ['X', 'O'], [['X'], ['O']], True),
                    'hetero = 수컷', True))
    p.append(column(2, 'Z - W', '조류 · 일부 어류',
                    ('암', ['Z', 'W'], [['Z'], ['W']], True),
                    ('수', ['Z', 'Z'], [['Z']], False),
                    'hetero = 암컷', True))
    p.append(column(3, '반수체 - 2배체', '벌 · 개미',
                    ('암', ['X', 'X'], [['X']], False),
                    ('수', ['X'], [['X']], False),
                    '성염색체로 안 갈린다', False, rows=False))

    # 4열은 성염색체가 아니라 수정 여부다 — 덮어 쓰는 설명
    x4 = X0 + 3 * (COLW + GAP)
    p.append('<rect x="%g" y="100" width="%g" height="212" rx="8" fill="#F9FAFB" '
             'stroke="#D1D5DB" stroke-width="1.3"/>' % (x4 + 12, COLW - 24))
    p.append(txt(x4 + COLW / 2, 130, '성을 정하는 것은', 11.5, 700, MID))
    p.append(txt(x4 + COLW / 2, 152, '수정되었는가', 14, 700, DARK))
    p.append('<line x1="%g" y1="168" x2="%g" y2="168" stroke="%s" stroke-width="1.1"/>'
             % (x4 + 30, x4 + COLW - 30, LINE))
    p.append(txt(x4 + COLW / 2, 194, '수정란 → 암컷', 12.5, 700, DARK))
    p.append(txt(x4 + COLW / 2, 214, '2배체 (2n)', 11.5, 700, TEAL_D))
    p.append(txt(x4 + COLW / 2, 254, '미수정란 → 수컷', 12.5, 700, DARK))
    p.append(txt(x4 + COLW / 2, 274, '반수체 (n)', 11.5, 700, HOT_T))
    p.append(txt(x4 + COLW / 2, 300, '배우자 칸을 셀 일이 없다', 10.5, 700, MID))

    # ── 아래 띠 ① 정의
    p.append('<line x1="14" y1="392" x2="866" y2="392" stroke="%s" stroke-width="1.3"/>' % LINE)
    p.append('<rect x="22" y="406" width="842" height="60" rx="8" fill="#FFF7ED" '
             'stroke="#FDBA74" stroke-width="1.4"/>')
    p.append(txt(440, 432, '★ heterogametic = 배우자를 두 종류 만드는 쪽 — 체계 이름이 아니라 칸 개수를 센다',
                 13.5, 700, HOT_T))
    p.append(txt(440, 454, 'X-Y 수컷 · X-O 수컷 · Z-W 암컷 — 체계에 따라 hetero인 성이 바뀐다',
                 11.5, 700, MID))

    # ── 아래 띠 ② 사람에서 더 묻는 것
    p.append(txt(14, 500, '사람에서 더 묻는 것', 12.5, 700, GREY, 'start'))
    bw, bg = 272, 12
    for i, (head, lines, col) in enumerate((
            ('Y 위의 한 자리', ['SRY (성 결정 부위)', '정소 발달에 필수'], TEAL_D),
            ('해부학적 신호', ['약 2개월 무렵', '그전에는 구분이 안 된다'], MID),
            ('두 X 중 하나를 끈다', ['불활성화 → 바소체(Barr body)', '삼색(calico) 고양이 무늬의 원인'], VIOL_D))):
        bx = 22 + i * (bw + bg)
        p.append('<rect x="%g" y="514" width="%g" height="96" rx="8" fill="#F9FAFB" '
                 'stroke="#D1D5DB" stroke-width="1.2"/>' % (bx, bw))
        p.append(txt(bx + bw / 2, 540, head, 12.5, 700, col))
        for j, ln in enumerate(lines):
            p.append(txt(bx + bw / 2, 566 + j * 20, ln, 11, 700, MID))

    # 범례
    p.append(chrom(60, 646, 'X'))
    p.append(txt(74, 650, '긴 막대 = X 또는 Z', 10.5, 700, MID, 'start'))
    p.append(chrom(230, 646, 'Y'))
    p.append(txt(244, 650, '짧은 막대 = Y 또는 W', 10.5, 700, MID, 'start'))
    p.append(chrom(420, 646, 'O'))
    p.append(txt(434, 650, '점선 = 성염색체 없음(O)', 10.5, 700, MID, 'start'))
    p.append('<rect x="620" y="634" width="24" height="24" rx="5" fill="none" stroke="%s" '
             'stroke-width="2"/>' % HOT_S)
    p.append(txt(652, 650, '굵은 주황 테두리 = heterogametic', 10.5, 700, HOT_T, 'start'))

    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg, '백틱·역슬래시가 들어가면 주입이 깨진다'
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))


if __name__ == '__main__':
    main()

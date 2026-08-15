#!/usr/bin/env python3
"""d05p04 「반성·한성·종성」 SVG 생성기.

★ 세 가지를 가르는 그림 문법 — 3×2 칸의 무늬가 서로 다르다
  반성  남자 칸이 셋이 아니라 **둘**이다        (X가 하나뿐 = 반접합)
  한성  한 성이 **전부 ✗**다                    (성이 잠근다)
  종성  **가운데 칸(이형접합)만** 갈린다        (우열이 뒤집힌다)

어휘는 d05 안에서 통일한다
  막대 = 염색체 · 원 = 대립유전자(채운 우성 / 빈 열성)
  청록 = 성염색체(d05p03과 같다) · 회색 = 상염색체
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d05p04.svg')

W, H = 880, 750
TEAL, TEAL_D = '#14B8A6', '#0F766E'
AUTO, AUTO_D = '#D1D5DB', '#6B7280'          # 상염색체
DOM, DOM_D = '#C2410C', '#9A3412'            # 대립유전자 자리
ON_F, ON_S = '#FFEDD5', '#C2410C'            # 나타남
OFF_F, OFF_S = '#F3F4F6', '#9CA3AF'          # 안 나타남
GREY, DARK, MID, LINE = '#9CA3AF', '#374151', '#6B7280', '#E5E7EB'

COLW, GAP, X0 = 272, 12, 22


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def chrom(cx, cy, long_, col, dk, gene=None):
    """염색체 막대 하나. gene: None 없음 / True 우성 / False 열성"""
    h = 34 if long_ else 20
    s = ['<rect x="%g" y="%g" width="13" height="%g" rx="6" fill="%s" stroke="%s" '
         'stroke-width="1.6"/>' % (cx - 6.5, cy - h / 2, h, col, dk)]
    if gene is not None:
        s.append('<circle cx="%g" cy="%g" r="6.5" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (cx, cy, DOM if gene else '#FFFFFF', DOM_D))
    return ''.join(s)


def badge(cx, cy, on):
    """나타남 / 안 나타남 표시. 글자를 안 쓰고 형태로 가른다."""
    f, s = (ON_F, ON_S) if on else (OFF_F, OFF_S)
    g = ['<circle cx="%g" cy="%g" r="11" fill="%s" stroke="%s" stroke-width="1.8"/>'
         % (cx, cy, f, s)]
    if on:
        g.append('<circle cx="%g" cy="%g" r="4.5" fill="%s"/>' % (cx, cy, ON_S))
    else:
        g.append('<path d="M%g %g L%g %g" stroke="%s" stroke-width="2.2" '
                 'stroke-linecap="round"/>' % (cx - 5.5, cy - 5.5, cx + 5.5, cy + 5.5, OFF_S))
    return ''.join(g)


def genocell(cx, cy, alleles):
    """유전자형 한 칸 — 원 하나 또는 둘."""
    n = len(alleles)
    g = []
    for i, a in enumerate(alleles):
        x = cx + (i - (n - 1) / 2) * 20
        g.append('<circle cx="%g" cy="%g" r="8" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (x, cy, DOM if a else '#FFFFFF', DOM_D))
    return ''.join(g)


def column(i, title, sub, chroms, rows, note, hot_cells, example=None):
    """rows = [(성라벨, [(유전자형, 나타남), ...]), ...]  hot_cells = 강조할 (행,칸) 목록"""
    x = X0 + i * (COLW + GAP)
    cx = x + COLW / 2
    g = ['<rect x="%g" y="66" width="%g" height="396" rx="9" fill="#FFFFFF" '
         'stroke="#D1D5DB" stroke-width="1.3"/>' % (x, COLW)]
    g.append(txt(cx, 34, title, 14.5, 700, DARK))
    g.append(txt(cx, 54, sub, 10.5, 700, MID))

    # 유전자가 어디 있나 — 염색체 아이콘
    g.append(txt(cx, 92, '유전자가 있는 자리', 10.5, 700, GREY))
    n = len(chroms)
    for j, (long_, col, dk, gene) in enumerate(chroms):
        g.append(chrom(cx + (j - (n - 1) / 2) * 22, 122, long_, col, dk, gene))
    g.append('<line x1="%g" y1="152" x2="%g" y2="152" stroke="%s" stroke-width="1.1"/>'
             % (x + 16, x + COLW - 16, LINE))

    # 3×2 칸
    cw, cg = 66, 8
    x0 = x + 38
    for r, (sexlab, cells) in enumerate(rows):
        ry = 186 + r * 108
        g.append(txt(x + 22, ry + 26, sexlab, 12, 700, MID))
        for c, (alleles, on) in enumerate(cells):
            ccx = x0 + c * (cw + cg) + cw / 2
            hot = (r, c) in hot_cells
            g.append('<rect x="%g" y="%g" width="%g" height="86" rx="7" fill="%s" '
                     'stroke="%s" stroke-width="%g"/>'
                     % (ccx - cw / 2, ry - 8, cw, '#FFF7ED' if hot else '#FFFFFF',
                        '#C2410C' if hot else '#E5E7EB', 2.0 if hot else 1.1))
            g.append(genocell(ccx, ry + 20, alleles))
            g.append(badge(ccx, ry + 56, on))
    g.append(txt(cx, 420, note, 11, 700, DOM_D))
    if example:
        g.append(txt(cx, 444, example, 11, 700, MID))
    return ''.join(g)


def main():
    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td8 dd8">' % (W, H)]
    p.append('<title id="td8">반성·한성·종성 — 3×2 칸의 무늬가 서로 다르다</title>')
    p.append('<desc id="dd8">세 열로 반성유전, 한성유전, 종성유전을 늘어놓았다. '
             '열마다 유전자가 놓인 염색체를 위에 그리고, 아래에 유전자형 세 가지 곱하기 성 두 가지의 칸을 두었다. '
             '칸 안 위쪽 원이 유전자형이고 아래쪽 표시가 형질이 나타나는지 여부다. '
             '반성은 남자 줄의 칸이 셋이 아니라 둘이고, 한성은 한 성의 칸이 전부 안 나타남이며, '
             '종성은 가운데 이형접합 칸에서만 남녀가 갈린다. '
             '아래에 두 물음으로 가르는 판정 줄과 반성유전의 전달 규칙을 붙였다.</desc>')

    # ── 반성유전
    p.append(column(
        0, '반성유전', '유전자가 성염색체(X) 위에 있다',
        [(True, TEAL, TEAL_D, False), (False, TEAL, TEAL_D, None)],
        [('여', [([True, True], True), ([True, False], True), ([False, False], False)]),
         ('남', [([True], True), ([False], False)])],
        '★ 남자 줄만 칸이 둘이다 — X가 하나뿐(반접합)', {(1, 0), (1, 1)},
        '사람 색맹 · 뒤셴 · 혈우병 · 초파리 눈색'))

    # ── 한성유전
    p.append(column(
        1, '한성유전', '유전자는 상염색체 위에 있다',
        [(True, AUTO, AUTO_D, True), (True, AUTO, AUTO_D, False)],
        [('암', [([True, True], True), ([True, False], True), ([False, False], False)]),
         ('수', [([True, True], False), ([True, False], False), ([False, False], False)])],
        '★ 수컷 줄이 전부 안 나타남 — 성이 잠근다', {(1, 0), (1, 1), (1, 2)},
        '닭 벼슬 · 수염 · 젖 분비'))

    # ── 종성유전
    p.append(column(
        2, '종성유전', '유전자는 상염색체 위에 있다',
        [(True, AUTO, AUTO_D, True), (True, AUTO, AUTO_D, False)],
        [('여', [([True, True], True), ([True, False], False), ([False, False], False)]),
         ('남', [([True, True], True), ([True, False], True), ([False, False], False)])],
        '★ 가운데 칸에서만 갈린다 — 우열이 뒤집힌다', {(0, 1), (1, 1)},
        '대머리 — 성호르몬 환경이 정한다'))

    # ── 판정 줄
    p.append('<line x1="14" y1="480" x2="866" y2="480" stroke="%s" stroke-width="1.3"/>' % LINE)
    p.append('<rect x="22" y="494" width="842" height="92" rx="8" fill="#F9FAFB" '
             'stroke="#D1D5DB" stroke-width="1.3"/>')
    p.append(txt(440, 520, '★ 두 물음이면 갈린다', 13, 700, DARK))
    p.append(txt(228, 550, '① 유전자가 어디 있나', 11.5, 700, TEAL_D))
    p.append(txt(228, 570, '성염색체면 반성', 11.5, 700, TEAL_D))
    p.append(txt(652, 550, '② 상염색체면, 성별에 따라 무엇이 달라지나', 11.5, 700, DOM_D))
    p.append(txt(652, 570, '나타나는가(한성) / 우열이 뒤집히는가(종성)', 11.5, 700, DOM_D))
    p.append('<line x1="440" y1="506" x2="440" y2="576" stroke="%s" stroke-width="1.1"/>' % LINE)

    # ── 반성유전의 전달 규칙
    p.append(txt(14, 616, '반성유전에서 더 묻는 것', 12, 700, GREY, 'start'))
    bw, bg = 272, 12
    boxes = [
        ('아버지의 X는 딸에게만', ['아들은 아버지에게서 Y를 받는다', '그래서 아들 표현형은 어머니가 정한다'], TEAL_D),
        ('어머니의 X는 아들·딸 모두', ['아들은 X가 하나뿐이라', '어머니 것이 그대로 나타난다'], TEAL_D),
        ('사람의 X연관 열성 셋', ['색맹 · 뒤셴 근위축증 · 혈우병', '초파리는 눈색'], DOM_D),
    ]
    for i, (head, lines, col) in enumerate(boxes):
        bx = 22 + i * (bw + bg)
        p.append('<rect x="%g" y="630" width="%g" height="96" rx="8" fill="#F9FAFB" '
                 'stroke="#D1D5DB" stroke-width="1.2"/>' % (bx, bw))
        p.append(txt(bx + bw / 2, 656, head, 12.5, 700, col))
        for j, ln in enumerate(lines):
            p.append(txt(bx + bw / 2, 682 + j * 20, ln, 11, 700, MID))

    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg, '백틱·역슬래시가 들어가면 주입이 깨진다'
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))


if __name__ == '__main__':
    main()

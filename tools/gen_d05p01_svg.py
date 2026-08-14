#!/usr/bin/env python3
"""d05p01 「상인과 상반」 SVG 생성기.

왜 손으로 안 쓰나 — 좌표와 개수가 곧 사실인 도해라, 자리를 손으로 적으면 반드시 어긋난다.
막대 하나·원 하나까지 계산해서 찍는다.

문법
  채운 원 = 우성 대립유전자 · 빈 원(테두리만) = 열성
  청록 = A/a 유전자좌 · 주황 = B/b 유전자좌
  막대 하나 = 염색체 하나. ★ 배우자는 막대를 통째로 물려받으므로 막대에 적힌 그대로가 배우자다.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d05p01.svg')

W, H = 880, 560
TEAL_F, TEAL_S = '#14B8A6', '#0F766E'      # A/a 자리
ORNG_F, ORNG_S = '#F97316', '#C2410C'      # B/b 자리
BAR_F, BAR_S = '#F3F4F6', '#9CA3AF'
GREY, DARK, MID = '#9CA3AF', '#374151', '#6B7280'

BARW, BARH, R = 250, 20, 9.5
XA, XB = 0.30, 0.72                        # 막대 안에서 두 유전자좌의 상대 위치


def bar(x, y, a_dom, b_dom, w=BARW, h=BARH):
    """염색체 막대 하나. a_dom·b_dom 이 True면 채운 원(우성)."""
    s = ['<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" stroke="%s" '
         'stroke-width="1.3"/>' % (x, y, w, h, h / 2, BAR_F, BAR_S)]
    cy = y + h / 2
    for rel, dom, f, st in ((XA, a_dom, TEAL_F, TEAL_S), (XB, b_dom, ORNG_F, ORNG_S)):
        cx = x + w * rel
        fill = f if dom else '#FFFFFF'
        s.append('<circle cx="%g" cy="%g" r="%g" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (cx, cy, R, fill, st))
    return ''.join(s)


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def col(cx, cis):
    """한 열(상인 또는 상반)을 통째로 그린다. cx = 열 중심 x."""
    g = []
    bx = cx - BARW / 2

    # ── ① 상동염색체 한 쌍
    if cis:
        top, bot = (True, True), (False, False)
    else:
        top, bot = (True, False), (False, True)
    g.append(bar(bx, 68, *top))
    g.append(bar(bx, 100, *bot))
    # 쌍이라는 표시 — 왼쪽에 대괄호
    g.append('<path d="M%g 66 L%g 66 L%g 122 L%g 122" fill="none" stroke="%s" '
             'stroke-width="1.4"/>' % (bx - 14, bx - 20, bx - 20, bx - 14, GREY))
    g.append(txt(bx - 30, 98, '쌍', 10.5, 700, GREY))

    # ── ② 배우자 — 막대를 통째로 물려받는다
    g.append('<path d="M%g 132 L%g 156" stroke="%s" stroke-width="1.6" fill="none" '
             'marker-end="url(#ar)"/>' % (cx, cx, GREY))
    g.append(bar(bx + 12, 168, *top, w=BARW - 24, h=17))
    g.append(bar(bx + 12, 196, *bot, w=BARW - 24, h=17))
    g.append(txt(cx, 232, '배우자 두 가지', 11.5, 700, MID))

    # ── ③ 자가교배 표현형
    g.append('<path d="M%g 240 L%g 264" stroke="%s" stroke-width="1.6" fill="none" '
             'marker-end="url(#ar)"/>' % (cx, cx, GREY))
    if cis:
        cells = [('#CCFBF1', '3', '#115E59'), ('#F3F4F6', '1', '#4B5563')]
        ratio, note = '3 : 1', '두 가지 표현형'
    else:
        cells = [('#FFEDD5', '1', '#C2410C'), ('#CCFBF1', '2', '#115E59'),
                 ('#DBEAFE', '1', '#1E40AF')]
        ratio, note = '1 : 2 : 1', '세 가지 표현형'
    n = len(cells)
    cw, gap = 62, 10
    tot = n * cw + (n - 1) * gap
    x0 = cx - tot / 2
    for i, (fill, lab, tc) in enumerate(cells):
        x = x0 + i * (cw + gap)
        g.append('<rect x="%g" y="276" width="%g" height="46" rx="5" fill="%s" '
                 'stroke="%s" stroke-width="1.2"/>' % (x, cw, fill, '#9CA3AF'))
        g.append(txt(x + cw / 2, 307, lab, 20, 700, tc))
    g.append(txt(cx, 344, ratio, 17, 700, DARK))
    g.append(txt(cx, 363, note, 11.5, 700, MID))
    return ''.join(g)


def main():
    p = []
    p.append('<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td5 dd5">' % (W, H))
    p.append('<title id="td5">상인연관과 상반연관 — 같은 막대에 모였는가 엇갈렸는가</title>')
    p.append('<desc id="dd5">상동염색체 한 쌍을 막대 둘로 그리고 두 유전자좌를 원으로 찍었다. '
             '채운 원이 우성, 빈 원이 열성이다. 왼쪽 상인은 한 막대에 채운 원끼리 모여 있고 '
             '오른쪽 상반은 막대마다 하나씩 엇갈려 있다. 배우자는 막대를 통째로 물려받으므로 '
             '막대에 적힌 그대로가 배우자가 되고, 자가교배 표현형이 3대1과 1대2대1로 갈린다. '
             '아래 띠는 교차가 없을 때(완전연관)와 있을 때(불완전연관)를 견준다.</desc>')
    p.append('<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" '
             'markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="%s"/>'
             '</marker></defs>' % GREY)

    # 열 제목
    p.append(txt(228, 34, '상인연관 (cis)', 14.5, 700, DARK))
    p.append(txt(228, 52, '채운 원끼리 한 막대에 모였다', 11, 700, MID))
    p.append(txt(652, 34, '상반연관 (trans)', 14.5, 700, DARK))
    p.append(txt(652, 52, '막대마다 하나씩 엇갈렸다', 11, 700, MID))
    p.append('<line x1="440" y1="26" x2="440" y2="374" stroke="#E5E7EB" stroke-width="1.4"/>')

    # 왼쪽 단계 라벨
    for y, t in ((104, '① 상동염색체'), (196, '② 배우자'), (306, '③ 자가교배')):
        p.append(txt(14, y, t, 11, 700, GREY, 'start'))

    p.append(col(228, True))
    p.append(col(652, False))

    # ── 아래 띠 — 완전연관 vs 불완전연관
    p.append('<line x1="14" y1="396" x2="866" y2="396" stroke="#E5E7EB" stroke-width="1.4"/>')
    p.append(txt(14, 420, '교차가 없으면 / 있으면', 11, 700, GREY, 'start'))

    # 완전연관
    p.append('<rect x="150" y="404" width="270" height="132" rx="7" fill="#F9FAFB" '
             'stroke="#D1D5DB" stroke-width="1.2"/>')
    p.append(txt(285, 426, '완전연관 — 교차 없음', 12.5, 700, DARK))
    p.append(bar(178, 440, True, True, w=214, h=16))
    p.append(bar(178, 464, False, False, w=214, h=16))
    p.append(txt(285, 502, '배우자 두 가지뿐', 12, 700, MID))
    p.append(txt(285, 521, '부모형만 나온다', 11, 700, MID))

    # 불완전연관
    p.append('<rect x="460" y="404" width="290" height="132" rx="7" fill="#FFF7ED" '
             'stroke="#FDBA74" stroke-width="1.4"/>')
    p.append(txt(605, 426, '불완전연관 — 감수 1분열 전기에 교차', 12.5, 700, '#9A3412'))
    p.append(bar(486, 440, True, True, w=100, h=16))
    p.append(bar(486, 464, False, False, w=100, h=16))
    p.append(txt(536, 494, '부모형 (많다)', 10.5, 700, MID))
    p.append(bar(624, 440, True, False, w=100, h=16))
    p.append(bar(624, 464, False, True, w=100, h=16))
    p.append(txt(674, 494, '재조합형 (적다)', 10.5, 700, '#C2410C'))
    p.append(txt(605, 521, '★ 배우자 네 가지 — 그런데 수가 같지 않다', 11, 700, '#9A3412'))

    # 범례 — 아래 왼쪽 빈 자리에 둔다(막대와 겹치지 않는 유일한 곳)
    p.append('<g><circle cx="30" cy="452" r="7.5" fill="%s" stroke="%s" stroke-width="2"/>'
             '<circle cx="30" cy="476" r="7.5" fill="#FFFFFF" stroke="%s" stroke-width="2"/>'
             % (TEAL_F, TEAL_S, TEAL_S))
    p.append(txt(44, 456, '채운 원 = 우성', 10.5, 700, MID, 'start'))
    p.append(txt(44, 480, '빈 원 = 열성', 10.5, 700, MID, 'start'))
    p.append('<circle cx="30" cy="504" r="7.5" fill="%s" stroke="%s" stroke-width="2"/>'
             % (ORNG_F, ORNG_S))
    p.append(txt(44, 508, '색 = 유전자좌', 10.5, 700, MID, 'start'))
    p.append('</g>')

    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg, '백틱·역슬래시가 들어가면 주입이 깨진다'
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))


if __name__ == '__main__':
    main()

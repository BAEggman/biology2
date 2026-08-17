#!/usr/bin/env python3
"""d07p01 「멘델 확률판」 SVG 생성기.

★ 이 단원의 확률 문항은 전부 네모 넷에서 나온다
      Pp × Pp 의 퍼넷 네모 넷 → 1 : 2 : 1 (유전자형) · 3 : 1 (표현형)
  그 넷을 어떻게 세느냐만 다르다.
      그냥 세면          PP 1/4 · Pp 1/2 · pp 1/4
      우성만 모아 세면    3/4 · 그중 동형 1/3 · 이형 2/3   ← ★ 분모가 4에서 3으로 바뀐다
      아이 여럿이면       곱셈 법칙 (1/4 × 1/4 = 1/16)
      「적어도 하나」면    전체 1에서 빼는 여집합

  띠1  퍼넷 네모 넷 (색으로 표현형이 갈린다)
  띠2  네모를 세는 세 가지 방법 — 분모가 4냐 3이냐
  띠3  아이가 여럿일 때 — 곱셈과 여집합
  띠4  다른 교배들 — AA×aa · Aa×aa

숫자는 손으로 적지 않는다. 분수는 전부 코드가 계산하고 찍은 뒤 스스로 검산한다.
"""
import os
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d07p01.svg')

W, H = 960, 880
DARK, MID, GREY, LINE = '#374151', '#6B7280', '#9CA3AF', '#E5E7EB'
PALE_S = '#D1D5DB'
DOM_F, DOM_S, DOM_T = '#CCFBF1', '#0F766E', '#115E59'     # 우성 표현형
REC_F, REC_S, REC_T = '#FEE2E2', '#DC2626', '#991B1B'     # 열성 표현형
ACC_F, ACC_S, ACC_T = '#FEF3C7', '#D97706', '#92400E'


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def box(x, y, w, h, f, s, sw=1.4, r=8):
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" stroke="%s" '
            'stroke-width="%g"/>' % (x, y, w, h, r, f, s, sw))


def fr(f):
    return '%d/%d' % (f.numerator, f.denominator) if f.denominator != 1 else str(f.numerator)


def main():
    # ── 셈은 전부 코드가 한다
    cells = ['PP', 'Pp', 'Pp', 'pp']
    n = len(cells)
    gPP, gPp, gpp = [F(cells.count(g), n) for g in ('PP', 'Pp', 'pp')]
    dom = gPP + gPp                       # 우성 표현형
    rec = gpp                             # 열성 표현형
    domHomo = F(cells.count('PP'), cells.count('PP') + cells.count('Pp'))
    domHet = 1 - domHomo
    two_rec = rec * rec                   # 두 아이 모두 열성
    one_rec = 2 * rec * (1 - rec)         # 둘 중 하나만 열성
    three_dom = dom ** 3                  # 세 아이 모두 우성
    assert (gPP, gPp, gpp) == (F(1, 4), F(1, 2), F(1, 4))
    assert (dom, rec) == (F(3, 4), F(1, 4))
    assert (domHomo, domHet) == (F(1, 3), F(2, 3))
    assert (two_rec, one_rec, three_dom) == (F(1, 16), F(3, 8), F(27, 64))

    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td14 dd14">' % (W, H)]
    p.append('<title id="td14">멘델 확률판 — 네모 넷을 어떻게 세느냐</title>')
    p.append('<desc id="dd14">Pp와 Pp를 교배했을 때의 퍼넷 사각형 네 칸을 맨 위에 두고, '
             '그 네 칸을 세는 방법을 아래에 늘어놓은 표다. 네 칸은 PP, Pp, Pp, pp이고 '
             '앞의 셋은 우성 표현형이라 청록, 마지막 하나만 열성이라 붉다. '
             '그냥 세면 유전자형이 1대 2대 1, 표현형이 3대 1이다. '
             '우성인 것만 모아 세면 분모가 넷이 아니라 셋이 되어 동형이 3분의 1, '
             '이형이 3분의 2가 된다. 아이가 여럿이면 곱셈 법칙을 쓰고, '
             '적어도 한 명을 물으면 전체에서 빼는 여집합을 쓴다. '
             '맨 아래에는 AA와 aa, Aa와 aa 교배의 결과를 함께 실었다.</desc>')
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="#FFFFFF"/>' % (W, H))

    p.append(txt(480, 30, '멘델 확률판 — 네모 넷을 어떻게 세느냐', 17, 700, DARK))
    p.append(txt(480, 52, '★ 이 단원의 확률 문항은 전부 이 네 칸에서 나온다. 세는 방법만 다르다',
                 12, 700, MID))

    # ── 띠 1 : 퍼넷 네모 넷
    p.append(txt(24, 86, '① Pp × Pp 의 네 칸', 12.5, 700, GREY, 'start'))
    bx, by, cs = 104, 104, 84
    p.append(txt(bx + cs, by - 8, 'P', 13, 700, MID))
    p.append(txt(bx + cs * 2, by - 8, 'p', 13, 700, MID))
    p.append(txt(bx - 16, by + cs * 0.5 + 5, 'P', 13, 700, MID))
    p.append(txt(bx - 16, by + cs * 1.5 + 5, 'p', 13, 700, MID))
    grid = [['PP', 'Pp'], ['Pp', 'pp']]
    for r in range(2):
        for c in range(2):
            g = grid[r][c]
            f, s, t = (REC_F, REC_S, REC_T) if g == 'pp' else (DOM_F, DOM_S, DOM_T)
            x, y = bx + cs * (c + 0.5), by + cs * r
            p.append(box(x, y, cs, cs, f, s, 1.6))
            p.append(txt(x + cs / 2, y + cs / 2 + 7, g, 20, 700, t))
    p.append(txt(bx + cs * 1.5, by + cs * 2 + 26,
                 '유전자형 1 : 2 : 1 · 표현형 3 : 1', 12.5, 700, DARK))

    # ── 띠 2 : 세는 세 가지 방법
    p.append(box(370, 96, 566, 200, '#FFFFFF', PALE_S, 1.3))
    p.append(txt(384, 120, '② 같은 네 칸을 세 가지로 센다 — 분모가 무엇이냐가 전부다',
                 12, 700, GREY, 'start'))
    rows2 = [
        ('네 칸을 그냥 센다', 'PP는 한 칸', fr(gPP), DOM_T),
        ('', 'Pp는 두 칸', fr(gPp), DOM_T),
        ('', 'pp는 한 칸', fr(gpp), REC_T),
        ('표현형으로 묶는다', '청록 세 칸이 우성', fr(dom), DOM_T),
        ('', '붉은 한 칸이 열성', fr(rec), REC_T),
        ('★ 우성인 것만 모아 센다', '분모가 4가 아니라 3이 된다 — 동형', fr(domHomo), ACC_T),
        ('', '같은 분모 3에서 — 이형', fr(domHet), ACC_T),
    ]
    for i, (lab, mid, val, col) in enumerate(rows2):
        y = 148 + i * 21
        if lab:
            p.append(txt(384, y, lab, 11, 700, MID, 'start'))
        p.append(txt(640, y, mid, 11, 700, MID))
        p.append(txt(910, y, val, 13, 700, col, 'end'))

    # ── 띠 3 : 아이가 여럿일 때
    y3 = 320
    p.append(txt(24, y3, '③ 아이가 여럿이면 — 곱셈 법칙, 그리고 여집합', 12.5, 700, GREY, 'start'))
    p.append(box(24, y3 + 12, 912, 176, '#FFFFFF', PALE_S, 1.3))
    rows3 = [
        ('두 사건이 모두 일어난다', '곱셈 법칙 — 각각의 확률을 곱한다', ''),
        ('서로 배타적인 것 중 하나', '덧셈 법칙 — 각각의 확률을 더한다', ''),
        ('Aa × Aa 에서 아이 하나가 열성', '1/4', fr(rec)),
        ('아이 둘 다 열성', '1/4 × 1/4', fr(two_rec)),
        ('아이 둘 중 하나만 열성', '(1/4 × 3/4) 를 두 가지 순서로', fr(one_rec)),
        ('아이 셋 다 우성', '3/4 × 3/4 × 3/4', fr(three_dom)),
        ('★ 적어도 한 명이 열성', '1 에서 「아무도 아님」을 뺀다 — 여집합이 빠르다', ''),
    ]
    for i, (q, mid, val) in enumerate(rows3):
        y = y3 + 44 + i * 21
        p.append(txt(48, y, q, 11, 700, DARK, 'start'))
        p.append(txt(600, y, mid, 11, 700, MID))
        if val:
            p.append(txt(910, y, val, 13, 700, ACC_T, 'end'))

    # ── 띠 4 : 다른 교배들
    y4 = 528
    p.append(txt(24, y4, '④ 다른 교배 — 네 칸이 어떻게 달라지나', 12.5, 700, GREY, 'start'))
    p.append(box(24, y4 + 12, 912, 128, '#FFFFFF', PALE_S, 1.3))
    rows4 = [
        ('AA × aa (우성 순종 × 열성 순종)', '네 칸이 모두 Aa', '유전자형 모두 이형 · 표현형 모두 우성'),
        ('그 F1 을 자가교배하면', 'Aa × Aa 로 돌아온다', '위 ①의 네 칸 그대로 — 3 : 1'),
        ('Aa × aa (검정교배)', '네 칸이 Aa · Aa · aa · aa', '표현형 1 : 1'),
        ('★ 검정교배가 유전자형을 드러내는 이유', '상대가 aa라 자기 것을 못 가린다',
         '자손에 열성이 하나라도 나오면 이형'),
    ]
    for i, (a, b, c) in enumerate(rows4):
        y = y4 + 44 + i * 22
        p.append(txt(48, y, a, 11, 700, DARK, 'start'))
        p.append(txt(470, y, b, 11, 700, MID))
        p.append(txt(910, y, c, 11, 700, ACC_T, 'end'))

    # ── 띠 5 : 2/3 의 급소
    y5 = 690
    p.append(box(24, y5, 912, 116, ACC_F, ACC_S, 1.5))
    p.append(txt(480, y5 + 26, '★ 시험이 가장 자주 꼬는 자리 — 분모가 3이 되는 순간', 13, 700, ACC_T))
    p.append(txt(480, y5 + 52,
                 '「보인자 부부의 자녀가 정상일 때 그 아이가 보인자일 확률」은 1/2 이 아니라 '
                 + fr(domHet) + ' 다', 12, 700, DARK))
    p.append(txt(480, y5 + 76,
                 '이미 「정상이다」를 알고 있으니 붉은 칸 하나는 후보에서 빠진다 — '
                 '남은 세 칸 중 이형이 둘이다', 11, 700, MID))
    p.append(txt(480, y5 + 98,
                 'aa 가 아닌 형제자매가 보인자일 확률이 ' + fr(domHet) + ' 인 것도 같은 셈이다',
                 11, 700, MID))

    p.append('<line x1="14" y1="%g" x2="946" y2="%g" stroke="%s" stroke-width="1.3"/>'
             % (H - 42, H - 42, LINE))
    p.append(txt(480, H - 16,
                 '★ 확률 문제를 보면 분모부터 정한다 — 네 칸 전부냐, 조건이 붙어 셋이냐',
                 12.5, 700, DARK))

    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg
    import re as _re
    for t in _re.findall(r'<text[^>]*>(.*?)</text>', svg):
        assert '<' not in t, 'SVG text 안에 태그가 들어갔다(HTML 태그는 안 먹는다): %s' % t
    for need in ['1/4', '1/2', '3/4', '1/3', '2/3', '1/16', '3/8', '27/64',
                 '곱셈 법칙', '덧셈 법칙', '여집합', '표현형 1 : 1',
                 '유전자형 1 : 2 : 1 · 표현형 3 : 1']:
        assert need in svg, '그림에 %s 가 없다' % need
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))
    print('검산 통과 — 1/4·1/2·1/4 · 3/4·1/4 · 1/3·2/3 · 1/16·3/8·27/64')


if __name__ == '__main__':
    main()

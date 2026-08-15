#!/usr/bin/env python3
"""d05p05 「비분리와 염색체 이상」 SVG 생성기.

★ 비분리를 가르는 그림 문법 — 배우자 넷의 무늬가 다르다
  감수 I 비분리   상동 한 쌍이 통째로 한쪽으로 → n+1, n+1, n-1, n-1   (정상 배우자가 하나도 없다)
  감수 II 비분리  자매염색분체만 안 갈림       → n, n, n+1, n-1        (정상 배우자가 둘 있다)
  ★ 정상 배우자가 있느냐 없느냐가 둘을 가른다.

아래 띠 ① 이수성 — 하나 모자라면 1염색체성, 하나 더 많으면 3염색체성
아래 띠 ② 구조 이상 넷 — 결실·중복·역위·전좌를 같은 막대에 대고 견준다
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d05p05.svg')

W, H = 880, 812
BLUE, BLUE_D = '#60A5FA', '#1E40AF'          # 어버이 한쪽에서 온 염색체
ROSE, ROSE_D = '#FB923C', '#C2410C'          # 다른 쪽에서 온 염색체
GREY, DARK, MID, LINE = '#9CA3AF', '#374151', '#6B7280', '#E5E7EB'
BAD_F, BAD_S, BAD_T = '#FFEDD5', '#C2410C', '#9A3412'
OK_F, OK_S, OK_T = '#CCFBF1', '#0F766E', '#115E59'


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def rod(cx, cy, col, dk, h=26, w=9):
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="4" fill="%s" stroke="%s" '
            'stroke-width="1.4"/>' % (cx - w / 2, cy - h / 2, w, h, col, dk))


def gamete(cx, cy, rods, label, kind):
    """배우자 한 칸. rods = [(색쌍)...] · kind: 'ok' | 'plus' | 'minus'"""
    f, s, t = {'ok': (OK_F, OK_S, OK_T), 'plus': (BAD_F, BAD_S, BAD_T),
               'minus': (BAD_F, BAD_S, BAD_T)}[kind]
    g = ['<rect x="%g" y="%g" width="74" height="70" rx="8" fill="%s" stroke="%s" '
         'stroke-width="%g"/>' % (cx - 37, cy - 35, f, s, 1.2 if kind == 'ok' else 2.0)]
    n = len(rods)
    for i, (c, d) in enumerate(rods):
        g.append(rod(cx + (i - (n - 1) / 2) * 15, cy - 6, c, d))
    g.append(txt(cx, cy + 28, label, 11.5, 700, t))
    return ''.join(g)


def panel(x, title, sub, split, gams, verdict):
    """비분리 한 열."""
    cx = x + 208
    g = ['<rect x="%g" y="66" width="416" height="300" rx="9" fill="#FFFFFF" '
         'stroke="#D1D5DB" stroke-width="1.3"/>' % x]
    g.append(txt(cx, 34, title, 14.5, 700, DARK))
    g.append(txt(cx, 54, sub, 10.5, 700, MID))

    # 어버이 세포 — 상동 한 쌍(파랑·주황), 각각 자매염색분체 둘
    g.append(txt(cx, 92, '어버이 세포 (2n)', 10.5, 700, GREY))
    for i, (c, d) in enumerate([(BLUE, BLUE_D), (BLUE, BLUE_D), (ROSE, ROSE_D), (ROSE, ROSE_D)]):
        g.append(rod(cx - 24 + i * 16, 122, c, d, h=30))
    g.append('<path d="M%g 142 L%g 160" stroke="%s" stroke-width="1.6" fill="none" '
             'marker-end="url(#a5)"/>' % (cx, cx, GREY))
    g.append(txt(cx, 176, split, 11, 700, BAD_T))

    # 배우자 넷
    for i, (rods, label, kind) in enumerate(gams):
        g.append(gamete(x + 66 + i * 92, 250, rods, label, kind))
    g.append(txt(cx, 336, verdict, 12, 700, BAD_T))
    return ''.join(g)


def main():
    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td9 dd9">' % (W, H)]
    p.append('<title id="td9">비분리와 염색체 이상 — 정상 배우자가 남느냐가 둘을 가른다</title>')
    p.append('<desc id="dd9">위 두 칸은 감수 1분열 비분리와 감수 2분열 비분리를 나란히 놓은 것이다. '
             '각 칸에서 어버이 세포의 상동 한 쌍을 파랑과 주황 막대로 그리고, 아래에 만들어진 배우자 넷을 늘어놓았다. '
             '1분열 비분리는 네 배우자가 모두 비정상이라 n+1이 둘, n-1이 둘이고, '
             '2분열 비분리는 정상 배우자가 둘 남아 n, n, n+1, n-1이 된다. '
             '가운데 띠는 하나 모자란 1염색체성과 하나 더 많은 3염색체성을 견주고, '
             '아래 띠는 결실·중복·역위·전좌 네 가지를 같은 막대에 대고 보인다.</desc>')
    p.append('<defs><marker id="a5" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" '
             'markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="%s"/>'
             '</marker></defs>' % GREY)

    B, R = (BLUE, BLUE_D), (ROSE, ROSE_D)
    # 감수 I 비분리 — 상동 한 쌍이 통째로 한쪽으로
    p.append(panel(22, '감수 1분열 비분리', '상동염색체 한 쌍이 통째로 한쪽으로 간다',
                   '1분열에서 상동이 안 갈린다',
                   [([B, R], 'n+1', 'plus'), ([B, R], 'n+1', 'plus'),
                    ([], 'n-1', 'minus'), ([], 'n-1', 'minus')],
                   '★ 네 배우자가 전부 비정상 — 정상이 하나도 없다'))
    # 감수 II 비분리 — 자매염색분체만 안 갈림
    p.append(panel(442, '감수 2분열 비분리', '자매염색분체가 안 갈린다',
                   '1분열은 정상, 2분열에서 자매가 안 갈린다',
                   [([B], 'n', 'ok'), ([R], 'n', 'ok'),
                    ([B, B], 'n+1', 'plus'), ([], 'n-1', 'minus')],
                   '★ 정상 배우자가 둘 남는다'))

    # ── 가운데 띠 — 이수성
    p.append('<line x1="14" y1="386" x2="866" y2="386" stroke="%s" stroke-width="1.3"/>' % LINE)
    p.append(txt(14, 412, '이수성 — 정상 배수에서 벗어난 상태', 12, 700, GREY, 'start'))
    cards = [
        ('하나 모자람', '1염색체성', ['성염색체 1염색체성 = 터너 (X 하나만)'], 'minus'),
        ('정상', '2개', ['기준'], 'ok'),
        ('하나 더 많음', '3염색체성', ['21번 3염색체성 = 다운', '성염색체 3염색체성 = 클라인펠터'], 'plus'),
    ]
    bw, bg = 272, 12
    for i, (head, name, lines, kind) in enumerate(cards):
        bx = 22 + i * (bw + bg)
        f, s, t = {'ok': (OK_F, OK_S, OK_T), 'plus': (BAD_F, BAD_S, BAD_T),
                   'minus': (BAD_F, BAD_S, BAD_T)}[kind]
        p.append('<rect x="%g" y="428" width="%g" height="128" rx="8" fill="%s" stroke="%s" '
                 'stroke-width="1.4"/>' % (bx, bw, f, s))
        p.append(txt(bx + bw / 2, 452, head, 11.5, 700, MID))
        nrod = {'minus': 1, 'ok': 2, 'plus': 3}[kind]
        for j in range(nrod):
            p.append(rod(bx + bw / 2 + (j - (nrod - 1) / 2) * 16, 482, BLUE, BLUE_D, h=28))
        p.append(txt(bx + bw / 2, 518, name, 13, 700, t))
        for j, ln in enumerate(lines):
            p.append(txt(bx + bw / 2, 538 + j * 16, ln, 10, 700, MID))

    # ── 아래 띠 — 구조 이상 넷
    p.append('<line x1="14" y1="576" x2="866" y2="576" stroke="%s" stroke-width="1.3"/>' % LINE)
    p.append(txt(14, 602, '구조 이상 넷 — 같은 막대를 어떻게 건드렸나', 12, 700, GREY, 'start'))
    # 기준 막대: 다섯 토막
    seg = [('#93C5FD', '#1E40AF'), ('#60A5FA', '#1E40AF'), ('#3B82F6', '#1E40AF'),
           ('#2563EB', '#1E40AF'), ('#1D4ED8', '#1E40AF')]

    def strip(x, y, order, extra=None, w=26):
        g = []
        for i, k in enumerate(order):
            c, d = seg[k] if k >= 0 else (extra or ('#FCA5A5', '#B91C1C'))
            g.append('<rect x="%g" y="%g" width="%g" height="20" rx="3" fill="%s" stroke="%s" '
                     'stroke-width="1.2"/>' % (x + i * w, y, w, c, d))
        return ''.join(g)

    kinds = [
        ('결실', [0, 1, 3, 4], '한 토막이 없어졌다', None),
        ('중복', [0, 1, 2, 2, 3, 4], '한 토막이 되풀이된다', None),
        ('역위', [0, 3, 2, 1, 4], '가운데가 뒤집혀 다시 붙었다', None),
        ('전좌', [0, 1, -1, -1], '다른 염색체 조각이 붙었다', ('#FCA5A5', '#B91C1C')),
    ]
    kw = 200                       # 넷이므로 폭을 따로 잡는다 (22 + 4*200 + 3*12 = 858)
    for i, (name, order, note, extra) in enumerate(kinds):
        bx = 22 + i * (kw + bg)
        p.append('<rect x="%g" y="618" width="%g" height="122" rx="8" fill="#F9FAFB" '
                 'stroke="#D1D5DB" stroke-width="1.2"/>' % (bx, kw))
        p.append(txt(bx + kw / 2, 642, name, 13, 700, DARK))
        p.append(txt(bx + 14, 668, '원본', 9.5, 700, GREY, 'start'))
        p.append(strip(bx + 44, 658, [0, 1, 2, 3, 4], w=22))
        p.append(txt(bx + 14, 706, '결과', 9.5, 700, BAD_T, 'start'))
        p.append(strip(bx + 44, 696, order, extra, w=22))
        p.append(txt(bx + kw / 2, 732, note, 10, 700, MID))

    p.append(txt(440, 766, '★ 색 띠의 순서와 개수만 보면 넷이 갈린다 — '
                           '빠짐(결실) · 겹침(중복) · 거꾸로(역위) · 남의 것(전좌)',
                 11.5, 700, DARK))
    p.append(txt(440, 790, '전좌만 다른 색이 섞인다 — 나머지 셋은 같은 염색체 안에서 벌어진 일이다',
                 10.5, 700, MID))

    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg, '백틱·역슬래시가 들어가면 주입이 깨진다'
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))


if __name__ == '__main__':
    main()

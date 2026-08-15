#!/usr/bin/env python3
"""d05p08 「비분리 — 감수 I이냐 II냐」 SVG 생성기.

★ 이 도해가 가르는 것 — 정상 배우자를 세면 끝난다
      정상 감수분열   정상 4개
      감수 I 비분리   정상 0개   (n+1, n+1, n-1, n-1)
      감수 II 비분리  정상 2개   (n, n, n+1, n-1)
  「정상이 하나도 없으면 I, 둘이면 II」 — 이 한 줄이 이 단원의 전부다.

★ 덤으로 하나 더 — n+1 칸의 속을 보면 색이 다르다
      감수 I 비분리의 n+1 = 파랑 + 주황  (서로 다른 상동염색체 둘)
      감수 II 비분리의 n+1 = 주황 + 주황  (같은 자매염색분체 둘)

셀 수 있는 것은 손으로 적지 않는다. 동원체(작은 원)를 코드가 세고,
센 값이 표의 n / n+1 / n-1 및 정상 개수와 맞는지 스스로 검산한다(assert).
d01p02의 「염색체는 동원체 수로 센다」와 같은 문법이다.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d05p08.svg')

W, H = 960, 900

DARK, MID, GREY, LINE = '#374151', '#6B7280', '#9CA3AF', '#E5E7EB'
PALE_S = '#D1D5DB'
B_F, B_S = '#BFDBFE', '#1D4ED8'      # 아버지 쪽 상동염색체
R_F, R_S = '#FED7AA', '#C2410C'      # 어머니 쪽 상동염색체
OK_F, OK_S, OK_T = '#CCFBF1', '#0F766E', '#115E59'
BAD_F, BAD_S, BAD_T = '#FEE2E2', '#DC2626', '#991B1B'
WRN_F, WRN_S, WRN_T = '#FEF3C7', '#D97706', '#92400E'

COL = {'B': (B_F, B_S), 'R': (R_F, R_S)}

# (제목, 색, 감수 I 뒤 두 세포, 배우자 넷, 한 줄 설명)
CASES = [
    ('① 정상 감수분열', (OK_F, OK_S, OK_T),
     [['B'], ['R']],
     [['B'], ['B'], ['R'], ['R']],
     '상동염색체도 자매염색분체도 제때 갈렸다'),
    ('② 감수 I 비분리', (BAD_F, BAD_S, BAD_T),
     [['B', 'R'], []],
     [['B', 'R'], ['B', 'R'], [], []],
     'I에서 상동염색체 둘이 한쪽으로 몰렸다'),
    ('③ 감수 II 비분리', (WRN_F, WRN_S, WRN_T),
     [['B'], ['R']],
     [['B'], ['B'], ['R', 'R'], []],
     'I은 정상 · II에서 자매염색분체가 안 갈렸다'),
]

N = 1   # 반수체 염색체 수 — 상동염색체 한 쌍짜리 세포(2n = 2)로 그린다


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def box(x, y, w, h, f, s, sw=1.4, r=8, dash=''):
    d = ' stroke-dasharray="6 5"' if dash else ''
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" stroke="%s" '
            'stroke-width="%g"%s/>' % (x, y, w, h, r, f, s, sw, d))


def chrom(p, x, y, h, c, dup):
    """복제된 염색체는 자매염색분체 둘 + 동원체 하나, 복제 전은 막대 하나 + 동원체 하나.
    ★ 동원체(원)는 언제나 염색체 하나에 하나다 — 세는 단위가 이것이다."""
    f, s = COL[c]
    if dup:
        for dx in (-6.5, 6.5):
            p.append('<rect x="%g" y="%g" width="8" height="%g" rx="4" fill="%s" '
                     'stroke="%s" stroke-width="1.6"/>' % (x + dx - 4, y, h, f, s))
    else:
        p.append('<rect x="%g" y="%g" width="8" height="%g" rx="4" fill="%s" '
                 'stroke="%s" stroke-width="1.6"/>' % (x - 4, y, h, f, s))
    p.append('<circle cx="%g" cy="%g" r="4.6" fill="%s" stroke="#FFFFFF" '
             'stroke-width="1.4"/>' % (x, y + h / 2, s))


def cell(p, cx, cy, w, h, items, dup, empty_note=''):
    """세포 한 칸. items는 그 칸에 든 염색체 색 목록."""
    p.append(box(cx - w / 2, cy, w, h, '#FFFFFF', PALE_S, 1.3))
    if not items:
        p.append(txt(cx, cy + h / 2 + 4, empty_note or '없음', 11, 700, GREY))
        return
    gap = 26 if dup else 22
    x0 = cx - gap * (len(items) - 1) / 2
    for i, c in enumerate(items):
        chrom(p, x0 + i * gap, cy + 12, h - 24, c, dup)


def main():
    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td13 dd13">' % (W, H)]
    p.append('<title id="td13">비분리 도해 — 정상 배우자를 세면 감수 I인지 II인지 갈린다</title>')
    p.append('<desc id="dd13">상동염색체 한 쌍만 가진 세포에서 감수분열을 세 갈래로 그린 표다. '
             '왼쪽은 정상이라 배우자 넷이 모두 정상이고, 가운데는 감수 I에서 상동염색체 둘이 '
             '한쪽으로 몰려 정상 배우자가 하나도 없으며, 오른쪽은 감수 II에서 자매염색분체가 '
             '안 갈려 정상 배우자가 둘 남는다. 파랑은 아버지 쪽 상동염색체, 주황은 어머니 쪽이다. '
             '염색체 하나마다 동원체 원이 하나씩 있어 그 원을 세면 염색체 수가 나온다. '
             '맨 아래에는 염색체가 하나 많은 칸과 하나 적은 칸이 각각 어떤 결과를 낳는지 적혀 있다.</desc>')
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="#FFFFFF"/>' % (W, H))

    p.append(txt(480, 28, '비분리 — 정상 배우자를 세면 갈린다', 17, 700, DARK))
    p.append(txt(480, 50, '★ 정상이 하나도 없으면 감수 I · 둘이면 감수 II. 이 한 줄이 전부다',
                 12, 700, MID))

    # 범례
    p.append(box(24, 64, 912, 40, '#F9FAFB', LINE, 1.2))
    lg = [(48, 'B', '아버지 쪽 상동염색체'), (330, 'R', '어머니 쪽 상동염색체')]
    for lx, c, lab in lg:
        chrom(p, lx, 72, 24, c, False)
        p.append(txt(lx + 16, 89, lab, 11, 700, MID, 'start'))
    p.append('<circle cx="620" cy="84" r="4.6" fill="%s" stroke="#FFFFFF" stroke-width="1.4"/>' % DARK)
    p.append(txt(634, 89, '동원체 — 원 하나가 염색체 하나다(분체가 둘이어도)',
                 11, 700, MID, 'start'))

    CW, X0, GAP = 288, 24, 24
    counts = []
    for ci, (head, (hf, hs, ht), mid_cells, gametes, note) in enumerate(CASES):
        x = X0 + ci * (CW + GAP)
        cx = x + CW / 2
        p.append(box(x, 116, CW, 40, hf, hs, 1.6))
        p.append(txt(cx, 141, head, 13, 700, ht))
        p.append(txt(cx, 174, note, 10, 700, GREY))

        # 모세포 — 복제된 상동염색체 한 쌍
        p.append(txt(cx, 196, '모세포 (2n = 2, 복제 끝)', 10.5, 700, MID))
        cell(p, cx, 202, 150, 82, ['B', 'R'], True)

        p.append(txt(cx, 306, '감수 I 뒤 — 세포 둘', 10.5, 700, MID))
        for k, items in enumerate(mid_cells):
            cell(p, cx - 68 + k * 136, 312, 118, 82, items, True, '안 받았다')

        p.append(txt(cx, 416, '감수 II 뒤 — 배우자 넷', 10.5, 700, MID))
        gw = 62
        for k, items in enumerate(gametes):
            gx = cx - 1.5 * (gw + 8) + k * (gw + 8)
            cell(p, gx, 422, gw, 74, items, False, '0개')
            lab = {0: 'n−1', 1: 'n', 2: 'n+1'}[len(items)]
            fill = OK_T if len(items) == N else BAD_T
            p.append(txt(gx, 512, lab, 12, 700, fill))

        normal = sum(1 for g in gametes if len(g) == N)
        counts.append(normal)
        bf, bs, bt = (OK_F, OK_S, OK_T) if normal else (BAD_F, BAD_S, BAD_T)
        if 0 < normal < 4:
            bf, bs, bt = WRN_F, WRN_S, WRN_T
        p.append(box(x + 24, 524, CW - 48, 46, bf, bs, 1.6))
        p.append(txt(cx, 553, '정상 배우자 %d개' % normal, 14, 700, bt))

    # ── 검산 ①  정상 배우자 수
    assert counts == [4, 0, 2], '정상 배우자 수가 4·0·2가 아니다: %s' % counts

    # ── 검산 ②  동원체(원)를 실제로 센다 — 배우자 줄에 그린 원의 총수
    drawn = ''.join(p)
    want_circles = sum(len(g) for _, _, mids, gs, _ in CASES
                       for g in gs) \
        + sum(len(m) for _, _, mids, _, _ in CASES for m in mids) \
        + sum(2 for _ in CASES) + 2 + 1     # 모세포 2개씩 · 범례 막대 2 · 범례 동원체 1
    got = drawn.count('<circle')
    assert got == want_circles, '동원체 수가 안 맞는다 그린 것 %d · 세어야 할 것 %d' % (got, want_circles)

    # ── 아래 띠 1 : n+1 칸의 속
    p.append(txt(24, 606, '★ n+1 칸을 열어 보면 색이 다르다 — 여기서도 I과 II가 갈린다',
                 12.5, 700, GREY, 'start'))
    p.append(box(24, 616, 912, 96, '#FFFFFF', PALE_S, 1.3))
    chrom(p, 150, 636, 56, 'B', False)
    chrom(p, 176, 636, 56, 'R', False)
    p.append(txt(163, 706, '파랑 + 주황', 11, 700, MID))
    p.append(txt(210, 652, '감수 I 비분리의 n+1', 12, 700, BAD_T, 'start'))
    p.append(txt(210, 672, '서로 다른 상동염색체 둘이 함께 들어갔다', 11, 700, MID, 'start'))
    p.append('<line x1="480" y1="628" x2="480" y2="700" stroke="%s" stroke-width="1.2"/>' % LINE)
    chrom(p, 570, 636, 56, 'R', False)
    chrom(p, 596, 636, 56, 'R', False)
    p.append(txt(583, 706, '주황 + 주황', 11, 700, MID))
    p.append(txt(630, 652, '감수 II 비분리의 n+1', 12, 700, WRN_T, 'start'))
    p.append(txt(630, 672, '같은 염색체의 자매염색분체 둘이 함께 들어갔다', 11, 700, MID, 'start'))

    # ── 아래 띠 2 : 그 배우자가 수정되면
    p.append(txt(24, 740, '그 배우자가 수정되면 — 많아도 적어도 탈이 난다',
                 12.5, 700, GREY, 'start'))
    p.append(box(24, 750, 912, 96, '#FFFFFF', PALE_S, 1.3))
    p.append(box(44, 766, 424, 64, WRN_F, WRN_S, 1.4))
    p.append(txt(256, 790, 'n+1 → 3염색체성(2n+1)', 12.5, 700, WRN_T))
    p.append(txt(256, 814, '살아남기도 하지만 유전자 용량이 어긋나 표현형 이상이 생긴다',
                 10.5, 700, MID))
    p.append(box(492, 766, 424, 64, BAD_F, BAD_S, 1.4))
    p.append(txt(704, 790, 'n−1 → 1염색체성(2n−1)', 12.5, 700, BAD_T))
    p.append(txt(704, 814, '필수 유전자 수가 모자라 정상 발달이 어려워 대개 치명적이다',
                 10.5, 700, MID))

    p.append('<line x1="14" y1="866" x2="946" y2="866" stroke="%s" stroke-width="1.3"/>' % LINE)
    p.append(txt(480, 888, '★ 문제를 보면 배우자 넷 중 정상을 먼저 센다 — 0이면 I, 2면 II다',
                 12.5, 700, DARK))

    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg, '백틱·역슬래시가 들어가면 주입이 깨진다'
    for need in ['정상 배우자 4개', '정상 배우자 0개', '정상 배우자 2개',
                 'n+1', 'n−1', '파랑 + 주황', '주황 + 주황',
                 '3염색체성(2n+1)', '1염색체성(2n−1)']:
        assert need in svg, '그림에 %s 가 없다' % need
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))
    print('정상 배우자 수 %s · 동원체 %d개 (검산 통과)' % (counts, got))


if __name__ == '__main__':
    main()

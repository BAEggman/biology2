#!/usr/bin/env python3
"""d09p01 「요소와 요산 — 구간마다 다르게 다룬다」 SVG 생성기.

★ 왜 도해인가 — 이 묶음의 카드는 전부 「어느 구간에서 어떻게 다루는가」를 묻는다.
  s17 의 그림 판들은 구간을 하나씩 따로 그린다(사구체 · 헨레 · 원위 · 집합관).
  구간을 가로로 늘어놓고 물질을 세로로 놓아야 비로소 「같은 물질이 구간마다 다르다」가 보인다.
  ★ 순서·구간을 묻는 카드는 d 계열로 — 덱이 이미 세운 규칙이다.

  띠1  구간 넷 — 사구체 · 근위세뇨관 · 얇은 하행각 · 안쪽 수질 집합관
  띠2  요소 — 네 칸 다 채워진다 (여과 · 수동 재흡수 · 일부 이동 · 재순환)
  띠3  요산 — 두 칸만 채워지고, 근위 칸이 유일하게 「둘 다」다
  띠4  되찾는 방식 둘 — 밀어 올리는 것(능동)과 따라 흐르는 것(수동)
  띠5  급소 한 줄 — 되돌아오는 것은 요소뿐이고 그것이 극대 농축뇨를 만든다
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d09p01.svg')

W, H = 960, 828
DARK, MID, GREY, LINE = '#374151', '#6B7280', '#9CA3AF', '#E5E7EB'
UREA_F, UREA_S, UREA_T = '#FEF3C7', '#D97706', '#92400E'      # 요소 — 누런 요
URIC_F, URIC_S, URIC_T = '#F3F4F6', '#6B7280', '#374151'      # 요산 — 흰 요
ACT_F, ACT_S, ACT_T = '#CCFBF1', '#0F766E', '#115E59'         # 능동
PAS_F, PAS_S, PAS_T = '#E0E7FF', '#4338CA', '#3730A3'         # 수동
ACC_F, ACC_S, ACC_T = '#FEE2E2', '#DC2626', '#991B1B'         # 급소


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def box(x, y, w, h, f, s, sw=1.4, r=8):
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" stroke="%s" '
            'stroke-width="%g"/>' % (x, y, w, h, r, f, s, sw))


SEG = ['사구체', '근위세뇨관', '얇은 하행각', '안쪽 수질 집합관']
X0, CW, GAP = 168, 186, 8
def cx(i):  return X0 + i * (CW + GAP)
def ccx(i): return cx(i) + CW / 2


def main():
    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td09 dd09">' % (W, H)]
    p.append('<title id="td09">요소와 요산을 구간마다 어떻게 다루는가</title>')
    p.append('<desc id="dd09">네프론을 지나는 순서대로 사구체, 근위세뇨관, 얇은 하행각, '
             '안쪽 수질 집합관 네 구간을 가로로 늘어놓고, 요소와 요산이 각 구간에서 어떻게 '
             '다루어지는지를 두 줄로 적은 표다. 요소는 네 구간에서 모두 무슨 일인가가 일어나고, '
             '요산은 사구체와 근위세뇨관 두 곳에서만 일이 일어나며 근위세뇨관 칸만 재흡수와 분비가 '
             '함께 일어난다. 아래에는 되찾는 방식을 능동과 수동 둘로 갈라 각각에 해당하는 물질을 '
             '적었고, 요산은 수동 쪽에 있다. 맨 아래 한 줄은 되돌아오는 것이 요소뿐이며 그것이 '
             '가장 진한 오줌을 만든다는 것이다.</desc>')

    # ── 제목
    p.append(txt(480, 34, '요소와 요산 — 같은 길을 지나는데 구간마다 다르게 다룬다', 15, 700, DARK))
    p.append('<line x1="24" y1="48" x2="936" y2="48" stroke="%s" stroke-width="1.3"/>' % LINE)

    # ── 띠1 : 구간 넷
    y1 = 66
    p.append(txt(30, y1 + 28, '지나는 차례', 11.5, 700, MID, 'start'))
    for i, sname in enumerate(SEG):
        p.append(box(cx(i), y1, CW, 44, '#FFFFFF', GREY, 1.4))
        p.append(txt(ccx(i), y1 + 21, sname, 12.5, 700, DARK))
        p.append(txt(ccx(i), y1 + 36, '%d' % (i + 1), 10.5, 700, GREY))
        if i < 3:
            p.append('<path d="M%g %g L%g %g" stroke="%s" stroke-width="1.6" fill="none" '
                     'marker-end="url(#ar)"/>' % (cx(i) + CW + 1, y1 + 22, cx(i) + CW + GAP - 2, y1 + 22, GREY))
    p.append('<defs><marker id="ar" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" '
             'markerHeight="6" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="%s"/></marker></defs>' % GREY)

    # ── 띠2 : 요소
    y2 = 132
    UREA = [
        ['그냥 걸러진다', '작고 자유로워', '막는 것이 없다'],
        ['물이 먼저 빠져', '농도가 오르면', '따라 나간다 — 수동'],
        ['일부만', '수동으로', '든다'],
        ['나갔다가', '헨레를 거쳐', '도로 들어온다'],
    ]
    p.append(box(24, y2, 128, 118, UREA_F, UREA_S, 1.6))
    p.append(txt(88, y2 + 34, '요소', 16, 700, UREA_T))
    p.append(txt(88, y2 + 56, '펴서 깔린 요', 10.5, 700, UREA_T))
    p.append(txt(88, y2 + 76, '네 칸이', 10.5, 700, MID))
    p.append(txt(88, y2 + 92, '모두 찬다', 10.5, 700, MID))
    for i, cell in enumerate(UREA):
        p.append(box(cx(i), y2, CW, 118, '#FFFFFF', UREA_S, 1.4))
        for j, line in enumerate(cell):
            p.append(txt(ccx(i), y2 + 36 + j * 22, line, 12, 700, DARK))
    p.append(txt(ccx(3), y2 + 106, '★ 재순환', 11, 700, UREA_T))

    # ── 띠3 : 요산
    y3 = 268
    p.append(box(24, y3, 128, 108, URIC_F, URIC_S, 1.6))
    p.append(txt(88, y3 + 32, '요산', 16, 700, URIC_T))
    p.append(txt(88, y3 + 54, '접어 쌓은 요', 10.5, 700, URIC_T))
    p.append(txt(88, y3 + 74, '두 칸만', 10.5, 700, MID))
    p.append(txt(88, y3 + 90, '찬다', 10.5, 700, MID))
    URIC = [
        (['그냥 걸러진다'], False),
        (['되찾기도 하고', '내보내기도 한다', '★ 둘 다 일어난다'], True),
        ([], False),
        ([], False),
    ]
    for i, (cell, hot) in enumerate(URIC):
        if not cell:
            p.append(box(cx(i), y3, CW, 108, '#FBFBFA', LINE, 1.2))
            p.append(txt(ccx(i), y3 + 60, '따로 말하지 않는다', 11, 700, GREY))
            continue
        p.append(box(cx(i), y3, CW, 108, ACC_F if hot else '#FFFFFF',
                     ACC_S if hot else URIC_S, 1.8 if hot else 1.4))
        base = y3 + 40 if len(cell) == 3 else y3 + 60
        for j, line in enumerate(cell):
            p.append(txt(ccx(i), base + j * 22, line, 12, 700, ACC_T if hot else DARK))

    # ── 띠4 : 되찾는 방식 둘
    y4 = 402
    p.append(txt(30, y4 + 20, '되찾는 방식', 11.5, 700, MID, 'start'))
    p.append(box(24, y4 + 34, 448, 128, ACT_F, ACT_S, 1.6))
    p.append(txt(248, y4 + 62, '밀어 올린다 — 능동', 14, 700, ACT_T))
    p.append(txt(248, y4 + 88, '포도당 · 아미노산', 13, 700, DARK))
    p.append(txt(248, y4 + 112, '나트륨 · 칼륨', 13, 700, DARK))
    p.append(txt(248, y4 + 140, '값을 치러야 거슬러 올릴 수 있다', 10.5, 700, MID))

    p.append(box(488, y4 + 34, 448, 128, PAS_F, PAS_S, 1.6))
    p.append(txt(712, y4 + 62, '따라 흐른다 — 수동', 14, 700, PAS_T))
    p.append(txt(712, y4 + 88, '중탄산염 · 염화 이온 · 물', 13, 700, DARK))
    p.append(txt(712, y4 + 112, '그리고 요산', 13, 700, PAS_T))
    p.append(txt(712, y4 + 140, '기울기가 나면 저절로 따라간다', 10.5, 700, MID))

    # ── 띠5 : 급소
    y5 = 592
    p.append(box(24, y5, 912, 96, ACC_F, ACC_S, 1.6))
    p.append(txt(480, y5 + 28, '★ 되돌아오는 것은 요소뿐이다', 14, 700, ACC_T))
    p.append(txt(480, y5 + 54,
                 '나간 요소가 헨레로 되돌아와 안쪽 수질을 짜게 만들고, 그 짠 벽이 물을 더 끌어낸다',
                 12, 700, DARK))
    p.append(txt(480, y5 + 78,
                 '오래 목마를수록 이 되돌이가 커진다 — 가장 진한 오줌은 이렇게 만들어진다',
                 11.5, 700, MID))

    # ── 맨 아래 한 줄
    y6 = 706
    p.append(box(24, y6, 912, 76, '#FFFFFF', GREY, 1.4))
    p.append(txt(480, y6 + 30, '한 줄로 — 요소는 네 구간 다 손을 타고, 요산은 근위에서만 둘 다 겪는다',
                 13, 700, DARK))
    p.append(txt(480, y6 + 56, '두 물건은 같은 「요」인데 펴면 요소이고 접어 쌓으면 요산이다 (44-5)',
                 11.5, 700, MID))

    p.append('<line x1="14" y1="%g" x2="946" y2="%g" stroke="%s" stroke-width="1.3"/>'
             % (H - 32, H - 32, LINE))
    p.append(txt(480, H - 12, '구간을 가로로 놓아야 「같은 물질이 구간마다 다르다」가 보인다',
                 12, 700, DARK))
    p.append('</svg>')

    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg
    for t in re.findall(r'<text[^>]*>(.*?)</text>', svg):
        assert '<' not in t and '&' not in t, t
    for need in ['사구체', '근위세뇨관', '얇은 하행각', '안쪽 수질 집합관',
                 '되찾기도 하고', '내보내기도 한다', '일부만', '수동으로',
                 '밀어 올린다 — 능동', '따라 흐른다 — 수동', '그리고 요산',
                 '되돌아오는 것은 요소뿐이다']:
        assert need in svg, need
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))


if __name__ == '__main__':
    main()

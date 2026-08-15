#!/usr/bin/env python3
"""d05p07 「검정교배 계산판」 SVG 생성기.

★ 이 단원의 계산 문항은 전부 한 줄에서 나온다
      재조합형 ÷ 전체 × 100 = 교차율(%) = 지도거리(cM)
  묻는 방향만 셋이다 — 세는 쪽 · 거꾸로 세는 쪽 · 부모형을 묻는 쪽.

  띠1 세 방향 공식
  띠2 재조합형 수가 바로 주어질 때 (여섯 보기)
  띠3 네 클래스가 주어질 때 — 큰 둘이 부모형, 작은 둘이 재조합형 (다섯 보기)
  띠4 거꾸로 묻는 것 — 비율에서 마릿수, 부모형에서 재조합형

숫자가 곧 사실이라 손으로 적지 않는다. 표의 값은 전부 **코드가 계산해서** 찍고,
찍은 뒤 스스로 검산한다(assert).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d05p07.svg')

W, H = 880, 910

DARK, MID, GREY, LINE = '#374151', '#6B7280', '#9CA3AF', '#E5E7EB'
PALE, PALE_S = '#F9FAFB', '#D1D5DB'
OK_F, OK_S, OK_T = '#CCFBF1', '#0F766E', '#115E59'      # 세는 쪽
ACC_F, ACC_S, ACC_T = '#FEF3C7', '#D97706', '#92400E'   # 거꾸로 세는 쪽
ROSE_F, ROSE_S, ROSE_T = '#FFE4E6', '#BE123C', '#9F1239' # 부모형 쪽
PAR, PAR_D = '#93C5FD', '#1D4ED8'                        # 부모형 막대
REC, REC_D = '#FDA4AF', '#BE123C'                        # 재조합형 막대


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def box(x, y, w, h, f, s, sw=1.4, r=9):
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" stroke="%s" '
            'stroke-width="%g"/>' % (x, y, w, h, r, f, s, sw))


def fmt(v):
    """1000 → 1,000 · 9.5 → 9.5 · 17.0 → 17"""
    if isinstance(v, float):
        return ('%.1f' % v).rstrip('0').rstrip('.')
    return '{:,}'.format(v)


def main():
    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td12 dd12">' % (W, H)]
    p.append('<title id="td12">검정교배 계산판 — 재조합형 나누기 전체 곱하기 100</title>')
    p.append('<desc id="dd12">연관 검정교배의 계산 문항을 한 판에 모은 표다. '
             '맨 위에 세 방향의 공식이 있다. 재조합형을 전체로 나누고 100을 곱하면 교차율이고 '
             '그 값이 곧 지도거리다. 거꾸로 전체에 교차율을 곱하면 재조합형 마릿수가 나오고, '
             '전체에서 재조합형을 빼면 부모형이다. '
             '가운데 표는 재조합형 수가 바로 주어진 여섯 보기이고, '
             '그 아래 표는 네 클래스가 주어졌을 때 큰 둘을 부모형 작은 둘을 재조합형으로 갈라 푸는 다섯 보기이며, '
             '맨 아래 표는 비율에서 마릿수를 거꾸로 구하거나 부모형에서 재조합형을 구하는 여섯 보기다.</desc>')
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="#FFFFFF"/>' % (W, H))

    p.append(txt(440, 28, '검정교배 계산판 — 재조합형 ÷ 전체 × 100', 16, 700, DARK))
    p.append(txt(440, 48, '★ 이 단원의 계산 문항은 전부 이 한 줄에서 나온다. 묻는 방향만 셋이다',
                 11, 700, MID))

    # ── 띠 1 : 세 방향 공식
    y0 = 64
    cards = [
        ('① 세는 쪽', '재조합형 ÷ 전체 × 100', '= 교차율(%) = 지도거리(cM)', OK_F, OK_S, OK_T),
        ('② 거꾸로 세는 쪽', '전체 × 교차율 ÷ 100', '= 재조합형 마릿수', ACC_F, ACC_S, ACC_T),
        ('③ 부모형을 묻는 쪽', '전체 − 재조합형', '= 부모형 (비율도 100 − 교차율)', ROSE_F, ROSE_S, ROSE_T),
    ]
    cw, gap = 272, 12
    for i, (head, eq, note, f, s, t) in enumerate(cards):
        x = 22 + i * (cw + gap)
        p.append(box(x, y0, cw, 104, f, s, 1.5))
        p.append(txt(x + cw / 2, y0 + 24, head, 11.5, 700, MID))
        p.append(txt(x + cw / 2, y0 + 52, eq, 14, 700, t))
        p.append(txt(x + cw / 2, y0 + 80, note, 10.5, 700, MID))

    # ── 띠 2 : 재조합형 수가 바로 주어질 때
    y1 = 190
    rows2 = [(1000, 170), (200, 18), (400, 38), (600, 54), (1000, 95), (1000, 85), (1000, 320)]
    p.append(txt(22, y1 + 14, '② 재조합형 수가 바로 주어지면 — 나누고 100을 곱한다',
                 12, 700, GREY, 'start'))
    p.append(box(22, y1 + 24, 836, 192, '#FFFFFF', PALE_S, 1.3))
    colx = [92, 260, 430, 700]
    p.append(txt(colx[0], y1 + 50, '전체', 11, 700, MID))
    p.append(txt(colx[1], y1 + 50, '재조합형', 11, 700, MID))
    p.append(txt(colx[2], y1 + 50, '나눗셈', 11, 700, MID))
    p.append(txt(colx[3], y1 + 50, '교차율 = 지도거리', 11, 700, MID))
    p.append('<line x1="40" y1="%g" x2="840" y2="%g" stroke="%s" stroke-width="1"/>'
             % (y1 + 60, y1 + 60, LINE))
    for i, (tot, rec) in enumerate(rows2):
        yy = y1 + 82 + i * 20
        val = rec / tot * 100
        assert abs(val - round(val, 1)) < 1e-9
        p.append(txt(colx[0], yy, fmt(tot), 11.5, 700, DARK))
        p.append(txt(colx[1], yy, fmt(rec), 11.5, 700, REC_D))
        p.append(txt(colx[2], yy, '%s ÷ %s × 100' % (fmt(rec), fmt(tot)), 11, 700, MID))
        p.append(txt(colx[3], yy, '%s %% = %s cM' % (fmt(round(val, 1)), fmt(round(val, 1))),
                     12, 700, OK_T))

    # ── 띠 3 : 네 클래스가 주어질 때
    y2 = 416
    rows3 = [(82, 80, 19, 19), (470, 468, 31, 31), (146, 144, 55, 55),
             (355, 355, 145, 145), (350, 348, 151, 151)]
    p.append(txt(22, y2 + 14, '③ 네 무리가 주어지면 — 큰 둘이 부모형, 작은 둘이 재조합형이다',
                 12, 700, GREY, 'start'))
    p.append(box(22, y2 + 24, 836, 190, '#FFFFFF', PALE_S, 1.3))
    cx3 = [150, 330, 460, 600, 760]
    p.append(txt(cx3[0], y2 + 50, '네 무리', 11, 700, MID))
    p.append(txt(cx3[1], y2 + 50, '부모형 합', 11, 700, PAR_D))
    p.append(txt(cx3[2], y2 + 50, '재조합형 합', 11, 700, REC_D))
    p.append(txt(cx3[3], y2 + 50, '전체', 11, 700, MID))
    p.append(txt(cx3[4], y2 + 50, '교차율', 11, 700, MID))
    p.append('<line x1="40" y1="%g" x2="840" y2="%g" stroke="%s" stroke-width="1"/>'
             % (y2 + 60, y2 + 60, LINE))
    for i, four in enumerate(rows3):
        yy = y2 + 82 + i * 22
        s4 = sorted(four, reverse=True)
        par, rec = s4[0] + s4[1], s4[2] + s4[3]
        tot = par + rec
        val = rec / tot * 100
        p.append(txt(cx3[0], yy, ' · '.join(fmt(v) for v in four), 11, 700, DARK))
        p.append(txt(cx3[1], yy, fmt(par), 11.5, 700, PAR_D))
        p.append(txt(cx3[2], yy, fmt(rec), 11.5, 700, REC_D))
        p.append(txt(cx3[3], yy, fmt(tot), 11, 700, MID))
        p.append(txt(cx3[4], yy, '%s %%' % fmt(round(val, 1)), 12, 700, OK_T))
    p.append(txt(440, y2 + 200,
                 '★ 맨 아래 줄은 재조합형이 부모형에 거의 맞먹는다 — '
                 '연관은 있지만 꽤 멀다(50 %에 가까우면 독립처럼 본다)', 11, 700, ACC_T))

    # ── 띠 4 : 거꾸로 묻는 것
    y3 = 640
    p.append(txt(22, y3 + 14, '④ 거꾸로 묻는 것 — 비율에서 마릿수로, 부모형에서 재조합형으로',
                 12, 700, GREY, 'start'))
    p.append(box(22, y3 + 24, 836, 192, '#FFFFFF', PALE_S, 1.3))
    back = [
        ('교차율 32 %, 전체 500', '500 × 32 ÷ 100', '재조합형 160마리'),
        ('교차율 18.5 %, 전체 1,000', '1,000 × 18.5 ÷ 100', '재조합형 185마리'),
        ('교차율 27 %, 전체 200', '200 − (200 × 27 ÷ 100)', '부모형 146마리'),
        ('교차율 29 %', '100 − 29', '부모형 71 %'),
        ('부모형 760, 재조합형 240', '240 ÷ 1,000 × 100', '교차율 24 %'),
        ('전체 1,000 중 부모형 830', '(1,000 − 830) ÷ 1,000 × 100', '재조합형 17 %'),
    ]
    assert 500 * 32 // 100 == 160 and round(1000 * 18.5 / 100) == 185
    assert 200 - round(200 * 27 / 100) == 146 and 100 - 29 == 71
    assert round(240 / 1000 * 100) == 24 and round((1000 - 830) / 1000 * 100) == 17
    for i, (q, mid, ans) in enumerate(back):
        yy = y3 + 56 + i * 26
        p.append(txt(52, yy, q, 11, 700, DARK, 'start'))
        p.append(txt(470, yy, mid, 11, 700, MID))
        p.append(txt(830, yy, ans, 12, 700, ACC_T, 'end'))

    p.append('<line x1="14" y1="%g" x2="866" y2="%g" stroke="%s" stroke-width="1.3"/>'
             % (H - 40, H - 40, LINE))
    p.append(txt(440, H - 16,
                 '★ 먼저 부모형과 재조합형을 가른다 — 수만 보고 아무 둘이나 더하면 틀린다',
                 12, 700, DARK))

    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg, '백틱·역슬래시가 들어가면 주입이 깨진다'
    for need in ['17 % = 17 cM', '9 % = 9 cM', '9.5 % = 9.5 cM', '32 % = 32 cM',
                 '8.5 % = 8.5 cM', '19 %', '6.2 %', '27.5 %', '29 %', '30.2 %']:
        assert need in svg, '표에 %s 가 없다' % need
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 → %s' % (len(svg), OUT))


if __name__ == '__main__':
    main()

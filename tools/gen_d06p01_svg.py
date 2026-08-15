#!/usr/bin/env python3
"""d06p01 「나선의 자」 SVG 생성기 — 이중나선의 치수와 셈.

★ 왜 도해인가
  s38p01(사다리 한 바퀴)의 그림은 칸을 열둘로 그렸다. 「한 바퀴에 열 칸」을 그 그림에 걸면
  ★그린 것만 건다를 어긴다. 수는 그림이 아니라 자로 그린다 — 여기서는 열 칸이 정확히 열 칸이다.

  한 바퀴 = 10 염기쌍 = 3.4 nm · 염기쌍 사이 = 0.34 nm
  21,000 bp ÷ 10 = 2,100 바퀴 · 21,000 × 0.34 nm ≈ 7.1 µm

  왼쪽 자에서 두 기둥이 정확히 두 번 엇갈린다 — 그것이 한 바퀴다.

좌표와 개수가 곧 사실이라 손으로 쓰지 않는다.
"""
import os
import math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', '_d06p01.svg')

W, H = 880, 536
N = 10                                   # 한 바퀴에 놓인 염기쌍 수 — 이 값이 곧 사실이다
TOP, SLICE = 104, 33                     # 자의 위끝과 한 칸 높이
CX, AMP = 205, 84                        # 나선 중심축과 진폭

DARK, MID, GREY, LINE = '#374151', '#6B7280', '#9CA3AF', '#E5E7EB'
RAIL, RAIL_D = '#BFDBFE', '#1D4ED8'      # 당-인산 골격
RUNG, RUNG_D = '#CBD5E1', '#475569'      # 염기쌍 한 칸 — 색으로 A-T/G-C를 가르지 않는다
PALE, PALE_S = '#F9FAFB', '#D1D5DB'
ACC_F, ACC_S, ACC_T = '#FEF3C7', '#D97706', '#92400E'
OK_F, OK_S, OK_T = '#CCFBF1', '#0F766E', '#115E59'

BOT = TOP + N * SLICE                    # 자의 아래끝


def txt(x, y, t, size=12, weight=700, fill=DARK, anchor='middle'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%d" '
            'fill="%s">%s</text>' % (x, y, anchor, size, weight, fill, t))


def phase(t):
    """t는 0..1. 한 바퀴 동안 코사인이 두 번 0을 지난다 = 기둥이 두 번 엇갈린다."""
    return math.cos(2 * math.pi * t + math.pi / N)


def rail_path(sign):
    pts = []
    for k in range(0, 201):
        t = k / 200
        y = TOP + t * (N * SLICE)
        x = CX + sign * AMP * phase(t)
        pts.append('%.1f %.1f' % (x, y))
    return 'M' + ' L'.join(pts)


def main():
    p = ['<svg viewBox="0 0 %d %d" role="img" aria-labelledby="td11 dd11">' % (W, H)]
    p.append('<title id="td11">나선의 자 — 한 바퀴는 10 염기쌍이고 3.4 나노미터다</title>')
    p.append('<desc id="dd11">왼쪽은 이중나선 한 바퀴를 옆에서 본 자다. 두 기둥이 위에서 아래까지 '
             '정확히 두 번 엇갈리는데 그것이 한 바퀴이고, 그 사이에 가로 칸이 정확히 열 개 놓여 있다. '
             '칸마다 1부터 10까지 번호가 붙어 있다. 왼쪽 세로 화살표가 그 한 바퀴 전체를 3.4 나노미터로 재고, '
             '오른쪽 작은 괄호가 칸 하나를 0.34 나노미터로 잰다. '
             '오른쪽에는 셈 세 가지가 있다. 3.4를 10으로 나누면 0.34, '
             '21,000 염기쌍을 10으로 나누면 2,100바퀴, '
             '21,000에 0.34 나노미터를 곱하면 약 7.1 마이크로미터다.</desc>')
    p.append('<defs>'
             '<marker id="ad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
             '<marker id="au" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto"><path d="M10 0 L0 5 L10 10 z" fill="%s"/></marker>'
             '</defs>' % (ACC_S, ACC_S))
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="#FFFFFF"/>' % (W, H))

    p.append(txt(440, 28, '나선의 자 — 한 바퀴는 10 염기쌍이고 3.4 nm다', 16, 700, DARK))
    p.append(txt(440, 48, '★ s38p01의 사다리는 칸을 세는 그림이 아니다. 수는 여기서 센다',
                 11, 700, MID))

    # ── 왼쪽: 자
    p.append('<rect x="22" y="68" width="404" height="%g" rx="9" fill="#FFFFFF" stroke="%s" '
             'stroke-width="1.3"/>' % (BOT + 58 - 68, PALE_S))
    p.append(txt(36, 90, '한 바퀴를 옆에서 본 것', 11.5, 700, GREY, 'start'))

    # 칸(염기쌍) — 정확히 N개
    for i in range(N):
        t = (i + 0.5) / N
        y = TOP + (i + 0.5) * SLICE
        half = abs(AMP * phase(t))
        p.append('<rect x="%g" y="%g" width="%g" height="9" rx="4.5" fill="%s" stroke="%s" '
                 'stroke-width="1.2"/>' % (CX - half, y - 4.5, max(2 * half, 14), RUNG, RUNG_D))
        p.append(txt(316, y + 4, str(i + 1), 10.5, 700, GREY, 'start'))

    # 기둥 둘 — 정확히 두 번 엇갈린다
    for sign in (1, -1):
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round" '
                 'opacity="0.95"/>' % (rail_path(sign), RAIL))
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" '
                 'stroke-linecap="round"/>' % (rail_path(sign), RAIL_D))

    # 왼쪽 치수 — 한 바퀴 전체
    p.append('<line x1="72" y1="%g" x2="72" y2="%g" stroke="%s" stroke-width="1.8" '
             'marker-start="url(#au)" marker-end="url(#ad)"/>' % (TOP, BOT, ACC_S))
    p.append('<line x1="66" y1="%g" x2="300" y2="%g" stroke="%s" stroke-width="1" '
             'stroke-dasharray="3 3"/>' % (TOP, TOP, LINE))
    p.append('<line x1="66" y1="%g" x2="300" y2="%g" stroke="%s" stroke-width="1" '
             'stroke-dasharray="3 3"/>' % (BOT, BOT, LINE))
    ymid = (TOP + BOT) / 2
    p.append(txt(58, ymid - 6, '3.4 nm', 13, 700, ACC_T, 'end'))
    p.append(txt(58, ymid + 12, '한 바퀴', 10.5, 700, MID, 'end'))

    # 오른쪽 치수 — 칸 하나
    sy0 = TOP + 2 * SLICE
    sy1 = sy0 + SLICE
    p.append('<line x1="348" y1="%g" x2="348" y2="%g" stroke="%s" stroke-width="1.8" '
             'marker-start="url(#au)" marker-end="url(#ad)"/>' % (sy0, sy1, ACC_S))
    p.append('<line x1="330" y1="%g" x2="354" y2="%g" stroke="%s" stroke-width="1"/>'
             % (sy0, sy0, LINE))
    p.append('<line x1="330" y1="%g" x2="354" y2="%g" stroke="%s" stroke-width="1"/>'
             % (sy1, sy1, LINE))
    p.append(txt(358, (sy0 + sy1) / 2 - 2, '0.34 nm', 11.5, 700, ACC_T, 'start'))
    p.append(txt(358, (sy0 + sy1) / 2 + 13, '칸 하나', 10, 700, MID, 'start'))

    p.append(txt(224, BOT + 32, '★ 기둥이 두 번 엇갈리는 사이에 칸이 정확히 열 개다',
                 12, 700, DARK))

    # ── 오른쪽: 셈 세 가지
    bx, bw = 448, 410
    cards = [
        ('한 바퀴를 열로 나눈다', '3.4 nm ÷ 10 = 0.34 nm',
         '염기쌍 하나가 차지하는 높이', OK_F, OK_S, OK_T),
        ('염기쌍 수를 열로 나눈다', '21,000 bp ÷ 10 = 2,100 바퀴',
         '한 바퀴에 10 bp이므로 나누기만 하면 된다', ACC_F, ACC_S, ACC_T),
        ('염기쌍 수에 0.34을 곱한다', '21,000 × 0.34 nm ≈ 7,140 nm ≈ 7.1 μm',
         '같은 DNA를 길이로 물으면 이쪽이다', PALE, PALE_S, MID),
    ]
    ch, gap = 112, 16
    for i, (head, eq, note, f, s, t) in enumerate(cards):
        y = 88 + i * (ch + gap)
        p.append('<rect x="%g" y="%g" width="%g" height="%g" rx="9" fill="%s" stroke="%s" '
                 'stroke-width="1.5"/>' % (bx, y, bw, ch, f, s))
        p.append(txt(bx + bw / 2, y + 26, head, 11.5, 700, MID))
        p.append(txt(bx + bw / 2, y + 60, eq, 15.5, 700, t))
        p.append(txt(bx + bw / 2, y + 88, note, 10.5, 700, MID))

    p.append('<line x1="14" y1="%g" x2="866" y2="%g" stroke="%s" stroke-width="1.3"/>'
             % (H - 44, H - 44, LINE))
    p.append(txt(440, H - 20,
                 '★ 「한 바퀴 = 10 bp = 3.4 nm」 하나만 외우면 나머지는 나누기와 곱하기다',
                 12, 700, DARK))

    p.append('</svg>')
    svg = ''.join(p)
    assert '`' not in svg and '\\' not in svg, '백틱·역슬래시가 들어가면 주입이 깨진다'
    # 칸이 정확히 N개 그려졌는지 스스로 센다
    assert svg.count('rx="4.5"') == N, '칸 수가 %d가 아니다' % N
    open(OUT, 'w', encoding='utf-8').write(svg)
    print('SVG %d바이트 · 칸 %d개 → %s' % (len(svg), N, OUT))


if __name__ == '__main__':
    main()

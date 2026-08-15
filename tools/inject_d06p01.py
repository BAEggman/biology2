#!/usr/bin/env python3
"""d06 「DNA 치수와 셈 도해」 신설 + d06p01 「나선의 자」.

★ 왜 새로 만드나 — s38p01의 새 그림은 칸이 열둘이다.
  「한 바퀴에 열 칸」을 그 그림에 걸면 ★그린 것만 건다를 어긴다.
  수는 그림이 아니라 자로 센다. 여기서는 칸이 정확히 열 개이고 번호까지 붙어 있다.

  E1-30 · E1-30#1 · E1-30#2 · E1-33 을 s38p01#8에서 여기로 옮긴다.
  (옮김은 test/baseline.json 의 pmapMoved 에 적어야 통과한다)
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')
SVGF = os.path.join(ROOT, 'tools', '_d06p01.svg')

BR = ('★ <b>수는 그림이 아니라 자로 센다</b> — 두 기둥이 <b>두 번 엇갈리는</b> 사이가 한 바퀴이고, '
      '그 사이에 칸이 <b>정확히 열 개</b>다. 한 바퀴가 <b>3.4 nm</b>이니 칸 하나는 '
      '<b>0.34 nm</b>이고, 염기쌍 수를 열로 나누면 바퀴 수가 나온다.')

BX = """<p><b>★ 한 줄만 외운다 — 한 바퀴 = 10 bp = 3.4 nm.</b> 이 단원의 숫자 문제는 전부 이 한 줄에서 나누기와 곱하기로 나온다. 외울 것은 하나뿐이고 나머지는 산수다.</p><p><b>왼쪽 자를 읽는 법.</b> 두 기둥이 위에서 아래까지 <b>정확히 두 번</b> 엇갈린다. 나선이 한 바퀴 돌면 두 가닥은 서로 두 번 자리를 바꾸므로, 두 번 엇갈리는 그 구간이 곧 <b>한 바퀴</b>다. 그 사이에 가로 칸이 <b>열 개</b> 놓여 있고 1부터 10까지 번호를 매겨 두었다. 세로 화살표가 그 구간 전체를 <b>3.4 nm</b>로 재고, 오른쪽 작은 괄호가 칸 하나를 <b>0.34 nm</b>로 잰다.</p><p><b>칸이 위아래에서 길고 가운데에서 짧은 까닭.</b> 나선을 옆에서 보면 염기쌍이 정면을 향할 때는 길게, 옆을 향할 때는 짧게 보인다. 길이가 변하는 것이 아니라 <b>보이는 각도</b>가 변하는 것이다. 기둥이 엇갈리는 자리에서 칸이 가장 짧아진다.</p><p><b>셈 세 가지.</b> ① <b>3.4 ÷ 10 = 0.34 nm</b> — 염기쌍 하나가 차지하는 높이다. ② <b>염기쌍 수 ÷ 10 = 바퀴 수</b> — 21,000 bp라면 <b>2,100바퀴</b>다. ③ <b>염기쌍 수 × 0.34 nm = 길이</b> — 21,000 bp라면 약 7,140 nm, 곧 <b>7.1 μm</b>다. 발문이 <b>바퀴 수</b>를 묻는지 <b>길이</b>를 묻는지만 갈라 보면 어느 셈인지 바로 정해진다.</p><p><b>기출이 꼬는 자리.</b> ① 「한 바퀴가 0.34 nm다」 → <b>거짓</b>(0.34는 칸 하나이고 한 바퀴는 3.4다. 자릿수 하나가 함정이다). ② 「21,000 bp면 21,000바퀴다」 → <b>거짓</b>(열로 나눈다). ③ 「바퀴 수와 길이는 같은 계산이다」 → <b>거짓</b>(바퀴는 나누기, 길이는 곱하기다).</p><p><b>s38p01과의 관계.</b> 저쪽 사다리 그림은 결합의 <b>자리</b>와 조각의 <b>생김새</b>를 가르는 그림이지 칸을 세는 그림이 아니다. 실제로 그 그림의 칸 수는 열이 아니다. <b>수를 묻는 문제는 이 자에서 푼다.</b></p>"""

ROWS = [
    ('왼쪽 자 — 두 기둥이 위에서 아래까지 정확히 두 번 엇갈린다',
     '두 가닥이 서로 두 번 자리를 바꾸는 그 구간이 <b>한 바퀴</b>다', []),

    ('★ 그 구간 안의 가로 칸 — 1부터 10까지 번호가 붙어 정확히 열 개다 · '
     '왼쪽 세로 화살표가 그 전체를 잰다',
     '이중나선은 <b>한 바퀴가 3.4 nm</b>이고 그 사이에 <b>10 염기쌍</b>이 들어간다',
     ['E1-30', 'E1-30#1', 'E1-30#2']),

    ('오른쪽 작은 괄호 — 칸 하나만 따로 잰다',
     '<b>0.34 nm</b>. 3.4 nm를 열로 나눈 값이고, 염기쌍 하나가 차지하는 높이다', []),

    ('오른쪽 가운데 셈 카드 — 21,000을 10으로 나눈다',
     '<b>21,000 bp → 2,100바퀴</b>. 한 바퀴에 10 bp이므로 나누기만 하면 된다',
     ['E1-33']),

    ('오른쪽 아래 셈 카드 — 21,000에 0.34을 곱한다',
     '같은 DNA를 <b>길이</b>로 물으면 이쪽이다 — 약 7,140 nm, 곧 7.1 μm. '
     '바퀴 수는 나누기, 길이는 곱하기다', []),

    ('칸이 위아래에서 길고 기둥이 엇갈리는 자리에서 짧다',
     '길이가 변하는 것이 아니라 옆에서 본 <b>각도</b>가 변하는 것이다', []),
]


def close_brace(t, i):
    op = t[i]
    cl = {'{': '}', '[': ']'}[op]
    d, q, j = 0, None, i
    while j < len(t):
        c = t[j]
        if q:
            if c == '\\':
                j += 2
                continue
            if c == q:
                q = None
        elif c in '"\'`':
            q = c
        elif c == op:
            d += 1
        elif c == cl:
            d -= 1
            if d == 0:
                return j
        j += 1
    raise SystemExit('괄호 안 닫힘')


def q2(s):
    assert '"' not in s and '\\' not in s, s
    return '"%s"' % s


def main():
    src = open(SK, encoding='utf-8').read()
    assert "{id:'d06'" not in src, '이미 있다'
    assert '`' not in BX and "'" not in BR
    svg = open(SVGF, encoding='utf-8').read().strip()
    assert '`' not in svg and '\\' not in svg, 'SVG에 백틱·역슬래시'
    assert svg.startswith('<svg') and svg.endswith('</svg>')

    i = src.index("{id:'d05',t:")
    e = close_brace(src, i)

    rows = []
    for prop, fact, cards in ROWS:
        r = '[' + q2(prop) + ',' + q2(fact)
        if cards:
            r += ',[' + ','.join(q2(c) for c in cards) + ']'
        rows.append(r + ']')

    panel = ("{id:'d06p01',t:'나선의 자',svg:`" + svg + "`,br:'" + BR + "',bx:`" + BX
             + "`,f:[" + ',\n     '.join(rows) + ']}')
    scene = ("{id:'d06',t:'DNA 치수와 셈 도해',gate:'E',unit:'수는 그림이 아니라 자로 센다',"
             "panels:[\n   " + panel + ']}')
    out = src[:e + 1] + ',\n\n' + scene + src[e + 1:]

    k = out.index("{id:'d06p01'")
    blk = out[k:close_brace(out, k) + 1]
    ids = re.findall(r"\{id:'([sd]\d+p\d+[ab]?)'", out)
    assert len(ids) == len(set(ids)), '패널 id 중복'
    assert ids.index('d06p01') == ids.index('d05p06') + 1, '위치 오류'
    cards = re.findall(r'"(E1-[\w#]+)"', blk)
    assert len(cards) == len(set(cards)), '카드 중복'
    print('패널 %d개 · d06p01 행 %d · 카드 %d장 · SVG %d바이트'
          % (len(ids), len(ROWS), len(cards), len(svg)))
    open(SK, 'w', encoding='utf-8').write(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())

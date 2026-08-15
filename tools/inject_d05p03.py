#!/usr/bin/env python3
"""d05p03 「성결정 네 체계」 — d05 세 번째 도해.

★ 문법 하나 — heterogametic은 「배우자를 두 종류 만드는 쪽」이다.
  체계 이름을 외우는 게 아니라 **칸 개수를 센다**. 칸이 하나면 homo, 둘이면 hetero.
  그림에서 굵은 주황 테두리가 쳐진 줄이 곧 hetero다.

  X-Y   암 XX → 칸 하나 / 수 XY → 칸 둘 ★   (사람·초파리)
  X-O   암 XX → 칸 하나 / 수 XO → 칸 둘 ★   (메뚜기·귀뚜라미. 한 칸은 성염색체가 없는 배우자)
  Z-W   암 ZW → 칸 둘 ★ / 수 ZZ → 칸 하나   (조류·일부 어류)
  반수체-2배체   성염색체로 안 갈린다 — 수정되면 암컷(2n), 안 되면 수컷(n)   (벌·개미)

아래에 사람에서 더 묻는 것 셋 — SRY · 약 2개월 · X 불활성화(바소체, 삼색 고양이).

⚠ 그린 것만 건다 — 반성유전·한성유전·종성유전(E0-93~110)은 여기 없다. 다음 도해에서 건다.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')
SVGF = os.path.join(ROOT, 'tools', '_d05p03.svg')

BR = ('★ <b>heterogametic = 배우자를 두 종류 만드는 쪽</b> — 체계 이름이 아니라 '
      '<b>칸 개수</b>를 센다. 굵은 주황 테두리가 쳐진 줄이 곧 그것이다. '
      '<b>X-Y와 X-O는 수컷, Z-W는 암컷</b>이고, <b>반수체-2배체</b>는 아예 성염색체로 갈리지 않아 '
      '<b>수정되었는가</b>가 성을 정한다.')

BX = """<p><b>★ 세는 것이 이름보다 쉽다.</b> homogametic과 heterogametic을 체계마다 외우려 들면 반드시 헷갈린다. 정의로 돌아가면 한 줄이다 — <b>배우자를 한 종류만 만들면 homo, 두 종류 만들면 hetero</b>다. 그림에서 각 성의 오른쪽 칸을 세기만 하면 된다. 칸이 둘인 줄에 굵은 주황 테두리가 쳐져 있다.</p><p><b>X-Y (사람·초파리).</b> 암컷은 XX라 어떤 배우자를 만들어도 X 하나뿐이다 — <b>칸 하나, homo</b>. 수컷은 XY라 X를 담은 배우자와 Y를 담은 배우자 두 가지가 나온다 — <b>칸 둘, hetero</b>. 사람의 일반적인 성결정 체계가 이것이다.</p><p><b>X-O (메뚜기·귀뚜라미).</b> 수컷에게 Y가 아예 없다. 그래도 배우자는 <b>X를 받은 것과 아무것도 못 받은 것</b> 두 가지다 — 그림에서 점선 막대가 그 「없음」이다. 그러니 <b>여전히 칸 둘, hetero는 수컷</b>이다. X-Y와 X-O의 공통점이 바로 이것 — <b>둘 다 수컷이 heterogametic</b>이다.</p><p><b>Z-W (조류·일부 어류).</b> 글자만 바뀐 게 아니라 <b>hetero인 성이 뒤집힌다</b>. 암컷이 ZW라 칸 둘, 수컷이 ZZ라 칸 하나다. 그래서 <b>암컷이 heterogametic</b>이다. X-Y와 Z-W를 나란히 두면 굵은 테두리가 <b>서로 반대 줄</b>에 있다 — 그것이 두 체계 비교의 답이다. 동물 종류에 따라 hetero인 성이 바뀌는 까닭도 이것이다: 체계마다 <b>두 종류의 성염색체를 갖는 성이 다르기</b> 때문이다.</p><p><b>반수체-2배체 (벌·개미).</b> 여기는 셀 칸이 없다. 성염색체가 성을 정하는 것이 아니라 <b>수정 여부</b>가 정한다. <b>수정란에서 발생하면 2배체(2n) 암컷</b>, <b>미수정란에서 발생하면 반수체(n) 수컷</b>이다. 수컷에게는 아버지가 없다는 말이 여기서 나온다.</p><p><b>사람에서 더 묻는 것.</b> ① <b>SRY</b> — Y 염색체의 성 결정 부위로, 배아에서 <b>정소 발달에 필수</b>다. Y 전체가 아니라 이 한 자리가 방아쇠다. ② 성에 대한 <b>해부학적 신호는 약 2개월 무렵</b> 나타나기 시작하고, 그전에는 겉으로 구분되지 않는다. ③ 포유류 암컷은 <b>두 X 중 하나를 불활성화</b>한다. 응축된 그것이 <b>바소체(Barr body)</b>이고, 세포마다 꺼지는 쪽이 달라 털색 유전자가 얼룩덜룩 나오는 것이 <b>삼색(calico) 고양이</b> 무늬다.</p><p><b>기출이 꼬는 자리.</b> ① 「heterogametic은 언제나 수컷이다」 → <b>거짓</b>(Z-W는 암컷). ② 「X-O 수컷은 배우자가 한 종류다」 → <b>거짓</b>(X를 받은 것과 못 받은 것, 둘이다). ③ 「벌의 수컷은 XY다」 → <b>거짓</b>(성염색체가 아니라 반수체다). ④ 「바소체는 수컷에서 관찰된다」 → <b>거짓</b>(두 X가 있는 암컷에서다).</p>"""

ROWS = [
    ('첫째 열 — 사람과 초파리가 붙어 있다',
     '사람에서 일반적인 성결정 체계는 <b>X-Y 체계</b>다',
     ['E0-76']),

    ('★ 각 줄 오른쪽의 칸을 센다 — 칸이 하나면 한 종류, 둘이면 두 종류다',
     '<b>heterogametic</b>은 배우자를 <b>두 종류</b> 만드는 쪽이다. 굵은 주황 테두리가 쳐진 줄이 그것이다',
     None),

    ('X-Y 아랫줄(수) — 긴 막대와 짧은 막대에서 칸이 둘로 갈린다',
     'X-Y 체계에서 <b>heterogametic sex는 수컷</b>이다',
     ['E0-77']),

    ('X-Y 윗줄(암) — 긴 막대 둘에서 칸이 하나뿐이다',
     'X-Y 체계에서 <b>homogametic sex는 암컷</b>이다',
     ['E0-78']),

    ('X-O 아랫줄(수) — 한 칸이 점선이다. 성염색체를 못 받은 배우자인데도 칸은 여전히 둘이다',
     'X-O 체계에서도 <b>heterogametic sex는 수컷</b>이다',
     ['E0-79']),

    ('X-O 윗줄(암) — 긴 막대 둘에서 칸이 하나',
     'X-O 체계에서 <b>homogametic sex는 암컷</b>이다',
     ['E0-80']),

    ('셋째 열의 예 — 조류와 일부 어류',
     '조류와 일부 어류에서 흔한 것이 <b>Z-W 체계</b>다',
     ['E0-83']),

    ('Z-W 윗줄(암) — 여기서는 윗줄에 굵은 테두리가 쳐졌다',
     'Z-W 체계에서 <b>heterogametic sex는 암컷</b>이다',
     ['E0-81']),

    ('Z-W 아랫줄(수) — 보라 긴 막대 둘에서 칸이 하나',
     'Z-W 체계에서 <b>homogametic sex는 수컷</b>이다',
     ['E0-82']),

    ('★ 첫째 열과 셋째 열을 나란히 보면 굵은 테두리가 서로 반대 줄에 있다',
     '<b>X-Y는 수컷</b>, <b>Z-W는 암컷</b>이 heterogametic이다 — 두 체계 비교의 답이 이 자리다',
     ['E0-91']),

    ('첫째 열과 둘째 열은 굵은 테두리가 같은 줄(아랫줄)에 있다',
     'X-O와 X-Y의 공통점은 <b>둘 다 수컷이 heterogametic sex</b>라는 것이다',
     ['E0-92']),

    ('네 열의 테두리가 저마다 다른 줄에 쳐져 있다',
     '<b>성결정 체계(XY·XO·ZW)에 따라 두 종류의 성염색체를 갖는 성이 달라</b> 종류마다 '
     'hetero인 성이 바뀐다',
     ['E0-90']),

    ('넷째 열 — 벌과 개미, 그리고 셀 칸이 아예 없다',
     '벌과 개미의 성결정은 <b>반수체-2배체 체계</b>다',
     ['E0-84']),

    ('넷째 열 위칸 — 수정란에서 암컷으로 간다',
     '반수체-2배체에서 <b>암컷은 수정란에서 발생한 2배체(2n)</b>다',
     ['E0-85']),

    ('넷째 열 아래칸 — 미수정란에서 수컷으로 간다',
     '반수체-2배체에서 <b>수컷은 비수정란에서 발생한 반수체(n)</b>다',
     ['E0-86']),

    ('아래 왼쪽 상자 — Y 위의 한 자리',
     '사람 배아에서 정소 발달에 필수적인 Y 염색체 부위는 <b>SRY(성 결정 부위)</b>다. '
     'Y 전체가 아니라 이 한 자리가 방아쇠다',
     ['E0-87']),

    ('아래 가운데 상자 — 해부학적 신호가 나타나는 때',
     '사람 배아에서 성에 대한 해부학적 신호는 <b>약 2개월 무렵</b>부터 나타나기 시작한다',
     ['E0-88']),

    ('아래 오른쪽 상자 — 두 X 중 하나를 끈다',
     '포유류 암컷은 두 X 중 <b>하나가 불활성화</b>되고, 응축된 그것이 <b>바소체(Barr body)</b>다. '
     '세포마다 꺼지는 쪽이 달라 <b>삼색(calico) 고양이</b> 무늬가 생긴다',
     ['E0-89', 'E0-89#1', 'E0-89#2', 'E0-89#3']),
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
    assert "{id:'d05p03'" not in src, '이미 있다'
    assert '`' not in BX and "'" not in BR
    svg = open(SVGF, encoding='utf-8').read().strip()
    assert '`' not in svg and '\\' not in svg, 'SVG에 백틱·역슬래시'
    assert svg.startswith('<svg') and svg.endswith('</svg>')

    i = src.index("{id:'d05p02'")
    e = close_brace(src, i)

    rows = []
    for prop, fact, cards in ROWS:
        r = '[' + q2(prop) + ',' + q2(fact)
        if cards:
            r += ',[' + ','.join(q2(c) for c in cards) + ']'
        rows.append(r + ']')

    panel = ("{id:'d05p03',t:'성결정 네 체계',svg:`" + svg + "`,br:'" + BR + "',bx:`" + BX
             + "`,f:[" + ',\n     '.join(rows) + ']}')
    out = src[:e + 1] + ',\n   ' + panel + src[e + 1:]

    k = out.index("{id:'d05p03'")
    blk = out[k:close_brace(out, k) + 1]
    ids = re.findall(r"\{id:'([sd]\d+p\d+[ab]?)'", out)
    assert len(ids) == len(set(ids)), '패널 id 중복'
    assert ids.index('d05p03') == ids.index('d05p02') + 1, '위치 오류'
    cards = re.findall(r'"(E0-[\w#]+)"', blk)
    assert len(cards) == len(set(cards)), '카드 중복'
    print('패널 %d개 · d05p03 행 %d · 카드 %d장 · SVG %d바이트'
          % (len(ids), len(ROWS), len(cards), len(svg)))
    open(SK, 'w', encoding='utf-8').write(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())

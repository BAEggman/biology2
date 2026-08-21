# -*- coding: utf-8 -*-
"""d05p01(상인과 상반)에 「멘델의 독립의 법칙」 한 줄을 적는다.

★ 왜 — 걸린 카드 둘이 이름을 대놓고 묻는다
  E0-5 「연관유전자가 **멘델의 완전독립**과 다른 이유는?」
  D1-94「연관이 **독립의 법칙**의 예외로 보이는 이유는?」
  그런데 이 도해 어디에도 「멘델」도 「독립의 법칙」도 안 쓰여 있었다.
  도해는 소리 후크가 아니라 **글자**로 이름을 나른다 — 한 줄이면 끝난다.

★ 어디에 — 「② 배우자」 칸 바로 아래 (y 238~275 가 비어 있다)
  배우자가 두 가지뿐인 것이 곧 독립이 깨진 자리이므로, 그 그림 바로 밑이 맞다.
"""
import os
SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_d05p01.svg')
SK  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sketchy.html')

s = open(SVG, encoding='utf-8').read()
assert '멘델' not in s, '이미 들어 있다'

ANCHOR = '<rect x="161" y="276" width="62" height="46" rx="5" fill="#CCFBF1"'
assert s.count(ANCHOR) == 1
NOTE = ('<text x="440" y="252" text-anchor="middle" font-size="10.5" font-weight="700" fill="#7C2D12">'
        '★ 멘델의 독립의 법칙은 두 유전자가 서로 다른 막대에 실렸을 때만 성립한다</text>\n'
        '<text x="440" y="266" text-anchor="middle" font-size="10" fill="#6B7280">'
        '같은 막대에 실리면 막대째 함께 가므로 배우자가 두 가지뿐이다 — 이것이 연관이 멘델의 완전독립과 다른 이유다</text>\n')
s = s.replace(ANCHOR, NOTE + ANCHOR, 1)
open(SVG, 'w', encoding='utf-8').write(s)
print('_d05p01.svg — 멘델 한 줄 추가')

k = open(SK, encoding='utf-8').read()
i = k.index("{id:'d05p01'")
a0 = k.index('svg:`', i) + 5
b0 = k.index('`', a0)
assert k[a0:b0].lstrip().startswith('<svg')
assert '`' not in s
k = k[:a0] + s.strip() + k[b0:]
open(SK, 'w', encoding='utf-8').write(k)
print('sketchy.html 인라인 사본 교체')

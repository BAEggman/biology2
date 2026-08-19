#!/usr/bin/env python3
"""d05p03 「성결정 네 체계」 — 설명을 압축한다. 카드는 한 장도 안 뺀다.

사용자: 「성결정 네 체계 이거는 좀더 설명을 콘사이스하게 바꿀 필요가 있어, 너무 양이 많아」

원인은 분량이 아니라 **반복**이었다. hetero/homo를 체계마다 두 줄씩 따로 적어
「X-Y 체계에서 heterogametic sex는 수컷이다 / homogametic sex는 암컷이다」가
네 번 되풀이됐다. 짝을 한 줄로 합치면 20행 → 14행이 되고, 읽는 사람은
**한 줄에서 대비를 본다** — 그게 원래 이 표가 하려던 일이다.
"""
import re, sys
sys.path.insert(0, '/tmp/b2/tools')
from link_cards import _block, _rows

SK = '/tmp/b2/sketchy.html'
src = open(SK, encoding='utf-8').read()
i, j = _block(src, 'd05p03')
blk = src[i:j]

def q2(s):
    assert '"' not in s and '\\' not in s, s
    return '"%s"' % s

def row(prop, fact, cards):
    r = '[' + q2(prop) + ',' + q2(fact)
    if cards: r += ',[' + ','.join(q2(c) for c in cards) + ']'
    return r + ']'

ROWS = [
 ('첫째 열 — 사람과 초파리가 붙어 있다', '사람의 성결정은 <b>X-Y 체계</b>다', ['E0-76']),
 ('★ 각 줄 오른쪽의 칸을 센다 — 하나면 한 종류, 둘이면 두 종류다',
  '<b>heterogametic</b> = 배우자를 <b>두 종류</b> 만드는 쪽. 굵은 주황 테두리가 그 줄이다', ['D1-120']),
 ('X-Y 열 — 아랫줄(수)만 칸이 둘, 윗줄(암)은 하나',
  '<b>X-Y: hetero = 수컷, homo = 암컷</b>', ['E0-77', 'E0-78']),
 ('X-O 열 — 아랫줄(수)의 두 칸 중 하나가 <b>점선</b>, 윗줄(암)은 한 칸',
  '<b>X-O도 hetero = 수컷, homo = 암컷.</b> 점선이 「성염색체를 못 받음(O)」이다', ['E0-79', 'E0-80']),
 ('X-O 칸 속 — 암 칸에 긴 막대 하나, 수 칸 둘에 긴 막대와 점선',
  '암컷은 X만, 수컷은 <b>X와 O 두 가지</b>를 낸다', ['E0-147']),
 ('셋째 열의 예 — 조류와 일부 어류', '조류·일부 어류가 <b>Z-W 체계</b>다', ['E0-83']),
 ('★ Z-W 열 — 여기서만 굵은 테두리가 <b>윗줄(암)</b>에 있다',
  '<b>Z-W: hetero = 암컷, homo = 수컷</b> — X-Y와 뒤집힌다', ['E0-81', 'E0-139', 'E0-82']),
 ('Z-W 칸 속 — 암 칸 둘에 긴·짧은 보라 막대, 수 칸 하나에 긴 보라 막대',
  '수컷은 Z만, 암컷은 <b>Z와 W 두 가지</b>를 낸다 — 내는 쪽이 X-Y와 뒤집혀 있다', ['E0-146']),
 ('★ 첫째 열과 셋째 열 — 굵은 테두리가 서로 <b>반대 줄</b>에 있다',
  'X-Y는 수컷, Z-W는 암컷이 hetero다 — <b>두 체계 비교의 답이 이 자리</b>다', ['E0-91']),
 ('첫째 열과 둘째 열 — 테두리가 <b>같은 줄</b>(아랫줄)에 있다',
  'X-O와 X-Y의 공통점: <b>둘 다 수컷이 hetero</b>', ['E0-92', 'E0-140']),
 ('테두리가 세 열에만 있고, 그중 <b>Z-W만 윗줄</b>이다',
  '체계마다 hetero인 성이 바뀐다. 넷째 열에 테두리가 없는 것은 <b>성염색체로 갈리지 않기</b> 때문이다',
  ['E0-90']),
 ('넷째 열 — 벌과 개미, 셀 칸이 아예 없다 · 위칸은 수정란→암컷, 아래칸은 미수정란→수컷',
  '<b>반수체-2배체</b>. 암컷은 수정란에서 온 <b>2n</b>, 수컷은 미수정란에서 온 <b>n</b>이다',
  ['E0-84', 'E0-85', 'E0-86']),
 ('아래 왼쪽 상자 — Y 위의 <b>한 자리</b>',
  '정소 발달의 방아쇠는 <b>SRY</b>다 — Y 전체가 아니라 이 한 자리다', ['E0-87']),
 ('아래 가운데 상자 — 해부학적 신호가 나타나는 때', '사람 배아에서 <b>약 2개월</b>부터', ['E0-88']),
 ('아래 오른쪽 상자 — 두 X 중 하나를 끈다',
  '<b>바소체(Barr body)</b>. 세포마다 꺼지는 쪽이 달라 <b>삼색(calico) 고양이</b> 무늬가 생긴다',
  ['E0-89', 'E0-89#1', 'E0-89#2', 'E0-89#3']),
]

before = set(re.findall(r'"([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[\w#]+)"', blk))
after = set(c for _, _, cs in ROWS for c in cs)
assert before == after, ('카드가 바뀐다', sorted(before - after), sorted(after - before))

fi = blk.index(',f:[')
new_blk = blk[:fi] + ',f:[' + ',\n     '.join(row(*r) for r in ROWS) + ']}'
open(SK, 'w', encoding='utf-8').write(src[:i] + new_blk + src[j:])
print('d05p03 사실표 20행 → %d행 · 카드 %d장 그대로' % (len(ROWS), len(after)))

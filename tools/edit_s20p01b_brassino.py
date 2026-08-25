# -*- coding: utf-8 -*-
"""s20p01b — 브라시노스테로이드에 솔을 준다 (2026-08-25).

★ 왜 이 한 판으로 9장이 풀리나
  감사는 s20p01a 4 · s20p01b 3 · s20p01c 2 로 세지만, 답에 실제로 「브라시노스테로이드」가
  든 카드는 **둘뿐**이다 — S-PL-14(판 {a,b})와 X-PL-27(판 {a,c}).
  cardEv 가 걸린 판 전부의 소품을 합쳐 보므로,
  ① s20p01b 에 솔을 넣으면 S-PL-14 가 풀리고,
  ② X-PL-27 을 s20p01b#3 에 겹걸면 그 카드의 증거가 {a,b,c} 가 되어 함께 풀린다.
  그러면 세 판에 흩어져 있던 아홉 자리가 한 번에 떨어진다.

★ X-PL-27 겹걸기가 정직한 까닭
  X-PL-27 = 「종자 휴면을 유도하는 호르몬과 발아를 촉진하는 호르몬은?
             → 휴면=ABA / 발아=지베렐린·브라시노스테로이드」.
  s20p01b#3 의 사실 칸이 이미 「…그리고 **종자 발아**」라 적는다. 그 행이 곧 제자리다.

★ 솔은 붓이 아니다
  붓은 MSH(s07p02) 예약이고 s20p01a 에도 시토키닌의 붓이 있다. 그래서
  **자루 없는 나무 토막에 짧고 빳빳한 털이 촘촘한 솔**로 물건을 갈랐다.
  그림을 확인했다 — 부목 댄 줄기 밑동 곁 바닥에 털이 위로 오게 놓여 있다.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowlib import edit_row

P = '/tmp/b2/sketchy.html'
s = open(P, encoding='utf-8').read(); n0 = len(s)

PROP = ('부목 댄 줄기가 맨 줄기의 <b>두 배 굵고</b>, 그 밑동 곁 바닥에 '
        '<b>나무 토막에 짧고 빳빳한 털이 촘촘히 박힌 솔</b>이 털을 위로 하고 놓였다')
FACT = ('브라시노스테로이드 — 줄기 비대<b>브라시노스테로이드</b> — <b>세포 신장·분열</b>과 '
        '<b>관속 분화</b>, 그리고 <b>종자 발아</b>. 줄기가 굵어진 것이 신장과 분열이 함께 일어난 결과다. '
        '★ <b>솔</b>이 곧 이름이다 — <b>브라시</b>노스테로이드, 브러시. '
        '⚠ 칠하는 <b>붓</b>이 아니라 문지르는 <b>솔</b>이다 — 붓은 옆 판(s20p01a)의 시토키닌이 든 것이고 '
        '이쪽은 자루가 없는 나무 토막이다')

s, ch, new = edit_row(s, 's20p01b', 3, prop=PROP, fact=FACT)
assert ch, '소품·사실이 안 바뀌었다'
s, ch2, new2 = edit_row(s, 's20p01b', 3, fn=lambda cs: cs + ['X-PL-27'] if 'X-PL-27' not in cs else cs)
assert ch2, '카드가 안 붙었다'
print('#3 →', new2)
assert 0 < len(s) - n0 < 900, '길이 변화 이상 %d' % (len(s) - n0)
open(P + '.t', 'w', encoding='utf-8').write(s); os.replace(P + '.t', P)
print('✅ s20p01b#3 갱신 (%d → %d 자)' % (n0, len(s)))

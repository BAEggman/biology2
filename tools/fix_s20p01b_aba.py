# -*- coding: utf-8 -*-
"""s20p01b 1행 정정 — 그리지 않은 이름은 부르지 않는다.

s20p01b의 「잎의 셔터」는 ABA가 *하는 일*(닫는다)은 나르지만 *이름*은 못 나른다.
그런데 사실 칸이 ABA를 다섯 번 불러 음성 후크 감사가 그 한 행에서 5장을 위반으로 셌다.

이름을 부르는 자리를 새 판 s20p01c(갓 쓴 아비) 한 곳으로 모은다 —
s20p07에서 쓴 것과 같은 수법이고, 다음에 고칠 일이 생겨도 한 판만 고치면 된다.

카드 재배치
  P1-6     (넷 다)          → s20p01c 로 이동. 셔터는 넷 중 하나만 그린다
  X-PL-27  (휴면/발아)      → s20p01c 로 이동. 휴면 그림(묻고 누른 씨앗)이 거기 있다
  P1-6#2·O1-22·O1-22#2      → s20p01b 에 그대로 두고 s20p01c 를 배열로 더한다
                              (셔터가 양쪽에 있고, 이름은 새 판이 나른다)
"""
import os, re
SK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sketchy.html')

def _close(s, i):
    o = s[i]; c = {'{': '}', '[': ']'}[o]; d = 0; q = None; e = False
    for k in range(i, len(s)):
        ch = s[k]
        if q:
            if e: e = False; continue
            if ch == '\\': e = True; continue
            if ch == q: q = None
            continue
        if ch in '"\'`': q = ch; continue
        if ch == o: d += 1
        elif ch == c:
            d -= 1
            if not d: return k
    raise AssertionError('닫는 괄호를 못 찾음')

s = open(SK, encoding='utf-8').read()
i = s.index("{id:'s20p01b'")
pe = _close(s, i); blk = s[i:pe + 1]
fi = blk.index('f:[')
needle = '잎의 셔터를 끌어내려'
assert blk.count(needle, fi) == 1
k = blk.index(needle, fi); a = blk.rindex('[', fi, k); b = _close(blk, a)
row = blk[a:b + 1]

p1 = 1; p2 = row.index('"', p1 + 1)
f1 = row.index('"', p2 + 1); f2 = row.index('"', f1 + 1)
prop, fact = row[p1:p2 + 1], row[f1:f2 + 1]
rest = row[f2 + 1:-1].strip()
old = [x.strip().strip('"') for x in rest.strip(',').strip('[]').split(',') if x.strip()]
print('전  카드:', old)
assert set(old) == {'P1-6', 'P1-6#2', 'X-PL-27', 'O1-22', 'O1-22#2'}, old

NEW_FACT = ('"<b>기공을 닫는다</b> — 마르면 공변세포에서 물을 빼내 쭈그러뜨린다. '
            '★ <b>여는 것이 아니라 닫는다</b> — 이 판 최다 함정이다. '
            '이 호르몬이 하는 일은 넷인데 셔터는 그중 하나만 그린다 — '
            '★ <b>이름과 나머지 셋은 옆 판(갓 쓴 아비)에 있다.</b> '
            '이 판에는 그 이름을 나르는 소품이 없으므로 여기서 부르지 않는다"')
assert 'ABA' not in NEW_FACT, '이름을 지우는 것이 이 스크립트의 목적이다'
NEW_CARDS = ['P1-6#2', 'O1-22', 'O1-22#2']          # P1-6·X-PL-27 은 새 판으로 간다

new_row = '[' + prop + ',' + NEW_FACT + ',[' + ','.join('"%s"' % c for c in NEW_CARDS) + ']]'
s = s[:i + a] + new_row + s[i + b + 1:]
open(SK, 'w', encoding='utf-8').write(s)
print('후  카드:', NEW_CARDS, '· P1-6·X-PL-27 은 s20p01c 로 넘어간다')

# -*- coding: utf-8 -*-
"""O1-22「기공 열림·닫힘의 신호는?」는 답이 두 판에 걸쳐 그려져 있다.
   열림(청색광·시계·CO₂)은 s20p07(두 콩팥이 벌리는 틈)에,
   닫힘(ABA·셔터)은 s20p01b(멈추게 하는 셋)에 있다.
   급소가 두 판에 나뉘면 배열이 옳다 — 「그림으로 복구」가 두 장을 다 띄운다."""
import os
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

def link_one(pid, needle, cards, extra=''):
    s = open(SK, encoding='utf-8').read()
    i = s.index("{id:'%s'" % pid)
    pe = _close(s, i); blk = s[i:pe + 1]
    for c in cards:
        assert '"%s"' % c not in blk, c + ' 가 이미 그 판에 있다'
    fi = blk.index('f:[')                     # ★ bx 산문·SVG desc 에도 같은 말이 있다
    assert blk.count(needle, fi) == 1, '바늘이 %d번 (1 기대): %s' % (blk.count(needle, fi), needle)
    k = blk.index(needle, fi); a = blk.rindex('[', fi, k); b = _close(blk, a)
    row = blk[a:b + 1]
    p1 = 1; p2 = row.index('"', p1 + 1)
    f1 = row.index('"', p2 + 1); f2 = row.index('"', f1 + 1)
    prop, fact = row[p1:p2 + 1], row[f1:f2 + 1]
    rest = row[f2 + 1:-1].strip()
    old = [x.strip().strip('"') for x in rest.strip(',').strip('[]').split(',') if x.strip()] if rest.startswith(',') else []
    if extra: fact = fact[:-1] + ' ' + extra + '"'
    new_row = '[' + prop + ',' + fact + ',[' + ','.join('"%s"' % c for c in old + list(cards)) + ']]'
    s = s[:i + a] + new_row + s[i + b + 1:]
    open(SK, 'w', encoding='utf-8').write(s)
    print('%s ← %s  (그 행 카드 %d → %d장)' % (pid, ','.join(cards), len(old), len(old) + len(cards)))

link_one('s20p01b', '잎의 셔터를 끌어내려', ['O1-22'])

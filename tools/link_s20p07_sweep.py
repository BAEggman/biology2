# -*- coding: utf-8 -*-
"""s20p07 훑기 — 기공이 덱에 없던 탓에 미연결로 남아 있던 카드를 그린 행에 건다.

★ 건 것 (급소가 그림에 있다)
   1행 부푼 콩팥 둘이 서로 미는 그림 = 공변세포 한 쌍 · 팽압 · 열림
   2행 어두운 방울 in / 밝은 방울 out = CO₂·O₂ 교환 통로
   4행 홀쭉해진 둘 + 갈라진 땅 = 건조하면 닫는다 (ABA 이름은 옆 판이 나른다 → 배열)

★ 안 건 것 (급소가 그림에 없다 — 그린 것만 건다)
   O1-21·O1-21#1  K⁺ 유입이 첫 단계인데 이 판에 K⁺ 소품이 없다
   O1-15·O1-2     증산·수증기 소품이 없다 (밝은 방울은 O₂다)
   O1-9           물관의 음압까지 있어야 부호 범위가 성립한다
   O0-7           표피 변형 셋 중 뿌리털·모용이 덱에 아예 없다 (O0-7#1만 걸었다)
"""
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
    fi = blk.index('f:[')
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
    print('  %-8s ← %-34s (행 %d → %d장)' % (pid, ','.join(cards), len(old), len(old) + len(cards)))

link_one('s20p07', '빵빵하게 부풀어',
         ['M0-6#2', 'O1-20', 'O0-7#1', 'O1-10', 'O1-21#2', 'O1-21#3'])
link_one('s20p07', '어두운 방울</b>이 <b>안으로', ['M0-6#1'])
link_one('s20p07', '홀쭉해져</b> 틈이 <b>딱 붙었다', ['O1-22#2'])
link_one('s20p01b', '잎의 셔터를 끌어내려', ['O1-22#2'])   # ★ 배열 — ABA 이름은 이 판이 나른다

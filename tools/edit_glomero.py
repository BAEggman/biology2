# -*- coding: utf-8 -*-
"""글로메로균 4장 — s05p01#3(가죽 글러브)에 겹걸기.
왜: M2-8·M2-8#1·O2-23·O2-23#1 의 답에 「글로메로균」이 있는데 s22p03 에는
    이름을 나르는 소품이 없다. 급소(세포 안까지 뻗은 붉은 나뭇가지)는 s22p03 이 그리고,
    이름(글러브)은 s05p01#3 이 그린다. cardEv 가 두 판의 합을 보므로 둘 다 걸면 풀린다.
    s05p01#3 은 이미 사실 칸에 「★ 글러브가 곧 이름이다 — 글로메로균 …
    손가락이 나뭇가지처럼 갈라져 세포벽 안으로 들어가는 것이 수지상(arbuscular)이다」라 적고 있고,
    같은 뜻의 쌍둥이 카드 M2-19 가 이미 걸려 있다. 억지가 아니라 제자리다.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowlib import edit_row, get_rows

P = '/tmp/b2/sketchy.html'
s = open(P, encoding='utf-8').read()
n0 = len(s)

ADD = ['M2-8', 'M2-8#1', 'O2-23', 'O2-23#1']
print('전:', get_rows(s, 's05p01')[3][-120:])

s2, ch, new = edit_row(s, 's05p01', 3, fn=lambda cs: cs + [c for c in ADD if c not in cs])
assert ch, '안 바뀌었다'
assert 0 < len(s2) - n0 < 200, '길이 변화가 이상하다: %d' % (len(s2) - n0)
print('후:', new[-160:])

open(P + '.t', 'w', encoding='utf-8').write(s2)
os.replace(P + '.t', P)
print('✅ 썼다  %d → %d 자' % (n0, len(s2)))

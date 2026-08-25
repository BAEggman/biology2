# -*- coding: utf-8 -*-
"""s12p01 — 펩시노겐에 콜라 병을 준다 (2026-08-25).

★ 왜 겹걸기가 아니라 그림인가
  G1-92 「주세포는 펩시노겐, 벽세포는 HCl」의 급소는 **두 세포의 대비**인데
  콜라 병이 있는 s12p03 은 그것을 아예 안 그린다. 이름만 빌리려고 판을 하나 더 붙이면
  「그린 것만 건다」가 무너진다. 그래서 이 판에 병을 넣었다.

★ 병이 물건을 한 번 더 가른다
  기둥 인부 = 초록 유리 콜라 병에서 걸쭉한 반죽 (주세포 · 펩시노겐)
  벽돌 인부 = 민짜 흙 항아리에서 맑은 산     (벽세포 · HCl)
  s12p03 의 펩신도 같은 콜라 병이라 「펩시노겐 → 펩신」이 한 물건으로 이어진다.
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowlib import edit_row, get_rows

P='/tmp/b2/sketchy.html'
s=open(P,encoding='utf-8').read(); n0=len(s)
def fact_of(row):
    m=re.match(r'\[\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"', row)
    return m.group(2).replace('\\"','"')

r=get_rows(s,'s12p01')
print('전 #1:', r[1][:100]); print('전 #3:', r[3][:100])

s,ch,_=edit_row(s,'s12p01',1,
  prop='기둥 인부가 <b>초록 유리 콜라 병</b>에서 붓는 걸쭉한 반죽',
  fact=fact_of(r[1])+' ★ <b>콜라 병</b>이 곧 이름이다 — <b>펩시</b>노겐. '
       '옆 판 s12p03 에서 <b>펩신</b>이 든 것과 같은 병이라 「펩시노겐 → 펩신」이 한 물건으로 이어진다. '
       '⚠ 벽돌 인부는 민짜 흙 항아리다 — <b>병이냐 항아리냐</b>로 두 세포가 한 번 더 갈린다')
assert ch,'#1'
s,ch,_=edit_row(s,'s12p01',3,
  prop='벽돌 인부가 <b>민짜 흙 항아리</b>에서 붓는 맑은 산')
assert ch,'#3'
assert 0 < len(s)-n0 < 500, '길이 이상 %d'%(len(s)-n0)
open(P+'.t','w',encoding='utf-8').write(s); os.replace(P+'.t',P)
print('✅ %d → %d'%(n0,len(s)))

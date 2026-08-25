# -*- coding: utf-8 -*-
"""s13p03 — CD8·CD4 에 조끼 단추를 준다 (2026-08-25, v2).

★ 왜 단추인가
  로마자 감사 최대 항목(10장)이었다. 「음반(CD)」은 Cdk 계열 예약이라 막혀 있었는데,
  갈리는 것은 CD 가 아니라 **숫자 4와 8**이다. s37p01 의 「놋쇠 못의 개수」와 같은 수를 쓴다.

★ 왜 「넷씩 두 줄」인가 — v1 이 가르쳐 준 것
  v1 은 「한 줄에 여덟」을 요구했는데 **여섯**을 그렸다. 같은 그림에서 「넷」은 정확했다.
  그림 모델은 넷은 세지만 여덟은 못 센다. 그래서 v2 는
  **더블브레스티드(넷씩 두 줄) vs 싱글브레스티드(한 줄 넷)** 로 바꿨고 한 번에 맞았다.
  학생도 「두 줄이면 여덟, 한 줄이면 넷」으로 읽는다.

★ 자리가 곧 짝이다
  여덟 단추 = 작은 쟁반(MHC I)을 받는다 · 넷 단추 = 큰 판(MHC II)을 받는다.
  사실 칸이 이미 적어 둔 「곱이 8」(8×1 = 4×2)이 그림에서 세어진다.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowlib import edit_row, get_rows

P='/tmp/b2/sketchy.html'
s=open(P,encoding='utf-8').read(); n0=len(s)

rows=get_rows(s,'s13p03')
print('전 #2:', rows[2][:90]); print('전 #3:', rows[3][:90])

P2=('예외 없이 전원이 단 둥근 배지 + 작은 쟁반 · ★ 그 쟁반을 건네받는 사람의 조끼는 '
    '<b>단추가 넷씩 두 줄</b>이다')
F2=(rows[2].split('","')[1].rstrip('"]').replace('\\"','"') if False else None)

s,ch,_=edit_row(s,'s13p03',2,prop=P2)
assert ch,'#2 안 바뀜'
P3=('따로 선 넷 중 셋만 든 큰 판 · ★ 그 판을 건네받는 사람의 조끼는 '
    '<b>단추가 한 줄에 넷</b>이다')
s,ch,_=edit_row(s,'s13p03',3,prop=P3)
assert ch,'#3 안 바뀜'

# 사실 칸에 후크 설명을 덧붙인다
r=get_rows(s,'s13p03')
import re
def fact_of(row):
    # ["소품","사실",[...]] 에서 사실만
    m=re.match(r'\[\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"', row)
    return m.group(2).replace('\\"','"')
f2=fact_of(r[2]); f3=fact_of(r[3])
ADD2=(' ★ <b>단추 여덟</b>이 곧 <b>CD8</b>이다 — 넷씩 두 줄이라 세기 쉽다. '
      '쟁반 <b>하나</b>(MHC <b>I</b>) × 단추 <b>여덟</b> = 8. 이것이 「곱이 8」이다')
ADD3=(' ★ <b>단추 넷</b>이 곧 <b>CD4</b>이다 — 한 줄이라 두 줄짜리와 한눈에 갈린다. '
      '판 <b>둘</b>(MHC <b>II</b>) × 단추 <b>넷</b> = 8. 같은 8이다')
s,ch,_=edit_row(s,'s13p03',2,fact=f2+ADD2); assert ch
s,ch,_=edit_row(s,'s13p03',3,fact=f3+ADD3); assert ch

assert 0 < len(s)-n0 < 900, '길이 변화 이상 %d'%(len(s)-n0)
open(P+'.t','w',encoding='utf-8').write(s); os.replace(P+'.t',P)
r=get_rows(s,'s13p03')
print('후 #2:', r[2][:110]); print('후 #3:', r[3][:110])
print('✅ %d → %d 자'%(n0,len(s)))

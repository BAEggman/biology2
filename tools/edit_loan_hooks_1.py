# -*- coding: utf-8 -*-
"""음차 후크 1차 — 그림을 안 고치고 소품 이름만으로 살릴 수 있는 것들.
   사용자 지적: 「아포플라스트 심플라스트 등등 Phonetic cue 를 못 주는 그림들이 참 많아」"""
import sys, io
sys.path.insert(0,'/tmp/b2/tools'); import rowlib
P='/tmp/b2/sketchy.html'
s=io.open(P,encoding='utf8').read(); before=len(s)

# ── s22p02 — 나무 단면의 고리로 늘어선 네모 집들이 곧 「아파트 동」이다 ──────
#    그림에 이미 있는 것을 다르게 부를 뿐이라 「그린 것만 건다」를 어기지 않는다.
s,ch,_=rowlib.edit_row(s,'s22p02',0,
  prop='<b>아파트</b> 동 사이의 바깥 골목으로만 가는 길 — 어느 집에도 안 들어간다')
print('s22p02#0 아포플라스트:',ch)
s,ch,_=rowlib.edit_row(s,'s22p02',1,
  prop='아파트 문을 열고 <b>집 안을 질러</b>가는 길 — 문이 하나같이 장식 없는 <b>심플한 민짜</b>다')
print('s22p02#1 심플라스트:',ch)
s,ch,_=rowlib.edit_row(s,'s22p02',3,
  prop='<b>아파트</b> 단지를 한 바퀴 두른 검은 방수 띠 — 바깥 골목만 막고 집 문은 안 막는다')
print('s22p02#3 카스파리대:',ch)

# ── s15p02#1 — 배턴을 넘기는 것이 곧 trans-duce(건너 이끌다)다 ─────────────
s,ch,_=rowlib.edit_row(s,'s15p02',1,
  prop='배턴을 <b>건너편으로 넘겨</b> 나르는 릴레이 주자 — 받은 것을 그대로 안 쓰고 다음 사람 손에 옮긴다')
print('s15p02#1 트랜스듀신:',ch)

io.open(P,'w',encoding='utf8').write(s)
print('글자수 차', len(s)-before)

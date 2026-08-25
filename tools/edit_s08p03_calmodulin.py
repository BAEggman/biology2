# -*- coding: utf-8 -*-
"""s08p03 재생성 반영 — 칼모듈린에 소리를 준다."""
import sys, io
sys.path.insert(0,'/tmp/b2/tools'); import rowlib
P='/tmp/b2/sketchy.html'
s=io.open(P,encoding='utf8').read()

s,ch,_=rowlib.edit_row(s,'s08p03',1,
  prop='★ <b>자갈 넷</b>이 옴폭한 자리에 하나씩 딱 맞게 박힌 납작한 <b>모듈 쟁반</b>을 앞으로 들고, '
       '다른 손으로 조수의 어깨를 밀어 데려오는 인물',
  fact='<b>칼모듈린</b>이 마이오신 경사슬 인산화효소(MLCK)를 데려온다. '
       '★ <b>모듈</b> 쟁반이 곧 이름이다 — 칼<b>모듈</b>린. 그리고 자갈이 넷인 것도 사실 그대로다 — '
       '칼모듈린은 Ca²⁺를 <b>네 개</b> 붙잡아야 모양이 바뀌어 표적을 잡는다. '
       '★ 전령별 표적 넷 중 Ca²⁺ → 칼모듈린이 이것이다 — 2차 전달자 편이 아니라 평활근 편에 있어 놓치기 쉽다')
print('s08p03#1 :', ch)

s,ch,_=rowlib.edit_row(s,'s08p03',0,
  prop='왼쪽 담벼락 바깥에 걸린 <b>나사 구멍 넷만 남은 빈 받침판</b> — 구멍마다 아무것도 안 박혔다')
print('s08p03#0 :', ch)

io.open(P,'w',encoding='utf8').write(s)

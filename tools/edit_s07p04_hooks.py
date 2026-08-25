# -*- coding: utf-8 -*-
"""s07p04 재생성 반영 — 부신 호르몬 셋에 소리를 준다."""
import sys, io
sys.path.insert(0,'/tmp/b2/tools'); import rowlib
P='/tmp/b2/sketchy.html'
s=io.open(P,encoding='utf8').read()

s,ch,_=rowlib.edit_row(s,'s07p04',1,
  prop='맨 위층 — 쓰러진 소금통에서 흰 <b>알</b>갱이가 쏟아졌고, 인부가 솔로 그것을 쓸어 '
       '<b>도</b>로 통에 담고 있다',
  fact='<b>알도스테론</b> — Salt (사구대). '
       '★ <b>알</b>갱이를 <b>도</b>로 담는 것이 곧 이름이다 — <b>알도</b>스테론. '
       '그리고 하는 일도 그림 그대로다 — Na⁺를 <b>도로 거둬들인다</b>(재흡수). '
       '쏟는 것이 아니라 담는 쪽인 것이 요점이다')
print('#1 알도스테론:', ch)

s,ch,_=rowlib.edit_row(s,'s07p04',2,
  prop='가운데 층 — 층층 케이크 옆에 케이크만 한 <b>코르크 마개</b>가 서 있다',
  fact='<b>코르티솔</b> — Sugar (다발대). '
       '★ <b>코르크</b>가 곧 이름이다 — <b>코르티</b>솔. 게다가 코르크(cork)와 '
       '코르텍스(cortex, 겉껍질·<b>피질</b>)는 같은 뿌리라, 이 마개 하나가 「부신<b>피질</b>」까지 나른다. '
       '케이크가 당(糖)이다')
print('#2 코르티솔:', ch)

s,ch,_=rowlib.edit_row(s,'s07p04',3,
  prop='아래층 — 빨간 하트 옆에 작은 양철 <b>로봇</b> 인형이 서 있다 (네모 머리에 안테나)',
  fact='<b>안드로겐</b> — Sex (망상대). ★ 로봇이 곧 이름이다 — <b>안드로</b>이드. '
       '하트가 성(性)이고, 부신에서 나오는 것은 DHEA 같은 약한 남성호르몬이다')
print('#3 안드로겐:', ch)

io.open(P,'w',encoding='utf8').write(s)

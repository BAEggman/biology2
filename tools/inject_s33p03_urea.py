# -*- coding: utf-8 -*-
"""s33p03 — 그려져 있는데 안 걸어 둔 자리: 궤도 끝에 펴서 깔린 요(=요소).
   그림(img/s33p03.webp) 왼쪽 아래에 격자무늬 요가 반쯤 펼쳐져 깔려 있고
   그것을 내려놓은 수레는 빈 채로 궤도를 계속 돈다. 소품 칸이 이를 말한 적이 없다."""
import io,sys
p='sketchy.html'
s=io.open(p,encoding='utf-8').read()

# 1) 10행의 CO2 표현을 그림과 맞춘다 (그림: 바닥의 작은 통에서 피어오르는 둥근 방울)
old_co2 = '와 바닥에서 오르는 <b>어두운 방울</b>'
new_co2 = '과 바닥의 <b>작은 통에서 피어오르는 둥근 방울</b>'
assert s.count(old_co2)==1, ('co2 anchor', s.count(old_co2))
s = s.replace(old_co2, new_co2)
old_co2b = '<b>어두운 방울</b>이 CO₂다'
new_co2b = '<b>피어오르는 방울</b>이 CO₂다'
assert s.count(old_co2b)==1, ('co2b anchor', s.count(old_co2b))
s = s.replace(old_co2b, new_co2b)

# 2) 10행 뒤에 11행을 잇는다
marker = '둘이 크랭크로 들어간다",["EZ-057"]]]}]'
assert s.count(marker)==1, ('tail anchor', s.count(marker))
new_row = ('둘이 크랭크로 들어간다",["EZ-057"]],\n'
 '  ["궤도 <b>바깥쪽</b> — 수레가 내려놓고 간 <b>펴서 깔린 격자 요</b>, 그 뒤로 <b>빈 수레</b>가 궤도를 계속 돈다",'
 '"이 회로가 <b>내놓는 것이 요소</b>다. ★ 같은 「요」인데 <b>펴서 깔리면 요소, 접어 쌓으면 요산</b>이다 — 44-5「셋이 버리는 법」의 그 요와 같은 물건이다. '
 '내려놓는 자리가 <b>담장 밖</b>인 것이 「요소가 떨어져 나오는 마지막 단계는 세포질」이고, 짐을 내리고도 <b>수레가 비어서 계속 도는 것</b>이 오르니틴이 되돌아오는 것이다",'
 '["G1-141"]]]}]')
s = s.replace(marker, new_row)

io.open(p,'w',encoding='utf-8').write(s)
print('ok')

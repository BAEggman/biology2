# -*- coding: utf-8 -*-
"""s06p02 — 스트라메노파일에 「털 난 빨대」를 준다 (2026-08-25).

★ 소리와 뜻이 같이 맞는 드문 후크
  stramen = 라틴어 「짚(straw)」 · pilus = 「털」. 실제로 이 무리의 이름은
  편모에 난 **관 모양 털**에서 왔다. 스트라 ≈ 스트로(빨대), 파일 ≈ 털(pile).
  그래서 「짧고 빳빳한 털이 온몸에 돋은 빨대」 하나가 이름 전체를 나른다.

⚠ 솔(브라시노스테로이드)과 갈라야 한다
  빨대는 매끈한 속 빈 관에 둥근 주둥이가 있고 자루가 없다.
  솔은 나무 토막에 털이 박힌 것이다. 프롬프트에 「자루 없다·머리 없다·
  털은 관 몸통에서 직접 돋는다」로 못 박았고 그대로 나왔다.
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowlib import edit_row, get_rows
P='/tmp/b2/sketchy.html'
s=open(P,encoding='utf-8').read(); n0=len(s)
def fact_of(row):
    m=re.match(r'\[\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"', row)
    return m.group(2).replace('\\"','"')
r=get_rows(s,'s06p02'); print('전 #2:', r[2][:80])
s,ch,_=edit_row(s,'s06p02',2,
  prop='전면이 유리인 진열장 · 그 앞에 기대선 <b>짧고 빳빳한 털이 온몸에 돋은 빨대</b>',
  fact=fact_of(r[2])+' ★ <b>털 난 빨대</b>가 곧 이름이다 — <b>스트라</b>메노<b>파일</b>. '
       'stramen 이 라틴어로 <b>짚(straw)</b>, pilus 가 <b>털</b>이고, 실제로 이 무리의 이름은 '
       '편모에 난 <b>관 모양 털</b>에서 왔다. 소리와 뜻이 같이 맞는다. '
       '⚠ 자루가 없는 <b>매끈한 관</b>이다 — 나무 토막에 털이 박힌 <b>솔</b>(s20p01b 브라시노스테로이드)과 갈린다')
assert ch
assert 0 < len(s)-n0 < 400
open(P+'.t','w',encoding='utf-8').write(s); os.replace(P+'.t',P)
print('✅ %d → %d'%(n0,len(s)))

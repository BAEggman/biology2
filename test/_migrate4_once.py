#!/usr/bin/env python3
"""제안 4 (1/2) — sketchy.html에 링크 스키마를 도입하고 기존 PMAP 705개를 무손실 이관.

스키마
  panels[].pc : ['G1-31', ...]        패널 단위 링크 (행이 아직 안 정해진 것)
  panels[].f  : [소품, 사실, [카드ID]] 셋째 자리는 선택 — 행 단위 링크 (제안 5에서 채운다)

이관은 자동 행 배정을 하지 않는다. 표본 검수 결과 정밀도가 55~65%였고,
특히 discrim 카드가 반대쪽 행에 붙었다. 전부 pc로 넣고 제안 5에서 승인 흐름으로 내린다.

삽입은 재직렬화가 아니라 텍스트 삽입이다 — DATA 안의 SVG·백틱·HTML을 건드리지 않는다.
"""
import json, re, sys

SK='/tmp/b2/sketchy.html'; IX='/tmp/b2/index.html'
sk=open(SK,encoding='utf8').read()
ix=open(IX,encoding='utf8').read()

PMAP=json.loads(re.search(r'var PMAP=(\{.*?\});', ix, re.S).group(1))

# 카드 → 패널  ⇒  패널 → 카드
panel_cards={}
for cid, v in PMAP.items():
    for pid in (v if isinstance(v,list) else [v]):
        panel_cards.setdefault(pid, []).append(cid)
for pid in panel_cards:
    panel_cards[pid].sort()

total_links=sum(len(v) for v in panel_cards.values())
print('이관 대상: 카드 %d장 · 패널 %d개 · 링크 %d건' % (len(PMAP), len(panel_cards), total_links))

# 이미 pc가 있으면 중단 (idempotent 아님 — 한 번만 돈다)
assert 'pc:[' not in sk, '이미 pc가 들어 있다. 이 스크립트는 한 번만 돈다.'

ids=re.findall(r"\{id:'([sd]\d+p\d+[ab]?)',", sk)
assert len(ids)==106, '패널 %d개 (106 기대)' % len(ids)
assert len(set(ids))==106, '패널 id 중복'

inserted=0
def ins(m):
    global inserted
    pid=m.group(1)
    cards=panel_cards.get(pid)
    if not cards: return m.group(0)
    inserted+=1
    return "{id:'%s',pc:%s," % (pid, json.dumps(cards, ensure_ascii=False).replace(', ', ','))

sk2=re.sub(r"\{id:'([sd]\d+p\d+[ab]?)',", ins, sk)
assert inserted==len(panel_cards), '삽입 %d ≠ 대상 %d' % (inserted, len(panel_cards))

# 삽입 외에는 한 글자도 안 바뀌었는지 확인
stripped=re.sub(r",pc:\[[^\]]*\]", "", sk2.replace("{id:'","{id:'"))
# pc를 다시 걷어내면 원본과 같아야 한다
back=re.sub(r"(\{id:'[sd]\d+p\d+[ab]?')\,pc:\[[^\]]*\]\,", r"\1,", sk2)
assert back==sk, '삽입 외 변경이 있다 — 중단'

open(SK,'w',encoding='utf8').write(sk2)
print('  ✓ %d개 패널에 pc 삽입 · 삽입 외 변경 0 (역변환 대조 통과)' % inserted)
print('  sketchy.html %.2fMB → %.2fMB (+%.1fKB)' %
      (len(sk.encode())/1048576, len(sk2.encode())/1048576, (len(sk2.encode())-len(sk.encode()))/1024))

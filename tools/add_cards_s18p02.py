# -*- coding: utf-8 -*-
"""s18p02(태아 우회로와 혈역학)에 카드를 새로 뽑는다 — 2026-08-25.

왜: 이 판은 그림이 다 그려져 있는데 **걸린 카드가 0장인 고아 판**이다.
    훑기로 안 채워진 것이 아니라 **카드 전수 5,679장에 이 내용이 한 장도 없어서** 비었다
    (난원공·동맥관·정맥관·난원와·푸아죄유로 카드를 전수 검색해 0건을 확인했다).
근거: 프로젝트의 `지엽 정리.docx` 「태아 순환과 출생 후 변화」·「혈역학의 물리 법칙」 절.
      ⚠ 기출은 없다 — `claude/생물Sketchy_q블록61장_초안.md` 가 이미
      「태아 우회로를 다룬 기출은 BM상·하 전체에서 찾지 못했다」고 확인해 두었다.
      그래서 q블록(기출 해설)은 건드리지 않고 **카드만** 만든다. 출처를 n 에 적는다.
      티틴·네불린(T0-611·612)이 같은 문서에서 나온 선례다.
접두어: H2 (게이트 H 의 셋째 계열 — 손으로 뽑은 것임을 id 로 알아보게 한다).
"""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowlib import edit_row

IDX = '/tmp/b2/index.html'
SKY = '/tmp/b2/sketchy.html'
SRC = '지엽 정리 — 태아 순환과 출생 후 변화 / 혈역학의 물리 법칙 (기출 확인 안 됨)'
G = dict(g='H', gn='동물의 수송과 배설', ch='43 수송 시스템', ru=1)

def base(i, q, a, n=None, t='base'):
    c = dict(id=i, q=q, a=a, **G); c['p'] = i; c['t'] = t
    if n: c['n'] = n
    return c

def part(i, parent, q, a, n):
    c = dict(id=i, q=q, a=a, **G); c['p'] = parent; c['t'] = 'part'; c['n'] = n
    return c

NEW = [
  base('H2-1', '태아에게만 있다가 출생 후 닫히는 세 우회로는?',
       '난원공 · 동맥관 · 정맥관', SRC),
  base('H2-2', '난원공(foramen ovale)은 어디와 어디를 잇고 출생 후 무엇으로 남는가?',
       '좌우 심방 사이를 잇고, 출생 후 난원와(fossa ovalis)로 남는다', SRC),
  base('H2-3', '동맥관(ductus arteriosus)은 어디와 어디를 잇고 출생 후 무엇으로 남는가?',
       '폐동맥과 대동맥을 잇고, 출생 후 동맥관인대로 남는다', SRC),
  base('H2-4', '정맥관(ductus venosus)은 무엇을 우회하고 출생 후 무엇으로 남는가?',
       '간을 우회해 하대정맥으로 가고, 출생 후 정맥관인대로 남는다', SRC),
  base('H2-5', '동맥관의 폐쇄를 유도하는 것은?',
       '프로스타글란딘 농도 저하', SRC + ' · 출생 후 폐호흡이 시작되며 PG가 줄고 산소분압이 오른다'),
  base('H2-6', '세 태아 우회로가 남기는 흔적을 각각 쓰면?',
       '난원공→난원와 / 동맥관→동맥관인대 / 정맥관→정맥관인대',
       SRC + ' · 셋 중 둘만 「인대」이고 난원공만 「와(오목)」다', t='discrim'),
  base('H2-7', '푸아죄유 법칙(Poiseuille) — 혈류 저항은 무엇에 반비례하는가?',
       '혈관 반지름의 4제곱', SRC),
  base('H2-8', '혈관 반지름이 2배가 되면 혈류 저항은 몇 배가 되는가?',
       '1/16배', SRC + ' · 2⁴=16. 조금만 굵어져도 저항이 급감하는 것이 세동맥이 혈류 조절의 주역인 까닭이다'),
]

s = open(IDX, encoding='utf-8').read()
m = re.search(r'(id=["\']CARDS["\'][^>]*>)([\s\S]*?)(</script>)', s)
CARDS = json.loads(m.group(2))
have = {c['id'] for c in CARDS}
assert not (have & {c['id'] for c in NEW}), 'id 충돌'
n0 = len(CARDS)
CARDS.extend(NEW)
body = json.dumps(CARDS, ensure_ascii=False, separators=(',', ':'))
s2 = s[:m.start(2)] + body + s[m.end(2):]
open(IDX + '.t', 'w', encoding='utf-8').write(s2); os.replace(IDX + '.t', IDX)
print('✅ 카드 %d → %d 장' % (n0, len(CARDS)))

# ── 사실표에 건다 ──────────────────────────────────────────────
LINK = {0: ['H2-1', 'H2-2'], 1: ['H2-3', 'H2-5'], 2: ['H2-4'],
        3: ['H2-6'], 4: ['H2-7', 'H2-8']}
sk = open(SKY, encoding='utf-8').read(); m0 = len(sk)
for n, ids in LINK.items():
    sk, ch, new = edit_row(sk, 's18p02', n, fn=lambda cs, ids=ids: cs + [i for i in ids if i not in cs])
    assert ch, '행 %d 안 바뀌었다' % n
    print('  #%d → %s' % (n, new))
assert 0 < len(sk) - m0 < 400, '길이 변화 이상 %d' % (len(sk) - m0)
open(SKY + '.t', 'w', encoding='utf-8').write(sk); os.replace(SKY + '.t', SKY)
print('✅ s18p02 다섯 행에 걸었다')

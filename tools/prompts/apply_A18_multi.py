#!/usr/bin/env python3
# apply_A18_multi.py — 18장 「여러 단계의 조절」 2장(F1-45 · F1-147)을 L43a s8(담장 안에서 찍고 구멍으로 나가 밖에서 읽는다)에 덧붙인다(그림 손대지 않음).
#   계획 P9(공장의 먼 스위치 · 41장)를 넷으로 가를 때 나온 덧붙임 — 이 두 장은 새 물건이 필요 없다:
#   담장(핵막)이 일을 여러 곳으로 갈라 놓았다 = 거치는 곳마다 손댈 곳(조절 단계)이 는다 · 담장 없는 왼쪽 마당은 찍는 자리 하나.
#   L43a 는 gen 스크립트가 없다(옛 src 줄을 가진 과) — json 을 바로 고친다.
# 사용: python3 apply_A18_multi.py [--write]
import json, sys, re
ROOT = '/tmp/b2'; WRITE = '--write' in sys.argv
p = f'{ROOT}/lessons/L43a.json'; t = open(p, encoding='utf-8').read(); d = json.loads(t)
fmt = None
for ind in (1, 2):
    for nl in ('', '\n'):
        if json.dumps(d, ensure_ascii=False, indent=ind) + nl == t: fmt = (ind, nl)
assert fmt, '✕ 파일 모양'
S = open(f'{ROOT}/index.html', encoding='utf-8').read()
CARDS = {c['id'] for c in json.loads(re.search(r'<script[^>]*id=["\']CARDS["\'][^>]*>([\s\S]*?)</script>', S).group(1))}
ADD = ['F1-45', 'F1-147']
OLD_SAY = '그 사이에 RNA 가공이 끼어든다, 다음 과.'
NEW_SAY = ('그 사이에 RNA 가공이 끼어든다, 다음 과. 담장이 일을 여러 곳으로 갈라 놓으니 손댈 곳도 는다. 찍기 전, 찍을 때, 손질할 때, 구멍으로 내보낼 때, 밖에서 읽을 때, 읽고 난 뒤. '
           '진핵의 유전자 발현이 세균보다 복잡한 까닭이 이것, 전사 이전부터 번역 이후까지 여러 단계에서 조절된다. 담장 없는 왼쪽 마당은 찍으면서 바로 읽으니 손댈 곳이 찍는 자리 하나뿐. '
           '세균은 주로 전사 수준에서 단순하게 조절하고(오페론), 진핵은 여러 단계에서 겹겹이 조절한다.')
OLD_FACT = '진핵은 전사(핵)와 번역(세포질)이 공간으로 갈린다 — 그 사이에 RNA 가공'
NEW_FACT = '진핵은 전사(핵) · 번역(세포질)이 갈린다 — 사이에 RNA 가공 · 조절도 여러 단계'
OLD_HOOK = '안에서 만들고 밖에서 읽는다'
NEW_HOOK = '안에서 만들고 밖에서 읽는다 · 거치는 곳마다 손댈 곳 = 여러 단계의 조절'
st = next(s for s in d['stops'] if s['sid'] == 's8')
have = list(st.get('cards') or [])
bad = 0
for c in ADD:
    if c not in CARDS: print('✕ 카드 없음', c); bad += 1
    if c in have: print('✕ 이미 있음', c); bad += 1
if st['say'].count(OLD_SAY) != 1: print('✕ say'); bad += 1
if st['fact'] != OLD_FACT: print('✕ fact', st['fact']); bad += 1
if st['hook'] != OLD_HOOK: print('✕ hook', st['hook']); bad += 1
if bad: raise SystemExit(f'✕ {bad}')
st['cards'] = have + ADD                                   # s2 와 같은 자리(src 뒤)
st['say'] = st['say'].replace(OLD_SAY, NEW_SAY); st['fact'] = NEW_FACT; st['hook'] = NEW_HOOK
assert len(st['say']) <= 560 and len(st['fact']) <= 60, (len(st['say']), len(st['fact']))
print('L43a s8 + 2 → 카드', st['cards'], '· fact', len(st['fact']), '· say', len(st['say']), '· 열쇠', list(st.keys()))
if WRITE:
    open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=fmt[0]) + fmt[1]); print('written')

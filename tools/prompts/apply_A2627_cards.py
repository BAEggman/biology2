#!/usr/bin/env python3
# apply_A2627_cards.py — 26장(계통분류) · 27장(원핵생물) 덧붙임 가운데 「카드만」 7장(2026-11-17 · 지시서 차례 12 의 덧붙임 앞몫 — L03c).
#   L03c s1(세 가게 = 3역 · 우즈 rRNA) K2-28 / s2(앞의 둘이 원핵 = 모네라계를 둘로 가름) K2-29 · X-EV-8
#   L03c s6(Y 자 차양 = 에테르 지질 · 세포벽 펩티도글리칸 없음) K2-30 / s4(짚끈 감은 통 = 히스톤 · TATA 전사 기구) K2-31 · S-EV-17 · L0-28.
#   남은 1장(L0-27 극호염 · 극호열 · 메탄생성)은 L03c 뒤뜰 새 정거장.
import json, sys, re
ROOT = '/tmp/b2'; WRITE = '--write' in sys.argv
def load(lid):
    p = f'{ROOT}/lessons/{lid}.json'; t = open(p, encoding='utf-8').read(); d = json.loads(t)
    for ind in (1, 2):
        for nl in ('', '\n'):
            if json.dumps(d, ensure_ascii=False, indent=ind) + nl == t: return p, d, ind, nl
    raise SystemExit(f'✕ {lid} 파일 모양')
S = open(f'{ROOT}/index.html', encoding='utf-8').read()
CARDS = {c['id'] for c in json.loads(re.search(r'<script[^>]*id=["\']CARDS["\'][^>]*>([\s\S]*?)</script>', S).group(1))}
A = lambda old, add: (old, old + ' ' + add)
OPS = [
 ('L03c', 's1', ['K2-28'], *A('왼쪽이 세균, 가운데가 고세균, 오른쪽이 진핵.',
   '우즈가 리보솜 RNA, 곧 rRNA 서열을 비교해 세운 세 영역, 3역 체계다.')),
 ('L03c', 's2', ['K2-29', 'X-EV-8'], *A('고세균도 칸막이가 없어서 세균과 함께 원핵생물로 묶인다.',
   '예전에는 원핵생물을 모네라계 하나로 묶었으나, 세균과 고세균이 서로 별개의 역임이 밝혀져 모네라계는 폐기되었다.')),
 ('L03c', 's4', ['K2-31', 'S-EV-17', 'L0-28'], *A('일부 유전자에 인트론이 있는 것, RNA 중합효소가 진핵형으로 복잡한 것도 진핵을 닮았다.',
   '또한 TATA 결합 단백질 계열의 전사 기구를 가져 유전자 발현 축에서는 세균보다 진핵생물에 더 가깝다. 반면 세포벽에는 세균과 달리 펩티도글리칸이 없다.')),
 ('L03c', 's6', ['K2-30'], *A('세균과 진핵은 에스테르 결합에 곧은 사슬, 고세균만 에테르 결합에 가지 친 곁사슬.',
   '이 에테르 가지 사슬 막지질은 극한 환경에서도 안정하며, 고세균 세포벽에는 펩티도글리칸이 없다.')),
]
files = {}; bad = 0; nc = 0
for lid, sid, cards, old, new in OPS:
    if lid not in files: files[lid] = load(lid)
    p, d, ind, nl = files[lid]
    st = next(s for s in d['stops'] if s['sid'] == sid)
    have = set(st.get('cards') or [])
    for c in cards:
        if c.split('#')[0] not in CARDS and c not in CARDS: print('✕ 카드 없음', c); bad += 1
        if c in have: print('✕ 이미 있음', lid, sid, c); bad += 1
    st['cards'] = list(st.get('cards') or []) + cards; nc += len(cards)
    if old:
        if st['say'].count(old) != 1: print('✕ old', lid, sid, st['say'].count(old), old); bad += 1; continue
        st['say'] = st['say'].replace(old, new)
    if len(st['say']) > 560: print('✕ 말', lid, sid, len(st['say'])); bad += 1
    print(lid, sid, '+', len(cards), 'say', len(st['say']))
print('카드', nc)
if bad: raise SystemExit(f'✕ {bad}')
if WRITE:
    for lid, (p, d, ind, nl) in files.items():
        open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=ind) + nl)
    print('written', list(files))

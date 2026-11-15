#!/usr/bin/env python3
# apply_A면역_cards.py — 면역 덧붙임 중 「카드만」 붙이는 것(그림 손대지 않음 · 2026-11-15 · Opus 5.5) — 카드 더하기 + 말 보태기(old 가 정확히 한 번).
#   L01c s4 IM-100(항원 변이) · L01c s9 IM-105(HIV 는 제 역전사효소) · L49c s2 IM-095(자가면역 질환의 뜻).
#   IM-103 · 104(HIV 진입 — gp120 · CD4 · CXCR4 / CCR5)는 여기서 하지 않는다 — 같은 사실의 19장 카드 I0-53 · 54 와 옛 판 s02p01 「정문」을
#   물려받는 새 그림 P6 「항구 세관」(지시서 차례 16)에 함께 건다(A면역_덧붙임_설계.md §2).
# 사용: python3 apply_A면역_cards.py [--write]
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
OPS = [
 ('L01c', 's4', ['IM-100'],
  'A형에서는 이 과정이 항원 대변이로 이어져 대유행 균주가 출현할 수 있다.',
  'A형에서는 이 과정이 항원 대변이로 이어져 대유행 균주가 출현할 수 있다. 재편성이든 작은 돌연변이든 겉의 항원이 바뀌면, 몸이 기억해 둔 얼굴과 달라져 지난번 면역을 피한다. 이것이 항원 변이다. 독감이 해마다 다시 오는 까닭이고, 수면병의 트리파노소마도 겉옷을 갈아입어 같은 수를 쓴다.'),
 ('L01c', 's9', ['IM-105'],
  '방향이 거꾸로다.',
  '방향이 거꾸로다. 이 효소는 숙주에게 빌리지 않는다. V 번 부두의 선원이 제 크레인을 메고 왔듯, HIV 는 입자 안에 제 역전사효소를 싣고 들어와 그것으로 DNA 를 만든다. 숙주 것이 아니라 HIV 자신의 효소다.'),
 ('L49c', 's2', ['IM-095'],
  '자가면역이다. 그래서 1형은 인슐린 의존성이다.',
  '자가면역이다. 자기 몸의 성분을 비자기, 곧 남으로 잘못 알아보고 공격하는 병을 자가면역 질환이라 한다. β 세포를 잃었으니 1형은 인슐린 의존성이다.'),
]
files = {}; bad = 0
for lid, sid, cards, old, new in OPS:
    if lid not in files: files[lid] = load(lid)
    p, d, ind, nl = files[lid]
    st = next(s for s in d['stops'] if s['sid'] == sid)
    have = set(st.get('cards', []))
    for c in cards:
        if c not in CARDS: print('✕ 카드 없음', c); bad += 1
        if c in have: print('✕ 이미 있음', lid, sid, c); bad += 1
    st['cards'] = list(st.get('cards', [])) + cards
    if old:
        if st['say'].count(old) != 1: print('✕ old', lid, sid, old); bad += 1; continue
        st['say'] = st['say'].replace(old, new)
        if len(st['say']) > 560: print('✕ 말', lid, sid, len(st['say'])); bad += 1
    print(lid, sid, '+', len(cards), 'say', len(st['say']))
    print('   ', st['say'])
if bad: raise SystemExit(f'✕ {bad}')
if WRITE:
    for lid, (p, d, ind, nl) in files.items():
        open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=ind) + nl)
    print('written', list(files))

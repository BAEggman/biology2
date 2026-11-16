#!/usr/bin/env python3
# apply_A23_cards.py — 23장(집단진화) · 22장(진화) 덧붙임 가운데 「카드만」(그림 손대지 않음 · 2026-11-16 · Opus 5.5 · 지시서 차례 8).
#   L35b s2 3(선택은 편집 · 국지 환경 · 방향성 선택) · s3 1(적응도 = 번식 — 글에 있음) · s10 2(효과 축 — 글에 있음 · 완벽은 못 만든다 넷) · L35a s6 1(유성생식은 재배열만).
#   「+정거장」(L35b 홈통 둘 · 하트 단 수컷 · 짝 구슬 물굽이 / L35a 이산 vs 연속)은 그림을 보태는 일 — 차례 8 그림 몫(Gemini).
# 사용: python3 apply_A23_cards.py [--write]   (두 과 모두 gen 파일 없음 — JSON 이 원본)
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
N = (None, None)
OPS = [
 ('L35b', 's2', ['J0-19', 'J0-21', 'J1-26'], *A('여기서는 까마귀가 물어 던지는 흰 구슬이 불리한 쪽이고, 물에 남는 검은 구슬이 유리한 쪽이다.', '까마귀는 구슬을 새로 만들지도 칠하지도 않는다. 이미 있던 구슬 가운데서 고를 뿐이니 선택은 창조가 아니라 편집이다. 약이 내성균을 만드는 게 아니라 이미 있던 내성 개체를 골라 남긴다. 검은 구슬이 유리한 것도 지금 이 물굽이의 이야기, 다른 물가에서는 쓸모없거나 해로울 수 있다. 늘 한쪽 색만 골라 평균이 한 방향으로 옮겨 가는 것이 방향성 선택이다. 항생제 내성균, 가뭄 뒤 부리가 커진 핀치.')),
 ('L35b', 's3', ['J0-43'], *N),
 ('L35b', 's10', ['S-EV-13', 'J1-34'], *A('어제의 평형에서 이 셋 가운데 하나만 풀려도, 그 집단은 진화한다.', '그래도 까마귀가 완벽한 연못을 만들지는 못한다. 까닭은 넷, 이미 있는 구슬 위에서만 고르는 역사적 제약, 한쪽을 얻으면 다른 쪽을 잃는 절충, 연못에 없는 색은 고를 수 없는 변이 의존, 그리고 부동 같은 우연한 비적응 과정.')),
 ('L35a', 's6', ['J1-7'], *A('유전적 변이의 원천을 셋 꼽으면 돌연변이, 유전자 중복, 그리고 재조합을 일으키는 유성생식이다.', '다만 유성생식은 새 색을 칠하지 않는다. 새 대립유전자 없이 있던 것을 새 조합으로 재배열할 뿐이다.')),
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

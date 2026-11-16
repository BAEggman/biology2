#!/usr/bin/env python3
# apply_A3234_cards.py — 32장(동물의 다양성) · 33장(무척추동물) 덧붙임 가운데 「카드만」(그림 손대지 않음 · 2026-11-16 · Opus 5.5 · 지시서 차례 11 의 덧붙임 앞몫 — Gemini 없이 할 수 있는 것).
#   L04a s8(겹 둘뿐인 작은 공) X-AN-9 · N1-3 · N1-6 / L04b s3(노천 정수장 스펀지) S-AN-1 · N0-24 · N1-2 · s1(바닥 = 체강) N0-16 · s11(껍질 벗기) S-AN-2 · s4(깃 칼라) N0-8
#   L04c s8(마디 진 소시지 건물) N1-20 / L04e s2(달팽이 · 지렁이 · 게 간판) S-AN-6.
#   새 정거장(L04a 빵집 간판 · L04e 두 손님 · 별 간판 뒤판 · L04b 폴립 · 메두사 · L04c 액자 · 손님 차림 · 문어 · L04f 셋)은 `L04gh_설계.md` §6 — Gemini 를 다시 쓸 때.
# 사용: python3 apply_A3234_cards.py [--write]   (gen 파일 없음 — JSON 이 원본)
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
 ('L04a', 's8', ['X-AN-9', 'N1-3', 'N1-6'], *A('다만 신경과 근육이 아예 없는 쪽은 해면이고, 자포는 신경망과 수축하는 세포를 갖는다.',
   '자포동물은 몸이 방사대칭이고, 뇌 없이 온몸에 그물처럼 퍼진 신경망으로 사방을 느낀다.')),
 ('L04b', 's3', ['S-AN-1', 'N0-24', 'N1-2'], *A('물은 작은 구멍 유입공으로 들어와 큰 구멍 출수공 하나로 나간다.',
   '해면 몸속에는 변형세포가 기어 다니며 양분을 나르고, 뼈대인 골편과 해면질을 만든다. 동물 계통수의 맨 밑 세 갈래는 조직 없는 해면, 2배엽 방사대칭의 자포, 3배엽의 좌우대칭동물이다. 조직을 가진 나머지 동물 전부를 진정후생동물이라 한다.')),
 ('L04b', 's1', ['N0-16'], *A('바닥만 보고 세 구역을 가른다.',
   '다만 체강은 진화하면서 여러 번 따로 생기고 사라져서, 바닥만으로 계통을 가르지는 않는다.')),
 ('L04b', 's11', ['S-AN-2'], *A('윤형과 편형, 다음 과의 연체와 환형은 탈피하지 않는 촉수담륜동물로 따로 묶인다.',
   '선구동물의 두 갈래를 가르는 기준은 탈피동물의 큐티클 탈피와, 촉수담륜동물의 담륜자 유생 · 촉수관이다.')),
 ('L04b', 's4', ['N0-8'], *N),
 ('L04c', 's8', ['N1-20'], *A('여기는 몸 자체가 마디로 나뉜 건물, 마디가 뜻이다.',
   '환형동물에는 땅속의 지렁이, 피를 빠는 거머리, 바다의 갯지렁이가 있다.')),
 ('L04e', 's2', ['S-AN-6'], *A('연체, 환형, 절지는 전부 선구동물.',
   '넷을 가르는 결정적 표지는 연체의 치설과 외투막, 환형의 체절과 강모, 선충의 큐티클, 절지의 관절 진 다리다.')),
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

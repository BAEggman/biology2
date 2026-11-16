#!/usr/bin/env python3
# apply_A2831_cards.py — 28장(원생생물) · 31장(균류) 덧붙임 가운데 「카드만」(그림 손대지 않음 · 2026-11-16 · Opus 5.5 · 지시서 차례 10).
#   28장: L04b s4(물 붓는 일꾼의 깃 칼라 = 깃세포) — 깃편모충이 꼭 닮았다 → 동물 · 균류와 오피스토콘타(L1-24 · X-EV-12).
#   31장: L05a s8(물뿌리개 즙 · 녹는 낙엽) 영양 셋 · 분해자(M2-2 · M2-22) · s7(바위 위 오두막) 개척자(M2-26) · s11(키틴 겹비늘 = 절지와 같은 재료) 오피스토콘타(M2-16)
#         L05b s1(산울타리 칸 줄 = 균사 · 캠핑장 그물 = 균사체 M2-3) · s7(가로막 없는 통로 = 다핵균사 · 칸 = 격벽균사 M2-5) · s3(한 칸에 천막 둘 = n+n X-EV-22 — 글에 있음).
#   「+정거장」(L05a 녹슨 잎 흡기 · 잎 속 내생균 / L05b 캠핑장 매점 — 분생포자 · 효모 출아 · 불완전균)은 그림을 보태는 일 — `A2831_덧붙임_설계.md`(Gemini 구역 편집).
# 사용: python3 apply_A2831_cards.py [--write]   (세 과 모두 gen 파일 없음 — JSON 이 원본)
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
 ('L04b', 's4', ['L1-24', 'X-EV-12'], *A('편모로 물을 끌어들이고, 깃으로 세균과 먹이 알갱이를 걸러 삼킨다. 여과섭식.',
   '이 깃 두른 세포를 꼭 닮은 홑세포 원생생물이 깃편모충이다. 동물과 가장 가까운 원생생물 친척이라, 깃편모충과 동물과 균류를 함께 묶어 오피스토콘타라 한다.')),
 ('L05a', 's8', ['M2-2', 'M2-22'], *A('녹아 나온 작은 분자만 몸 안으로 흡수한다. 방향은 언제나 밖에서 안이다.',
   '무엇을 녹여 먹느냐로 셋이다. 죽은 유기물을 녹이는 분해자, 살아 있는 숙주에서 빼 먹는 기생, 서로 주고받는 상리공생. 이 낙엽처럼 셀룰로오스와 리그닌까지 녹이는 균류가 생태계의 핵심 분해자이고, 탄소와 질소를 다시 돌게 한다.')),
 ('L05a', 's7', ['M2-26'], *A('식물에 해를 끼치지 않고 잎 속에 들어가 사는 내생균도 대부분 자낭균이다.',
   '지의류는 흙 한 줌 없는 맨 바위에도 이렇게 붙어 살며 바위를 부수고 흙을 만든다. 1차 천이의 개척자다.')),
 ('L05a', 's11', ['M2-16'], *A('균류의 세포벽은 키틴이고, 절지동물의 외골격과 재료가 같다.',
   '균류는 식물보다 동물에 더 가깝다. 깃편모충, 동물과 함께 오피스토콘타로 묶인다.')),
 ('L05b', 's1', ['M2-3'], *A('칸 하나가 세포, 천막 하나가 핵 하나, 곧 반수체 n 이다.',
   '칸이 한 줄로 길게 이어진 것이 균사, 가는 관 꼴의 실이고, 그 줄들이 캠핑장 가득 얽힌 그물 전체가 균사체다. 가늘게 퍼져 부피에 비해 겉넓이가 크니 흡수에 유리하다.')),
 ('L05b', 's7', ['M2-5'], *A('균사를 칸으로 나누는 격벽이 없어서, 한 세포질 안에 핵이 여럿 들어 있다.',
   '핵분열만 거듭하고 세포질은 나누지 않아 생긴 것이다. 산울타리 가로막으로 칸이 나뉜 다른 줄은 격벽균사이고, 가로막에 구멍이 있어 핵이 오갈 수 있다.')),
 ('L05b', 's3', ['X-EV-22'], *N),
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

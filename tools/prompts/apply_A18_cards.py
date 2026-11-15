#!/usr/bin/env python3
# apply_A18_cards.py — 18장(유전자 발현 조절) 덧붙임 가운데 「카드만」(그림 손대지 않음 · 2026-11-15 · Opus 5.5 · 지시서 차례 6).
#   L43b 1(pre-mRNA) · L43g s5 3(유비퀴틴 · 프로테아좀 — 계획은 L19c 였으나 12장 덧붙임 때 그 꼴이 L48e s10 에 있음을 확인했고,
#     18장의 「단백질 분해로 양 조절」은 방금 지은 L43g s5 의 입술 자국 공 + 통 분쇄기가 맡는다) · L16c 2(Ras) · L19d 10(원종양 · 암유전자 · 다단계 · 유전성 · 폴립)
#   · L25b 5(조절유전자 따로 · 약화 = 2차 · trp ↔ lac) · L25a 4(lacZ · Y · A · 오페론 = 필요한 효소만) · L37b 2(히스톤 꼬리 · 접근성 ↔ 기계 모집).
#   「+정거장」(L25b 하나 · L25a 하나 · L37b 셋)은 그림을 보태는 일 — A18_덧붙임_설계.md.
# 사용: python3 apply_A18_cards.py [--write]   → L43g 는 gen 파일이 있으니 뒤이어 `python3 tools/kit/gen_sync.py L43g`
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
 ('L43b', 's1', ['F1-80'], *N),
 ('L43g', 's5', ['F1-90', 'F1-91', 'F1-166'], 'L48e 의 유비퀴틴과 프로테아좀, 단백질 분해다. 다 쓴 단백질을 부숴 양을 조절한다.', 'L48e 의 유비퀴틴과 프로테아좀이다. 입술 자국, 유비퀴틴은 분해할 단백질에 붙이는 표지이고, 그 표지를 단 것만 통 분쇄기, 프로테아좀이 부순다. 이미 만든 단백질의 양과 수명을 빠르게 조절하는 길이다.'),
 ('L16c', 's5', ['F1-133'], *A('교환국의 큰 지게꾼과 같은 집안인데 몸집이 작다.', '타이 창구에서 받은 성장 신호를 아래로 이어 나르는 것이 정상 라스의 일이다.')),
 ('L16c', 's9', ['F1-134'], '지티피를 가수분해하지 못해 늘 켜져 있으니', '지티피를 가수분해하지 못해 성장 신호가 없어도 늘 켜져 있으니'),
 ('L19d', 's10', ['F1-128', 'F1-129', 'F1-169', 'F1-131', 'F1-132'], '원종양유전자가 돌연변이로 늘 켜지면 암유전자가 된다. 대표가 Ras 와 Myc.', '원종양유전자는 정상일 때 세포의 성장과 분열을 돕는 유전자다. 이것이 돌연변이로 늘 켜지면 암유전자가 된다. 대표가 Ras 와 Myc. 바뀌는 길은 셋, 자리 이동, 유전자 증폭, 점 돌연변이. 한쪽 대립유전자만 과활성이 되어도 미는 힘이 생기니 암유전자는 우성처럼 행동한다.'),
 ('L19d', 's11', ['F1-127', 'F1-140'], *A('정상세포가 이렇게 암세포로 바뀌는 과정을 형질전환이라 한다.', '암은 세포 주기와 성장을 조절하는 유전자들에 돌연변이가 쌓여 생긴다. 하나로는 안 되고 여럿이 쌓여야 하는 것, 다단계 모델이다.')),
 ('L19d', 's7', ['F1-142'], *A('두 대립유전자가 모두 기능을 잃어야 드러난다.', '왼 문처럼 빗장 하나가 처음부터 부러진 채 태어나면 이미 한 단계를 지고 시작하니, 유전성 암이 위험한 까닭이다.')),
 ('L19d', 's13', ['F1-145'], *A('막는 쪽과 고치는 쪽이 같은 갈래의 두 몫.', '성장 · 분열 · 수복을 맡은 이런 유전자들의 조절이 무너지는 것, 그래서 암은 유전자 발현 조절과 이어진다.')),
 ('L19d', 's14', ['F1-141'], *A('제자리에 머무는 양성종양이다.', '상피에서 이렇게 처음 불어난 덩어리가 폴립, 또는 선종이다.')),
 ('L25b', 's2', ['F1-34'], *A('trp 억제자는 늘 만들어지지만 혼자서는 비활성이다.', '억제자를 만드는 조절유전자는 문지기처럼 오페론 줄 밖에 따로 떨어져 제 프로모터를 갖는다.')),
 ('L25b', 's5', ['F1-176'], *A('트립토판이 부족하면 켜진다는 것과 같은 결론이다.', '약화는 억제와 따로 도는 2차 조절이다.')),
 ('L25b', 's7', ['F1-44', 'F1-151', 'F1-152'], '그래도 둘 다 억제자에 의한 음성 조절을 받는다는 점은 같다.', 'trp 는 합성 경로의 억제성, lac 은 분해 경로의 유도성이다. 그래도 둘 다 조절유전자가 만든 억제자가 작동자 부근에서 전사를 다스리는 음성 조절을 받는다는 점은 같다. 다른 점은 억제자를 다루는 손, trp 는 최종산물이 보조억제자로 억제자를 켜고, lac 은 기질에서 온 유도자가 억제자를 끈다.'),
 ('L25a', 's1', ['F1-18', 'F1-19', 'F1-20'], *A('빨간 매트가 프로모터, 문턱이 작동자, 그림 타일 셋이 구조유전자다.', '차례로 해가 lacZ(β-갈락토시다아제), 나무가 lacY(퍼메이스), 집이 lacA(트랜스아세틸화효소).')),
 ('L25a', 's11', ['F1-35'], *A('포도당이 없을 때 가장 강하게 켜지는 유도성 오페론이다.', '오페론이 보여 주는 것은 하나, 세균은 환경에 따라 전사를 조절해 필요한 효소만 만든다.')),
 ('L37b', 's5', ['F1-53'], *A('히스톤 꼬리의 대표 변형은 아세틸화, 메틸화, 인산화 셋이다.', '히스톤 꼬리는 뉴클레오솜 밖으로 삐져나온 히스톤의 N 말단 영역이다.')),
 ('L37b', 's1', ['F1-94'], *A('그 차이가 그 안의 유전자가 읽히느냐 안 읽히느냐를 가른다.', '염색질 수준의 조절은 DNA 에 손이 닿느냐, 접근성 자체를 다스린다. 전사 개시의 조절은 그 자리에 전사 기계를 불러 모으는 일을 다스린다.')),
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

#!/usr/bin/env python3
# apply_A17_cards.py — 17장(유전자의 발현) 덧붙임 가운데 「카드만」(그림 손대지 않음 · 2026-11-15 · Opus 5.5 · 지시서 차례 6).
#   L10a 19(리보솜 몸 · 개시 AUG · 합성효소 스물 · 요동 U · N → C · 전위 · 신장 인자 · 방출 인자 = 물 · 가수분해) · L43b 7(캡 = 변형 G · 20 ~ 40 nt · 꼬리 50 ~ 250 A · AAUAAA 뒤 절단 · 3′ UTR · GU … AG)
#   · L43a 1(원핵 mRNA 가공 적음) · L16a 1(지용성 호르몬 = 직접 전사인자 — 글에 이미 있음).
#   L10a 의 「+정거장 둘」(스캐닝 · 코작 vs 샤인-달가노 · fMet / GTP 칩)은 그림을 보태는 일 — A17_덧붙임_설계.md.
# 사용: python3 apply_A17_cards.py [--write]   (네 과 모두 gen 파일 없음 — JSON 이 원본)
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
 ('L10a', 's1', ['F0-86'], *A('리보솜은 mRNA를 5′에서 3′로 읽는다.', '레일은 코돈을 차례로 내주는 주형이다.')),
 ('L10a', 's2', ['F0-17', 'F0-88', 'F0-90', 'F0-111', 'F0-89'], *A('S는 더하지 않는다.', '정거장은 rRNA 와 단백질로 지었다. rRNA 는 세균 리보솜에 세 가닥, 진핵 리보솜에 네 가닥이다. 레일을 무는 작은 상자가 mRNA 와 결합하는 쪽이다. 진핵세포에서 번역은 이렇게 세포질의 리보솜에서 일어난다. 테트라사이클린 · 스트렙토마이신은 칠십 S 만 막아 세균 리보솜만 멈추고 우리 리보솜은 건드리지 않는다. 선택적 독성이다.')),
 ('L10a', 's3', ['F0-22'], *A('곧장 P에 앉는다.', '개시 코돈은 AUG, 그가 든 구슬은 메티오닌이다.')),
 ('L10a', 's5', ['F0-101'], *A('구슬을 받은 사람이 충전된 tRNA다.', '자판기는 아미노산마다 하나씩, 스무 가지쯤 있다.')),
 ('L10a', 's6', ['F0-106'], *A('안티코돈 첫 자리가 이노신이면 U, C, A 셋과 다 짝짓는다.', '첫 자리가 U 면 코돈 셋째 자리의 A 와 G 를 둘 다 읽는다.')),
 ('L10a', 's7', ['F0-122', 'F0-123', 'F0-132'], *A('거꾸로 외우면 틀린다.', '그래서 사슬은 늘 새 구슬 쪽, C 말단으로 자란다. 맨 처음 구슬이 N 말단이고, 정거장 밖으로 먼저 빠져나오는 것도 N 말단이다.')),
 ('L10a', 's8', ['F0-112', 'F0-113'], *N),
 ('L10a', 's9', ['F0-125'], '전위 또는 전좌라고도 부른다.', '전위(translocation) 또는 전좌라고도 부른다.'),
 ('L10a', 's10', ['F0-129', 'F0-130'], *A('종결 코돈에는 tRNA 대신 방출 인자가 결합하고, 사슬이 풀려난다.', '방출 인자는 사슬 끝에 물 한 분자를 붙여 tRNA 에서 끊는다. 가수분해다.')),
 ('L10a', 's11', ['F0-114'], *N),
 ('L10a', 's12', ['F0-127'], *A('A는 들어옴, P는 펩타이드 보유, E는 나감.', '이 신장의 걸음마다 신장 인자라는 단백질들이 거든다.')),
 ('L43b', 's2', ['F0-58', 'F0-60'], *A('모자가 곧 5′ 캡.', '모자는 변형된 구아닌 하나, 전사가 스무에서 마흔 뉴클레오타이드쯤 나아간 직후에 씌운다.')),
 ('L43b', 's3', ['F0-62', 'F0-46', 'F0-47'], '띠의 3′ 끝에 아데닌 뉴클레오타이드만 수십에서 수백 개, 주형 없이 덧붙인 것.', '띠의 3′ 끝에 아데닌 뉴클레오타이드만 쉰에서 이백오십 개쯤, 주형 없이 덧붙인 것. 그 전에 띠는 AAUAAA 신호 조금 뒤에서 잘려 기계를 떠나고, 술은 그 잘린 끝에 단다.'),
 ('L43b', 's5', ['F0-64'], *A('남되 번역되지 않는다.', '꼬리 쪽 3′ UTR 은 번역되지 않고 조절을 맡는다.')),
 ('L43b', 's5', ['F0-71'], *A('잘라 내고 남은 것을 잇는 것이 스플라이싱.', '회색 토막은 대개 GU 로 시작해 AG 로 끝난다.')),
 ('L43a', 's2', ['F0-54'], *A('원핵은 전사와 번역이 동시에 일어난다.', '손질할 틈도 없이 곧바로 읽히니 원핵 mRNA 는 가공이 거의 없다.')),
 ('L16a', 's11', ['F0-43'], *N),
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

#!/usr/bin/env python3
# apply_A11_cards.py — 11장(광합성) 덧붙임 가운데 「카드만」(그림 손대지 않음 · 2026-11-16 · Opus 5.5 · 지시서 차례 7).
#   L45a 5(반응식 · 물 = 전자 · H⁺ / CO₂ = 탄소 · 먹이와 산소 · stomata) · L45c 9(P680⁺ · 센 산화제 · 물 분해 산물 · ¹⁸O · 자색황세균 · b₆f · NADP⁺ 환원효소 · 순환의 Fd → 사이토크롬 · H⁺ 기울기 두 원천)
#   · L45d 5(캘빈-벤슨 · RuBP 풀이름 · C₃ 작물 · G3P = 전구체 · O₂ 는 부산물) · L45e 4(C₄ 작물 · CAM 풀이 · CAM 식물 · 밤 · 낮 · 유기산).
#   「+정거장」(L45a 제 도시락 싸는 사람 vs 남의 도시락을 집는 사람)은 그림을 보태는 일 — A11_덧붙임_설계.md · A11_set.json.
# 사용: python3 apply_A11_cards.py [--write]   (네 과 모두 gen 파일 없음 — JSON 이 원본)
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
 ('L45a', 's1', ['C0-1', 'C0-240', 'C0-2', 'C0-21'], *A('널이 잎, 꼬투리가 그 안의 알갱이 하나, 엽록체다.', '반응식으로는 이산화탄소 여섯과 물 여섯이 빛에너지로 포도당 하나와 산소 여섯이 된다. 물은 전자와 수소 이온을, 이산화탄소는 탄소를 댄다. 생물권에 먹이, 곧 유기물과 숨 쉴 산소를 함께 대니 지구 생명에 꼭 필요한 일이다.')),
 ('L45a', 's4', ['C0-24'], *A('기공은 주로 잎 아랫면에 있다.', '기공 하나는 스토마, 여럿이면 스토마타.')),
 ('L45c', 's5', ['C0-95'], *A('엽록소 에이는 같은 분자인데 단백질 환경이 달라 흡수 파장이 다르다.', '피육백팔십은 전자를 내주면 피육백팔십 플러스가 된다.')),
 ('L45c', 's6', ['C0-88', 'C0-93', 'C0-15', 'C0-16'], *A('산소가 이산화탄소가 아니라 물에서 나온다는 것은 반 닐이 황세균 연구에서 끌어낸 결론이다.', '전자를 잃은 피육백팔십 플러스는 아주 센 산화제라 물에서도 전자를 뽑아 온다. 물이 쪼개지면 전자, 수소 이온, 산소가 나온다. 반 닐의 결론은 산소 동위원소 십팔을 붙인 물을 추적해 확인했다. 물 대신 황화수소를 쓰는 자색황세균 같은 무산소 광합성 세균은 산소를 내지 않는다.')),
 ('L45c', 's8', ['C0-102'], '다음은 계단 가운데 돌 성인 사이토크롬 복합체, 그 아래는 데스크톱 피시다.', '다음은 계단 가운데 돌 성인 사이토크롬 복합체, 정식 이름 사이토크롬 b₆f 복합체다. 그 아래는 데스크톱 피시다.'),
 ('L45c', 's9', ['C0-106'], '수소 이온 하나를 환원효소가 엔에이디피 플러스에 전달해', '수소 이온 하나를 페레독신 다음의 효소, 엔에이디피 플러스 환원효소가 엔에이디피 플러스에 전달해'),
 ('L45c', 's11', ['C0-124'], *N),
 ('L45c', 's12', ['C0-110'], *A('엔에이디피에이치를 만들 때도 스트로마 수소 이온을 하나 쓴다.', '선형 흐름에서 이 기울기를 만드는 원천은 둘, 루멘 안에서 물이 쪼개질 때 남는 수소 이온과 플라스토퀴논이 사이토크롬 복합체를 거치며 루멘으로 옮기는 수소 이온.')),
 ('L45d', 's1', ['C0-245'], *A('캘빈 회로는 고정, 환원, 재생 세 단계이고 한 바퀴에 이산화탄소 하나를 붙잡는다.', '캘빈-벤슨 회로라고도 한다.')),
 ('L45d', 's3', ['C0-155'], '마디 다섯 막대는 오탄당 알유비피.', '마디 다섯 막대는 오탄당 알유비피, 리불로오스 1,5-이인산.'),
 ('L45d', 's4', ['C0-186'], *A('첫 안정 산물이 삼탄이라 씨쓰리 식물.', '벼, 밀, 대두가 대표 씨쓰리 작물이다.')),
 ('L45d', 's8', ['C0-179', 'C0-241'], *A('포도당 하나에 이산화탄소 여섯, 에이티피 열여덟, 엔에이디피에이치 열둘.', '나간 지쓰리피가 포도당과 다른 유기물의 전구체다. 빛반응의 산소는 버려지는 부산물이고, 쓸모 있는 유기물의 재료는 이 지쓰리피다.')),
 ('L45e', 's6', ['C0-202'], *A('이 첫 고정은 엽육세포에서.', '대표 씨포 식물은 옥수수와 사탕수수.')),
 ('L45e', 's9', ['C0-221', 'C0-222', 'C0-235'], *A('먼저 옥살아세트산, 이것을 사탄 말산으로 바꿔 액포에 담아 둔다.', '캠은 돌나물과 유기산 대사, 크래슐러시언 애시드 메타볼리즘의 머리글자. 파인애플, 선인장, 다육식물이 대표다. 외울 말은 셋, 밤, 낮, 유기산 저장.')),
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

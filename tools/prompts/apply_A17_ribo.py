#!/usr/bin/env python3
# apply_A17_ribo.py — 17장 「리보솜의 행선지」 10장을 이미 그 사실을 나르는 정거장에 덧붙인다(그림 손대지 않음 · 카드 더하기 + 말 보태기).
#   계획 P8 은 이 10장을 새 그림에 넣으려 했으나, 그 뒤에 지은 L48d(긴 막사)가 같은 물건(지붕의 보라 짝 · 안내인 · 빨간 머리 구슬 · 접힌 구슬 공)을 이미 나른다 → 다시 그리지 않는다.
#   L48d 는 gen_L48d.py 가 원본이다 — 이 스크립트는 gen_L48d.py 의 글도 같이 고친다(--write 뒤 gen 과 json 이 같아야 한다).
# 사용: python3 apply_A17_ribo.py [--write]
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
 # 자유 · 부착 리보솜이 만드는 것 · 둘은 같은 리보솜(전환)
 ('L48d', 's3', ['F0-136', 'F0-137', 'F0-138'],
  '그리고 이렇게 조면소포체와 핵 바깥막에 붙은 부착 리보솜.',
  '그리고 이렇게 조면소포체와 핵 바깥막에 붙은 부착 리보솜. 자유 리보솜은 세포질에서 일할 단백질을, 부착 리보솜은 분비 단백질과 내막계 단백질을 만든다. 둘은 똑같은 리보솜이다. 따로 정해진 종류가 아니라, 지금 꿰는 사슬에 따라 풀밭과 지붕을 오간다.'),
 # 신호 펩타이드(약 20 aa · N 말단) · SRP(단백질-RNA 복합체) · 막의 수용체로 · 번역 도중
 ('L48d', 's6', ['F0-139', 'F0-140', 'F0-141', 'F0-142', 'F0-143'],
  '빨간 머리 구슬이 신호서열이다. 사슬의 N 말단, 맨 먼저 나오는 쪽에 붙는다. 그 신호를 알아보는 안내인이 SRP, 신호인식입자. SRP 가 리보솜째 조면소포체로 데려가면, 폴리펩타이드는 막에 박힌 단백질 복합체의 구멍을 지나 내강으로 들어간다.',
  '빨간 머리 구슬이 신호서열, 신호 펩타이드다. 아미노산 스무 개쯤으로, 사슬의 N 말단, 맨 먼저 나오는 쪽에 붙는다. 그 신호를 알아보는 안내인이 SRP, 신호인식입자 — 단백질과 RNA 가 뭉친 복합체다. SRP 가 리보솜째 조면소포체 막의 수용체로 데려가면, 폴리펩타이드는 막에 박힌 단백질 복합체의 구멍을 지나 내강으로 들어간다. 다 꿴 뒤가 아니라 꿰는 도중, 번역이 끝나기 전에 막에 닿는 것이다.'),
 # 들어간 뒤의 대표 가공 = 폴딩
 ('L48d', 's7', ['F0-145'],
  '분비 단백질은 내강에서 제 모양으로 접힌다.',
  '분비 단백질은 내강에서 제 모양으로 접힌다. 소기관 안으로 들어간 사슬이 겪는 대표 가공이 이 접힘, 폴딩이다.'),
 # 폴리좀의 장점
 ('L43a', 's2', ['F0-134'],
  '찍으면서 읽고 여럿이 한꺼번에 읽으니 세균은 단백질을 빨리 많이 만든다.',
  '찍으면서 읽고 여럿이 한꺼번에 읽으니 세균은 단백질을 빨리 많이 만든다. 폴리좀의 장점이 이것, mRNA 한 장으로 짧은 시간에 폴리펩타이드를 여럿 만든다. 진핵세포의 세포질에서도 같다.'),
]
files = {}; bad = 0
GEN = f'{ROOT}/tools/prompts/gen_L48d.py'; gen = open(GEN, encoding='utf-8').read()
for lid, sid, cards, old, new in OPS:
    if lid not in files: files[lid] = load(lid)
    p, d, ind, nl = files[lid]
    st = next(s for s in d['stops'] if s['sid'] == sid)
    have = list(st.get('cards', []))
    for c in cards:
        if c not in CARDS: print('✕ 카드 없음', c); bad += 1
        if c in have: print('✕ 이미 있음', lid, sid, c); bad += 1
    if st['say'].count(old) != 1: print('✕ old', lid, sid, old); bad += 1; continue
    if lid == 'L48d':                                   # gen_L48d.py 도 같이
        oc = json.dumps(have, ensure_ascii=False); ncs = json.dumps(have + cards, ensure_ascii=False)
        if gen.count(old) != 1 or gen.count('"cards": ' + oc) != 1: print('✕ gen', sid, gen.count(old), gen.count('"cards": ' + oc)); bad += 1
        gen = gen.replace(old, new).replace('"cards": ' + oc, '"cards": ' + ncs)
    st['cards'] = have + cards
    st['say'] = st['say'].replace(old, new)
    if len(st['say']) > 560: print('✕ 말', lid, sid, len(st['say'])); bad += 1
    print(lid, sid, '+', len(cards), '→ 카드', len(st['cards']), '· say', len(st['say']))
if bad: raise SystemExit(f'✕ {bad}')
if WRITE:
    for lid, (p, d, ind, nl) in files.items():
        open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=ind) + nl)
    open(GEN, 'w', encoding='utf-8').write(gen)
    print('written', list(files), '+ gen_L48d.py')

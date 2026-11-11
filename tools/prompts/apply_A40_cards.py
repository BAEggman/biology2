#!/usr/bin/env python3
# apply_A40_cards.py — 40·41장(+45 · 46장) 덧붙임 중 「카드만」 붙이는 것(그림 손대지 않음) — 카드 더하기 + 말 보태기(old 가 정확히 한 번).
# 사용: python3 apply_A40_cards.py [--write]
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
 ('L16a', 's1', ['G0-120', 'G0-132', 'G0-122', 'G0-135', 'Q0-8'],
  '수용, 전달, 반응.',
  '수용, 전달, 반응. 세포 밖 신호를 세포 안 반응으로 바꾸는 이 연속된 변화가 신호전달이다. 물에 녹는 수용성 호르몬은 막을 못 지나 이 창구, 세포 표면의 수용체에 붙는다. 막 수용체, 2차 전령, 증폭이 함께 나오면 수용성 호르몬의 길이다.'),
 ('L16a', 's4', ['G0-123'], None, None),
 ('L16a', 's11', ['G0-129', 'G0-130', 'G0-131', 'G0-133', 'G0-186', 'Q0-6', 'Q0-7', 'Q0-12'],
  '디엔에이의 전사를 조절한다.',
  '디엔에이의 전사를 조절한다. 호르몬과 수용체가 함께 핵으로 가는 것은 유전자 전사를 조절하기 위해서다. 유전자 발현이 바뀌니 반응이 늦게 오고 오래간다. 에스트로겐이 간세포에서 난황 전구물질 비텔로제닌을 만들게 하는 것이 그 예다. 핵 이동과 전사 조절이 함께 나오면 지용성 호르몬의 길. 지용성은 스테로이드와 티록신이고, 티록신은 아민인데 예외로 기름에 녹는다. 티록신과 비타민 D 의 수용체는 핵에, 스테로이드의 수용체는 보통 세포질에 있다.'),
 ('L16b', 's2', ['G0-124'],
  '이 캠프의 일을 시작한다.',
  '이 캠프의 일을 시작한다. 간세포 안에서 이 신호를 잇는 대표 2차 전령이 cAMP 다.'),
 ('L07b', 's8', ['G0-170'],
  '어른이 되어 지나치면 말단비대증이다.',
  '어른이 되어 지나치면 말단비대증이다. 성장이 끝난 뒤에도 손발 같은 말단의 뼈와 연부조직이 자란다.'),
 ('L46b', 's1', ['G0-1'],
  '그 사이를 모세혈관이 잇는다.',
  '그 사이를 모세혈관이 잇는다. 순환계는 이렇게 심장, 혈관, 혈액 셋으로 이루어진다.'),
 ('L46b', 's5', ['G0-13', 'G0-14'],
  '동맥혈이 정맥혈이 되는 자리가 여기다.',
  '동맥혈이 정맥혈이 되는 자리가 여기다. 실관 끝과 꽃 사이, 흰 방울이 떠다니는 그 틈이 세포사이액이다. 교환 표면과 몸 세포를 잇는 물이다. 영양이 그 틈을 건너 꽃으로 가고 노폐물이 거꾸로 건너와, 세포가 먹고 치울 수 있다.'),
 ('L49a', 's10', ['G0-211'],
  '든 배턴이 성장호르몬, 놓인 배턴이 소마토스타틴이다.',
  '든 배턴이 성장호르몬, 놓인 배턴이 소마토스타틴이다. 성장호르몬은 지방을 헐고 단백질을 쌓으며, 간의 당신생으로 혈당을 올린다. 운동, 스트레스, 저혈당 때 나온다.'),
 ('L07a', 's7', ['Q1-28'],
  '양성 피드백의 대표 예.',
  '양성 피드백의 대표 예. 분만 때는 프로스타글란딘도 자궁 수축을 거들고, 에스트로겐이 자궁의 옥시토신 수용체를 늘린다.'),
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
if bad: raise SystemExit(f'✕ {bad}')
if WRITE:
    for lid, (p, d, ind, nl) in files.items():
        open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=ind) + nl)
    print('written', list(files))

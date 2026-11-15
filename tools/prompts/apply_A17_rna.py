#!/usr/bin/env python3
# apply_A17_rna.py — 계획 P10(담장 밖 두루마리 마당)의 17장 카드 다섯을 이미 그려진 과에 카드만으로(2026-11-15 · 지시서 차례 6).
#  F0-13(rRNA · tRNA = 번역 안 되는 기능 RNA) → L43f s6(외발 기계의 보라 종이 · 세발 기계의 클로버를 이미 그림)
#  F0-14 · F0-80 · F0-81 · F0-82(리보자임 · 한 가닥이라 자유롭게 접혀 입체 · RNA 세계) → L54a s6(종이 리본 끝이 접혀 손이 됨 · RNA 세계)
#  같은 개념을 두 그림에 그리지 않는다(L43g 에서 뺌).
import json
def patch(lid, sid, cards, after, add):
    p = f'/tmp/b2/lessons/{lid}.json'; d = json.load(open(p, encoding='utf-8'))
    s = next(x for x in d['stops'] if x['sid'] == sid)
    for c in cards:
        assert c not in s['cards'], c; s['cards'].append(c)
    assert s['say'].count(after) == 1, (lid, after); s['say'] = s['say'].replace(after, after + ' ' + add)
    assert len(s['say']) <= 560, len(s['say'])
    open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1)); print(lid, sid, s['cards'], len(s['say']))
patch('L43f', 's6', ['F0-13'], 'RNA 중합효소 III 은 tRNA 를 주로 만든다.',
      'rRNA 와 tRNA 는 단백질로 번역되지 않고도 제 일을 하는 RNA 의 대표다.')
patch('L54a', 's6', ['F0-14', 'F0-80', 'F0-81', 'F0-82'], '리본이 일하는 효소(-자임)가 된 셈이다.',
      '리본은 한 가닥이라 자유롭게 접혀 복잡한 입체 꼴을 만든다. 두 가닥이 맞물린 밧줄(DNA)보다 효소 노릇을 하기 쉬운 까닭이다.')

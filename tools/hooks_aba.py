# -*- coding: utf-8 -*-
"""ABA 후크 확정 — 갓 쓴 늙은 아비 = 「아바」 (형태 ①).

_후크대기에서 빼고 hooks 에 넣는다. 심볼예약에도 적어 다음 판이 갓을 딴 데 쓰지 않게 한다.

★ 왜 낙엽을 안 썼나 — abscisic 은 「떨어뜨리는」이라 뜻은 맞지만
   실제 잎 탈리는 에틸렌이 하고, 그 낙엽은 이미 옆 판 s20p01b 에 있다. 심볼 충돌이다.
★ 왜 자물쇠를 안 썼나 — 「금색 자물쇠 = 약물·독물 전용」이 예약돼 있다.
   휴면은 「흙에 묻고 손바닥으로 누른다」로 그렸다 — s20p01a 의 「끌로 깬다」와 정확히 반대다.
"""
import json, collections, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hooks.json')
d = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)

d['hooks']['ABA'] = collections.OrderedDict([
    ('props', ['갓 쓴 늙은 아비', '갓 쓴 아비', '아비']),
    ('형태', '①'),
    ('왜', 'ABA를 붙여 읽으면 「아바」 — 갓 쓴 늙은 아비가 그 소리다(s20p01c). '
           '온실에서 닿는 것마다 멈추는 사람이라 하는 일 넷과도 붙는다'),
])
d['hooks']['앱시스산'] = collections.OrderedDict([
    ('props', ['갓 쓴 늙은 아비', '갓 쓴 아비', '아비']),
    ('형태', '①'),
    ('왜', 'ABA의 우리말 이름. 같은 아비가 나른다'),
])

res = d.setdefault('_심볼예약', collections.OrderedDict())
res['갓 쓴 늙은 아비'] = ('ABA(앱시스산) 전용 — 「아바」 소리다(s20p01c). '
                    '⚠ 챙 넓은 검은 갓이라 s20p01a·s20p01b 의 야구모자 쓴 온실 인부들과 갈린다. '
                    '⚠ s39p03 의 허수아비(허시)·s12p04 의 흰머리 노인(나이아신 결핍)과도 다른 사람이다')
res['흙에 묻고 손바닥으로 누른 씨앗'] = ('종자 휴면 전용 — ABA가 거는 쪽(s20p01c). '
                             '푸는 쪽은 s20p01a 의 「끌로 씨앗 껍질을 깬다」(지베렐린·브라시노스테로이드)다. '
                             '⚠ 자물쇠를 쓰지 않은 것은 「금색 자물쇠 = 약물·독물 전용」이기 때문이다')
res['납작하게 웅크린 모종'] = '생장 억제 전용 — 키를 못 키우고 옆으로 퍼진 것(s20p01c)'
res['갈라진 땅과 마른 바람'] = (str(res.get('갈라진 땅과 마른 바람', '')) +
                       ' · s20p01c 에서는 그 위 화분의 잎만 빳빳한 것이 건조 내성이다').strip(' ·')

wait = d.get('_후크대기', {})
wait.pop('ABA', None)

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('hooks +ABA/앱시스산 · 예약 %d · 대기 %d (%s)'
      % (len(res), len(wait), ' · '.join(wait.keys())))

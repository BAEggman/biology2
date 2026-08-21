# -*- coding: utf-8 -*-
"""사전 누락 훑기 ② — 그림에 이미 있는데 hooks.json 에만 없던 것.

★ AM  이미 등록돼 있었는데 소품이 하나뿐이었다.
   s05p01 은 「가죽 글러브의 손가락」, s22p03 은 「붉은 나뭇가지」로 같은 것을 그렸다.
   arbuscule 은 「작은 나무」이고 우리말 이름도 「수지상(樹枝狀)」이라 나뭇가지가 곧 그 이름이다.

★ ECM 아예 없었다. 「뿌리 겉만 감고 지나는 실」 — ecto = 겉. 형태 ④(뜻)다.
   ⚠ ECM 은 세포외기질이기도 한데, 덱에서는 그쪽을 한글 「세포외기질」로만 쓴다. 충돌 없다.

★★ 안 등록한 것 하나 — SGLT
   s17p01 은 SGLT2 를 「자루 1」, SGLT1 을 「자루 2」로 그렸다. 사실은 맞다
   (SGLT2 = Na 1 : 포도당 1 / SGLT1 = Na 2 : 포도당 1).
   그런데 **자루 개수가 이름의 숫자와 반대**라서 후크로 쓰면 거꾸로 외운다.
   후크로 등록하는 대신 **함정이라고 적어 준다** — 그게 이 자리에서 더 값이 크다.
"""
import json, collections, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'tools', 'hooks.json')
d = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)

am = d['hooks']['AM']
for w in ('붉은 나뭇가지', '나뭇가지', '수지상'):
    if w not in am['props']: am['props'].append(w)
am['왜'] = ('수지상균근(arbuscular) — arbuscule 은 「작은 나무」이고 우리말 이름도 수지상(樹枝狀)이다. '
           's05p01 은 껍질 속으로 파고드는 글러브의 손가락으로, s22p03 은 세포 안까지 뻗은 붉은 나뭇가지로 '
           '같은 것을 그렸다')

d['hooks']['ECM'] = collections.OrderedDict([
    ('props', ['겉만 감고', '겉만', '겉에서 감']),
    ('형태', '④'),
    ('왜', '외생균근(ectomycorrhiza) — ecto = 겉. 「뿌리 겉만 감고 지나는 실」이 그대로 그 이름이다. '
           'AM(안까지 파고드는 나뭇가지)과 「안까지 갔나 겉만 감았나」 하나로 갈린다'),
])
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('hooks — AM 소품 보탬 · ECM 신설')

# ── s17p01 : 자루 개수가 이름과 반대라는 것을 적는다 ──────────────
SK = os.path.join(ROOT, 'sketchy.html')
s = open(SK, encoding='utf-8').read()
FIX = [
 ('SGLT2 — Na⁺ 1 : 포도당 1, 저친화 대용량, 근위 초기',
  'SGLT2 — Na⁺ 1 : 포도당 1, 저친화 대용량, 근위 초기. '
  '★ <b>자루 개수가 이름의 숫자와 반대다</b> — 자루 하나가 SGLT<b>2</b>다'),
 ('SGLT1 — Na⁺ 2 : 포도당 1, 고친화, 근위 후반',
  'SGLT1 — Na⁺ 2 : 포도당 1, 고친화, 근위 후반. '
  '★ 여기도 반대다 — 자루 <b>둘</b>이 SGLT<b>1</b>이다. 뒤집어 외우기 쉬운 자리다'),
]
for a, b in FIX:
    assert s.count(a) == 1, a[:30]
    s = s.replace(a, b, 1)

# ── s05p02 : 그리지 않은 약어를 부르지 않는다 ─────────────────────
A = '병꼴균은 편모포자, 글로메로균은 AM균근이다'
B = '병꼴균은 편모포자, 글로메로균은 수지상균근이다(그 나뭇가지는 뿌리 장면에 있다)'
assert s.count(A) == 1
s = s.replace(A, B, 1)
open(SK, 'w', encoding='utf-8').write(s)
print('s17p01 — 자루 개수가 이름과 반대라는 함정을 적음 · s05p02 — AM 약어를 풀어 씀')

# -*- coding: utf-8 -*-
"""d02p03(정자 vs 난자 형성)에 정자 꼬리를 달고 크기·운동성 한 줄을 적는다.

★ 왜 — pc 훑기에서 세 장이 폐기될 자리였다
  Q1-5 · Q1-5#1 · Q1-5#2 「난자 = 크고 비운동성·양분 저장 / 정자 = 작고 운동성」.
  그림에는 크기 대비만 있고(난자 원 r25 vs 극체 r7.5), 정자 쪽 원 넷은 그냥 동그라미였다 —
  「정자 형성」 그림인데 정자가 정자처럼 안 생겼다는 것 자체가 아쉬운 자리이기도 하다.
  도해는 내가 직접 고칠 수 있으니 ③ 폐기가 아니라 ④ 그림 고침이다.

  ① 정자 원 넷에 꼬리를 단다 (운동성)
  ② 캡션 세 줄을 12 씩 내려 꼬리 자리를 만든다
  ③ 맨 아래에 크기·운동성·양분 한 줄 (도해는 글자로도 가르친다)
"""
import os
SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_d02p03.svg')
s = open(SVG, encoding='utf-8').read()
assert '꼬리' not in s, '이미 들어 있다'

# ① 캡션 세 줄을 내린다 — 꼬리가 들어갈 자리
for old_y, new_y in (('264', '276'), ('286', '296'), ('308', '316')):
    a = '<text x="215" y="%s"' % old_y
    assert s.count(a) == 1, a
    s = s.replace(a, '<text x="215" y="%s"' % new_y, 1)

# ② 정자 원 넷에 꼬리 — 원 아래 가장자리(y=239)에서 S자로 흐른다
TAILS = '\n'.join(
    '<path d="M%d 239 c -6 6 6 11 0 17" fill="none" stroke="#1E40AF" '
    'stroke-width="1.6" stroke-linecap="round"/>' % cx for cx in (128, 192, 238, 302))
a = '<text x="215" y="276"'
assert s.count(a) == 1
s = s.replace(a, TAILS + '\n    ' + a, 1)

# ③ 캔버스를 조금 늘리고 맨 아래 한 줄
s = s.replace('viewBox="0 0 880 476"', 'viewBox="0 0 880 502"', 1)
# ⚠ text-anchor="middle" 안에 <tspan> 을 쓰면 겹쳐 그려진다(실측). 한 색으로 쓴다.
LINE = ('<text x="440" y="486" text-anchor="middle" font-size="11" font-weight="700" fill="#4B5563">'
        '난자는 크고 스스로 못 움직이며 양분을 싣는다 · 정자는 작고 꼬리로 헤엄친다</text>')
s = s.rstrip()
assert s.endswith('</svg>')
s = s[:-len('</svg>')] + '  ' + LINE + '\n</svg>'
open(SVG, 'w', encoding='utf-8').write(s)
print('_d02p03.svg — 정자 꼬리 넷 + 크기·운동성 한 줄')

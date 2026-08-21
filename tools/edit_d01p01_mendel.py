# -*- coding: utf-8 -*-
"""d01p01(감수분열 3열 대조표)에 「멘델의 두 법칙」 줄을 더한다.

★ 왜 — 도해는 이름을 글자로 나른다
  이 표의 마지막 줄은 「다양성을 만드는 자리 → 독립분배 · 교차·키아스마」인데,
  거기 걸린 카드 여섯 장이 전부 **멘델**을 이름으로 부른다. 그런데 표 어디에도
  「멘델」이라는 글자가 없다 — 학생은 표를 외운 뒤 이름을 따로 외워야 했다.
  Sketchy 그림이면 소리 후크를 세워야 하지만, 도해는 **글자 한 줄이면 끝난다.**

★ 무엇을 적나 — 두 법칙이 각각 표의 어느 칸에서 성립하는지
  분리의 법칙 = 후기 I 에서 **상동염색체가 갈린다** (이미 표에 있는 칸)
  독립의 법칙 = 중기 I 의 **배열 ①②, 쌍마다 어느 극으로 갈지 무관** (이미 표에 있는 칸)
  둘 다 **감수 1분열 한 칸**에 몰려 있다는 것이 이 표의 결론이다.

★ 표를 늘리는 법 — 세로선·바탕 톤·마무리 글줄이 전부 y=770 에 맞춰져 있다.
  viewBox 를 64 늘리고, 그 셋을 같이 늘린 뒤 새 줄을 770~832 에 넣는다.
"""
import os, re
SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_d01p01.svg')
SK  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sketchy.html')

s = open(SVG, encoding='utf-8').read()
assert '멘델' not in s, '이미 들어 있다'

# ① 캔버스를 늘린다
s = s.replace('viewBox="0 0 880 824"', 'viewBox="0 0 880 888"', 1)
# ② 감수 1분열 칸의 바탕 톤을 새 줄까지 늘린다 (54~770 → 54~832)
s = s.replace('<rect x="357" y="54" width="257" height="716" fill="#FFF7ED"',
              '<rect x="357" y="54" width="257" height="778" fill="#FFF7ED"', 1)
# ③ 세로 구분선 넷을 늘린다
for x in ('100', '357', '614', '871'):
    a = '<line x1="%s" y1="54" x2="%s" y2="770"/>' % (x, x)
    b = '<line x1="%s" y1="54" x2="%s" y2="832"/>' % (x, x)
    assert s.count(a) == 1, a
    s = s.replace(a, b, 1)
# ④ 새 가로 구분선 — 기존 y=770 선 바로 뒤에 붙인다(같은 <g> 안이라 스타일이 이어진다)
a = '<line x1="10" y1="770" x2="871" y2="770"/>'
assert s.count(a) == 1
s = s.replace(a, a + '\n<line x1="10" y1="832" x2="871" y2="832"/>', 1)

# ⑤ 마무리 두 글줄을 아래로 민다
for old_y, new_y in (('792', '856'), ('810', '874')):
    a = '<text x="440" y="%s"' % old_y
    assert s.count(a) == 1, a
    s = s.replace(a, '<text x="440" y="%s"' % new_y, 1)

# ⑥ 새 줄 — 770~832
ROW = '''
<text x="55" y="794" text-anchor="middle" font-size="10.5" fill="#6B7280">멘델의</text>
<text x="55" y="808" text-anchor="middle" font-size="10.5" fill="#6B7280">두 법칙</text>
<text x="229" y="800" text-anchor="middle" font-size="11.5" fill="#9CA3AF">없음</text>
<text x="743" y="800" text-anchor="middle" font-size="11.5" fill="#9CA3AF">없음</text>
<rect x="368" y="778" width="112" height="22" rx="6" fill="#FFEDD5" stroke="#C2410C" stroke-width="1.2"/>
<text x="424" y="793" text-anchor="middle" font-size="10.5" font-weight="700" fill="#7C2D12">멘델 · 분리의 법칙</text>
<rect x="490" y="778" width="112" height="22" rx="6" fill="#FFEDD5" stroke="#C2410C" stroke-width="1.2"/>
<text x="546" y="793" text-anchor="middle" font-size="10.5" font-weight="700" fill="#7C2D12">멘델 · 독립의 법칙</text>
<text x="486" y="820" text-anchor="middle" font-size="10" fill="#7C2D12">분리 = 후기 I 에서 상동이 갈린다 · 독립 = 중기 I 의 배열 두 가지 — 둘 다 이 한 칸이다</text>'''
a = '<text x="440" y="856"'
assert s.count(a) == 1
s = s.replace(a, ROW.strip() + '\n' + a, 1)

open(SVG, 'w', encoding='utf-8').write(s)
print('_d01p01.svg — 멘델 줄 추가 (%d바이트)' % len(s))

# ⑦ sketchy.html 안의 인라인 사본도 같이 갈아 끼운다
k = open(SK, encoding='utf-8').read()
i = k.index("{id:'d01p01'")
a0 = k.index('svg:`', i) + 5
b0 = k.index('`', a0)
old_svg = k[a0:b0]
assert old_svg.lstrip().startswith('<svg'), old_svg[:60]
assert '`' not in s
k = k[:a0] + s.strip() + k[b0:]
open(SK, 'w', encoding='utf-8').write(k)
print('sketchy.html 인라인 사본 교체 (%d → %d바이트)' % (len(old_svg), len(s.strip())))

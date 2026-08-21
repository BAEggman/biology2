# -*- coding: utf-8 -*-
"""d01p03(광합성 Z 도식)에 「주머니 한 장을 갈라 보면」 확대 칸을 넣는다.

★ 왜 — pc 훑기에서 폐기될 뻔한 다섯 장을 살린다
  이 판의 pc 38장을 한 장씩 판정하다 보니, 루멘과 ATP 합성효소가 그림에 없어서
  다섯 장이 「급소가 그림에 없다」로 폐기될 자리였다:
    C0-138 H⁺ 저장고는?            → 틸라코이드 루멘
    C0-111 ATP 합성효소 통과 방향은? → 루멘 → 스트로마
    C0-112 ATP 생성 장소는?         → 스트로마
    C0-148 ATP가 스트로마 쪽에서 나는 까닭은?
    C0-37  꼭 구분할 세 공간은?      → 스트로마 · 틸라코이드막 · 틸라코이드 루멘
  도해는 Gemini 없이 내가 직접 그릴 수 있다 — 그러니 ③ 폐기가 아니라 ④ 그림 고침이 맞다.

★ 그리고 순환 캡션에 한 줄 — 「캘빈이 ATP를 더 쓰니 그 비를 맞춘다」
  C0-127·C0-136 이 묻는 것이 정확히 그 까닭인데 도식에 그 말이 없었다.

★ 캔버스를 아래로 88 늘린다. 아래 상자 높이와 어원 캡션이 같이 내려간다.
"""
import os
SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_d01p03.svg')
SK  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sketchy.html')

s = open(SVG, encoding='utf-8').read()
assert '루멘' not in s, '이미 들어 있다'

# ① 캔버스와 아래 상자를 늘린다
s = s.replace('viewBox="0 0 880 612"', 'viewBox="0 0 880 700"', 1)
a = '<rect x="44" y="346" width="812" height="254" rx="10" fill="#F9FAFB" stroke="#E5E7EB"/>'
assert s.count(a) == 1
s = s.replace(a, '<rect x="44" y="346" width="812" height="342" rx="10" fill="#F9FAFB" stroke="#E5E7EB"/>', 1)

# ② 어원 캡션을 아래로 민다
a = '<text x="450" y="584" text-anchor="middle" font-size="10.5" fill="#6B7280">thylakos'
assert s.count(a) == 1
s = s.replace(a, '<text x="450" y="672" text-anchor="middle" font-size="10.5" fill="#6B7280">thylakos', 1)

# ③ 순환 캡션 — 왜 순환을 함께 돌리는지
a = '<text x="290" y="20" text-anchor="middle" font-size="11.5" fill="#6B7280">순환적 — 광계 I만 사용, ATP만 생성</text>'
assert s.count(a) == 1
s = s.replace(a, '<text x="290" y="20" text-anchor="middle" font-size="11.5" fill="#6B7280">'
                 '순환적 — 광계 I만 사용, ATP만 생성 · 캘빈이 ATP를 더 쓰니 그 비를 맞춘다</text>', 1)

# ④ 새 띠 — 주머니 한 장 확대
INSET = '''
<line x1="60" y1="556" x2="840" y2="556" stroke="#E5E7EB"/>
<text x="62" y="576" font-size="11.5" font-weight="700" fill="#4B5563">주머니 한 장을 갈라 보면 — ATP가 나는 자리</text>
<line x1="330" y1="530" x2="270" y2="588" stroke="#9CA3AF" stroke-width="1" stroke-dasharray="3 3"/>
<rect x="120" y="588" width="300" height="46" rx="14" fill="#FFF7ED" stroke="#C2410C" stroke-width="1.8"/>
<text x="150" y="606" font-size="10.5" font-weight="700" fill="#7C2D12">틸라코이드 루멘</text>
<g fill="#C2410C">
<circle cx="152" cy="622" r="3.5"/><circle cx="170" cy="622" r="3.5"/><circle cx="188" cy="622" r="3.5"/>
<circle cx="206" cy="622" r="3.5"/><circle cx="224" cy="622" r="3.5"/><circle cx="242" cy="622" r="3.5"/>
</g>
<text x="262" y="626" font-size="10" font-weight="700" fill="#7C2D12">H⁺가 여기 쌓인다</text>
<text x="129" y="650" font-size="9.5" fill="#C2410C">← 테두리가 틸라코이드막</text>
<line x1="360" y1="600" x2="360" y2="624" stroke="#C2410C" stroke-width="2.2"/>
<polygon points="360,632 355,622 365,622" fill="#C2410C"/>
<rect x="356" y="632" width="9" height="12" fill="#1E40AF"/>
<circle cx="360.5" cy="654" r="11" fill="#DBEAFE" stroke="#1E40AF" stroke-width="1.6"/>
<text x="392" y="642" font-size="10.5" font-weight="700" fill="#1E40AF">ATP 합성효소</text>
<text x="392" y="657" font-size="11" font-weight="700" fill="#1E40AF">→ ATP</text>
<text x="120" y="672" font-size="10" fill="#6B7280">아래쪽이 스트로마 — 캘빈회로가 ATP를 쓰는 바로 그 자리다</text>
<text x="655" y="592" text-anchor="middle" font-size="11" font-weight="700" fill="#4B5563">꼭 갈라야 하는 세 공간</text>
<text x="655" y="610" text-anchor="middle" font-size="10.5" fill="#6B7280">스트로마 · 틸라코이드막 · 틸라코이드 루멘</text>
<text x="655" y="630" text-anchor="middle" font-size="10" fill="#6B7280">H⁺는 루멘에 쌓였다가 막의 합성효소를 거쳐 스트로마로 나온다</text>
<text x="655" y="646" text-anchor="middle" font-size="10" fill="#6B7280">그래서 ATP는 스트로마 쪽에서 난다 — 쓰는 자리에서 만든다</text>'''
a = '<text x="450" y="672" text-anchor="middle"'
assert s.count(a) == 1
s = s.replace(a, INSET.strip() + '\n' + a, 1)

open(SVG, 'w', encoding='utf-8').write(s)
print('_d01p03.svg — 루멘·ATP 합성효소 확대 칸 + 순환 까닭 한 줄')

# ⑤ sketchy.html 인라인 사본 교체
k = open(SK, encoding='utf-8').read()
i = k.index("{id:'d01p03'")
a0 = k.index('svg:`', i) + 5
b0 = k.index('`', a0)
assert k[a0:b0].lstrip().startswith('<svg')
assert '`' not in s
open(SK, 'w', encoding='utf-8').write(k[:a0] + s.strip() + k[b0:])
print('sketchy.html 인라인 사본 교체')

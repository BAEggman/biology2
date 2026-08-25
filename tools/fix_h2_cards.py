# -*- coding: utf-8 -*-
"""H2 카드 교정 — 2026-08-25. 독립 검수(적대적 판정)에서 셋이 IMPRECISE 로 걸렸다.

★ H2-5  「프로스타글란딘 농도 저하」만으로는 불완전하다. 표준 교과서는 **동맥혈 산소분압 상승**을
        1차 자극으로 들고 PGE₂ 감소를 함께 든다. 「주된 요인」을 묻는 문항에서 틀릴 수 있었다.
★ H2-4  기시점인 **제대정맥**이 빠져 있었다. 그리고 제대정맥의 흔적은 **간원삭**이고
        정맥관의 흔적이 정맥관인대라, 기시점을 빼면 이 둘이 섞인다.
★ H2-7  층류 조건이 빠져 있었다. 혈액은 실제로 비뉴턴유체·박동성 흐름이다.
＋ H2-1  난원공은 성인 약 25%에서 해부학적으로 안 닫힌다(PFO) — 「기능적 폐쇄」를 주에 적는다.
＋ H2-9  신설 — 저항이 1/16 이면 유량은 16배다. 「몇 배」를 뒤집어 내는 문항이 흔하다.
        s18p02#4 「조금 굵은데 분출은 몇 배」가 유량을 이미 그리고 있으므로 제자리다.
"""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowlib import edit_row

IDX = '/tmp/b2/index.html'; SKY = '/tmp/b2/sketchy.html'
SRC = '지엽 정리 — 태아 순환과 출생 후 변화 / 혈역학의 물리 법칙 (기출 확인 안 됨)'

FIX = {
 'H2-1': dict(n=SRC + ' · ⚠ 난원공은 성인 약 25%에서 해부학적으로는 안 닫힌 채 남는다(PFO) — 출생 직후의 것은 좌심방압 상승에 따른 기능적 폐쇄다'),
 'H2-4': dict(a='제대정맥과 하대정맥을 이어 간을 우회하고, 출생 후 정맥관인대로 남는다',
              n=SRC + ' · ⚠ 제대정맥 자체의 흔적은 **간원삭**(ligamentum teres)이고 정맥관의 흔적이 정맥관인대(ligamentum venosum)다 — 기시점을 빼면 이 둘이 섞인다'),
 'H2-5': dict(a='동맥혈 산소분압 상승(1차 자극)과 프로스타글란딘(PGE₂) 감소',
              n=SRC + ' · 출생과 함께 폐호흡이 시작되어 PO₂가 오르고, 태반이 떨어지고 폐에서 대사되며 PGE₂가 준다. 지엽 정리는 PGE₂ 저하만 적지만 「주된 요인」을 묻는 문항은 산소분압 상승을 요구한다'),
 'H2-7': dict(a='혈관 반지름의 4제곱 (층류 조건)',
              n=SRC + ' · R = 8ηL/πr⁴ — 점성 η와 길이 L에는 비례한다. ⚠ 저항은 r⁴에 반비례하고 **유량은 r⁴에 비례**한다 — 방향을 뒤집어 내는 문항이 흔하다. 혈액은 실제로는 비뉴턴유체이고 흐름도 박동성이다'),
}
NEW = [dict(id='H2-9', q='혈관 반지름이 2배가 되면 혈류량(유량)은 몇 배가 되는가?',
            a='16배', g='H', gn='동물의 수송과 배설', ch='43 수송 시스템', ru=1,
            p='H2-9', t='discrim',
            n=SRC + ' · 같은 2⁴=16 인데 **저항은 1/16, 유량은 16배**다. 짝으로 붙여 두어야 뒤집힌 선지에 안 걸린다')]

s = open(IDX, encoding='utf-8').read()
m = re.search(r'(id=["\']CARDS["\'][^>]*>)([\s\S]*?)(</script>)', s)
CARDS = json.loads(m.group(2))
n0 = len(CARDS)
hit = 0
for c in CARDS:
    if c['id'] in FIX:
        c.update(FIX[c['id']]); hit += 1
assert hit == len(FIX), '못 찾은 카드가 있다 %d/%d' % (hit, len(FIX))
assert not ({x['id'] for x in NEW} & {c['id'] for c in CARDS}), 'id 충돌'
CARDS.extend(NEW)
body = json.dumps(CARDS, ensure_ascii=False, separators=(',', ':'))
open(IDX + '.t', 'w', encoding='utf-8').write(s[:m.start(2)] + body + s[m.end(2):])
os.replace(IDX + '.t', IDX)
print('✅ %d장 교정 · %d → %d장' % (hit, n0, len(CARDS)))

sk = open(SKY, encoding='utf-8').read(); m0 = len(sk)
sk, ch, new = edit_row(sk, 's18p02', 4, fn=lambda cs: cs + ['H2-9'] if 'H2-9' not in cs else cs)
assert ch and 0 < len(sk) - m0 < 60
print('  s18p02#4 →', new)
open(SKY + '.t', 'w', encoding='utf-8').write(sk); os.replace(SKY + '.t', SKY)
